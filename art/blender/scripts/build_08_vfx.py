"""Sheet 08: VFX. Renders the Roblox particle textures, previews every VFX kind on
small stand-in bases, and exports the VFX catalog.

    "D:/Steam/steamapps/common/Blender/blender.exe" --background --factory-startup \
        --python art/blender/scripts/build_08_vfx.py

Outputs
- art/vfx/textures/<name>.png      one per texture named in vfx.KINDS (transparent RGBA)
- art/vfx/vfx_catalog.json         vfx.catalog()
- art/blender/renders/08_vfx.png        stand-in bases with realize()d sockets, studio light
- art/blender/renders/08_vfx_dim.png    the same with the studio dimmed so the lights read
- art/blender/renders/08_vfx_textures.png  contact sheet of the textures on a dark ground

Every texture is low-poly geometry with baked, flat-shaded emissive vertex colours
(one shared material), rendered orthographically by Eevee. The facet shading is
computed in Python from a fixed key direction, so the stylised look is
deterministic and independent of scene lights.
"""

import importlib
import json
import math
import os
import random
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Euler, Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
BLENDER_DIR = os.path.dirname(HERE)
ART = os.path.dirname(BLENDER_DIR)
sys.path.insert(0, os.path.join(BLENDER_DIR, "lib"))
import flintkit as fk  # noqa: E402
import vfx  # noqa: E402

importlib.reload(fk)
importlib.reload(vfx)

TEX_DIR = os.path.join(ART, "vfx", "textures")
VFX_DIR = os.path.join(ART, "vfx")
RENDERS = os.path.join(BLENDER_DIR, "renders")
PI = math.pi
KEY = Vector((-0.45, -0.78, 0.52)).normalized()  # baked facet light: upper left, toward camera

lin = fk.hex_rgb


def mix(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def smooth(e0, e1, x):
    t = min(max((x - e0) / (e1 - e0), 0.0), 1.0)
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------------------
# FX mesh builder: bmesh + per-corner RGBA ("Col"), emission-only material
# ---------------------------------------------------------------------------


def fx_material():
    mat = bpy.data.materials.get("FX_VC")
    if mat:
        return mat
    mat = bpy.data.materials.new("FX_VC")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "Col"
    attr.attribute_type = "GEOMETRY"
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 1.0
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(attr.outputs["Color"], em.inputs["Color"])
    nt.links.new(attr.outputs["Alpha"], mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "DITHERED"
    return mat


class FX:
    def __init__(self, seed=1):
        self.bm = bmesh.new()
        self.col = self.bm.loops.layers.float_color.new("Col")
        self.rng = random.Random(seed)

    def paint(self, verts, rgb, alpha=1.0, shade=(0.8, 0.3), key=KEY):
        """Colour the faces of `verts`: flat facet shade x rgb (tuple or fn(co)),
        alpha (float or fn(vert)) per corner so it interpolates smoothly."""
        bm = self.bm
        bm.normal_update()
        faces = set()
        for v in verts:
            faces.update(v.link_faces)
        for f in faces:
            f.smooth = False
            s = shade[0] + shade[1] * max(0.0, f.normal.dot(key))
            for lp in f.loops:
                c = rgb(lp.vert.co) if callable(rgb) else rgb
                a = alpha(lp.vert) if callable(alpha) else alpha
                lp[self.col] = (c[0] * s, c[1] * s, c[2] * s, max(0.0, min(1.0, a)))
        return verts

    # -- primitives (built in the XZ plane, camera looks +Y from -Y) --------

    def tongue(self, base, h, r, lean=0.0, wob=0.0, wob_phase=0.0, sides=5, rot=0.0, depth=1.0,
               prof=None, tip_curl=0.0):
        """Faceted flame tongue: a bulging, tapering ring stack with a curling tip."""
        bm = self.bm
        prof = prof or [(0.0, 0.62), (0.13, 1.0), (0.32, 0.92), (0.52, 0.68), (0.7, 0.42),
                        (0.86, 0.2), (1.0, 0.0)]
        bx, by, bz = base
        rings = []
        tip = None
        for t, m in prof:
            off = lean * h * t * t + wob * h * math.sin(PI * 1.6 * t + wob_phase) * t + tip_curl * h * t ** 4
            c = Vector((bx + off, by, bz + h * t))
            if m <= 0:
                tip = bm.verts.new(c)
                continue
            ring = []
            for i in range(sides):
                a = 2 * PI * i / sides + rot
                ring.append(bm.verts.new(c + Vector((math.cos(a) * r * m, math.sin(a) * r * m * depth, 0))))
            rings.append(ring)
        # rounded bottom
        bottom = bm.verts.new(Vector((bx, by, bz - r * 0.35)))
        for i in range(sides):
            j = (i + 1) % sides
            bm.faces.new((bottom, rings[0][j], rings[0][i]))
        for ra, rb in zip(rings, rings[1:]):
            for i in range(sides):
                j = (i + 1) % sides
                bm.faces.new((ra[i], ra[j], rb[j], rb[i]))
        for i in range(sides):
            j = (i + 1) % sides
            bm.faces.new((rings[-1][i], rings[-1][j], tip))
        return [v for r_ in rings for v in r_] + [tip, bottom]

    def diamond(self, c, rx, rz, depth=0.6, sides=4, rot=0.0):
        """Elongated bipyramid (spark / fragment)."""
        bm = self.bm
        c = Vector(c)
        ring = [bm.verts.new(c + Vector((math.cos(2 * PI * i / sides + rot) * rx, math.sin(2 * PI * i / sides + rot) * rx * depth, 0)))
                for i in range(sides)]
        top = bm.verts.new(c + Vector((0, 0, rz)))
        bot = bm.verts.new(c + Vector((0, 0, -rz * 0.6)))
        for i in range(sides):
            j = (i + 1) % sides
            bm.faces.new((ring[i], ring[j], top))
            bm.faces.new((ring[j], ring[i], bot))
        return ring + [top, bot]

    def ico(self, c, r, sub=1, jitter=0.0, squash=(1, 1, 1), rot=0.0):
        vs = bmesh.ops.create_icosphere(self.bm, subdivisions=sub, radius=1.0)["verts"]
        R = Euler((rot * 0.7, rot, rot * 1.3)).to_matrix()
        for v in vs:
            j = 1.0 + self.rng.uniform(-jitter, jitter)
            p = R @ v.co
            v.co = Vector((p.x * squash[0], p.y * squash[1], p.z * squash[2])) * r * j + Vector(c)
        return vs

    def disc(self, c, radius, rings=12, segs=16, lift=0.0, rot=0.0):
        """Concentric-ring disc in the XZ plane facing -Y; centre lifted toward the camera."""
        bm = self.bm
        c = Vector(c)
        centre = bm.verts.new(c + Vector((0, -lift, 0)))
        prev = None
        allv = [centre]
        for k in range(1, rings + 1):
            rr = radius * k / rings
            ring = [bm.verts.new(c + Vector((math.cos(2 * PI * i / segs + rot) * rr,
                                             -lift * (1 - k / rings),
                                             math.sin(2 * PI * i / segs + rot) * rr))) for i in range(segs)]
            for i in range(segs):
                j = (i + 1) % segs
                if prev is None:
                    bm.faces.new((centre, ring[j], ring[i]))
                else:
                    bm.faces.new((prev[i], prev[j], ring[j], ring[i]))
            prev = ring
            allv += ring
        return allv

    def star(self, c, outer, inner, lift=0.3, inner_lift=0.06):
        """Faceted star: outer tips (list of (x, z)), inner notches between them, raised centre."""
        bm = self.bm
        c = Vector(c)
        n = len(outer)
        cen = bm.verts.new(c + Vector((0, -lift, 0)))
        tips = [bm.verts.new(c + Vector((x, 0, z))) for x, z in outer]
        notch = []
        for i in range(n):
            a0 = math.atan2(outer[i][1], outer[i][0])
            a1 = math.atan2(outer[(i + 1) % n][1], outer[(i + 1) % n][0])
            if a1 < a0:
                a1 += 2 * PI
            a = (a0 + a1) / 2
            notch.append(bm.verts.new(c + Vector((math.cos(a) * inner, -inner_lift, math.sin(a) * inner))))
        for i in range(n):
            bm.faces.new((cen, notch[i - 1], tips[i]))
            bm.faces.new((cen, tips[i], notch[i]))
        return [cen] + tips + notch

    def arc_strip(self, c, R, a0, a1, w, segs=18, wobble=0.0, lift=0.03, phase=0.0):
        """Tapered crescent band along a circle arc (angles in degrees) in the XZ plane."""
        bm = self.bm
        c = Vector(c)
        mids, outs, ins = [], [], []
        for k in range(segs + 1):
            t = k / segs
            a = math.radians(a0 + (a1 - a0) * t)
            rr = R * (1 + wobble * math.sin(t * 7 + phase))
            ww = w * math.sin(PI * t) ** 0.7 + 1e-3
            d = Vector((math.cos(a), 0, math.sin(a)))
            outs.append(bm.verts.new(c + d * (rr + ww / 2)))
            ins.append(bm.verts.new(c + d * (rr - ww / 2)))
            mids.append(bm.verts.new(c + d * rr + Vector((0, -lift, 0))))
        for k in range(segs):
            bm.faces.new((ins[k], mids[k], mids[k + 1], ins[k + 1]))
            bm.faces.new((mids[k], outs[k], outs[k + 1], mids[k + 1]))
        return outs + ins + mids

    def finish(self, name, coll, loc=(0, 0, 0)):
        me = bpy.data.meshes.new(name)
        self.bm.to_mesh(me)
        self.bm.free()
        me.materials.append(fx_material())
        obj = bpy.data.objects.new(name, me)
        obj.location = loc
        coll.objects.link(obj)
        if hasattr(obj, "visible_shadow"):
            obj.visible_shadow = False
        return obj


# ---------------------------------------------------------------------------
# Flames
# ---------------------------------------------------------------------------

C_OUT, C_TIP = lin("#F2601C"), lin("#D8401A")
C_MID, C_MID_TIP = lin("#FFB232"), lin("#FF8F28")
C_CORE, C_CORE_HI = lin("#FFDA4E"), lin("#FFF3B0")


def grad(c0, c1, z0, z1):
    return lambda co: mix(c0, c1, smooth(z0, z1, co.z))


def flame_frame(fx, cx, cz, t):
    """One flipbook frame (t in [0,1), loops seamlessly), cell centred on (cx, cz), cell
    half-size 1. Layers are pushed toward the camera (-Y): outer, mid, core."""
    z0 = cz - 0.86

    def osc(k, ph, amp=1.0):
        return amp * math.sin(2 * PI * (k * t + ph))

    fade = lambda v: smooth(z0 - 0.12, z0 + 0.2, v.co.z)  # soft root  # noqa: E731
    layers = [
        # y, colour gradient, tongues: (x, r, H, lean, k, phase, curl)
        (0.0, grad(C_OUT, C_TIP, z0 + 0.7, z0 + 1.6), [
            (0.0, 0.38, 1.46, 0.02, 1, 0.00, 0.08), (-0.27, 0.25, 1.0, -0.1, 2, 0.30, -0.06),
            (0.28, 0.24, 1.1, 0.1, 1, 0.55, 0.07), (-0.45, 0.15, 0.62, -0.18, 2, 0.75, -0.04),
            (0.46, 0.14, 0.56, 0.19, 1, 0.15, 0.04)]),
        (-1.0, grad(C_MID, C_MID_TIP, z0 + 0.3, z0 + 1.25), [
            (0.02, 0.32, 1.24, 0.0, 1, 0.10, -0.06), (-0.22, 0.22, 0.84, -0.08, 2, 0.45, -0.05),
            (0.23, 0.21, 0.88, 0.08, 1, 0.70, 0.05)]),
        (-2.0, grad(C_CORE_HI, C_CORE, z0 + 0.1, z0 + 0.85), [
            (0.0, 0.25, 0.92, 0.0, 1, 0.25, 0.04), (-0.15, 0.16, 0.6, -0.08, 2, 0.6, -0.03),
            (0.16, 0.16, 0.64, 0.08, 1, 0.9, 0.03)]),
    ]
    for li, (y, col, tongues) in enumerate(layers):
        for ti, (x, r, H, lean, k, ph, curl) in enumerate(tongues):
            h = H * (1 + osc(k, ph, 0.18))
            ln = lean + osc(k, ph + 0.25, 0.1)
            xx = x + osc(1, ph + 0.5, 0.025)
            vs = fx.tongue((cx + xx, y, z0 + 0.05), h, r * (1 + osc(k, ph + 0.4, 0.05)), lean=ln,
                           wob=0.07, wob_phase=2 * PI * (t + ph), sides=5, rot=0.3 + ti * 1.1 + li * 0.5,
                           tip_curl=curl + osc(1, ph + 0.1, 0.1))
            fx.paint(vs, col, fade, shade=(0.8, 0.32))
        # base blob unifying the root
        bl = fx.ico((cx, y, z0 + 0.12), 1.0, sub=1, squash=(0.42 - li * 0.08, 0.3, 0.24 - li * 0.03),
                    rot=0.4 + li)
        fx.paint(bl, col, fade, shade=(0.8, 0.32))
    # detached fragments: split off the tips, rise and shrink away (seamless: size 0 at wrap)
    frags = [(0.0, -1e-3 + 0.0, 0.17, 0.98, 0.72, 0.05, C_OUT),
             (1 / 3, -1e-3, 0.13, 0.72, 0.6, -0.3, C_OUT),
             (2 / 3, -1e-3, 0.14, 0.78, 0.62, 0.32, C_OUT),
             (0.17, -1.0, 0.1, 0.7, 0.45, 0.12, C_MID),
             (0.6, -1.0, 0.09, 0.62, 0.42, -0.15, C_MID)]
    for ph, y, s, zs, rise, x0, c in frags:
        u = (t + ph) % 1.0
        size = s * math.sin(PI * u) ** 0.8
        if size < 0.012:
            continue
        x = cx + x0 + x0 * 0.6 * u + 0.04 * math.sin(2 * PI * u)
        z = z0 + zs + rise * u
        vs = fx.diamond((x, y + 0.3, z), size * 0.62, size * 1.5, depth=0.8, sides=5, rot=ph * 5)
        fx.paint(vs, c, 1.0, shade=(0.82, 0.3))


def flame3d(fx, loc, h, r, seed=1, toward=(-0.38, -0.92), n=6):
    """Camera-agnostic 3D flame for the preview bases: outer ring of curling tongues,
    a mid layer and a pale core nudged toward the camera (same style as the sheets)."""
    rng = random.Random(seed)
    x0, y0, z0 = loc
    fw = Vector((toward[0], toward[1], 0)).normalized()
    f_out = grad(C_OUT, C_TIP, z0 + h * 0.3, z0 + h)
    f_mid = grad(C_MID, C_MID_TIP, z0 + h * 0.2, z0 + h * 0.7)
    f_core = grad(C_CORE, C_CORE_HI, z0, z0 + h * 0.3)

    def tongue_dir(base, hh, rr, d, curl, col, sides=5):
        vs = fx.tongue((0, 0, 0), hh, rr, lean=curl, wob=0.05, wob_phase=rng.uniform(0, 6), sides=sides,
                       rot=rng.uniform(0, 6))
        ang = math.atan2(d.y, d.x)
        bmesh.ops.rotate(fx.bm, verts=vs, cent=(0, 0, 0), matrix=Matrix.Rotation(ang, 3, "Z"))
        bmesh.ops.translate(fx.bm, verts=vs, vec=Vector(base))
        fx.paint(vs, col, 1.0, shade=(0.78, 0.34))

    tongue_dir((x0, y0, z0), h, r * 0.62, Vector((1, 0, 0)), 0.05, f_out, 6)
    for i in range(n):
        a = 2 * PI * i / n + rng.uniform(-0.25, 0.25)
        d = Vector((math.cos(a), math.sin(a), 0))
        tongue_dir((x0 + d.x * r * 0.5, y0 + d.y * r * 0.5, z0), h * rng.uniform(0.5, 0.8),
                   r * rng.uniform(0.36, 0.46), d, rng.uniform(0.25, 0.45), f_out)
    c1 = Vector((x0, y0, z0)) + fw * r * 0.52
    for i in range(3):
        a = 2 * PI * i / 3 + 0.4
        d = Vector((math.cos(a), math.sin(a), 0))
        tongue_dir(c1 + d * r * 0.2, h * rng.uniform(0.58, 0.75), r * 0.36, d, 0.12, f_mid)
    c2 = Vector((x0, y0, z0)) + fw * r * 0.8
    for i in range(2):
        d = Vector((math.cos(i * PI + 0.3), math.sin(i * PI + 0.3), 0))
        tongue_dir(c2 + d * r * 0.12, h * rng.uniform(0.4, 0.5), r * 0.26, d, 0.06, f_core)
    # a couple of spark diamonds hovering above the tips (as on the reference sheets)
    for i in range(2):
        a = rng.uniform(0, 2 * PI)
        p = (x0 + math.cos(a) * r * 0.7, y0 + math.sin(a) * r * 0.7, z0 + h * rng.uniform(1.05, 1.3))
        vs = fx.diamond(p, r * 0.07, r * 0.17, depth=1.0, sides=4, rot=0.7)
        fx.paint(vs, C_CORE, 1.0, shade=(0.85, 0.25))


# ---------------------------------------------------------------------------
# Texture scene
# ---------------------------------------------------------------------------


def tex_scene():
    sc = bpy.data.scenes.get("FX_Tex") or bpy.data.scenes.new("FX_Tex")
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.film_transparent = True
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.image_settings.color_depth = "8"
    sc.render.resolution_percentage = 100
    sc.render.filter_size = 1.2
    w = bpy.data.worlds.get("FX_Black") or bpy.data.worlds.new("FX_Black")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0
    sc.world = w
    if "FX_TexCam" not in bpy.data.objects:
        cam = bpy.data.objects.new("FX_TexCam", bpy.data.cameras.new("FX_TexCam"))
        cam.data.type = "ORTHO"
        cam.location = (0, -50, 0)
        cam.rotation_euler = (PI / 2, 0, 0)
        cam.data.clip_end = 200
        sc.collection.objects.link(cam)
        sc.camera = cam
    return sc


def tex_clear(sc):
    for o in list(sc.collection.objects):
        if o.name != "FX_TexCam":
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me is not None and me.users == 0:
                bpy.data.meshes.remove(me)


def postprocess(path, cells=1):
    """Zero a 2 px border round each (flipbook) cell and bleed colour into fully
    transparent pixels, so bilinear filtering in Roblox never pulls in black."""
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    a = px[..., 3]
    step = w // cells
    for k in range(cells + 1):
        e = k * step
        a[:, max(0, e - 2):min(w, e + 2)] = 0
        a[max(0, e - 2):min(h, e + 2), :] = 0
    rgb = px[..., :3] * a[..., None]
    wt = a.copy()
    for _ in range(10):
        rgb = (rgb + np.roll(rgb, 1, 0) + np.roll(rgb, -1, 0) + np.roll(rgb, 1, 1) + np.roll(rgb, -1, 1)) / 5
        wt = (wt + np.roll(wt, 1, 0) + np.roll(wt, -1, 0) + np.roll(wt, 1, 1) + np.roll(wt, -1, 1)) / 5
    mean = (px[..., :3] * a[..., None]).sum((0, 1)) / max(a.sum(), 1e-6)
    fill = np.where(wt[..., None] > 1e-4, rgb / np.maximum(wt[..., None], 1e-6), mean)
    empty = a < 0.5 / 255
    px[..., :3] = np.where(empty[..., None], fill, px[..., :3])
    px[..., 3] = a
    img.pixels = px.ravel()
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


def render_tex(name, build, size, ortho=2.0, samples=96, cells=1):
    sc = tex_scene()
    tex_clear(sc)
    fx = FX(seed=sum(map(ord, name)))
    build(fx)
    fx.finish("FX_" + name, sc.collection)
    sc.camera.data.ortho_scale = ortho
    sc.render.resolution_x = sc.render.resolution_y = size
    sc.eevee.taa_render_samples = samples
    path = os.path.join(TEX_DIR, name + ".png")
    os.makedirs(TEX_DIR, exist_ok=True)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True, scene=sc.name)
    postprocess(path, cells)
    print(f"[08] texture {name} {size}px")
    return path


# -- texture builders ---------------------------------------------------------

WHITE = (1.0, 1.0, 1.0)


def halo(fx, radius, peak, power=2.0, y=0.3, color=WHITE, segs=20):
    vs = fx.disc((0, y, 0), radius, rings=18, segs=segs)
    fx.paint(vs, color, lambda v: peak * (1 - min(1.0, Vector((v.co.x, v.co.z)).length / radius)) ** power,
             shade=(1.0, 0.0))


def build_fire(fx):
    for i in range(16):
        r, c = divmod(i, 4)
        flame_frame(fx, (c - 1.5) * 2, (1.5 - r) * 2, i / 16)


def build_spark(fx):
    halo(fx, 0.7, 0.3, 2.4)
    vs = fx.star((0, 0, 0), [(0, 0.9), (-0.46, 0), (0, -0.9), (0.46, 0)], 0.25, lift=0.4, inner_lift=0.1)
    fx.paint(vs, WHITE, 1.0, shade=(0.66, 0.42))


def build_ember(fx):
    halo(fx, 0.95, 0.55, 1.8)
    pts = [(math.cos(2 * PI * i / 8 + PI / 8) * 0.34, math.sin(2 * PI * i / 8 + PI / 8) * 0.34) for i in range(8)]
    vs = fx.star((0, 0, 0), pts, 0.3, lift=0.2, inner_lift=0.0)
    fx.paint(vs, WHITE, 1.0, shade=(0.8, 0.25))


def build_glow(fx):
    vs = fx.disc((0, 0, 0), 0.97, rings=28, segs=24)
    fx.paint(vs, WHITE, lambda v: (1 - min(1.0, Vector((v.co.x, v.co.z)).length / 0.97)) ** 2.3, shade=(1.0, 0.0))


def build_rune(fx):
    blue = lin("#BFE6F2")
    pale = lin("#E8F8FD")
    halo(fx, 0.95, 0.38, 2.0, color=blue)
    # lozenge glyph outline (as carved on the rune stones)
    for k, (R, wd) in enumerate(((0.62, 0.075), (0.36, 0.06))):
        pts = [(0, R), (-R * 0.78, 0), (0, -R), (R * 0.78, 0), (0, R)]
        for (x1, z1), (x2, z2) in zip(pts, pts[1:]):
            d = Vector((x2 - x1, 0, z2 - z1))
            L = d.length + wd
            vs = bmesh.ops.create_cube(fx.bm, size=1.0)["verts"]
            bmesh.ops.scale(fx.bm, vec=(L, 0.06, wd), verts=vs)
            bmesh.ops.rotate(fx.bm, verts=vs, cent=(0, 0, 0),
                             matrix=Matrix.Rotation(-math.atan2(d.z, d.x), 3, "Y"))
            bmesh.ops.translate(fx.bm, vec=((x1 + x2) / 2, -0.1 - k * 0.05, (z1 + z2) / 2), verts=vs)
            fx.paint(vs, blue, 0.95, shade=(0.85, 0.2))
    vs = fx.star((0, -0.4, 0), [(0, 0.28), (-0.17, 0), (0, -0.28), (0.17, 0)], 0.05, lift=0.15)
    fx.paint(vs, pale, 1.0, shade=(0.85, 0.2))


def build_smoke(fx):
    puffs = [(0.0, -0.05, 0.47), (-0.36, -0.16, 0.33), (0.37, -0.12, 0.34), (-0.16, 0.31, 0.34),
             (0.21, 0.27, 0.32), (0.03, -0.38, 0.3), (-0.5, 0.12, 0.2), (0.52, 0.16, 0.19), (0.0, 0.52, 0.22)]
    grey = lin("#F4F2F0")
    for i, (x, z, r) in enumerate(puffs):
        c = Vector((x, fx.rng.uniform(-0.2, 0.2), z))
        vs = fx.ico(c, r, sub=1, jitter=0.09, rot=i * 0.7)

        def alpha(v, c=c, r=r):
            facing = max(0.0, -(v.co - c).normalized().y)
            edge = smooth(0.0, 0.6, facing)
            border = smooth(0.0, 0.18, 0.98 - Vector((v.co.x, v.co.z)).length)
            return 0.95 * edge * border

        fx.paint(vs, grey, alpha, shade=(0.6, 0.45))


def build_mist(fx):
    rng = fx.rng
    for i in range(16):
        a = rng.uniform(0, 2 * PI)
        d = rng.uniform(0, 0.4) * (1 if i else 0)
        c = Vector((math.cos(a) * d, rng.uniform(-0.3, 0.3), math.sin(a) * d * 0.75))
        r = rng.uniform(0.32, 0.46) * (1.3 if i == 0 else 1)
        vs = fx.ico(c, r, sub=2, jitter=0.05, rot=i)

        def alpha(v, c=c):
            facing = max(0.0, -(v.co - c).normalized().y)
            border = smooth(0.0, 0.45, 0.97 - Vector((v.co.x, v.co.z)).length)
            return 0.2 * smooth(0.0, 1.0, facing) ** 1.8 * border

        fx.paint(vs, WHITE, alpha, shade=(0.92, 0.1))


def build_splash(fx):
    rng = fx.rng
    org = Vector((0, 0, -0.8))
    # crown: a low splash mound, an arc of big droplets thrown up and out, spray dots
    for i in range(5):
        c = org + Vector(((i - 2) * 0.17, 0.1, 0.1 + 0.05 * (2 - abs(i - 2))))
        vs = fx.ico(c, 0.16 - 0.025 * abs(i - 2), sub=1, jitter=0.12, squash=(1.2, 0.8, 0.75), rot=i)
        fx.paint(vs, WHITE, 0.95, shade=(0.62, 0.42))
    n = 14
    for i in range(n):
        th = math.radians(-68 + 136 * (i + rng.uniform(0.2, 0.8)) / n)
        d = rng.uniform(0.55, 1.05) + 0.35 * math.cos(th)
        dirv = Vector((math.sin(th), 0, math.cos(th)))
        c = org + dirv * d
        c.x = max(-0.85, min(0.85, c.x))
        c.z = max(-0.85, min(0.85, c.z))
        r = max(0.05, 0.15 * (1.2 - d / 1.6)) * rng.uniform(0.8, 1.15)
        vs = bmesh.ops.create_icosphere(fx.bm, subdivisions=1, radius=r)["verts"]
        for v in vs:
            if v.co.z < 0:
                v.co.z *= 2.1  # tail trails back toward the impact
        q = dirv.to_track_quat("Z", "Y").to_matrix()
        bmesh.ops.rotate(fx.bm, verts=vs, cent=(0, 0, 0), matrix=q)
        bmesh.ops.translate(fx.bm, verts=vs, vec=c)
        fx.paint(vs, WHITE, 0.97, shade=(0.62, 0.42))
    for i in range(10):
        c = (rng.uniform(-0.8, 0.8), 0.0, rng.uniform(-0.5, 0.85))
        vs = fx.ico(c, rng.uniform(0.018, 0.034), sub=0)
        fx.paint(vs, WHITE, 0.9, shade=(0.8, 0.2))


def build_foam(fx):
    rng = fx.rng
    halo(fx, 0.96, 0.1, 1.6, y=0.4, segs=14)
    arcs = [(0.62, 15, 205, 0.13, 0.0), (0.44, 150, 385, 0.11, 1.0), (0.79, 225, 335, 0.075, 2.0),
            (0.27, -40, 130, 0.09, 3.0), (0.83, 40, 115, 0.06, 4.0)]
    for R, a0, a1, w, ph in arcs:
        vs = fx.arc_strip((0, 0, 0), R, a0, a1, w, segs=22, wobble=0.045, phase=ph)
        fx.paint(vs, WHITE, 1.0, shade=(0.78, 0.28))
    for i in range(14):  # bubbles along the bands
        R, a0, a1, w, _ = arcs[i % len(arcs)]
        a = math.radians(rng.uniform(a0, a1))
        rr = R + rng.uniform(-1, 1) * w * 1.4
        c = (math.cos(a) * rr, -0.02, math.sin(a) * rr)
        vs = fx.ico(c, rng.uniform(0.025, 0.055), sub=1, squash=(1, 0.4, 1))
        fx.paint(vs, WHITE, 1.0, shade=(0.8, 0.25))


def build_dust(fx):
    halo(fx, 0.92, 0.42, 2.0)
    pts = [(math.cos(2 * PI * i / 6) * 0.3, math.sin(2 * PI * i / 6) * 0.3) for i in range(6)]
    vs = fx.star((0, 0, 0), pts, 0.27, lift=0.15, inner_lift=0.0)
    fx.paint(vs, WHITE, 0.92, shade=(0.88, 0.15))


TEX_BUILDERS = {
    "fire_flipbook_4x4": (build_fire, 8.0, 128),
    "smoke_puff": (build_smoke, 2.0, 1024),
    "spark_diamond": (build_spark, 2.0, 1024),
    "ember_dot": (build_ember, 2.0, 1024),
    "glow_soft": (build_glow, 2.0, 1024),
    "rune_mote": (build_rune, 2.0, 1024),
    "mist_soft": (build_mist, 2.0, 1024),
    "splash_droplets": (build_splash, 2.0, 256),
    "foam_patch": (build_foam, 2.0, 1024),
    "dust_mote": (build_dust, 2.0, 1024),
}


def render_textures():
    names = sorted({e["texture"] for k in vfx.KINDS.values() for e in k["emitters"]})
    missing = set(names) - set(TEX_BUILDERS)
    assert not missing, f"no builder for {missing}"
    paths = {}
    for n in names:
        build, ortho, samples = TEX_BUILDERS[n]
        info = vfx.TEXTURES[n]
        paths[n] = render_tex(n, build, info["size"], ortho, samples, cells=4 if n.endswith("4x4") else 1)
    return paths


# ---------------------------------------------------------------------------
# Texture contact sheet
# ---------------------------------------------------------------------------


def label(coll, text, loc, size=0.26, color="#E9E1D3"):
    cu = bpy.data.curves.new("FXL_" + text, "FONT")
    cu.body = text
    cu.size = size
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    ob = bpy.data.objects.new("FXL_" + text, cu)
    ob.location = loc
    ob.rotation_euler = (PI / 2, 0, 0)
    m = bpy.data.materials.get("FX_Label") or bpy.data.materials.new("FX_Label")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*lin(color), 1)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    cu.materials.append(m)
    coll.objects.link(ob)
    return ob


def image_plane(coll, path, size, loc):
    me = bpy.data.meshes.new("FXP_" + os.path.basename(path))
    bm = bmesh.new()
    s = size / 2
    vs = [bm.verts.new(p) for p in ((-s, 0, -s), (s, 0, -s), (s, 0, s), (-s, 0, s))]
    f = bm.faces.new(vs)
    uv = bm.loops.layers.uv.new("UV")
    for lp, co in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        lp[uv].uv = co
    bm.to_mesh(me)
    bm.free()
    mat = bpy.data.materials.new("FXP_" + os.path.basename(path))
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(path, check_existing=True)
    tex.interpolation = "Linear"
    em = nt.nodes.new("ShaderNodeEmission")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    nt.links.new(tex.outputs["Alpha"], mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "BLENDED"
    me.materials.append(mat)
    ob = bpy.data.objects.new(me.name, me)
    ob.location = loc
    coll.objects.link(ob)
    return ob


def tile_plane(coll, size, loc, color):
    me = bpy.data.meshes.new("FXT_tile")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=size / 2,
                          matrix=Matrix.Rotation(PI / 2, 4, "X"))
    bm.to_mesh(me)
    bm.free()
    m = bpy.data.materials.new("FXT_tile")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*lin(color), 1)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    me.materials.append(m)
    ob = bpy.data.objects.new("FXT_tile", me)
    ob.location = loc
    coll.objects.link(ob)


def contact_sheet(paths, out_path):
    sc = bpy.data.scenes.new("FX_Sheet")
    sc.render.engine = "BLENDER_EEVEE"
    sc.view_settings.view_transform = "Standard"
    sc.render.film_transparent = False
    sc.render.resolution_x, sc.render.resolution_y = 1600, 900
    sc.eevee.taa_render_samples = 32
    w = bpy.data.worlds.new("FX_Dark")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (*lin("#1D1A18"), 1)
    sc.world = w
    cam = bpy.data.objects.new("FX_SheetCam", bpy.data.cameras.new("FX_SheetCam"))
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 16
    cam.location = (0, -30, 0)
    cam.rotation_euler = (PI / 2, 0, 0)
    sc.collection.objects.link(cam)
    sc.camera = cam
    coll = sc.collection
    tile = "#2A2623"
    tile_plane(coll, 7.4, (-3.95, 1, 0.35), tile)
    image_plane(coll, paths["fire_flipbook_4x4"], 7.4, (-3.95, 0, 0.35))
    label(coll, "fire_flipbook_4x4  (1024, 4x4 loop)", (-3.95, -0.5, -3.75), size=0.3)
    singles = [n for n in sorted(paths) if n != "fire_flipbook_4x4"]
    for i, n in enumerate(singles):
        r, c = divmod(i, 3)
        x, z = 1.35 + c * 2.65, 2.85 - r * 2.85
        tile_plane(coll, 2.1, (x, 1, z + 0.22), tile)
        image_plane(coll, paths[n], 2.1, (x, 0, z + 0.22))
        label(coll, f"{n} ({vfx.TEXTURES[n]['size']})", (x, -0.5, z - 1.08), size=0.19)
    sc.render.filepath = out_path
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    bpy.ops.render.render(write_still=True, scene=sc.name)
    print(f"[08] contact sheet {out_path}")


# ---------------------------------------------------------------------------
# Preview stand-in bases
# ---------------------------------------------------------------------------


def done(a, coll):
    """Asset.finish() and the offset it applied, so sockets land in final local studs."""
    bm = a.bm
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    zs = [v.co.z for v in bm.verts]
    off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
    obj = a.finish(collection=coll, mark_asset=False)
    return obj, off


def attach_flame(base, off, loc, h, r, seed, coll):
    fx = FX(seed)
    flame3d(fx, Vector(loc) - off, h, r, seed=seed)
    ob = fx.finish(f"{base.name}_Flame", coll)
    ob.parent = base
    return ob


def sock(base, off, kind, loc, scale=1.0):
    return vfx.add(base, kind, tuple(Vector(loc) - off), scale=scale)


def base_torch(coll):
    a = fk.Asset("TorchHead", "VFX Bases", seed=81)
    a.cyl(0.3, 0.34, 5.0, 7, mat="wood_dark")
    a.rope_rings(0.32, 3.9, count=2, thickness=0.09)
    a.cyl(0.42, 0.62, 0.9, 8, loc=(0, 0, 5.0), mat="wood")
    a.torus(0.6, 0.08, loc=(0, 0, 5.35), seg=10, mat="rope")
    a.cyl(0.56, 0.5, 0.12, 8, loc=(0, 0, 5.82), mat="charcoal")
    obj, off = done(a, coll)
    attach_flame(obj, off, (0, 0, 5.85), 1.7, 0.52, 3, coll)
    sock(obj, off, "torch_fire", (0, 0, 6.0))
    return obj, 20


def base_campfire(coll):
    a = fk.Asset("FireRing", "VFX Bases", seed=82)
    for i in range(10):
        ang = 2 * PI * i / 10
        a.rock((1.6, 1.4, 1.2), loc=(math.cos(ang) * 2.8, math.sin(ang) * 2.8, 0), rot=(0, 0, ang),
               subdiv=1, facets=10)
    for i in range(5):
        ang = 2 * PI * i / 5 + 0.3
        p1 = (math.cos(ang) * 1.6, math.sin(ang) * 1.6, 0.25)
        a.beam(p1, (math.cos(ang) * 0.25, math.sin(ang) * 0.25, 1.9), 0.22, mat="wood_dark")
    a.cyl(1.4, 1.2, 0.2, 9, mat="charcoal")
    obj, off = done(a, coll)
    attach_flame(obj, off, (0, 0, 0.25), 4.2, 1.3, 7, coll)
    sock(obj, off, "campfire", (0, 0, 0.6))
    return obj, 20


def base_brazier(coll):
    a = fk.Asset("BrazierBowl", "VFX Bases", seed=83)
    a.stone_block((2.6, 2.6, 0.6), loc=(0, 0, 0.3))
    a.stone_block((1.9, 1.9, 2.6), loc=(0, 0, 1.9), mat="stone_light")
    a.stone_block((2.5, 2.5, 0.5), loc=(0, 0, 3.4))
    a.cyl(1.0, 1.45, 0.9, 9, loc=(0, 0, 3.6), mat="iron")
    a.cyl(1.2, 1.15, 0.14, 9, loc=(0, 0, 4.3), mat="charcoal")
    obj, off = done(a, coll)
    attach_flame(obj, off, (0, 0, 4.4), 2.1, 0.85, 5, coll)
    sock(obj, off, "brazier_fire", (0, 0, 4.6))
    sock(obj, off, "embers", (0, 0, 4.8), 0.6)
    return obj, 20


def base_furnace(coll):
    a = fk.Asset("FurnaceArch", "VFX Bases", seed=84)
    a.stone_block((8.0, 4.4, 0.6), loc=(0, 0, 0.3), mat="stone_dark")
    for s in (-1, 1):
        for k in range(3):
            a.stone_block((1.9, 3.6, 1.45), loc=(s * 2.9, 0, 0.6 + 0.75 + k * 1.5),
                          mat="stone" if k % 2 else "stone_light")
    R = 2.0
    for i in range(7):
        ang = PI * (i + 0.5) / 7
        p = (math.cos(ang) * (R + 0.55), 0, 4.6 + math.sin(ang) * (R + 0.55))
        a.stone_block((1.0, 3.6, 1.2), loc=p, rot=(0, -(ang - PI / 2), 0), mat="stone_light" if i % 2 else "stone")
    a.stone_block((7.6, 3.6, 2.0), loc=(0, 0.1, 8.0))
    a.box((4.4, 0.5, 5.6), loc=(0, 1.5, 3.4), mat="stone_dark")
    a.box((4.0, 3.0, 0.3), loc=(0, 0, 0.75), mat="charcoal")
    a.strip([(0, 0.55), (-0.45, 0), (0, -0.55), (0.45, 0), (0, 0.55)], 0.16, 0.12,
            loc=(0, -1.85, 8.0), rot=(PI / 2, 0, 0), mat="glow_orange")
    a.strip([(0, 0.25), (0, -0.25)], 0.12, 0.12, loc=(0, -1.85, 8.0), rot=(PI / 2, 0, 0), mat="fire_core")
    obj, off = done(a, coll)
    attach_flame(obj, off, (0, 0.2, 0.9), 2.8, 1.25, 11, coll)
    sock(obj, off, "forge_fire", (0, 0, 1.0))
    sock(obj, off, "heat_glow", (0, -1.2, 1.8))
    sock(obj, off, "glyph_glow", (0, -2.1, 8.0))
    return obj, 20


def base_chimney(coll):
    a = fk.Asset("ChimneyStack", "VFX Bases", seed=85)
    z = 0.0
    for k in range(6):
        w = 3.2 - k * 0.12
        a.stone_block((w, w, 1.5), loc=(0, 0, z + 0.75), mat="stone_light" if k % 2 else "stone")
        z += 1.5
    for s in (-1, 1):
        a.stone_block((2.9, 0.5, 0.7), loc=(0, s * 1.2, z + 0.35))
        a.stone_block((0.5, 1.9, 0.7), loc=(s * 1.2, 0, z + 0.35))
    a.box((1.9, 1.9, 0.2), loc=(0, 0, z + 0.4), mat="charcoal")
    obj, off = done(a, coll)
    sock(obj, off, "chimney_smoke", (0, 0, z + 0.8))
    return obj, 22


def base_rune(coll):
    a = fk.Asset("RuneSlab", "VFX Bases", seed=86)
    a.stone_block((8.0, 6.0, 1.3), loc=(0, 0, 0.65), bevel=0.35, jitter=0.06)
    for R in (1.9, 1.1, 0.4):
        a.strip([(0, R), (-R, 0), (0, -R), (R, 0), (0, R)], 0.22, 0.06, loc=(0, 0, 1.3), mat="rune_blue")
    obj, off = done(a, coll)
    sock(obj, off, "rune_glow", (0, 0, 1.45))
    return obj, 35


def base_waterfall(coll):
    a = fk.Asset("WaterfallDrop", "VFX Bases", seed=87)
    for s in (-1, 1):
        for k in range(4):
            a.rock((3.8, 3.6, 3.0), loc=(s * 3.4, 3.2, k * 2.5), subdiv=1, facets=12)
    a.rock((10.0, 3.4, 2.0), loc=(0, 4.2, 9.2), subdiv=1, facets=12)
    a.box((3.6, 3.0, 10.0), loc=(0, 4.0, 5.0), mat="stone_dark")
    # falling water sheet: faceted strips bulging forward, foam where it lands
    for i in range(10):
        z1, z2 = 10.2 - i * 1.0, 9.2 - i * 1.0
        y = 2.3 - 0.15 * math.sin(i * 0.5)
        a.box((3.0 - 0.08 * (i % 2), 0.4, 1.05), loc=(0, y - i * 0.03, (z1 + z2) / 2),
              mat="water" if i % 3 else "water_deep")
    a.cyl(5.5, 5.8, 0.4, 14, loc=(0, -1.5, 0), mat="water")
    for i in range(9):
        ang = PI + PI * i / 8
        a.rock((1.4, 1.2, 0.9), loc=(math.cos(ang) * 5.9, -1.5 + math.sin(ang) * 5.4, 0), subdiv=1, facets=10)
    obj, off = done(a, coll)
    sock(obj, off, "waterfall_mist", (0, 1.4, 0.45))
    sock(obj, off, "water_foam", (0, -0.6, 0.42), 0.8)
    return obj, 24


def base_shore(coll):
    a = fk.Asset("Shoreline", "VFX Bases", seed=88)
    a.box((13.0, 6.0, 1.0), loc=(0, 2.6, 0.2), rot=(-0.07, 0, 0), mat="dirt", bevel=0.2)
    a.box((13.0, 2.2, 1.0), loc=(0, 5.2, 0.55), mat="grass_ground", bevel=0.2)
    a.box((13.0, 7.0, 0.5), loc=(0, -3.0, 0.25), mat="water")
    for i, x in enumerate((-5.0, -1.2, 3.6)):
        a.rock((1.6, 1.3, 1.0), loc=(x, 0.6 + 0.3 * (i % 2), 0.2), subdiv=1, facets=10)
    obj, off = done(a, coll)
    for x in (-3.2, 0.6, 4.4):
        sock(obj, off, "water_foam", (x, -0.4, 0.52))
    return obj, 35


def base_dirt(coll):
    a = fk.Asset("DirtPatch", "VFX Bases", seed=89)
    a.cyl(4.6, 4.4, 0.3, 9, mat="dirt", jitter=0.08)
    a.cyl(5.2, 5.0, 0.2, 10, mat="grass_ground")
    rng = random.Random(4)
    for i in range(6):
        ang = rng.uniform(0, 2 * PI)
        d = rng.uniform(1.2, 3.8)
        a.rock((0.6, 0.5, 0.4), loc=(math.cos(ang) * d, math.sin(ang) * d, 0.25), subdiv=1, facets=10)
    obj, off = done(a, coll)
    sock(obj, off, "dust", (0, 0, 1.2))
    return obj, 28


BASES = [base_torch, base_campfire, base_brazier, base_furnace, base_chimney, base_rune,
         base_waterfall, base_shore, base_dirt]


def root_of(o):
    while o.parent is not None:
        o = o.parent
    return o


def framing_proxy(base, coll):
    pts = []
    for o in [base] + [c for c in base.children_recursive if c.type == "MESH"]:
        pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), 0.0))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    me = bpy.data.meshes.new("Proxy_" + base.name)
    bm = bmesh.new()
    vs = bmesh.ops.create_cube(bm, size=1.0)["verts"]
    bmesh.ops.scale(bm, vec=hi - lo, verts=vs)
    bmesh.ops.translate(bm, vec=(lo + hi) / 2, verts=vs)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("Proxy_" + base.name, me)
    ob.hide_render = True
    coll.objects.link(ob)
    return ob


def tile(cell_paths, cols, cell, path):
    rows = math.ceil(len(cell_paths) / cols)
    w, h = cell
    sheet = np.ones((rows * h, cols * w, 4), dtype=np.float32)
    for i, p in enumerate(cell_paths):
        img = bpy.data.images.load(p, check_existing=False)
        px = np.array(img.pixels[:], dtype=np.float32).reshape(img.size[1], img.size[0], 4)
        r, c = divmod(i, cols)
        y0 = (rows - 1 - r) * h
        sheet[y0:y0 + h, c * w:c * w + w] = px[:h, :w]
        bpy.data.images.remove(img)
    out = bpy.data.images.new("FX_Tile", cols * w, rows * h, alpha=True)
    out.pixels = sheet.ravel()
    out.filepath_raw = path
    out.file_format = "PNG"
    out.save()
    bpy.data.images.remove(out)


def studio_dim(scene, dim):
    key, fill = bpy.data.objects["FB_Key"], bpy.data.objects["FB_Fill"]
    nt = scene.world.node_tree
    cam_bg = nt.nodes["Background"]
    amb = [n for n in nt.nodes if n.type == "BACKGROUND" and n.name != "Background"][0]
    if dim:
        key.data.energy, fill.data.energy = 0.45, 0.1
        amb.inputs["Strength"].default_value = 0.12
        cam_bg.inputs["Color"].default_value = (*lin("#6A6560"), 1)
    else:
        key.data.energy, fill.data.energy = 3.2, 0.8
        amb.inputs["Strength"].default_value = 0.75
        cam_bg.inputs["Color"].default_value = (*lin(fk.BG_HEX), 1)
    ground = bpy.data.objects["FB_Ground"]
    gm = ground.data.materials[0]
    bg = lin("#6A6560") if dim else lin(fk.BG_HEX)
    gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (
        *(c * fk.GROUND_ALBEDO for c in bg), 1)


def preview_sheets():
    scene = bpy.context.scene
    fk.reset_file()
    fk._studio(scene)
    scene.eevee.taa_render_samples = 64
    coll = bpy.data.collections.new("VFX Bases")
    scene.collection.children.link(coll)
    bases = []
    for i, fn in enumerate(BASES):
        obj, el = fn(coll)
        obj.location = (i * 120.0, 0, 0)
        bases.append((obj, el))
    bpy.context.view_layer.update()
    made = vfx.realize(scene)
    made2 = vfx.realize(scene)  # idempotency check: must replace, not duplicate
    n_prev = len([o for o in bpy.data.objects if o.name.startswith(vfx.PREVIEW_PREFIX)])
    assert n_prev == len(made2), (n_prev, len(made), len(made2))
    print(f"[08] realize(): {n_prev} preview objects for "
          f"{len([o for o in scene.objects if o.get('vfx_kind')])} sockets")
    # flicker check: the driver must vary energy over frames
    lights = [o for o in made2 if o.type == "LIGHT"]
    es = []
    for f in range(1, 49, 2):
        scene.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        es.append(lights[0].evaluated_get(dg).data.energy)
    print(f"[08] flicker {lights[0].name}: base {lights[0].data['vfx_base_energy']:.0f} W, "
          f"frames 1-48 min {min(es):.0f} max {max(es):.0f} mean {sum(es) / len(es):.0f}")
    # scoped re-realize + clear must only touch that asset's previews
    one = bases[0][0]
    n_before = len([o for o in bpy.data.objects if o.name.startswith(vfx.PREVIEW_PREFIX)])
    vfx.realize(scene, [one])
    n_after = len([o for o in bpy.data.objects if o.name.startswith(vfx.PREVIEW_PREFIX)])
    assert n_before == n_after, (n_before, n_after)
    vfx.clear(scene)
    assert not [o for o in bpy.data.objects if o.name.startswith(vfx.PREVIEW_PREFIX)]
    made2 = vfx.realize(scene)
    scene.frame_set(1)
    bpy.context.view_layer.update()
    proxies = [framing_proxy(b, coll) for b, _ in bases]
    cell = (512, 448)
    for dim, out in ((False, "08_vfx.png"), (True, "08_vfx_dim.png")):
        studio_dim(scene, dim)
        cells = []
        for (b, el), px in zip(bases, proxies):
            for o in scene.objects:
                if o.name.startswith("FB_") or o.type in ("CAMERA", "EMPTY"):
                    continue
                o.hide_render = root_of(o) is not b or o is px or o.name.startswith("Proxy_")
            scene.render.resolution_x, scene.render.resolution_y = cell
            fk.frame(px, fk.DEFAULT_AZIMUTH, el, margin=1.02)
            p = os.path.join(RENDERS, "08_vfx_cells", f"{'dim_' if dim else ''}{b.name}.png")
            os.makedirs(os.path.dirname(p), exist_ok=True)
            scene.render.filepath = p
            bpy.ops.render.render(write_still=True)
            cells.append(p)
        tile(cells, 3, cell, os.path.join(RENDERS, out))
        print(f"[08] preview {out}")
    studio_dim(scene, False)
    fk.save(os.path.join(BLENDER_DIR, "assets", "08_vfx_preview.blend"))


def main():
    only = os.environ.get("FX_ONLY", "")
    paths = {n: os.path.join(TEX_DIR, n + ".png") for n in vfx.TEXTURES}
    if only in ("", "tex"):
        paths = render_textures()
        contact_sheet(paths, os.path.join(RENDERS, "08_vfx_textures.png"))
    if only in ("", "preview"):
        preview_sheets()
    os.makedirs(VFX_DIR, exist_ok=True)
    with open(os.path.join(VFX_DIR, "vfx_catalog.json"), "w", encoding="utf-8") as fh:
        json.dump(vfx.catalog(), fh, indent=2)
    print("[08] done")


main()
