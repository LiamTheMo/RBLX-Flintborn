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

Lights: `light` is one PointLight at the socket, keys color, brightness, range,
flicker / pulse (animated in game), and optional `shadows` (PointLight.Shadows,
default false; the preview honours it too).

Beams. A kind may also have `beams`: Roblox Beams running from the socket
(Attachment0) to an END point (Attachment1), for falling water, flowing streaks
and other ribbons. Beam kinds need the end point:

    vfx.add(obj, "waterfall_curtain", (0, -2, 20), end=(0, -3, 1), width=8)

`end` is in the same asset-local Blender studs as `loc`. The socket stores it as
`vfx_end` (Blender local) and gets a child Empty `<socket>_End` there; the
`roblox` JSON gets `end` (Roblox axes, relative to the socket), `axis` and
`normal` (Roblox unit vectors: set both Attachments so their Axis / RightVector
is `axis`, the direction CurveSize0/1 bend along, and their SecondaryAxis /
UpVector is `normal`, the face direction of a beam with FaceCamera false). By
default `axis` is the start->end direction and `normal` faces up for flat beams
(water_flow) or toward the asset front (Blender -Y) for steep ones (falls);
`normal=` / `axis=` override them (Blender local). `width=` sets the first
beam's Width0 and scales the others (and any emitter with `shape_follows_width`)
to match. Beam keys: name, texture, color / transparency (sequences along the
beam from start to end), width0, width1, texture_speed (studs/s, positive scrolls
from start to end), texture_length (studs per tile), texture_mode
(Wrap/Stretch/Static), light_emission, light_influence, segments, face_camera,
and optional curve0 / curve1 (CurveSize0/1). The texture's horizontal axis (u)
runs along the beam, its vertical axis (v) across the width. Multiply Width0/1
and TextureLength by `vfx_scale`.
"""

import json
import math
import os
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
    # -- falling and flowing water, vapour. Beam kinds need vfx.add(..., end=(x, y, z)).
    "waterfall_curtain": {  # socket on the top lip, end where the fall meets the pool
        "emitters": [
            {"name": "Spray", "texture": "splash_droplets", "color": ["#FFFFFF", "#D8F1FA"], "size": [0.7, 1.5],
             "transparency": [0.35, 1.0], "lifetime": [0.4, 0.8], "rate": 8, "speed": [1.0, 2.5], "spread": 40,
             "light_emission": 0.15, "acceleration": [0, -25, 0], "rotation": [-30, 30],
             "shape": [7.0, 0.3, 0.5], "shape_follows_width": 0.9},
        ],
        "beams": [
            # the body of the fall: bold streaks scrolling down
            {"name": "Fall", "texture": "waterfall_streaks", "color": ["#FFFFFF", "#D4F1FB"],
             "transparency": [0.2, 0.15, 0.3], "width0": 8.0, "width1": 9.0, "texture_speed": 15.0,
             "texture_length": 10.0, "texture_mode": "Wrap", "light_emission": 0.25, "light_influence": 0.7,
             "segments": 12, "face_camera": False},
            # a fainter, faster sheen layer in front: two speeds read as depth
            {"name": "Sheen", "texture": "waterfall_streaks", "color": ["#FFFFFF", "#E8F8FD"],
             "transparency": [0.6, 0.5, 0.7], "width0": 6.8, "width1": 7.8, "texture_speed": 22.0,
             "texture_length": 6.0, "texture_mode": "Wrap", "light_emission": 0.35, "light_influence": 0.6,
             "segments": 12, "face_camera": False},
        ],
        "light": None,
    },
    "water_flow": {  # flat streaks on a river or stream surface; start -> end = the flow direction
        "emitters": [],
        "beams": [
            {"name": "Streaks", "texture": "water_streaks", "color": ["#FFFFFF", "#E6F7FC"],
             "transparency": [0.92, 0.72, 0.72, 0.92], "width0": 6.0, "width1": 6.0, "texture_speed": 4.0,
             "texture_length": 8.0, "texture_mode": "Wrap", "light_emission": 0.1, "light_influence": 0.8,
             "segments": 4, "face_camera": False},
        ],
        "light": None,
    },
    "vapour": {  # soft white rising steam / water-spray haze (not the grey chimney_smoke)
        "emitters": [
            {"name": "Vapour", "texture": "mist_soft", "color": ["#FFFFFF", "#EEF8FB"], "size": [3.0, 9.0],
             "transparency": [0.85, 0.72, 1.0], "lifetime": [4, 7], "rate": 3, "speed": [0.8, 1.6], "spread": 20,
             "light_emission": 0.15, "drag": 0.4, "acceleration": [0.2, 0.6, 0], "rotation": [0, 360],
             "rot_speed": [-10, 10], "shape": [3.0, 0.5, 3.0]},
            {"name": "Wisps", "texture": "smoke_puff", "color": ["#FFFFFF", "#F4FAFC"], "size": [1.5, 4.0],
             "transparency": [0.8, 1.0], "lifetime": [2.5, 4.0], "rate": 2, "speed": [1.5, 2.5], "spread": 15,
             "light_emission": 0.1, "drag": 0.3, "acceleration": [0.1, 0.4, 0], "rotation": [0, 360],
             "rot_speed": [-15, 15]},
        ],
        "light": None,
    },
    # -- world kit: harvesting. `burst` emitters have rate 0 and fire
    # ParticleEmitter:Emit(burst) when the socket's `trigger` event happens
    # ("hit" = each tool strike, "deplete" = the node empties). Override `color`
    # per material, e.g. vfx.add(obj, "harvest_hit", loc, color=["#E2713A", "#B8542A"]).
    "harvest_hit": {
        "trigger": "hit",
        "emitters": [
            {"name": "Chips", "texture": "rock_chip", "color": ["#B9B1AB", "#8F8B8F"], "size": [0.45, 0.25],
             "transparency": [0, 0, 1], "lifetime": [0.5, 0.9], "rate": 0, "burst": 8, "speed": [7, 12],
             "spread": 55, "light_emission": 0.0, "acceleration": [0, -35, 0], "rotation": [0, 360],
             "rot_speed": [-360, 360]},
            {"name": "Dust", "texture": "smoke_puff", "color": ["#CFC6BE", "#B3AAA2"], "size": [0.8, 2.2],
             "transparency": [0.45, 1.0], "lifetime": [0.6, 1.1], "rate": 0, "burst": 4, "speed": [1.5, 3],
             "spread": 70, "light_emission": 0.0, "drag": 3.0, "rotation": [0, 360], "rot_speed": [-40, 40]},
        ],
        "light": None,
    },
    "harvest_deplete": {
        "trigger": "deplete",
        "emitters": [
            {"name": "Chips", "texture": "rock_chip", "color": ["#B9B1AB", "#8F8B8F"], "size": [0.7, 0.35],
             "transparency": [0, 0, 1], "lifetime": [0.7, 1.2], "rate": 0, "burst": 18, "speed": [8, 15],
             "spread": 80, "light_emission": 0.0, "acceleration": [0, -35, 0], "rotation": [0, 360],
             "rot_speed": [-360, 360], "shape": [3.0, 1.0, 3.0]},
            {"name": "Dust", "texture": "smoke_puff", "color": ["#D6CEC6", "#B3AAA2"], "size": [2.0, 5.0],
             "transparency": [0.35, 1.0], "lifetime": [1.0, 1.8], "rate": 0, "burst": 10, "speed": [2, 4],
             "spread": 90, "light_emission": 0.0, "drag": 2.5, "rotation": [0, 360], "rot_speed": [-30, 30],
             "shape": [3.0, 0.5, 3.0]},
        ],
        "light": None,
    },
    "ore_glint": {  # sparse twinkles on ore inserts; set color to the ore
        "emitters": [
            {"name": "Glint", "texture": "spark_diamond", "color": ["#FFF4D6", "#FFD9A8"], "size": [0, 0.5, 0],
             "transparency": [0.1, 1.0], "lifetime": [0.5, 0.8], "rate": 0.8, "speed": [0, 0], "spread": 0,
             "light_emission": 1.0, "rotation": [0, 90], "shape": [2.0, 1.5, 2.0]},
        ],
        "light": None,
    },
    "crystal_glow": {  # steady soft light from a crystal cluster / geode cave; set light to the crystal's colour
        # Light only: the crystals' own sparkle is a separate ore_glint socket on their tips. No flicker or pulse
        # (crystals shine steadily). Shadows on, so the asset's own walls keep the light in its cave: place the
        # socket in the open, clear of the crystal meshes, or they shadow it. Override the whole light, e.g.
        # vfx.add(obj, "crystal_glow", loc, light={"color": "#6FB7FF", "brightness": 0.8, "range": 8,
        #                                         "flicker": False, "shadows": True})
        "emitters": [],
        "light": {"color": "#B06AF5", "brightness": 1.0, "range": 10, "flicker": False, "shadows": True},
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
    "rock_chip": {"size": 256, "tint": True, "about": "cluster of three faceted stone chips, white-grey"},
    # Beam textures: u (width) runs along the beam, v (height) across it; both tile.
    "waterfall_streaks": {"size": 512, "height": 256, "tint": True, "tile": "uv",
                          "about": "falling-water streak bands and foam flecks, white / pale blue on transparent; "
                                   "streaks run along u (the beam), tiles both ways"},
    "water_streaks": {"size": 256, "tint": True, "tile": "uv",
                      "about": "sparse thin flow streaks on transparent, along u; tiles both ways"},
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


def _to_rbx(v):
    """Blender (x, y, z up) -> Roblox (x, y up, z)."""
    return [round(float(v[0]), 4) + 0.0, round(float(v[2]), 4) + 0.0, round(-float(v[1]), 4) + 0.0]


def beam_frame(direction, face_camera=False, normal=None, axis=None):
    """(axis, normal) unit vectors in Blender space for a beam along `direction`:
    axis = the curve direction (default: along the beam), normal = the beam's face
    (default: up for a flat beam, the asset front -Y for a steep one), made
    perpendicular to the axis."""
    d = Vector(direction)
    d = d.normalized() if d.length > 1e-6 else Vector((0, 0, -1))
    ax = Vector(axis).normalized() if axis is not None and Vector(axis).length > 1e-6 else d
    if normal is not None and Vector(normal).length > 1e-6:
        n = Vector(normal)
    elif face_camera:
        n = Vector((math.sin(math.radians(-22)), -math.cos(math.radians(-22)), math.tan(math.radians(20))))
    else:
        n = Vector((0, 0, 1)) if abs(d.z) < 0.5 else Vector((0, -1, 0))
    n = n - ax * n.dot(ax)
    if n.length < 1e-4:  # normal along the axis: pick any perpendicular
        n = ax.orthogonal()
    return ax, n.normalized()


def add(obj, kind, loc, scale=1.0, name=None, end=None, normal=None, axis=None, **overrides):
    """Attach a VFX socket to `obj` at local `loc` (studs). Returns the Empty.

    Kinds with `beams` need `end` (asset-local studs, like `loc`): the beam runs
    from the socket to it. `normal` / `axis` (Blender local vectors) override the
    beam orientation, `width=` the beam width (see the module docstring). Other
    keyword arguments replace top-level keys of the kind's spec (color, emitters...).
    """
    if kind not in KINDS:
        raise ValueError(f"unknown VFX kind {kind!r}; use one of {sorted(KINDS)}")
    spec = json.loads(json.dumps(KINDS[kind]))
    width = overrides.pop("width", None)
    spec.update(overrides)
    beams = spec.get("beams") or []
    if beams and end is None:
        raise ValueError(f"VFX kind {kind!r} has beams: pass end=(x, y, z), the beam's end point in asset studs")
    if width is not None and beams:
        base = float(beams[0].get("width0", 1.0)) or 1.0
        for b in beams:
            k = float(width) / base
            b["width0"] = round(float(b.get("width0", base)) * k, 3)
            b["width1"] = round(float(b.get("width1", b["width0"])) * k, 3)
        for em in spec.get("emitters", []):
            if em.get("shape_follows_width") and em.get("shape"):
                em["shape"][0] = round(float(width) * float(em["shape_follows_width"]), 3)
    empty = bpy.data.objects.new(name or f"VFX_{kind}", None)
    empty.empty_display_type = "SPHERE"
    empty.empty_display_size = 0.4 * scale
    for coll in obj.users_collection:
        coll.objects.link(empty)
    empty.parent = obj
    empty.location = loc
    empty["vfx_kind"] = kind
    empty["vfx_scale"] = float(scale)
    if end is not None:
        rel = Vector(end) - Vector(loc)
        face_camera = bool(beams and beams[0].get("face_camera"))
        ax, n = beam_frame(rel, face_camera, normal, axis)
        spec["end"] = _to_rbx(rel)
        spec["axis"] = _to_rbx(ax)
        spec["normal"] = _to_rbx(n)
        empty["vfx_end"] = [float(c) for c in end]
        empty["vfx_axis"] = [float(c) for c in ax]
        empty["vfx_normal"] = [float(c) for c in n]
        tip = bpy.data.objects.new(f"{empty.name}_End", None)
        tip.empty_display_type = "CONE"
        tip.empty_display_size = 0.3 * scale
        for coll in obj.users_collection:
            coll.objects.link(tip)
        tip.parent = empty
        tip.location = rel
        tip["vfx_end_of"] = empty.name
    empty["roblox"] = json.dumps(spec)
    return empty


def end_of(socket):
    """A beam socket's end point relative to the socket (Blender, socket space), or None."""
    for c in socket.children:
        if c.get("vfx_end_of"):
            return Vector(c.location)
    if socket.get("vfx_end") is not None:
        return Vector(socket["vfx_end"]) - Vector(socket.location)
    try:
        e = json.loads(socket.get("roblox", "{}")).get("end")
    except ValueError:
        e = None
    return _rb(e) if e else None


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
            "Beams: one Beam per entry of a kind's `beams`, from an Attachment at the socket (Attachment0) to "
            "one at socket position + `end` (Attachment1). Orient both Attachments with Axis = `axis` and "
            "SecondaryAxis = `normal` (the face of a beam with FaceCamera false). color/transparency are "
            "sequences from Attachment0 to Attachment1. Width0/Width1 and TextureLength scale with vfx_scale.",
            "Beam texture_speed is in studs/second along the beam (positive = start to end). Roblox does not "
            "document TextureSpeed's unit; if it is texture lengths per second, set TextureSpeed = "
            "texture_speed / texture_length (verify once in Studio).",
            "Beam textures put u (the image's width) along the beam and v across it.",
            "Emitters with shape_follows_width already have shape[0] set from the socket's width override.",
            "A kind's light is one PointLight in the socket's Attachment: Color, Brightness, Range (x vfx_scale), "
            "Shadows = light.shadows (default false); flicker/pulse are animated in game.",
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
LIGHT_SHADOWS = False   # default shadowless: cheap, and not blocked by the asset's own flame mesh
                        # (a kind's light can ask for shadows: "shadows": True)
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
    "rock_chip": ("solid", "chips"),
    "fire_flipbook_4x4": (None, None),  # the asset mesh already carries the flame
    # beam textures: drawn as textured strips by _beam_strip, never as particles
    "waterfall_streaks": (None, None),
    "water_streaks": (None, None),
}
BEAM_PREVIEW_SEGMENTS = 16  # at most this many quads along a previewed beam
TEXTURE_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "vfx", "textures"))


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


def _beam_material(texture, light_emission):
    """Blended, double-sided material for beam strips: the beam's texture PNG (from
    art/vfx/textures, tiled by the strip's UVs) x the VFXCol colour/alpha, lit but
    with an emission floor so the water reads in any light."""
    le = round(float(light_emission or 0.0), 2)
    name = f"{PREVIEW_PREFIX}beam_{texture}_{int(le * 100)}"
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "VFXCol"
    attr.attribute_type = "GEOMETRY"
    colour, alpha = attr.outputs["Color"], attr.outputs["Alpha"]
    path = os.path.join(TEXTURE_DIR, texture + ".png")
    if os.path.exists(path):
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(path, check_existing=True)
        tex.extension = "REPEAT"
        tex.interpolation = "Linear"
        uv = nt.nodes.new("ShaderNodeUVMap")
        uv.uv_map = "UVMap"
        nt.links.new(uv.outputs["UV"], tex.inputs["Vector"])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        nt.links.new(tex.outputs["Color"], mix.inputs["A"])
        nt.links.new(colour, mix.inputs["B"])
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        nt.links.new(tex.outputs["Alpha"], mul.inputs[0])
        nt.links.new(alpha, mul.inputs[1])
        colour, alpha = mix.outputs["Result"], mul.outputs[0]
    nt.links.new(colour, bsdf.inputs["Base Color"])
    nt.links.new(colour, bsdf.inputs["Emission Color"])
    nt.links.new(alpha, bsdf.inputs["Alpha"])
    bsdf.inputs["Roughness"].default_value = 0.35
    bsdf.inputs["Emission Strength"].default_value = 0.3 + 0.8 * le
    nt.links.new(bsdf.outputs[0], out.inputs["Surface"])
    for attr_name, val in (("surface_render_method", "BLENDED"), ("use_backface_culling", False),
                           ("use_transparency_overlap", True), ("use_transparent_shadow", True)):
        if hasattr(mat, attr_name):
            setattr(mat, attr_name, val)
    return mat


def _bezier(p0, p1, p2, p3, t):
    s = 1 - t
    return p0 * s ** 3 + p1 * 3 * s * s * t + p2 * 3 * s * t * t + p3 * t ** 3


def _beam_strip(s, beam, layer, scale):
    """A textured quad strip previewing one Roblox Beam of socket `s`: start at the
    socket, end at its end point, Width0 -> Width1, CurveSize0/1 along the axis,
    u along the beam (TextureLength studs per tile in Wrap mode), v across it.
    Returns the mesh object (socket space, unparented) or None without an end."""
    rel = end_of(s)
    if rel is None:
        return None
    face_camera = bool(beam.get("face_camera"))
    if s.get("vfx_axis") is not None and s.get("vfx_normal") is not None and not face_camera:
        ax, n = Vector(s["vfx_axis"]), Vector(s["vfx_normal"])
    else:
        ax, n = beam_frame(rel, face_camera)
    p0, p3 = Vector((0, 0, 0)), Vector(rel)
    p1 = p0 + ax * float(beam.get("curve0", 0.0))
    p2 = p3 - ax * float(beam.get("curve1", 0.0))
    segs = max(1, min(int(beam.get("segments", 10)), BEAM_PREVIEW_SEGMENTS))
    w0 = float(beam.get("width0", 1.0)) * scale
    w1 = float(beam.get("width1", beam.get("width0", 1.0))) * scale
    tile = max(float(beam.get("texture_length", 1.0)) * scale, 1e-3)
    mode = beam.get("texture_mode", "Wrap")
    lift = n * 0.04 * (layer + 1)  # layered beams sit just in front of one another
    bm = bmesh.new()
    col = bm.loops.layers.float_color.new("VFXCol")
    uvl = bm.loops.layers.uv.new("UVMap")
    rows, dist, prev = [], 0.0, None
    for i in range(segs + 1):
        t = i / segs
        p = _bezier(p0, p1, p2, p3, t)
        tan = _bezier(p0, p1, p2, p3, min(1.0, t + 1e-3)) - _bezier(p0, p1, p2, p3, max(0.0, t - 1e-3))
        side = tan.cross(n)
        if side.length < 1e-6:
            side = ax.cross(n)
        side.normalize()
        if prev is not None:
            dist += (p - prev).length
        prev = p
        w = w0 + (w1 - w0) * t
        u = t if mode == "Stretch" else dist / tile
        c = _seq(beam.get("color", ["#FFFFFF"]), t)
        a = 1.0 - _seq(beam.get("transparency", [0.0]), t)[0]
        left = bm.verts.new(p - side * w / 2 + lift)
        right = bm.verts.new(p + side * w / 2 + lift)
        rows.append(((left, (u, 0.0)), (right, (u, 1.0)), (c[0], c[1], c[2], a)))
    for (l0, r0, c0), (l1, r1, c1) in zip(rows, rows[1:]):
        f = bm.faces.new((l0[0], r0[0], r1[0], l1[0]))
        f.smooth = False
        for lp, (uvv, cc) in zip(f.loops, ((l0[1], c0), (r0[1], c0), (r1[1], c1), (l1[1], c1))):
            lp[uvl].uv = uvv
            lp[col] = cc
    me = bpy.data.meshes.new(f"{PREVIEW_PREFIX}{s.name}_{beam.get('name', 'Beam')}")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(_beam_material(beam.get("texture", ""), beam.get("light_emission", 0.0)))
    mo = bpy.data.objects.new(me.name, me)
    if hasattr(mo, "visible_shadow"):
        mo.visible_shadow = False
    return mo


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
    if shape == "chips":  # a few faceted stone chips, like the rock_chip texture
        out = []
        for _ in range(3):
            r = size * rng.uniform(0.12, 0.2)
            vs = bmesh.ops.create_icosphere(bm, subdivisions=0, radius=r)["verts"]
            sq = (rng.uniform(0.7, 1.3), rng.uniform(0.7, 1.3), rng.uniform(0.5, 0.9))
            for v in vs:
                v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2]))
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
    if em.get("burst"):  # one burst, caught mid-flight
        n = max(3, min(MAX_PER_EMITTER, em["burst"]))
    else:
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
    speed, spread, drag, acceleration, size and transparency, plus one textured,
    blended quad strip per beam from the socket to its end point (the beam's PNG
    from art/vfx/textures, colour and transparency along it). `objects` limits it
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
            ld.use_shadow = bool(light.get("shadows", LIGHT_SHADOWS))
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
            for layer, beam in enumerate(spec.get("beams") or []):
                mo = _beam_strip(s, beam, layer, scale)
                if mo is not None:
                    made.append(mo)
        for o in made:
            if o.parent is None and o.get("vfx_socket") is None:
                o["vfx_socket"] = s.name
                coll.objects.link(o)
                o.parent = s
    return made
