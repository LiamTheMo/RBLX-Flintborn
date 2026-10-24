"""Live preview: mirror a sheet's assets into the open Blender GUI.

Run inside the interactive Blender (through the Blender MCP), never in a build
script. Each sheet owns one collection ("Sheet_01_buildings", ...) in the
"Flintborn Assets" scene and only ever replaces its own objects, so several
builders can sync safely one after another.

    import sys; sys.path.insert(0, r"D:/Projects/Roblox/RBLX-Flintborn/art/blender/lib")
    import importlib, livesync; importlib.reload(livesync)
    result = livesync.sync("01_buildings")
"""

import os
import re

import bpy

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHEETS = ["01_buildings", "02_fences_towers", "03_furnishings", "04_weapons_tools",
          "05_trees_plants", "06_rocks_runes_camp", "07_terrain_kit"]
ROW_SPACING = 70.0  # studs between sheet rows along -Y
SCENE_NAME = "Flintborn Assets"


def _scene():
    scene = bpy.data.scenes.get(SCENE_NAME)
    if scene is None:
        scene = bpy.context.scene
        scene.name = SCENE_NAME
    return scene


def _base_name(name):
    return re.sub(r"\.\d{3}$", "", name)


def sync(sheet):
    """Replace this sheet's preview collection with the latest saved assets."""
    path = os.path.join(ROOT, "assets", sheet + ".blend")
    if not os.path.exists(path):
        return {"sheet": sheet, "error": "no saved .blend yet: " + path}
    scene = _scene()
    cname = "Sheet_" + sheet
    coll = bpy.data.collections.get(cname)
    if coll is None:
        coll = bpy.data.collections.new(cname)
        scene.collection.children.link(coll)
    # Drop the previous version of this sheet only.
    for obj in list(coll.objects):
        mesh = obj.data if obj.type == "MESH" else None
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    existing_mats = {m.name: m for m in bpy.data.materials}
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.objects = [n for n in src.objects if not n.startswith("FB_")]
    row = SHEETS.index(sheet) if sheet in SHEETS else len(SHEETS)
    names = []
    for obj in dst.objects:
        keep = obj is not None and (obj.type == "MESH" or obj.get("vfx_kind"))
        if not keep:
            if obj is not None:
                bpy.data.objects.remove(obj, do_unlink=True)
            continue
        coll.objects.link(obj)
        if obj.parent is None:
            obj.location.y -= row * ROW_SPACING
        if obj.type != "MESH":
            continue
        # Reuse the shared palette materials instead of piling up FB_wood.001 copies.
        for slot in obj.material_slots:
            m = slot.material
            if m is not None and _base_name(m.name) != m.name and _base_name(m.name) in existing_mats:
                slot.material = existing_mats[_base_name(m.name)]
        names.append(obj.name)
    for m in list(bpy.data.materials):
        if m.users == 0:
            bpy.data.materials.remove(m)
    for me in list(bpy.data.meshes):
        if me.users == 0:
            bpy.data.meshes.remove(me)
    return {"sheet": sheet, "collection": cname, "objects": len(names), "names": names}
