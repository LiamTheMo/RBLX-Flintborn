"""Flintkit: shared modelling, material and render helpers for Flintborn assets.

Every asset script imports this module so all sheets share one palette, one
shape language and one camera. Conventions:

- 1 Blender unit = 1 Roblox stud. A Roblox character is ~5.5 studs tall.
- Each asset is ONE mesh object (multi-material), origin at the bottom centre,
  front facing -Y, marked as a Blender asset in its own collection.
- Shading is flat (faceted). Every mesh carries a "Tint" colour attribute that
  the shared materials multiply into the base colour, giving each plank, post
  or stone its own slight hand-painted variation.
- Water keys outside PALETTE (KIT_PALETTE and sheet-prefixed module keys such as
  w03_water_shallow) render see-through (blended, alpha = 1 - the Roblox
  Transparency the kit exporter writes: 0.3 deep, 0.5 shallow, 0.4 otherwise;
  `set_water_transparency(mat, t)` overrides one). Their base colour is the same
  tileable cartoon water texture the exporter writes (lib/kitwater.py, cached in
  assets/kit/water_preview/), projected from the object at 16 studs per tile.
  PALETTE water stays flat and opaque, so the lobby looks as before.

Run Blender headless, e.g.:
    blender --background --factory-startup --python build_xx.py
"""

import math
import os
import random

import bmesh
import bpy
import numpy as np
from mathutils import Euler, Matrix, Vector

# ---------------------------------------------------------------------------
# Palette (sRGB hex, roughness, metallic, emission strength)
# ---------------------------------------------------------------------------

PALETTE = {
    "wood": ("#7E4E28", 0.85, 0.0, 0.0),
    "wood_dark": ("#5A361A", 0.85, 0.0, 0.0),
    "wood_light": ("#A2703F", 0.85, 0.0, 0.0),
    "wood_end": ("#C48852", 0.85, 0.0, 0.0),  # cut ends and carved tips
    "bark": ("#93653A", 0.9, 0.0, 0.0),
    "rope": ("#CB944B", 0.8, 0.0, 0.0),
    "rope_dark": ("#A17230", 0.8, 0.0, 0.0),
    "stone": ("#8F8B8F", 0.9, 0.0, 0.0),
    "stone_light": ("#AEAAAC", 0.9, 0.0, 0.0),
    "stone_dark": ("#6C6970", 0.9, 0.0, 0.0),
    "iron": ("#666B75", 0.5, 0.4, 0.0),
    "iron_dark": ("#4C5059", 0.55, 0.4, 0.0),
    "iron_edge": ("#9A9DA4", 0.4, 0.5, 0.0),  # sharpened blade edges
    "thatch": ("#D3A548", 0.9, 0.0, 0.0),
    "thatch_dark": ("#AE822E", 0.9, 0.0, 0.0),
    "leaf": ("#6C9A28", 0.8, 0.0, 0.0),  # warm, deep canopy green (lobby reference)
    "leaf_light": ("#86AE2E", 0.8, 0.0, 0.0),
    "leaf_dark": ("#3F6A1E", 0.8, 0.0, 0.0),
    "pine": ("#3A6C28", 0.8, 0.0, 0.0),  # darker, slightly cooler than the broadleaves
    "pine_dark": ("#284A22", 0.8, 0.0, 0.0),
    "cloth_red": ("#A63A2B", 0.85, 0.0, 0.0),
    "cloth_cream": ("#E7D3AE", 0.85, 0.0, 0.0),
    "parchment": ("#EAD5A8", 0.9, 0.0, 0.0),
    "ink": ("#9A6B40", 0.9, 0.0, 0.0),
    "clay": ("#C4633D", 0.85, 0.0, 0.0),
    "clay_light": ("#E8B98C", 0.85, 0.0, 0.0),
    "wicker": ("#C89A52", 0.85, 0.0, 0.0),
    "bone": ("#EADFC8", 0.7, 0.0, 0.0),
    "flower_white": ("#F5F2EA", 0.7, 0.0, 0.0),
    "flower_yellow": ("#F2C230", 0.7, 0.0, 0.0),
    "berry": ("#C8262B", 0.5, 0.0, 0.0),
    "dirt": ("#C68A4C", 0.95, 0.0, 0.0),
    "grass_ground": ("#A2B82C", 0.95, 0.0, 0.0),  # warm yellow-green (lobby reference)
    "grass_light": ("#B4D23E", 0.95, 0.0, 0.0),
    "grass_dark": ("#2F6528", 0.95, 0.0, 0.0),
    "sand": ("#D8B678", 0.95, 0.0, 0.0),
    "water": ("#2DA0CD", 0.2, 0.0, 0.0),
    "water_deep": ("#167DAD", 0.2, 0.0, 0.0),
    "water_shallow": ("#81C3DA", 0.2, 0.0, 0.0),
    "cliff_rock": ("#5C5B64", 0.9, 0.0, 0.0),  # terrain-kit cliffs: cool blue-violet grey
    "cliff_rock_light": ("#AAA19C", 0.9, 0.0, 0.0),
    "cliff_rock_dark": ("#3F3E47", 0.9, 0.0, 0.0),
    "dirt_tan": ("#C6964B", 0.95, 0.0, 0.0),
    "foam": ("#E9F6FA", 0.4, 0.0, 0.0),
    "earth": ("#A86E3C", 0.95, 0.0, 0.0),  # exposed soil on cliff and ramp edges
    "charcoal": ("#3B2A20", 0.95, 0.0, 0.0),
    # Emissive
    "fire_core": ("#FFE58A", 0.5, 0.0, 2.2),
    "fire_mid": ("#FFA42E", 0.5, 0.0, 1.8),
    "fire_outer": ("#F2601C", 0.5, 0.0, 1.5),
    "ember": ("#FF7A2A", 0.5, 0.0, 1.4),
    "glow_orange": ("#FF8C2A", 0.5, 0.0, 1.8),  # forge glyphs, lava seams
    "rune_blue": ("#BFE6F2", 0.5, 0.0, 0.4),  # engraved rune stones
}

# World-kit colours (art/reference/kit sheets), kept apart from PALETTE so the
# lobby export's palette.png layout never changes. Kit sheet modules may add their
# own keys (prefixed with the sheet id) through their PALETTE dict; build_kit.py
# merges them in before building. The kit exporter reads colours back from each
# material's `flintkit_hex`, so any key here is exportable. The _light/_dark keys
# are for genuinely different material (a paler stratum, a wet base), never for
# painting sun or shadow onto faces: lighting does that.
KIT_PALETTE = {
    # W01 boulders: warm mauve-grey rock with cool blue-grey shadow facets
    "kit_rock": ("#A89C9C", 0.9, 0.0, 0.0),
    "kit_rock_light": ("#C9BCB4", 0.9, 0.0, 0.0),
    "kit_rock_dark": ("#7F7C8A", 0.9, 0.0, 0.0),
    "moss": ("#8AAA24", 0.9, 0.0, 0.0),
    "moss_light": ("#C4D02E", 0.9, 0.0, 0.0),
    "moss_dark": ("#5E8A1E", 0.9, 0.0, 0.0),
    # R01 stone and common ores
    "ore_stone": ("#9D9590", 0.9, 0.0, 0.0),
    "ore_stone_light": ("#B9B1AB", 0.9, 0.0, 0.0),
    "ore_stone_dark": ("#6E696B", 0.9, 0.0, 0.0),
    "limestone": ("#DCC6A2", 0.9, 0.0, 0.0),
    "limestone_dark": ("#C2A883", 0.9, 0.0, 0.0),
    "flint": ("#3F424C", 0.45, 0.1, 0.0),
    "flint_light": ("#5C606D", 0.45, 0.1, 0.0),
    "coal": ("#2F3137", 0.6, 0.0, 0.0),
    "coal_light": ("#4B4D55", 0.6, 0.0, 0.0),
    "copper": ("#E2713A", 0.5, 0.35, 0.0),
    "copper_dark": ("#B8542A", 0.55, 0.35, 0.0),
    "patina": ("#4FA89B", 0.7, 0.0, 0.0),
}


def palette_entry(name):
    """(hex, roughness, metallic, emission) for a PALETTE or KIT_PALETTE key."""
    return PALETTE[name] if name in PALETTE else KIT_PALETTE[name]


def is_emissive(name):
    return palette_entry(name)[3] > 0


EMISSIVE = {k for k, v in PALETTE.items() if v[3] > 0}
# Foliage and ground greens: a weak specular so the sky's sheen does not wash the
# saturated greens out toward grey.
LOW_SPEC = {"leaf", "leaf_light", "leaf_dark", "pine", "pine_dark", "grass_ground", "grass_light",
            "grass_dark", "moss", "moss_light", "moss_dark"}


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(srgb_to_linear(int(h[i : i + 2], 16) / 255) for i in (0, 2, 4))


def material(name):
    """Get or create a shared palette material by palette key."""
    mname = "FB_" + name
    mat = bpy.data.materials.get(mname)
    if mat:
        return mat
    hexcol, rough, metal, emit = palette_entry(name)
    rgb = hex_rgb(hexcol)
    mat = bpy.data.materials.new(mname)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if name in LOW_SPEC and "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.2
    if emit > 0:
        bsdf.inputs["Base Color"].default_value = (*rgb, 1)
        bsdf.inputs["Emission Color"].default_value = (*rgb, 1)
        bsdf.inputs["Emission Strength"].default_value = emit
    else:
        attr = nt.nodes.new("ShaderNodeAttribute")
        attr.attribute_name = "Tint"
        attr.attribute_type = "GEOMETRY"
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        mix.inputs["A"].default_value = (*rgb, 1)
        nt.links.new(attr.outputs["Color"], mix.inputs["B"])
        nt.links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
    mat.diffuse_color = (*rgb, 1)
    mat["flintkit_hex"] = hexcol
    mat["flintkit_key"] = name
    mat["flintkit_spec"] = [rough, metal, emit]
    if is_water_key(name) and name not in PALETTE and emit <= 0:
        _water_texture(mat, name, hexcol)
        _see_through(mat, water_transparency(name))
    return mat


# ---------------------------------------------------------------------------
# Water: see-through in kit renders, as Roblox shows it
# ---------------------------------------------------------------------------

WATER_KEYS = {"water", "water_deep", "water_shallow"}
WATER_TRANSPARENCY = {"deep": 0.3, "shallow": 0.5, "default": 0.4}  # Roblox Transparency by key word


def is_water_key(name):
    """Water faces: the PALETTE water keys or any key containing "water"
    (w03_water_shallow, w03_water_fall ...). The kit exporter uses the same rule."""
    return name in WATER_KEYS or "water" in name.lower()


def water_transparency(name, mat=None):
    """Roblox Transparency for a water key: a material's `kit_transparency`
    custom property if set, else 0.3 for deep, 0.5 for shallow, 0.4 otherwise."""
    if mat is not None and mat.get("kit_transparency") is not None:
        return float(mat["kit_transparency"])
    k = name.lower()
    if "deep" in k:
        return WATER_TRANSPARENCY["deep"]
    if "shallow" in k:
        return WATER_TRANSPARENCY["shallow"]
    return WATER_TRANSPARENCY["default"]


WATER_PREVIEW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 "assets", "kit", "water_preview")


def _water_texture(mat, name, hexcol):
    """Kit water preview: the exporter's water/<key>.png texture (lib/kitwater.py,
    cached as WATER_PREVIEW_DIR/<key>.png) in place of the flat colour, still x
    Tint. Object coordinates / 16 with box projection give the exporter's UVs
    (up-facing faces: u = x / 16, v = y / 16 from the asset origin), and stay put
    when the runner moves assets around. Falls back to the flat colour on error."""
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    link = next((l for l in bsdf.inputs["Base Color"].links), None)
    mix = link.from_node if link is not None else None
    if mix is None or mix.type != "MIX" or nt.nodes.get("FB_WaterTex") is not None:
        return
    try:
        import sys

        lib = os.path.dirname(os.path.abspath(__file__))
        if lib not in sys.path:
            sys.path.append(lib)
        import kitwater

        safe = "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in name)
        path = kitwater.cached_png(os.path.join(WATER_PREVIEW_DIR, safe + ".png"), hexcol, name)
        image = bpy.data.images.load(path, check_existing=True)
    except Exception as exc:  # noqa: BLE001  (never break a build over the preview)
        print(f"flintkit: water preview texture for {name} failed, flat colour kept: {exc!r}")
        return
    image.colorspace_settings.name = "sRGB"
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.vector_type = "POINT"
    s = 1.0 / kitwater.TILE_STUDS
    mapping.inputs["Scale"].default_value = (s, s, s)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.name = "FB_WaterTex"
    tex.image = image
    tex.extension = "REPEAT"
    tex.interpolation = "Linear"
    tex.projection = "BOX"  # up/down faces (x, y), +-Y faces (x, z), +-X faces (y, z), as exported
    tex.projection_blend = 0.0
    nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], mix.inputs["A"])


def _see_through(mat, transparency):
    """Blended Eevee material with alpha 1 - transparency, single-sided like a
    Roblox MeshPart, casting no shadow (the exporter sets CastShadow false)."""
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    node = nt.nodes.get("FB_WaterAlpha")
    if node is None:
        lp = nt.nodes.new("ShaderNodeLightPath")
        inv = nt.nodes.new("ShaderNodeMath")
        inv.operation = "SUBTRACT"
        inv.inputs[0].default_value = 1.0
        nt.links.new(lp.outputs["Is Shadow Ray"], inv.inputs[1])
        node = nt.nodes.new("ShaderNodeMath")
        node.name = "FB_WaterAlpha"
        node.operation = "MULTIPLY"
        nt.links.new(inv.outputs[0], node.inputs[1])
        nt.links.new(node.outputs[0], bsdf.inputs["Alpha"])
    node.inputs[0].default_value = max(0.0, min(1.0, 1.0 - transparency))
    for attr_name, val in (("surface_render_method", "BLENDED"), ("use_backface_culling", True),
                           ("use_transparency_overlap", False), ("use_transparent_shadow", True)):
        if hasattr(mat, attr_name):
            setattr(mat, attr_name, val)
    mat.diffuse_color = (*mat.diffuse_color[:3], 1.0 - transparency)


def set_water_transparency(mat, transparency):
    """Override one water material's Roblox Transparency: stores `kit_transparency`
    (read by the kit exporter) and updates the preview alpha to match."""
    mat["kit_transparency"] = float(transparency)
    if mat.node_tree is not None and mat.node_tree.nodes.get("Principled BSDF"):
        _see_through(mat, float(transparency))
    return mat


# ---------------------------------------------------------------------------
# Asset builder: one bmesh, many parts, one material slot per palette key
# ---------------------------------------------------------------------------


def _mat4(loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    if isinstance(scale, (int, float)):
        scale = (scale, scale, scale)
    m = Matrix.Translation(Vector(loc)) @ Euler(rot).to_matrix().to_4x4()
    s = Matrix.Diagonal((*scale, 1.0))
    return m @ s


def _faces_of(verts):
    faces = set()
    for v in verts:
        faces.update(v.link_faces)
    return list(faces)


def _edges_of(verts):
    edges = set()
    for v in verts:
        edges.update(v.link_edges)
    return list(edges)


class Asset:
    """Accumulates primitive parts into one multi-material mesh.

    Rotations are Euler XYZ in radians. Every part method returns its verts.
    `tint` is a brightness multiplier around 1.0; by default each part gets a
    random tint in [1 - tint_var, 1 + tint_var].
    """

    def __init__(self, name, category, seed=None, tint_var=0.07):
        self.name = name
        self.category = category
        self.bm = bmesh.new()
        self.tint_layer = self.bm.loops.layers.float_color.new("Tint")
        self.mats = []
        self.rng = random.Random(seed if seed is not None else sum(map(ord, name)))
        self.tint_var = tint_var

    # -- internals ---------------------------------------------------------

    def _mi(self, matname):
        if matname not in self.mats:
            self.mats.append(matname)
        return self.mats.index(matname)

    def _finish(self, verts, mat, tint=None, jitter=0.0, face_tint_var=0.0):
        mi = self._mi(mat)
        if jitter:
            for v in verts:
                v.co += Vector(
                    (
                        self.rng.uniform(-jitter, jitter),
                        self.rng.uniform(-jitter, jitter),
                        self.rng.uniform(-jitter, jitter),
                    )
                )
        t = tint if tint is not None else 1.0 + self.rng.uniform(-self.tint_var, self.tint_var)
        for f in _faces_of(verts):
            f.material_index = mi
            f.smooth = False
            ft = t * (1.0 + self.rng.uniform(-face_tint_var, face_tint_var)) if face_tint_var else t
            for loop in f.loops:
                loop[self.tint_layer] = (ft, ft, ft, 1.0)
        return verts

    def transform(self, verts, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
        bmesh.ops.transform(self.bm, matrix=_mat4(loc, rot, scale), verts=verts)
        return verts

    # -- primitives ----------------------------------------------------------

    def cyl(self, r1, r2, h, sides=8, loc=(0, 0, 0), rot=(0, 0, 0), mat="wood",
            jitter=0.0, tint=None, cap=True, twist=0.0):
        """Faceted cylinder/cone. Base at local z=0, extends to z=h."""
        res = bmesh.ops.create_cone(self.bm, cap_ends=cap, cap_tris=False, segments=sides,
                                    radius1=r1, radius2=max(r2, 1e-4), depth=h,
                                    matrix=Matrix.Translation((0, 0, h / 2)))
        verts = res["verts"]
        if twist:
            bmesh.ops.rotate(self.bm, verts=verts, cent=(0, 0, 0), matrix=Matrix.Rotation(twist, 3, "Z"))
        self.transform(verts, loc, rot)
        return self._finish(verts, mat, tint, jitter)

    def box(self, size, loc=(0, 0, 0), rot=(0, 0, 0), mat="wood", bevel=0.0,
            jitter=0.0, tint=None, base=False):
        """Box of `size` (x, y, z) centred on loc (or sitting on loc if base=True)."""
        res = bmesh.ops.create_cube(self.bm, size=1.0)
        verts = res["verts"]
        bmesh.ops.scale(self.bm, vec=Vector(size), verts=verts)
        if base:
            bmesh.ops.translate(self.bm, vec=(0, 0, size[2] / 2), verts=verts)
        if bevel:
            geom = bmesh.ops.bevel(self.bm, geom=_edges_of(verts), offset=bevel, segments=1,
                                   affect="EDGES", profile=0.5)
            verts = list(set(verts) | set(geom["verts"]))
            verts = [v for v in verts if v.is_valid]
        self.transform(verts, loc, rot)
        return self._finish(verts, mat, tint, jitter)

    def ico(self, radius, loc=(0, 0, 0), rot=(0, 0, 0), mat="stone", subdiv=1,
            jitter=0.0, tint=None, facets=0.0, face_tint_var=0.0):
        """Icosphere; `radius` may be a scalar or (rx, ry, rz). `facets` (degrees)
        dissolves near-coplanar faces into big chiselled facets."""
        if isinstance(radius, (int, float)):
            radius = (radius, radius, radius)
        res = bmesh.ops.create_icosphere(self.bm, subdivisions=subdiv, radius=1.0)
        verts = res["verts"]
        bmesh.ops.scale(self.bm, vec=Vector(radius), verts=verts)
        if jitter:
            for v in verts:
                d = v.co.normalized()
                v.co += d * self.rng.uniform(-jitter, jitter) * max(radius)
            jitter = 0.0
        if facets:
            bmesh.ops.dissolve_limit(self.bm, angle_limit=math.radians(facets), verts=verts,
                                     edges=_edges_of(verts))
            verts = [v for v in verts if v.is_valid]
        self.transform(verts, loc, rot)
        return self._finish(verts, mat, tint, 0.0, face_tint_var)

    def torus(self, R, r, loc=(0, 0, 0), rot=(0, 0, 0), mat="rope", seg=12, rseg=4,
              tint=None, squash=1.0):
        """Torus in the local XY plane (axis Z). `squash` scales tube height."""
        bm = self.bm
        rings = []
        for i in range(seg):
            a = 2 * math.pi * i / seg
            ring = []
            for j in range(rseg):
                b = 2 * math.pi * j / rseg + math.pi / rseg
                x = (R + r * math.cos(b)) * math.cos(a)
                y = (R + r * math.cos(b)) * math.sin(a)
                z = r * math.sin(b) * squash
                ring.append(bm.verts.new((x, y, z)))
            rings.append(ring)
        for i in range(seg):
            for j in range(rseg):
                a, b = rings[i][j], rings[(i + 1) % seg][j]
                c, d = rings[(i + 1) % seg][(j + 1) % rseg], rings[i][(j + 1) % rseg]
                bm.faces.new((a, b, c, d))
        verts = [v for ring in rings for v in ring]
        self.transform(verts, loc, rot)
        return self._finish(verts, mat, tint)

    def poly_prism(self, points2d, depth, loc=(0, 0, 0), rot=(0, 0, 0), mat="cloth_cream",
                   tint=None):
        """Extruded 2D polygon (local XY outline, extruded +Z by depth). Points CCW."""
        bm = self.bm
        bottom = [bm.verts.new((x, y, 0)) for x, y in points2d]
        top = [bm.verts.new((x, y, depth)) for x, y in points2d]
        bm.faces.new(list(reversed(bottom)))
        bm.faces.new(top)
        n = len(points2d)
        for i in range(n):
            bm.faces.new((bottom[i], bottom[(i + 1) % n], top[(i + 1) % n], top[i]))
        verts = bottom + top
        self.transform(verts, loc, rot)
        return self._finish(verts, mat, tint)

    def strip(self, points2d, width, depth, loc=(0, 0, 0), rot=(0, 0, 0), mat="rune_blue",
              tint=None):
        """Line glyph: a thin bar along each consecutive pair of local-XY points."""
        out = []
        for (x1, y1), (x2, y2) in zip(points2d, points2d[1:]):
            dx, dy = x2 - x1, y2 - y1
            length = math.hypot(dx, dy) + width
            ang = math.atan2(dy, dx)
            mid = ((x1 + x2) / 2, (y1 + y2) / 2, depth / 2)
            verts = bmesh.ops.create_cube(self.bm, size=1.0)["verts"]
            bmesh.ops.scale(self.bm, vec=(length, width, depth), verts=verts)
            bmesh.ops.rotate(self.bm, verts=verts, cent=(0, 0, 0), matrix=Matrix.Rotation(ang, 3, "Z"))
            bmesh.ops.translate(self.bm, vec=mid, verts=verts)
            self.transform(verts, loc, rot)
            out += self._finish(verts, mat, tint)
        return out

    # -- composite parts --------------------------------------------------------

    def stake(self, radius, height, tip=None, loc=(0, 0, 0), sides=7, jitter=0.03,
              mat="wood", tip_mat="wood_end", lean=(0, 0)):
        """Palisade stake: faceted post with a carved pencil tip."""
        tip = tip if tip is not None else radius * 2.2
        body = height - tip
        rot = (lean[0], lean[1], self.rng.uniform(0, math.pi))
        t = 1.0 + self.rng.uniform(-self.tint_var, self.tint_var)
        v1 = self.cyl(radius, radius * 0.97, body, sides, mat=mat, jitter=radius * jitter, tint=t)
        v2 = self.cyl(radius * 0.97, radius * 0.06, tip, sides, loc=(0, 0, body), mat=tip_mat,
                      jitter=radius * jitter * 0.5, tint=t, cap=False)
        verts = v1 + v2
        self.transform(verts, loc, rot)
        return verts

    def post(self, radius, height, loc=(0, 0, 0), sides=8, jitter=0.03, mat="wood",
             top_mat="wood_end", chamfer=0.25):
        """Flat-topped post with a chamfered, lighter cut top."""
        t = 1.0 + self.rng.uniform(-self.tint_var, self.tint_var)
        c = radius * chamfer
        v1 = self.cyl(radius, radius, height - c, sides, mat=mat, jitter=radius * jitter, tint=t)
        v2 = self.cyl(radius, radius * 0.8, c, sides, loc=(0, 0, height - c), mat=top_mat, tint=t)
        verts = v1 + v2
        self.transform(verts, loc, (0, 0, self.rng.uniform(0, math.pi)))
        return verts

    def beam(self, p1, p2, radius, sides=7, mat="wood", end_mat="wood_end", jitter=0.02,
             overhang=0.0):
        """Log between two points with lighter cut ends."""
        p1, p2 = Vector(p1), Vector(p2)
        d = p2 - p1
        length = d.length + 2 * overhang
        t = 1.0 + self.rng.uniform(-self.tint_var, self.tint_var)
        ce = min(radius * 0.25, length * 0.1)
        v = self.cyl(radius, radius, length - 2 * ce, sides, loc=(0, 0, ce), mat=mat,
                     jitter=radius * jitter, tint=t)
        v += self.cyl(radius * 0.85, radius, ce, sides, mat=end_mat, tint=t)
        v += self.cyl(radius, radius * 0.85, ce, sides, loc=(0, 0, length - ce), mat=end_mat, tint=t)
        rot = d.to_track_quat("Z", "Y").to_euler()
        bmesh.ops.translate(self.bm, vec=(0, 0, -overhang), verts=v)
        self.transform(v, p1, rot)
        return v

    def rope_rings(self, radius, z, count=2, thickness=None, loc=(0, 0), gap=None,
                   mat="rope", axis_rot=(0, 0, 0)):
        """Stacked rope wraps around a post of `radius` centred at loc, from height z."""
        thickness = thickness or max(radius * 0.18, 0.06)
        gap = gap if gap is not None else thickness * 1.9
        out = []
        for i in range(count):
            out += self.torus(radius + thickness * 0.55, thickness, mat=mat,
                              loc=(0, 0, z + i * gap), seg=10, rseg=4,
                              tint=1.0 + self.rng.uniform(-0.05, 0.05))
        self.transform(out, (loc[0], loc[1], 0), axis_rot)
        return out

    def tube_loop(self, points, thickness, mat="rope", rseg=5, closed=True, tint=None):
        """Sweep a faceted tube of radius `thickness` along a 3D polyline."""
        bm = self.bm
        pts = [Vector(p) for p in points]
        n = len(pts)
        rings = []
        for i, p in enumerate(pts):
            if closed:
                t = pts[(i + 1) % n] - pts[i - 1]
            else:
                t = pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]
            t.normalize()
            up = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
            nrm = t.cross(up).normalized()
            bi = nrm.cross(t).normalized()
            ring = []
            for j in range(rseg):
                b = 2 * math.pi * j / rseg
                ring.append(bm.verts.new(p + thickness * (math.cos(b) * nrm + math.sin(b) * bi)))
            rings.append(ring)
        segs = n if closed else n - 1
        for i in range(segs):
            r1, r2 = rings[i], rings[(i + 1) % n]
            for j in range(rseg):
                bm.faces.new((r1[j], r2[j], r2[(j + 1) % rseg], r1[(j + 1) % rseg]))
        if not closed:
            bm.faces.new(list(reversed(rings[0])))
            bm.faces.new(rings[-1])
        verts = [v for r in rings for v in r]
        return self._finish(verts, mat, tint)

    def rope_band(self, xs, radius, z, count=2, thickness=0.13, y=0.0, mat="rope", arc=6):
        """Rope wraps lashing a straight row of stakes at x positions `xs` (along X,
        at depth y) with stake `radius`. Follows each stake's curve like real lashing."""
        xs = sorted(xs)
        R = radius * 1.02 + thickness * 0.9
        out = []
        for k in range(count):
            zz = z + k * thickness * 1.85
            pts = []

            def arc_pts(cx, a0, a1):
                steps = max(2, int(abs(a1 - a0) / 180 * arc) + 1)
                for s in range(steps + 1):
                    a = math.radians(a0 + (a1 - a0) * s / steps)
                    pts.append((cx + R * math.cos(a), y + R * math.sin(a), zz))

            for i, cx in enumerate(xs):  # front side, left to right
                a0 = 90 if i == 0 else 215
                a1 = 450 if i == len(xs) - 1 else 325
                arc_pts(cx, a0 if i == 0 else a0, a1 if i < len(xs) - 1 else 270 + 180)
            for i, cx in enumerate(reversed(xs[1:-1])):  # back side, right to left
                arc_pts(cx, 35, 145)
            # remove near-duplicate consecutive points
            clean = [pts[0]]
            for p in pts[1:]:
                if (Vector(p) - Vector(clean[-1])).length > thickness * 0.5:
                    clean.append(p)
            if (Vector(clean[0]) - Vector(clean[-1])).length < thickness * 0.5:
                clean.pop()
            out += self.tube_loop(clean, thickness, mat=mat,
                                  tint=1.0 + self.rng.uniform(-0.05, 0.05))
        return out

    def lashing(self, loc, size=0.35, thickness=0.07, rot=(0, 0, 0), mat="rope"):
        """X-shaped rope lashing at a joint (two crossed flattened loops)."""
        out = []
        for a in (math.pi / 4, -math.pi / 4):
            out += self.torus(size, thickness, rot=(0, a, 0), seg=10, rseg=4, mat=mat, squash=0.7)
        self.transform(out, loc, rot)
        return out

    def plank(self, size, loc=(0, 0, 0), rot=(0, 0, 0), mat="wood", bevel=None, jitter=None):
        bevel = bevel if bevel is not None else min(size) * 0.12
        jitter = jitter if jitter is not None else min(size) * 0.04
        return self.box(size, loc, rot, mat=mat, bevel=bevel, jitter=jitter)

    def stone_block(self, size, loc=(0, 0, 0), rot=(0, 0, 0), mat="stone", bevel=None,
                    jitter=None):
        bevel = bevel if bevel is not None else min(size) * 0.14
        jitter = jitter if jitter is not None else min(size) * 0.05
        return self.box(size, loc, rot, mat=mat, bevel=bevel, jitter=jitter)

    def rock(self, size, loc=(0, 0, 0), rot=(0, 0, 0), mat="stone", subdiv=2, rough=0.12,
             facets=14, sink=0.15):
        """Chiselled low-poly boulder; `size` = (x, y, z) full extents."""
        r = (size[0] / 2, size[1] / 2, size[2] / 2)
        loc = (loc[0], loc[1], loc[2] + r[2] * (1 - sink))
        verts = self.ico(r, loc, rot, mat=mat, subdiv=subdiv, jitter=rough, facets=facets,
                         face_tint_var=0.05)
        # flatten the buried underside
        floor = loc[2] - r[2] * (1 - sink)
        for v in verts:
            if v.co.z < floor:
                v.co.z = floor
        return verts

    def leaf_blob(self, radius, loc=(0, 0, 0), mat="leaf", subdiv=1, rough=0.12, facets=0):
        return self.ico(radius, loc, mat=mat, subdiv=subdiv, jitter=rough, facets=facets,
                        face_tint_var=0.06)

    # -- foliage: faceted "cauliflower" leaf masses -------------------------------
    #
    # The kit references build crowns and bushes from many chunky clumps: each a
    # rounded star of protruding faceted lobes round a low peak, overlapping into
    # one big lumpy mass. leaf_cluster makes one clump, canopy fills a whole crown
    # volume with them. One material, flat facets, one small random Tint per clump
    # (never by height or facing: lighting shades it), faces buried inside another
    # clump are deleted, nothing below `floor`.
    #
    # Only verts.new / faces.new / transform / delete are used here: in this
    # Blender, bmesh.ops.dissolve_limit and create_icosphere(subdivisions >= 2)
    # invalidate the Python references to every OTHER vert already in the bmesh.

    # Lobed-dome ring layout, top to bottom, per `facets` level: (tip elevation
    # deg, tip radius, notch elevation, notch radius). A ring with notch radius
    # None has one vert per lobe (the ridge to the peak, or the base); the others
    # have two verts per lobe (its flat outer face) and one notch between lobes.
    _DOME_RINGS = {
        1: ((58, 0.80, 0, None), (24, 1.0, 18, 0.64), (-10, 0.92, -14, 0.6), (-46, 0.6, 0, None)),
        2: ((66, 0.78, 0, None), (40, 0.96, 34, 0.68), (12, 1.0, 6, 0.6), (-16, 0.9, -20, 0.58),
            (-50, 0.58, 0, None)),
    }

    def _lobed_dome(self, rng, lobes, lobe_size, rough, facets=1, depth=1.0):
        """Unit lobed dome (local +Z up): an off-centre peak, ridges down to
        `lobes` broad lobes pushed out round the upper hemisphere, deep notches
        between them, a flat polygon base. `depth` scales how deep the notches
        between lobes cut in (0 = a plain faceted dome). Explicit triangles:
        16 x lobes - 2 at facets=1, 22 x lobes - 2 at facets=2. Returns its verts."""
        bm = self.bm
        L = max(3, int(lobes))
        lo, hi = lobe_size
        mid = (lo + hi) / 2
        step = 2 * math.pi / L
        az0 = rng.uniform(0, 2 * math.pi)
        tips = [az0 + i * step + rng.uniform(-0.18, 0.18) * step for i in range(L)]
        prom = [rng.uniform(lo, hi) / mid for _ in range(L)]  # each lobe's own size, ~0.8-1.2
        lift = [rng.uniform(-7, 7) for _ in range(L)]  # each lobe sits a little higher or lower
        gaps = [(tips[(i + 1) % L] - tips[i]) % (2 * math.pi) for i in range(L)]

        def vert(az, el, r):
            el = math.radians(el + rng.uniform(-3, 3))
            r *= 1.0 + rng.uniform(-rough, rough)
            return bm.verts.new((r * math.cos(el) * math.cos(az), r * math.cos(el) * math.sin(az),
                                 r * math.sin(el)))

        pole = bm.verts.new((rng.uniform(-0.1, 0.1), rng.uniform(-0.1, 0.1), rng.uniform(0.84, 0.96)))
        rings = []
        for el_t, r_t, el_n, r_n in self._DOME_RINGS.get(int(facets), self._DOME_RINGS[1]):
            ring = []
            for i in range(L):
                rt = r_t * (1 + 0.3 * (prom[i] - 1))
                if r_n is None:
                    ring.append(vert(tips[i], el_t + lift[i] * 0.5, rt))
                    continue
                w = gaps[i] * 0.2 * prom[i]
                ring.append(vert(tips[i] - w, el_t + lift[i], rt))
                ring.append(vert(tips[i] + w, el_t + lift[i], rt))
                ring.append(vert(tips[i] + gaps[i] * rng.uniform(0.45, 0.55), el_n, rt - (rt - r_n) * depth))
            rings.append(ring)
        new = bm.faces.new
        for i in range(L):
            new((pole, rings[0][i], rings[0][(i + 1) % L]))
        for up, dn in zip(rings, rings[1:]):
            for i in range(L):
                j = (i + 1) % L
                if len(up) == len(dn):
                    for k in range(3 * i, 3 * i + 3):
                        n = (k + 1) % len(up)
                        new((up[k], dn[k], dn[n]))
                        new((up[k], dn[n], up[n]))
                elif len(up) < len(dn):  # ridge ring above a lobe ring
                    new((up[i], dn[3 * i], dn[3 * i + 1]))
                    new((up[i], dn[3 * i + 1], dn[3 * i + 2]))
                    new((up[i], dn[3 * i + 2], up[j]))
                    new((up[j], dn[3 * i + 2], dn[3 * j]))
                else:  # lobe ring above the base ring
                    new((up[3 * i], dn[i], up[3 * i + 1]))
                    new((up[3 * i + 1], dn[i], up[3 * i + 2]))
                    new((up[3 * i + 2], dn[i], dn[j]))
                    new((up[3 * i + 2], dn[j], up[3 * j]))
        new(list(reversed(rings[-1])))
        return [pole] + [v for r in rings for v in r]

    def _leaf_part(self, rng, radius, loc, lobes, squash, lobe_size, facets, rough, axis=None,
                   depth=1.0):
        """One placed lobed dome as a part record: [verts, centre, bounding
        radius]. `radius` may be (rx, ry, rz); `axis`
        tilts the dome's up direction (default straight up)."""
        verts = self._lobed_dome(rng, lobes, lobe_size, rough, facets, depth)
        rx, ry, rz = radius if isinstance(radius, (tuple, list)) else (radius, radius, radius)
        up = Vector(axis).normalized() if axis is not None else Vector((0, 0, 1))
        m = (Matrix.Translation(Vector(loc)) @ up.to_track_quat("Z", "Y").to_matrix().to_4x4()
             @ Matrix.Rotation(rng.uniform(-0.12, 0.12), 4, "X")
             @ Matrix.Rotation(rng.uniform(-0.12, 0.12), 4, "Y")
             @ Matrix.Diagonal((rx, ry, rz * squash, 1.0)))
        bmesh.ops.transform(self.bm, matrix=m, verts=verts)
        return [verts, Vector(loc), max(rx, ry, rz) * (1 + rough)]

    def _leaf_cull(self, parts, floor=None, margin=0.88):
        """Delete faces buried inside another clump: every vert of the face lies
        within `margin` of the way from that clump's centre to its surface (a ray
        cast from the centre through the vert hits nothing that close). Lobed
        domes are star-shaped round their centre, so the test is reliable; the
        margin keeps faces that bridge a notch. Returns the number deleted."""
        from mathutils.bvhtree import BVHTree

        trees = []
        for verts, c, _ in parts:
            faces = _faces_of(verts)
            idx = {v: n for n, v in enumerate(verts)}
            ok = faces and (floor is None or c.z > floor + 1e-3)
            trees.append(BVHTree.FromPolygons([v.co.copy() for v in verts],
                                              [[idx[v] for v in f.verts] for f in faces]) if ok else None)
        dead = set()
        for i, (verts, c, br) in enumerate(parts):
            near = [j for j, (_, cj, bj) in enumerate(parts)
                    if j != i and trees[j] is not None and (cj - c).length < bj + br]
            for f in _faces_of(verts):
                pts = [v.co.copy() for v in f.verts]
                if floor is not None and min(q.z for q in pts) <= floor + 1e-3:
                    continue
                for j in near:
                    cj = parts[j][1]
                    for q in pts:
                        d = q - cj
                        dl = d.length
                        if dl > 1e-6 and trees[j].ray_cast(cj, d / dl, dl / margin)[0] is not None:
                            break  # this vert is near or outside clump j's surface
                    else:
                        dead.add(f)
                        break
        if dead:
            bmesh.ops.delete(self.bm, geom=list(dead), context="FACES")
        for p in parts:
            p[0] = [v for v in p[0] if v.is_valid]
        return len(dead)

    def _leaf_floor(self, verts, floor):
        """Clamp verts to z >= floor; faces left lying on the floor face the
        ground, so they are deleted."""
        if floor is None:
            return verts
        for v in verts:
            if v.co.z < floor:
                v.co.z = floor
        flat = [f for f in _faces_of(verts) if all(abs(v.co.z - floor) < 1e-4 for v in f.verts)]
        if flat:
            bmesh.ops.delete(self.bm, geom=flat, context="FACES")
        return [v for v in verts if v.is_valid]

    def leaf_cluster(self, radius, loc=(0, 0, 0), mat="leaf", lobes=7, squash=0.8,
                     lobe_size=(0.45, 0.65), facets=1, rough=0.1, seed=None, tint=None,
                     floor=None, axis=None, depth=1.0):
        """One stylised "cauliflower" leaf clump of about `radius` studs centred on loc.

        A lobed dome: a low off-centre peak with ridges running down to `lobes`
        broad, protruding lobes round the upper hemisphere, deep notches between
        them, and a flat base, so it reads as the references' chunky rounded star
        with big crisp flat facets. Each lobe gets its own size (lobe_size range,
        relative; ~0.8-1.2x) and height. `squash` flattens it along `axis` (default
        up; tilt it to face a clump outward), `facets` is the detail level (1:
        16 x lobes - 2 tris, 110 for 7 lobes; 2: 22 x lobes - 2, 152 for 7 lobes,
        rounder lobes for big hero clumps), `depth` scales the notches between
        lobes (0.5 = softer, rounder clump), `rough` jitters the vertices. Nothing
        goes below `floor`. One material, one random Tint (+/- tint_var).
        Returns the verts."""
        rng = random.Random(seed) if seed is not None else self.rng
        part = self._leaf_part(rng, radius, loc, lobes, squash, lobe_size, facets, rough, axis, depth)
        verts = self._leaf_floor(part[0], floor)
        t = tint if tint is not None else 1.0 + rng.uniform(-self.tint_var, self.tint_var)
        return self._finish(verts, mat, t, 0.0, face_tint_var=0.015)

    def canopy(self, center, size, mat="leaf", clumps=None, clump_radius=None, density=1.0,
               droop=0.0, seed=None, lobes=(6, 8), squash=0.95, lobe_size=(0.45, 0.65),
               facets=2, rough=0.1, floor=None, inner=True, core=True, flat_bottom=0.75,
               tilt=0.35, bulge=0.45, depth=0.75):
        """A whole crown or bush: fills the ellipsoid of full extents `size` (x, y, z)
        centred on `center` with overlapping leaf clusters, so it reads as one big,
        dense, lumpy cauliflower mass like the kit references.

        Clumps sit just inside the shell (their outer edges on it, so the result
        is about `size`), each turned `tilt` of the
        way from straight up toward the shell's outward normal (0 = all face up).
        They are bigger toward the top and smaller underneath, where the shell is
        pulled up (`flat_bottom` scales the lower half-height). `droop` (0-1) pulls
        rim clumps below the equator down for a heavy, hanging edge. `inner` adds
        a sparse layer at half depth (depth between the outer clumps), `core` one
        big many-lobed filler so no light shows through; `bulge` (x the clump
        radius) is how far the clumps stand out of that filler: higher = more
        distinct clumps with deeper gaps between them. Clumps whose surface is
        wholly covered by earlier ones are skipped and faces buried inside
        another clump are deleted.

        `clump_radius` = (min, max) studs; the default scales with the size, so
        the default clump count (shell area x `density`) is ~14-18 outer clumps
        at any size. `clumps` sets that count. lobes / squash / lobe_size /
        facets / rough / depth go to every clump (`lobes` may be a (min, max)
        range). Each clump gets its own random Tint (+/- tint_var), never one by
        height or facing.

        Triangles: about 150 per clump at facets=2, 110 at facets=1. A 14 x 14 x
        10 crown at the defaults is ~2600 tris, a 7.5 x 7 x 5 bush ~2500. For a
        crown of several masses (one canopy per branch end) pass facets=1,
        core=False, inner=False and clumps=6-9 per mass. Returns all verts."""
        rng = random.Random(seed) if seed is not None else self.rng
        c0 = Vector(center)
        a, b, c = size[0] / 2, size[1] / 2, size[2] / 2
        m = (a + b + c) / 3
        rmin, rmax = clump_radius if clump_radius else (0.3 * m, 0.48 * m)
        ravg = (rmin + rmax) / 2
        if clumps is None:
            p = 1.6
            area = 4 * math.pi * (((a * b) ** p + (a * c) ** p + (b * c) ** p) / 3) ** (1 / p)
            clumps = max(3, round(density * 0.55 * area / (math.pi * ravg * ravg)))
        lo, hi = (lobes, lobes) if isinstance(lobes, int) else lobes
        up = Vector((0, 0, 1))

        # candidate clumps (position, radius, axis): the outer shell on a golden spiral
        cands = []
        golden = math.pi * (3 - math.sqrt(5))
        rot = rng.uniform(0, 2 * math.pi)
        for i in range(clumps):
            z = 1 - 2 * (i + 0.5) / clumps
            ring = math.sqrt(max(0.0, 1 - z * z))
            az = rot + i * golden + rng.uniform(-0.2, 0.2)
            d = Vector((math.cos(az) * ring, math.sin(az) * ring, z))
            t = (d.z + 1) / 2
            r = (rmin + (rmax - rmin) * (0.15 + 0.85 * t)) * rng.uniform(0.88, 1.12)
            cz = c if d.z >= 0 else c * flat_bottom
            inset = r * rng.uniform(0.92, 1.08)  # the clump's outer edge on the shell
            pos = c0 + Vector((d.x * max(a - inset, 0), d.y * max(b - inset, 0), d.z * max(cz - inset, 0)))
            if droop and d.z < 0.35:
                h = math.hypot(d.x, d.y)
                pos.z -= droop * c * h * h * (0.35 - d.z)
            normal = Vector((d.x / max(a, 1e-3), d.y / max(b, 1e-3), d.z / max(cz, 1e-3))).normalized()
            axis = up.lerp(normal, tilt)
            axis.z = max(axis.z, -0.15)
            cands.append((pos, r, axis.normalized()))
        cands.sort(key=lambda prx: -prx[1])
        if inner:
            for i in range(max(1, round(clumps * 0.2))):
                z = rng.uniform(-0.2, 1.0)
                az = rng.uniform(0, 2 * math.pi)
                ring = math.sqrt(max(0.0, 1 - z * z))
                d = Vector((math.cos(az) * ring, math.sin(az) * ring, z))
                cands.append((c0 + Vector((d.x * a * 0.45, d.y * b * 0.45, d.z * c * 0.45)),
                              rmax * rng.uniform(0.95, 1.15), up.lerp(d, 0.4).normalized()))

        # skip clumps whose whole sphere is covered by already accepted ones
        samples = [Vector(s).normalized() for s in
                   ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1),
                    (1, 1, 1), (1, 1, -1), (1, -1, 1), (1, -1, -1),
                    (-1, 1, 1), (-1, 1, -1), (-1, -1, 1), (-1, -1, -1))]
        sink = ravg * (0.55 + bulge)  # the filler sits this far inside the shell
        core_r = (max(a - sink, 0.3 * a), max(b - sink, 0.3 * b), max(c - sink, 0.3 * c))
        solids = []  # (centre, radius) each accepted clump surely fills
        accepted = []
        for pos, r, axis in cands:
            covered = True
            for s in samples:
                q = pos + s * (r * 0.9)
                if core and ((q.x - c0.x) / core_r[0]) ** 2 + ((q.y - c0.y) / core_r[1]) ** 2 + \
                        ((q.z - c0.z) / core_r[2]) ** 2 < 0.4 ** 2:
                    continue
                if not any((q - sc).length < sr for sc, sr in solids):
                    covered = False
                    break
            if covered:
                continue
            accepted.append((pos, r, axis))
            solids.append((pos, r * 0.45))

        groups = []
        if core:  # one big many-lobed filler
            groups.append(self._leaf_part(rng, core_r, c0 - Vector((0, 0, c * 0.1)), 9, 1.0, lobe_size,
                                          2, rough * 0.6))
        for pos, r, axis in accepted:
            groups.append(self._leaf_part(rng, r, pos, rng.randint(lo, hi), squash, lobe_size, facets,
                                          rough, axis, depth))
        for g in groups:
            g[0] = self._leaf_floor(g[0], floor)
        self._leaf_cull(groups, floor)
        out = []
        for g in groups:
            t = 1.0 + rng.uniform(-self.tint_var, self.tint_var)
            out += self._finish(g[0], mat, t, 0.0, face_tint_var=0.015)
        return out

    def flame(self, height, radius, loc=(0, 0, 0), tongues=5):
        """Stylised fire: an outer, mid and core cone cluster with jagged tongues."""
        out = []
        for layer, (mat, s) in enumerate((("fire_outer", 1.0), ("fire_mid", 0.72), ("fire_core", 0.45))):
            for i in range(tongues if layer == 0 else max(2, tongues - 2)):
                a = 2 * math.pi * i / tongues + layer
                off = radius * 0.45 * s if i else 0
                h = height * s * (1.0 if i == 0 else self.rng.uniform(0.55, 0.85))
                p = (loc[0] + math.cos(a) * off, loc[1] + math.sin(a) * off, loc[2])
                out += self.cyl(radius * s * (0.75 if i else 1), 0.0, h, 5, loc=p,
                                rot=(self.rng.uniform(-0.15, 0.15), self.rng.uniform(-0.15, 0.15), a),
                                mat=mat, tint=1.0)
        return out

    def rivet(self, loc, normal_rot=(0, 0, 0), r=0.08, mat="iron_dark"):
        return self.cyl(r, r * 0.55, r * 0.6, 6, loc=loc, rot=normal_rot, mat=mat)

    # -- output ------------------------------------------------------------------

    def finish(self, location=(0, 0, 0), collection=None, mark_asset=True, origin="BOTTOM"):
        """Write the mesh, centre the origin at the bottom, mark as asset."""
        bm = self.bm
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        if origin == "BOTTOM" and bm.verts:
            xs = [v.co.x for v in bm.verts]
            ys = [v.co.y for v in bm.verts]
            zs = [v.co.z for v in bm.verts]
            off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
            bmesh.ops.translate(bm, vec=-off, verts=bm.verts)
        me = bpy.data.meshes.new(self.name)
        bm.to_mesh(me)
        bm.free()
        for m in self.mats:
            me.materials.append(material(m))
        obj = bpy.data.objects.new(self.name, me)
        obj.location = location
        coll = collection or asset_collection(self.name, self.category)
        coll.objects.link(obj)
        obj["flintkit_category"] = self.category
        obj["tris"] = sum(len(p.vertices) - 2 for p in me.polygons)
        dims = obj.dimensions
        obj["studs"] = f"{dims.x:.1f} x {dims.y:.1f} x {dims.z:.1f}"
        if mark_asset:
            obj.asset_mark()
            obj.asset_data.tags.new(self.category)
            obj.asset_data.description = f"Flintborn {self.category}: {self.name} ({obj['studs']} studs)"
        return obj


# ---------------------------------------------------------------------------
# File and scene helpers
# ---------------------------------------------------------------------------


def reset_file():
    """Empty the factory scene (no cube, light or camera)."""
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


def asset_collection(name, category):
    root = bpy.data.collections.get("Assets")
    if root is None:
        root = bpy.data.collections.new("Assets")
        bpy.context.scene.collection.children.link(root)
    cat = bpy.data.collections.get(category)
    if cat is None:
        cat = bpy.data.collections.new(category)
        root.children.link(cat)
    return cat


def layout_row(objs, spacing=4.0):
    """Lay assets side by side along +X for the file overview."""
    x = 0.0
    for o in objs:
        w = o.dimensions.x
        o.location = (x + w / 2, 0, 0)
        x += w + spacing


def save(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)


# ---------------------------------------------------------------------------
# Rendering: reference-sheet look (warm grey studio, soft key light)
# ---------------------------------------------------------------------------

BG_HEX = "#D8D4CD"
GROUND_ALBEDO = 0.7
DEFAULT_AZIMUTH = -22  # degrees; camera swung toward the asset's left side
DEFAULT_ELEVATION = 20


def _studio(scene):
    scene.render.engine = "BLENDER_EEVEE"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.render.film_transparent = False
    world = scene.world or bpy.data.worlds.new("FB_Studio")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    if "FB_Mix" not in nt.nodes:
        out = nt.nodes.get("World Output")
        bg = nt.nodes.get("Background")
        bg.inputs["Color"].default_value = (*hex_rgb(BG_HEX), 1)  # what the camera sees
        bg.inputs["Strength"].default_value = 1.0
        amb = nt.nodes.new("ShaderNodeBackground")  # what lights the asset
        amb.inputs["Color"].default_value = (*hex_rgb("#C9D2DC"), 1)
        amb.inputs["Strength"].default_value = 0.75
        lp = nt.nodes.new("ShaderNodeLightPath")
        mix = nt.nodes.new("ShaderNodeMixShader")
        mix.name = "FB_Mix"
        nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
        nt.links.new(amb.outputs[0], mix.inputs[1])
        nt.links.new(bg.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs["Surface"])
    if "FB_Key" not in bpy.data.objects:
        key = bpy.data.objects.new("FB_Key", bpy.data.lights.new("FB_Key", "SUN"))
        key.data.energy = 3.2
        key.data.angle = math.radians(12)
        key.rotation_euler = (math.radians(50), 0, math.radians(-40))
        scene.collection.objects.link(key)
        fill = bpy.data.objects.new("FB_Fill", bpy.data.lights.new("FB_Fill", "SUN"))
        fill.data.energy = 0.8
        fill.data.angle = math.radians(30)
        fill.rotation_euler = (math.radians(70), 0, math.radians(150))
        scene.collection.objects.link(fill)
    if "FB_Ground" not in bpy.data.objects:
        me = bpy.data.meshes.new("FB_Ground")
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=500)
        bm.to_mesh(me)
        bm.free()
        g = bpy.data.objects.new("FB_Ground", me)
        gm = bpy.data.materials.new("FB_GroundMat")
        gm.use_nodes = True
        # Darker than the backdrop so that, once lit, the floor matches it and only
        # the contact shadow reads.
        gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (
            *(c * GROUND_ALBEDO for c in hex_rgb(BG_HEX)), 1)
        gm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 1.0
        me.materials.append(gm)
        scene.collection.objects.link(g)
    if "FB_Cam" not in bpy.data.objects:
        cam = bpy.data.objects.new("FB_Cam", bpy.data.cameras.new("FB_Cam"))
        cam.data.lens = 50
        scene.collection.objects.link(cam)
        scene.camera = cam


def frame(obj, azimuth=DEFAULT_AZIMUTH, elevation=DEFAULT_ELEVATION, margin=1.1):
    """Point the studio camera at obj from the front-left (front = -Y)."""
    scene = bpy.context.scene
    cam = bpy.data.objects["FB_Cam"]
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    centre = sum(corners, Vector()) / 8
    radius = max((c - centre).length for c in corners)
    fov = cam.data.angle
    aspect = scene.render.resolution_x / scene.render.resolution_y
    fit = fov / 2 if aspect >= 1 else math.atan(math.tan(fov / 2) * aspect)
    dist = radius * margin / math.sin(fit)
    az, el = math.radians(azimuth), math.radians(elevation)
    direction = Vector((math.sin(az), -math.cos(az), math.tan(el))).normalized()
    cam.location = centre + direction * dist
    cam.rotation_euler = (centre - cam.location).to_track_quat("-Z", "Y").to_euler()
    ground = bpy.data.objects["FB_Ground"]
    ground.location = (centre.x, centre.y, min(c.z for c in corners))


def render_asset(obj, path, res=(512, 384), azimuth=DEFAULT_AZIMUTH, elevation=DEFAULT_ELEVATION, samples=32):
    """Render one asset alone in the studio to `path` (PNG)."""
    scene = bpy.context.scene
    _studio(scene)
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    try:
        scene.eevee.taa_render_samples = samples
    except AttributeError:
        pass
    hidden = []
    for o in scene.objects:
        if o.type == "MESH" and o is not obj and o.name != "FB_Ground":
            if not o.hide_render:
                hidden.append(o)
                o.hide_render = True
    frame(obj, azimuth, elevation)
    scene.render.filepath = path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.render.render(write_still=True)
    for o in hidden:
        o.hide_render = False
    return path


def render_sheet(objs, path, cols=4, cell=(384, 288), keep_cells=True, **kw):
    """Render each asset and tile them in reading order into one PNG contact sheet,
    matching the reference sheets' grid. Individual cells are kept next to it."""
    base, _ = os.path.splitext(path)
    cell_paths = []
    for i, o in enumerate(objs):
        p = f"{base}_cells/{i + 1:02d}_{o.name}.png"
        render_asset(o, p, res=cell, **kw)
        cell_paths.append(p)
    rows = math.ceil(len(objs) / cols)
    w, h = cell
    sheet = np.ones((rows * h, cols * w, 4), dtype=np.float32)
    sheet[..., :3] = [int(BG_HEX[i:i + 2], 16) / 255 for i in (1, 3, 5)]  # empty cells match the backdrop (sRGB, as PNG pixels are)
    for i, p in enumerate(cell_paths):
        img = bpy.data.images.load(p, check_existing=False)
        px = np.array(img.pixels[:], dtype=np.float32).reshape(img.size[1], img.size[0], 4)
        r, c = divmod(i, cols)
        y0 = (rows - 1 - r) * h  # Blender images are bottom-up
        sheet[y0 : y0 + h, c * w : c * w + w] = px[:h, :w]
        bpy.data.images.remove(img)
    out = bpy.data.images.new("FB_Sheet", cols * w, rows * h, alpha=True)
    out.pixels = sheet.ravel()
    out.filepath_raw = path
    out.file_format = "PNG"
    out.save()
    bpy.data.images.remove(out)
    if not keep_cells:
        for p in cell_paths:
            os.remove(p)
    return path
