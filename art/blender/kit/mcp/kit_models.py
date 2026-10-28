"""Tools for the numbered model references (art/blender/assets/references/NNN.png, one production study per
model; INDEX.md there maps numbers to names), following the roblox-blender-model skill.

Each model lives in FlintbornWorldKit.blend under Kit/"M<NNN> <Name>", tagged kit_sheet = "M<NNN>", so the
kit studio, checks and exporter work unchanged:
    BLENDER_ARGS="art/blender/assets/kit/FlintbornWorldKit.blend --sheet M001" \
        art/blender/run.sh scripts/export_kit_roblox.py art/roblox/models/M001/manifest.json

    import sys; sys.path.insert(0, ".../art/blender/kit/mcp")
    import kit_mcp, kit_models; kit_mcp.install()
"""
import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.kdtree import KDTree

import kit_mcp as K

MODEL_REFS = K.REPO + "/art/blender/assets/references"
MODEL_RENDERS = K.REPO + "/art/blender/renders/models"


def ref(num):
    return f"{MODEL_REFS}/{num:03d}.png"


def code(num):
    return f"M{num:03d}"


def coll(num, title):
    """The model's collection under Kit ("M001 Stone"), created on first use."""
    kit = bpy.data.collections["Kit"]
    c = next((c for c in kit.children if c.name.split(" ")[0] == code(num)), None)
    if not c:
        c = bpy.data.collections.new(f"{code(num)} {title}")
        kit.children.link(c)
    return c


def mk(sheet, name, fn, **kw):
    """kit_mcp.mk, but never rebuilds an object that belongs to another sheet: if `name` is already taken by
    another sheet's asset (e.g. a kit row's FlintInsertSmall), the model's own copy gets the model code
    appended (FlintInsertSmallM002)."""
    old = bpy.data.objects.get(name)
    if old and old.get("kit_sheet") not in (None, sheet):
        name = f"{name}{sheet}"
    return K.mk(sheet, name, fn, **kw)


def raw_sample(path, box):
    """Median true sRGB (0-255) of a box (x0, y0, x1, y1, top-left origin) - for flat swatches."""
    px = K.NS["KIT"]["load_px"](path)
    h = px.shape[0]
    x0, y0, x1, y1 = box
    c = px[h - y1:h - y0, x0:x1, :3].reshape(-1, 3)
    return [int(v) for v in np.median(c, axis=0) * 255]


def sample(path, box, kind="stone", paper=(238, 234, 227), tol=22):
    """kit_mcp.sample, but pixels within tol of the sheet paper / studio floor colour are dropped first (the
    stone filter otherwise counts the near-white background). True sRGB 0-255."""
    px = K.NS["KIT"]["load_px"](path)
    h = px.shape[0]
    x0, y0, x1, y1 = box
    s = np.clip(px[h - y1:h - y0, x0:x1, :3].reshape(-1, 3), 0, 1) * 255
    s = s[np.abs(s - np.array(paper)).max(axis=1) > tol]
    r, g, b = s[:, 0], s[:, 1], s[:, 2]
    mx, mn = s.max(axis=1), s.min(axis=1)
    sat = (mx - mn) / np.maximum(mx, 1)
    m = {"green": (g > r + 8) & (g > b + 25) & (sat > 0.3), "stone": (sat < 0.25) & (mx > 40),
         "brown": (r > g + 15) & (g > b) & (sat > 0.3), "all": np.ones(len(s), bool)}[kind]
    sel = s[m]
    if not len(sel):
        return {"n": 0}
    lum = sel.mean(axis=1)
    lo, hi = np.percentile(lum, 25), np.percentile(lum, 75)
    hexs = lambda c: "#" + "".join(f"{int(x):02X}" for x in c)
    med = np.median(sel, axis=0)
    return {"n": int(len(sel)), "median": [int(x) for x in med], "hex": hexs(med),
            "dark": [int(x) for x in np.median(sel[lum <= lo], axis=0)],
            "light": [int(x) for x in np.median(sel[lum >= hi], axis=0)]}


def _override(o):
    """Context for mesh operators on o: o active and the only selection, in the 3D viewport's window region."""
    for ob in bpy.context.view_layer.objects:
        ob.select_set(False)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    win = bpy.context.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == "VIEW_3D")
    region = next(r for r in area.regions if r.type == "WINDOW")
    if area.spaces[0].local_view:            # objects outside local view can't enter Edit mode
        with bpy.context.temp_override(window=win, area=area, region=region):
            bpy.ops.view3d.localview(frame_selected=False)
    o.hide_set(False)
    return bpy.context.temp_override(window=win, area=area, region=region, active_object=o, object=o,
                                     selected_objects=[o], selected_editable_objects=[o])


def union_loose(o, merge=0.01):
    """Boolean-union an object's separate closed shells into one manifold surface (no interior faces where parts
    interpenetrate). Materials and the Tint attribute carry over from each shell. Returns the shell count merged."""
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    others = split_loose(o)
    for p in others:
        m = o.modifiers.new("U", "BOOLEAN")
        m.operation, m.solver, m.object = "UNION", "EXACT", p
        m.material_mode = "TRANSFER"
        with _override(o):
            bpy.ops.object.modifier_apply(modifier=m.name)
        bpy.data.objects.remove(p, do_unlink=True)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=merge)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=merge)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    drop_specks(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    repair_nonmanifold(o)
    K.drop_unused_slots(o)
    return len(others)


def _build_offset(build_fn):
    """The bottom-centre offset kit_mcp.mk shifts an asset by: found from a probe build of build_fn."""
    probe = K.fk().Asset("_probe", "probe")
    build_fn(probe)
    xs, ys, zs = ([v.co[i] for v in probe.bm.verts] for i in range(3))
    probe.bm.free()
    return Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))


def _placed(o, build_fn, fn, name):
    """fn's geometry as a temporary object lined up with o, which mk built from build_fn."""
    a = K.fk().Asset(name, "probe")
    fn(a)
    c = a.finish(collection=o.users_collection[0], mark_asset=False, origin=None)
    c.matrix_world = o.matrix_world @ Matrix.Translation(-_build_offset(build_fn))
    return c


def merge_in(o, build_fn, fn):
    """Join more geometry (fn, in the same build coordinates as build_fn, which built o) into o, e.g. what goes
    inside a cavity carve() cut. Union it afterwards with union_loose; finish() recentres the origin."""
    c = _placed(o, build_fn, fn, "_merge")
    with _override(o):
        c.select_set(True)
        with bpy.context.temp_override(selected_objects=[o, c], selected_editable_objects=[o, c]):
            bpy.ops.object.join()


def carve(o, build_fn, cutter_fn):
    """Exact boolean difference of a cutter from a built asset; the new cut faces take the cutter's materials (and
    Tint). Both functions add geometry to a flintkit.Asset in the same build coordinates; the cutter is placed by
    the asset's bottom-centre offset, found from a probe build of build_fn."""
    c = _placed(o, build_fn, cutter_fn, "_cutter")
    m = o.modifiers.new("Carve", "BOOLEAN")
    m.operation, m.solver, m.object = "DIFFERENCE", "EXACT", c
    m.use_self = True
    m.material_mode = "TRANSFER"
    with _override(o):
        bpy.ops.object.modifier_apply(modifier=m.name)
    me = c.data
    bpy.data.objects.remove(c, do_unlink=True)
    bpy.data.meshes.remove(me)
    K.drop_unused_slots(o)


def drop_specks(bm, min_area=0.3):
    """Delete specks: tiny closed slivers booleans and cleanup can leave where several shells meet inside a mesh."""
    bm.faces.index_update()
    ids, n = _shell_ids(bm)
    area = [0.0] * n
    for f in bm.faces:
        area[ids[f.index]] += f.calc_area()
    specks = [f for f in bm.faces if area[ids[f.index]] < min_area]
    if specks:
        bmesh.ops.delete(bm, geom=specks, context="FACES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    return len(specks)


def _shell_ids(bm):
    """Face index -> shell number."""
    ids, n = {}, 0
    for f in bm.faces:
        if f.index in ids:
            continue
        stack = [f]
        ids[f.index] = n
        while stack:
            g = stack.pop()
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in ids:
                        ids[h.index] = n
                        stack.append(h)
        n += 1
    return ids, n


def split_loose(o):
    """Move every shell but the first out of o into its own temporary object (same materials and attributes,
    same transform). Pure bmesh, so it works from any mode/context. Returns the new objects."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    ids, n = _shell_ids(bm)
    bm.free()
    out = []
    for k in range(1, n):
        me = o.data.copy()
        b = bmesh.new()
        b.from_mesh(me)
        b.faces.ensure_lookup_table()
        bmesh.ops.delete(b, geom=[f for f in b.faces if ids[f.index] != k], context="FACES")
        b.to_mesh(me)
        b.free()
        p = bpy.data.objects.new(f"{o.name}_shell{k}", me)
        p.matrix_world = o.matrix_world
        o.users_collection[0].objects.link(p)
        out.append(p)
    b = bmesh.new()
    b.from_mesh(o.data)
    b.faces.ensure_lookup_table()
    bmesh.ops.delete(b, geom=[f for f in b.faces if ids[f.index] != 0], context="FACES")
    b.to_mesh(o.data)
    b.free()
    return out


def repair_nonmanifold(o, tries=3):
    """Exact booleans can leave an edge shared by four faces where two shells only graze each other (two
    sliver faces meeting the edge). Delete the smallest faces on such edges, re-fill the holes, and repeat.
    Returns the number of non-manifold edges left."""
    for _ in range(tries):
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bad = [e for e in bm.edges if len(e.link_faces) > 2]
        if not bad:
            bm.free()
            return 0
        kill = set()
        for e in bad:
            fs = sorted(e.link_faces, key=lambda f: f.calc_area())
            kill.update(fs[:len(fs) - 2])
        bmesh.ops.delete(bm, geom=list(kill), context="FACES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        bnd = [e for e in bm.edges if e.is_boundary]
        if bnd:
            bmesh.ops.holes_fill(bm, edges=bnd)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(o.data)
        bm.free()
    bm = bmesh.new()
    bm.from_mesh(o.data)
    n = sum(1 for e in bm.edges if not e.is_manifold)
    bm.free()
    return n


def _shells(bm):
    seen, n = set(), 0
    for f in bm.faces:
        if f in seen:
            continue
        n += 1
        stack = [f]
        seen.add(f)
        while stack:
            g = stack.pop()
            for e in g.edges:
                for h in e.link_faces:
                    if h not in seen:
                        seen.add(h)
                        stack.append(h)
    return n


def audit(o):
    """The skill's 2d inspection for one object: counts, non-manifold / boundary / wire edges, loose verts,
    zero-area faces, duplicate verts, n-gons, shells, outward normals, origin, size, materials, UVs."""
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    kd = KDTree(len(bm.verts))
    for i, v in enumerate(bm.verts):
        kd.insert(v.co, i)
    kd.balance()
    dup = sum(1 for v in bm.verts if len(kd.find_range(v.co, 0.0005)) > 1)
    vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in bm.faces) / 3.0
    res = {"name": o.name, "tris": sum(len(f.verts) - 2 for f in bm.faces), "faces": len(bm.faces),
           "verts": len(bm.verts), "ngons": sum(1 for f in bm.faces if len(f.verts) > 4),
           "nonmanifold_edges": sum(1 for e in bm.edges if not e.is_manifold),
           "boundary_edges": sum(1 for e in bm.edges if e.is_boundary),
           "wire_edges": sum(1 for e in bm.edges if e.is_wire),
           "loose_verts": sum(1 for v in bm.verts if not v.link_faces),
           "zero_area_faces": sum(1 for f in bm.faces if f.calc_area() < 1e-6),
           "dup_verts": dup, "shells": _shells(bm), "normals": "outward" if vol > 0 else "INWARD"}
    bm.free()
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    res.update({"size": [round(d, 2) for d in o.dimensions],
                "origin_offset": [round((min(xs) + max(xs)) / 2, 3), round((min(ys) + max(ys)) / 2, 3), round(min(zs), 3)],
                "custom_normals": me.has_custom_normals, "materials": [m.name for m in me.materials],
                "uv_layers": [u.name for u in me.uv_layers], "modifiers": [m.name for m in o.modifiers],
                "transforms_applied": tuple(o.rotation_euler) == (0, 0, 0) and tuple(o.scale) == (1, 1, 1)})
    return res


def _uv_islands(bm, uv, eps=1e-5):
    """Faces grouped into UV islands: neighbours across an edge share an island when both edge ends have the same
    UVs on both sides."""
    parent = list(range(len(bm.faces)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for e in bm.edges:
        if len(e.link_faces) != 2:
            continue
        f1, f2 = e.link_faces
        a = {l.vert: l[uv].uv for l in f1.loops}
        b = {l.vert: l[uv].uv for l in f2.loops}
        if all((a[v] - b[v]).length < eps for v in e.verts):
            parent[find(f1.index)] = find(f2.index)
    return [find(f.index) for f in bm.faces]


def _tri_overlap(t1, t2, eps=1e-7):
    """Two 2D triangles overlap with positive area (separating axis test; touching edges don't count)."""
    for tri in (t1, t2):
        for i in range(3):
            a, b = tri[i], tri[(i + 1) % 3]
            n = (b[1] - a[1], a[0] - b[0])
            p1 = [n[0] * p[0] + n[1] * p[1] for p in t1]
            p2 = [n[0] * p[0] + n[1] * p[1] for p in t2]
            if max(p1) <= min(p2) + eps or max(p2) <= min(p1) + eps:
                return False
    return True


def _seg_dist(p1, p2, q1, q2):
    def pd(p, a, b):
        ab = b - a
        t = 0.0 if ab.length_squared == 0 else max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
        return (p - (a + ab * t)).length

    def side(o, a, b):
        return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x)
    if side(q1, q2, p1) * side(q1, q2, p2) < 0 and side(p1, p2, q1) * side(p1, p2, q2) < 0:
        return 0.0
    return min(pd(p1, q1, q2), pd(p2, q1, q2), pd(q1, p1, p2), pd(q2, p1, p2))


def uv_stats(o, cell=0.05):
    """Stage 3 measurements of the active UV layer (faces are fanned into triangles):
    islands; overlapping triangle pairs (and how many cross islands); flipped triangles; the minimum gap between
    islands and to the 0-1 border; texel density per island (UV area / 3D area, relative to the whole mesh:
    min / median / max); and stretch per triangle: conformal (largest / smallest singular value of the 3D -> UV
    map, 1 = no shear), area (UV / 3D area against the mesh average, worse of r and 1/r) and the worst corner-angle
    change in degrees."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    uv = bm.loops.layers.uv.active
    if uv is None or not bm.faces:
        bm.free()
        return {"name": o.name, "uv_layer": None}
    isl = _uv_islands(bm, uv)
    tris = []
    for f in bm.faces:
        ls = list(f.loops)
        for i in range(1, len(ls) - 1):
            t = (ls[0], ls[i], ls[i + 1])
            tris.append((f.index, [l[uv].uv.copy() for l in t], [l.vert.co.copy() for l in t]))
    area3 = {}
    areau = {}
    rows = []
    for fi, u, p in tris:
        e1, e2 = p[1] - p[0], p[2] - p[0]
        n = e1.cross(e2)
        a3 = n.length / 2
        au = ((u[1].x - u[0].x) * (u[2].y - u[0].y) - (u[1].y - u[0].y) * (u[2].x - u[0].x)) / 2
        k = isl[fi]
        area3[k] = area3.get(k, 0.0) + a3
        areau[k] = areau.get(k, 0.0) + abs(au)
        if a3 < 1e-12:
            continue
        x = e1.normalized()
        y = n.normalized().cross(x)
        s1, s2 = (e1.dot(x), e1.dot(y)), (e2.dot(x), e2.dot(y))
        t1, t2 = u[1] - u[0], u[2] - u[0]
        det = s1[0] * s2[1] - s2[0] * s1[1]
        i00, i01, i10, i11 = s2[1] / det, -s2[0] / det, -s1[1] / det, s1[0] / det
        a, b = t1.x * i00 + t2.x * i10, t1.x * i01 + t2.x * i11
        c, d = t1.y * i00 + t2.y * i10, t1.y * i01 + t2.y * i11
        E, F, G = a * a + c * c, a * b + c * d, b * b + d * d
        root = math.sqrt(max(0.0, (E - G) ** 2 + 4 * F * F))
        smax, smin = math.sqrt(max(0.0, (E + G + root) / 2)), math.sqrt(max(0.0, (E + G - root) / 2))
        angles3 = [(p[(i + 2) % 3] - p[i]).angle(p[(i + 1) % 3] - p[i], 0.0) for i in range(3)]
        uv3 = [Vector((q.x, q.y, 0.0)) for q in u]
        anglesu = [(uv3[(i + 2) % 3] - uv3[i]).angle(uv3[(i + 1) % 3] - uv3[i], 0.0) for i in range(3)]
        rows.append((smax / smin if smin > 1e-12 else math.inf, abs(au) / a3, a * d - b * c < 0,
                     max(abs(i - j) for i, j in zip(angles3, anglesu))))
    g = sum(areau.values()) / sum(area3.values())
    dens = sorted(areau[k] / area3[k] / g for k in area3 if area3[k] > 0)
    # overlaps: triangles bucketed on a grid by their UV bounding boxes
    boxes = [(min(q.x for q in u), min(q.y for q in u), max(q.x for q in u), max(q.y for q in u)) for _, u, _ in tris]
    grid = {}
    for k, bx in enumerate(boxes):
        for i in range(int(bx[0] // cell), int(bx[2] // cell) + 1):
            for j in range(int(bx[1] // cell), int(bx[3] // cell) + 1):
                grid.setdefault((i, j), []).append(k)
    pairs = {(a, b) for lst in grid.values() for ii, a in enumerate(lst) for b in lst[ii + 1:]
             if tris[a][0] != tris[b][0]}
    overlaps = cross = 0
    for a, b in pairs:
        A, B = boxes[a], boxes[b]
        if A[2] <= B[0] or B[2] <= A[0] or A[3] <= B[1] or B[3] <= A[1]:
            continue
        if _tri_overlap([(q.x, q.y) for q in tris[a][1]], [(q.x, q.y) for q in tris[b][1]]):
            overlaps += 1
            cross += isl[tris[a][0]] != isl[tris[b][0]]
    # gaps: island boundary edges, bucketed with a gap-sized pad
    edges = []
    for f in bm.faces:
        for l in f.loops:
            other = [x for x in l.edge.link_faces if x is not f]
            if not other or isl[other[0].index] != isl[f.index]:
                edges.append((isl[f.index], l[uv].uv.copy(), l.link_loop_next[uv].uv.copy()))
    pad = 0.02
    eg = {}
    for k, (_, a, b) in enumerate(edges):
        for i in range(int((min(a.x, b.x) - pad) // pad), int((max(a.x, b.x) + pad) // pad) + 1):
            for j in range(int((min(a.y, b.y) - pad) // pad), int((max(a.y, b.y) + pad) // pad) + 1):
                eg.setdefault((i, j), []).append(k)
    gap = math.inf
    seen = set()
    for lst in eg.values():
        for ii, a in enumerate(lst):
            for b in lst[ii + 1:]:
                if edges[a][0] != edges[b][0] and (a, b) not in seen:
                    seen.add((a, b))
                    gap = min(gap, _seg_dist(edges[a][1], edges[a][2], edges[b][1], edges[b][2]))
    us = [q for _, u, _ in tris for q in u]
    border = min(min(q.x for q in us), min(q.y for q in us), 1 - max(q.x for q in us), 1 - max(q.y for q in us))
    bm.free()
    conf = sorted(r[0] for r in rows)
    area = [max(r[1] / g, g / r[1]) if r[1] > 0 else math.inf for r in rows]
    return {"name": o.name, "uv_layer": o.data.uv_layers.active.name, "islands": len(set(isl)),
            "overlap_pairs": overlaps, "overlap_cross_island": cross, "flipped": sum(r[2] for r in rows),
            "min_gap": round(gap, 4) if gap < math.inf else None, "border": round(border, 4),
            "uv_fill": round(sum(areau.values()), 3),
            "density": [round(dens[0], 3), round(dens[len(dens) // 2], 3), round(dens[-1], 3)],
            "stretch_conformal_worst": round(conf[-1], 3),
            "stretch_conformal_p95": round(conf[int(0.95 * (len(conf) - 1))], 3),
            "stretch_area_worst": round(max(area), 3),
            "angle_change_worst_deg": round(math.degrees(max(r[3] for r in rows)), 2),
            "texels_per_stud_1024": round(math.sqrt(g) * 1024, 1)}


def smart_uv(o, margin=0.008, angle=66.0, method=None, min_angle=25.0):
    """UVs into 'UVMap', packed with an exact margin: margin is a fraction of UV space round each island, so the
    gap between islands is 2 x margin (0.016 at the default; 2 px at 1024^2 is 0.002) and margin to the border.
    Smart UV Project at `angle` makes the islands. With method "ANGLE_BASED" (or "CONFORMAL" / "MINIMUM_STRETCH")
    those island borders become seams and each island is re-unwrapped by that method, which removes the
    projection's foreshortening (Smart UV alone compresses faces up to `angle` off its axis, up to 1/cos(angle))
    and gives every island the same texel density. If the unwrap folds an island over itself, the angle drops by
    10 degrees (not below min_angle) and it runs again. Returns uv_stats(o).
    (The repo's GLB exporter writes its own palette-cell UVs on export; this layer serves FBX/OBJ export and any
    texture work.)"""
    if not o.data.polygons:
        return None
    while True:
        with _override(o):
            bpy.ops.object.mode_set(mode="EDIT")
            try:
                bpy.ops.mesh.select_all(action="SELECT")
                if method:
                    bpy.ops.mesh.mark_seam(clear=True)      # the seams are this unwrap's own island borders
                bpy.ops.uv.smart_project(angle_limit=math.radians(angle), island_margin=margin,
                                         margin_method="FRACTION", area_weight=0.0, correct_aspect=True,
                                         scale_to_bounds=False)
                if method:
                    bpy.ops.uv.select_all(action="SELECT")
                    bpy.ops.uv.seams_from_islands(mark_seams=True, mark_sharp=False)
                    bpy.ops.mesh.select_all(action="SELECT")
                    bpy.ops.uv.unwrap(method=method, fill_holes=False, correct_aspect=True,
                                      margin_method="FRACTION", margin=margin)
            finally:
                bpy.ops.object.mode_set(mode="OBJECT")
        stats = uv_stats(o)
        stats["angle"] = angle
        stats["method"] = method or "SMART"
        if not method or (not stats["overlap_pairs"] and not stats["flipped"]) or angle - 10 < min_angle:
            return stats
        angle -= 10


def finish(o, union=True, uv=True):
    """Cleanup pass for a finished asset: union interpenetrating shells, merge by distance, outward normals, no
    custom split normals, flat shading, UVs, origin kept at the bottom centre. uv: True for smart_uv's defaults,
    a dict of smart_uv arguments, or False for none. Returns the audit (with smart_uv's uv_stats under "uv")."""
    if union and len(o.data.polygons):
        union_loose(o)
    if len(o.data.vertices):
        # re-centre: unions and subtractions can move the extents, so put the origin back at the bottom centre
        me = o.data
        xs = [v.co.x for v in me.vertices]
        ys = [v.co.y for v in me.vertices]
        zs = [v.co.z for v in me.vertices]
        off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
        if off.length > 1e-4:
            for v in me.vertices:
                v.co -= off
            for c in o.children:
                c.location -= off
    # booleans can leave slivers: merge near-duplicate verts and dissolve degenerate faces on every mesh
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=0.002)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    drop_specks(bm)
    bm.to_mesh(o.data)
    bm.free()
    # no n-gons (the boolean leaves some where shells meet): triangulate faces of more than 4 sides
    bm = bmesh.new()
    bm.from_mesh(o.data)
    ng = [f for f in bm.faces if len(f.verts) > 4]
    if ng:
        bmesh.ops.triangulate(bm, faces=ng)
        bm.to_mesh(o.data)
    bm.free()
    if o.data.has_custom_normals:
        with _override(o):
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
    repair_nonmanifold(o)
    for p in o.data.polygons:
        p.use_smooth = False
    K.drop_unused_slots(o)
    uv_res = None
    if uv:
        uv_res = smart_uv(o, **(uv if isinstance(uv, dict) else {}))
    res = audit(o)
    if uv_res:
        res["uv"] = uv_res
    return res


VIEWS = {"front34": (-28, 12), "rear34": (152, 12), "front": (0, 4), "side": (90, 4), "rear": (180, 4),
         "top": (0, 89), "underside": (20, -45)}


def views(num, objs, names=("front34", "rear34", "front", "side", "rear", "top", "underside"), cell=(480, 400),
          vfx=True, extra=None):
    """Render a model from the reference sheet's views into renders/models/M<NNN>/<view>.png plus a contact
    sheet M<NNN>_views.png (4 per row, in order). extra = {name: (objs, azimuth, elevation)} for exploded or
    parts shots. The underside view hides the studio floor."""
    kit = K.NS["KIT"]
    out_dir = f"{MODEL_RENDERS}/{code(num)}"
    os.makedirs(out_dir, exist_ok=True)
    objs = list(objs) if isinstance(objs, (list, tuple)) else [objs]
    old = kit["CELL"]
    kit["CELL"] = cell
    sc = bpy.context.scene
    ground = bpy.data.objects.get("FB_Ground")
    # the studio floor follows each shot (build_kit.frame_box puts it under the group's lowest point, up in the air
    # for lifted exploded parts): put it back afterwards and keep it out of the viewport, where it would slice
    # through the models on display; renders still see it (hide_render is separate)
    ground_home = ground.location.copy() if ground else None
    paths = []
    shots = [(v, objs) + VIEWS[v] for v in names] + [(k, list(g), az, el) for k, (g, az, el) in (extra or {}).items()]
    try:
        if vfx:
            kit["vfx"].clear(sc)
            kit["vfx"].realize(sc, list({o for _, g, _, _ in shots for o in g}))
        for name, group, az, el in shots:
            if ground:
                ground.hide_render = el < 0
            paths.append(kit["render_group"](group, f"{out_dir}/{name}.png", az, el))
    finally:
        kit["CELL"] = old
        if ground:
            ground.hide_render = False
            ground.location = (ground_home.x, ground_home.y, 0.0)
            ground.hide_set(True)
        if vfx:
            kit["vfx"].clear(sc)
    rows = [kit["hstack"](paths[i:i + 4]) for i in range(0, len(paths), 4)]
    w = max(r.shape[1] for r in rows)
    rows = [np.concatenate([r, np.ones((r.shape[0], w - r.shape[1], 4), np.float32)], axis=1) if r.shape[1] < w else r
            for r in rows]
    sheet = f"{out_dir}/{code(num)}_views.png"
    kit["save_px"](kit["vstack"](rows), sheet)
    return sheet


DISPLAY_Y0, DISPLAY_STEP, DISPLAY_COLS = -200.0, 60.0, 10


def display(num, objs, title=None):
    """Put a model on display in FlintbornWorldKit.blend: its own 60-stud slot in the numbered-models area
    (south of the kit sheets; 10 per row), the hero at the slot's front, its parts in a row behind it, and a
    text label (in the _Labels collection, outside Kit, so exports and checks never see it)."""
    col, row = (num - 1) % DISPLAY_COLS, (num - 1) // DISPLAY_COLS
    x0, y0 = col * DISPLAY_STEP, DISPLAY_Y0 - row * DISPLAY_STEP
    hero = next((o for o in objs if o.get("kit_role") == "hero"), objs[0])
    hero.location = (x0, y0, 0)
    rest = [o for o in objs if o is not hero]
    if rest:
        widths = [o.dimensions.x for o in rest]
        gap = 2.0
        total = sum(widths) + gap * (len(rest) - 1)
        x = x0 - total / 2
        back = y0 + hero.dimensions.y / 2 + 4 + max(o.dimensions.y for o in rest) / 2
        for o, w in zip(rest, widths):
            o.location = (x + w / 2, back, 0)
            x += w + gap
    labels = bpy.data.collections.get("_Labels")
    if not labels:
        labels = bpy.data.collections.new("_Labels")
        bpy.context.scene.collection.children.link(labels)
    name = f"Label_{code(num)}"
    lab = bpy.data.objects.get(name)
    if not lab:
        lab = bpy.data.objects.new(name, bpy.data.curves.new(name, "FONT"))
        labels.objects.link(lab)
    lab.data.body = f"{num:03d} {title or hero.get('kit_subject') or hero.name}"
    lab.data.size = 2.5
    lab.data.align_x = "CENTER"
    lab.location = (x0, y0 - hero.dimensions.y / 2 - 4, 0.02)
    lab.hide_render = True
    bpy.context.view_layer.update()
    return [tuple(round(c, 2) for c in o.location) for o in objs]


def explode(objs, offsets):
    """Temporarily move objects by offsets {obj: (dx, dy, dz)} for an exploded shot; returns a restore list."""
    saved = [(o, o.location.copy()) for o in objs]
    for o in objs:
        d = offsets.get(o.name)
        if d:
            o.location += Vector(d)
    bpy.context.view_layer.update()
    return saved


def restore(saved):
    for o, loc in saved:
        o.location = loc
    bpy.context.view_layer.update()
