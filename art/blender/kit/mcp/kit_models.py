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
from mathutils import Vector
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
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    K.drop_unused_slots(o)
    return len(others)


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


def smart_uv(o, margin=0.008, angle=66.0):
    """Smart UV Project into 'UVMap'; margin 0.008 so gaps between islands clear 2 px at 1024^2. (The repo's GLB exporter writes its own
    palette-cell UVs on export; this layer serves FBX/OBJ export and any texture work.)"""
    if not o.data.polygons:
        return
    with _override(o):
        bpy.ops.object.mode_set(mode="EDIT")
        try:
            bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.uv.smart_project(angle_limit=math.radians(angle), island_margin=margin, area_weight=0.0,
                                     correct_aspect=True, scale_to_bounds=False)
        finally:
            bpy.ops.object.mode_set(mode="OBJECT")


def finish(o, union=True, uv=True):
    """Cleanup pass for a finished asset: union interpenetrating shells, merge by distance, outward normals, no
    custom split normals, flat shading, Smart UV, origin kept at the bottom centre. Returns the audit."""
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
    for p in o.data.polygons:
        p.use_smooth = False
    K.drop_unused_slots(o)
    if uv:
        smart_uv(o)
    return audit(o)


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
