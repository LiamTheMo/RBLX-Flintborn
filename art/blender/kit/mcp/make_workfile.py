"""Make the light modelling work file art/blender/assets/kit/wip/LIGHT.blend (gitignored).

FlintbornWorldKit.blend holds every model (about 1M vertices, 36 MB), so a per-modeller copy is slow to open, save and
render. A builder needs only this from it:
- the studio: scene and render settings, the world (FB_Studio mix of paper background and ambient), FB_Key, FB_Fill,
  FB_Ground (+ FB_GroundMat) and FB_Cam. build_kit.kit_studio() re-tunes them on every render; flintkit would make
  them on first use, but the copies here carry the file's exact settings;
- the "Kit" collection (kit_models.coll() files each model under it), plus _wip, _Labels and Assets (empty);
- every palette material (FB_*, with flintkit_key / _hex / _spec): K.restore_palette() registers their keys, so
  shared keys (w01_rock, a model's earlier in-between keys) resolve as in the kit file. They are kept by one
  fake-user holder mesh (_FB_PaletteHolder), so nothing on the materials themselves changes;
- the water preview images those materials use (external files, nothing packed).
Everything else goes: every model, kit row and asset object, the _Reference sheet images and the labels. --keep
M067,M066 keeps those models' collections (to build next to, or compare with, an earlier model).

Run it with Blender's Python, either way:
    "$BLENDER_PATH" --background --factory-startup --python art/blender/kit/mcp/make_workfile.py -- [--keep M067]
        [--src <kit .blend>] [--out <light .blend>]
copies the source (default the kit file; never opened or saved itself) to <out dir>/_light_src.blend, opens the copy,
strips it, saves --out and deletes the copy. Or inside a running bgmcp session on a kit copy (e.g. wip/MNNN.blend):
    $PY art/blender/kit/mcp/bgmcp.py run <port> art/blender/kit/mcp/make_workfile.py
strips the session's current file in place and saves it as LIGHT.blend (the session then works in LIGHT.blend).
Prints / returns a summary: what was kept and removed, and the file size.
"""
import os
import shutil
import sys
import time

import bpy

try:
    HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:                     # exec'd by bgmcp: no __file__; kit_mcp is on the path there
    import kit_mcp
    HERE = os.path.join(kit_mcp.REPO, "art", "blender", "kit", "mcp")
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
KIT_FILE = os.path.join(REPO, "art", "blender", "assets", "kit", "FlintbornWorldKit.blend")
OUT = os.path.join(REPO, "art", "blender", "assets", "kit", "wip", "LIGHT.blend")
KEEP_TOP = ("Kit", "_wip", "_Labels", "Assets")       # top-level collections kept (emptied)
HOLDER = "_FB_PaletteHolder"


def _args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    opts = {"src": KIT_FILE, "out": OUT, "keep": []}
    i = 0
    while i < len(argv):
        k = argv[i].lstrip("-")
        if k in ("src", "out"):
            opts[k] = os.path.abspath(argv[i + 1])
            i += 2
        elif k == "keep":
            opts["keep"] = [s.strip().upper() for s in argv[i + 1].split(",") if s.strip()]
            i += 2
        else:
            raise SystemExit(f"make_workfile: unknown argument {argv[i]}")
    return opts


def _same(p, q):
    return os.path.normcase(os.path.abspath(p)) == os.path.normcase(os.path.abspath(q))


def strip(keep=()):
    """Strip the open file down to what a builder needs (see the module docstring). Returns a summary."""
    t0 = time.time()
    before = {"objects": len(bpy.data.objects), "meshes": len(bpy.data.meshes),
              "verts": sum(len(m.vertices) for m in bpy.data.meshes), "materials": len(bpy.data.materials),
              "images": len(bpy.data.images)}
    kit = bpy.data.collections.get("Kit")
    if kit is None:
        raise RuntimeError("no Kit collection: not a kit file")
    keep = {k.upper() for k in keep}
    keep_colls = [c for c in kit.children if c.name.split(" ")[0].upper() in keep]
    # palette materials first get a holder, so purging the models never takes them
    holder = bpy.data.meshes.get(HOLDER) or bpy.data.meshes.new(HOLDER)
    held = {m.name for m in holder.materials if m}
    for m in bpy.data.materials:
        if (m.name.startswith("FB_") or "flintkit_key" in m) and m.name not in held:
            holder.materials.append(m)
    holder.use_fake_user = True
    keep_objs = {o for o in bpy.data.objects if o.name.startswith("FB_")}
    for c in keep_colls:
        for o in c.all_objects:
            keep_objs.add(o)
            keep_objs.update(o.children_recursive)
    labels = {f"Label_{c.name.split(' ')[0]}" for c in keep_colls}
    keep_objs.update(o for o in bpy.data.objects if o.name in labels)
    removed = 0
    for o in list(bpy.data.objects):
        if o not in keep_objs:
            bpy.data.objects.remove(o, do_unlink=True)
            removed += 1

    def drop(c):
        for ch in list(c.children):
            drop(ch)
        bpy.data.collections.remove(c)
    for c in list(kit.children):
        if c not in keep_colls:
            drop(c)
    for c in list(bpy.context.scene.collection.children):
        if c.name not in KEEP_TOP:
            drop(c)
        else:
            for ch in list(c.children):
                if c is not kit:
                    drop(ch)
    purged = bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    after = {"objects": len(bpy.data.objects), "meshes": len(bpy.data.meshes),
             "verts": sum(len(m.vertices) for m in bpy.data.meshes), "materials": len(bpy.data.materials),
             "images": len(bpy.data.images)}
    return {"before": before, "after": after, "objects_removed": removed, "purged": purged,
            "kept_models": [c.name for c in keep_colls], "studio": sorted(o.name for o in bpy.data.objects
                                                                           if o.name.startswith("FB_")),
            "strip_s": round(time.time() - t0, 2)}


def save(out):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    t0 = time.time()
    bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
    return {"out": out, "bytes": os.path.getsize(out), "save_s": round(time.time() - t0, 2)}


def main_background(opts):
    """blender --background --python: copy the source, open the copy, strip, save, delete the copy."""
    src, out = opts["src"], opts["out"]
    if _same(out, KIT_FILE):
        raise SystemExit("make_workfile: refusing to write over the kit file")
    tmp = os.path.join(os.path.dirname(out), "_light_src.blend")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    shutil.copyfile(src, tmp)
    try:
        t0 = time.time()
        bpy.ops.wm.open_mainfile(filepath=tmp)
        res = {"open_src_s": round(time.time() - t0, 2)}
        res.update(strip(opts["keep"]))
        res.update(save(out))
    finally:
        for p in (tmp, tmp + "1"):
            if os.path.exists(p):
                os.remove(p)
    return res


def main_session(keep=(), out=OUT):
    """Inside a running session on a kit COPY: strip it in place and save it as `out`."""
    if _same(bpy.data.filepath, KIT_FILE):
        raise RuntimeError("make_workfile: this session has FlintbornWorldKit.blend itself open; use a copy")
    res = strip(keep)
    res.update(save(out))
    return res


if bpy.app.background and "--python" in sys.argv and any(a.endswith("make_workfile.py") for a in sys.argv):
    summary = main_background(_args())
    print("MAKE_WORKFILE", summary)
else:
    result = main_session()        # bgmcp: `result` is returned to the caller
