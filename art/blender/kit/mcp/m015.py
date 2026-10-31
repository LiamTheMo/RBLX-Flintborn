"""015 Ember Meteor (references/015.png): one big rounded fractured meteor - a faceted dome of dark rock split into
four thick shell pieces round a hot faceted ember core, which glows through a main opening at the front, smaller
windows at the back and right side, a small opening in the crown where the seams meet, and thin glowing seams and
cracks with real depth; a ring of low pale warm stones round the foot.

    import importlib, kit_models, m015; importlib.reload(kit_models); importlib.reload(m015); m015.build()

Construction (studs; front -Y, ground z = 0; M015_spec.md "Stage 1 rework (overall read)"):
- One common meteor dome (`dome()`), mirror-symmetric about the plane x = XC, and the Ember Core inside it
  (`core()`, also mirror-symmetric, so a mirrored piece still fits it).
- The dome is cut into four sectors by vertical planes through the centre (the seams, seen from above as a cross).
  Each piece = dome ∩ its sector prism (a hairline 0.04 inside each seam line) − the hollow (the core scaled HOLLOW, so
  the piece overlaps the core and the union leaves crisp creases) − the openings it borders − the seam slots along its
  edges − its own crack slot. Seams and cracks are the same lofted slot cutters (M015_spec.md §6.2): splayed walls in
  rows (lip, ember wall, core band) and a hot floor.
- Parts (each piece built by its own function in the shared build frame):
  - EmberMeteorSlab (A, `slab()`): the front-left piece, wrapping from the front window round the left side to the
    back-left seam (the long bent piece), with crack 1 down its front face (the sliver beside the window).
  - EmberMeteorCap (B, `cap()`): the front-right piece, between the front window and the side window.
  - EmberMeteorChunk (C, `chunk()`): the back-right piece, the tallest, its crack running diagonally down its back-right
    flank. The back-left piece is this part mirrored about x = XC (the main session's decision): the dome, core,
    rear window, crown opening and back seam are symmetric about that plane and the left seam is the mirror of the right.
  - EmberCore (`core()`), EmberMeteorBaseRock (`base_rock()`, low rounded stone).
- The hero (EmberMeteorDeposit) is pasted from the finished part meshes (m011._paste; the back-left piece is the
  mirrored chunk, the base rocks are thirteen transformed copies of the stone), unioned and floor-cut at the ground.
Stage 1 gives one placeholder key per region; later stages regrade them.
Stage 2+3: _polish() on every part (before the hero pastes it) and on the hero: all triangles, no corner under
POLISH_LIM (5 degrees) with the slot verts held (_wall_verts), origin at the bottom centre, then the UVs per object
(_uv_pass, UV_ANGLE). build() also reports corners, crossings, interior faces, inner shells and uv_stats.
Stages 4-6 (finish_stages, on the finished meshes; colour only): palette() (calibrated keys, Neon core / core_hot /
ember_wall), colour_all() (faces classified by the construction surface they lie on, then coloured by position fields:
shell patches + ground band + spill, slot rows by depth, rim walls graded outer lip -> core, core height + lateral +
occlusion, rock patches + crevices; broad Tint per facet), _vfx() (two heat_glow sockets with shadowed PointLights in
the window recesses, four embers sockets: crown, front, both flanks). report() measures the renders against the sheet
with the study's cls(). Round 2 (M015_spec.md "Stage 4-6 (round 2)"): slot rows packed into the visible top of each
slot (lip, ember wall / core, hot), rims graded per opening (RIM_STEPS), ember_wall Neon #C95E2A, re-calibrated.
"""
import math
import random
import zlib

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import kit_mcp as K
import kit_models as M
import m009
import m011
import m012
import m014

NUM, TITLE, SHEET = 15, "Ember Meteor", "M015"
SHELL, LIP, WALL = "m015_shell", "m015_ember_lip", "m015_ember_wall"
CORE, HOT, DEEP, BASE = "m015_core", "m015_core_hot", "m015_core_deep", "m015_base"
OFF = "m015_offset"
UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)

SHELL_LIGHT, SHELL_DARK, SHELL_WARM = "m015_shell_light", "m015_shell_dark", "m015_shell_warm"
BASE_LIGHT, BASE_DARK = "m015_base_light", "m015_base_dark"
NEON = 1.0              # the exporter's GLOW_EMISSION threshold: core and core_hot export as Neon pieces, nothing else
# stage 4 palette: key -> (hex, roughness, emission, low specular). Calibrated base colours (stage 1's placeholders
# were the §5.4 starting hexes); targets, dome results and the hero re-measures in M015_spec.md "Stage 4" and TARGETS.
# Pass 1 (calibrate(), test dome, every key within 6 levels of its target): shell #46434C, light #5C5861, dark
# #312E3A, warm #4D474C, lip #4A211D, wall #A74F34, core #FB7430, hot #FBAB4E, deep #A33A16, base #857774, base light
# #968885, base dark #6A5D58.
# Pass 2 (report() on the hero, cls() masks, VFX off): the shell rendered 9-26 levels under the sheet in the lit views
# (front #4E484E / #685E64, f34 #575057 / #60595F, top #575156 / #61595E): the dome's top faces the key light, the
# hero's flanks don't (as M014). The shell family x (1.41, 1.38, 1.34) in linear light, the geometric mean of the three
# views' gains. The base rocks matched on the dome values (front #AC9389 / #AF968C), so they stay.
# Stage 5: core, core_hot and ember_wall are Neon (emission NEON, previewed unlit by _glow_mats); the rest solid.
# Stage 4-6 round 2 (M015_spec.md "Stage 4-6 (round 2)"): re-calibrated against the new rims, pillar and slot rows.
# Pass 1 (calibrate(), test dome; rendered / target): shell #4B4751 (#60595F / #5F585E), light #635F68 (#7C7478 /
# #7C7378), dark #34313E (#47424B / #45404A), warm #524B51 (#685D5F / #685D5E), lip #522420 (#602620 / #5E2620), wall
# #C95E2A (#D75B23 / #D85A22, the verifier's crack target), core #FB7430, hot #FBAB4E, deep #AE3F19 (#DA451A /
# #D9441A), base #8F7F7C (#B49A8F / #B39A8F), base light #9F908D, base dark #72635E.
# Pass 2 (report(light=True) on the hero, cls() masks, all six sheet views; linear-light gains, two rounds): shell
# x 1.24 and warm x 1.24, light x 1.95, dark x 0.67 (round a: the six views' shell medians 6-25 levels under the
# sheet's and the lit quartile 20-30 under; round b, after the tone seed change: medians ~10 over, the shade quartile
# 15-25 over the sheet's #373134), deep x 1.3 (the front and f34 rims read 40-57 % dark lip L against the sheet's
# thin lip), the base rocks x 0.89 (front / f34 rocks 9-19 levels over, top 5 under).
PALETTE = {SHELL: ("#534F5B", 0.88, 0.0, False), SHELL_LIGHT: ("#88828E", 0.88, 0.0, False),
           SHELL_DARK: ("#2A2732", 0.9, 0.0, False), SHELL_WARM: ("#5C535B", 0.88, 0.0, False),
           LIP: ("#522420", 0.85, 0.0, True), WALL: ("#C95E2A", 0.75, NEON, False),
           CORE: ("#FB7430", 0.5, NEON, False), HOT: ("#FBAB4E", 0.5, NEON, False),
           DEEP: ("#C4481E", 0.5, 0.0, True), BASE: ("#887875", 0.92, 0.0, False),
           BASE_LIGHT: ("#978986", 0.92, 0.0, False), BASE_DARK: ("#6C5E59", 0.92, 0.0, False)}


def palette():
    for k, (hexcol, rough, emit, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, emit=emit, low_spec=low)
        _restyle(k)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, emit=emit, low_spec=low)     # (low specular once the material exists)
    _glow_mats()
    _ember_spec()


def _restyle(key):
    """Drop an FB_ material whose node set no longer matches its key's emission (flintkit builds emissive keys
    without the Tint node, and set_colour never clears an emission), so flintkit makes it afresh (m009)."""
    mat = bpy.data.materials.get("FB_" + key)
    if mat and mat.node_tree:
        tinted = any(n.type == "MIX" for n in mat.node_tree.nodes)
        if tinted == (K.fk().palette_entry(key)[3] > 0):
            # (meshes already using it are remapped to the new material, so no slot is left empty)
            mat.name = mat.name + "_restyle"
            new = K.fk().material(key)
            mat.user_remap(new)
            bpy.data.materials.remove(mat)
            return True
    return False


EMBER_SPEC = 0.06      # Specular IOR Level on the lip / rim / core_deep family, mix keys too (flintkit makes mixes at
#                        0.2: the front window's lit rim face went salmon pink, lit quartile #D8716A, a white sheen
#                        over the dark red where the sheet's lit rims are orange-red)


def _ember_spec():
    for m in bpy.data.materials:
        if m.name.startswith(("FB_m015_ember", "FB_m015_core_deep")) and m.node_tree and \
                list(m.get("flintkit_spec", [0, 0, 0]))[2] < NEON:
            b = m.node_tree.nodes.get("Principled BSDF")
            if b and "Specular IOR Level" in b.inputs:
                b.inputs["Specular IOR Level"].default_value = EMBER_SPEC


def _glow_mats():
    """Blender preview of the Neon keys (emission >= NEON) as Roblox shows Neon: the key's own colour, unshaded (the
    BSDF's base colour black, no specular, so only the emission shows). The exported hex is unchanged (m009)."""
    for mat in bpy.data.materials:
        if not (mat.name.startswith("FB_m015_") and mat.node_tree):
            continue
        if list(mat.get("flintkit_spec", [0, 0, 0]))[2] < NEON:
            continue
        b = mat.node_tree.nodes.get("Principled BSDF")
        for l in list(b.inputs["Base Color"].links):
            mat.node_tree.links.remove(l)
        b.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)
        if "Specular IOR Level" in b.inputs:
            b.inputs["Specular IOR Level"].default_value = 0.0


INFO = {}

# ---- the common dome and the core ---------------------------------------------------------------------------------
XC, YC = 0.3, -0.3              # plan centre of the dome and the core; the mirror plane is x = XC
DOME = dict(rx=5.1, ry=4.6, h=7.3, n=8, amp=0.07, back=0.35, peak=0.6)
# rings: (height fraction, radius fraction); odd rings turn half a step (broad triangular facets), all mirror-symmetric.
# (the first pass, 10 points on 7 rings, read as a smooth ball: 121 facets; the sheet's mass is a few big planes with
# steep flanks and a broad shoulder)
DOME_RINGS = ((-0.05, 0.9), (0.2, 1.0), (0.45, 0.95), (0.66, 0.82), (0.83, 0.6), (0.95, 0.32))
DOME_TOP = 1.0                  # two ridge points at the crown
DOME_MERGE = 3.0
CORE_AT = Vector((XC, YC - 0.35, 3.05))      # a little forward, nearer the main opening
CORE_DIM = dict(r=(2.65, 2.55, 2.65), n=32, seed=15041, wob=(0.95, 1.04))
CORE_MERGE = 20.0
HOLLOW = 0.9                    # the pieces' hollow is the core scaled this much about its centre (overlap ~0.25)


def _edges_in_order(bm, faces):
    """The edges of faces in creation order. (A Python set of BMEdges iterates by memory address, and
    dissolve_limit's result depends on the order it is given the edges in: with the set, the core came out 58 or 60
    tris, min corner 18.6 or 4.8 / 8.0 degrees, from one build to the next.)"""
    bm.edges.index_update()
    return sorted({e for f in faces for e in f.edges}, key=lambda e: e.index)


def _hull(a, pts, merge):
    """m014._hull with the merge's edges in a fixed order (_edges_in_order), so every build makes the same mesh."""
    vs = [a.bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(a.bm, input=vs)
    for v in vs:
        if v.is_valid and not v.link_faces:
            a.bm.verts.remove(v)
    vs = [v for v in vs if v.is_valid]
    faces = K.faces_of(vs)
    bmesh.ops.recalc_face_normals(a.bm, faces=faces)
    if merge:
        bmesh.ops.dissolve_limit(a.bm, angle_limit=math.radians(merge), verts=vs,
                                 edges=_edges_in_order(a.bm, faces))
        vs = [v for v in vs if v.is_valid]
    facets = len(K.faces_of(vs))
    bmesh.ops.triangulate(a.bm, faces=[f for f in K.faces_of(vs) if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(a.bm, faces=K.faces_of(vs))
    return vs, facets


def _sym_jit(th, ring):
    """Radius jitter that is the same at theta and 180 - theta (mirror-symmetric about the YZ plane)."""
    s, c = math.sin(th), abs(math.cos(th))
    return 1.0 + DOME["amp"] * math.sin(3.1 * s + 2.3 * c + 1.7 * ring)


def _dome_pts():
    d = DOME
    pts = []
    for k, (fz, rf) in enumerate(DOME_RINGS):
        n = d["n"]
        for i in range(n):
            th = math.pi / 2 + (i + 0.5 + 0.5 * (k % 2)) * 2 * math.pi / n
            j = _sym_jit(th, k)
            y = d["ry"] * rf * j * math.sin(th) + d["back"] * fz          # the crown leans a little back
            # the back pieces rise highest: upper back points lift. (Build fixes, verifier round 1: the lift is now
            # zero on the back seam's plane (|cos| = 0) and full 45 deg either side, on BR's and BL's own crowns, and
            # the summit ridge sits in front of the crown opening instead of behind it: with the back crown above the front
            # one along x = XC, the front view looked straight through the back seam's hairline under the crown.)
            lift = d["peak"] * max(0.0, math.sin(th)) * max(0.0, fz - 0.4) / 0.6 * min(1.0, 1.6 * abs(math.cos(th)))
            pts.append(Vector((XC + d["rx"] * rf * j * math.cos(th), YC + y, fz * d["h"] + lift)))
    for x in (-0.35, 0.35):     # just in front of the crown opening, so the front crown is the summit at x = XC
        pts.append(Vector((XC + x, YC - 2.6, DOME_TOP * d["h"] + 0.3)))
    return pts


def dome(a, mat=SHELL):
    vs, n = _hull(a, _dome_pts(), DOME_MERGE)
    a._finish(vs, mat, tint=1.0)
    INFO["dome_facets"] = n
    return vs


def _core_pts(scale=1.0):
    """Fibonacci points on the core ellipsoid, the x >= 0 half mirrored (the core is symmetric about x = 0)."""
    c = CORE_DIM
    rng = random.Random(c["seed"])
    ga = math.pi * (3 - math.sqrt(5))
    pts = []
    for i in range(c["n"]):
        z = 1 - 2 * (i + 0.5) / c["n"]
        r = math.sqrt(max(0.0, 1 - z * z))
        k = rng.uniform(*c["wob"])
        th = ga * i + rng.uniform(-0.12, 0.12)
        p = Vector((r * math.cos(th) * k * c["r"][0], r * math.sin(th) * k * c["r"][1], z * k * c["r"][2]))
        if p.x >= -1e-6:
            pts.append(p * scale)
            if p.x > 0.05:
                pts.append(Vector((-p.x, p.y, p.z)) * scale)
    return pts


def core(a):
    """Ember Core, centred on the origin; placeholder keys by height plus a lean to +Y: deep / core / hot."""
    c = CORE_DIM
    vs, n = _hull(a, _core_pts(), CORE_MERGE)
    a._finish(vs, CORE, tint=1.0)
    INFO["core_facets"] = n
    di, hi = a._mi(DEEP), a._mi(HOT)
    for f in K.faces_of(vs):
        p = f.calc_center_median()
        u = (p.z + c["r"][2]) / (2 * c["r"][2]) + 0.1 * p.y / c["r"][1]
        if u < 0.3:
            f.material_index = di
        elif u > 0.72:
            f.material_index = hi
    return vs


def _hollow(a):
    # the same merge as the core, so the hollow is exactly the core's shape scaled (with merge 0 the hollow kept
    # vertices the core's 20-degree merge dissolves, and the pieces' red inner walls showed round the core)
    vs, _ = _hull(a, [CORE_AT + p for p in _core_pts(HOLLOW)], CORE_MERGE)
    a._finish(vs, LIP, tint=1.0)
    return vs


# ---- sectors (the seams, seen from above) --------------------------------------------------------------------------
# seam azimuths (deg from +X towards +Y; the front is -90): front FL|FR, right FR|BR, back BR|BL (on the mirror plane),
# left BL|FL (the mirror of the right one)
SEAM_AZ = {"front": -75.0, "right": -5.0, "back": 90.0, "left": 185.0}
SECTORS = {"FL": ("left", "front"), "FR": ("front", "right"), "BR": ("right", "back"), "BL": ("back", "left")}
# each piece stops this far short of a seam line (no coplanar contact in the union). (Build fixes, verifier round 1:
# tried -0.04, neighbours overlapping by 0.08 so a seam would be only its closed slot; but both neighbours are cut by
# the same slot tube, crown opening and hollow, so in the overlap strip their cut faces coincide exactly, and the
# hero's union came out with 51 non-manifold edges and 867 crossing face pairs. Back to +0.04; the sightlines are
# closed by the depth caps, the back seam's taper and the FR pillar instead.)
HAIR = 0.04
# per seam (default HAIR). The back seam lies on the mirror plane, so its gap can only be closed by BR and the mirrored
# BL overlapping; its 0.08 gap was a straight sightline over the core in the rear view (9 px at z 5.7). With the
# remesh fix (no wild vertex) the overlap unions cleanly for this seam alone (coincident cut faces in a 0.08 strip,
# tested headless: 0 non-manifold, 0 crossings). Overlapping every seam still breaks: the hero lost its core and the
# Chunk got 4 crossings (headless test), so the right / left / front seams keep the 0.08 gap.
SEAM_HAIR = {"back": -0.04}


def _sector_poly(key):
    s0, s1 = SECTORS[key]
    a0, a1 = (math.radians(SEAM_AZ[s]) for s in SECTORS[key])
    if a1 < a0:
        a1 += 2 * math.pi
    c = Vector((XC, YC))
    d0, d1 = Vector((math.cos(a0), math.sin(a0))), Vector((math.cos(a1), math.sin(a1)))
    n0, n1 = Vector((-d0.y, d0.x)), Vector((d1.y, -d1.x))             # inward normals of the two seam lines
    # the corner where the two offset lines meet
    p0, p1 = c + n0 * SEAM_HAIR.get(s0, HAIR), c + n1 * SEAM_HAIR.get(s1, HAIR)
    den = d0.x * d1.y - d0.y * d1.x
    t = ((p1 - p0).x * d1.y - (p1 - p0).y * d1.x) / den
    corner = p0 + d0 * t
    R = 14.0
    out = [corner, p0 + d0 * R]
    k = max(2, int(math.degrees(a1 - a0) / 15))
    for i in range(1, k):
        a = a0 + (a1 - a0) * i / k
        out.append(c + Vector((math.cos(a), math.sin(a))) * R * 1.05)
    out.append(p1 + d1 * R)
    return out


def _prism(a, poly, z0=-3.0, z1=12.0, mat=SHELL):
    pts = [Vector((p.x, p.y, z)) for z in (z0, z1) for p in poly]
    vs, _ = _hull(a, pts, 0.0)
    a._finish(vs, mat, tint=1.0)
    return vs


# ---- openings (frusta: a small diamond inside, a bigger one outside, so the rims splay) ---------------------------------
# (centre on the core side, direction out, half-width, half-height (along "up" in the section), length, outer flare)
OPENINGS = {
    # (round-1 fixes: tried keeping every opening's inner top under a crown shaft started at 5.2, to close the last
    # grazing sightlines over the core (3-4 px, under 0.05 stud wide); the shaft's floor ring then made the Slab and
    # Chunk polish cross faces and the hero lost its core - reverted)
    "front": dict(c=(XC + 0.35, YC - 1.0, 3.5), d=(0.1, -1.0, 0.0), hw=2.2, hh=2.5, flare=1.22, up=(0.0, 0.0, 1.0)),
    # (build fixes, verifier round 1: rear hw 1.95 -> 2.3, side hw 1.35 -> 1.8 and moved forward, the side view's
    # sheet window being f 0.62-0.87; glow shares were side 8.3 / 15.8 %, rear 17.5 / 22.8 %)
    # (and its centre 3.7 -> 3.1: with its top above the core's crown (5.67) the front window, the crown shaft and the
    # rear window made one open channel over the core - a see-through at z 5.6-5.7 from the front and rear views)
    "rear": dict(c=(XC, YC + 1.0, 3.1), d=(0.0, 1.0, 0.0), hw=2.3, hh=2.35, flare=1.22, up=(0.0, 0.0, 1.0)),
    "side": dict(c=(XC + 1.0, YC - 1.7, 3.3), d=(1.0, -0.3, 0.0), hw=1.8, hh=2.0, flare=1.22, up=(0.0, 0.0, 1.0)),
    "crown": dict(c=(XC, YC + 0.1, 4.6), d=(0.0, 0.0, 1.0), hw=1.75, hh=2.05, flare=1.3, up=(0.0, 1.0, 0.0)),
}
# FR keeps a solid pillar between the front and side openings: a plan wedge between these azimuths is taken out of
# both frusta before they cut FR, so no sightline runs in at the front window and out at the side one past the
# core's flank (verifier round 1, view (-45, 20)); at y YC - 1.6 without it the two openings met and cut FR in two.
PILLAR_AZ = (-60.0, -47.0)
OPEN_LEN = 7.0
PIECE_OPENINGS = {"FL": ("front", "crown"), "FR": ("front", "side", "crown"), "BR": ("rear", "crown")}


def _opening(a, key):
    o = OPENINGS[key]
    c, d, up = Vector(o["c"]), Vector(o["d"]).normalized(), Vector(o["up"])
    up = (up - d * up.dot(d)).normalized()
    side = d.cross(up).normalized()
    pts = []
    for dist, sc in ((0.0, 1.0), (OPEN_LEN, o["flare"])):
        q = c + d * dist
        pts += [q + side * o["hw"] * sc, q + up * o["hh"] * sc, q - side * o["hw"] * sc, q - up * o["hh"] * sc]
    vs, _ = _hull(a, pts, 0.0)
    a._finish(vs, LIP, tint=1.0)
    return vs


def _pillar(a):
    """The plan wedge FR keeps between its front and side openings (PILLAR_AZ), full height."""
    c = Vector((XC, YC))
    poly = [c] + [c + Vector((math.cos(math.radians(t)), math.sin(math.radians(t)))) * 14.0 for t in PILLAR_AZ]
    return _prism(a, poly, mat=LIP)


# ---- slot cutters (seams and cracks; M015_spec.md §6.2) ---------------------------------------------------------------
STEP = 0.42             # stations at most this far apart
FLOOR = 0.45            # floor width as a share of the opening G
ROWS = (0.25, 0.55)     # wall rows (fractions of the depth): lip | ember wall | core bands
CHAMFER = (0.08, 0.06)  # one-side lip chamfer on cracks: depth, extra set-back at the surface (full at G >= 0.2)
LID = 0.5
END_DEPTH = 0.55        # depth multiplier at a closed (G = 0) end
AIM = Vector((XC, YC, 2.6))     # slot control rays point at this from (az, el)


def _dir(az, el):
    a, e = math.radians(az), math.radians(el)
    return Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))


def _tree(fn):
    p = K.fk().Asset("_probe", "probe")
    fn(p)
    p.bm.verts.ensure_lookup_table()
    p.bm.faces.ensure_lookup_table()
    t = BVHTree.FromBMesh(p.bm)
    p.bm.free()
    return t


SEAM_STEP = 0.75        # seams are long; fewer stations keep the hero under budget


def stations(tree, ctrl, depth, plane=False, step=STEP):
    """Slot stations [(p, n, t, G, d)] from control points (az, el, G): rays from outside at AIM, snapped to the
    surface, resampled to `step`, normals smoothed (projected into the mirror plane when `plane`)."""
    hits = []
    for az, el, g in ctrl:
        d = _dir(az, el)
        o = AIM + d * 20
        h = tree.ray_cast(o, -d, 40)
        hits.append((h[0], h[1], az, el, g))
    st = []
    for (p0, n0, az0, el0, g0), (p1, n1, az1, el1, g1) in zip(hits, hits[1:]):
        k = max(1, math.ceil((p1 - p0).length / step))
        for i in range(k):
            f = i / k
            d = _dir(az0 + (az1 - az0) * f, el0 + (el1 - el0) * f)
            h = tree.ray_cast(AIM + d * 20, -d, 40)
            st.append([h[0], h[1].copy(), g0 + (g1 - g0) * f])
    st.append([hits[-1][0], hits[-1][1].copy(), hits[-1][4]])
    for _ in range(3):
        ns = [s[1] for s in st]
        for j in range(len(st)):
            st[j][1] = (ns[max(0, j - 1)] + ns[j] * 2 + ns[min(len(st) - 1, j + 1)]).normalized()
    if plane:
        for s in st:
            s[1].x = 0.0
            s[1].normalize()
            s[0].x = XC
    out = []
    for j, (p, n, g) in enumerate(st):
        t = (st[min(len(st) - 1, j + 1)][0] - st[max(0, j - 1)][0]).normalized()
        out.append((p, n, t, g, depth * (END_DEPTH if g <= 1e-9 else 1.0)))
    return out


_EDGE_KEYS = (CORE, WALL, LIP, LIP, LIP, LIP, LIP, LIP, LIP, WALL, CORE, HOT)


def _profile(p, n, t, G, d, chamfer=True):
    s = n.cross(t).normalized()
    nn = t.cross(s).normalized()
    if nn.dot(n) < 0:
        nn = -nn
    half, g = G / 2, FLOOR * G / 2

    def w(f):
        return half + (g - half) * f
    ch = CHAMFER[1] * min(1.0, G / 0.2) if chamfer else 0.0
    cd = CHAMFER[0]
    hs = (-d, -ROWS[1] * d, -ROWS[0] * d, -cd, 0.0, LID)
    wa = (w(1.0), w(ROWS[1]), w(ROWS[0]), w(cd / d), half + ch, half + ch)
    wb = (w(1.0), w(ROWS[1]), w(ROWS[0]), w(cd / d), half, half)
    return [p + nn * h + s * x for h, x in zip(hs, wa)], [p + nn * h - s * x for h, x in zip(hs, wb)]


def _tube(a, st, chamfer=True, mirror=False):
    bm = a.bm
    profs = []
    for p, n, t, G, d in st:
        A, B = _profile(p, n, t, G, d, chamfer)
        if mirror:
            A = [Vector((2 * XC - q.x, q.y, q.z)) for q in A]
            B = [Vector((2 * XC - q.x, q.y, q.z)) for q in B]
        va = [bm.verts.new(q) for q in A]
        vb = va if G <= 1e-9 else [bm.verts.new(q) for q in B]
        profs.append(va + vb[::-1])
    mats = {k: a._mi(k) for k in set(_EDGE_KEYS)}
    faces = []
    n = len(profs[0])
    for j in range(len(profs) - 1):
        p, q = profs[j], profs[j + 1]
        for k in range(n):
            uniq = list(dict.fromkeys([p[k], p[(k + 1) % n], q[(k + 1) % n], q[k]]))
            if len(uniq) < 3:
                continue
            f = bm.faces.new(uniq)
            f.material_index = mats[_EDGE_KEYS[k]]
            faces.append(f)
    for pr in (profs[0], profs[-1]):
        uniq = list(dict.fromkeys(pr))
        if len(uniq) == n:
            f = bm.faces.new(uniq)
            f.material_index = mats[CORE]
            faces.append(f)
    vs = list({v for f in faces for v in f.verts})
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    if sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in faces) < 0:
        bmesh.ops.reverse_faces(bm, faces=faces)
    bmesh.ops.triangulate(bm, faces=[f for f in faces if f.is_valid and len(f.verts) > 3])
    for f in K.faces_of(vs):
        f.smooth = False
        for l in f.loops:
            l[a.tint_layer] = (1.0, 1.0, 1.0, 1.0)
    return vs


# seams: (az, el, G) from low to the crown opening; G opens behind the rocks and runs into the crown opening.
# The right seam is cut on FR and BR; the left seam is its exact mirror (FL; BL gets it by being the mirrored BR).
SEAM_DEPTH = 1.25
SEAMS = {
    "right": [(SEAM_AZ["right"], el, g) for el, g in ((-14, 0.0), (-6, 0.36), (12, 0.5), (30, 0.4), (50, 0.48),
                                                     (64, 0.42), (76, 0.5))],
    # (verifier round 1: run open into the crown, its V notch showed on the front silhouette at mid-width - 0.80 of
    # the height against the sheet's 1.0; it now closes over el 64-72, below the raised back crown)
    "back": [(SEAM_AZ["back"], el, g) for el, g in ((-12, 0.0), (-4, 0.38), (16, 0.48), (36, 0.38), (54, 0.5),
                                                   (64, 0.36), (72, 0.0))],
    "front": [(SEAM_AZ["front"], el, g) for el, g in ((-16, 0.0), (-8, 0.36), (10, 0.48), (40, 0.42), (56, 0.48),
                                                     (68, 0.4), (78, 0.5))],
}
PIECE_SEAMS = {"FL": ("front", "left"), "FR": ("front", "right"), "BR": ("right", "back")}
# cracks inside a piece: (az, el, G); crack 1 on FL (boulder | sliver), the BR crack (mirrored onto BL)
CRACK_DEPTH = 1.0
CRACKS = {
    "FL": ((-117, 34, 0.0), (-119, 29, 0.42), (-124, 18, 0.3), (-133, 7, 0.36), (-130, -4, 0.26), (-129, -12, 0.18),
           (-129, -18, 0.0)),
    "BR": ((53, 66, 0.0), (49, 60, 0.26), (37, 44, 0.34), (31, 28, 0.3), (35, 15, 0.24), (37, 5, 0.16),
           (38, -3, 0.0)),
}
ST = {}                         # slot stations by name, in the build frame (crack_probe)


def _cutters(a, piece, tree):
    for s in PIECE_SEAMS[piece]:
        if s == "left":
            _tube(a, ST["right"], chamfer=False, mirror=True)
        else:
            _tube(a, ST[s], chamfer=False)
    if piece in CRACKS:
        _tube(a, ST["crack_" + piece], chamfer=True)


CAP_MARGIN = 0.15       # a slot floor stays at least this far short of the hollow or an opening it doesn't enter
CAP_MIN = 0.35          # (but never shallower than this)


def _inside(tree, q):
    loc, nrm, _i, _d = tree.find_nearest(q)
    return loc is not None and (q - loc).dot(nrm) < 0


def _cap(st, trees):
    """Each station's depth capped at the shell's thickness below it: rays along -n from the station's centre and its
    two lip corners to the hollow and to every opening the point is not already inside, minus CAP_MARGIN. (Verifier
    round 1: crack 1's upper stations, 1.0 deep where FL is only about 0.8 thick beside the front window, broke into
    the hollow - a see-through hole in the Slab part, genus 1.) Returns the new stations and how many were capped."""
    out, n = [], 0
    for p, nrm, t, G, d in st:
        s = nrm.cross(t).normalized()
        tmin = math.inf
        for q in (p, p + s * (G / 2), p - s * (G / 2)):
            for tr in trees:
                if _inside(tr, q):
                    continue
                h = tr.ray_cast(q, -nrm, 6.0)
                if h[0] is not None:
                    tmin = min(tmin, h[3])
        dd = min(d, max(CAP_MIN, tmin - CAP_MARGIN))
        n += dd < d - 1e-6
        out.append((p, nrm, t, G, dd))
    return out, n


def _slots():
    tree = _tree(dome)
    ST.clear()
    caps = [_tree(_hollow)] + [_tree(lambda a, k=k: _opening(a, k)) for k in OPENINGS]
    INFO["capped"] = {}
    for s, ctrl in SEAMS.items():
        ST[s], INFO["capped"][s] = _cap(stations(tree, ctrl, SEAM_DEPTH, plane=(s == "back"), step=SEAM_STEP), caps)
    for p, ctrl in CRACKS.items():
        ST["crack_" + p], INFO["capped"]["crack_" + p] = _cap(stations(tree, ctrl, CRACK_DEPTH), caps)
    return tree


# ---- pieces -----------------------------------------------------------------------------------------------------------
def _tmp(name, fn):
    old = bpy.data.objects.get(name)
    if old:
        me = old.data
        bpy.data.objects.remove(old, do_unlink=True)
        if me.users == 0:
            bpy.data.meshes.remove(me)
    a = K.fk().Asset(name, "probe", tint_var=0.0)
    fn(a)
    return a.finish(collection=M.coll(NUM, TITLE), mark_asset=False, origin=None)


def _bool(o, other, op, self_x=False):
    m = o.modifiers.new("B", "BOOLEAN")
    m.operation, m.solver, m.object = op, "EXACT", other
    m.use_self, m.material_mode = self_x, "TRANSFER"
    with M._override(o):
        bpy.ops.object.modifier_apply(modifier=m.name)
    me = other.data
    bpy.data.objects.remove(other, do_unlink=True)
    if me.users == 0:
        bpy.data.meshes.remove(me)


def piece_obj(piece):
    """One shell piece as a temporary build-frame object: dome ∩ sector − hollow − openings − slots, floor-cut."""
    tree = _slots() if not ST else None
    o = _tmp(f"_m015_piece_{piece}", dome)
    _bool(o, _tmp("_m015_sector", lambda a: _prism(a, _sector_poly(piece))), "INTERSECT")
    _bool(o, _tmp("_m015_hollow", _hollow), "DIFFERENCE")
    if piece == "FR":
        # the front and side frusta as one cutter, the pillar taken out of it, then the crown. (Cutting them one by
        # one, each minus the pillar, left a crossing face pair on FR's hollow that grew to 5 in the cleanup; the
        # hero's exact union then returned an empty mesh for core u FR and dropped the core.)
        cut = _tmp("_m015_open", lambda a: [_opening(a, k) for k in ("front", "side")])
        M.union_loose(cut)
        _bool(cut, _tmp("_m015_pillar", _pillar), "DIFFERENCE")
        _bool(o, cut, "DIFFERENCE")
        _bool(o, _tmp("_m015_open", lambda a: _opening(a, "crown")), "DIFFERENCE")
    else:
        for k in PIECE_OPENINGS[piece]:
            _bool(o, _tmp("_m015_open", lambda a, k=k: _opening(a, k)), "DIFFERENCE")
    _bool(o, _tmp("_m015_cut", lambda a: _cutters(a, piece, tree)), "DIFFERENCE", self_x=True)
    m014._floor_cut(o, 0.0)
    M.union_loose(o)
    m012._drop_inner(o)          # crumbs the openings cut loose (under 2 % of the piece's area)
    return o


def _paste_tmp(name):
    return lambda a: m011._paste(a, bpy.data.objects[name], Matrix.Identity(4))


def slab(a):
    return _paste_tmp("_m015_piece_FL")(a)


def cap(a):
    return _paste_tmp("_m015_piece_FR")(a)


def chunk(a):
    return _paste_tmp("_m015_piece_BR")(a)


PIECE_PART = {"FL": ("EmberMeteorSlab", slab), "FR": ("EmberMeteorCap", cap), "BR": ("EmberMeteorChunk", chunk)}


# ---- Base Rock --------------------------------------------------------------------------------------------------------
ROCK_DIM = dict(size=(2.4, 2.2, 1.3), seed=15051)
ROCK_RINGS = [(0.0, 0.94, 8), (0.3, 1.0, 8), (0.62, 0.84, 7), (0.86, 0.55, 5), (1.0, 0.24, 3)]
ROCK_MERGE = 3.0


def base_rock(a):
    vs = K.hull_rock(a, ROCK_DIM["size"], seed=ROCK_DIM["seed"], mat=BASE, rings=ROCK_RINGS, jitter=0.07,
                     lean=(0.14, 0.08), keep_bottom=True)
    faces = K.faces_of(vs)
    bmesh.ops.dissolve_limit(a.bm, angle_limit=math.radians(ROCK_MERGE), verts=vs,
                             edges=_edges_in_order(a.bm, faces))
    vs = [v for v in vs if v.is_valid]
    INFO["rock_facets"] = len(K.faces_of(vs))
    bmesh.ops.triangulate(a.bm, faces=[f for f in K.faces_of(vs) if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(a.bm, faces=K.faces_of(vs))
    for f in K.faces_of(vs):
        for l in f.loops:
            l[a.tint_layer] = (1.0, 1.0, 1.0, 1.0)
    return vs


# low stones round the foot: (label, azimuth deg about the dome centre, distance from it, W, D, H, yaw, mirror)
# (build fixes, verifier round 1: the ring covered 13-16 % of our silhouette against the sheet's 26-29 %, the front
# rock tops 0.23 H against 0.39. Every stone is broader; F4, front right, 2.6 tall (0.35 H); F2, S1, B2, B4 at
# 0.25-0.3 H; the rest 0.2 H. The front and back rows sit 0.15-0.65 closer in, so the hero's depth stays
# within 10.0 +- 0.6.)
ROCKS = (
    ("F1", 200, 4.7, 2.6, 2.3, 1.6, 20.0, False),
    ("F2", 238, 4.6, 3.2, 2.6, 1.95, -30.0, True),
    ("F3", 262, 4.45, 2.8, 2.3, 1.4, 10.0, False),
    ("F4", 294, 5.0, 3.8, 3.2, 2.6, 140.0, False),      # (4.7: 0.08 from the core; 5.0 keeps >= 0.2)
    ("F5", 318, 5.6, 1.5, 1.3, 0.9, 60.0, True),
    ("S1", 345, 4.75, 2.9, 3.0, 1.95, 95.0, False),
    ("S2", 12, 5.0, 1.6, 1.5, 1.1, 200.0, True),
    ("B1", 38, 4.7, 2.6, 2.4, 1.7, 250.0, False),
    ("B2", 66, 4.45, 3.6, 2.8, 2.25, 190.0, True),
    ("B3", 93, 4.3, 2.6, 2.2, 1.5, 300.0, False),
    ("B4", 122, 4.45, 3.3, 2.6, 1.95, 170.0, True),
    ("B5", 158, 4.7, 2.6, 2.4, 1.6, 75.0, False),
    ("P1", 100, 5.05, 1.1, 1.0, 0.7, 30.0, True),
)
ROCK_SINK = 0.3
ROCK_OUT = -0.3       # (round-1 fixes: the bigger stones at +0.3 made the hero 12.2 x 11.7, over the 12.0 x 10.6
#                         bands; pulled in, they also sink a little deeper into the foot)
ROCK_SCALE = 1.0


# ---- hero ----------------------------------------------------------------------------------------------------------------
def _frame(o):
    return Matrix.Translation(Vector(o[OFF]))


def _part_dims(o):
    m = _frame(o)
    ps = [m @ v.co for v in o.data.vertices]
    return Vector([max(p[i] for p in ps) - min(p[i] for p in ps) for i in range(3)])


SINK = 0.05                     # the pieces go this far below the ground in the hero, so the floor cut never runs
#                                 along their own flat bottoms (coplanar faces in the bisect)
MIRROR = Matrix.Translation((2 * XC, 0, -SINK)) @ Matrix.Diagonal((-1.0, 1.0, 1.0, 1.0))


def _rock_place(k, part):
    _, az, dist, w, d, h, yaw, mirror = ROCKS[k]
    pd = _part_dims(part)
    pre = Matrix.Diagonal((-1.0, 1.0, 1.0, 1.0)) if mirror else Matrix.Identity(4)
    a = math.radians(az)
    dist += ROCK_OUT
    x, y = XC + math.cos(a) * dist, YC + math.sin(a) * dist * DOME["ry"] / DOME["rx"]
    w, d, h = w * ROCK_SCALE, d * ROCK_SCALE, h * ROCK_SCALE
    return (Matrix.Translation((x, y, -ROCK_SINK)) @ Matrix.Rotation(math.radians(yaw), 4, "Z") @
            Matrix.Diagonal((w / pd.x, d / pd.y, (h + ROCK_SINK) / pd.z, 1.0)) @ pre)


def placements():
    """name -> (part object name, matrix from the part's mesh coordinates into the hero's build frame)."""
    out = {}
    for key, (part, _fn) in PIECE_PART.items():
        out[key] = (part, Matrix.Translation((0, 0, -SINK)) @ _frame(bpy.data.objects[part]))
    br = bpy.data.objects["EmberMeteorChunk"]
    out["BL"] = (br.name, MIRROR @ _frame(br))
    out["Core"] = ("EmberCore", Matrix.Translation(CORE_AT) @ _frame(bpy.data.objects["EmberCore"]))
    rock = bpy.data.objects["EmberMeteorBaseRock"]
    for k, r in enumerate(ROCKS):
        out[r[0]] = (rock.name, _rock_place(k, rock) @ _frame(rock))
    return out


def hero(a):
    for name, (part, m) in placements().items():
        m011._paste(a, bpy.data.objects[part], m)


NOTES = {
    "EmberMeteorDeposit": "ember meteor event node: one rounded fractured meteor dome of four thick dark shell pieces "
                          "round a faceted ember core, which glows through a main front opening, small back / side / "
                          "crown openings and thin seams and cracks with real depth; a ring of low pale stones; one "
                          "closed mesh, flat base",
    "EmberMeteorSlab": "Shell Piece A (front-left): thick curved sector of the meteor dome, wrapping from the front "
                       "opening round the left side, with a glowing crack slot down its front",
    "EmberMeteorCap": "Shell Piece B (front-right): thick sector of the meteor dome between the front and side openings",
    "EmberMeteorChunk": "Shell Piece C (back-right, also used mirrored at the back-left): the tallest sector of the "
                        "meteor dome, a glowing crack slot running diagonally down its back flank",
    "EmberCore": "Ember Core (reusable): chunky faceted ball, about 30 broad facets, hot crown, deep underside",
    "EmberMeteorBaseRock": "Base Rock (reusable): low rounded faceted stone, blunt off-centre crown, flat bottom",
}


# ---- cleanup --------------------------------------------------------------------------------------------------------
WALL_KEYS = (LIP, WALL)
CLEAN_MOVE = 0.1


def _keys(o):
    return [(m.get("flintkit_key") or m.name[3:]) if m else "" for m in o.data.materials]


def _clean(o, planes=()):
    """m011._clean with the slot wall rows locked (colour geometry) and the given z planes kept flat."""
    keys = _keys(o)
    wall = {i for i, k in enumerate(keys) if k in WALL_KEYS}
    plane = m011._plane_lock(planes)

    def movable(v, co):
        if any(f.material_index in wall for f in v.link_faces):
            return False
        return plane(v, co)
    ears = m014._dissolve_ears(o)
    pockets = m012._drop_inner(o)
    log = m011._clean(o, movable, max_move=CLEAN_MOVE)
    pockets += m012._drop_inner(o)
    log.update(ears=ears, pockets=pockets, nonmanifold_left=M.repair_nonmanifold(o))
    return log


def _fill_holes(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bnd = [e for e in bm.edges if e.is_boundary]
    n = len(bnd)
    if bnd:
        if not bmesh.ops.holes_fill(bm, edges=bnd)["faces"]:
            bmesh.ops.contextual_create(bm, geom=bnd)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY")
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(o.data)
    bm.free()
    return n


def _ground_keys(o):
    """Floor-cap faces take the key of the wall they close (spread inwards ring by ring)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    ground = {f for f in bm.faces if all(abs(v.co.z) < 1e-4 for v in f.verts)}
    done = {}
    for _ in range(200):
        new = {}
        for f in ground - set(done):
            ks = [g.material_index if g not in ground else done.get(g) for e in f.edges for g in e.link_faces
                  if g is not f]
            ks = [k for k in ks if k is not None]
            if ks:
                new[f] = max(set(ks), key=ks.count)
        if not new:
            break
        done.update(new)
    for f, k in done.items():
        f.material_index = k
    bm.to_mesh(o.data)
    bm.free()
    return len(done)


def _ground_slivers(o, lim=3.0, max_len=0.2):
    """A thin floor-cap triangle fanned onto a short ground edge (where a rock's union meets a piece's wall at the
    ground, 0.1 apart): merge that edge's two ground verts at its middle (each moves at most max_len / 2 along the
    ground). Returns the number merged."""
    n = 0
    for _ in range(10):
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bad = [f for f in bm.faces if all(abs(v.co.z) < 1e-4 for v in f.verts) and m011._fmin(f) < math.radians(lim)]
        done = False
        for f in bad:
            e = min(f.edges, key=lambda x: x.calc_length())
            a, b = e.verts
            na = {x.other_vert(a) for x in a.link_edges}
            nb = {x.other_vert(b) for x in b.link_edges}
            if e.calc_length() <= max_len and len(na & nb) == 2:
                bmesh.ops.pointmerge(bm, verts=[a, b], merge_co=(a.co + b.co) / 2)
                n += 1
                done = True
                break
            # else flip a long edge shared with another floor face (both flat on the ground, so the surface stays
            # exactly where it is) when that opens the worse corner
            for le in sorted(f.edges, key=lambda x: -x.calc_length()):
                g = next((x for x in le.link_faces if x is not f), None)
                if g is None or len(g.verts) != 3 or not all(abs(v.co.z) < 1e-4 for v in g.verts):
                    continue
                A, B = le.verts
                c = next(v for v in f.verts if v not in le.verts)
                d = next(v for v in g.verts if v not in le.verts)
                if bm.edges.get((c, d)):
                    continue
                old = min(m011._fmin(f), m011._fmin(g))
                new = min(m011._min_angle([A.co, c.co, d.co]), m011._min_angle([c.co, B.co, d.co]))
                ok = all(m011._normal(q).z * f.normal.z > 0 for q in ([A.co, c.co, d.co], [c.co, B.co, d.co])) or \
                    all(m011._normal(q).z * f.normal.z < 0 for q in ([A.co, c.co, d.co], [c.co, B.co, d.co]))
                if new > old and ok and bmesh.ops.rotate_edges(bm, edges=[le], use_ccw=False)["edges"]:
                    n += 1
                    done = True
                    break
            if done:
                break
            # else (a fan onto a short edge no flip can open): split its two long edges, which lie flat on the
            # ground, at their middles, so the triangle on the short edge is half as long
            longs = sorted(f.edges, key=lambda x: -x.calc_length())[:2]
            if all(all(abs(v.co.z) < 1e-4 for x in le.link_faces for v in x.verts) for le in longs):
                res = bmesh.ops.subdivide_edges(bm, edges=longs, cuts=1, use_grid_fill=False)
                bmesh.ops.triangulate(bm, faces=[x for x in bm.faces if len(x.verts) > 3], quad_method="BEAUTY",
                                      ngon_method="BEAUTY")
                n += 1
                done = True
                break
        if done:
            bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-5)
            bm.to_mesh(o.data)
        bm.free()
        if not done:
            break
    return n


def _finish(o):
    _ground_slivers(o)
    _fill_holes(o)
    o[OFF] = list(Vector(o[OFF]) + m012._bottom_centre(o))
    res = M.finish(o, union=False, uv=False)      # (the UVs are made by _polish)
    for _ in range(3):
        th = m012._thin(o, 3.0)
        if not (th["under"] or res["boundary_edges"] or res["nonmanifold_edges"]):
            break
        if th["under"]:
            res["forced"] = m012._force_slivers(o, lim=3.0)
        res["filled"] = _fill_holes(o)
        M.repair_nonmanifold(o)
        o[OFF] = list(Vector(o[OFF]) + m012._bottom_centre(o))
        res = M.finish(o, union=False, uv=False)
    return res


def _self_hits(o):
    return m014._self_hits(o)[0]


# ---- stage 2: polish (after _finish and the ground keys) ---------------------------------------------------------------
POLISH_LIM = 5.0        # no corner under this many degrees on any part or the hero
POLISH_ON = True        # False: _polish only re-centres and re-makes the UVs (the stage-1 meshes, for A/B checks)
FEATURE_DEG = 1.0       # an edge is a feature line if its two faces differ in key or bend more than this
SLIDE_ALIGN = 170.0     # a vert on exactly two feature edges this straight may slide along them
SLIDE_STEPS = (0.005, 0.01, 0.02, 0.035, 0.05, 0.08, 0.12)


def _feature_edges(v):
    out = []
    for e in v.link_edges:
        lf = e.link_faces
        if len(lf) != 2 or lf[0].material_index != lf[1].material_index or \
                lf[0].normal.angle(lf[1].normal, 0.0) > math.radians(FEATURE_DEG):
            out.append(e)
    return out


def _slide_dirs(v, f):
    """Moves of v that leave the surface and every key / crease line where they are: within the plane when all its
    faces are one flat facet of one key, along the line when it sits on one straight feature line (a slot row, a lip
    line, a crease, the ground edge). Returns [(unit dir, max length)] or []."""
    fe = _feature_edges(v)
    if not fe:
        nf = f.normal
        es = [(w.co - v.co) for w in f.verts if w is not v]
        es = [e - nf * e.dot(nf) for e in es]
        es = [e.normalized() for e in es if e.length > 1e-9]
        dirs = es + [-e for e in es] + [nf.cross(e).normalized() for e in es] + [-nf.cross(e).normalized() for e in es]
        lim = 0.45 * min(e.calc_length() for e in v.link_edges)
        return [(d, lim) for d in dirs]
    if len(fe) == 2:
        d1, d2 = ((e.other_vert(v).co - v.co) for e in fe)
        if d1.length > 1e-9 and d2.length > 1e-9 and \
                d1.normalized().dot(d2.normalized()) < -math.cos(math.radians(180.0 - SLIDE_ALIGN)):
            return [(d1.normalized(), 0.45 * d1.length), (d2.normalized(), 0.45 * d2.length)]
    return []


def _slide(bm, f, lim):
    """Open the thin face f by sliding one of its corners (any corner, locked rows included) within its own facet
    or along its own feature line: the surface, the slot rows and the key boundaries stay where they are (a straight
    line loses a bend of at most 10 degrees at that vert). Every face round it must end past lim and turn under ~11
    degrees (in-plane moves turn none)."""
    best = None
    for v in f.verts:
        ring = list(v.link_faces)
        old = [x.normal.copy() for x in ring]
        home = v.co.copy()
        for d, mx in _slide_dirs(v, f):
            for s in SLIDE_STEPS:
                if s > mx:
                    break
                p = home + d * s
                if abs(home.z) < 1e-4:
                    if abs(p.z) > 1e-4:
                        continue
                    p.z = home.z
                v.co = p
                worst, ok = math.pi, True
                for x, n0 in zip(ring, old):
                    x.normal_update()
                    if x.normal.length < 1e-9 or x.normal.dot(n0) < 0.98:
                        ok = False
                        break
                    worst = min(worst, m011._fmin(x))
                if ok and worst > lim and (best is None or s < best[0] or (s == best[0] and worst > best[1])):
                    best = (s, worst, v, p.copy())
                if ok and worst > lim:
                    break
        v.co = home
        for x in ring:
            x.normal_update()
    if best:
        best[2].co = best[3]
        for x in best[2].link_faces:
            x.normal_update()
        return True
    return False


NUDGE_FAR = (0.005, 0.01, 0.02, 0.035, 0.05, 0.08, 0.1)    # _nudge_far step sizes (studs)


def _nudge_far(bm, f, lim, locked):
    """The last resort for a free corner of f: m009._nudge_free's move, searched wider (24 directions in the face's
    plane and both normals, steps up to 0.1): the move that leaves the worst corner round that vert best, taken if it
    is past lim, no face round it turns more than about 25 degrees, and ground verts stay on the ground."""
    nf = f.normal.copy()
    t0 = (f.verts[1].co - f.verts[0].co)
    t0 = (t0 - nf * t0.dot(nf)).normalized()
    t1 = nf.cross(t0)
    dirs = [nf, -nf] + [t0 * math.cos(k * math.pi / 12) + t1 * math.sin(k * math.pi / 12) for k in range(24)]
    best = None
    for v in f.verts:
        if v in locked:
            continue
        ring = list(v.link_faces)
        old = [x.normal.copy() for x in ring]
        home = v.co.copy()
        for s in NUDGE_FAR:
            for d in dirs:
                p = home + d * s
                if abs(home.z) < 1e-4:
                    if abs(d.z) > 0.999:
                        continue
                    p.z = home.z
                v.co = p
                worst, ok = math.pi, True
                for x, n0 in zip(ring, old):
                    x.normal_update()
                    if x.normal.length < 1e-9 or x.normal.dot(n0) < 0.9:
                        ok = False
                        break
                    worst = min(worst, m011._fmin(x))
                if ok and worst > lim and (best is None or (s, -worst) < (best[0], -best[1])):
                    best = (s, worst, v, p.copy())
            if best and best[2] is v:
                break
        v.co = home
        for x in ring:
            x.normal_update()
    if best:
        best[2].co = best[3]
        for x in best[2].link_faces:
            x.normal_update()
        return True
    return False


COLLAPSE_LEN = 0.25     # _collapse: a free vert merges onto a neighbour at most this far away
LOCK_MERGE = 0.1        # ... and two verts this close merge even if one is a slot vert (the smallest such move wins)
COLLAPSE_TURN = 0.85    # no face round a collapse turns more than about 32 degrees


def _on_ground(v):
    return abs(v.co.z) < 1e-4


def _collapse(bm, f, locked):
    """Last resort (m012._force_slivers' collapse, with the lock): merge the two ends of one of the thin face f's
    short edges, onto either end or (for an edge under LOCK_MERGE) its middle. A slot vert moves only on an edge
    under LOCK_MERGE; a ground vert never leaves the ground. Taken if the link condition holds, no face round it
    turns more than COLLAPSE_TURN allows, nothing crosses, and the worst corner round it improves; moves of free
    verts first. Returns how far a slot vert moved (0.0 for none), or None."""
    best = None
    for e in sorted(f.edges, key=lambda x: x.calc_length()):
        L = e.calc_length()
        if L > COLLAPSE_LEN or len(e.link_faces) != 2:
            continue
        a, b = e.verts
        na = {x.other_vert(a) for x in a.link_edges}
        nb = {x.other_vert(b) for x in b.link_edges}
        if len(na & nb) != 2:
            continue
        opts = []
        for keep, gone in ((a, b), (b, a)):
            if (gone in locked and L > LOCK_MERGE) or (_on_ground(gone) and not _on_ground(keep)):
                continue
            opts.append((keep.co.copy(), L if gone in locked else 0.0))
        if L <= LOCK_MERGE and _on_ground(a) == _on_ground(b):
            opts.append(((a.co + b.co) / 2, L / 2 if (a in locked or b in locked) else 0.0))
        ring = [x for x in set(a.link_faces) | set(b.link_faces) if not (a in x.verts and b in x.verts)]
        old = min(m011._fmin(x) for x in set(a.link_faces) | set(b.link_faces))
        for pos, lmove in opts:
            ok, worst = True, math.pi
            for x in ring:
                pts = [pos if v in (a, b) else v.co for v in x.verts]
                n = m011._normal(pts)
                if n.length < 1e-12 or n.normalized().dot(x.normal) < COLLAPSE_TURN:
                    ok = False
                    break
                worst = min(worst, m011._min_angle(pts))
            if ok and worst > old:
                key = (lmove > 0, round(lmove, 4), -worst)
                if best is None or key < best[0]:
                    best = (key, a, b, pos, lmove)
    if not best:
        return None
    _, a, b, pos, lmove = best
    ha, hb = a.co.copy(), b.co.copy()
    a.co, b.co = pos, pos
    ring = [x for x in set(a.link_faces) | set(b.link_faces) if not (a in x.verts and b in x.verts)]
    for x in ring:
        x.normal_update()
    bad = _crossing(bm, ring, also={a, b})
    a.co, b.co = ha, hb
    for x in set(a.link_faces) | set(b.link_faces):
        x.normal_update()
    if bad:
        return None
    was = a in locked or b in locked
    bmesh.ops.pointmerge(bm, verts=[a, b], merge_co=pos)
    for v in (a, b):
        if v.is_valid and was:
            locked.add(v)
    return lmove


LOCK_TOL = 1e-3        # a vert this close to a slot cutter's surface is a slot vert (lip line, rows, floor)


def _cutter_tree(o, hero=False):
    """BVH of every slot cutter (seams and cracks, the left seam and BL's crack mirrored) in o's mesh frame."""
    a = K.fk().Asset("_probe", "probe")
    for s in ("right", "back", "front"):
        _tube(a, ST[s], chamfer=False)
    _tube(a, ST["right"], chamfer=False, mirror=True)
    for p in CRACKS:
        _tube(a, ST["crack_" + p], chamfer=True)
    _tube(a, ST["crack_BR"], chamfer=True, mirror=True)
    shift = -Vector(o[OFF]) - (Vector((0.0, 0.0, SINK)) if hero else Vector())
    for v in a.bm.verts:
        v.co += shift
    a.bm.verts.ensure_lookup_table()
    a.bm.faces.ensure_lookup_table()
    t = BVHTree.FromBMesh(a.bm)
    a.bm.free()
    return t


def _crossing(bm, faces, also=()):
    """True if any of `faces` crosses a face of bm that shares none of its verts (nor any vert in `also`)."""
    faces = [x for x in faces if x.is_valid and x.normal.length > 0]
    if not faces:
        return False
    bm.faces.index_update()
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    also = set(also)
    for x in faces:
        vs = list(x.verts)
        sub = BVHTree.FromPolygons([v.co for v in vs], [list(range(len(vs)))])
        for _, j in sub.overlap(tree):
            y = bm.faces[j]
            if y is x or set(y.verts) & (set(vs) | also):
                continue
            return True
    return False


def _guarded(bm, f, fn):
    """Run fn() (a move of one of f's corners); undo it if a face round the moved corner now crosses another."""
    home = {v: v.co.copy() for v in f.verts}
    if not fn():
        return False
    moved = [v for v in home if (v.co - home[v]).length > 1e-12]
    ring = {x for v in moved for x in v.link_faces}
    if _crossing(bm, ring):
        for v in moved:
            v.co = home[v]
        for x in ring:
            x.normal_update()
        return False
    return True


REGION_DEG = 3.5       # a remesh region: faces of one key whose normals are within this of the thin face's
REMESH_ADD = 12         # at most this many new verts per region
WHY = [None]            # why the last _remesh gave up (debug)


def _region(f):
    n0 = f.normal
    reg, stack = {f}, [f]
    while stack and len(reg) < 120:
        x = stack.pop()
        for e in x.edges:
            for g in e.link_faces:
                if g in reg or g.material_index != f.material_index or len(g.verts) != 3 or \
                        g.normal.angle(n0, 0.0) > math.radians(REGION_DEG):
                    continue
                reg.add(g)
                stack.append(g)
    return reg


def _remesh(bm, f, lim, locked):
    """Re-triangulate the near-flat facet round the thin face f (same key, normals within REGION_DEG) without
    moving anything: its outline and every vert on it stay (slot verts inside it too); free interior verts may go;
    new verts are added inside it on the old surface (the circumcentre of the worst triangle, else points along its
    inner edges, else its centroid; never where it would make a triangle under lim with an outline segment, which
    can't be split), and the whole facet becomes a constrained Delaunay triangulation of them (mathutils
    delaunay_2d_cdt in the facet's plane). Taken only if it leaves fewer corners under lim, its worst corner no worse,
    every triangle facing the facet's way and nothing crossing. Returns the number of new verts, or None."""
    from mathutils.geometry import delaunay_2d_cdt, intersect_point_tri_2d
    reg = _region(f)
    n0 = f.normal.copy()
    o0 = f.verts[0].co.copy()
    u = f.verts[1].co - o0
    u = (u - n0 * u.dot(n0)).normalized()
    w = n0.cross(u)

    def to2(p):
        return Vector(((p - o0).dot(u), (p - o0).dot(w)))
    bedges = [e for x in reg for e in x.edges if sum(g in reg for g in e.link_faces) == 1]
    bverts = {v for e in bedges for v in e.verts}
    allv = {v for x in reg for v in x.verts}
    keep = [v for v in allv if v in bverts or v in locked]
    drop = [v for v in allv if v not in bverts and v not in locked]
    idx = {v: i for i, v in enumerate(keep)}
    old_tris = [([to2(v.co) for v in x.verts], [v.co.copy() for v in x.verts]) for x in reg]
    old_worst = min(m011._fmin(x) for x in reg)

    def lift(p):
        for t2, t3 in old_tris:
            if intersect_point_tri_2d(p, *t2):
                a, b, c = t2
                den = (b.y - c.y) * (a.x - c.x) + (c.x - b.x) * (a.y - c.y)
                if abs(den) < 1e-9:
                    continue
                l1 = ((b.y - c.y) * (p.x - c.x) + (c.x - b.x) * (p.y - c.y)) / den
                l2 = ((c.y - a.y) * (p.x - c.x) + (a.x - c.x) * (p.y - c.y)) / den
                # (build fixes, verifier round 1: a near-degenerate old triangle that intersect_point_tri_2d still
                # accepted gave barycentrics of order 1e7, and a "lifted" vertex landed 16 million studs below the
                # Chunk - the exact union of the hero then crashed Blender. Only weights inside the triangle count.)
                if min(l1, l2, 1 - l1 - l2) < -1e-6 or max(l1, l2, 1 - l1 - l2) > 1 + 1e-6:
                    continue
                return t3[0] * l1 + t3[1] * l2 + t3[2] * (1 - l1 - l2)
        return None
    pts2 = [to2(v.co) for v in keep]
    cons = [(idx[e.verts[0]], idx[e.verts[1]]) for e in bedges]
    segs = [(pts2[a], pts2[b]) for a, b in cons]
    added = []
    best = None
    old_bad = sum(1 for x in reg if m011._fmin(x) < lim)
    cset = set(cons) | {(b, a) for a, b in cons}
    from mathutils.geometry import intersect_point_line

    tl = math.tan(lim * 1.2)

    def clear(p):
        """p would not make a triangle under lim with any outline segment it can see (segments can't be split)."""
        if lift(p) is None:
            return False
        for s0, s1 in segs:
            q, t = intersect_point_line(p, s0, s1)
            L = (s1 - s0).length
            # (the triangle p would make with the segment: its corners at both ends must stay past lim)
            if -0.05 < t < 1.05 and (p - q).length < tl * max(t, 1.0 - t) * L:
                return False
        return True

    def steiner(q, allp):
        a2, b2, c2 = (allp[k] for k in q)
        cands = []
        d = 2 * (a2.x * (b2.y - c2.y) + b2.x * (c2.y - a2.y) + c2.x * (a2.y - b2.y))
        if abs(d) > 1e-14:
            ux = (a2.length_squared * (b2.y - c2.y) + b2.length_squared * (c2.y - a2.y) +
                  c2.length_squared * (a2.y - b2.y)) / d
            uy = (a2.length_squared * (c2.x - b2.x) + b2.length_squared * (a2.x - c2.x) +
                  c2.length_squared * (b2.x - a2.x)) / d
            cands.append(Vector((ux, uy)))
        inner = [(q[i], q[(i + 1) % 3]) for i in range(3) if (q[i], q[(i + 1) % 3]) not in cset]
        for a, b in sorted(inner, key=lambda e: -(allp[e[0]] - allp[e[1]]).length):
            for t in (0.5, 0.35, 0.65, 0.2, 0.8):
                cands.append(allp[a].lerp(allp[b], t))
        cands.append((a2 + b2 + c2) / 3)
        for c in cands:
            if clear(c) and min((c - x).length for x in allp) > 1e-3:
                return c
        return None
    for _ in range(REMESH_ADD + 1):
        allp = pts2 + [p for p, _ in added]
        vco, _, faces, orig, _, _ = delaunay_2d_cdt(allp, cons, [], 0, 1e-7)
        if len(vco) != len(allp) or any(len(o_) != 1 for o_ in orig):
            WHY[0] = "cdt merged verts"
            return None
        back = [o_[0] for o_ in orig]
        tris = []
        for t in faces:
            q = [back[k] for k in t]
            c = (allp[q[0]] + allp[q[1]] + allp[q[2]]) / 3
            if lift(c) is not None:
                tris.append(q)
        p3 = [v.co for v in keep] + [p for _, p in added]
        angs = [m011._min_angle([p3[k] for k in q]) for q in tris]
        if not angs:
            WHY[0] = "no triangles"
            return None
        nbad = sum(1 for x in angs if x < lim)
        score = (nbad, -min(angs))
        if best is None or score < best[0]:
            best = (score, min(angs), tris, list(added))
        if not nbad:
            break
        cand = None
        for k in sorted(range(len(tris)), key=lambda k: angs[k]):
            if angs[k] >= lim:
                break
            cand = steiner(tris[k], allp)
            if cand is not None:
                break
        if cand is None:
            break
        added.append((cand, lift(cand)))
    if best is None or best[1] < old_worst - 1e-9 or best[0][0] >= old_bad:
        WHY[0] = ("no gain", old_bad, round(math.degrees(old_worst), 2), best and best[0][0],
                  best and round(math.degrees(best[1]), 2))
        return None
    _, worst, tris, added = best
    # apply: the old faces and free interior verts go, the new verts and triangles come in
    tint = bm.loops.layers.float_color.get("Tint")
    tc = tuple(f.loops[0][tint]) if tint else None
    mat, smooth = f.material_index, f.smooth
    p3 = [v.co for v in keep] + [p for _, p in added]
    for q in tris:
        nq = m011._normal([p3[k] for k in q])
        if nq.length < 1e-12 or nq.normalized().dot(n0) < math.cos(math.radians(10.0)) and \
                (-nq).normalized().dot(n0) < math.cos(math.radians(10.0)):
            WHY[0] = "tilted"
            return None
    bm.faces.index_update()
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    sub = BVHTree.FromPolygons([Vector(p) for p in p3], [list(q) for q in tris])
    for i, j in sub.overlap(tree):
        y = bm.faces[j]
        if y in reg or set(y.verts) & {keep[k] for k in tris[i] if k < len(keep)}:
            continue
        WHY[0] = "crossing"
        return None
    inner_e = [e for x in reg for e in x.edges if all(g in reg for g in e.link_faces)]
    # (round-1 fixes: a locked vert inside the region, all of whose edges are inner edges, would be deleted with them
    # and the rebuilt triangles would reference a dead vert - give up on such a region instead)
    ie = set(inner_e)
    if any(all(e in ie for e in v.link_edges) for v in keep):
        WHY[0] = "locked interior vert"
        return None
    bmesh.ops.delete(bm, geom=list(reg), context="FACES_ONLY")
    inner_e = [e for e in set(inner_e) if e.is_valid]
    if inner_e:
        bmesh.ops.delete(bm, geom=inner_e, context="EDGES")
    loose = [v for v in drop if v.is_valid]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context="VERTS")
    verts = list(keep) + [bm.verts.new(p) for _, p in added]
    for q in tris:
        vs = [verts[k] for k in q]
        if m011._normal([v.co for v in vs]).dot(n0) < 0:
            vs = vs[::-1]
        nf = bm.faces.new(vs)
        nf.material_index, nf.smooth = mat, smooth
        nf.normal_update()
        if tint:
            for lp in nf.loops:
                lp[tint] = tc
    return len(added)


def _wall_verts(o, bm):
    """The locked verts: every vert on a slot cutter's surface (the lip line, chamfer row, the 0.25 / 0.55 wall rows
    and the floor; colour and depth geometry), and every vert on an ember-wall face. The openings' rims and the
    hollow carry the lip key too, but are not slot rows, so they may move like the shell."""
    keys = _keys(o)
    wall = {i for i, k in enumerate(keys) if k == WALL}
    out = {v for f in bm.faces if f.material_index in wall for v in f.verts}
    if not ST:
        _slots()
    t = _cutter_tree(o, hero="EmberMeteorDeposit" in o.name)
    for v in bm.verts:
        hit = t.find_nearest(v.co, LOCK_TOL)
        if hit[0] is not None:
            out.add(v)
    return out


def _polish(o):
    """Stage 2 (m009 pattern, extended): all faces triangles, then every corner under POLISH_LIM opened by the first
    of these that works, least invasive first:
    1. a near-flat same-key flip (m009._flip_thin; the surface moves at most m009.POLISH_TOL);
    2. a slide of a corner within its own flat facet or along its own straight feature line (_slide; slot verts too:
       the surface and every row / key line stay where they are);
    3. a re-triangulation of the near-flat facet round it with new inner verts (_remesh; nothing moves);
    4. a nudge of up to 0.08 of a free corner (m009._nudge_free, `locked` = the slot verts, _wall_verts);
    5. an edge collapse (_collapse: free verts up to COLLAPSE_LEN, two verts under LOCK_MERGE apart even on a slot);
    6. a wider nudge of a free corner (_nudge_far).
    Moves 2, 4 and 6 are undone if they make faces cross; 3 and 5 check before. Ground verts stay on the ground.
    The origin goes back to the bottom centre (the offset follows) and the UVs are re-made (stage 3)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    split = m012._tri_quads(bm)
    locked = _wall_verts(o, bm)
    lim = math.radians(POLISH_LIM)
    log = {"split": split, "flip": 0, "slide": 0, "remesh": 0, "remesh_verts": 0, "nudge": 0, "collapse": 0, "nudge_far": 0, "slot_merge": 0,
           "slot_move_max": 0.0}
    for _ in range(10 if POLISH_ON else 0):
        bad = sorted((f for f in bm.faces if m011._fmin(f) < lim), key=m011._fmin)
        if not bad:
            break
        changed = False
        for f in bad:
            if not f.is_valid or m011._fmin(f) >= lim:
                continue
            if m009._flip_thin(bm, f, lim):
                log["flip"] += 1
            elif _guarded(bm, f, lambda: _slide(bm, f, lim)):
                log["slide"] += 1
            else:
                r = _remesh(bm, f, lim, locked)
                if r is not None:
                    log["remesh"] += 1
                    log["remesh_verts"] += r
                elif _guarded(bm, f, lambda: m009._nudge_free(bm, f, lim, locked)):
                    log["nudge"] += 1
                else:
                    mv = _collapse(bm, f, locked)
                    if mv is None:
                        if _guarded(bm, f, lambda: _nudge_far(bm, f, lim, locked)):
                            log["nudge_far"] += 1
                            changed = True
                        continue
                    log["collapse"] += 1
                    if mv > 0:
                        log["slot_merge"] += 1
                        log["slot_move_max"] = round(max(log["slot_move_max"], mv), 4)
            changed = True
        if not changed:
            break
    left = [f for f in bm.faces if m011._fmin(f) < lim]
    log["left"] = len(left)
    log["left_where"] = [([round(c, 2) for c in f.calc_center_median()], round(math.degrees(m011._fmin(f)), 2),
                          sum(v in locked for v in f.verts)) for f in left[:8]]
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    bc = m012._bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
        o[OFF] = list(Vector(o[OFF]) + bc)
    o.data.update()
    log["min_deg"] = m012._thin(o, POLISH_LIM)["min_deg"]
    log["uv"] = _uv_pass(o)
    return log


# ---- stage 3: UVs -------------------------------------------------------------------------------------------------------
# Smart UV islands made seams, re-unwrapped ANGLE_BASED, margin 0.008 (M011-M014). The island angle per object
# (min_angle = angle, so smart_uv never falls back; folds are cut free by m012._uv_unfold), from 35 / 40 / 45 / 50 /
# 55 on the polished meshes by uv_stats' worst, then p95 conformal stretch, then fewest islands (as M014): hero 35
# (1.054 / 1.007; 45: 1.070 / 1.014), slab 40 (1.033), cap 35 (1.029 / 1.008), chunk 40 (1.018; 45: 1.094), core 50
# (1.000, 8 islands), base rock 35 (1.021; 45: 1.082). Table in M015_spec.md "Stage 2+3".
UV_ANGLE = {"EmberMeteorDeposit": 35.0, "EmberMeteorSlab": 40.0, "EmberMeteorCap": 35.0, "EmberMeteorChunk": 40.0,
            "EmberCore": 50.0, "EmberMeteorBaseRock": 35.0}


def _uv(o):
    a = UV_ANGLE.get(o.name, UV["angle"])
    return dict(UV, angle=a, min_angle=a)


def _uv_pass(o):
    M.smart_uv(o, **_uv(o))
    cut = m012._uv_unfold(o)
    s = M.uv_stats(o)
    return {"angle": _uv(o)["angle"], "cut_free": cut, "islands": s["islands"], "overlaps": s["overlap_pairs"],
            "flipped": s["flipped"], "conformal": (s["stretch_conformal_worst"], s["stretch_conformal_p95"])}


def _interior_faces(o):
    """Faces whose outside lies inside the solid: a point 2e-3 off the face centre along its normal is inside
    (odd ray parity) on at least 2 of 3 ray directions."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    dirs = [Vector(d).normalized() for d in ((0.31, 0.17, 0.93), (-0.62, 0.71, 0.33), (0.45, -0.83, -0.32))]
    n = 0
    for f in bm.faces:
        p0 = f.calc_center_median() + f.normal * 2e-3
        inside = 0
        for d in dirs:
            hits, p = 0, p0.copy()
            for _ in range(400):
                loc, _, idx, _ = tree.ray_cast(p, d)
                if loc is None:
                    break
                hits += 1
                p = loc + d * 1e-5
            inside += hits % 2
        n += inside >= 2
    bm.free()
    return n


# ---- measurement: orthographic label rasters against the sheet's study tables ----------------------------------------
SHEET_PROFILES = {
    "front": (.09, .53, .62, .70, .78, .82, .79, .74, .78, .95, 1.0, .99, .97, .95, .93, .87, .81, .76, .70, .49, .11),
    "side": (.07, .38, .55, .67, .77, .82, .86, .91, .95, .98, .99, .96, .92, .86, .84, .79, .70, .63, .59, .42, .09),
    "rear": (.09, .49, .64, .77, .84, .89, .94, .97, 1.0, .93, .79, .98, .98, .95, .93, .90, .83, .73, .64, .51, .10),
}
SHEET_SHARE = {"front": 0.263, "side": 0.177, "rear": 0.242, "top": 0.270}
SHEET_ASPECT = {"front": 1.34, "side": 1.14, "rear": 1.38, "top": 1.08}
MEASURE_VIEWS = {"front": (0.0, 7.0), "side": (90.0, 7.0), "rear": (180.0, 7.0), "top": (0.0, 78.0)}
MIRRORED = {"side"}
LABEL = {SHELL: 1, CORE: 2, HOT: 2, DEEP: 2, WALL: 2, LIP: 3, BASE: 4}


def _raster(o, az, el, res=240):
    """Orthographic label image of o: 0 empty, 1 shell, 2 glow orange (core keys, ember wall), 3 lip, 4 rock."""
    a, e = math.radians(az), math.radians(el)
    dirv = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
    right = Vector((math.cos(a), math.sin(a), 0.0))
    up = dirv.cross(right).normalized()
    me = o.data
    co = np.array([tuple(v.co) for v in me.vertices])
    P = np.stack([co @ np.array(right), co @ np.array(up), co @ np.array(dirv)], axis=1)
    u0, u1, v0, v1 = P[:, 0].min(), P[:, 0].max(), P[:, 1].min(), P[:, 1].max()
    s = res / (u1 - u0)
    W, H = res + 1, int((v1 - v0) * s) + 1
    zb = np.full((H, W), -1e9)
    lab = np.zeros((H, W), np.uint8)
    # (by key family, so stage 4's shades and mixes keep their region: base* rock, ember_lip* lip, ember_wall* and
    # core* glow, the rest shell)
    lbl = [4 if key.startswith(BASE) else 3 if key.startswith(LIP) else 2 if key.startswith((WALL, "m015_core"))
           else 1 for key in _keys(o)]
    for p in me.polygons:
        lb = lbl[p.material_index]
        idx = list(p.vertices)
        for k in range(1, len(idx) - 1):
            t = P[[idx[0], idx[k], idx[k + 1]]]
            x = (t[:, 0] - u0) * s
            y = (t[:, 1] - v0) * s
            xa, xb = int(max(0, math.floor(x.min()))), int(min(W - 1, math.ceil(x.max())))
            ya, yb = int(max(0, math.floor(y.min()))), int(min(H - 1, math.ceil(y.max())))
            den = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
            if abs(den) < 1e-12:
                continue
            gx, gy = np.meshgrid(np.arange(xa, xb + 1) + 0.0, np.arange(ya, yb + 1) + 0.0)
            l1 = ((y[1] - y[2]) * (gx - x[2]) + (x[2] - x[1]) * (gy - y[2])) / den
            l2 = ((y[2] - y[0]) * (gx - x[2]) + (x[0] - x[2]) * (gy - y[2])) / den
            l3 = 1 - l1 - l2
            inside = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
            d = l1 * t[0, 2] + l2 * t[1, 2] + l3 * t[2, 2]
            sub = zb[ya:yb + 1, xa:xb + 1]
            upd = inside & (d > sub)
            sub[upd] = d[upd]
            lab[ya:yb + 1, xa:xb + 1][upd] = lb
    return lab


def _runs(row):
    out, start = [], None
    for i, v in enumerate(row):
        if v and start is None:
            start = i
        elif not v and start is not None:
            out.append((start, i - 1))
            start = None
    if start is not None:
        out.append((start, len(row) - 1))
    return out


def silhouette(o, az, el, mirrored=False, res=240):
    lab = _raster(o, az, el, res)
    if mirrored:
        lab = lab[:, ::-1]
    H, W = lab.shape
    filled = lab > 0
    prof, rocks = [], []
    for k in range(21):
        c = min(W - 1, int(round(k / 20 * (W - 1))))
        rows = np.nonzero(filled[:, c])[0]
        prof.append(round(float(rows.max() / (H - 1)), 2) if len(rows) else 0.0)
        col = lab[:, c]
        top = None
        for r in range(H):
            if col[r] == 4:
                top = r
            elif col[r]:
                break
        rocks.append(round(top / (H - 1), 2) if top is not None else None)
    met = (lab == 1) | (lab == 2) | (lab == 3)
    glow = lab == 2
    out = {"aspect": round(W / H, 2), "profile": prof, "rock_tops": rocks,
           "share": round(float(glow.sum() / max(1, met.sum())), 3),
           "lip_share": round(float((lab == 3).sum() / max(1, met.sum())), 3),
           "rock_share": round(float((lab == 4).sum() / max(1, filled.sum())), 3)}
    mc = np.nonzero(met.any(axis=0))[0]
    mr = np.nonzero(met.any(axis=1))[0]
    out["meteor_w_h"] = round(float((mc.max() - mc.min()) / max(1, mr.max() - mr.min())), 2) if len(mc) else None
    rows = {}
    for h in (0.2, 0.25, 0.35, 0.45, 0.49, 0.58, 0.62, 0.7, 0.76, 0.82, 0.9):
        r = int(round(h * (H - 1)))
        rows[h] = [(round(a / (W - 1), 2), round(b / (W - 1), 2)) for a, b in _runs(glow[r]) if b - a >= 1]
    out["glow_runs"] = rows
    return out


def measure(o=None):
    o = o or bpy.data.objects["EmberMeteorDeposit"]
    out = {}
    for v, (az, el) in MEASURE_VIEWS.items():
        s = silhouette(o, az, el, v in MIRRORED)
        if v in SHEET_PROFILES:
            err = [abs(a - b) for a, b in zip(s["profile"], SHEET_PROFILES[v])]
            s["prof_err"] = (round(sum(err) / len(err), 3), round(max(err), 2))
        s["sheet_share"], s["sheet_aspect"] = SHEET_SHARE[v], SHEET_ASPECT[v]
        out[v] = s
    for v, (az, el) in {"f34": (-14.0, 10.0), "r34": (166.0, 10.0)}.items():
        s = silhouette(o, az, el)
        out[v] = {"aspect": s["aspect"], "share": s["share"]}
    return out


SIGHT_VIEWS = ((0, 7), (90, 7), (180, 7), (-90, 7), (0, 78), (0, 89), (-45, 20), (45, 20), (135, 20), (-135, 20),
               (-14, 10), (166, 10), (-28, 12), (152, 12), (-45, 45), (135, 45))


def see_through(o, views=SIGHT_VIEWS, res=420):
    """Straight-through sightlines: for each view (azimuth, elevation) the object's orthographic coverage mask
    (`_raster`, res pixels across, about 0.03 stud on the hero); an empty pixel enclosed by covered ones (a hole in
    the mask, not connected to its border) is a line of sight straight through. Returns {view: hole pixels} for the
    views with any (pixels are about res / width per stud)."""
    out = {}
    for az, el in views:
        lab = _raster(o, az, el, res)
        empty = lab == 0
        seen = np.zeros_like(empty)
        seen[0, :], seen[-1, :], seen[:, 0], seen[:, -1] = empty[0, :], empty[-1, :], empty[:, 0], empty[:, -1]
        while True:
            grow = seen.copy()
            grow[1:, :] |= seen[:-1, :]
            grow[:-1, :] |= seen[1:, :]
            grow[:, 1:] |= seen[:, :-1]
            grow[:, :-1] |= seen[:, 1:]
            grow &= empty
            if (grow == seen).all():
                break
            seen = grow
        n = int((empty & ~seen).sum())
        if n:
            out[f"{az},{el}"] = n
    return out


def gaps():
    """The core against each rock (nearest distance, >= 0.2 wanted) and the shell pieces' overlap with the core."""
    trees = {}
    for name, (part, m) in placements().items():
        o = bpy.data.objects[part]
        vs = [m @ v.co for v in o.data.vertices]
        polys = [list(p.vertices) for p in o.data.polygons]
        if m.to_3x3().determinant() < 0:
            polys = [p[::-1] for p in polys]
        trees[name] = (BVHTree.FromPolygons(vs, polys), vs)
    ct, cv = trees["Core"]
    # (the shells' overlap with the core is fixed by construction: each piece's hollow is the core scaled HOLLOW, so
    # its inner face sits (1 - HOLLOW) x the core's radius, 0.24-0.27, inside the core; a nearest-face probe through
    # the slotted pieces gave meaningless depths)
    out = {"core_to_rock": {}, "core_touches": {}}
    for r in ROCKS:
        t, vs = trees[r[0]]
        out["core_to_rock"][r[0]] = -1.0 if ct.overlap(t) else round(min(ct.find_nearest(p)[3] for p in vs), 2)
    for sh in ("FL", "FR", "BR", "BL"):
        out["core_touches"][sh] = bool(ct.overlap(trees[sh][0]))
    return out


def crack_probe(h=None, n=5):
    """BVH ray pairs across each seam and crack in the hero (n stations along the open run): lip-to-lip opening,
    floor width, depth from the uncut dome surface to the floor."""
    h = h or bpy.data.objects["EmberMeteorDeposit"]
    off = Vector(h[OFF])
    bm = bmesh.new()
    bm.from_mesh(h.data)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    out = {}
    for name, st in ST.items():
        open_ = [s for s in st if s[3] > 1e-9]
        rows = []
        for i in range(n):
            p, nrm, t, G, d = open_[int(round(i * (len(open_) - 1) / (n - 1)))]
            P = p - off
            S = nrm.cross(t).normalized()
            hit = tree.ray_cast(P + nrm * 1.5, -nrm, 8.0)
            dep = round(hit[3] - 1.5, 2) if hit[0] is not None else None

            def width(q):
                a = tree.ray_cast(q, S, 2.0)
                b = tree.ray_cast(q, -S, 2.0)
                return round((a[3] if a[0] else 2.0) + (b[3] if b[0] else 2.0), 2)
            rows.append({"at": [round(c, 2) for c in p], "G": round(G, 2), "opening": width(P - nrm * 0.05),
                         "floor": width(P - nrm * (dep - 0.05)) if dep and dep > 0.2 else None, "depth": dep})
        out[name] = rows
    bm.free()
    return out


# ---- stage 4: materials, colour and texture ------------------------------------------------------------------------
# Calibration (K.calibrate on the kit's test dome, through calibrate() below). Targets are the sheet's RENDERED
# medians (M015_spec.md §5.2 / §5.4), not the swatches. key -> (sRGB, kind)
TARGETS = {SHELL: ((0x5F, 0x58, 0x5E), "stone"), SHELL_LIGHT: ((0x7C, 0x73, 0x78), "stone"),
           SHELL_DARK: ((0x45, 0x40, 0x4A), "stone"), SHELL_WARM: ((0x68, 0x5D, 0x5E), "stone"),
           LIP: ((0x5E, 0x26, 0x20), "vivid"), WALL: ((0xD8, 0x5A, 0x22), "vivid"),
           CORE: ((0xFD, 0x74, 0x28), "vivid"), HOT: ((0xFD, 0xB5, 0x48), "vivid"),
           DEEP: ((0xD9, 0x44, 0x1A), "vivid"), BASE: ((0xB3, 0x9A, 0x8F), "stone"),
           BASE_LIGHT: ((0xC8, 0xAF, 0xA3), "stone"), BASE_DARK: ((0x8F, 0x78, 0x6D), "stone")}


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS), with the Neon preview kept on every round (m009 / m014). Stone
    keys are sampled unfiltered (the test box lies wholly on the dome; K.sample's sat < 0.18 stone filter drops the
    warm base rock, sat up to 0.24). Returns {key: (hex, rendered)}; the orphaned test-dome meshes are purged."""
    keys = keys or list(TARGETS)
    for k in keys:
        _restyle(k)
    set0, sample0 = K.set_colour, K.sample

    def set_colour(key, hexcol, **kw):
        set0(key, hexcol, **kw)
        _glow_mats()

    def sample(src, box, kind="green"):
        return M.sample(src, box, "all", paper=(255, 253, 240), tol=6) if kind == "stone" else \
            sample0(src, box, kind)
    K.set_colour, K.sample = set_colour, sample
    try:
        for k in keys:
            K.fk().material(k)
        _glow_mats()
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        K.set_colour, K.sample = set0, sample0
        _drop_calib()


def _drop_calib():
    """K.calibrate removes its test dome object but not its mesh: purge the orphan T_Calib meshes that carry only
    this model's keys."""
    gone = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")
            and all(x is None or x.name.startswith("FB_m015_") for x in m.materials)]
    for m in gone:
        bpy.data.meshes.remove(m)
    return len(gone)


# Every field is a position. Shell, slot and rim faces are coloured in the shared piece build frame (a part's mesh
# coords + its offset; the hero's + its offset + SINK), so the parts and the hero carry the same colouring where they
# coincide; the core in the core-centred frame; each base rock in the rock part's own mesh frame. Faces are first
# classified by the construction surface they lie on (_classify), never by key or facing, so the pass repeats.
KIND = {"EmberMeteorDeposit": "hero", "EmberMeteorSlab": "FL", "EmberMeteorCap": "FR", "EmberMeteorChunk": "BR",
        "EmberCore": "core", "EmberMeteorBaseRock": "rock"}
SINKV = Vector((0.0, 0.0, SINK))
ON_TOL = 0.03           # a face lies on a construction surface if its centre is this close (polish nudges <= 0.1)
SLOT_TOL = 2e-3         # slot faces are locked to their cutter (stage 2)
DOME_TOL = 0.15         # a shell face this close to the dome is outer surface; deeper ones are the seam hairlines
STEPS = 3


def _q(t):
    return round(min(1.0, max(0.0, t)) * (STEPS + 1)) / (STEPS + 1)


def _step(d, ramp):
    for lim, t in ramp:
        if d < lim:
            return t
    return 0.0


def _mirror(v):
    return Vector((2 * XC - v.x, v.y, v.z))


def _slot_runs():
    """(name, stations, mirrored, crack): every slot, with the left seam and BL's crack as mirrored copies."""
    out = [(s, ST[s], False, s.startswith("crack")) for s in ST]
    return out + [("left", ST["right"], True, False), ("crack_BL", ST["crack_BR"], True, True)]


def _core_placed(a):
    vs, _ = _hull(a, [CORE_AT + SINKV + q for q in _core_pts()], CORE_MERGE)
    a._finish(vs, CORE, tint=1.0)
    return vs


G = {}


def _geo():
    """Construction surfaces as BVHs in the piece build frame, and the slot stations (KD tree)."""
    if G:
        return G
    from mathutils.kdtree import KDTree
    if not ST:
        _slots()
    G["dome"] = _tree(dome)
    G["hollow"] = _tree(_hollow)
    G["open"] = {k: _tree(lambda a, k=k: _opening(a, k)) for k in OPENINGS}
    G["open"]["pillar"] = _tree(_pillar)        # the pillar's cut walls are window rims too
    G["core"] = _tree(_core_placed)

    def slots(a):
        for _n, st, mir, crack in _slot_runs():
            _tube(a, st, chamfer=crack, mirror=mir)
    G["slots"] = _tree(slots)
    pts = []
    for name, st, mir, _c in _slot_runs():
        for p, _n, _t, g, d in st:
            pts.append((_mirror(p) if mir else p.copy(), g, d, name))
    kd = KDTree(len(pts))
    for i, x in enumerate(pts):
        kd.insert(x[0], i)
    kd.balance()
    G["st"], G["st_kd"] = pts, kd
    return G


def _paint_off(o):
    k = KIND[o.name]
    off = Vector(o[OFF]) if OFF in o else Vector()
    if k == "hero":
        return off + SINKV
    if k == "core":
        return off + CORE_AT + SINKV
    return off          # the pieces: their build frame; the rock part: its own mesh frame (offset 0)


def _on(tree, c, tol):
    return tree.find_nearest(c, tol)[0] is not None


def _pillar_wall(c):
    """Which of the FR pillar's two cut walls a point lies on: "_f" (the PILLAR_AZ[0] plane, the front window's side)
    or "_s" (the PILLAR_AZ[1] plane, the side window's side). By construction surface, as the rims are."""
    d = []
    for az in PILLAR_AZ:
        n = Vector((-math.sin(math.radians(az)), math.cos(math.radians(az))))
        d.append(abs((Vector((c.x, c.y)) - Vector((XC, YC))).dot(n)))
    return "_f" if d[0] <= d[1] else "_s"


def _classify(o, p):
    """Per face: rock, core, ground, slot, rim_<opening>, hollow, dome or sector (the hidden seam hairline walls)."""
    g = _geo()
    kind = KIND[o.name]
    out = {}
    for f in p.bm.faces:
        c = p.at(f)
        if kind == "rock" or (kind == "hero" and p.key(f).startswith(BASE)):
            cl = "rock"
        elif kind == "core" or (kind == "hero" and _on(g["core"], c, ON_TOL)):
            cl = "core"
        elif all(v.co.z < 1e-4 for v in f.verts):
            cl = "ground"
        elif _on(g["slots"], c, SLOT_TOL):
            cl = "slot"
        else:
            cl = next(("rim_" + n for n, t in g["open"].items() if _on(t, c, ON_TOL)), None)
            if cl == "rim_pillar":
                cl += _pillar_wall(c)
            if cl is None:
                if _on(g["hollow"], c, ON_TOL):
                    cl = "hollow"
                elif g["dome"].find_nearest(c)[3] < DOME_TOL:
                    cl = "dome"
                else:
                    cl = "sector"
        out[f] = cl
    return out


# --- shell (outside): broad light / dark patches per facet, a darker ground band among the rocks, warm spill near the
# glow (a window rim, a slot lip or the core); never by facing
# (round 2, verifier round 1: "shell contrast is low": dead zone 0.12 -> 0.05 and width 0.3 -> 0.15, so most facets
# take a full light or dark step, as the sheet's mottled dark shell does)
# (and seed 15061 -> 15071: with the full steps, 15061 put a dark bias on the front quarter (mean tone -0.20, 14 sq
# studs of shell_dark against 5 of shell_light; front shell median 20 levels under the sheet's) and a light one on the
# left (+0.42). Of eight seeds, 15071 is even (front +0.11, back -0.06, left -0.22, right +0.34, 24-37 % full-step
# facets) and keeps K.check's baked-shading score at 0.08 or less; 15121 and 15091 were as even but lit the up-facing
# facets (score 0.37 / 0.42), which reads as painted light)
SHELL_TONE = dict(scale=0.2, seed=15071, dead=0.05, width=0.15)
GROUND_BAND = ((1.0, 0.5), (2.0, 0.25))         # hero z below -> this far towards SHELL_DARK
# distance to the nearest glow surface -> towards SHELL_WARM. (The spec's 0.25 / 0.5 / 0.9 ramp warmed 68 % of the
# outer shell's area: with four seams and two cracks across the dome, most broad facets' centres lie within 0.9 of
# a slot or a rim. The sheet's warm band is 1-10 px, about 0.5 stud.)
SPILL = ((0.2, 0.5), (0.45, 0.25))
SECTOR_DARK = 0.3       # seam hairline walls: SHELL_DARK down to this depth, then LIP
# --- slots: the row by depth below the uncut dome (fraction t of the station's slot depth d): lip | wall | core |
# hot floor; the floor cools to CORE where the slot narrows (its tapered ends, the seams' closed feet)
# (the lip row as plain LIP left the cracks reading as dark grooves from the front: slot median #381511, L share 2x
# the sheet's; the sheet's crack deciles run 1 lip, 2 red-brown, 7 orange / hot. So only the chamfer row (t < 0.07)
# is the dark lip line and the lip row is the lip -> wall 50 % step)
# (Stage 4-6 round 2, verifier round 1: "cracks read as dark grooves, not glowing embers". The lip -> wall 50 % row
# was solid and sat in the slot's own shade, so 81-97 % of crack pixels fell in the dark lip class L against the
# sheet's 16-23 %. Now only the chamfer row is the dark lip line; the walls are Neon from t 0.07: ember_wall to 0.3,
# core below, the hot floor)
# (and the first try with core down to t 0.93 measured no hot crack pixel in any view, where the sheet's crack lit
# quartile is the hot #FAA82E: the floor alone is too narrow to be seen, so the hot row starts at t 0.6, cooling to
# core where the slot narrows, as the floor does)
# (and the rows deeper than the first wall band are hidden from every sheet view: a 0.3-wide, 1.0-deep slot shows
# only its chamfer and the top quarter of its far wall, so moving the hot row from t 0.93 to 0.45 changed no crack
# pixel. The four steps are therefore packed into what is seen: the chamfer the dark lip; the first wall band split
# at its triangles' centres (t 0.08-0.25, centroids at 1/3 and 2/3), the upper ones ember_wall and the lower ones
# core, a red -> orange sawtooth that reads as a gradient along the crack; band 2 and below hot, as the sheet's
# yellow centre line, cooling to core where the slot narrows)
SLOT_ROWS = ((0.07, (LIP, LIP, 0.0)), (0.165, (WALL, WALL, 0.0)), (0.3, (CORE, CORE, 0.0)))
FLOOR_HOT_G = 0.22
# --- window rims (one frustum wall per piece side, cut into many triangles by the booleans): s = 0 at the outer
# dome, 1 at the core. The sheet's rims read lit red-orange next to the core and dark red at the outer lip.
# (solid keys only, so the big rim faces keep their lit facet steps; ember_wall is Neon, stage 5)
# (the outer band as plain LIP gave an L share twice the sheet's, and redder (#5A1B0D against #653735): the spec's
# cavity gradient runs shell -> shell_warm -> ember_lip -> the core's colours, so the outermost band is the
# shell_warm / lip half-step)
# (Stage 4-6 round 2, verifier round 1: the rims gave a dark-red lip share of 9-13 % against the sheet's 6-9 %; the
# rim pixels were 52-69 % L. The sheet's rim walls read red-tinted grey (#625156) at the outer edge and the core's
# glow right at the junction, with only a thin dark red line between. So the outer half is warm shell, a thin lip
# line, then the solid deep orange-red, and the band touching the core glows (Neon ember_wall): the heat at the
# junction, which also widens the windows' glow as the sheet draws them)
# RIM_STEPS[opening] = the s where each band ends: warm shell | shell_warm / lip 50 (the thin dark lip line) |
# lip / deep 75 | core_deep (solid, lit orange-red) | then Neon ember_wall to the core.
RIM_KEYS = ((SHELL_WARM, SHELL_WARM, 0.0), (SHELL_WARM, LIP, 0.5), (LIP, DEEP, 0.75), (DEEP, DEEP, 0.0),
            (WALL, WALL, 0.0))
# Per opening (and per pillar wall, `_pillar_wall`), because the flared rims fill very different shares of each view.
# Measured by making one opening's rims fully Neon and the rest grey (glow-share points added, as % of the meteor):
# front frustum front 3.7 / f34 1.8 / top 1.6; pillar front-side wall front 6.5 / f34 7.9; pillar side-side wall
# side 7.9 only; rear frustum rear 8.2 / r34 10.1; crown top 7.0; side frustum front 8.0 / f34 3.9 / top 3.2 / side
# 1.9. All rims grey: front 22.7, side 6.2, rear 17.1, top 18.2, f34 19.8, r34 13.6 % (sheet 24.5 / 16.3 / 22.4 /
# 23.8 / 20.7 / 15.6). So the walls seen from the front stay warm shell and glow only at the junction; the pillar's
# side wall (the side window's main rim as the side view sees it) glows almost wholly; the rear and crown rims glow
# from mid-wall (the rear less, as it is r34's main rim too).
RIM_STEPS = {"front": (0.62, 0.72, 0.84, 0.92), "pillar_f": (0.62, 0.72, 0.84, 0.92),
             "pillar_s": (0.05, 0.08, 0.1, 0.12), "side": (0.35, 0.45, 0.58, 0.68), "rear": (0.45, 0.55, 0.68, 0.78),
             "crown": (0.1, 0.15, 0.2, 0.25)}
HOLLOW_KEY = (LIP, DEEP, 0.25)
# --- core: u = height fraction + CORE_LAT x lateral towards (+X, +Y) + CORE_NOISE x broad noise; the hero's core
# faces within CORE_OCC of a shell are core_deep (occlusion: the sheet's #9C2509-#BF3E12 strips under the rims)
# (lateral towards (+X, +Y) as the spec put it made the whole back of the core hot: the rear and r34 windows read
# #FFB348, where the sheet's rear core is orange #FB6521 with hot facets only up top; and the front window had no
# hot facet (lit quartile #FF7429 against the sheet's #FDB745). So the lean is towards +X only: the front view's
# upper right, as the sheet draws it.)
# (height at full weight made the whole crown hot: the top view's core read #FFB449 against the sheet's orange
# #FC7325 with hot facets (lit quartile #FECD5A); so height x CORE_UP, and the crown is hot only on its +X side)
# The height term folds back above CORE_CAP (slope CORE_FOLD), so the hot facets are the upper belt on the +X side
# - what the front, f34 and rear windows see (the sheet's window lit quartiles #FDB745 / #FEB140) - and the topmost
# cap stays orange (the top view's median: at hot > 0.6 without the fold it read #FFB348).
# (CORE_LAT 0.35 made the +X side window all hot: core median #FFB349 against the sheet's side #FC6C23; at 0.22 the
# front, side, top and f34 windows all read an orange median with a hot lit quartile, as the sheet's do; 0.15 lost the
# front's hot facets)
# (round 2: with 0.22 / 0.56 the window cores measured lit quartile #FF7429 in every view - no hot facet - against
# the sheet's #FDB745 / #FEB140 / #FECD5A: its cores are hot in the upper middle from every side. So the +X lean is
# halved and the hot band starts lower)
CORE_UP, CORE_LAT, CORE_NOISE, CORE_SCALE, CORE_SEED = 0.75, 0.0, 0.2, 0.35, 15062
CORE_FWD = 0.15         # lean towards the front (-Y)
CORE_CAP, CORE_FOLD = 0.75, 2.0
CORE_BANDS = (0.24, 0.44)
CORE_CAP, CORE_FOLD, CORE_FWD = 0.75, 1.5, 0.07   # (round 2 sweep: the core's 58 facets make the hot share jump a
# facet at a time - front 26 / 53 % at band 0.44 / 0.43 - so the band keeps every window's median orange with hot facets
# in the lit quartile: hot share front 26, f34 21, side 35, rear 18, r34 17, top 41 % against the sheet's 37 / 40 / 29
# / 28 / 30 / 33 %)
CORE_OCC = 0.25
# --- base rocks (each in its own frame): light patches; the ground-contact row and the faces against a shell a
# little darker; the crown never
ROCK_TONE = dict(scale=0.7, seed=15063, dead=0.15, width=0.3)
# height fraction below -> this far towards BASE_DARK. Off: 0.22 / 25 % scored K.check's baked-shading corr 0.80 on
# the 58-tri stone (its low ring is its outward / down-facing ring, as on M009's), so it read as painted shade
ROCK_GROUND = (0.0, 0.0)
ROCK_CREVICE = ((0.25, 0.5), (0.5, 0.25))
ROCK_CROWN = 0.7
# --- Tint: a per-piece level x broad mottling per facet (no per-triangle confetti)
PIECE_TINT = {"FL": 1.0, "FR": 0.97, "BR": 1.03, "BL": 0.98, "core": 1.0, "rock": 1.0,
              "F1": 1.02, "F2": 0.97, "F3": 1.03, "F4": 0.99, "F5": 1.02, "S1": 0.97, "S2": 1.03, "B1": 1.0,
              "B2": 0.97, "B3": 1.02, "B4": 0.99, "B5": 1.03, "P1": 0.98}
MOTTLE = {"shell": dict(amp=0.06, scale=0.45, seed=15064), "rock": dict(amp=0.05, scale=0.6, seed=15065),
          "slot": dict(amp=0.03, scale=0.5, seed=15066), "core": dict(amp=0.03, scale=0.5, seed=15067)}
SHADING_OK = ("crack and rim walls graded by depth below the lip (the sheet's lip -> ember -> orange -> hot "
              "gradient, M015_spec.md §5.5-5.6); the shell's patches follow broad position noise, not facing")


def _facets(faces):
    """m012._facets kept inside `faces` (round 2: m012's flood crosses into any edge-connected coplanar face, so a
    core facet coplanar with the rim triangles next to it painted 17 rear-rim faces core_deep, and Tint groups ran
    across class borders)."""
    allowed = set(faces)
    seen, out = set(), []
    for f in faces:
        if f in seen:
            continue
        g, stack = [], [f]
        seen.add(f)
        while stack:
            x = stack.pop()
            g.append(x)
            for e in x.edges:
                for y in e.link_faces:
                    if y in allowed and y not in seen and y.normal.dot(f.normal) > 0.9995:
                        seen.add(y)
                        stack.append(y)
        out.append(g)
    return out


def _sector_of(c):
    a = math.degrees(math.atan2(c.y - YC, c.x - XC)) % 360.0
    return "FR" if 285.0 <= a < 355.0 else "BR" if (a >= 355.0 or a < 90.0) else "BL" if a < 185.0 else "FL"


class _Rock:
    def __init__(self, label, m, part):
        self.label, self.m, self.inv = label, m, m.inverted()
        ps = [v.co for v in part.data.vertices]
        self.lo = Vector([min(q[i] for q in ps) for i in range(3)])
        self.hi = Vector([max(q[i] for q in ps) for i in range(3)])
        r = random.Random(zlib.crc32(label.encode()))      # (str hash() changes per Blender session)
        self.noff = Vector((r.uniform(0, 50), r.uniform(0, 50), r.uniform(0, 50))) if label != "rock" else Vector()

    def norm(self, q):
        mid, half = (self.lo + self.hi) / 2, (self.hi - self.lo) / 2
        return max(abs(q[i] - mid[i]) / max(half[i], 1e-6) for i in range(3))


def _rocks():
    part = bpy.data.objects["EmberMeteorBaseRock"]
    return [_Rock(r[0], placements()[r[0]][1], part) for r in ROCKS]


def _mix(k1, k2, t):
    return K.mix_key(k1, k2, t) if k1 != k2 else k1


def _ladder(base, dark, light, t):
    t = _q(abs(t)) * (1 if t >= 0 else -1)
    return base if t == 0 else _mix(base, light, t) if t > 0 else _mix(base, dark, -t)


def _tone(nf, c, tone):
    n = nf(c)
    if abs(n) < tone["dead"]:
        return 0.0
    return math.copysign((abs(n) - tone["dead"]) / tone["width"], n)


def _centre(p, faces, pos):
    a = sum(f.calc_area() for f in faces) or 1.0
    return sum((pos(f) * f.calc_area() for f in faces), Vector()) / a


def _tint(p, groups, level, mottle, pos):
    m = MOTTLE[mottle]
    nf = K.noise_field(scale=m["scale"], seed=m["seed"])
    for gr in groups:
        c = _centre(p, gr, pos)
        k = level(gr, c) * (1.0 + m["amp"] * 1.6 * nf(c))
        for f in gr:
            for l in f.loops:
                l[p.tint_layer] = (k, k, k, 1.0)


def colour(o):
    """Stage 4 on one finished M015 object (hero or part). Returns the face count per key."""
    g = _geo()
    kind = KIND[o.name]
    p = m009._paint(o, _paint_off(o))           # every Tint reset to 1 first, so the pass repeats
    cls = _classify(o, p)
    by = {}
    for f, cl in cls.items():
        by.setdefault(cl, []).append(f)
    hero = kind == "hero"
    # the hero's shell surface (occlusion of the core, crevices of the rocks)
    shell_faces = [f for f, cl in cls.items() if cl not in ("core", "rock")]
    shell_tree = None
    if hero and shell_faces:
        vs = [v.co + p.off for v in p.bm.verts]
        p.bm.verts.index_update()
        shell_tree = BVHTree.FromPolygons(vs, [[v.index for v in f.verts] for f in shell_faces])

    def glow_d(c):
        return min(g["core"].find_nearest(c)[3], g["slots"].find_nearest(c)[3],
                   min(t.find_nearest(c)[3] for t in g["open"].values()))
    # shell outside: per facet tone, per face spill / ground
    nf = K.noise_field(scale=SHELL_TONE["scale"], seed=SHELL_TONE["seed"])
    groups = _facets(by.get("dome", []) + by.get("ground", []))
    for gr in groups:
        c0 = _centre(p, gr, p.at)
        t0 = _tone(nf, c0, SHELL_TONE)
        for f in gr:
            c = p.at(f)
            if cls[f] == "ground":
                key = SHELL
            else:
                ts = _step(glow_d(c), SPILL)
                if ts:
                    key = _mix(SHELL, SHELL_WARM, ts)
                else:
                    key = _ladder(SHELL, SHELL_DARK, SHELL_LIGHT, t0 - _step((c - SINKV).z, GROUND_BAND))
            f.material_index = p._mi(key)
    for f in by.get("sector", []):
        f.material_index = p._mi(SHELL_DARK if g["dome"].find_nearest(p.at(f))[3] < SECTOR_DARK else LIP)
    for f in by.get("hollow", []):
        f.material_index = p._mi(_mix(*HOLLOW_KEY))
    # window rims: graded from the outer lip to the core
    for cl in [k for k in by if k.startswith("rim_")]:
        for f in by[cl]:
            c = p.at(f)
            a, b = g["dome"].find_nearest(c)[3], g["core"].find_nearest(c)[3]
            s = a / max(a + b, 1e-6)
            k1, k2, t = next((x for lim, x in zip(RIM_STEPS[cl[4:]], RIM_KEYS) if s < lim), RIM_KEYS[-1])
            f.material_index = p._mi(_mix(k1, k2, t))
    # slots: rows by depth, the floor hot where the slot is open
    floor = {}
    for f in by.get("slot", []):
        c = p.at(f)
        _, i, _ = g["st_kd"].find(c)
        _pt, G_, d, _name = g["st"][i]
        t = g["dome"].find_nearest(c)[3] / max(d, 1e-6)
        key = next((_mix(*k) for lim, k in SLOT_ROWS if t < lim), None)
        if key is None:
            key = HOT if G_ >= FLOOR_HOT_G else CORE
            floor[key] = floor.get(key, 0) + 1
        f.material_index = p._mi(key)
    # core
    if by.get("core"):
        nfc = K.noise_field(scale=CORE_SCALE, seed=CORE_SEED)
        cc = CORE_AT + SINKV
        rx, ry, rz = CORE_DIM["r"]
        for gr in _facets(by["core"]):
            for f in gr:
                q = p.at(f) - cc
                hf = (q.z + rz) / (2 * rz)
                hf = hf if hf < CORE_CAP else CORE_CAP - (hf - CORE_CAP) * CORE_FOLD
                u = CORE_UP * hf + CORE_LAT * q.x / rx - CORE_FWD * q.y / ry + CORE_NOISE * nfc(q)
                key = DEEP if u < CORE_BANDS[0] else CORE if u < CORE_BANDS[1] else HOT
                if shell_tree is not None and shell_tree.find_nearest(p.at(f))[3] < CORE_OCC:
                    key = DEEP
                f.material_index = p._mi(key)
    # base rocks
    if by.get("rock"):
        nfr = K.noise_field(scale=ROCK_TONE["scale"], seed=ROCK_TONE["seed"])
        part = bpy.data.objects["EmberMeteorBaseRock"]
        rocks = _rocks() if hero else [_Rock("rock", Matrix.Identity(4), part)]
        H = rocks[0].hi.z - rocks[0].lo.z
        rock_of = {}
        for f in by["rock"]:
            hc = p.at(f) - SINKV if hero else f.calc_center_median()
            rk = min(rocks, key=lambda r: r.norm(r.inv @ hc))
            rock_of[f] = rk
            q = rk.inv @ hc
            u = (q.z - rk.lo.z) / H
            dark = 0.0
            if shell_tree is not None:
                dark = _step(shell_tree.find_nearest(p.at(f))[3], ROCK_CREVICE)
            if u < ROCK_GROUND[0]:
                dark = max(dark, ROCK_GROUND[1])
            if dark and u < ROCK_CROWN:
                key = _mix(BASE, BASE_DARK, dark)
            else:
                t = _tone(nfr, q + rk.noff, ROCK_TONE)
                key = _mix(BASE, BASE_LIGHT, _q(t)) if t > 0 else BASE
            f.material_index = p._mi(key)
    # Tint
    if hero or kind in ("FL", "FR", "BR"):
        sh = by.get("dome", []) + by.get("ground", []) + by.get("sector", [])
        _tint(p, _facets(sh), lambda gr, c: PIECE_TINT[kind if not hero else _sector_of(c)], "shell", p.at)
        walls = by.get("hollow", []) + [f for k in by if k.startswith("rim_") for f in by[k]] + by.get("slot", [])
        _tint(p, _facets(walls), lambda gr, c: 1.0, "slot", p.at)
    if by.get("core"):
        _tint(p, _facets(by["core"]), lambda gr, c: 1.0, "core", p.at)
    if by.get("rock"):
        for rk in {id(r): r for r in rock_of.values()}.values():
            fs = [f for f in by["rock"] if rock_of[f] is rk]
            pos = (lambda f, rk=rk: rk.inv @ (p.at(f) - SINKV) + rk.noff) if hero else \
                (lambda f: f.calc_center_median())
            _tint(p, _facets(fs), lambda gr, c, rk=rk: PIECE_TINT.get(rk.label, 1.0), "rock", pos)
    # Neon keys carry no Tint (the exporter drops it): 1.0
    for f in p.bm.faces:
        if p.key(f) in (CORE, HOT, WALL):
            for l in f.loops:
                l[p.tint_layer] = (1.0, 1.0, 1.0, 1.0)
    counts = {}
    for f in p.bm.faces:
        counts[p.key(f)] = counts.get(p.key(f), 0) + 1
    counts["_classes"] = {k: len(v) for k, v in by.items()}
    counts["_floor"] = floor
    p.done()
    return counts


def colour_all(objs=None):
    """Stage 4 on every object; then the shading waiver where K.check flags only the depth-graded walls."""
    objs = objs or [bpy.data.objects[n] for n in KIND]
    G.clear()
    out = {o.name: colour(o) for o in objs}
    _glow_mats()
    _ember_spec()
    for o in objs:
        if "kit_shading_ok" in o:
            del o["kit_shading_ok"]
    probs = K.check(objs)
    for o in objs:
        if any(x.startswith(o.name + ":") and "lighting is painted" in x for x in probs):
            o["kit_shading_ok"] = SHADING_OK
    out["_check"] = probs
    out["_shading"] = {o.name: o.get("kit_baked_shading") for o in objs}
    return out


# ---- stage 4 measurement: our renders against the sheet, with the study's masks (measure.py cls) -------------------
SHEET_PATH = "D:/Projects/Roblox/RBLX-Flintborn/art/blender/assets/references/015.png"
SHEET_PAPER = (242, 237, 230)
SHEET_BOX = {"f34": (20, 130, 460, 445), "r34": (470, 150, 845, 445), "front": (20, 508, 270, 716),
             "side": (276, 508, 510, 716), "rear": (516, 508, 767, 716), "top": (773, 508, 1003, 716)}
REPORT_VIEWS = {"front": (0, 7), "side": (90, 7), "rear": (180, 7), "top": (0, 78), "f34": (-14, 10),
                "r34": (166, 10)}
REPORT_DIR = K.TEMP_ROOT + "m015_s4"
LABEL_RGB = {"shell": (0.0, 1.0, 0.0), "rim": (1.0, 0.0, 1.0), "slot": (1.0, 1.0, 0.0), "core": (0.0, 0.0, 1.0),
             "rock": (1.0, 0.0, 0.0), "crack": (0.0, 1.0, 1.0)}
# (Stage 4-6 round 2) the sheet's crack boxes (M015_spec.md §5.2): crack 1 and crack 2 front, the BR crack side and
# rear, crack 5 rear; measured on the O + L pixels (the crack itself, not the shell round it)
SHEET_CRACKS = {"crack1_front": (95, 600, 130, 690), "crack2_front": (215, 545, 250, 665),
                "br_side": (325, 570, 395, 640), "br_rear": (545, 575, 625, 640), "crack5_rear": (695, 595, 735, 680)}
CRACK_HOT = (245, 140)  # a crack pixel is "hot" (the sheet's yellow-orange floor) at r >= 245 and g >= 140


def _cls_px(c, paper=None):
    """measure.py cls() on an (h, w, 3) sRGB 0-255 array: 0 none, 1 S shell, 2 O glow, 3 L lip, 4 B base rock."""
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    l = (r + g + b) / 3
    out = np.zeros(r.shape, np.uint8)
    O = (r >= 120) & (r - b >= 70) & (r > g + 30)
    L = ~O & (r - b >= 22) & (r > g + 12) & (l < 105)
    B = ~O & ~L & (((g - b >= 6) & (r - b >= 16) & (l >= 80)) | ((r - b >= 26) & (l >= 85)))
    S = ~O & ~L & ~B & (l < 228)
    out[S], out[O], out[L], out[B] = 1, 2, 3, 4
    if paper is not None:
        out[np.abs(c - np.array(paper)).max(axis=2) <= 14] = 0
    return out


def _hexs(c):
    return "#" + "".join(f"{int(round(x)):02X}" for x in c)


def _stats(sel):
    if len(sel) < 20:
        return None
    lum = sel.mean(axis=1)
    lo, hi = np.percentile(lum, 25), np.percentile(lum, 75)
    return (_hexs(np.median(sel, axis=0)), _hexs(np.median(sel[lum >= hi], axis=0)),
            _hexs(np.median(sel[lum <= lo], axis=0)), int(len(sel)))


def _class_stats(img, cl):
    met = (cl == 1) | (cl == 2) | (cl == 3)
    n = max(1, int(met.sum()))
    return {"O": round(float((cl == 2).sum()) / n, 3), "L": round(float((cl == 3).sum()) / n, 3),
            "B_of_all": round(float((cl == 4).sum()) / max(1, int((cl > 0).sum())), 3),
            "S_med": _stats(img[cl == 1]), "O_med": _stats(img[cl == 2]), "L_med": _stats(img[cl == 3]),
            "B_med": _stats(img[cl == 4])}


def _top_down(px):
    return (np.clip(px[::-1, :, :3], 0, 1) * 255).astype(np.float64)


def sheet_stats():
    img = _top_down(K.NS["KIT"]["load_px"](SHEET_PATH))
    out = {}
    for v, (x0, y0, x1, y1) in SHEET_BOX.items():
        c = img[y0:y1, x0:x1]
        out[v] = _class_stats(c, _cls_px(c, SHEET_PAPER))
    return out


def _labels(o):
    p = m011._Paint(o, off=_paint_off(o))
    cls = _classify(o, p)
    g = _geo()
    out = {}
    for f, cl in cls.items():
        lab = "shell" if cl in ("dome", "ground", "sector") else "rim" if cl.startswith("rim_") or \
            cl == "hollow" else cl
        if lab == "slot" and g["st"][g["st_kd"].find(p.at(f))[1]][3].startswith("crack"):
            lab = "crack"       # the two crack slots (and BL's mirrored one), apart from the seams
        out[f.index] = lab
    p.bm.free()
    return out


def _crack_stats(sel):
    """Crack pixels: median / lit / shade (as _stats); `bright`, the share in the cls() glow class O (reads as glowing
    orange); `L`, the share in the dark lip class; `hot`, the share at CRACK_HOT."""
    if len(sel) < 20:
        return None
    st = _stats(sel)
    cl = _cls_px(sel[None, :, :])[0]
    return {"med": st[0], "lit": st[1], "shade": st[2], "n": st[3],
            "bright": round(float((cl == 2).mean()), 3), "L": round(float((cl == 3).mean()), 3),
            "hot": round(float(((sel[:, 0] >= CRACK_HOT[0]) & (sel[:, 1] >= CRACK_HOT[1])).mean()), 3)}


def sheet_cracks():
    """The sheet's crack boxes (SHEET_CRACKS), on their O + L pixels."""
    img = _top_down(K.NS["KIT"]["load_px"](SHEET_PATH))
    out = {}
    for k, (x0, y0, x1, y1) in SHEET_CRACKS.items():
        c = img[y0:y1, x0:x1]
        cl = _cls_px(c, SHEET_PAPER)
        out[k] = _crack_stats(c[(cl == 2) | (cl == 3)])
    return out


def _label_render(o, path, az, el):
    """o rendered with flat emission label colours (same verts, so the same framing as its colour render; m014)."""
    lab = _labels(o)
    me = o.data.copy()
    tmp = bpy.data.objects.new("_m015_labels", me)
    o.users_collection[0].objects.link(tmp)
    tmp.matrix_world = o.matrix_world
    mats = []
    try:
        me.materials.clear()
        for name, rgb in LABEL_RGB.items():
            m = bpy.data.materials.new("_m015_label_" + name)
            m.use_nodes = True
            nt = m.node_tree
            nt.nodes.clear()
            em = nt.nodes.new("ShaderNodeEmission")
            em.inputs["Color"].default_value = (*rgb, 1.0)
            out = nt.nodes.new("ShaderNodeOutputMaterial")
            nt.links.new(em.outputs[0], out.inputs[0])
            me.materials.append(m)
            mats.append(m)
        names = list(LABEL_RGB)
        for pl in me.polygons:
            pl.material_index = names.index(lab[pl.index])
        return K.NS["KIT"]["render_group"]([tmp], path, az, el)
    finally:
        bpy.data.objects.remove(tmp, do_unlink=True)
        bpy.data.meshes.remove(me)
        for m in mats:
            bpy.data.materials.remove(m)


def _label_mask(px):
    c = px[..., :3]
    mx = c.max(axis=2)
    n = c / np.maximum(mx, 1e-4)[..., None]
    sat = (mx - c.min(axis=2)) / np.maximum(mx, 1e-4)
    best, bd = np.full(mx.shape, -1), np.full(mx.shape, 9.0)
    for i, rgb in enumerate(LABEL_RGB.values()):
        d = np.abs(n - np.array(rgb)).max(axis=2)
        upd = d < bd
        best[upd], bd[upd] = i, d[upd]
    ok = (mx > 0.15) & (sat > 0.6) & (bd < 0.45)
    out = {}
    for i, name in enumerate(LABEL_RGB):
        m = ok & (best == i)
        e = m.copy()
        e[1:, :] &= m[:-1, :]
        e[:-1, :] &= m[1:, :]
        e[:, 1:] &= m[:, :-1]
        e[:, :-1] &= m[:, 1:]
        out[name] = e
    return out


def report(views=None, light=False, out_dir=None, tag=""):
    """Render the hero (colour + labels) at the sheet's angles and measure, inside the hero's own pixels, the study's
    cls() classes (glow share O, lip share L, shell / glow / lip / base medians) plus the medians per construction
    region. light: the sockets' PointLights realised (no particle stand-ins), as the game lights it."""
    import os
    h = bpy.data.objects["EmberMeteorDeposit"]
    out_dir = out_dir or REPORT_DIR
    os.makedirs(out_dir, exist_ok=True)
    kit = K.NS["KIT"]
    old = kit["CELL"]
    kit["CELL"] = (480, 400)
    sc = bpy.context.scene
    ground = bpy.data.objects.get("FB_Ground")
    home = ground.location.copy() if ground else None
    out = {}
    if light:
        kit["vfx"].clear(sc)
        kit["vfx"].realize(sc, [h], particles=False)
    try:
        for v, (az, el) in (views or REPORT_VIEWS).items():
            pc = kit["render_group"]([h], f"{out_dir}/{v}{tag}.png", az, el)
            pl = _label_render(h, f"{out_dir}/{v}_lab.png", az, el)
            img = _top_down(kit["load_px"](pc))
            mk = _label_mask(kit["load_px"](pl)[::-1])
            obj = np.zeros(img.shape[:2], bool)
            for m in mk.values():
                obj |= m
            cl = _cls_px(img)
            cl[~obj] = 0
            r = _class_stats(img, cl)
            r["regions"] = {k: _stats(img[m]) for k, m in mk.items()}
            # (round 2) each region's cls() make-up (share of the meteor's S + O + L pixels, and O / L inside it)
            met = max(1, int(((cl == 1) | (cl == 2) | (cl == 3)).sum()))
            r["reg_cls"] = {k: {"of_meteor": round(float(m.sum()) / met, 3),
                                "O": round(float((cl[m] == 2).mean()), 3) if m.any() else 0.0,
                                "L": round(float((cl[m] == 3).mean()), 3) if m.any() else 0.0}
                            for k, m in mk.items() if k != "rock"}
            r["crack"] = _crack_stats(img[mk["crack"]])
            r["core_px"] = _crack_stats(img[mk["core"]])
            out[v] = r
    finally:
        kit["CELL"] = old
        if ground:
            ground.location = (home.x, home.y, 0.0)
            ground.hide_set(True)
        if light:
            kit["vfx"].clear(sc)
    return out


# ---- stages 5+6: light and VFX sockets on the hero (M015_spec.md §7 and "Stage 5+6") --------------------------------
# All points are in the hero build frame (front -Y, ground z 0); _vfx() adds them to the FINISHED hero at
# point - h[OFF] (hero-local studs). Lights sit in the open in the window recesses, in front of the core, never inside
# the mesh (M009's lesson: a light inside the meteor shone through and turned the rim rocks peach); shadows on.
# (the spec's 0.9 / 0.6: the front window's rims lit to O and the front / f34 glow shares went 4.6 / 5.1 points over
# the sheet's, the rear stayed 5 under; the back window faces away from the studio key, so its light carries more)
# (build fixes, verifier round 1: (0.9, -4.3, 3.6) put 6 of the heat box's 125 spawn points inside the shell / F4
# after the rocks grew; 0.6 further out and 0.2 up clears it)
FRONT_LIGHT = dict(pos=(0.9, -4.9, 3.8), color="#FF7A22", brightness=0.7, range=10.0, flicker=True, shadows=True)
BACK_LIGHT = dict(pos=(0.3, 3.9, 4.2), color="#FF7A22", brightness=0.9, range=8.0, flicker=True, shadows=True)
# "Ember Glow VFX (separate asset). Simple emissive glow": soft warm puffs over each window (the sheet's halo
# #F8DCC0-#F9D5B0 hugging the silhouette is the place's Bloom on the Neon core plus these)
HEAT_FX = {"name": "Heat", "texture": "glow_soft", "color": ["#FFB347", "#FF6A1A"], "size": [1.4, 2.0],
           "transparency": [0.6, 1.0], "lifetime": [0.8, 1.2], "rate": 2.5, "speed": [0.2, 0.4], "spread": 5,
           "light_emission": 1.0}
# "floating ember shards": the VFX panel's ~10 faceted shards 0.4-0.8 studs (orange #FD6A22 / #FE5A1B / #FE6815, hot
# #FD9F2A / #FEBD79 / #FCC074) and a few 0.15 sparks, 0.5-3 studs off the silhouette, drifting up and out
EMBER_FX = {"name": "Embers", "texture": "ember_dot", "color": ["#FEBD79", "#FD6A22", "#FE5A1B"],
            "size": [0.55, 0.45, 0.15], "transparency": [0.0, 0.1, 1.0], "lifetime": [2.0, 3.5], "rate": 3.0,
            "speed": [0.6, 1.4], "spread": 70, "light_emission": 1.0, "drag": 0.6, "acceleration": [0, 0.5, 0]}
# (kind, build-frame point, emitter overrides, light): shapes are Roblox (x, height, depth); every spawn box's 5^3
# grid lies outside the hero (fx_check)
SOCKETS = (
    ("heat_glow", FRONT_LIGHT["pos"], {"shape": [1.8, 2.4, 0.4]}, FRONT_LIGHT),
    ("heat_glow", BACK_LIGHT["pos"], {"rate": 2.0, "shape": [1.4, 2.2, 0.4]}, BACK_LIGHT),
    ("embers", (0.3, 0.0, 8.4), {"shape": [4.0, 0.6, 3.5]}, None),
    ("embers", (0.9, -5.6, 2.6), {"rate": 1.5, "shape": [2.0, 1.0, 0.6]}, None),
    # (round 2, verifier round 1: "embers only at the crown and front". The VFX panel's shards float round both
    # flanks too, 0.5-3 studs off the silhouette from low to above the top: a tall thin spawn box beside each flank,
    # 1.2 out from the shell's widest point at z 1.5-6 (x -4.39 / +5.21))
    ("embers", (-5.6, -0.3, 4.0), {"rate": 1.5, "shape": [0.8, 3.6, 3.0]}, None),
    ("embers", (6.4, -0.3, 4.0), {"rate": 1.5, "shape": [0.8, 3.6, 3.0]}, None),
)


def _vfx(h):
    """Stages 5+6: the hero's sockets (SOCKETS), replacing any it has. Returns them."""
    for c in [c for c in h.children if c.get("vfx_kind")]:
        bpy.data.objects.remove(c, do_unlink=True)
    off = Vector(h[OFF])
    made = []
    for kind, pos, em, light in SOCKETS:
        base = HEAT_FX if kind == "heat_glow" else EMBER_FX
        kw = {"emitters": [dict(base, **em)]}
        if kind == "heat_glow":
            kw["light"] = {k: light[k] for k in ("color", "brightness", "range", "flicker", "shadows")}
        made.append(K.socket(h, kind, Vector(pos) - off, **kw))
    return made


def fx_check(h=None):
    """Each socket: the nearest hero surface from the socket point, and how many of its spawn box's 5^3 grid points
    lie inside the hero (ray parity on 3 directions, majority)."""
    import json
    h = h or bpy.data.objects["EmberMeteorDeposit"]
    bm = bmesh.new()
    bm.from_mesh(h.data)
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    dirs = [Vector(d).normalized() for d in ((0.31, 0.17, 0.93), (-0.62, 0.71, 0.33), (0.45, -0.83, -0.32))]

    def inside(q):
        k = 0
        for d in dirs:
            n, x = 0, q.copy()
            for _ in range(200):
                hit = tree.ray_cast(x, d)
                if hit[0] is None:
                    break
                n += 1
                x = hit[0] + d * 1e-5
            k += n % 2
        return k >= 2
    out = []
    for s in [c for c in h.children if c.get("vfx_kind")]:
        spec = json.loads(s["roblox"])
        loc = Vector(s.location)
        sh = (spec.get("emitters") or [{}])[0].get("shape")
        bad = 0
        if sh:
            for i in range(5):
                for j in range(5):
                    for k in range(5):
                        q = loc + Vector(((i / 4 - 0.5) * sh[0], (k / 4 - 0.5) * sh[2], (j / 4 - 0.5) * sh[1]))
                        bad += inside(q)
        out.append({"name": s.name, "kind": s["vfx_kind"], "at": [round(c, 2) for c in loc + Vector(h[OFF])],
                    "clear": round(tree.find_nearest(loc)[3], 2), "inside": inside(loc), "box_inside": bad,
                    "roblox_xyz": [round(loc.x, 2), round(loc.z, 2), round(-loc.y, 2)]})
    bm.free()
    return out


def finish_stages(h, objs):
    """Stages 4-6 on the finished meshes: the palette, the hero's sockets, the colour pass."""
    palette()
    socks = _vfx(h)
    col = colour_all(objs)
    return {"sockets": [(s.name, s["vfx_kind"], [round(c, 3) for c in s.location]) for s in socks], "colour": col}


# ---- build ------------------------------------------------------------------------------------------------------------
def _force5(o):
    """The few corners _polish leaves under POLISH_LIM (verifier round 1: Slab 0.98 deg at the front crown, Chunk and
    hero 4.2 deg): m012._force_slivers at POLISH_LIM (edge collapses up to 0.25 and sub-0.06 nudges, ground kept
    flat), then _polish again for the origin, offset and UVs. Returns the number forced."""
    if not m012._thin(o, POLISH_LIM)["under"]:
        return 0
    n = m012._force_slivers(o, lim=POLISH_LIM)
    if m012._thin(o, POLISH_LIM)["under"]:
        n += _merge_needles(o)
    _polish(o)
    return n


def _nm_verts(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    n = sum(1 for v in bm.verts if not v.is_manifold)
    bm.free()
    return n


def _fix_bowties(o, step=0.01):
    """A vertex two separate fans of faces share (every edge manifold, the vertex not: a bow-tie, which makes the
    Euler characteristic odd; the round-1 fixes found one on the Slab at the front window's top corner, left by a
    sliver collapse): each fan after the first gets its own copy of the vertex, moved `step` towards that fan's
    centre. Face attributes (key, UVs, Tint) are copied. Returns the number split."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    n = 0
    for v in [v for v in bm.verts if not v.is_manifold and all(e.is_manifold for e in v.link_edges)]:
        left, fans = set(v.link_faces), []
        while left:
            f0 = left.pop()
            fan, stack = {f0}, [f0]
            while stack:
                f = stack.pop()
                for e in f.edges:
                    if v not in e.verts:
                        continue
                    for g in e.link_faces:
                        if g in left:
                            left.discard(g)
                            fan.add(g)
                            stack.append(g)
            fans.append(fan)
        for fan in fans[1:]:
            c = sum((f.calc_center_median() for f in fan), Vector()) / len(fan)
            nv = bm.verts.new(v.co + (c - v.co).normalized() * step)
            for f in list(fan):
                vs = [nv if x is v else x for x in f.verts]
                nf = bm.faces.new(vs)
                nf.material_index, nf.smooth = f.material_index, f.smooth
                for la, lb in zip(f.loops, nf.loops):
                    for layer in bm.loops.layers.uv.values():
                        lb[layer].uv = la[layer].uv
                    for layer in bm.loops.layers.float_color.values():
                        lb[layer] = la[layer]
                bm.faces.remove(f)
            n += 1
    if n:
        # the moved fans' old edges to v are left with no faces: drop them (else they count as wire edges)
        bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces], context="EDGES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(o.data)
    bm.free()
    return n


def _merge_needles(o, max_len=0.05):
    """Needles force_slivers won't take (its link test refuses them): merge each one's shortest edge (under max_len)
    at its middle, drop any doubled face pair, and keep the result only if it stays manifold with no crossings (the
    back seam's overlap left two at the hollow's crown, 0.012 / 0.015 edges, 0.8 / 1.4 deg)."""
    keep = o.data.copy()
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bad = [f for f in bm.faces if m011._fmin(f) < math.radians(POLISH_LIM)]
    edges = {min(f.edges, key=lambda e: e.calc_length()) for f in bad}
    n = 0
    for e in edges:
        if e.is_valid and e.calc_length() < max_len:
            a, b = e.verts
            bmesh.ops.pointmerge(bm, verts=[a, b], merge_co=(a.co + b.co) / 2)
            n += 1
    seen, fins = {}, []
    for f in bm.faces:
        k = frozenset(f.verts)
        if k in seen:
            fins += [f, seen[k]]
        seen[k] = f
    if fins:
        bmesh.ops.delete(bm, geom=list(set(fins)), context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(o.data)
    bm.free()
    M.repair_nonmanifold(o)
    _fill_holes(o)
    a = M.audit(o)
    if a["nonmanifold_edges"] or a["boundary_edges"] or _self_hits(o):
        old = o.data
        o.data = keep
        bpy.data.meshes.remove(old)
        o.data.name = o.name
        return 0
    bpy.data.meshes.remove(keep)
    return n


def _parity(tree, q, d=Vector((0.31, 0.17, 0.93)).normalized()):
    """q inside the closed mesh of `tree` (ray parity)."""
    n, p = 0, q.copy()
    for _ in range(400):
        hit = tree.ray_cast(p, d)
        if hit[0] is None:
            break
        n += 1
        p = hit[0] + d * 1e-5
    return n % 2 == 1


def _sane(o, limit=30.0):
    """Stop before the hero's exact unions if a part's mesh has a vertex far outside the model (a wild vertex there
    crashes Blender inside the boolean instead of raising)."""
    co = [v.co for v in o.data.vertices]
    ext = max(max(abs(c[i]) for c in co) for i in range(3))
    if ext > limit:
        raise RuntimeError(f"{o.name}: a vertex {ext:.1f} studs from its origin; not unioning it")


def build(render=True):
    M.coll(NUM, TITLE)
    palette()
    ST.clear()
    _slots()
    objs, log = {}, {}
    o = M.mk(SHEET, "EmberCore", core, subject=TITLE, role="part", notes=NOTES["EmberCore"], budget=1000,
             collision="hull")
    o[OFF] = list(M._build_offset(core))
    log["EmberCore"] = {"finish": {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges")}}
    log["EmberCore"]["polish"] = _polish(o)
    objs["EmberCore"] = o
    for key, (name, fn) in PIECE_PART.items():
        piece_obj(key)
        o = M.mk(SHEET, name, fn, subject=TITLE, role="part", notes=NOTES[name], budget=1000, collision="hull")
        o[OFF] = list(M._build_offset(fn))
        lg = {"clean": _clean(o, (0.0,))}
        lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "forced")}
        lg["ground_faces"] = _ground_keys(o)
        K.drop_unused_slots(o)
        lg["polish"] = _polish(o)          # stage 2+3, before the hero pastes the part
        lg["force5"] = _force5(o)
        lg["bowtie"] = _fix_bowties(o)
        _sane(o)
        log[name] = lg
        objs[name] = o
    o = M.mk(SHEET, "EmberMeteorBaseRock", base_rock, subject=TITLE, role="part", notes=NOTES["EmberMeteorBaseRock"],
             budget=1000, collision="hull")
    o[OFF] = list(M._build_offset(base_rock))
    _finish(o)
    log["EmberMeteorBaseRock"] = {"polish": _polish(o)}
    objs["EmberMeteorBaseRock"] = o
    _cleanup_tmp()
    h = M.mk(SHEET, "EmberMeteorDeposit", hero, subject=TITLE, role="hero", notes=NOTES["EmberMeteorDeposit"],
             budget=4000, collision="hull")
    hoff = M._build_offset(hero)
    M.union_loose(h)
    m014._floor_cut(h, -hoff.z)
    h[OFF] = list(Vector((hoff.x, hoff.y, 0.0)))
    log["hero"] = {"clean": _clean(h, (0.0,))}
    log["hero"]["finish"] = {k: v for k, v in _finish(h).items() if k in ("tris", "nonmanifold_edges", "forced")}
    log["hero"]["ground_faces"] = _ground_keys(h)
    K.drop_unused_slots(h)
    log["hero"]["polish"] = _polish(h)
    log["hero"]["force5"] = _force5(h)
    log["hero"]["bowtie"] = _fix_bowties(h)
    order = [h] + [objs[n] for n in ("EmberMeteorSlab", "EmberMeteorCap", "EmberMeteorChunk", "EmberCore",
                                     "EmberMeteorBaseRock")]
    stages = finish_stages(h, order)        # stages 4-6 (colour only: no geometry or UV change)
    M.display(NUM, order, TITLE)
    dropped = _drop_unused(order)
    out = {"audit": [{k: M.audit(o)[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges",
                                                     "boundary_edges", "normals", "ngons", "materials")}
                     for o in order],
           "thin": {o.name: m012._thin(o, 3.0) for o in order}, "self_hits": {o.name: _self_hits(o) for o in order},
           "info": dict(INFO), "log": log, "dropped": dropped, "gaps": gaps(), "measure": measure(h),
           "cracks": crack_probe(h), "problems": K.check(order), "stages": stages, "fx": fx_check(h)}
    # stage 2+3 checks on every object (M015_spec.md "Stage 2+3")
    out["corner5"] = {o.name: m012._thin(o, POLISH_LIM) for o in order}
    out["interior"] = {o.name: _interior_faces(o) for o in order}
    out["inner_shells"] = {o.name: m009._inner_shells(o) for o in order}
    out["uv"] = {o.name: M.uv_stats(o) for o in order}
    # straight-through sightlines (verifier round 1): the hero from the sheet's and the verifier's angles, the shell
    # parts from the same set
    out["see_through"] = {o.name: see_through(o) for o in order[:4]}
    out["problems"] += [f"{n}: see-through at {v}" for n, v in out["see_through"].items() if v]
    out["nm_verts"] = {o.name: _nm_verts(o) for o in order}
    out["problems"] += [f"{n}: {c} non-manifold verts" for n, c in out["nm_verts"].items() if c]
    # the core must survive the hero's unions (a broken operand once made core u FR come out empty, silently)
    bmh = bmesh.new()
    bmh.from_mesh(h.data)
    bmh.faces.ensure_lookup_table()
    th = BVHTree.FromBMesh(bmh)
    bmh.free()
    out["core_present"] = _parity(th, CORE_AT - Vector(h[OFF]))
    if not out["core_present"]:
        out["problems"].append("EmberMeteorDeposit: the core is missing (its centre is not inside the hero)")
    out["problems"] += [f"{n}: {c['under']} faces with a corner under {POLISH_LIM} deg"
                        for n, c in out["corner5"].items() if c["under"]]
    out["problems"] += [f"{n}: {c} crossing face pairs" for n, c in out["self_hits"].items() if c]
    out["problems"] += [f"{n}: {c} interior faces" for n, c in out["interior"].items() if c]
    out["problems"] += [f"{n}: {s['overlap_pairs']} UV overlaps, {s['flipped']} flipped" for n, s in out["uv"].items()
                        if s["overlap_pairs"] or s["flipped"]]
    if render:
        out["views"] = render_views(order)
    return out


def _cleanup_tmp():
    for o in [o for o in bpy.data.objects if o.name.startswith("_m015_")]:
        me = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if me and me.users == 0:
            bpy.data.meshes.remove(me)


def _drop_unused(objs):
    _drop_calib()
    names = {o.name for o in objs}
    meshes = [m for m in bpy.data.meshes if m.users == 0 and (m.name.split(".")[0] in names or
                                                               m.name.startswith(("_probe", "_cutter", "_m015")))]
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m015_")]
    out = {"meshes": len(meshes), "materials": sorted(m.name for m in mats)}
    for m in meshes:
        bpy.data.meshes.remove(m)
    for m in mats:
        bpy.data.materials.remove(m)
    for o in objs:
        if o.data.name != o.name and o.name not in bpy.data.meshes:
            o.data.name = o.name
    return out


def iterate():
    """Build without the full render set, then the preview shots; a compact summary for tuning."""
    r = build(render=False)
    preview()
    mm = r["measure"]
    return {"audit": [(a["name"], a["tris"], a["size"], a["shells"], a["nonmanifold_edges"]) for a in r["audit"]],
            "thin": {k: v["min_deg"] for k, v in r["thin"].items()}, "info": r["info"], "gaps": r["gaps"],
            "self": r["self_hits"],
            "meas": {v: {k: mm[v].get(k) for k in ("aspect", "meteor_w_h", "share", "prof_err", "profile")}
                     for v in mm}}


def preview():
    h = bpy.data.objects["EmberMeteorDeposit"]
    return M.views(NUM, [h], names=(), extra={
        "front_sheet": ([h], 0, 7), "side_sheet": ([h], 90, 7), "rear_sheet": ([h], 180, 7), "top78": ([h], 0, 78),
        "f34_sheet": ([h], -14, 10), "r34_sheet": ([h], 166, 10)}, vfx=False)


# exploded shot: each piece pulled out along its sector's middle direction and lifted, the core lifted
EXPLODE = {"Core": (0.0, 0.0, 4.5), "FL": (-3.2, -2.6, 3.0), "FR": (2.8, -3.2, 2.5), "BR": (3.0, 2.6, 3.5),
           "BL": (-3.0, 2.8, 3.5)}


def render_views(objs):
    h = objs[0]
    parts = objs[1:]
    shown = []
    try:
        x0, y0 = h.location.x + 40, h.location.y
        for name, (part, m) in placements().items():
            src = bpy.data.objects[part]
            c = bpy.data.objects.new(f"_m015_expl_{name}", src.data)
            src.users_collection[0].objects.link(c)
            c.matrix_world = Matrix.Translation(Vector((x0, y0, 0.0)) + Vector(EXPLODE.get(name, (0, 0, 0)))) @ m
            shown.append(c)
        bpy.context.view_layer.update()
        extra = {"front_sheet": ([h], 0, 7), "side_sheet": ([h], 90, 7), "rear_sheet": ([h], 180, 7),
                 "top78": ([h], 0, 78), "f34_sheet": ([h], -14, 10), "r34_sheet": ([h], 166, 10),
                 "exploded": (shown, -10, 14)}
        for o in parts:          # each piece from outside, showing its slots
            az = {"EmberMeteorSlab": -40, "EmberMeteorCap": -20, "EmberMeteorChunk": 140}.get(o.name, -25)
            extra["part_" + o.name.replace("EmberMeteor", "").replace("Ember", "").lower()] = ([o], az, 14)
        # (stages 5+6: rendered with the sockets realised - the window lights and the glow / ember stand-ins; they
        # don't veil the model. The colour compare against the sheet is report(), with and without the lights.)
        return M.views(NUM, [h], extra=extra, vfx=True)
    finally:
        for c in shown:
            bpy.data.objects.remove(c, do_unlink=True)
        M.display(NUM, objs, TITLE)
