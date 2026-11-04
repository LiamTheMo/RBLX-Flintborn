"""The builder scaffold every numbered model shares (STAGES.md, "Shared library (2026-11-04)"): object creation from a
flintkit Asset, stage 2-3 cleanup, stored points and sockets, the standard build run, checks and renders. A builder
keeps only its model-specific shapes and data; the pieces come from kit_parts (P).

    import kit_build as B, kit_parts as P
    MODEL = B.Model(67, "Table and Seating", palette=PALETTE, targets=TARGETS)

    def build(render=True, close=False):
        return MODEL.run(hero=(HERO, hero_fn), parts=PARTS, notes=NOTES, collision=COLLISION,
                         budgets={HERO: 4000}, target_size=TARGET_SIZE, views=SHEET_VIEWS, render=render, close=...)

    import importlib, kit_parts, kit_build, mNNN
    importlib.reload(kit_parts); importlib.reload(kit_build); importlib.reload(mNNN); mNNN.build()

Model(num, title, palette={key: (hex, rough, metal, emit, low_spec)}, targets={key: ((r, g, b), kind)}, uv=UV)
    .sheet "M067", .key "m067", .OFF "m067_offset" (the object's origin in the build frame), .PFX "_m067_" (temp
    objects), .dir (its renders folder, under kit_models.MODEL_RENDERS)
    .palette()             set the model's keys, resync its in-between (mix) keys, Neon preview for glow keys
    .sync_palette()        re-apply KIT_PALETTE to every FB_<key>_ material (mix materials made during a build)
    .calibrate(keys)       K.calibrate on .targets ("all" kinds sampled with the studio paper dropped)
    .make(name, fn, role, budget, collision, notes, temp, uv) -> (obj, log): build fn(a) into a fresh object and
                           clean it (cleanup()); stores <key>_pieces / _ropes / _leaves from kit_parts' registers
    .at(o, p)              a build-frame point in world space;  .store_points(o, {name: (p, facing)})
    .sockets(o, fx)        VFX sockets from [(kind, build-frame point, overrides)]
    .run(hero=(name, fn), parts=[(name, fn)], notes, collision, budgets, target_size, points, fx, views,
         exploded, scale, close, variants, verify, checks, render, part_shots, spin) -> report dict
    .render(objs, ...)     the default renders (below);  .preview(names) the hero's listed views only
    .hero_only(fn)         rebuild just the hero without UVs (tuning loop)
    .render_close(objs, path, az, el, centre, radius), .render_cam(objs, path, loc, look, lens), .marker(h, at)

Module level: cleanup(o, ...), triangulate(o, mode), earclip_faces(bm, faces), recentre(o, off_key), uv_unfold(o, uv),
bottom_centre(o), linked(o, name, matrix), remove(objs), fallback_checks(objs, budgets, target_size).

Checks: run() calls kit_verify.run(objs, budgets=..., size={hero: target_size}, **verify) when kit_verify.py is
importable (it owns the checks, reads the <key>_pieces / _offset properties make() stores, and returns a dict with a
"problems" list; pass its optional checks through verify, e.g. verify=dict(foliage=True, walk={...})); without it,
fallback_checks() runs the basic audit, budget, size, UV and K.check.
checks=[fn(objs) -> (report, problems)] adds model-specific checks either way.

Renders (into .dir, all on the contact sheet <SHEET>_views.png): one per sheet cell the builder lists in views
({name: (az, el) or (az, el, variant)}; names containing "_sheet" use the 3x long lens with the floor hidden, as the
sheet's orthographic-looking cells), an exploded view of the parts and a scale view with a 5.5-stud character.
Close-ups only when asked (close={name: dict(at, r, az, el) or dict(cam, look, lens)}); part_shots and spin likewise.
Builds give the same objects in the GUI kit file and in a background session (bgmcp) or the light work file
(make_workfile.py): nothing here depends on the viewport, and sync_palette() equalises materials made during a build.
"""
import importlib
import json
import time

import bmesh
import bpy
from mathutils import Matrix, Vector

import kit_mcp as K
import kit_models as M
import kit_parts as P

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)      # every model since m064
SHEET_LENS = 3.0                 # the *_sheet views' lens factor (m033 / m067 / m070)
NEON = 1.0                       # emission at which a key exports as Neon
DEFAULT_VIEWS = {"front34": (-28, 12), "front": (0, 4), "side": (90, 4), "rear": (180, 4), "top": (0, 89)}
EXPLODED = (-20, 15)
SCALE_VIEW = (-25, 8)
PART_SHOT = (-20, 15)
MARKER_KEY = "kit_rock_dark"     # the scale character's key (a flintkit kit key, always present)
AUDIT_KEYS = ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "wire_edges", "loose_verts",
              "zero_area_faces", "ngons", "dup_verts")


def verifier():
    """kit_verify if it is importable, else None (the checks module may land after this one)."""
    try:
        return importlib.import_module("kit_verify")
    except ImportError:
        return None


# ---- cleanup -----------------------------------------------------------------------------------------------------------
def bottom_centre(o):
    xs = [v.co.x for v in o.data.vertices]
    ys = [v.co.y for v in o.data.vertices]
    zs = [v.co.z for v in o.data.vertices]
    return Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))


def recentre(o, off_key):
    """Origin to the bbox bottom centre; o[off_key] accumulates the shift (the origin in the build frame)."""
    bc = bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
        o[off_key] = list(Vector(o.get(off_key, (0.0, 0.0, 0.0))) + bc)
    o.data.update()


def earclip_faces(bm, faces):
    """Replace each face by ear-clipped triangles in its own plane (kit_parts.earclip: the best-shaped ear first, no
    slivers), keeping its material, smoothing and every loop layer (Tint, UVs). Returns the new face count."""
    layers = list(bm.loops.layers.float_color.values()) + list(bm.loops.layers.color.values()) + \
        list(bm.loops.layers.uv.values())
    made = 0
    for f in list(faces):
        if not f.is_valid or len(f.verts) < 4:
            continue
        vs = list(f.verts)
        n = P.newell([v.co for v in vs])
        if n.length < 1e-12:
            continue
        n.normalize()
        e1 = n.orthogonal().normalized()
        e2 = n.cross(e1)
        tris = P.earclip([(v.co.dot(e1), v.co.dot(e2)) for v in vs])
        data = {l.vert: [(lay, l[lay].copy() if hasattr(l[lay], "copy") else l[lay].uv.copy()) for lay in layers]
                for l in f.loops}
        mi, smooth = f.material_index, f.smooth
        bm.faces.remove(f)
        for t in tris:
            try:
                nf = bm.faces.new([vs[i] for i in t])
            except ValueError:
                continue
            nf.material_index, nf.smooth = mi, smooth
            for l in nf.loops:
                for lay, val in data[l.vert]:
                    if lay in bm.loops.layers.uv.values():
                        l[lay].uv = val
                    else:
                        l[lay] = val
            made += 1
    return made


def triangulate(o, mode="ngons"):
    """mode "ngons": ear-clip faces of 5+ sides (quads stay); "all": quads split too (BEAUTY); None: nothing."""
    if not mode:
        return 0
    bm = bmesh.new()
    bm.from_mesh(o.data)
    n = earclip_faces(bm, [f for f in bm.faces if len(f.verts) > 4])
    if mode == "all":
        q = [f for f in bm.faces if len(f.verts) == 4]
        if q:
            bmesh.ops.triangulate(bm, faces=q, quad_method="BEAUTY", ngon_method="BEAUTY")
            n += len(q)
    bm.to_mesh(o.data)
    bm.free()
    return n


def uv_overlaps(o):
    """UV-overlapping face pairs (fanned triangles, grid-bucketed)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    uv = bm.loops.layers.uv.active
    tris = []
    for f in bm.faces:
        ls = [(l[uv].uv.x, l[uv].uv.y) for l in f.loops]
        for i in range(1, len(ls) - 1):
            tris.append((f.index, [ls[0], ls[i], ls[i + 1]]))
    bm.free()
    boxes = [(min(p[0] for p in t), min(p[1] for p in t), max(p[0] for p in t), max(p[1] for p in t)) for _, t in tris]
    grid = {}
    for k, b in enumerate(boxes):
        for i in range(int(b[0] // 0.05), int(b[2] // 0.05) + 1):
            for j in range(int(b[1] // 0.05), int(b[3] // 0.05) + 1):
                grid.setdefault((i, j), []).append(k)
    pairs = {(a_, b_) for lst in grid.values() for i, a_ in enumerate(lst) for b_ in lst[i + 1:]
             if tris[a_][0] != tris[b_][0]}
    return [(tris[a_][0], tris[b_][0]) for a_, b_ in pairs if M._tri_overlap(tris[a_][1], tris[b_][1])]


def uv_unfold(o, uv=UV, rounds=4):
    """Cut the smaller face of each UV-overlapping pair free along seams and unwrap again (m012). Returns faces cut."""
    cut = 0
    for _ in range(rounds):
        bad = uv_overlaps(o)
        if not bad:
            break
        polys = o.data.polygons
        free = {min((a_, b_), key=lambda i: polys[i].area) for a_, b_ in bad}
        keys = {tuple(sorted(e)) for i in free for e in polys[i].edge_keys}
        for e in o.data.edges:
            if tuple(sorted(e.vertices)) in keys:
                e.use_seam = True
        cut += len(free)
        with M._override(o):
            bpy.ops.object.mode_set(mode="EDIT")
            try:
                bpy.ops.mesh.select_all(action="SELECT")
                bpy.ops.uv.unwrap(method=uv.get("method") or "ANGLE_BASED", fill_holes=False, correct_aspect=True,
                                  margin_method="FRACTION", margin=uv.get("margin", 0.008))
            finally:
                bpy.ops.object.mode_set(mode="OBJECT")
    return cut


def cleanup(o, off_key, uv=UV, tri="ngons", merge=0.0):
    """Stage 2-3 pass on a built object of closed shells (no booleans): merge by distance (merge > 0 only: it can weld
    touching shells), n-gons ear-clipped (tri), normals outward per shell, flat shading, no custom normals, origin at
    the bbox bottom centre (o[off_key]), bowties split, UVs (uv: smart_uv arguments, angle-based islands, overlaps cut
    free; False for none), unused slots dropped. Returns a log."""
    lg = {}
    bm = bmesh.new()
    bm.from_mesh(o.data)
    if merge > 0:
        n0 = len(bm.verts)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=merge)
        lg["merged"] = n0 - len(bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    lg["triangulated"] = triangulate(o, tri)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    for p in o.data.polygons:
        p.use_smooth = False
    if o.data.has_custom_normals:
        with M._override(o):
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
    recentre(o, off_key)
    lg["bowties"] = M.fix_bowties(o)
    if uv:
        M.smart_uv(o, **uv)
        lg["uv_cut"] = uv_unfold(o, uv)
    K.drop_unused_slots(o)
    return lg


def linked(o, name, m):
    """A linked copy of o (same mesh) at world matrix m, in o's collection (exploded views)."""
    c = bpy.data.objects.new(name, o.data)
    o.users_collection[0].objects.link(c)
    c.matrix_world = m
    return c


def remove(objs):
    for o in objs:
        if o is None or o.name not in bpy.data.objects:
            continue
        me = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(me, bpy.types.Mesh) and me.users == 0:
            bpy.data.meshes.remove(me)


def fallback_checks(objs, budgets=None, target_size=None, hero=None):
    """The basic checks when kit_verify is not there: M.audit counts (non-manifold, boundary, bowties, n-gons ...),
    outward normals, budgets, the hero's target size (W, D, H as (value, tolerance)), UV overlaps and gaps, and the
    kit's own colour checks (K.check). Returns (report, problems)."""
    budgets = budgets or {}
    problems = list(K.check(objs))
    audit = {}
    for o in objs:
        au = M.audit(o)
        audit[o.name] = {k: au[k] for k in ("tris", "size", "shells", "normals") + AUDIT_KEYS}
        lim = budgets.get(o.name, int(o.get("kit_budget", 1000)))
        if au["tris"] > lim:
            problems.append(f"{o.name}: {au['tris']} tris over {lim}")
        for k in AUDIT_KEYS:
            if au[k]:
                problems.append(f"{o.name}: {k} {au[k]}")
        if au["normals"] != "outward":
            problems.append(f"{o.name}: normals {au['normals']}")
        if o.data.uv_layers:
            u = M.uv_stats(o)
            if u.get("overlap_pairs") or u.get("flipped"):
                problems.append(f"{o.name}: UV overlaps {u.get('overlap_pairs')} flipped {u.get('flipped')}")
            if u.get("min_gap") is not None and u["min_gap"] < 0.0159:
                problems.append(f"{o.name}: UV island gap {u['min_gap']}")
    if hero is not None and target_size:
        for (tgt, tol), got, ax in zip(target_size, hero.dimensions, "WDH"):
            if abs(got - tgt) > tol:
                problems.append(f"{hero.name}: {ax} {got:.2f} outside {tgt} +- {tol}")
    return {"audit": audit}, problems


# ---- the model ---------------------------------------------------------------------------------------------------------
class Model:
    """One numbered model's build context (see the module docstring)."""

    def __init__(self, num, title, palette=None, targets=None, uv=UV, seed=7):
        self.num, self.title = num, title
        self.sheet = M.code(num)
        self.key = self.sheet.lower()
        self.OFF, self.PFX = f"{self.key}_offset", f"_{self.key}_"
        self.palette_spec = dict(palette or {})
        self.targets = dict(targets or {})
        self.uv, self.seed = uv, seed

    @property
    def dir(self):
        return f"{M.MODEL_RENDERS}/{self.sheet}"

    # -- palette ----------------------------------------------------------------------------------------------------
    def palette(self):
        """Set every key in .palette_spec ((hex, rough, metal, emit, low_spec)), create its material, resync the
        model's in-between keys from their parents, and give Neon keys their preview look."""
        f = K.fk()
        for k, (hexcol, rough, metal, emit, low) in self.palette_spec.items():
            K.set_colour(k, hexcol, rough=rough, metal=metal, emit=emit, low_spec=low)
            f.material(k)
            K.set_colour(k, hexcol, rough=rough, metal=metal, emit=emit, low_spec=low)
        for m in list(bpy.data.materials):
            key = m.name[3:] if m.name.startswith(f"FB_{self.key}_") else None
            if key and "_x_" in key:
                k1, rest = key.split("_x_", 1)
                tail, pct = rest.rsplit("_", 1)
                k2 = f"{self.key}_{tail}"
                if k1 in self.palette_spec and k2 in self.palette_spec and pct.isdigit():
                    f.KIT_PALETTE.pop(key, None)
                    K.mix_key(k1, k2, int(pct) / 100)
        self.glow_preview()

    def sync_palette(self):
        """Re-apply KIT_PALETTE to every FB_<key>_ material. A mix key's material is first made by Asset.finish with
        flintkit's default low specular; this sets it as K.set_colour would, so a build in a fresh file renders like
        one in the kit file. Returns the keys synced."""
        f = K.fk()
        done = []
        for m in bpy.data.materials:
            key = m.name[3:] if m.name.startswith(f"FB_{self.key}_") else None
            if key and key in f.KIT_PALETTE:
                e = f.KIT_PALETTE[key]
                K.set_colour(key, e[0], rough=e[1], metal=e[2], emit=e[3], low_spec=key in f.LOW_SPEC)
                done.append(key)
        self.glow_preview()
        return done

    def glow_preview(self):
        """Neon keys (emission >= NEON) preview as Roblox shows Neon: their own colour, unshaded (m009 / m064)."""
        for mat in bpy.data.materials:
            if not (mat.name.startswith(f"FB_{self.key}_") and mat.node_tree):
                continue
            if list(mat.get("flintkit_spec", [0, 0, 0]))[2] < NEON:
                continue
            b = mat.node_tree.nodes.get("Principled BSDF")
            if b is None:
                continue
            for lk in list(b.inputs["Base Color"].links):
                mat.node_tree.links.remove(lk)
            b.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)
            if "Specular IOR Level" in b.inputs:
                b.inputs["Specular IOR Level"].default_value = 0.0

    def calibrate(self, keys=None, iters=6, out_dir=None):
        """K.calibrate on .targets; "all" kinds are sampled with the studio paper dropped. Returns {key: (hex, got)};
        write the hexes back into the builder's PALETTE."""
        keys = keys or list(self.targets)
        sample0 = K.sample

        def sample(src, box, kind="green"):
            return M.sample(src, box, "all", paper=(242, 238, 230), tol=14) if kind == "all" else sample0(src, box, kind)
        K.sample = sample
        try:
            for k in keys:
                K.fk().material(k)
            return K.calibrate({k: self.targets[k] for k in keys}, iters=iters, out_dir=out_dir)
        finally:
            K.sample = sample0
            for m in [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]:
                bpy.data.meshes.remove(m)

    # -- objects ------------------------------------------------------------------------------------------------------
    def make(self, name, fn, role="part", budget=1000, collision="hull", notes="", temp=False, uv=True, tri="ngons",
             merge=0.0):
        """Build fn(a) into a fresh object `name` (an old one of that name is replaced; one of another sheet is
        refused), tag it (kit_sheet, role, collision, budget, notes) unless temp, store kit_parts' registers on it,
        then cleanup() (uv=False: triangulate and recentre only). Returns (obj, log)."""
        t0 = time.time()
        old = bpy.data.objects.get(name)
        if old:
            if old.get("kit_sheet") not in (None, self.sheet) and not temp:
                raise RuntimeError(f"{name} belongs to {old.get('kit_sheet')}")
            remove(list(old.children_recursive))
            remove([old])
        a = K.fk().Asset(name, f"{self.sheet} {self.title}", seed=self.seed, tint_var=0.0)
        P.reset()
        fn(a)
        o = a.finish(collection=M.coll(self.num, self.title), mark_asset=not temp, origin=None)
        K.drop_unused_slots(o)
        if not temp:
            K.tag(o, self.sheet, self.title, role, collision, budget, notes)
        o[self.OFF] = [0.0, 0.0, 0.0]
        o.location = (0, 0, 0)
        o[f"{self.key}_pieces"] = json.dumps([[k, n_, [round(x, 5) for x in c]] for k, n_, c in P.PIECES])
        if P.ROPES:
            o[f"{self.key}_ropes"] = json.dumps(P.ROPES)
        if P.LEAVES:
            o[f"{self.key}_leaves"] = json.dumps([[l["name"], l["n"], l["kind"]] for l in P.LEAVES])
        bpy.context.view_layer.update()
        if uv:
            lg = cleanup(o, self.OFF, uv=self.uv if uv is True else uv, tri=tri, merge=merge)
        else:
            lg = {"triangulated": triangulate(o, tri or "ngons")}
            recentre(o, self.OFF)
        lg["secs"] = round(time.time() - t0, 1)
        return o, lg

    def at(self, o, p):
        """A build-frame point of object o in world space."""
        return o.matrix_world @ Matrix.Translation(-Vector(o[self.OFF])) @ Vector(p)

    def local(self, o, p):
        """A build-frame point in o's local (origin-relative) coordinates."""
        return Vector(p) - Vector(o[self.OFF])

    def store_points(self, o, pts):
        """Stored points (seat, door, hang, ...) for Studio: {name: point} or {name: (point, facing)}, written relative
        to the object's origin (and name_facing)."""
        for k, v in pts.items():
            p, f = (v if isinstance(v, (tuple, list)) and len(v) == 2 and hasattr(v[0], "__len__") else (v, None))
            o[k] = [round(x, 4) for x in self.local(o, p)]
            if f is not None:
                o[k + "_facing"] = [float(x) for x in f]

    def sockets(self, o, fx):
        """VFX sockets on o from [(kind, build-frame point, overrides)]; old ones removed first."""
        remove([c for c in o.children if c.get("vfx_kind")])
        return [K.socket(o, kind, self.local(o, p), **(kw[0] if kw else {})) for kind, p, *kw in fx]

    def cleanup_tmp(self):
        remove([o for o in bpy.data.objects if o.name.startswith(self.PFX)])

    def drop_unused(self):
        """Unused materials of this model and orphan meshes of its temp objects."""
        mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and
                m.name.startswith(f"FB_{self.key}_")]
        for m in mats:
            bpy.data.materials.remove(m)
        meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((self.PFX, "_probe", "T_Calib"))]
        for m in meshes:
            bpy.data.meshes.remove(m)
        return len(mats), len(meshes)

    def export_stats(self, objs):
        """What the exporter's STATS line reports: VFX sockets and glow (Neon) keys per object."""
        return {o.name: {"vfx_sockets": len([c for c in o.children_recursive if c.get("vfx_kind")]),
                         "glow_keys": sorted({m.name[3:] for m in o.data.materials
                                              if list(m.get("flintkit_spec", [0, 0, 0]))[2] >= NEON})} for o in objs}

    # -- the standard run ------------------------------------------------------------------------------------------------
    def run(self, hero, parts=(), notes=None, collision=None, budgets=None, target_size=None, points=None, fx=None,
            views=None, exploded=None, scale=None, close=None, variants=None, verify=None, checks=(), render=True,
            part_shots=False, spin=False, after=None):
        """Build the parts and the hero, store points and sockets, put them on display, check, render.

        hero = (name, fn); parts = [(name, fn)] built first, in order. notes / collision / budgets: {name: value}
        (budgets default 4000 hero, 1000 parts; collision default "hull"). target_size = ((W, tol), (D, tol), (H, tol))
        of the hero. points = {obj name: {point name: point or (point, facing)}} in the build frame; fx = {obj name:
        [(kind, point, overrides)]}. verify: keyword options for kit_verify.run. checks: [fn(objs) -> (report,
        problems)] model-specific. after(objs): a hook after display (e.g. extra stored values). Render options as
        in render(). Returns a report dict (audit, problems, verify, offsets, materials, timings, views)."""
        t0 = time.time()
        notes, collision, budgets = notes or {}, collision or {}, dict(budgets or {})
        M.coll(self.num, self.title)
        self.palette()
        objs, log = {}, {}
        for name, fn in parts:
            objs[name], log[name] = self.make(name, fn, "part", budgets.get(name, 1000), collision.get(name, "hull"),
                                              notes.get(name, ""))
        hname, hfn = hero
        h, log[hname] = self.make(hname, hfn, "hero", budgets.get(hname, 4000), collision.get(hname, "precise"),
                                  notes.get(hname, ""))
        geo = json.loads(json.dumps(P.GEO, default=lambda v: [round(x, 3) for x in v]))
        objs = {hname: h, **objs}
        for oname, pts in (points or {}).items():
            self.store_points(objs[oname], pts)
        for oname, f in (fx or {}).items():
            self.sockets(objs[oname], f)
        self.cleanup_tmp()
        order = [h] + [objs[n] for n, _ in parts]
        M.display(self.num, order, self.title)
        log["dropped"] = self.drop_unused()
        log["synced"] = len(self.sync_palette())
        for o in order:
            d = o.dimensions
            o["studs"] = f"{d.x:.2f} x {d.y:.2f} x {d.z:.2f}"
        if after:
            after(objs)
        out = {"objects": {o.name: {"tris": sum(len(p.vertices) - 2 for p in o.data.polygons),
                                    "size": [round(x, 3) for x in o.dimensions],
                                    "offset": [round(x, 3) for x in o[self.OFF]],
                                    "materials": [m.name[3:] for m in o.data.materials]} for o in order},
               "geo": geo, "log": log}
        tv = time.time()
        kv = verifier()
        budgets_all = {o.name: budgets.get(o.name, 4000 if o is h else 1000) for o in order}
        if kv is not None:
            opts = {"budgets": budgets_all}
            if target_size:
                opts["size"] = {hname: tuple(target_size)}
            opts.update(verify or {})
            res = kv.run(order, **opts)
            out["verify"] = res
            problems = list(res.get("problems", []))
            out["checked_by"] = "kit_verify"
        else:
            rep, problems = fallback_checks(order, budgets_all, target_size, h)
            out["verify"] = rep
            out["checked_by"] = "kit_build.fallback_checks"
        for fn in checks:
            rep, pr = fn(objs)
            out.setdefault("checks", {})[getattr(fn, "__name__", "check")] = rep
            problems += list(pr)
        out["problems"] = problems
        out["export_stats"] = self.export_stats(order)
        out["build_s"] = round(tv - t0, 1)
        out["check_s"] = round(time.time() - tv, 1)
        if render:
            tr = time.time()
            out["views"] = self.render(order, views=views, exploded=exploded, scale=scale, close=close,
                                       variants=variants, part_shots=part_shots, spin=spin)
            out["render_s"] = round(time.time() - tr, 1)
        return out

    def hero_only(self, name, fn, budget=4000, uv=False):
        """Rebuild just the hero (tuning loop): counts, size, offset; no UVs unless asked; parts left as they are."""
        M.coll(self.num, self.title)
        self.palette()
        h, lg = self.make(name, fn, "hero", budget, "precise", uv=uv)
        self.cleanup_tmp()
        rest = [o for o in M.coll(self.num, self.title).objects if o is not h and o.get("kit_sheet") == self.sheet]
        M.display(self.num, [h] + sorted(rest, key=lambda o: o.name), self.title)
        self.sync_palette()
        au = M.audit(h)
        return {"hero": {k: au[k] for k in ("tris", "size", "shells", "normals") + AUDIT_KEYS}, "log": lg,
                "geo": json.loads(json.dumps(P.GEO, default=lambda v: [round(x, 3) for x in v])),
                "offset": [round(x, 3) for x in h[self.OFF]]}

    # -- renders ----------------------------------------------------------------------------------------------------------
    def long_lens(self, kit=None):
        """(orig, wrapped) render_group: names containing "_sheet" get SHEET_LENS x the lens and no studio floor."""
        kit = kit or K.NS["KIT"]
        orig = kit["render_group"]

        def rg(group, path, azimuth=-22, elevation=20):
            cam = bpy.data.objects["FB_Cam"].data
            lens = cam.lens
            ground = bpy.data.objects.get("FB_Ground")
            gh = ground.hide_render if ground else None
            if "_sheet" in path.rsplit("/", 1)[-1]:
                cam.lens = lens * SHEET_LENS
                if ground:
                    ground.hide_render = True
            try:
                return orig(group, path, azimuth, elevation)
            finally:
                cam.lens = lens
                if ground:
                    ground.hide_render = gh
        return orig, rg

    def marker(self, h, at, name="char", key=MARKER_KEY):
        """A 5.5-stud character stand-in at build-frame point `at` (temp object)."""
        a = K.fk().Asset(self.PFX + name, "probe", seed=1, tint_var=0.0)
        a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=key, tint=0.7)
        a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=key, tint=0.7)
        a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=key, tint=0.7)
        c = a.finish(collection=h.users_collection[0], mark_asset=False)
        c.location = self.at(h, at)
        bpy.context.view_layer.update()
        return c

    def variant(self, h, tag, fn):
        """A temp object built from fn, lined up with the hero (e.g. the hero without a part the sheet's cell omits)."""
        o, _ = self.make(self.PFX + tag, fn, temp=True, uv=False)
        o.location = h.location + Vector(o[self.OFF]) - Vector(h[self.OFF])
        bpy.context.view_layer.update()
        return o

    def exploded_copies(self, objs, layout=None):
        """Linked copies of the parts for the exploded view, 40 + the hero's width to its right. layout = {part name:
        offset (x, y, z) or [offsets] or a 4x4 matrix}; default: the parts in a row, 2 studs apart."""
        h = objs[0]
        by = {o.name: o for o in objs}
        o0 = Matrix.Translation((h.location.x + 40 + h.dimensions.x, h.location.y, 0))
        shown = []
        if layout is None:
            parts = objs[1:]
            total = sum(o.dimensions.x for o in parts) + 2.0 * max(0, len(parts) - 1)
            x = -total / 2
            layout = {}
            for o in parts:
                layout[o.name] = (x + o.dimensions.x / 2, 0.0, 0.0)
                x += o.dimensions.x + 2.0
        for i, (name, spec) in enumerate(layout.items()):
            if name not in by:
                continue
            specs = spec if isinstance(spec, list) else [spec]
            for k, s in enumerate(specs):
                m = s if isinstance(s, Matrix) else Matrix.Translation(s)
                shown.append(linked(by[name], f"{self.PFX}expl_{i}_{k}", o0 @ m))
        bpy.context.view_layer.update()
        return shown

    def render(self, objs, views=None, exploded=None, scale=None, close=None, variants=None, part_shots=False,
               spin=False, vfx=None):
        """The default renders into .dir: one per listed sheet view, the exploded view, the scale view, all on
        <SHEET>_views.png; close-ups, part shots and an eight-azimuth spin only when asked. scale = a build-frame
        point for the character (default beside the hero's front-left corner) or False. vfx: realise sockets (default
        when the hero has any)."""
        h = objs[0]
        kit = K.NS["KIT"]
        views = views or DEFAULT_VIEWS
        temp = []
        out = {}
        try:
            vobj = {}
            for tag, fn in (variants or {}).items():
                vobj[tag] = self.variant(h, tag, fn)
                temp.append(vobj[tag])
            extra = {}
            for name, spec in views.items():
                az, el, *rest = spec
                extra[name] = ([vobj[rest[0]]] if rest else [h], az, el)
            if part_shots:
                for o in objs[1:]:
                    extra["part_" + o.name.lower()] = ([o], *PART_SHOT)
            if len(objs) > 1 and exploded is not False:
                ex = self.exploded_copies(objs, exploded)
                temp += ex
                extra["exploded"] = (ex, *EXPLODED)
            if scale is not False:
                if scale is None:
                    off = Vector(h[self.OFF])
                    scale = (off.x - h.dimensions.x / 2 - 1.5, off.y - h.dimensions.y / 2 - 1.0, 0.0)
                mk = self.marker(h, scale)
                temp.append(mk)
                extra["scale"] = ([h, mk], *SCALE_VIEW)
            vfx = any(c.get("vfx_kind") for c in h.children) if vfx is None else vfx
            orig, kit["render_group"] = self.long_lens(kit)
            try:
                out["sheet"] = M.views(self.num, [h], names=(), extra=extra, vfx=vfx)
                if spin:
                    out["spin"] = self.render_spin(h)
            finally:
                kit["render_group"] = orig
            for name, c in (close or {}).items():
                path = f"{self.dir}/{name}.png"
                if "cam" in c:
                    out[name] = self.render_cam([h], path, self.at(h, c["cam"]), self.at(h, c["look"]),
                                                c.get("lens", 18.0))
                else:
                    out[name] = self.render_close([h], path, c.get("az", -30), c.get("el", 20), self.at(h, c["at"]),
                                                  c.get("r", 1.0))
            return out
        finally:
            remove(temp)
            M.display(self.num, objs, self.title)

    def preview(self, hero_name, views, names=None, variants=None):
        """Just the hero's listed sheet views (fast tuning loop): views as in render(), names a subset."""
        h = bpy.data.objects[hero_name]
        temp = {}
        kit = K.NS["KIT"]
        orig, kit["render_group"] = self.long_lens(kit)
        try:
            extra = {}
            for name in (names or list(views)):
                az, el, *rest = views[name]
                if rest and rest[0] not in temp:
                    temp[rest[0]] = self.variant(h, rest[0], variants[rest[0]])
                extra[name] = ([temp[rest[0]]] if rest else [h], az, el)
            return M.views(self.num, [h], names=(), extra=extra, vfx=False)
        finally:
            kit["render_group"] = orig
            remove(list(temp.values()))

    def render_spin(self, h, el=10, cell=(420, 360)):
        """The eight-azimuth sheet (az 0, 45 ... 315, long lens, floor hidden) -> <SHEET>_spin.png."""
        kit = K.NS["KIT"]
        old = kit["CELL"]
        kit["CELL"] = cell
        try:
            paths = [kit["render_group"]([h], f"{self.dir}/spin{az:03d}_sheet.png", az, el) for az in range(0, 360, 45)]
        finally:
            kit["CELL"] = old
        out = f"{self.dir}/{self.sheet}_spin.png"
        kit["save_px"](kit["vstack"]([kit["hstack"](paths[i:i + 4]) for i in (0, 4)]), out)
        return out

    def render_close(self, objs, path, az, el, centre, radius, cell=(480, 400)):
        """A close-up from (az, el) framed on a sphere (centre in world space, radius) (m033 / m067)."""
        kit = K.NS["KIT"]
        fb = kit["frame_box"]
        c = Vector(centre)
        box = [c + Vector((dx, dy, dz)) * radius for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)]
        kit["frame_box"] = lambda corners, a_, e_: fb(box, a_, e_)
        ground = bpy.data.objects.get("FB_Ground")
        if ground:
            ground.hide_render = el < 0
        old = kit["CELL"]
        kit["CELL"] = cell
        try:
            return kit["render_group"](objs, path, az, el)
        finally:
            kit["CELL"] = old
            kit["frame_box"] = fb
            if ground:
                ground.hide_render = False

    def render_cam(self, objs, path, loc, look, lens=18.0, cell=(560, 420)):
        """A render from a fixed camera at loc looking at look (world space), e.g. from under a table (m064)."""
        kit = K.NS["KIT"]
        fb = kit["frame_box"]
        cam = bpy.data.objects["FB_Cam"]
        lens0 = cam.data.lens
        ground = bpy.data.objects.get("FB_Ground")
        loc, look = Vector(loc), Vector(look)
        z0 = objs[0].matrix_world.translation.z

        def fixed(corners, az, el):
            cam.data.shift_x = cam.data.shift_y = 0.0
            cam.location = loc
            cam.rotation_euler = (look - loc).to_track_quat("-Z", "Y").to_euler()
            cam.data.lens = lens
            if ground:
                ground.location = (loc.x, loc.y, z0)
        kit["frame_box"] = fixed
        old = kit["CELL"]
        kit["CELL"] = cell
        try:
            return kit["render_group"](objs, path, 0, 10)
        finally:
            kit["frame_box"] = fb
            kit["CELL"] = old
            cam.data.lens = lens0


def install():
    """Load the kit helpers once per session (K.install) and return (K, M, P, this module)."""
    if "KIT" not in K.NS:
        K.install()
    return K, M, P, importlib.import_module(__name__)
