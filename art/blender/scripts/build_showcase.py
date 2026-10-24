"""Compose one showcase image of everything: the lobby map above every asset sheet and the VFX.

Lays the finished renders out as image planes under an orthographic camera, adds titles, and
renders `art/blender/renders/final/flintborn_showcase.png`. Run after the sheets and the lobby:

    blender --background --factory-startup --python art/blender/scripts/build_showcase.py
"""

import os

import bpy

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
R = os.path.join(ROOT, "renders")
OUT = os.path.join(R, "final", "flintborn_showcase.png")

PX = 100.0  # pixels per Blender unit in the output
WIDTH = 38.4  # 3840 px canvas
MARGIN = 1.0
GAP = 0.6
CAPTION = 0.55

HERO = ("lobby_map.png", "Lobby map: assembled from the asset libraries, with live VFX lights")
GRID = [
    [("01_buildings.png", "01 Buildings"), ("02_fences_towers.png", "02 Fences & towers"),
     ("03_furnishings.png", "03 Furnishings")],
    [("04_weapons_tools.png", "04 Weapons & tools"), ("05_trees_plants.png", "05 Trees & plants"),
     ("06_rocks_runes_camp.png", "06 Rocks, runes & camp")],
    [("07_terrain_kit.png", "07 Terrain kit"), ("08_vfx_dim.png", "08 VFX previews"),
     ("08_vfx_textures.png", "08 VFX particle textures")],
]
BG = (0.86, 0.84, 0.80)
INK = (0.17, 0.13, 0.10)


def reset():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)


def image_plane(path, x, y_top, w):
    """Place an image plane `w` wide with its top-left corner at (x, y_top). Returns its height."""
    img = bpy.data.images.load(path, check_existing=True)
    iw, ih = img.size
    h = w * ih / iw
    me = bpy.data.meshes.new(os.path.basename(path))
    me.from_pydata([(0, -h, 0), (w, -h, 0), (w, 0, 0), (0, 0, 0)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for loop, co in zip(uv.data, [(0, 0), (1, 0), (1, 1), (0, 1)]):
        loop.uv = co
    mat = bpy.data.materials.new("M_" + os.path.basename(path))
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Smart"
    emit = nt.nodes.new("ShaderNodeEmission")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(tex.outputs["Color"], emit.inputs["Color"])
    nt.links.new(emit.outputs[0], out.inputs["Surface"])
    me.materials.append(mat)
    ob = bpy.data.objects.new(me.name, me)
    ob.location = (x, y_top, 0)
    bpy.context.scene.collection.objects.link(ob)
    return h


def text(body, x, y_top, size, bold=False):
    cu = bpy.data.curves.new("T", "FONT")
    cu.body = body
    cu.size = size
    cu.align_y = "TOP"
    try:
        cu.font = bpy.data.fonts.load(r"C:/Windows/Fonts/segoeuib.ttf" if bold else r"C:/Windows/Fonts/segoeui.ttf")
    except RuntimeError:
        pass
    ob = bpy.data.objects.new("T", cu)
    ob.location = (x, y_top, 0.01)
    mat = bpy.data.materials.new("Ink")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    emit = nt.nodes.new("ShaderNodeEmission")
    emit.inputs["Color"].default_value = (*INK, 1)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(emit.outputs[0], out.inputs["Surface"])
    cu.materials.append(mat)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def main():
    reset()
    scene = bpy.context.scene
    y = -MARGIN
    text("FLINTBORN — LOBBY & ASSET LIBRARY", MARGIN, y, 1.1, bold=True)
    y -= 1.5
    text("Blender asset sheets built from the reference art · 1 unit = 1 Roblox stud", MARGIN, y, 0.5)
    y -= 1.1
    inner = WIDTH - 2 * MARGIN
    y -= image_plane(os.path.join(R, HERO[0]), MARGIN, y, inner)
    text(HERO[1], MARGIN, y - 0.15, CAPTION)
    y -= CAPTION + 0.3 + GAP
    cols = 3
    cw = (inner - GAP * (cols - 1)) / cols
    for row in GRID:
        heights = []
        for i, (name, caption) in enumerate(row):
            path = os.path.join(R, name)
            if not os.path.exists(path):
                continue
            x = MARGIN + i * (cw + GAP)
            text(caption, x, y, CAPTION, bold=True)
            heights.append(image_plane(path, x, y - CAPTION - 0.2, cw))
        y -= CAPTION + 0.2 + (max(heights) if heights else 0) + GAP
    total_h = -y + MARGIN - GAP

    world = scene.world or bpy.data.worlds.new("W")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (*BG, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = max(WIDTH, total_h)
    cam.location = (WIDTH / 2, -total_h / 2, 10)
    scene.collection.objects.link(cam)
    scene.camera = cam
    scene.render.engine = "BLENDER_EEVEE"
    scene.view_settings.view_transform = "Standard"
    scene.render.resolution_x = int(WIDTH * PX)
    scene.render.resolution_y = int(total_h * PX)
    scene.render.resolution_percentage = 100
    scene.eevee.taa_render_samples = 16
    scene.render.filepath = OUT
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    bpy.ops.render.render(write_still=True)
    print("SHOWCASE", OUT, scene.render.resolution_x, scene.render.resolution_y)


main()
