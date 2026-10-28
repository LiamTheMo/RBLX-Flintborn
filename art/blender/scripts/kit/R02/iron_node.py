"""R02 row 1: IronNode resource (host dome with rust-rimmed steel plates)."""
import math

from mathutils import Vector

SUBJECT = "IronNode"
ROW = 1

PALETTE = {
    "r02_base_rock": ("#8C827D", 0.95, 0, 0),  # Base rocks everywhere, sulfur host slab, obsidian host/base slabs (warm light grey)
    "r02_iron_host": ("#7B7270", 0.95, 0, 0),  # Iron host rock boulder (cool grey-brown; lightened so the render mid tone matches)
    "r02_rust": ("#C4602B", 0.85, 0, 0),  # Orange rust rim around iron chunks (separate thin shell/collar geometry)
    "r02_iron": ("#9DB1D2", 0.18, 0.45, 0),  # Iron ore chunks, bluish steel faces (glossy)
}

IRON, RUST, HOST, BASE = "r02_iron", "r02_rust", "r02_iron_host", "r02_base_rock"
CHIPS = ["#9DB1D2", "#7B7270"]

# Host dome: rock(size=HOST_SIZE, sink=HOST_SINK) -> ellipsoid centre / radii
HOST_SIZE = (9.4, 8.4, 8.2)
HOST_SINK = 0.3


def _pent(w, h, spin=0.0, skew=0.0):
    pts = [(0.0 + skew * w, h / 2), (-w / 2, h * 0.14), (-w * 0.34, -h / 2),
           (w * 0.36, -h / 2), (w / 2, h * 0.1)]
    c, s = math.cos(spin), math.sin(spin)
    return [(x * c - y * s, x * s + y * c) for x, y in pts]


def _ngon(n, w, h, spin=0.0, wobble=0.0):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n + spin
        k = 1.0 + wobble * math.sin(3.1 * i + 0.7)
        pts.append((math.cos(t) * w / 2 * k, math.sin(t) * h / 2 * k))
    return pts


def _ring(bm, pts, z, scale=1.0, off=0.0, shift=(0.0, 0.0), zvar=None):
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    out = []
    for i, (x, y) in enumerate(pts):
        dx, dy = x - cx, y - cy
        d = math.hypot(dx, dy) or 1.0
        k = scale + off / d
        zz = z + (zvar[i % len(zvar)] if zvar else 0.0)
        out.append(bm.verts.new((cx + dx * k + shift[0], cy + dy * k + shift[1], zz)))
    return out


def _mid(pts, inset):
    """Points at the edge midpoints of a CCW loop, pulled toward the centre."""
    n = len(pts)
    cx = sum(p[0] for p in pts) / n
    cy = sum(p[1] for p in pts) / n
    out = []
    for i in range(n):
        x = (pts[i][0] + pts[(i + 1) % n][0]) / 2
        y = (pts[i][1] + pts[(i + 1) % n][1]) / 2
        out.append((cx + (x - cx) * inset, cy + (y - cy) * inset))
    return out


def _loft(bm, rings):
    """Closed solid through stacked rings (first = bottom, last = top)."""
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    n = len(rings[0])
    for lo, hi in zip(rings, rings[1:]):
        for i in range(n):
            bm.faces.new((lo[i], lo[(i + 1) % n], hi[(i + 1) % n], hi[i]))
    return [v for r in rings for v in r]


def gem(a, pts, z0, zg, zb, zt, loc=(0, 0, 0), rot=(0, 0, 0), rim=0.24, rim_z=(-0.6, 0.18),
        table=0.5, back=0.8, table_shift=(0.0, 0.0), zvar=(0.0,), rim_mat=RUST, inset=0.78):
    """Gem-like steel plate in local XY (outward = +Z): tapered back (z0) up to a
    girdle (zg), a crown ring of facets at edge midpoints (zb) and a table (zt).
    Every crown facet sits at its own angle so flat shading gives bright and dark
    facets. A thin rust collar slab (rim wider all round) sits behind it."""
    bm = a.bm
    if rim:
        rv = _loft(bm, [_ring(bm, pts, rim_z[0], off=rim), _ring(bm, pts, rim_z[1], off=rim)])
        a.transform(rv, loc, rot)
        a._finish(rv, rim_mat)
    n = len(pts)
    A0 = _ring(bm, pts, z0, scale=back)
    A = _ring(bm, pts, zg)
    B = _ring(bm, _mid(pts, inset), zb, zvar=zvar)
    C = _ring(bm, pts, zt, scale=table, shift=table_shift)
    bm.faces.new(list(reversed(A0)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((A0[i], A0[j], A[j], A[i]))
        bm.faces.new((A[i], A[j], B[i]))
        bm.faces.new((A[j], B[j], B[i]))
        bm.faces.new((B[i], B[j], C[j]))
        bm.faces.new((B[i], C[j], C[i]))
    bm.faces.new(C)
    gv = A0 + A + B + C
    a.transform(gv, loc, rot)
    a._finish(gv, IRON)


def host_frame(size, sink):
    r = Vector((size[0] / 2, size[1] / 2, size[2] / 2))
    c = Vector((0, 0, r.z * (1 - sink)))
    return c, r


def surface(c, r, d):
    d = Vector(d).normalized()
    s = 1.0 / math.sqrt(sum((d[i] / r[i]) ** 2 for i in range(3)))
    p = c + d * s
    n = Vector(((p - c)[i] / r[i] ** 2 for i in range(3))).normalized()
    return p, n


def flatten(verts, p, n, radius, depth):
    """Push verts above the plane (p - n*depth) within `radius` down onto it."""
    q = p - n * depth
    for v in verts:
        off = v.co - q
        h = off.dot(n)
        lat = (off - n * h).length
        if h > 0 and lat < radius:
            v.co -= n * h


# (direction from dome centre, width, height, spin deg, upward tilt)
HERO_CHUNKS = [
    ((-0.5, -0.85, 0.2), 3.5, 4.5, 12, 0.5),    # big, lower-left front, tilted back
    ((0.42, -0.88, -0.05), 2.6, 3.0, -18, 0.45), # medium, front-right low
    ((0.62, -0.28, 0.74), 2.7, 3.2, 35, 0.0),   # upper right shoulder, skyward
    ((-0.12, 0.32, 0.94), 1.8, 1.5, 70, 0.0),   # small top, peeking
]

BASE_ROCKS = [  # (x, y, size)
    (-3.4, -3.0, (3.2, 2.9, 2.3)),
    (3.3, -3.0, (3.0, 2.7, 2.1)),
    (0.1, -4.0, (1.8, 1.6, 1.4)),
    (-4.2, 0.6, (2.2, 2.0, 1.6)),
    (4.2, 0.5, (2.3, 2.1, 1.6)),
    (-1.2, 3.7, (1.9, 1.7, 1.4)),
]

ZVAR = (0.06, -0.05, 0.1, -0.02, 0.03)


def place_chunks(c, r, host_verts, chunks, depth=0.15):
    out = []
    for d, w, h, spin, lift in chunks:
        p, n = surface(c, r, d)
        n = (n + Vector((0, 0, lift))).normalized()  # tilt the plate back toward the sky
        rot = tuple(n.to_track_quat("Z", "Y").to_euler())
        flatten(host_verts, p, n, max(w, h) / 2 + 0.4, depth)
        out.append((p, n, w, h, spin, rot))
    return out


def build_host(fk, name, label, size, sink, chunks, with_plates):
    a = fk.Asset(name, label)
    c, r = host_frame(size, sink)
    hv = a.rock(size, (0, 0, 0), (0, 0, 0.3), HOST, subdiv=2, rough=0.07, facets=3, sink=sink)
    placed = place_chunks(c, r, hv, chunks, 0.3 if with_plates else 0.55)
    for p, n, w, h, spin, rot in placed:
        pts = _pent(w, h, math.radians(spin), 0.08)
        if with_plates:
            k = min(1.0, max(0.6, max(w, h) / 4.5))
            loc = tuple(p - n * 0.3)
            gem(a, pts, -0.5, 0.2 * k + 0.05, 0.62 * k, 0.88 * k, loc=loc, rot=rot, rim=0.18,
                rim_z=(-0.6, 0.3 * k), table=0.42, inset=0.72,
                table_shift=(0.05 * w, 0.04 * h), zvar=ZVAR)
        else:
            # bare seat: a flat pentagonal pad recessed into the pocket
            loc = tuple(p - n * 0.55)
            pv = _loft(a.bm, [_ring(a.bm, pts, -0.4, scale=0.95), _ring(a.bm, pts, 0.2, scale=0.9)])
            a.transform(pv, loc, rot)
            a._finish(pv, HOST)
    return a, c, r, placed


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []

    # ---------------- hero ----------------
    a, c, r, placed = build_host(fk, "IronNode", "R02 IronNode", HOST_SIZE, HOST_SINK,
                                 HERO_CHUNKS, True)
    for i, (x, y, s) in enumerate(BASE_ROCKS):
        a.rock(s, (x, y, 0), (0, 0, 0.7 * i), BASE, subdiv=2, rough=0.08, facets=11, sink=0.4)
    hero = a.finish()
    vfx.add(hero, "harvest_hit", (-1.5, -4.5, 3.5), color=CHIPS)
    vfx.add(hero, "ore_glint", (-2.0, -4.6, 3.5), scale=0.8)
    out.append(kit.tag(hero, "hero", collision="hull", budget=4500,
                       notes="Iron node: faceted grey host dome with four rust-rimmed gem-like steel "
                             "plates and six base rocks. Sockets: harvest_hit on the front strike face "
                             "(steel+host chips), ore_glint on the big front plate. Iron does not "
                             "glow: no light."))

    # ---------------- parts ----------------
    a, _, _, _ = build_host(fk, "IronHostRock", "R02 IronHostRock", (9.5, 8.2, 8.0), HOST_SINK,
                            HERO_CHUNKS[:3], False)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Modular part: bare iron host boulder with flat pentagonal pockets where "
                             "IronChunk plates seat."))

    a = fk.Asset("IronChunk", "R02 IronChunk")
    gem(a, _pent(3.0, 4.0, 0.0, 0.1), 0.0, 0.45, 0.85, 1.05, rot=(math.radians(80), 0, 0),
        rim=0.24, rim_z=(-0.05, 0.25), back=0.75, table_shift=(0.1, 0.15), zvar=ZVAR)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=600,
                       notes="Modular part: one gem-like steel ore plate with its rust collar; seat "
                             "it on IronHostRock's flat pockets."))

    a = fk.Asset("IronBaseRock", "R02 IronBaseRock")
    a.rock((2.0, 1.7, 1.4), (0, 0, 0), (0, 0, 0.4), BASE, subdiv=2, rough=0.08, facets=11, sink=0.3)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=400,
                       notes="Modular part: small light base rock for the node's foot."))

    # ---------------- drops ----------------
    a = fk.Asset("IronChunkDrop", "R02 IronChunkDrop")
    gem(a, _pent(1.3, 0.95, 0.3, 0.1), 0.0, 0.45, 0.95, 1.15, rot=(0.12, -0.08, 0),
        rim=0.07, rim_z=(0.0, 0.2), back=0.85, table=0.62, table_shift=(0.06, 0.04),
        zvar=(0.08, -0.06, 0.12, -0.03, 0.05))
    out.append(kit.tag(a.finish(), "drop", collision="none", budget=300,
                       notes="Iron ore drop: faceted steel chunk with a rust underside edge."))

    a = fk.Asset("IronChunkDrop2", "R02 IronChunkDrop2")
    gem(a, _ngon(6, 1.55, 1.1, 0.4, 0.08), 0.0, 0.3, 0.6, 0.78, rot=(-0.06, 0.1, 0),
        rim=0.07, rim_z=(0.0, 0.18), back=0.9, table=0.55, table_shift=(-0.05, 0.05),
        zvar=(0.05, -0.04, 0.08, 0.0, -0.05, 0.06))
    out.append(kit.tag(a.finish(), "drop", collision="none", budget=300,
                       notes="Iron ore drop variant: flatter hexagonal steel chunk, rust underside."))

    # ---------------- depleted ----------------
    a = fk.Asset("IronNodeDepleted", "Depleted (Base)")
    size = (9.0, 7.5, 3.4)
    dv = a.rock(size, (0, 0, 0), (0, 0, 0.2), HOST, subdiv=2, rough=0.07, facets=3, sink=0.25)
    dc, dr = host_frame(size, 0.25)
    for d, rad in (((-0.35, -0.2, 1.0), 1.4), ((0.35, 0.25, 1.0), 1.2), ((0.55, -0.5, 0.7), 1.0)):
        sp, sn = surface(dc, dr, d)
        flatten(dv, sp, sn, rad, 0.35)
    a.rock((4.6, 4.0, 2.4), (-1.3, 0.5, 1.1), (0, 0, 0.6), HOST, subdiv=1, rough=0.08,
           facets=0, sink=0.45)
    for i, (x, y, s) in enumerate([(-4.4, -1.0, (2.0, 1.9, 1.5)), (4.5, -0.3, (1.8, 1.7, 1.3)),
                                   (3.4, -2.8, (1.2, 1.1, 0.9))]):
        a.rock(s, (x, y, 0), (0, 0, 0.9 * i), BASE, subdiv=2, rough=0.08, facets=11, sink=0.35)
    dep = a.finish()
    vfx.add(dep, "harvest_deplete", (0, 0, 0.5), color=CHIPS)
    out.append(kit.tag(dep, "depleted", collision="hull", budget=2000,
                       notes="Depleted iron node: low faceted host mound with an off-centre hump, "
                             "shallow pits and base rocks at the ends. Socket: harvest_deplete at "
                             "the base centre."))
    return out
