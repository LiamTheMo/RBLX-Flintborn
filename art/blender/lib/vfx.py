"""VFX sockets: where an asset's effects live, and what they are in Roblox.

Meshes only carry the static look of an effect (an emissive flame shape, a glowing
glyph). The *live* effect, meaning flicker, sparks, smoke, light, mist, is
described by a VFX socket: an Empty parented to the asset at the emitter
position, named `VFX_<kind>` and carrying custom properties:

- `vfx_kind`   one of KINDS below
- `vfx_scale`  size multiplier (1.0 = tuned for the kind's typical asset)
- `roblox`     JSON: the ParticleEmitter(s) and PointLight to create in Studio,
               with textures named after the PNGs that sheet 08 renders into
               `art/vfx/textures/` (upload them, then swap in the asset ids)

Builders call `vfx.add(obj, kind, (x, y, z))` after `Asset.finish()`, with the
location in the asset's local studs. `vfx.realize(scene)` turns sockets into
Blender lights and lightweight particle stand-ins for preview renders;
`vfx.clear(scene)` removes them again.

Emitter values are in Roblox terms and Roblox axes (Y up): sizes, speeds and
accelerations in studs, rates in particles/second, angles in degrees. Two-value
lists are NumberRanges (min, max); longer `size`/`transparency`/`color` lists are
sequences with evenly spaced keypoints over the particle's life. Multiply Size,
Speed, Acceleration, shape and light Range by the socket's `vfx_scale`.
"""

import json
import math
import random
import zlib

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

# Colours are sRGB hex. Sizes and speeds are in studs. Rates are particles/second.
# Optional emitter keys: `flipbook` (FlipbookLayout), `acceleration` (Roblox XYZ),
# `drag`, `rotation` / `rot_speed` (degrees, NumberRanges), `orientation`
# ("flat" = VelocityPerpendicular, lies in the plane of the water), `shape`
# (size in studs of an invisible box Part the emitter sits in, Roblox XYZ; no
# shape = emit from the socket point via an Attachment).
FIRE = ["#FFFFFF", "#FFF4E0", "#FFD2A8"]  # the flipbook carries its own colours
KINDS = {
    "torch_fire": {
        "emitters": [
            {"name": "Flame", "texture": "fire_flipbook_4x4", "flipbook": "4x4", "color": FIRE,
             "size": [0.9, 1.2, 0.3], "transparency": [0.1, 0.15, 1.0], "lifetime": [0.4, 0.7], "rate": 18,
             "speed": [1.2, 2.0], "spread": 6, "light_emission": 1.0, "acceleration": [0, 1.5, 0],
             "rotation": [-8, 8]},
            {"name": "Embers", "texture": "ember_dot", "color": ["#FFC86A", "#FF6A1A"], "size": [0.3, 0.1],
             "transparency": [0, 1], "lifetime": [0.8, 1.6], "rate": 4, "speed": [2.5, 4.5], "spread": 25,
             "light_emission": 1.0, "drag": 1.2, "acceleration": [0, 1, 0]},
        ],
        "light": {"color": "#FF9A3C", "brightness": 1.6, "range": 14, "flicker": True},
    },
    "campfire": {
        "emitters": [
            {"name": "Flame", "texture": "fire_flipbook_4x4", "flipbook": "4x4", "color": FIRE,
             "size": [2.6, 3.4, 0.8], "transparency": [0.05, 0.15, 1.0], "lifetime": [0.5, 0.9], "rate": 30,
             "speed": [1.8, 3.0], "spread": 12, "light_emission": 1.0, "acceleration": [0, 2.5, 0],
             "rotation": [-10, 10], "shape": [2.5, 0.2, 2.5]},
            {"name": "Sparks", "texture": "spark_diamond", "color": ["#FFF2B0", "#FFB347"], "size": [0.45, 0.15],
             "transparency": [0, 1], "lifetime": [1.0, 2.2], "rate": 8, "speed": [5, 8], "spread": 30,
             "light_emission": 1.0, "drag": 1.4, "acceleration": [0, 1.5, 0]},
            {"name": "Smoke", "texture": "smoke_puff", "color": ["#6E6A66", "#9A9692"], "size": [1.5, 4.5],
             "transparency": [0.6, 1.0], "lifetime": [2.5, 4.0], "rate": 3, "speed": [2, 3], "spread": 10,
             "light_emission": 0.0, "rotation": [0, 360], "rot_speed": [-25, 25], "acceleration": [0.3, 0.3, 0]},
        ],
        "light": {"color": "#FF8C2A", "brightness": 2.5, "range": 28, "flicker": True},
    },
    "brazier_fire": {
        "emitters": [
            {"name": "Flame", "texture": "fire_flipbook_4x4", "flipbook": "4x4", "color": FIRE,
             "size": [1.4, 1.9, 0.4], "transparency": [0.05, 0.15, 1.0], "lifetime": [0.45, 0.8], "rate": 22,
             "speed": [1.5, 2.6], "spread": 10, "light_emission": 1.0, "acceleration": [0, 2.0, 0],
             "rotation": [-8, 8]},
            {"name": "Embers", "texture": "ember_dot", "color": ["#FFC86A", "#FF6A1A"], "size": [0.3, 0.1],
             "transparency": [0, 1], "lifetime": [1, 2], "rate": 5, "speed": [3, 5], "spread": 25,
             "light_emission": 1.0, "drag": 1.2, "acceleration": [0, 1, 0]},
        ],
        "light": {"color": "#FF9A3C", "brightness": 2.0, "range": 18, "flicker": True},
    },
    "forge_fire": {
        "emitters": [
            {"name": "Flame", "texture": "fire_flipbook_4x4", "flipbook": "4x4", "color": ["#FFFFFF", "#FFF0D8", "#FFC090"],
             "size": [2.2, 3.0, 0.6], "transparency": [0.05, 0.15, 1.0], "lifetime": [0.5, 0.9], "rate": 28,
             "speed": [1.2, 2.2], "spread": 15, "light_emission": 1.0, "rotation": [-10, 10],
             "shape": [3.0, 0.2, 1.5]},
            {"name": "Sparks", "texture": "spark_diamond", "color": ["#FFF2B0", "#FFB347"], "size": [0.4, 0.12],
             "transparency": [0, 1], "lifetime": [0.8, 1.6], "rate": 6, "speed": [4, 7], "spread": 35,
             "light_emission": 1.0, "drag": 1.6, "acceleration": [0, 1.5, 0]},
        ],
        "light": {"color": "#FF7A22", "brightness": 3.0, "range": 30, "flicker": True},
    },
    "chimney_smoke": {
        "emitters": [
            {"name": "Smoke", "texture": "smoke_puff", "color": ["#5E5A57", "#A8A4A0"], "size": [1.2, 5.0],
             "transparency": [0.45, 1.0], "lifetime": [3, 5], "rate": 4, "speed": [2.5, 4], "spread": 8,
             "light_emission": 0.0, "acceleration": [0.6, 0.4, 0], "drag": 0.3, "rotation": [0, 360],
             "rot_speed": [-20, 20]},
        ],
        "light": None,
    },
    "embers": {
        "emitters": [
            {"name": "Embers", "texture": "ember_dot", "color": ["#FFC86A", "#FF6A1A"], "size": [0.3, 0.1],
             "transparency": [0, 1], "lifetime": [1.2, 2.4], "rate": 6, "speed": [1.5, 3], "spread": 40,
             "light_emission": 1.0, "drag": 0.8, "acceleration": [0, 0.8, 0]},
        ],
        "light": None,
    },
    "heat_glow": {  # furnace slits, lava seams, forge mouth
        "emitters": [
            {"name": "Heat", "texture": "glow_soft", "color": ["#FF8C2A", "#FF5A1A"], "size": [1.0, 1.4],
             "transparency": [0.5, 1.0], "lifetime": [0.8, 1.2], "rate": 3, "speed": [0.3, 0.6], "spread": 5,
             "light_emission": 1.0},
        ],
        "light": {"color": "#FF7A22", "brightness": 1.2, "range": 10, "flicker": True},
    },
    "glyph_glow": {  # forge emblem and carved glyphs (orange)
        "emitters": [
            {"name": "Glimmer", "texture": "glow_soft", "color": ["#FFB347", "#FF8C2A"], "size": [1.2, 1.6],
             "transparency": [0.6, 1.0], "lifetime": [1.5, 2.5], "rate": 1.5, "speed": [0, 0.2], "spread": 0,
             "light_emission": 1.0},
        ],
        "light": {"color": "#FF8C2A", "brightness": 0.9, "range": 10, "flicker": False, "pulse": True},
    },
    "rune_glow": {  # pale blue engraved rune stones
        "emitters": [
            {"name": "Motes", "texture": "rune_mote", "color": ["#FFFFFF", "#CDEFFA"], "size": [0.5, 0.15],
             "transparency": [0.2, 1.0], "lifetime": [2, 3.5], "rate": 2, "speed": [0.3, 0.8], "spread": 30,
             "light_emission": 1.0, "rotation": [0, 90], "shape": [3.0, 0.2, 2.0]},
        ],
        "light": {"color": "#A8E2F4", "brightness": 0.6, "range": 8, "flicker": False, "pulse": True},
    },
    "waterfall_mist": {
        "emitters": [
            {"name": "Mist", "texture": "mist_soft", "color": ["#FFFFFF", "#DDF2FA"], "size": [3, 7],
             "transparency": [0.55, 1.0], "lifetime": [1.5, 2.5], "rate": 10, "speed": [1.5, 3], "spread": 70,
             "light_emission": 0.2, "drag": 1.0, "rotation": [0, 360], "rot_speed": [-15, 15],
             "shape": [5.0, 0.5, 2.0]},
            {"name": "Splash", "texture": "splash_droplets", "color": ["#FFFFFF", "#CBEAF6"], "size": [1.0, 2.0],
             "transparency": [0.1, 1.0], "lifetime": [0.5, 0.9], "rate": 14, "speed": [5, 8], "spread": 50,
             "light_emission": 0.1, "acceleration": [0, -20, 0], "rotation": [-30, 30],
             "shape": [4.0, 0.2, 1.5]},
        ],
        "light": None,
    },
    "water_foam": {  # shore lines and river riffles
        "emitters": [
            {"name": "Foam", "texture": "foam_patch", "color": ["#FFFFFF", "#E3F4FA"], "size": [2.0, 3.0],
             "transparency": [0.2, 1.0], "lifetime": [2.0, 3.0], "rate": 4, "speed": [0.05, 0.12], "spread": 0,
             "light_emission": 0.0, "orientation": "flat", "rotation": [0, 360], "rot_speed": [-12, 12],
             "shape": [6.0, 0.1, 1.5]},
        ],
        "light": None,
    },
    "dust": {  # gate threshold, path ends: very sparse floating motes
        "emitters": [
            {"name": "Dust", "texture": "dust_mote", "color": ["#F3E1B8", "#E2C890"], "size": [0.3, 0.12],
             "transparency": [0.4, 1.0], "lifetime": [3, 5], "rate": 1.5, "speed": [0.1, 0.3], "spread": 180,
             "light_emission": 0.3, "shape": [8.0, 2.0, 4.0]},
        ],
        "light": None,
    },
}

# The PNGs sheet 08 renders into art/vfx/textures/<name>.png. `tint` = white or
# greyscale, so the emitter Color sequence sets the final colour.
TEXTURES = {
    "fire_flipbook_4x4": {"size": 1024, "tint": False, "flipbook": "4x4",
                          "about": "16-frame seamless loop of a faceted flame: pale yellow core, orange body, red-orange tips"},
    "smoke_puff": {"size": 256, "tint": True, "about": "soft faceted puff, white-grey"},
    "spark_diamond": {"size": 256, "tint": True, "about": "bright 4-point diamond spark with a faint halo"},
    "ember_dot": {"size": 128, "tint": True, "about": "small glowing faceted dot"},
    "glow_soft": {"size": 256, "tint": True, "about": "radial soft glow"},
    "rune_mote": {"size": 256, "tint": False, "about": "pale-blue rune glimmer: lozenge glyph and star"},
    "mist_soft": {"size": 512, "tint": True, "about": "large soft white mist blob"},
    "splash_droplets": {"size": 256, "tint": True, "about": "fan of faceted water droplets"},
    "foam_patch": {"size": 512, "tint": True, "about": "flat white foam swirl, seen from above"},
    "dust_mote": {"size": 128, "tint": True, "about": "tiny soft mote"},
}

# Which assets carry which sockets, as built into the sheet .blend files
# (sheet, asset, [(kind, where, vfx_scale)]); one entry per socket.
ASSET_SOCKETS = [
    ("01_buildings", "AncestralForge", [
        ("brazier_fire", "chimney-top flame", 1.0), ("chimney_smoke", "chimney top", 1.0),
        ("glyph_glow", "emblem", 1.0), ("heat_glow", "furnace arch", 1.0),
        ("heat_glow", "lava seam", 0.6)]),
    ("01_buildings", "DeployGate", [("torch_fire", "left gate torch", 1.0), ("torch_fire", "right gate torch", 1.0),
                                    ("dust", "threshold", 1.0)]),
    ("02_fences_towers", "PalisadeTorchPost", [("torch_fire", "just above the cup", 1.0)]),
    ("03_furnishings", "SmeltingFurnace", [("forge_fire", "fire arch", 1.0), ("chimney_smoke", "chimney top", 1.0),
                                           ("heat_glow", "chimney slits", 1.0)]),
    ("06_rocks_runes_camp", "Campfire", [("campfire", "centre of the log pile", 1.0)]),
    ("06_rocks_runes_camp", "TorchPost", [("torch_fire", "torch head", 1.0)]),
    ("06_rocks_runes_camp", "StoneBrazier", [("brazier_fire", "bowl", 1.0)]),
    ("06_rocks_runes_camp", "LargeRuneStone", [("rune_glow", "glyph", 1.0)]),
    ("06_rocks_runes_camp", "ElongatedRuneStone", [("rune_glow", "glyph", 1.0)]),
    ("06_rocks_runes_camp", "TriangularRuneStone", [("rune_glow", "glyph", 1.0)]),
    ("07_terrain_kit", "CaveEntrance", [("torch_fire", "left cave-mouth torch", 1.0),
                                        ("torch_fire", "right cave-mouth torch", 1.0),
                                        ("heat_glow", "cave interior", 1.5)]),
    ("07_terrain_kit", "Riverbank", [("water_foam", "shore line", 1.0)] * 3),
    ("07_terrain_kit", "RockyLakeshore", [("water_foam", "shore line", 1.0)] * 3),
    ("07_terrain_kit", "WaterfallCliff", [("waterfall_mist", "where the fall hits the pool", 1.4),
                                          ("water_foam", "pool rim", 1.0), ("water_foam", "pool rim", 1.0)]),
]


def add(obj, kind, loc, scale=1.0, name=None, **overrides):
    """Attach a VFX socket to `obj` at local `loc` (studs). Returns the Empty."""
    if kind not in KINDS:
        raise ValueError(f"unknown VFX kind {kind!r}; use one of {sorted(KINDS)}")
    spec = json.loads(json.dumps(KINDS[kind]))
    spec.update(overrides)
    empty = bpy.data.objects.new(name or f"VFX_{kind}", None)
    empty.empty_display_type = "SPHERE"
    empty.empty_display_size = 0.4 * scale
    for coll in obj.users_collection:
        coll.objects.link(empty)
    empty.parent = obj
    empty.location = loc
    empty["vfx_kind"] = kind
    empty["vfx_scale"] = float(scale)
    empty["roblox"] = json.dumps(spec)
    return empty


def sockets(obj):
    """All VFX sockets under an asset object."""
    return [c for c in obj.children if c.get("vfx_kind")]


def catalog():
    """Everything Studio needs, as plain JSON-able data (written to art/vfx/vfx_catalog.json)."""
    return {
        "version": 1,
        "units": "studs; Roblox axes (Y up); colours sRGB hex",
        "notes": [
            "Two-value lists are NumberRanges (min, max); size/transparency/color lists of any other "
            "length are sequences with evenly spaced keypoints over the particle life.",
            "Multiply Size, Speed, Acceleration, shape and light Range by the socket's vfx_scale.",
            "Texture names refer to art/vfx/textures/<name>.png; upload them and swap in rbxassetid://<id>.",
        ],
        "textures": TEXTURES,
        "kinds": KINDS,
        "assets": [{"sheet": s, "asset": a, "sockets": [{"kind": k, "where": w, "vfx_scale": sc}
                                                        for k, w, sc in socks]}
                   for s, a, socks in ASSET_SOCKETS],
    }


# ---------------------------------------------------------------------------
# Blender preview: lights + particle stand-ins
# ---------------------------------------------------------------------------

PREVIEW_PREFIX = "VFXPreview_"
PREVIEW_COLLECTION = "VFX Preview"
LIGHT_WATTS = 1.4       # Blender watts per (Roblox brightness x range^2 studs)
LIGHT_SHADOWS = False   # shadowless: cheap, and not blocked by the asset's own flame mesh
MAX_PER_EMITTER = 12

# How each texture looks as a 3D stand-in: (look, shape)
_STAND_IN = {
    "spark_diamond": ("glow", "diamond"),
    "ember_dot": ("glow", "ember"),
    "glow_soft": ("haze", "blob"),
    "rune_mote": ("glow", "mote"),
    "dust_mote": ("glow", "mote"),
    "smoke_puff": ("soft", "puff"),
    "mist_soft": ("mist", "mound"),
    "splash_droplets": ("solid", "droplets"),
    "foam_patch": ("solid", "foam"),
    "fire_flipbook_4x4": (None, None),  # the asset mesh already carries the flame
}


def _lin(h):
    h = h.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return out


def _seq(vals, f):
    """Evaluate an evenly spaced sequence (numbers or hex colours) at f in [0, 1]."""
    if isinstance(vals[0], str):
        vals = [_lin(v) for v in vals]
    else:
        vals = [[v] for v in vals]
    if len(vals) == 1:
        return vals[0]
    x = min(max(f, 0.0), 1.0) * (len(vals) - 1)
    i = min(int(x), len(vals) - 2)
    t = x - i
    return [a + (b - a) * t for a, b in zip(vals[i], vals[i + 1])]


def _rb(v):
    """Roblox (x, y up, z) -> Blender (x, y, z up)."""
    return Vector((v[0], -v[2], v[1]))


def _scene_sockets(scene, objects):
    found = []
    pool = scene.objects if objects is None else objects
    for o in pool:
        if o.get("vfx_kind"):
            found.append(o)
        if objects is not None:
            found += [c for c in o.children_recursive if c.get("vfx_kind")]
    seen, out = set(), []
    for s in found:
        if s.name not in seen:
            seen.add(s.name)
            out.append(s)
    return out


def _preview_collection(scene):
    coll = bpy.data.collections.get(PREVIEW_COLLECTION)
    if coll is None:
        coll = bpy.data.collections.new(PREVIEW_COLLECTION)
    if coll.name not in scene.collection.children:
        scene.collection.children.link(coll)
    return coll


def _remove_objects(objs):
    for o in objs:
        data = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if data is not None and data.users == 0:
            if isinstance(data, bpy.types.Mesh):
                bpy.data.meshes.remove(data)
            elif isinstance(data, bpy.types.Light):
                bpy.data.lights.remove(data)


def clear(scene=None, socket_names=None):
    """Remove VFX preview objects (all of them, or only those of `socket_names`)."""
    scene = scene or bpy.context.scene
    doomed = [o for o in bpy.data.objects if o.name.startswith(PREVIEW_PREFIX)
              and (socket_names is None or o.get("vfx_socket") in socket_names)
              and (scene is None or o.name in scene.objects or not o.users_scene)]
    _remove_objects(doomed)
    coll = bpy.data.collections.get(PREVIEW_COLLECTION)
    if coll is not None and not coll.objects and socket_names is None:
        bpy.data.collections.remove(coll)


def _material(look):
    name = f"{PREVIEW_PREFIX}mat_{look}"
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "VFXCol"
    attr.attribute_type = "GEOMETRY"
    alpha = attr.outputs["Alpha"]
    if look in ("haze", "soft", "mist"):  # soft facet edges: fade faces that turn away
        lw = nt.nodes.new("ShaderNodeLayerWeight")
        lw.inputs["Blend"].default_value = 0.5
        inv = nt.nodes.new("ShaderNodeMath")
        inv.operation = "SUBTRACT"
        inv.inputs[0].default_value = 1.0
        nt.links.new(lw.outputs["Facing"], inv.inputs[1])
        pw = nt.nodes.new("ShaderNodeMath")
        pw.operation = "POWER"
        nt.links.new(inv.outputs[0], pw.inputs[0])
        pw.inputs[1].default_value = {"haze": 2.0, "soft": 0.8, "mist": 0.7}[look]
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        nt.links.new(pw.outputs[0], mul.inputs[0])
        nt.links.new(attr.outputs["Alpha"], mul.inputs[1])
        alpha = mul.outputs[0]
    mix = nt.nodes.new("ShaderNodeMixShader")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    if look in ("glow", "haze"):
        sh = nt.nodes.new("ShaderNodeEmission")
        sh.inputs["Strength"].default_value = 2.2 if look == "glow" else 1.6
        nt.links.new(attr.outputs["Color"], sh.inputs["Color"])
    else:
        sh = nt.nodes.new("ShaderNodeBsdfPrincipled")
        nt.links.new(attr.outputs["Color"], sh.inputs["Base Color"])
        nt.links.new(attr.outputs["Color"], sh.inputs["Emission Color"])
        sh.inputs["Roughness"].default_value = {"soft": 1.0, "mist": 0.9, "solid": 0.35}[look]
        sh.inputs["Emission Strength"].default_value = {"soft": 0.05, "mist": 0.5, "solid": 0.3}[look]
    nt.links.new(alpha, mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(sh.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    # blended: noise-free soft edges in the viewport and in renders
    for attr_name, val in (("surface_render_method", "BLENDED"), ("use_backface_culling", True),
                           ("use_transparency_overlap", look != "solid")):
        if hasattr(mat, attr_name):
            setattr(mat, attr_name, val)
    return mat


def _shape(bm, shape, size, rng, vel):
    """Add one stand-in particle of `shape` at the origin; returns its verts."""
    if shape in ("diamond", "mote"):
        rx, rz = (0.17, 0.45) if shape == "diamond" else (0.3, 0.42)
        pts = [(rx, 0, 0), (-rx, 0, 0), (0, rx, 0), (0, -rx, 0), (0, 0, rz), (0, 0, -rz)]
        vs = [bm.verts.new(Vector(p) * size) for p in pts]
        for a, b in ((0, 2), (2, 1), (1, 3), (3, 0)):
            bm.faces.new((vs[a], vs[b], vs[4]))
            bm.faces.new((vs[b], vs[a], vs[5]))
        rot = Euler((rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), rng.uniform(0, math.pi)))
        bmesh.ops.rotate(bm, verts=vs, cent=(0, 0, 0), matrix=rot.to_matrix())
        return vs
    if shape in ("ember", "blob", "puff", "mound"):
        sub = 0 if shape == "ember" else 1
        r = {"ember": 0.3, "blob": 0.38, "puff": 0.4, "mound": 0.42}[shape] * size
        vs = bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)["verts"]
        sq = (1.0, 1.0, 0.62 if shape == "mound" else 1.0)
        for v in vs:
            j = 1.0 + (rng.uniform(-0.12, 0.12) if shape in ("puff", "mound") else 0.0)
            v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2])) * r * j
        bmesh.ops.rotate(bm, verts=vs, cent=(0, 0, 0),
                         matrix=Euler((0, 0, rng.uniform(0, math.pi))).to_matrix())
        return vs
    if shape == "droplets":
        out = []
        up = vel.normalized() if vel.length > 1e-4 else Vector((0, 0, 1))
        for _ in range(3):
            r = size * rng.uniform(0.08, 0.13)
            vs = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)["verts"]
            for v in vs:  # teardrop: stretch the trailing half
                if v.co.z < 0:
                    v.co.z *= 2.2
            q = up.to_track_quat("Z", "Y").to_matrix()
            bmesh.ops.rotate(bm, verts=vs, cent=(0, 0, 0), matrix=q)
            off = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * size * 0.3
            bmesh.ops.translate(bm, verts=vs, vec=off)
            out += vs
        return out
    if shape == "foam":  # two flat swirl crescents, like the foam_patch texture
        out = []
        a0 = rng.uniform(0, 2 * math.pi)
        for R, span, w in ((0.36, 4.0, 0.11), (0.2, 3.2, 0.08)):
            n = 9
            outer, inner = [], []
            for i in range(n + 1):
                t = i / n
                a = a0 + span * t
                ww = w * math.sin(math.pi * t) ** 0.6 + 0.004
                rr = R * (1 + 0.08 * math.sin(t * 9 + a0))
                d = Vector((math.cos(a), math.sin(a), 0))
                outer.append(bm.verts.new(d * (rr + ww) * size + Vector((0, 0, 0.015 * size))))
                inner.append(bm.verts.new(d * (rr - ww) * size))
            for i in range(n):
                bm.faces.new((inner[i], outer[i], outer[i + 1], inner[i + 1]))
            out += outer + inner
            a0 += math.pi * 0.9
        return out
    raise ValueError(shape)


def _snapshot(em, scale, rng):
    """Positions/velocities/ages of a still frame of this emitter (Blender socket space)."""
    life = em["lifetime"]
    n = int(round(em["rate"] * (life[0] + life[1]) / 2 * 0.7))
    n = max(3, min(MAX_PER_EMITTER, n))
    spread = math.radians(em.get("spread", 0))
    acc = _rb(em.get("acceleration", (0, 0, 0))) * scale
    drag = em.get("drag", 0.0)
    shape = em.get("shape")
    out = []
    for k in range(n):
        L = rng.uniform(*life)
        f0 = 0.15 if em["texture"] == "smoke_puff" else 0.0  # fresh puffs hide in the flame
        f = f0 + (k + rng.random()) / n * (0.9 - f0)
        age = L * f
        ax, ay = rng.uniform(-spread, spread), rng.uniform(-spread, spread)
        d = Euler((ax, ay, 0)).to_matrix() @ Vector((0, 0, 1))
        v = d * rng.uniform(*em["speed"]) * scale
        p = Vector((0, 0, 0))
        if shape:
            p = Vector((rng.uniform(-0.5, 0.5) * shape[0], rng.uniform(-0.5, 0.5) * shape[2],
                        rng.uniform(-0.5, 0.5) * shape[1])) * scale
        steps = 24
        dt = age / steps
        for _ in range(steps):
            v = v + acc * dt
            if drag:
                v = v * math.exp(-drag * dt)
            p = p + v * dt
        out.append((p, v, f))
    return out


def _flicker(light_data, base, spec, seed):
    """Animate energy with a driver (expression `frame`, so no Python auto-run is
    needed) whose F-curve holds a constant generator plus a noise or sine modifier."""
    if not (spec.get("flicker") or spec.get("pulse")):
        return
    light_data.driver_remove("energy")
    fc = light_data.driver_add("energy")
    fc.driver.type = "SCRIPTED"
    fc.driver.expression = "frame"
    for m in list(fc.modifiers):
        fc.modifiers.remove(m)
    gen = fc.modifiers.new("GENERATOR")
    gen.mode = "POLYNOMIAL"
    gen.poly_order = 1
    gen.coefficients[0] = base
    gen.coefficients[1] = 0.0
    if spec.get("flicker"):
        nz = fc.modifiers.new("NOISE")
        nz.blend_type = "REPLACE"  # centred: base + (noise - 0.5) * strength
        nz.scale = 3.0
        nz.strength = base * 1.1
        nz.phase = seed % 97
        nz.offset = 0.0
        if hasattr(nz, "depth"):
            nz.depth = 1
    else:
        fn = fc.modifiers.new("FNGENERATOR")
        fn.function_type = "SIN"
        fn.amplitude = base * 0.25
        fn.phase_multiplier = 0.12
        fn.phase_offset = seed % 7
        fn.use_additive = True


def realize(scene=None, objects=None, particles=True):
    """Turn VFX sockets into Blender preview effects.

    Each socket gets a point light (if its kind has one: colour, energy from
    brightness x range^2, flicker/pulse driver) and, with `particles`, one merged
    stand-in mesh per emitter: a still frame of that emitter (sparks, embers,
    smoke puffs, mist mounds, droplets, foam patches, motes) simulated from its
    speed, spread, drag, acceleration, size and transparency. `objects` limits it
    to those assets/sockets (default: every socket in the scene). Re-running
    replaces the previous `VFXPreview_*` objects; all live in the `VFX Preview`
    collection. Returns the created objects.
    """
    scene = scene or bpy.context.scene
    socks = _scene_sockets(scene, objects)
    clear(scene, None if objects is None else {s.name for s in socks})
    coll = _preview_collection(scene)
    made = []
    for s in socks:
        try:
            spec = json.loads(s.get("roblox", "{}"))
        except ValueError:
            spec = {}
        if not spec:
            spec = KINDS.get(s["vfx_kind"], {})
        scale = float(s.get("vfx_scale", 1.0))
        seed = zlib.crc32(s.name.encode()) ^ zlib.crc32((s.parent.name if s.parent else "").encode())
        rng = random.Random(seed)
        light = spec.get("light")
        if light:
            ld = bpy.data.lights.new(f"{PREVIEW_PREFIX}{s.name}_Light", "POINT")
            ld.color = _lin(light["color"])
            rng_studs = light["range"] * scale
            base = LIGHT_WATTS * light["brightness"] * rng_studs ** 2
            ld.energy = base
            ld["vfx_base_energy"] = base
            ld.shadow_soft_size = 0.3 * scale
            ld.use_shadow = LIGHT_SHADOWS
            if hasattr(ld, "use_custom_distance"):
                ld.use_custom_distance = True
                ld.cutoff_distance = rng_studs * 1.5
            _flicker(ld, base, light, seed)
            lo = bpy.data.objects.new(f"{PREVIEW_PREFIX}{s.name}_Light", ld)
            lo.location = (0, 0, 0.25 * scale)
            made.append(lo)
        if particles:
            for em in spec.get("emitters", []):
                look, shape = _STAND_IN.get(em["texture"], (None, None))
                if look is None:
                    continue
                bm = bmesh.new()
                col = bm.loops.layers.float_color.new("VFXCol")
                for p, v, f in _snapshot(em, scale, rng):
                    size = _seq(em["size"], f)[0] * scale
                    a = 1.0 - _seq(em["transparency"], f)[0]
                    if look in ("soft", "mist", "haze"):  # soft edges eat alpha; compensate
                        a = min(1.0, a * (2.2 if look == "mist" else 1.6))
                    c = _seq(em["color"], f)
                    vs = _shape(bm, shape, size, rng, v)
                    if em.get("orientation") == "flat":
                        p = Vector((p.x, p.y, 0.03))
                    bmesh.ops.translate(bm, verts=vs, vec=p)
                    faces = set()
                    for vv in vs:
                        faces.update(vv.link_faces)
                    for fc in faces:
                        fc.smooth = False
                        sh = rng.uniform(0.92, 1.06)
                        for lp in fc.loops:
                            lp[col] = (c[0] * sh, c[1] * sh, c[2] * sh, a)
                me = bpy.data.meshes.new(f"{PREVIEW_PREFIX}{s.name}_{em['name']}")
                bm.to_mesh(me)
                bm.free()
                me.materials.append(_material(look))
                mo = bpy.data.objects.new(me.name, me)
                if hasattr(mo, "visible_shadow"):
                    mo.visible_shadow = False
                made.append(mo)
        for o in made:
            if o.parent is None and o.get("vfx_socket") is None:
                o["vfx_socket"] = s.name
                coll.objects.link(o)
                o.parent = s
    return made
