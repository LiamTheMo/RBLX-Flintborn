"""Flintkit: shared modelling, material and render helpers for Flintborn assets.

Every asset script imports this module so all sheets share one palette, one
shape language and one camera. Conventions:

- 1 Blender unit = 1 Roblox stud. A Roblox character is ~5.5 studs tall.
- Each asset is ONE mesh object (multi-material), origin at the bottom centre,
  front facing -Y, marked as a Blender asset in its own collection.
- Shading is flat (faceted). Every mesh carries a "Tint" colour attribute that
  the shared materials multiply into the base colour, giving each plank, post
  or stone its own slight hand-painted variation.

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

EMISSIVE = {k for k, v in PALETTE.items() if v[3] > 0}
# Foliage and ground greens: a weak specular so the sky's sheen does not wash the
# saturated greens out toward grey.
LOW_SPEC = {"leaf", "leaf_light", "leaf_dark", "pine", "pine_dark", "grass_ground", "grass_light",
            "grass_dark"}


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
    hexcol, rough, metal, emit = PALETTE[name]
    rgb = hex_rgb(hexcol)
    mat = bpy.data.materials.new(mname)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if name in LOW_SPEC and "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.2
    if name in EMISSIVE:
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
