"""Build sheet 09: the default player character (R6) and its clothing.

Matches art/reference/character/hair_01_bald.png: a soft, rounded blocky body
in warm peach skin with the classic smile face, a tan hide wrap over the right
shoulder with a ragged hem and a knot at the left hip, and ragged brown shorts.
The proportions are Roblox's default R6 sizes, not the reference's:

    Head  part 2 x 1 x 1 (mesh ~1.25 rounded, centred 0.5 above the neck)
    Torso 2 x 2 x 1   Arms 1 x 2 x 1   Legs 1 x 2 x 1   (5 studs tall)

Rig: an armature with the standard R6 joints (RootJoint, Neck, Left/Right
Shoulder, Left/Right Hip) at Roblox's pivots; every body part is rigidly
parented to its bone, so any R6 animation poses it the same way. The joint
C0/C1 values exported in the manifest are Roblox's defaults, so the default
Animate script and every R6 animation work unchanged.

Clothing is separate meshes so tribes can colour them: the Shirt (hide wrap and
knot) rides on the Torso; the Pants are PantsWaist (Torso), PantsLeftLeg and
PantsRightLeg (their legs), so each piece follows its R6 limb.

Textures are baked from procedural shaders (Cycles) at 1024 px: colour, normal
and roughness for the shirt and the pants, a neutral pants colour map (tinted
in Roblox with SurfaceAppearance.Color) plus one baked colour map per tribe
colour, and the face decal.

Outputs:
    art/blender/assets/09_character.blend
    art/character/textures/*.png
    art/roblox/character/*.glb + manifest.json   (Roblox-ready, like the lobby;
                                                  textures stay in art/character/textures)
    art/blender/renders/09_character_{turnaround,tribes,parts,rig,textures}.png

Run through the wrapper:
    art/blender/run.sh scripts/build_09_character.py
"""

import json
import math
import os
import sys

import blf
import bmesh
import bpy
import imbuf
import numpy as np
from mathutils import Matrix, Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
BLENDER_DIR = os.path.dirname(HERE)
ART = os.path.dirname(BLENDER_DIR)
sys.path.insert(0, os.path.join(BLENDER_DIR, "lib"))
import flintkit as fk  # noqa: E402

OUT_BLEND = os.path.join(BLENDER_DIR, "assets", "09_character.blend")
TEX_DIR = os.path.join(ART, "character", "textures")
EXPORT_DIR = os.path.join(ART, "roblox", "character")
RENDER_DIR = os.path.join(BLENDER_DIR, "renders")
FONT_TITLE = r"C:\Windows\Fonts\georgiab.ttf"
FONT_BODY = r"C:\Windows\Fonts\georgia.ttf"

TEX_SIZE = 1024
BG = "#F7F3EA"  # the reference sheet's warm cream
SKIN = "#F1C7A3"
SHIRT = "#C8B392"
PANTS_NEUTRAL = "#BDB5A8"  # tinted per tribe; baked variants below
TRIBES = [
    ("Earth", "#6B4A2F"),  # the default, as in the reference
    ("Ember", "#9C3328"),
    ("Clay", "#B5602F"),
    ("Ochre", "#B98A2E"),
    ("Moss", "#4F6C2F"),
    ("Tide", "#2E7671"),
    ("River", "#2F5C90"),
    ("Dusk", "#5D3F79"),
    ("Ash", "#55575C"),
    ("Bone", "#D6CAB1"),
]

# R6 parts: name -> (size x, y, z in Blender axes: x right-left, y depth, z up), centre.
# Front faces -Y, so the character's right side is -X.
PARTS = {
    "Torso": ((2.0, 1.0, 2.0), (0.0, 0.0, 3.0)),
    "Head": ((1.25, 1.25, 1.2), (0.0, 0.0, 4.5)),
    "Right Arm": ((1.0, 1.0, 2.0), (-1.5, 0.0, 3.0)),
    "Left Arm": ((1.0, 1.0, 2.0), (1.5, 0.0, 3.0)),
    "Right Leg": ((1.0, 1.0, 2.0), (-0.5, 0.0, 1.0)),
    "Left Leg": ((1.0, 1.0, 2.0), (0.5, 0.0, 1.0)),
}
ROUNDING = {"Head": 0.3, "Torso": 0.12}
# Bones: name -> (head = joint pivot, tail, parent bone, part it carries).
BONES = {
    "HumanoidRootPart": ((0, 0, 2.0), (0, 0, 3.0), None, None),
    "Torso": ((0, 0, 3.0), (0, 0, 4.0), "HumanoidRootPart", "Torso"),
    "Head": ((0, 0, 4.0), (0, 0, 5.1), "Torso", "Head"),
    # Limb bones hang straight down from the joint, so their local X is the world X
    # axis R6 shoulders and hips swing about (forward = negative X rotation).
    "Right Arm": ((-1.0, 0, 3.5), (-1.0, 0, 2.0), "Torso", "Right Arm"),
    "Left Arm": ((1.0, 0, 3.5), (1.0, 0, 2.0), "Torso", "Left Arm"),
    "Right Leg": ((-1.0, 0, 2.0), (-1.0, 0, 0.0), "Torso", "Right Leg"),
    "Left Leg": ((1.0, 0, 2.0), (1.0, 0, 0.0), "Torso", "Left Leg"),
}
# Roblox's default R6 Motor6D values (C0 on Part0, C1 on Part1), as 12 numbers.
MOTORS = {
    "RootJoint": ("HumanoidRootPart", "Torso", [0, 0, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0],
                  [0, 0, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0]),
    "Neck": ("Torso", "Head", [0, 1, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0], [0, -0.5, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0]),
    "Right Shoulder": ("Torso", "Right Arm", [1, 0.5, 0, 0, 0, 1, 0, 1, 0, -1, 0, 0],
                       [-0.5, 0.5, 0, 0, 0, 1, 0, 1, 0, -1, 0, 0]),
    "Left Shoulder": ("Torso", "Left Arm", [-1, 0.5, 0, 0, 0, -1, 0, 1, 0, 1, 0, 0],
                      [0.5, 0.5, 0, 0, 0, -1, 0, 1, 0, 1, 0, 0]),
    "Right Hip": ("Torso", "Right Leg", [1, -1, 0, 0, 0, 1, 0, 1, 0, -1, 0, 0],
                  [0.5, 1, 0, 0, 0, 1, 0, 1, 0, -1, 0, 0]),
    "Left Hip": ("Torso", "Left Leg", [-1, -1, 0, 0, 0, -1, 0, 1, 0, 1, 0, 0],
                 [-0.5, 1, 0, 0, 0, -1, 0, 1, 0, 1, 0, 0]),
}
CLOTHING = {  # mesh -> body part it is welded to
    "Shirt": "Torso",
    "PantsWaist": "Torso",
    "PantsRightLeg": "Right Leg",
    "PantsLeftLeg": "Left Leg",
}


def lin(hexcol):
    return fk.hex_rgb(hexcol)


def srgb(c):
    c = np.clip(c, 0, None)
    return np.where(c <= 0.0031308, 12.92 * c, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def to_lin(c):
    return np.where(c <= 0.04045, c / 12.92, np.power((c + 0.055) / 1.055, 2.4))


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

def link(obj, collection):
    collection.objects.link(obj)
    return obj


def rounded_box(name, size, centre, radius, collection):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=radius, segments=6, profile=0.5, affect="EDGES")
    for f in bm.faces:
        f.smooth = True
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = link(bpy.data.objects.new(name, me), collection)
    obj.location = centre
    return obj


def rounded_rect(a, b, r, s):
    """Point and outward normal at arc-length fraction s of a rounded rectangle
    (half sizes a, b, corner radius r) centred on the origin, counter-clockwise."""
    straight = [2 * (b - r), 2 * (a - r), 2 * (b - r), 2 * (a - r)]  # right, top, left, bottom
    arc = math.pi * r / 2
    total = sum(straight) + 4 * arc
    d = (s % 1.0) * total
    corners = [(a - r, b - r), (-(a - r), b - r), (-(a - r), -(b - r)), (a - r, -(b - r))]
    starts = [(a, -(b - r)), (a - r, b), (-a, b - r), (-(a - r), -b)]
    dirs = [(0, 1), (-1, 0), (0, -1), (1, 0)]
    for side in range(4):
        if d <= straight[side]:
            sx, sy = starts[side]
            dx, dy = dirs[side]
            return (sx + dx * d, sy + dy * d), (dy, -dx)
        d -= straight[side]
        if d <= arc:
            cx, cy = corners[side]
            angle = side * math.pi / 2 + d / r
            n = (math.cos(angle), math.sin(angle))
            return (cx + r * n[0], cy + r * n[1]), n
        d -= arc
    return starts[0], (1, 0)


def shell(name, centre, a, b, r, bottom, top, collection, ring_count, around, keep=None, flare=None, cut=None):
    """A tube of quads around a rounded-rect cross-section from z = bottom(theta) to top,
    with faces kept by keep(x, y, z), then cut cleanly by `cut` = (point, normal, wave):
    everything on the normal's side of that plane goes, and the new edge gets a soft
    wave(x) so it reads as cut hide. Solidified later."""
    bm = bmesh.new()
    grid = []
    for i in range(ring_count + 1):
        u = i / ring_count
        row = []
        for j in range(around):
            s = j / around
            (x, y), (nx, ny) = rounded_rect(a, b, r, s)
            z0 = bottom(s)
            z = z0 + u * (top - z0)
            push = flare(z) if flare else 0.0
            row.append(bm.verts.new((centre[0] + x + nx * push, centre[1] + y + ny * push, z)))
        grid.append(row)
    for i in range(ring_count):
        for j in range(around):
            quad = [grid[i][j], grid[i][(j + 1) % around], grid[i + 1][(j + 1) % around], grid[i + 1][j]]
            cx = sum(v.co.x for v in quad) / 4 - centre[0]
            cz = sum(v.co.z for v in quad) / 4
            cy = sum(v.co.y for v in quad) / 4 - centre[1]
            if keep is None or keep(cx, cy, cz):
                f = bm.faces.new(quad)
                f.smooth = True
    loose = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm, geom=loose, context="VERTS")
    if cut:
        point, normal, wave = cut
        normal = Vector(normal).normalized()
        geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
        result = bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=point, plane_no=normal,
                                        clear_outer=True)
        for v in result["geom_cut"]:
            if isinstance(v, bmesh.types.BMVert):
                v.co -= normal * wave(v.co.x)
        for f in bm.faces:
            f.smooth = True
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return link(bpy.data.objects.new(name, me), collection)


def strap(name, collection):
    """The hide band over the right shoulder: a sweep across the torso top from the
    front, over the rounded edge, to the back."""
    bm = bmesh.new()
    # Lies flush over the shoulder, just proud of the wrap so the two never z-fight.
    a_front, top, r = 0.552, 4.052, 0.15
    path = []
    for k in range(9):  # front face, going up
        path.append((-a_front, 3.55 + k * (top - r - 3.55) / 8))
    for k in range(1, 7):  # front corner
        t = k / 6 * math.pi / 2
        path.append((-(a_front - r) - r * math.cos(t), top - r + r * math.sin(t)))
    for k in range(1, 10):  # over the top
        path.append((-(a_front - r) + k * 2 * (a_front - r) / 9, top))
    for k in range(1, 7):  # back corner
        t = k / 6 * math.pi / 2
        path.append(((a_front - r) + r * math.sin(t), top - r + r * math.cos(t)))
    for k in range(1, 9):  # back face, going down
        path.append((a_front, top - r - k * (top - r - 3.55) / 8))
    xs = [-1.052, -0.96, -0.8, -0.62, -0.44, -0.32]
    rows = []
    for py, pz in path:
        rows.append([bm.verts.new((x, py, pz)) for x in xs])
    for i in range(len(rows) - 1):
        for j in range(len(xs) - 1):
            f = bm.faces.new([rows[i][j], rows[i][j + 1], rows[i + 1][j + 1], rows[i + 1][j]])
            f.smooth = True
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return link(bpy.data.objects.new(name, me), collection)


def blob(bm, centre, radii, rot_z=0.0, rot_x=0.0):
    geom = bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=9, radius=1.0)
    verts = geom["verts"]
    M = (Matrix.Translation(centre) @ Matrix.Rotation(rot_z, 4, "Z") @ Matrix.Rotation(rot_x, 4, "X")
         @ Matrix.Diagonal((*radii, 1)))
    bmesh.ops.transform(bm, matrix=M, verts=verts)
    for v in verts:
        for f in v.link_faces:
            f.smooth = True


def knot(name, collection):
    """The tied knot at the left hip, front: a bunched centre, two lobes and two tails."""
    bm = bmesh.new()
    c = Vector((0.92, -0.58, 2.36))
    blob(bm, c, (0.17, 0.12, 0.15))
    blob(bm, c + Vector((-0.17, -0.01, 0.05)), (0.13, 0.09, 0.09), rot_z=0.3)
    blob(bm, c + Vector((0.15, 0.02, 0.06)), (0.11, 0.09, 0.09), rot_z=-0.4)
    blob(bm, c + Vector((-0.05, -0.03, -0.27)), (0.08, 0.05, 0.21), rot_x=0.15)
    blob(bm, c + Vector((0.09, -0.02, -0.23)), (0.07, 0.05, 0.17), rot_z=-0.3, rot_x=0.1)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return link(bpy.data.objects.new(name, me), collection)


def apply_modifiers(obj):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    obj.modifiers.clear()
    old = obj.data
    obj.data = me
    me.name = old.name
    bpy.data.meshes.remove(old)


def join(target, others):
    for o in others:
        o.data.transform(o.matrix_world)
        o.matrix_world = Matrix()
    target.data.transform(target.matrix_world)
    target.matrix_world = Matrix()
    bm = bmesh.new()
    for o in [target] + others:
        bm.from_mesh(o.data)
    bm.to_mesh(target.data)
    bm.free()
    for o in others:
        bpy.data.objects.remove(o)


def wavy(base, amp, freq, seed):
    def f(s):
        t = s * 2 * math.pi
        return (base + amp * math.sin(freq * t + seed) + amp * 0.6 * math.sin(2.7 * freq * t + seed * 2.1)
                + amp * 0.5 * noise.noise(Vector((math.cos(t) * 2, math.sin(t) * 2, seed))))
    return f


def build_clothing(col):
    # The wrap: a tube around the torso, cut on the diagonal from the right shoulder
    # (-X, top) to below the left armpit, hanging past the torso over the shorts.
    # The cut runs from the right shoulder (x -1.06, top) to the left side at z 3.2.
    diagonal = ((-1.04, 0.0, 4.04), (0.84, 0.0, 2.08), lambda x: 0.02 + 0.02 * math.sin(x * 9.0 + 1.3))


    # Flat like the master: the wrap hugs the torso straight down to a gently wavy
    # hem, with no outward flare.
    wrap = shell("Shirt", (0, 0, 0), 1.04, 0.54, 0.15, wavy(1.62, 0.035, 7, 1.0), 4.04, col,
                 ring_count=40, around=96, cut=diagonal)
    band = strap("ShirtStrap", col)
    tie = knot("ShirtKnot", col)
    # No subdivision: smooth shading keeps the cloth soft and each mesh well under
    # Roblox's ~20k triangle limit.
    for o in (wrap, band):
        mod = o.modifiers.new("Thick", "SOLIDIFY")
        mod.thickness = 0.035
        mod.offset = -1.0
        mod.use_even_offset = True
        apply_modifiers(o)
    join(wrap, [band, tie])

    pants = []
    # Under the shirt: kept close to the torso so the wrap never clips through it.
    waist = shell("PantsWaist", (0, 0, 0), 1.02, 0.52, 0.14, lambda s: 1.9, 2.32, col, ring_count=6, around=72)
    pants.append(waist)
    for name, x, seed in (("PantsRightLeg", -0.5, 2.0), ("PantsLeftLeg", 0.5, 5.0)):
        leg = shell(name, (x, 0, 0), 0.528, 0.528, 0.13, wavy(0.97, 0.03, 5, seed), 2.06, col,
                    ring_count=16, around=56)
        pants.append(leg)
    for o in pants:
        mod = o.modifiers.new("Thick", "SOLIDIFY")
        mod.thickness = 0.03
        mod.offset = -1.0
        mod.use_even_offset = True
        apply_modifiers(o)
    return wrap, pants


# ---------------------------------------------------------------------------
# Materials and baking
# ---------------------------------------------------------------------------

def new_image(name, colorspace="sRGB"):
    img = bpy.data.images.new(name, TEX_SIZE, TEX_SIZE, alpha=False, float_buffer=False)
    img.colorspace_settings.name = colorspace
    return img


def shader_material(name, kind):
    """Procedural hide (shirt) or woven wool (pants) used only for baking."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    n, l = nt.nodes, nt.links
    bsdf = n["Principled BSDF"]
    coord = n.new("ShaderNodeTexCoord")
    mottle = n.new("ShaderNodeTexNoise")
    mottle.inputs["Scale"].default_value = 5.0
    mottle.inputs["Detail"].default_value = 6.0
    l.new(coord.outputs["Object"], mottle.inputs["Vector"])
    blotch = n.new("ShaderNodeTexNoise")
    blotch.inputs["Scale"].default_value = 1.4
    blotch.inputs["Detail"].default_value = 2.0
    l.new(coord.outputs["Object"], blotch.inputs["Vector"])
    base = lin(SHIRT if kind == "shirt" else PANTS_NEUTRAL)
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[0].color = (*(c * 0.93 for c in base), 1)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (*(min(1.0, c * 1.04) for c in base), 1)
    l.new(mottle.outputs["Fac"], ramp.inputs["Fac"])
    darken = n.new("ShaderNodeMix")
    darken.data_type = "RGBA"
    darken.blend_type = "MULTIPLY"
    l.new(ramp.outputs["Color"], darken.inputs["A"])
    blotch_ramp = n.new("ShaderNodeValToRGB")
    blotch_ramp.color_ramp.elements[0].position = 0.35
    blotch_ramp.color_ramp.elements[0].color = (0.95, 0.94, 0.93, 1)
    blotch_ramp.color_ramp.elements[1].position = 0.7
    blotch_ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    l.new(blotch.outputs["Fac"], blotch_ramp.inputs["Fac"])
    l.new(blotch_ramp.outputs["Color"], darken.inputs["B"])
    darken.inputs["Factor"].default_value = 1.0
    color_out = darken.outputs["Result"]
    # Surface detail: suede grain + soft folds (shirt), or a woven grid (pants).
    grain = n.new("ShaderNodeTexNoise")
    grain.inputs["Scale"].default_value = 70.0 if kind == "shirt" else 45.0
    grain.inputs["Detail"].default_value = 3.0
    l.new(coord.outputs["Object"], grain.inputs["Vector"])
    folds = n.new("ShaderNodeTexNoise")
    folds.inputs["Scale"].default_value = 3.0
    folds.inputs["Detail"].default_value = 2.0
    l.new(coord.outputs["Object"], folds.inputs["Vector"])
    bump1 = n.new("ShaderNodeBump")
    bump1.inputs["Strength"].default_value = 0.07
    bump1.inputs["Distance"].default_value = 0.02
    l.new(grain.outputs["Fac"], bump1.inputs["Height"])
    bump2 = n.new("ShaderNodeBump")
    bump2.inputs["Strength"].default_value = 0.2
    bump2.inputs["Distance"].default_value = 0.05
    l.new(folds.outputs["Fac"], bump2.inputs["Height"])
    l.new(bump1.outputs["Normal"], bump2.inputs["Normal"])
    normal_out = bump2.outputs["Normal"]
    if kind == "pants":
        weave_u = n.new("ShaderNodeTexWave")
        weave_u.inputs["Scale"].default_value = 26.0
        weave_u.bands_direction = "X"
        weave_v = n.new("ShaderNodeTexWave")
        weave_v.inputs["Scale"].default_value = 26.0
        weave_v.bands_direction = "Z"
        for w in (weave_u, weave_v):
            l.new(coord.outputs["Object"], w.inputs["Vector"])
        weave = n.new("ShaderNodeMath")
        weave.operation = "MULTIPLY"
        l.new(weave_u.outputs["Fac"], weave.inputs[0])
        l.new(weave_v.outputs["Fac"], weave.inputs[1])
        bump3 = n.new("ShaderNodeBump")
        bump3.inputs["Strength"].default_value = 0.18
        bump3.inputs["Distance"].default_value = 0.02
        l.new(weave.outputs["Value"], bump3.inputs["Height"])
        l.new(normal_out, bump3.inputs["Normal"])
        normal_out = bump3.outputs["Normal"]
        weave_tone = n.new("ShaderNodeMix")
        weave_tone.data_type = "RGBA"
        weave_tone.blend_type = "MULTIPLY"
        weave_ramp = n.new("ShaderNodeValToRGB")
        weave_ramp.color_ramp.elements[0].color = (0.9, 0.9, 0.9, 1)
        weave_ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
        l.new(weave.outputs["Value"], weave_ramp.inputs["Fac"])
        l.new(color_out, weave_tone.inputs["A"])
        l.new(weave_ramp.outputs["Color"], weave_tone.inputs["B"])
        weave_tone.inputs["Factor"].default_value = 1.0
        color_out = weave_tone.outputs["Result"]
    l.new(color_out, bsdf.inputs["Base Color"])
    l.new(normal_out, bsdf.inputs["Normal"])
    rough = n.new("ShaderNodeMapRange")
    rough.inputs["To Min"].default_value = 0.78
    rough.inputs["To Max"].default_value = 0.95
    l.new(grain.outputs["Fac"], rough.inputs["Value"])
    l.new(rough.outputs["Result"], bsdf.inputs["Roughness"])
    return mat


def unwrap(obj):
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.01)
    bpy.ops.object.mode_set(mode="OBJECT")


def bake_set(objs, mat, prefix):
    """Bake colour, normal and roughness for objects sharing one UV layout atlas."""
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 8
    scene.render.bake.margin = 8
    images = {
        "color": new_image(prefix + "_color"),
        "normal": new_image(prefix + "_normal", "Non-Color"),
        "roughness": new_image(prefix + "_roughness", "Non-Color"),
    }
    node = mat.node_tree.nodes.new("ShaderNodeTexImage")
    mat.node_tree.nodes.active = node
    for o in objs:
        o.data.materials.clear()
        o.data.materials.append(mat)
    for o in bpy.context.view_layer.objects:
        o.select_set(o in objs)
    bpy.context.view_layer.objects.active = objs[0]
    for kind, kwargs in (("color", {"type": "DIFFUSE", "pass_filter": {"COLOR"}}),
                         ("normal", {"type": "NORMAL", "normal_space": "TANGENT"}),
                         ("roughness", {"type": "ROUGHNESS"})):
        node.image = images[kind]
        bpy.ops.object.bake(use_clear=True, margin=8, **kwargs)
        path = os.path.join(TEX_DIR, f"{prefix}_{kind}.png")
        images[kind].filepath_raw = path
        images[kind].file_format = "PNG"
        images[kind].save()
    mat.node_tree.nodes.remove(node)
    return images


def tribe_variants(neutral_path):
    """One pants colour map per tribe: the neutral map's detail, tinted in linear space."""
    img = bpy.data.images.load(neutral_path, check_existing=False)
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    bpy.data.images.remove(img)
    base = np.array(lin(PANTS_NEUTRAL), dtype=np.float32)
    detail = to_lin(px[..., :3]) / base
    paths = {}
    for name, hexcol in TRIBES:
        tinted = srgb(np.clip(detail * np.array(lin(hexcol), dtype=np.float32), 0, 1))
        out = np.concatenate([tinted, np.ones((h, w, 1), np.float32)], axis=2)
        image = bpy.data.images.new("pants_" + name, w, h, alpha=False, float_buffer=False)
        image.pixels[:] = out.ravel()
        path = os.path.join(TEX_DIR, f"pants_color_{name.lower()}.png")
        image.filepath_raw = path
        image.file_format = "PNG"
        image.save()
        bpy.data.images.remove(image)
        paths[name] = path
    return paths


def face_texture(path, size=512):
    """The classic smile: two tall oval eyes and a round smile, black on transparent."""
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32) + 0.5
    ink = np.zeros((size, size), np.float32)
    for cx in (0.405 * size, 0.595 * size):
        cy, rx, ry = 0.36 * size, 0.036 * size, 0.082 * size
        d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
        ink = np.maximum(ink, np.clip((1.0 - d) * rx, 0, 1))
    t = np.linspace(-1, 1, 160)
    half_width, radius, cy = 0.2 * size, 0.215 * size, 0.53 * size
    pts = np.stack([size / 2 + half_width * t, cy + np.sqrt(radius ** 2 - (half_width * t) ** 2)], 1)
    stroke = 0.017 * size
    for y0 in range(0, size, 64):
        sub_x, sub_y = xx[y0:y0 + 64, :, None], yy[y0:y0 + 64, :, None]
        dist = np.sqrt((sub_x - pts[None, None, :, 0]) ** 2 + (sub_y - pts[None, None, :, 1]) ** 2).min(2)
        ink[y0:y0 + 64] = np.maximum(ink[y0:y0 + 64], np.clip(stroke - dist + 0.5, 0, 1))
    rgba = np.zeros((size, size, 4), np.float32)
    rgba[..., :3] = 0.07
    rgba[..., 3] = ink
    image = bpy.data.images.new("face", size, size, alpha=True, float_buffer=False)
    image.pixels[:] = rgba[::-1].ravel()
    image.filepath_raw = path
    image.file_format = "PNG"
    image.save()
    return image


def textured_material(name, color, normal, roughness):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    for img, socket, cs in ((color, "Base Color", "sRGB"), (roughness, "Roughness", "Non-Color")):
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(img, check_existing=True) if isinstance(img, str) else img
        tex.image.colorspace_settings.name = cs
        nt.links.new(tex.outputs["Color"], bsdf.inputs[socket])
    ntex = nt.nodes.new("ShaderNodeTexImage")
    ntex.image = bpy.data.images.load(normal, check_existing=True) if isinstance(normal, str) else normal
    ntex.image.colorspace_settings.name = "Non-Color"
    nmap = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(ntex.outputs["Color"], nmap.inputs["Color"])
    nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def skin_material():
    mat = bpy.data.materials.new("Skin")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*lin(SKIN), 1)
    bsdf.inputs["Roughness"].default_value = 0.55
    return mat


def face_material(image):
    mat = bpy.data.materials.new("Face")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = image
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    bsdf.inputs["Roughness"].default_value = 0.5
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "BLENDED"
    return mat


# ---------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------

def build_rig(col, parts, clothing):
    arm_data = bpy.data.armatures.new("R6Rig")
    rig = link(bpy.data.objects.new("R6Rig", arm_data), col)
    bpy.context.view_layer.objects.active = rig
    for o in bpy.context.view_layer.objects:
        o.select_set(o is rig)
    bpy.ops.object.mode_set(mode="EDIT")
    for name, (head, tail, parent, _) in BONES.items():
        bone = arm_data.edit_bones.new(name)
        bone.head, bone.tail = Vector(head), Vector(tail)
    for name, (_, _, parent, _) in BONES.items():
        if parent:
            arm_data.edit_bones[name].parent = arm_data.edit_bones[parent]
    bpy.ops.object.mode_set(mode="OBJECT")
    # Rigid parenting: each part (and the clothing welded to it) follows one bone.
    def attach(obj, bone_name):
        world = obj.matrix_world.copy()
        obj.parent = rig
        obj.parent_type = "BONE"
        obj.parent_bone = bone_name
        bone = rig.pose.bones[bone_name]
        obj.matrix_world = world
        return bone

    bpy.context.view_layer.update()
    for name, (_, _, _, part) in BONES.items():
        if part:
            attach(parts[part], name)
    for name, part in CLOTHING.items():
        attach(clothing[name], part)
    attach(parts["Face"], "Head")
    return rig


def pose(rig, angles):
    """angles: bone -> (x, y, z) degrees about the bone's own axes; {} = rest."""
    for bone in rig.pose.bones:
        bone.rotation_mode = "XYZ"
        a = angles.get(bone.name, (0, 0, 0))
        bone.rotation_euler = tuple(math.radians(v) for v in a)
    bpy.context.view_layer.update()


# ---------------------------------------------------------------------------
# Rendering and sheets
# ---------------------------------------------------------------------------

def studio():
    fk.BG_HEX = BG
    fk.GROUND_ALBEDO = 0.74
    scene = bpy.context.scene
    fk._studio(scene)
    scene.render.engine = "BLENDER_EEVEE"
    try:
        scene.eevee.taa_render_samples = 64
    except AttributeError:
        pass
    cam = bpy.data.objects["FB_Cam"]
    cam.data.type = "ORTHO"
    key = bpy.data.objects["FB_Key"]
    key.rotation_euler = (math.radians(55), 0, math.radians(-30))
    key.data.energy = 3.0
    key.data.angle = math.radians(25)  # soft contact shadows like the reference
    ground = bpy.data.objects["FB_Ground"]
    ground.location = (0, 0, 0)
    # With the camera tilted down, the floor fills the whole backdrop; this albedo
    # makes it render as the sheet's cream under the key and ambient light.
    ground.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (
        0.842, 0.782, 0.680, 1)
    return scene


def render_cell(path, root_rot_deg, res=(480, 640), scale=6.4, centre_z=2.7, offset_x=0.0):
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    rig = bpy.data.objects["R6Rig"]
    rig.rotation_euler = (0, 0, math.radians(root_rot_deg))
    rig.location = (offset_x, 0, 0)
    cam = bpy.data.objects["FB_Cam"]
    cam.data.ortho_scale = scale
    el = math.radians(6)
    cam.location = (offset_x, -30 * math.cos(el), centre_z + 30 * math.sin(el))
    cam.rotation_euler = (math.radians(90) - el, 0, 0)
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    rig.rotation_euler = (0, 0, 0)
    rig.location = (0, 0, 0)
    return path


def load_px(path):
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[::-1].copy()
    bpy.data.images.remove(img)
    return px


def save_px(path, px):
    h, w = px.shape[:2]
    img = bpy.data.images.new("sheet", w, h, alpha=True, float_buffer=False)
    img.pixels[:] = px[::-1].ravel()
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


def canvas(w, h):
    px = np.ones((h, w, 4), np.float32)
    px[..., :3] = [int(BG[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return px


def paste(dst, src, x, y):
    h, w = src.shape[:2]
    dst[y:y + h, x:x + w] = src[:, :, :]


def write_text(png, items):
    """items: (text, x_centre, y_baseline_from_top, size, font, rgb)."""
    buf = imbuf.load(png)
    height = buf.size[1]
    for text, cx, by, size, font, rgb in items:
        fid = blf.load(font if os.path.exists(font) else "")
        with blf.bind_imbuf(fid, buf):
            blf.size(fid, size)
            width, _ = blf.dimensions(fid, text)
            blf.color(fid, *rgb, 1.0)
            blf.position(fid, cx - width / 2, height - by, 0)
            blf.draw_buffer(fid, text)
    imbuf.write(buf, filepath=png)


INK = (0.12, 0.09, 0.08)


def sheet_turnaround(cells_dir):
    views = [("FRONT", 0), ("SIDE", 90), ("BACK", 180), ("THREE-QUARTER", 32)]
    w, h = 440, 600
    out = canvas(w * 4 + 80, h + 260)
    for i, (label, rot) in enumerate(views):
        p = render_cell(os.path.join(cells_dir, f"turn_{i}.png"), rot, res=(w, h))
        paste(out, load_px(p), 40 + i * w, 130)
    path = os.path.join(RENDER_DIR, "09_character_turnaround.png")
    save_px(path, out)
    items = [("FLINTBORN  —  DEFAULT CHARACTER (R6)", out.shape[1] / 2, 86, 44, FONT_TITLE, INK)]
    for i, (label, _) in enumerate(views):
        items.append((label, 40 + i * w + w / 2, 130 + h + 52, 26, FONT_TITLE, INK))
    items.append(("Roblox default R6 proportions · 5 studs tall · clothing is separate meshes",
                  out.shape[1] / 2, 130 + h + 100, 20, FONT_BODY, (0.35, 0.3, 0.27)))
    write_text(path, items)
    return path


def sheet_tribes(cells_dir, set_pants):
    w, h = 360, 470
    cols = 5
    rows = math.ceil(len(TRIBES) / cols)
    out = canvas(w * cols + 80, h * rows + 120 * rows + 140)
    items = [("TRIBE PANTS COLOURS", out.shape[1] / 2, 86, 42, FONT_TITLE, INK)]
    for i, (name, hexcol) in enumerate(TRIBES):
        set_pants(name)
        p = render_cell(os.path.join(cells_dir, f"tribe_{name}.png"), 18, res=(w, h), scale=6.0, centre_z=2.65)
        r, c = divmod(i, cols)
        x, y = 40 + c * w, 130 + r * (h + 120)
        paste(out, load_px(p), x, y)
        sw = np.ones((26, 26, 4), np.float32)
        sw[..., :3] = [int(hexcol[k:k + 2], 16) / 255 for k in (1, 3, 5)]
        paste(out, sw, x + w // 2 - 13, y + h + 52)
        items.append((name.upper() + ("  (DEFAULT)" if i == 0 else ""), x + w / 2, y + h + 36, 22, FONT_TITLE, INK))
        items.append((hexcol, x + w / 2, y + h + 104, 17, FONT_BODY, (0.35, 0.3, 0.27)))
    set_pants(TRIBES[0][0])
    path = os.path.join(RENDER_DIR, "09_character_tribes.png")
    save_px(path, out)
    write_text(path, items)
    return path


def sheet_rig(cells_dir, rig):
    poses = [
        ("REST (R6 JOINTS)", {}),
        ("WALK", {"Right Arm": (-35, 0, 0), "Left Arm": (35, 0, 0), "Right Leg": (30, 0, 0), "Left Leg": (-30, 0, 0)}),
        ("WAVE", {"Left Arm": (0, 0, -150), "Head": (0, 14, 0)}),
        ("SWING", {"Right Arm": (-105, 0, 0), "Torso": (0, 15, 0), "Left Leg": (-15, 0, 0), "Right Leg": (12, 0, 0)}),
    ]
    w, h = 440, 600
    out = canvas(w * 4 + 80, h + 230)
    rig.show_in_front = True
    items = [("R6 RIG  —  PARTS POSE ON ROBLOX'S DEFAULT JOINTS", out.shape[1] / 2, 86, 38, FONT_TITLE, INK)]
    for i, (label, angles) in enumerate(poses):
        pose(rig, angles)
        p = render_cell(os.path.join(cells_dir, f"pose_{i}.png"), 22, res=(w, h))
        paste(out, load_px(p), 40 + i * w, 130)
        items.append((label, 40 + i * w + w / 2, 130 + h + 52, 24, FONT_TITLE, INK))
    pose(rig, {})
    items.append(("Neck · Left/Right Shoulder · Left/Right Hip · RootJoint  (standard Motor6D C0/C1)",
                  out.shape[1] / 2, 130 + h + 92, 19, FONT_BODY, (0.35, 0.3, 0.27)))
    path = os.path.join(RENDER_DIR, "09_character_rig.png")
    save_px(path, out)
    write_text(path, items)
    return path


def sheet_parts(cells_dir, parts, clothing):
    """Two exploded panels: the six R6 body parts, and the four clothing pieces."""
    # Pull-apart offsets by attach part. Everything moves up or out from the feet,
    # so nothing sinks below the floor.
    body_offsets = {
        "Head": (0, 0, 1.5), "Torso": (0, 0, 0.7), "Right Arm": (-0.8, 0, 0.7), "Left Arm": (0.8, 0, 0.7),
        "Right Leg": (-0.4, 0, 0), "Left Leg": (0.4, 0, 0),
    }
    # Clothing: the shirt lifts clear of the waist band; the leg pieces spread apart.
    cloth_offsets = {"Shirt": (0, 0, 1.2), "PantsWaist": (0, 0, 0),
                     "PantsRightLeg": (-0.4, 0, 0), "PantsLeftLeg": (0.4, 0, 0)}
    body = [parts[n] for n in PARTS] + [parts["Face"]]
    cloth = list(clothing.values())
    saved = {o: o.matrix_world.copy() for o in body + cloth}

    def explode(objs, offsets):
        for o in objs:
            key = o.name if o.name in offsets else "Head"
            o.matrix_world = Matrix.Translation(Vector(offsets[key])) @ saved[o]

    def show(objs):
        for o in body + cloth:
            o.hide_render = o not in objs

    w, h = 640, 760
    explode(body, body_offsets)
    show(body)
    left = render_cell(os.path.join(cells_dir, "parts_body.png"), 0, res=(w, h), scale=8.4, centre_z=3.4)
    for o in body:
        o.matrix_world = saved[o]
    # The clothing alone, pulled apart the same way (shirt and waist stay on the torso).
    explode(cloth, cloth_offsets)
    show(cloth)
    right = render_cell(os.path.join(cells_dir, "parts_cloth.png"), 18, res=(w, h), scale=8.4, centre_z=3.4)
    for o in body + cloth:
        o.matrix_world = saved[o]
        o.hide_render = False
    out = canvas(w * 2 + 80, h + 300)
    paste(out, load_px(left), 40, 130)
    paste(out, load_px(right), 40 + w, 130)
    path = os.path.join(RENDER_DIR, "09_character_parts.png")
    save_px(path, out)
    items = [("R6 PARTS AND CLOTHING PIECES", out.shape[1] / 2, 86, 40, FONT_TITLE, INK),
             ("BODY  (R6 PARTS)", 40 + w / 2, 130 + h + 46, 24, FONT_TITLE, INK),
             ("CLOTHING  (SEPARATE MESHES)", 40 + w + w / 2, 130 + h + 46, 24, FONT_TITLE, INK),
             ("Head 2x1x1 part (rounded 1.25 mesh)", 40 + w / 2, 130 + h + 86, 19, FONT_BODY, INK),
             ("Torso 2x2x1 · Arms 1x2x1 · Legs 1x2x1", 40 + w / 2, 130 + h + 116, 19, FONT_BODY, INK),
             ("Shirt → Torso · PantsWaist → Torso", 40 + w + w / 2, 130 + h + 86, 19, FONT_BODY, INK),
             ("PantsLeftLeg / PantsRightLeg → their legs", 40 + w + w / 2, 130 + h + 116, 19, FONT_BODY, INK)]
    write_text(path, items)
    return path


def sheet_textures(paths):
    tiles = [
        ("SHIRT COLOUR", paths["shirt_color"]), ("SHIRT NORMAL", paths["shirt_normal"]),
        ("SHIRT ROUGHNESS", paths["shirt_roughness"]), ("FACE DECAL", paths["face"]),
        ("PANTS NEUTRAL", paths["pants_color"]), ("PANTS NORMAL", paths["pants_normal"]),
        ("PANTS ROUGHNESS", paths["pants_roughness"]), ("PANTS · EARTH", paths["tribes"]["Earth"]),
    ]
    tribe_tiles = [(n.upper(), paths["tribes"][n]) for n, _ in TRIBES[1:]]
    size = 300
    cols = 4
    allt = tiles + tribe_tiles
    rows = math.ceil(len(allt) / cols)
    out = canvas(cols * (size + 40) + 40, rows * (size + 70) + 160)
    items = [("CHARACTER TEXTURES", out.shape[1] / 2, 86, 40, FONT_TITLE, INK)]
    for i, (label, p) in enumerate(allt):
        px = load_px(p)
        img_h, img_w = px.shape[:2]
        ys = (np.arange(size) * img_h / size).astype(int)
        xs = (np.arange(size) * img_w / size).astype(int)
        small = px[ys][:, xs]
        if label == "FACE DECAL":  # show the decal on skin, as it sits on the head
            skin = np.ones_like(small)
            skin[..., :3] = [int(SKIN[k:k + 2], 16) / 255 for k in (1, 3, 5)]
            a = small[..., 3:4]
            small = np.concatenate([small[..., :3] * a + skin[..., :3] * (1 - a), np.ones_like(a)], 2)
        r, c = divmod(i, cols)
        x, y = 40 + c * (size + 40), 130 + r * (size + 70)
        paste(out, small, x, y)
        items.append((label, x + size / 2, y + size + 36, 19, FONT_TITLE, INK))
    path = os.path.join(RENDER_DIR, "09_character_textures.png")
    save_px(path, out)
    write_text(path, items)
    return path


# ---------------------------------------------------------------------------
# Roblox export
# ---------------------------------------------------------------------------

C = Matrix(((1, 0, 0), (0, 0, 1), (0, -1, 0)))  # Blender -> Roblox/glTF axes


def to_rbx(v):
    return [round(v[0], 4), round(v[2], 4), round(-v[1], 4)]


def export_piece(obj, name, scene):
    me = obj.data.copy()
    me.transform(obj.matrix_world)
    lo = Vector([min(v.co[i] for v in me.vertices) for i in range(3)])
    hi = Vector([max(v.co[i] for v in me.vertices) for i in range(3)])
    centre = (lo + hi) / 2
    me.transform(Matrix.Translation(-centre))
    tmp = bpy.data.objects.new("export_" + name, me)
    scene.collection.objects.link(tmp)
    for o in bpy.context.view_layer.objects:
        o.select_set(o is tmp)
    bpy.context.view_layer.objects.active = tmp
    path = os.path.join(EXPORT_DIR, name.replace(" ", "") + ".glb")
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_yup=True,
                              export_apply=False, export_texcoords=True, export_normals=True,
                              export_materials="NONE", export_animations=False, export_skins=False,
                              export_morph=False, export_cameras=False, export_lights=False)
    bpy.data.objects.remove(tmp)
    dims = hi - lo
    return {"file": os.path.basename(path), "tris": sum(len(p.vertices) - 2 for p in me.polygons),
            "size": [round(dims.x, 4), round(dims.z, 4), round(dims.y, 4)], "centre": centre}


def export_roblox(parts, clothing, texture_paths):
    # Replace only what this export writes; asset_ids.json (upload records) stays.
    os.makedirs(EXPORT_DIR, exist_ok=True)
    for old in os.listdir(EXPORT_DIR):
        if old.endswith(".glb") or old == "manifest.json":
            os.remove(os.path.join(EXPORT_DIR, old))
    scene = bpy.context.scene
    manifest = {"version": 1, "rig": "R6", "units": "studs; Roblox axes (Y up, front -Z)",
                "textureDir": "art/character/textures",
                "note": ("Meshes are centred on their bounding box. Roblox's glTF import turns meshes "
                         "half a turn about Y (see scripts/roblox_lobby_map.py), so place each with "
                         "CFrame.Angles(0, math.pi, 0) after its offset."),
                "parts": {}, "clothing": {}, "motors": {}, "colors": {}, "textures": {}}
    for name in PARTS:
        info = export_piece(parts[name], name, scene)
        part_centre = Vector(PARTS[name][1])
        info["partSize"] = [2.0, 1.0, 1.0] if name == "Head" else to_rbx_size(PARTS[name][0])
        info["offset"] = to_rbx(info.pop("centre") - part_centre)
        manifest["parts"][name] = info
    for name, part in CLOTHING.items():
        info = export_piece(clothing[name], name, scene)
        info["part"] = part
        info["offset"] = to_rbx(info.pop("centre") - Vector(PARTS[part][1]))
        manifest["clothing"][name] = info
    for name, (p0, p1, c0, c1) in MOTORS.items():
        manifest["motors"][name] = {"part0": p0, "part1": p1, "c0": c0, "c1": c1}
    manifest["humanoidRootPart"] = {"size": [2, 2, 1], "transparency": 1}
    manifest["colors"] = {"skin": SKIN, "shirt": SHIRT, "pantsNeutral": PANTS_NEUTRAL,
                          "tribes": {n: h for n, h in TRIBES}}
    # Textures stay in art/character/textures (named relative to textureDir).
    for key, p in texture_paths.items():
        if key == "tribes":
            for n, tp in p.items():
                manifest["textures"]["pants_color_" + n.lower()] = os.path.basename(tp)
        else:
            manifest["textures"][key] = os.path.basename(p)
    with open(os.path.join(EXPORT_DIR, "manifest.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=1)
    return manifest


def to_rbx_size(size):
    return [size[0], size[2], size[1]]


# ---------------------------------------------------------------------------

def main():
    fk.reset_file()
    os.makedirs(TEX_DIR, exist_ok=True)
    os.makedirs(RENDER_DIR, exist_ok=True)
    scene = bpy.context.scene
    col = bpy.data.collections.new("Character")
    scene.collection.children.link(col)

    parts = {}
    for name, (size, centre) in PARTS.items():
        parts[name] = rounded_box(name, size, centre, ROUNDING.get(name, 0.12), col)
    face_plane = bpy.data.meshes.new("Face")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for loop in f.loops:
            loop[uv].uv = (loop.vert.co.x + 0.5, loop.vert.co.y + 0.5)
    bmesh.ops.rotate(bm, verts=bm.verts, matrix=Matrix.Rotation(math.radians(90), 3, "X"))
    bm.to_mesh(face_plane)
    bm.free()
    parts["Face"] = link(bpy.data.objects.new("Face", face_plane), col)
    parts["Face"].location = (0, -0.627, 4.5)
    parts["Face"].scale = (1.05, 1.0, 1.05)

    shirt, pants = build_clothing(col)
    clothing = {"Shirt": shirt}
    for o in pants:
        clothing[o.name] = o

    for o in list(clothing.values()) + [parts[n] for n in PARTS]:
        unwrap(o)

    # Bake: shirt alone; the pants pieces share one atlas.
    shirt_maps = bake_set([shirt], shader_material("ShirtBake", "shirt"), "shirt")
    pants_objs = [clothing["PantsWaist"], clothing["PantsRightLeg"], clothing["PantsLeftLeg"]]
    pants_maps = bake_set(pants_objs, shader_material("PantsBake", "pants"), "pants")
    tribes = tribe_variants(os.path.join(TEX_DIR, "pants_color.png"))
    face_img = face_texture(os.path.join(TEX_DIR, "face.png"))

    skin = skin_material()
    for name in PARTS:
        parts[name].data.materials.append(skin)
    parts["Face"].data.materials.append(face_material(face_img))
    shirt.data.materials.clear()
    shirt.data.materials.append(textured_material("Shirt", os.path.join(TEX_DIR, "shirt_color.png"),
                                                  os.path.join(TEX_DIR, "shirt_normal.png"),
                                                  os.path.join(TEX_DIR, "shirt_roughness.png")))
    pants_mats = {}
    for name, _ in TRIBES:
        pants_mats[name] = textured_material("Pants_" + name, tribes[name],
                                             os.path.join(TEX_DIR, "pants_normal.png"),
                                             os.path.join(TEX_DIR, "pants_roughness.png"))

    def set_pants(name):
        for o in pants_objs:
            o.data.materials.clear()
            o.data.materials.append(pants_mats[name])

    set_pants(TRIBES[0][0])
    rig = build_rig(col, parts, clothing)

    texture_paths = {
        "shirt_color": os.path.join(TEX_DIR, "shirt_color.png"),
        "shirt_normal": os.path.join(TEX_DIR, "shirt_normal.png"),
        "shirt_roughness": os.path.join(TEX_DIR, "shirt_roughness.png"),
        "pants_color": os.path.join(TEX_DIR, "pants_color.png"),
        "pants_normal": os.path.join(TEX_DIR, "pants_normal.png"),
        "pants_roughness": os.path.join(TEX_DIR, "pants_roughness.png"),
        "face": os.path.join(TEX_DIR, "face.png"),
        "tribes": tribes,
    }
    manifest = export_roblox(parts, clothing, texture_paths)

    fk.save(OUT_BLEND)

    studio()
    cells = os.path.join(RENDER_DIR, "09_character_cells")
    os.makedirs(cells, exist_ok=True)
    sheet_turnaround(cells)
    sheet_tribes(cells, set_pants)
    sheet_rig(cells, rig)
    sheet_parts(cells, parts, clothing)
    sheet_textures(texture_paths)
    tris = {n: v["tris"] for n, v in list(manifest["parts"].items()) + list(manifest["clothing"].items())}
    print("CHARACTER BUILT", json.dumps(tris))


main()
