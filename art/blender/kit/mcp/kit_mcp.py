"""World-kit helpers for modelling live through the Blender MCP.

The kit is re-modelled by hand in the open Blender (art/blender/assets/kit/FlintbornWorldKit.blend).
Helpers defined only inside an MCP call vanish when Blender restarts, so the shared ones live here.
Load once per Blender session (each MCP call can then use NS["..."]):

    import sys; sys.path.insert(0, "D:/Projects/Roblox/RBLX-Flintborn/art/blender/kit/mcp")
    import importlib, kit_mcp; importlib.reload(kit_mcp); kit_mcp.install()

Per-model shape builders stay in the MCP calls; only generic tools belong here.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

REPO = "D:/Projects/Roblox/RBLX-Flintborn"
LIB = REPO + "/art/blender/lib"
NS = bpy.app.driver_namespace

# Row order of every sheet (module name, subject) as on the master sheets.
FOLIAGE_SPEC = 0.06   # Specular IOR Level for kit foliage, moss and grass (flintkit default for LOW_SPEC is 0.2)
DOME = [(0.0, 1.0, 9), (0.30, 1.0, 9), (0.62, 0.86, 8), (0.86, 0.55, 6), (1.0, 0.18, 3)]


def load_kit():
    """build_kit.py's namespace (studio, framing, compare renders, checks) without running main()."""
    if LIB not in sys.path:
        sys.path.insert(0, LIB)
    import importlib
    import flintkit
    import vfx
    if "KIT" not in NS:
        importlib.reload(flintkit)
        importlib.reload(vfx)
        src = open(REPO + "/art/blender/scripts/build_kit.py", encoding="utf-8").read()
        src = src.rsplit("\nmain()", 1)[0]
        kit = {"__file__": REPO + "/art/blender/scripts/build_kit.py", "__name__": "build_kit_mcp"}
        exec(compile(src, "build_kit.py", "exec"), kit)
        NS["KIT"] = kit
    return NS["KIT"]


def fk():
    import flintkit
    return flintkit


def set_colour(key, hexcol, rough=0.9, metal=0.0, emit=0.0, low_spec=False):
    """Set a KIT_PALETTE key and update its material in place if it exists."""
    f = fk()
    f.KIT_PALETTE[key] = (hexcol, rough, metal, emit)
    if low_spec:
        f.LOW_SPEC.add(key)
    mat = bpy.data.materials.get("FB_" + key) or (f.material(key) if key.startswith(("w", "r", "v")) else None)
    if not mat:
        return
    rgb = f.hex_rgb(hexcol)
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    mix = next((n for n in nt.nodes if n.type == "MIX"), None)
    if mix:
        mix.inputs["A"].default_value = (*rgb, 1)
    elif bsdf:
        bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    if bsdf:
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
        if key in f.LOW_SPEC and "Specular IOR Level" in bsdf.inputs:
            # foliage/moss/grass: barely any sheen, or the sky's white glints wash the greens pale and bluish
            bsdf.inputs["Specular IOR Level"].default_value = FOLIAGE_SPEC
        if emit > 0:
            bsdf.inputs["Emission Color"].default_value = (*rgb, 1)
            bsdf.inputs["Emission Strength"].default_value = emit
    mat.diffuse_color = (*rgb, 1)
    mat["flintkit_hex"] = hexcol
    mat["flintkit_spec"] = [rough, metal, emit]


def sheet_coll(sheet):
    """The sheet's collection under Kit, found by its id prefix ("W01")."""
    kit = bpy.data.collections["Kit"]
    return next(c for c in kit.children if c.name.split(" ")[0] == sheet)


def socket(o, kind, loc, **kw):
    """VFX socket on o at asset-local studs."""
    kit = NS["KIT"]
    n = len([c for c in o.children if c.get("vfx_kind") == kind]) + 1
    return kit["vfx"].add(o, kind, tuple(loc), name=f"VFX_{o.name}_{kind}_{n}", **kw)


def hull_rock(a, size, loc=(0, 0, 0), seed=1, mat="w01_rock", rings=DOME, jitter=0.09, rot=0.0,
              lean=(0.0, 0.0), tilt=(0.0, 0.0), keep_bottom=False, facet_var=0.0):
    """Big-faceted rock: convex hull of jittered point rings. size = full (x, y, z) extent,
    base at loc.z. rings = (height frac, radius frac, points) from the ground up. lean shifts the
    crown by a fraction of the radius; tilt rotates the whole rock (x, y radians) after building."""
    rng = random.Random(seed)
    rx, ry, rz = size[0] / 2, size[1] / 2, size[2]
    bm = a.bm
    pts = []
    for h, rf, n in rings:
        off = rng.uniform(0, 2 * math.pi)
        for k in range(n):
            th = off + 2 * math.pi * k / n + rng.uniform(-0.25, 0.25) * (2 * math.pi / n)
            r = rf * (1 + rng.uniform(-jitter, jitter))
            z = h * rz * (1 + (rng.uniform(-jitter, jitter) if 0 < h < 1 else 0))
            x = math.cos(th) * rx * r + lean[0] * rx * h
            y = math.sin(th) * ry * r + lean[1] * ry * h
            pts.append(Vector((x, y, max(0.0, z))))
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    for v in vs:
        if v.is_valid and not v.link_faces:
            bm.verts.remove(v)
    verts = [v for v in vs if v.is_valid]
    faces = list({f for v in verts for f in v.link_faces})
    # convex_hull can leave a flat face pointing inward; without this a flat TOP ring (all points at
    # h=1.0) came out facing down and was deleted below as if it were the base, leaving an open crater
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    if not keep_bottom:
        zmin = min(v.co.z for v in verts)
        bot = [f for f in faces if f.normal.z < -0.99 and f.calc_center_median().z < zmin + 1e-3]
        if bot:
            bmesh.ops.delete(bm, geom=bot, context="FACES_ONLY")
        verts = [v for v in verts if v.is_valid]
    m = Matrix.Rotation(rot, 3, "Z")
    if tilt != (0.0, 0.0):
        m = Matrix.Rotation(tilt[1], 3, "Y") @ Matrix.Rotation(tilt[0], 3, "X") @ m
    bmesh.ops.rotate(bm, verts=verts, cent=(0, 0, 0), matrix=m)
    bmesh.ops.translate(bm, verts=verts, vec=Vector(loc))
    a._finish(verts, mat, face_tint_var=facet_var)
    return verts


PEBBLE = [(0.0, 0.92, 6), (0.4, 1.0, 6), (0.8, 0.7, 5), (1.0, 0.25, 3)]


def pebble(a, size, loc, seed, mat, rot=None):
    """Small faceted stone (about 20-30 tris)."""
    rng = random.Random(seed)
    return hull_rock(a, size, loc=loc, seed=seed, mat=mat, rings=PEBBLE, jitter=0.12,
                     rot=rng.uniform(0, 6.28) if rot is None else rot)


def _faces_from(bm, rows, closed=False):
    """Quad/tri strip faces between consecutive vertex rows (lists of equal length or tip rows of 1)."""
    out = []
    for r0, r1 in zip(rows, rows[1:]):
        n = max(len(r0), len(r1))
        rng_ = range(n if closed else n - 1)
        for i in rng_:
            j = (i + 1) % n
            q = [r0[min(i, len(r0) - 1)], r0[min(j, len(r0) - 1)], r1[min(j, len(r1) - 1)], r1[min(i, len(r1) - 1)]]
            q = [v for k, v in enumerate(q) if v not in q[:k]]
            if len(q) >= 3:
                try:
                    out.append(bm.faces.new(q))
                except ValueError:
                    pass
    return out


def drape(a, center, radius, mat, seed=1, lobes=7, thick=0.35, rings=3, segs=None, direction=(0, 0, -1),
          lift=0.04, crumple=0.12, scallop=0.22, squash=(1.0, 1.0), angle=0.0):
    """A thick lobed patch (moss, lichen, snow, ivy mat) shrink-wrapped onto whatever is already in
    the asset, by casting rays along direction. center is a point in front of the surface; the
    patch spreads in the plane perpendicular to direction. Builds a closed shell: crumpled top,
    underside just inside the surface, edges tapering to a thin rim. Call it right after the host
    geometry (the BVH is built from everything in the asset so far)."""
    from mathutils.bvhtree import BVHTree
    rng = random.Random(seed)
    bm = a.bm
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    d = Vector(direction).normalized()
    # horizontal casts: u runs sideways along the face, v straight up it (squash[1] stretches it vertically)
    u = d.cross(Vector((0, 0, 1))).normalized() if abs(d.z) < 0.9 else d.orthogonal().normalized()
    v = u.cross(d).normalized()
    ru = Matrix.Rotation(angle, 3, d)
    u, v = ru @ u, ru @ v
    segs = segs or max(18, lobes * 6)
    ph = [rng.uniform(0, 6.28) for _ in range(3)]
    lob = [rng.uniform(0.7, 1.15) for _ in range(lobes)]

    def rad(t):
        k = t / (2 * math.pi) * lobes
        i = int(k) % lobes
        f = k - int(k)
        bump = math.sin(math.pi * f) ** 0.35                    # fat rounded lobe, narrow notch between lobes
        r = 0.66 + 0.34 * bump * lob[i]
        r *= 1 + scallop * 0.12 * math.sin(2 * math.pi * f * 2 + ph[0])
        return r

    c = Vector(center)
    top_rows, bot_rows = [], []
    for ri in range(rings + 1):
        f = ri / rings
        n = 1 if ri == 0 else segs
        trow, brow = [], []
        for k in range(n):
            t = 2 * math.pi * k / n
            r = radius * f * (rad(t) if ri else 0)
            p = c + u * (math.cos(t) * r * squash[0]) + v * (math.sin(t) * r * squash[1])
            hit = tree.ray_cast(p - d * 30, d, 80)
            if hit[0] is None:
                continue
            h, nrm = hit[0], hit[1]
            edge = ri == rings
            th = thick * (1 - f ** 2.2) + 0.05
            th *= 1 + rng.uniform(-crumple, crumple) * (0 if edge else 2)
            trow.append(bm.verts.new(h + nrm * (th + lift)))
            brow.append(bm.verts.new(h - nrm * 0.06))
        if len(trow) == n:
            top_rows.append(trow)
            bot_rows.append(brow)
        else:
            for x in trow + brow:
                bm.verts.remove(x)
            break
    if len(top_rows) < 2:
        return [x for r in top_rows + bot_rows for x in r]
    for r in bot_rows[1:-1]:                    # hidden underside: one fan from the centre to the rim
        for x in r:
            bm.verts.remove(x)
    bot_rows = [bot_rows[0], bot_rows[-1]]
    verts = [x for r in top_rows + bot_rows for x in r]
    _faces_from(bm, top_rows, closed=True)
    _faces_from(bm, bot_rows, closed=True)
    # outer rim joins the two edges; recalc_face_normals then orients the closed shell
    rim = []
    to, bo = top_rows[-1], bot_rows[-1]
    for i in range(len(to)):
        j = (i + 1) % len(to)
        try:
            rim.append(bm.faces.new((to[i], bo[i], bo[j], to[j])))
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=list({f for x in verts for f in x.link_faces}))
    a._finish(verts, mat)
    return verts


def faces_of(verts):
    vs = set(verts)
    return [f for f in {f for v in verts if v.is_valid for f in v.link_faces} if all(x in vs for x in f.verts)]


def texture(a, verts, amp=0.09, scale=0.3, jitter=0.025, seed=0):
    """Surface texture through Tint: broad low-frequency patches (amp, patch size ~1/scale studs)
    plus a little per-face jitter, multiplied into each face's existing Tint. Never by facing."""
    from mathutils import noise
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    lay = a.tint_layer
    for f in faces_of(verts):
        c = f.calc_center_median() * scale + off
        k = 1.0 + amp * noise.noise(c) * 1.6 + rng.uniform(-jitter, jitter)
        for loop in f.loops:
            t = loop[lay][0] * k
            loop[lay] = (t, t, t, 1.0)


def paint(a, verts, key, where, seed=0):
    """Move the faces of verts into palette key where where(centre, rng) is true; for real colour
    regions (a damp base band, cooler stone patches, young leaf tips), not lighting."""
    rng = random.Random(seed)
    mi = a._mi(key)
    n = 0
    for f in faces_of(verts):
        if where(f.calc_center_median(), rng):
            f.material_index = mi
            n += 1
    return n


def refine(a, verts, cuts=1):
    """Split each face of a part into coplanar pieces (4 per triangle at cuts=1). The facets and
    silhouette stay exactly the same under flat shading, but colour blends get finer resolution.
    Returns the part's new vert list (old vertex references of ANY part go stale after this; the
    part's faces are found again through a temporary face tag)."""
    bm = a.bm
    lay = bm.faces.layers.int.get("kit_refine") or bm.faces.layers.int.new("kit_refine")
    for f in bm.faces:
        f[lay] = 0
    faces = faces_of(verts)
    for f in faces:
        f[lay] = 1
    edges = list({e for f in faces for e in f.edges})
    bmesh.ops.subdivide_edges(bm, edges=edges, cuts=cuts, use_grid_fill=True)
    mine = [f for f in bm.faces if f[lay] == 1]
    bmesh.ops.triangulate(bm, faces=mine)
    mine = [f for f in bm.faces if f[lay] == 1]
    return list({v for f in mine for v in f.verts})


def mix_hex(h1, h2, t):
    a_ = [int(h1.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    b_ = [int(h2.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a_, b_))


def mix_key(k1, k2, t):
    """A palette key t of the way from k1 to k2 (created on first use, e.g. w01_rock_x_cool_50)."""
    t = round(t, 2)
    if t <= 0:
        return k1
    if t >= 1:
        return k2
    f = fk()
    tail = k2.split("_", 1)[1] if k2.split("_", 1)[0] == k1.split("_", 1)[0] else k2
    tail = tail[len(k1.split("_", 1)[1]) + 1:] if tail.startswith(k1.split("_", 1)[1] + "_") else tail
    key = f"{k1}_x_{tail}_{int(t * 100)}"
    e1, e2 = f.palette_entry(k1), f.palette_entry(k2)
    hexcol = mix_hex(e1[0], e2[0], t)
    if f.KIT_PALETTE.get(key, (None,))[0] != hexcol:     # new, or a parent colour changed: resync
        set_colour(key, hexcol, rough=e1[1] + (e2[1] - e1[1]) * t, low_spec=k1 in f.LOW_SPEC)
    return key


def blend(a, verts, k1, k2, field, level=0.0, width=0.25, mode="blend", steps=3, jitter=0.0, seed=0):
    """Colour a surface between two palette keys by a scalar field over face centres.

    field(centre) -> value; faces above level + width/2 get k2, below level - width/2 keep k1.
    mode decides the boundary, judged per material pair:
      "hard"  - a clean edge at level (two genuinely different things meeting);
      "half"  - one 50/50 band of faces along the edge (a short soft transition);
      "blend" - a gradient over the band in `steps` mixed colours (weathering, stone variation,
                moss fading out, ripening).
    Each face stays one flat colour (that is all Roblox's palette texture can show), so the
    gradient is built across bands of faces with in-between palette keys."""
    rng = random.Random(seed)
    mis = {}
    n = 0
    for f in faces_of(verts):
        v = field(f.calc_center_median()) + (rng.uniform(-jitter, jitter) if jitter else 0.0)
        if mode == "hard":
            t = 1.0 if v > level else 0.0
        else:
            t = (v - (level - width / 2)) / width
            t = min(1.0, max(0.0, t))
            if mode == "half":
                t = 0.0 if t < 0.2 else 1.0 if t > 0.8 else 0.5
            else:
                t = round(t * (steps + 1)) / (steps + 1)
        if t <= 0:
            continue
        key = mix_key(k1, k2, t)
        if key not in mis:
            mis[key] = a._mi(key)
        f.material_index = mis[key]
        n += 1
    return n


def noise_field(scale=0.22, seed=0):
    """Broad smooth noise over position (about -0.6..0.6), for stone patches and colour drift."""
    from mathutils import noise
    r = random.Random(seed)
    off = Vector((r.uniform(0, 100), r.uniform(0, 100), r.uniform(0, 100)))
    return lambda c: noise.noise(c * scale + off)


def patches(scale=0.22, level=0.25, seed=0):
    """A where() for paint(): broad noise patches covering roughly (0.5 - level) of the surface."""
    from mathutils import noise
    r = random.Random(seed)
    off = Vector((r.uniform(0, 100), r.uniform(0, 100), r.uniform(0, 100)))
    return lambda c, rng: noise.noise(c * scale + off) > level


def moss_slab(a, center, radius, height, top_mat, side_mat, seed=1, lobes=6, band=0.3, squash=(1.0, 1.0), rot=0.0,
              peak=(0.0, 0.0), notch=0.22):
    """One moss clump as on the W01 exploded view: a thick slab with an angular lobed outline
    (pointed lobes, notches between), a vertical side band, and a low peaked top of a few big flat
    facets. Base at center.z. top_mat for the top, side_mat for the side band and underside (the
    darker stem layer). peak shifts the summit (fraction of radius). Returns (top_verts, all_verts).
    About 6 * lobes * 2 tris per ring set (~100 for 6 lobes)."""
    rng = random.Random(seed)
    bm = a.bm
    cx, cy, z0 = center
    m = Matrix.Rotation(rot, 3, "Z")
    # each lobe has a broad blunt end (two corners) and a notch after it
    outline, owner = [], []
    step = 2 * math.pi / lobes
    for k in range(lobes):
        b = k * step + rng.uniform(-0.1, 0.1) * step
        rl = radius * rng.uniform(0.88, 1.06)
        for t, r in ((b - 0.22 * step, rl * rng.uniform(0.93, 1.0)), (b + 0.22 * step, rl * rng.uniform(0.93, 1.0)),
                     (b + 0.5 * step, radius * rng.uniform(0.66, 0.76) + (0.22 - notch))):
            outline.append(m @ Vector((math.cos(t) * r * squash[0], math.sin(t) * r * squash[1], 0)))
            owner.append(k)
    n = len(outline)
    c = Vector((cx, cy, z0))
    pk = m @ Vector((peak[0] * radius * squash[0], peak[1] * radius * squash[1], 0))
    bot = [bm.verts.new(c + p * 0.94) for p in outline]
    rim = [bm.verts.new(c + p + Vector((0, 0, band * rng.uniform(0.85, 1.15)))) for p in outline]
    mid = []
    for k in range(lobes):
        lob = [outline[i] for i in range(n) if owner[i] == k][:2]
        p = (lob[0] + lob[1]) / 2
        mid.append(bm.verts.new(c + pk * 0.5 + p * rng.uniform(0.52, 0.62) +
                                Vector((0, 0, band + (height - band) * rng.uniform(0.68, 0.9)))))
    top = bm.verts.new(c + pk + Vector((0, 0, height)))
    bc = bm.verts.new(c + pk * 0.3)
    side_f, top_f = [], []
    for i in range(n):
        j = (i + 1) % n
        side_f.append(bm.faces.new((bot[i], bot[j], rim[j], rim[i])))
        side_f.append(bm.faces.new((bc, bot[j], bot[i])))
        oi, oj = owner[i], owner[j]
        if oi == oj:
            top_f.append(bm.faces.new((rim[i], rim[j], mid[oi])))
        else:                                   # notch -> next lobe: bridge the two lobe centres
            top_f.append(bm.faces.new((rim[i], rim[j], mid[oj])))
            top_f.append(bm.faces.new((rim[i], mid[oj], mid[oi])))
    for k in range(lobes):
        top_f.append(bm.faces.new((mid[k], mid[(k + 1) % lobes], top)))
    allv = bot + rim + mid + [top, bc]
    bmesh.ops.recalc_face_normals(bm, faces=side_f + top_f)
    a._finish(allv, side_mat)
    ti = a._mi(top_mat)
    for f in top_f:
        f.material_index = ti
    return [v for v in rim + mid + [top]], allv


def bvh(a):
    """A BVH of everything in the asset so far (build it before adding the piece you will conform)."""
    from mathutils.bvhtree import BVHTree
    a.bm.verts.ensure_lookup_table()
    a.bm.faces.ensure_lookup_table()
    return BVHTree.FromBMesh(a.bm)


def tag_part(a, verts, name):
    """Name a part by tagging its faces. Vertex lists go stale after any later split (refine) in
    the same asset, but face tags survive, so use part(a, name) to get the part back later."""
    lay = a.bm.faces.layers.int.get("kit_part") or a.bm.faces.layers.int.new("kit_part")
    ids = a.__dict__.setdefault("_parts", {})
    pid = ids.setdefault(name, len(ids) + 1)
    for f in faces_of(verts):
        f[lay] = pid
    return name


def part(a, name):
    """The current verts of a part tagged with tag_part()."""
    lay = a.bm.faces.layers.int.get("kit_part")
    pid = a.__dict__.get("_parts", {}).get(name)
    if lay is None or pid is None:
        return []
    return list({v for f in a.bm.faces if f[lay] == pid for v in f.verts})


def bvh_of(verts):
    """A BVH of just one part's faces (so a piece can be set on that part even under a taller one)."""
    from mathutils.bvhtree import BVHTree
    faces = faces_of(verts)
    idx = {}
    coords = []
    polys = []
    for f in faces:
        p = []
        for v in f.verts:
            if v not in idx:
                idx[v] = len(coords)
                coords.append(v.co.copy())
            p.append(idx[v])
        polys.append(p)
    return BVHTree.FromPolygons(coords, polys)


def conform(verts, tree, sink=0.12, z_from=60.0, fallback=None):
    """Set a separately modelled piece down onto a surface: each vertex keeps its own height above
    the piece's base but follows the surface under it (a slab bends over a rock crown and keeps its
    thickness). verts were built with their base at local z=0. Vertices that miss tree (hanging past
    the target part) drop onto fallback (e.g. the whole asset) instead."""
    for v in verts:
        if not v.is_valid:
            continue
        o, d = Vector((v.co.x, v.co.y, z_from)), Vector((0, 0, -1))
        h = tree.ray_cast(o, d, 200)
        if h[0] is None and fallback is not None:
            h = fallback.ray_cast(o, d, 200)
        if h[0] is not None:
            v.co.z += h[0].z - sink


def conform_side(verts, tree, centre, direction, sink=0.04, back=20.0):
    """Set a piece modelled flat (in local XY, thickness along +Z, centred on the origin) onto a
    side face: local X runs across the face, local Y up it, local Z out of it. Rays are cast along
    direction (horizontal, pointing into the rock) through `centre` (a point on or near the face)."""
    d = Vector(direction).normalized()
    u = d.cross(Vector((0, 0, 1))).normalized()
    w = u.cross(d).normalized()                 # up the face
    c = Vector(centre)
    for v in verts:
        if not v.is_valid:
            continue
        lx, ly, lz = v.co
        p = c + u * lx + w * ly
        h = tree.ray_cast(p - d * back, d, back * 3)
        if h[0] is not None:
            v.co = h[0] - d * (lz - sink)
        else:
            v.co = p - d * (lz - sink)


def top_at(a, xy, on=None):
    """Height of the top surface at xy (on one part's verts, or the whole asset), or 0."""
    tree = bvh_of(on) if on else bvh(a)
    h = tree.ray_cast(Vector((xy[0], xy[1], 60.0)), Vector((0, 0, -1)), 200)
    return h[0].z if h[0] is not None else 0.0


def hit(a, p, direction=(0, 0, -1)):
    """First surface of the asset so far hit by a ray from p (location, normal) or (None, None)."""
    from mathutils.bvhtree import BVHTree
    a.bm.verts.ensure_lookup_table()
    a.bm.faces.ensure_lookup_table()
    r = BVHTree.FromBMesh(a.bm).ray_cast(Vector(p), Vector(direction).normalized(), 200)
    return (r[0], r[1]) if r[0] is not None else (None, None)


# Leaf outlines (x along the leaf as a fraction of length, half-width as a fraction of width), base to tip
# down one side; the other side mirrors it. WorldModeling.md 6.1: narrow at the stem, widest at 0.5-0.65 L.
LEAF_OUTLINES = {
    "ovate": [(0.28, 0.42), (0.58, 0.5)],                       # 6-point broad pointed leaf (12 tris)
    "round": [(0.22, 0.44), (0.55, 0.5), (0.84, 0.32)],         # clover / moss lobe, blunt tip (16 tris)
    "lance": [(0.3, 0.42), (0.62, 0.5)],                        # use with a narrow width (0.18-0.3 L)
    "heart": [(0.12, 0.46), (0.42, 0.5), (0.75, 0.3)],          # shoulders pushed out near the base
    "strap": [(0.2, 0.46), (0.75, 0.5), (0.92, 0.34)],          # width held along the blade, rounded tip
    "disc": [(0.14, 0.42), (0.48, 0.5), (0.84, 0.36)],               # round blunt herb leaf (16 tris)
}


def leaf(a, base, length, width, mat, yaw=0.0, pitch=0.5, fold=0.12, curl=0.15, thick=0.05, shape="ovate",
         camber=0.06, notch=0.0, **_):
    """One broad solid leaf (WorldModeling.md 6.1): an outline fanned to a raised front ridge and a
    back ridge, so it is a closed shallow wedge with real thickness (12-16 tris). base = stem point;
    yaw around Z; pitch = rise from horizontal (radians); fold lifts the edges into a cup; curl bends
    the tip down; thick = back thickness; camber = front ridge height (fraction of length); notch
    pulls the base in for heart leaves."""
    bm = a.bm
    rot = Matrix.Rotation(yaw, 3, "Z") @ Matrix.Rotation(-pitch, 3, "Y")
    B = Vector(base)
    L, W = length, width
    side = LEAF_OUTLINES[shape]
    ring = [(notch * L, 0.0)] + [(f * L, -h * W) for f, h in side] + [(L, 0.0)] + [(f * L, h * W) for f, h in reversed(side)]

    def place(x, y, z):
        t = x / L
        return B + rot @ Vector((x, y, z - curl * L * t * t))

    out = [bm.verts.new(place(x, y, fold * abs(y))) for x, y in ring]
    front = bm.verts.new(place(0.52 * L, 0.0, camber * L + fold * W * 0.15))
    back = bm.verts.new(place(0.52 * L, 0.0, -thick))
    n = len(out)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((front, out[i], out[j]))
        bm.faces.new((back, out[j], out[i]))
    verts = out + [front, back]
    a._finish(verts, mat)
    return verts


CLOVER_TIERS = ((8, 0.05, 0.85, (0.32, 0.55)), (6, 0.38, 0.72, (0.7, 1.0)), (4, 0.7, 0.55, (0.95, 1.25)))


def clover(a, loc, size, seed, leaf_mat, flowers=0, petal="w01_petal", pollen="w01_pollen",
           shape="round", height=1.0, tiers=CLOVER_TIERS, leaf_size=1.0, young_mat=None):
    """Leafy mound: tiers of broad rounded leaves fanning out from the clump centre, wide and low
    outside, steeper and higher in the middle (W01 clover, ground cover). No stems show.
    size ~ clump radius in studs. tiers = (count, base height frac, length frac, pitch range).
    young_mat colours the inner, newer leaves (a lighter, yellower green) when given."""
    rng = random.Random(seed)
    x0, y0, z0 = loc
    out = []
    for ti, (n, hz, lf, (p0, p1)) in enumerate(tiers):
        ly = rng.uniform(0, 6.28)
        # old outer leaves -> half-and-half middle tier -> young inner leaves (a stepped, not abrupt, change)
        mat = leaf_mat
        if young_mat and len(tiers) > 1:
            t = ti / (len(tiers) - 1)
            mat = mix_key(leaf_mat, young_mat, 0.0 if t < 0.25 else 1.0 if t > 0.75 else 0.5)
        for k in range(n):
            yaw = ly + 2 * math.pi * k / n + rng.uniform(-0.3, 0.3)
            L = size * lf * leaf_size * rng.uniform(0.85, 1.05)
            base = (x0 + math.cos(yaw) * size * 0.08, y0 + math.sin(yaw) * size * 0.08, z0 + size * height * hz)
            out += leaf(a, base, L, L * rng.uniform(0.72, 0.85), mat, yaw=yaw, pitch=rng.uniform(p0, p1),
                        fold=0.22, curl=0.3, thick=0.04 * size, shape=shape)
    for f in range(flowers):
        yaw = rng.uniform(0, 6.28)
        r = size * rng.uniform(0.25, 0.45)
        daisy(a, (x0 + math.cos(yaw) * r, y0 + math.sin(yaw) * r, z0 + size * height * rng.uniform(0.7, 0.85)),
              size * 0.5, seed + 31 * f, petal, pollen, petals=7)
    return out


def daisy(a, loc, radius, seed, petal_mat, centre_mat, petals=6, tilt=0.25):
    """Flat white daisy: petals radiating round a domed yellow centre, tilted a little."""
    rng = random.Random(seed)
    yaw0 = rng.uniform(0, 6.28)
    for k in range(petals):
        yaw = yaw0 + 2 * math.pi * k / petals
        leaf(a, (loc[0], loc[1], loc[2]), radius, radius * 0.55, petal_mat, yaw=yaw, pitch=tilt * math.cos(yaw - yaw0) + 0.08,
             fold=0.05, curl=0.1, thick=0.04, shape="ovate")
    a.cyl(radius * 0.3, radius * 0.18, radius * 0.22, sides=6, loc=(loc[0], loc[1], loc[2] - 0.02), mat=centre_mat)


def tag(o, sheet, subject, role, collision="hull", budget=None, notes=""):
    kit = NS["KIT"]
    o["kit_sheet"] = sheet
    o["kit_subject"] = subject
    o["kit_role"] = role
    o["kit_collision"] = collision
    o["kit_budget"] = int(budget or kit["BUDGET"][role])
    if notes:
        o["kit_notes"] = notes
    if o.asset_data:
        have = [x.name for x in o.asset_data.tags]
        for t in (sheet, subject, role):
            if t not in have:
                o.asset_data.tags.new(t)
    return o


def mk(sheet, name, fn, subject=None, role=None, notes=None, budget=None, collision=None, fx=(),
       keep_fx=False, tint_var=0.05, seed=7):
    """Build (or rebuild in place) one kit asset.

    fn(a) adds geometry to a flintkit.Asset. fx = [(kind, loc, overrides), ...] in the same build
    coordinates as fn (shifted with the bottom-centre origin). An existing object of that name keeps
    its location, subject, role, notes, collision and budget unless given; keep_fx also carries its
    old sockets over at their local positions."""
    old = bpy.data.objects.get(name)
    meta = {}
    old_fx = []
    loc = (0, 0, 0)
    coll = sheet_coll(sheet)
    if old:
        loc = tuple(old.location)
        meta = {k: old.get(k) for k in ("kit_subject", "kit_role", "kit_notes", "kit_collision", "kit_budget")}
        old_fx = [(c.get("vfx_kind"), tuple(c.location), c.scale[0]) for c in old.children if c.get("vfx_kind")]
        for c in list(old.children_recursive):
            bpy.data.objects.remove(c, do_unlink=True)
        coll = old.users_collection[0]
        bpy.data.objects.remove(old, do_unlink=True)
    a = fk().Asset(name, f"{sheet} {subject or meta.get('kit_subject')}", seed=seed, tint_var=tint_var)
    fn(a)
    xs = [v.co.x for v in a.bm.verts]
    ys = [v.co.y for v in a.bm.verts]
    zs = [v.co.z for v in a.bm.verts]
    off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
    o = a.finish(collection=coll, location=loc)
    drop_unused_slots(o)
    if "kit_part" in o.data.attributes:              # authoring-only tags, not exported
        o.data.attributes.remove(o.data.attributes["kit_part"])
    tag(o, sheet, subject or meta.get("kit_subject"), role or meta.get("kit_role"),
        collision or meta.get("kit_collision") or "hull", budget or meta.get("kit_budget"),
        notes if notes is not None else (meta.get("kit_notes") or ""))
    bpy.context.view_layer.update()
    for kind, p, *kw in fx:
        socket(o, kind, Vector(p) - off, **(kw[0] if kw else {}))
    if keep_fx and not fx:
        for kind, p, sc in old_fx:
            socket(o, kind, p, scale=sc)
    return o


def drop_unused_slots(o):
    """Remove material slots no face uses (e.g. a host stripped off a part)."""
    me = o.data
    used = sorted({p.material_index for p in me.polygons})
    if len(used) == len(me.materials):
        return
    remap = {old: new for new, old in enumerate(used)}
    for p in me.polygons:
        p.material_index = remap[p.material_index]
    keep = [me.materials[i] for i in used]
    me.materials.clear()
    for m in keep:
        me.materials.append(m)


def row_objs(sheet, subject):
    """A subject's assets ordered hero, parts, variants, drops, depleted."""
    order = {"hero": 0, "part": 1, "variant": 2, "drop": 3, "depleted": 4}
    objs = [o for o in sheet_coll(sheet).objects if o.type == "MESH" and o.get("kit_subject") == subject]
    return sorted(objs, key=lambda o: (order.get(o.get("kit_role"), 9), o.get("kit_order", 0)))


def _frame_box_min(corners, azimuth, elevation):
    kit = NS["KIT"]
    m = NS.get("FRAME_MIN")
    if m:
        xs = [c.x for c in corners]
        ys = [c.y for c in corners]
        zs = [c.z for c in corners]
        cx, cy, z0 = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)
        sx, sy, sz = m
        corners = list(corners) + [Vector((cx + dx * sx / 2, cy + dy * sy / 2, z0 + dz * sz))
                                   for dx in (-1, 1) for dy in (-1, 1) for dz in (0, 1)]
    return kit["frame_box_orig"](corners, azimuth, elevation)


def render_row(sheet, module, row, subject, objs=None, vfx=True, frame_hero=False, **camera):
    """Render the subject's cells and its compare image (reference row above ours).

    camera: HERO_AZIMUTH, HERO_ELEVATION, SIDE_AZIMUTH as in the module contract.
    frame_hero frames hero and variants at least at the hero's size (true relative scale).
    Returns the compare image path."""
    kit = NS["KIT"]
    bpy.context.view_layer.update()       # rebuilt objects: refresh world matrices before framing
    objs = objs or row_objs(sheet, subject)
    M = type("M", (), dict(MODULE=module, ROW=row, SUBJECT=subject, **camera))
    if "frame_box_orig" not in kit:
        kit["frame_box_orig"] = kit["frame_box"]
    kit["frame_box"] = _frame_box_min
    hero = next((o for o in objs if o.get("kit_role") == "hero"), objs[0])
    orig = kit["render_group"]

    def rg(group, path, azimuth=-22, elevation=20):
        if frame_hero and any(s in path for s in ("1_hero", "2_front", "3_side", "6_variant")):
            NS["FRAME_MIN"] = tuple(hero.dimensions)
        try:
            return orig(group, path, azimuth, elevation)
        finally:
            NS["FRAME_MIN"] = None

    kit["render_group"] = rg
    sc = bpy.context.scene
    try:
        if vfx:
            kit["vfx"].clear(sc)
            kit["vfx"].realize(sc, objs)
        kit["render_subject"](sheet, M, objs)
    finally:
        kit["render_group"] = orig
        kit["frame_box"] = kit["frame_box_orig"]
        if vfx:
            kit["vfx"].clear(sc)
    return os.path.join(kit["RENDER_DIR"], sheet, f"{module}_compare.png")


def crop(src, box, out, scale=2):
    """Crop box=(x0, y0, x1, y1) (pixels, top-left origin) from a PNG and save it scaled up
    (nearest) for a close look. Works on reference sheets and our own cells."""
    import numpy as np
    kit = NS["KIT"]
    px = kit["load_px"](src)          # rows bottom-up, as Blender stores them
    h = px.shape[0]
    x0, y0, x1, y1 = box
    c = px[h - y1:h - y0, x0:x1]
    if scale > 1:
        c = np.repeat(np.repeat(c, scale, axis=0), scale, axis=1)
    kit["save_px"](c, out)
    return out


def sample(src, box, kind="green"):
    """Median sRGB (0-255) of the pixels inside box=(x0, y0, x1, y1) (top-left origin) that look
    like `kind`: green (moss, leaves, grass), stone (low-saturation), brown, or all. Also returns the
    25th/75th percentile brightness so lit and shaded tones can be compared, and the pixel count."""
    import numpy as np
    kit = NS["KIT"]
    px = kit["load_px"](src)
    h = px.shape[0]
    x0, y0, x1, y1 = box
    c = px[h - y1:h - y0, x0:x1, :3].reshape(-1, 3)

    def to_srgb(v):
        v = np.clip(v, 0, 1)
        return np.where(v <= 0.0031308, v * 12.92, 1.055 * np.power(v, 1 / 2.4) - 0.055)
    s = to_srgb(c) * 255                       # Blender loads PNGs as linear floats
    r, g, b = s[:, 0], s[:, 1], s[:, 2]
    mx, mn = s.max(axis=1), s.min(axis=1)
    sat = (mx - mn) / np.maximum(mx, 1)
    if kind == "green":
        m = (g > r + 8) & (g > b + 25) & (sat > 0.3)
    elif kind == "stone":
        m = (sat < 0.18) & (mx > 60) & (mx < 245)
    elif kind == "brown":
        m = (r > g + 15) & (g > b) & (sat > 0.3)
    else:
        m = np.ones(len(s), bool)
    sel = s[m]
    if len(sel) == 0:
        return {"n": 0}
    lum = sel.mean(axis=1)
    lo, hi = np.percentile(lum, 25), np.percentile(lum, 75)
    return {"n": int(len(sel)), "median": [int(x) for x in np.median(sel, axis=0)],
            "dark": [int(x) for x in np.median(sel[lum <= lo], axis=0)],
            "light": [int(x) for x in np.median(sel[lum >= hi], axis=0)]}


def calibrate(targets, iters=4, out_dir=None):
    """Match palette keys to the master sheet AS RENDERED. targets = {key: ((r, g, b) sRGB median
    sampled from the reference with sample(), kind)}. Each key is put on a faceted test dome, rendered
    with the kit studio and hero camera, sampled the same way, and its base colour corrected in linear
    light (rendered/target ratio per channel) for a few rounds. Returns {key: (hex, rendered median)}."""
    import numpy as np
    kit = NS["KIT"]
    f = fk()
    out_dir = out_dir or SCRATCH
    os.makedirs(out_dir, exist_ok=True)

    def lin(c):
        c = c / 255.0
        return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

    def srgb(v):
        v = np.clip(v, 0, 1)
        return np.where(v <= 0.0031308, v * 12.92, 1.055 * np.power(v, 1 / 2.4) - 0.055) * 255

    res = {}
    for key, (target, kind) in targets.items():
        name = "T_Calib"
        for it in range(iters + 1):
            o = test_asset(name, lambda a: hull_rock(a, (4.0, 3.6, 2.6), seed=7, mat=key, rings=DOME))
            p = kit["render_group"]([o], os.path.join(out_dir, f"_calib_{key}.png"), -22, 22)
            got = sample(p, (60, 40, 260, 200), kind)
            if not got.get("n"):
                break
            g = np.array(got["median"], float)
            if it == iters or np.abs(g - np.array(target)).max() < 6:
                break
            hexcol = f.palette_entry(key)[0]
            base = np.array([int(hexcol.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)], float)
            new_lin = lin(base) * (lin(np.array(target, float)) + 1e-4) / (lin(g) + 1e-4)
            new = srgb(np.clip(new_lin, 0, 1))
            e = f.palette_entry(key)
            set_colour(key, "#" + "".join(f"{int(round(x)):02X}" for x in new), rough=e[1], metal=e[2], emit=e[3],
                       low_spec=key in f.LOW_SPEC)
        res[key] = (f.palette_entry(key)[0], got.get("median"))
        ob = bpy.data.objects.get(name)
        if ob:
            bpy.data.objects.remove(ob, do_unlink=True)
    return res


def ref_sheet(sheet):
    d = REPO + "/art/reference/kit"
    return d + "/" + next(f for f in os.listdir(d) if f.startswith(sheet + "_") and f.endswith(".png"))


SCRATCH = "C:/Users/Orang/AppData/Local/Temp/claude/D--Projects-Roblox-RBLX-Flintborn/kitlook/"


def look(objs, name, views=((-22, 20), (0, 6), (90, 6), (0, 89)), cell=(560, 420), vfx=False, out_dir=None):
    """Quick large look at objects: a 2-column sheet of views (azimuth, elevation). Returns the path."""
    kit = NS["KIT"]
    objs = objs if isinstance(objs, (list, tuple)) else [objs]
    out_dir = out_dir or SCRATCH
    os.makedirs(out_dir, exist_ok=True)
    old = kit["CELL"]
    kit["CELL"] = cell
    sc = bpy.context.scene
    paths = []
    try:
        if vfx:
            kit["vfx"].clear(sc)
            kit["vfx"].realize(sc, objs)
        for i, (az, el) in enumerate(views):
            paths.append(kit["render_group"](objs, os.path.join(out_dir, f"_{name}_{i}.png"), az, el))
    finally:
        kit["CELL"] = old
        if vfx:
            kit["vfx"].clear(sc)
    rows = [kit["hstack"](paths[i:i + 2]) for i in range(0, len(paths), 2)]
    out = os.path.join(out_dir, f"{name}.png")
    kit["save_px"](kit["vstack"](rows) if len(rows) > 1 else rows[0], out)
    return out


def test_asset(name, fn, seed=7, tint_var=0.05):
    """Build fn into a throwaway object in the _wip collection (replacing one of that name)."""
    coll = bpy.data.collections.get("_wip")
    if not coll:
        coll = bpy.data.collections.new("_wip")
        bpy.context.scene.collection.children.link(coll)
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    a = fk().Asset(name, "wip", seed=seed, tint_var=tint_var)
    fn(a)
    o = a.finish(collection=coll, mark_asset=False)
    o.location = (0, -400, 0)
    bpy.context.view_layer.update()
    return o


def focus(names, shading="MATERIAL"):
    """Open models in the Blender viewport on their own (local view, framed, material preview) so
    the work can be watched and checked in the GUI, not only in renders."""
    win = bpy.context.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == "VIEW_3D")
    region = next(r for r in area.regions if r.type == "WINDOW")
    names = [names] if isinstance(names, str) else list(names)
    with bpy.context.temp_override(window=win, area=area, region=region):
        if area.spaces[0].local_view:
            bpy.ops.view3d.localview(frame_selected=False)
        for o in bpy.context.view_layer.objects:
            o.select_set(False)
        objs = [bpy.data.objects[n] for n in names]
        for o in objs:
            o.hide_set(False)
            o.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        bpy.ops.view3d.localview(frame_selected=True)
        area.spaces[0].shading.type = shading
    return names


def check(objs):
    kit = NS["KIT"]
    probs = []
    for o in objs:
        kit["check"](o, probs)
    return probs


def stats(objs):
    return [(o.name, o.get("kit_role"), sum(len(p.vertices) - 2 for p in o.data.polygons), o.get("kit_budget"),
             tuple(round(d, 1) for d in o.dimensions), [m.name[3:] for m in o.data.materials],
             [c.get("vfx_kind") for c in o.children if c.get("vfx_kind")]) for o in objs]


def restore_palette():
    """Re-register sheet palette keys from the saved FB_ materials (KIT_PALETTE resets with Blender)."""
    f = fk()
    added = []
    for mat in bpy.data.materials:
        key = mat.get("flintkit_key") or (mat.name[3:] if mat.name.startswith("FB_") else None)
        if not key or key in f.PALETTE or key in f.KIT_PALETTE or "flintkit_hex" not in mat:
            continue
        spec = list(mat.get("flintkit_spec", [0.9, 0.0, 0.0]))
        f.KIT_PALETTE[key] = (mat["flintkit_hex"], *spec)
        bsdf = mat.node_tree.nodes.get("Principled BSDF") if mat.node_tree else None
        if bsdf and "Specular IOR Level" in bsdf.inputs and abs(bsdf.inputs["Specular IOR Level"].default_value - 0.2) < 1e-3:
            f.LOW_SPEC.add(key)
        added.append(key)
    return added


def install():
    load_kit()
    restore_palette()
    NS.update(set_colour=set_colour, sheet_coll=sheet_coll, socket=socket, hull_rock=hull_rock, tag=tag,
              mk=mk, row_objs=row_objs, render_row=render_row, check=check, stats=stats, DOME=DOME,
              crop=crop, ref_sheet=ref_sheet, sample=sample, calibrate=calibrate, pebble=pebble, drape=drape, leaf=leaf, clover=clover, daisy=daisy,
              look=look, test_asset=test_asset, focus=focus, bvh=bvh, bvh_of=bvh_of, tag_part=tag_part, part=part, top_at=top_at, conform_side=conform_side, conform=conform, moss_slab=moss_slab,
              blend=blend, mix_key=mix_key, refine=refine, texture=texture)
    return sorted(k for k in ("set_colour", "sheet_coll", "socket", "hull_rock", "tag", "mk", "row_objs",
                              "render_row", "check", "stats"))
