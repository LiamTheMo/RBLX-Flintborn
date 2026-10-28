"""004 Obsidian (references/004.png): a cluster of sharp faceted obsidian crystals growing from a base of
rounded faceted rocks.

    import importlib, m004; importlib.reload(m004); m004.build()

Parts as on the sheet: Obsidian Chunk A (tall left), B (tall centre), C (tall right), D (small front right),
E (small front left), Base Rock (cluster). The hero is their union.
"""
import math
import random

import bmesh
from mathutils import Matrix, Vector

import kit_mcp as K
import kit_models as M

NUM, TITLE, SHEET = 4, "Obsidian", "M004"
OBS, OBS_MID, OBS_EDGE, ROCK, ROCK_COOL = "m004_obsidian", "m004_obsidian_mid", "m004_obsidian_edge", "m004_rock", "m004_rock_cool"

# crystals: (label, base x, y, radius, height, lean x, lean y, twist, seed)
# crystals: (label, base x, y, radius, height, lean x, lean y, twist, seed, base z). Fat faceted shafts (width
# about 0.45 of height) rising out of the top of the rock cluster and fanning outward, as on the sheet.
CRYSTALS = (("A", -2.3, 0.4, 2.5, 6.8, -0.28, 0.04, 0.3, 4011, 1.4), ("B", 0.3, 1.0, 2.75, 7.8, 0.02, 0.08, 0.0, 4012, 1.5),
            ("C", 2.6, 0.2, 2.3, 6.4, 0.22, 0.02, -0.4, 4013, 1.4), ("D", 1.9, -2.0, 1.25, 3.3, 0.25, -0.22, 0.6, 4014, 1.25),
            ("E", -1.75, -2.0, 1.3, 3.5, -0.25, -0.22, -0.2, 4015, 1.3))
# base rock cluster: (x, y, w, d, h, seed)
ROCKS = ((0.0, 0.2, 4.6, 4.0, 2.0, 4031), (-3.0, -0.5, 3.2, 2.9, 1.7, 4032), (3.0, -0.4, 3.0, 2.8, 1.6, 4033),
         (-0.9, -2.4, 2.8, 2.4, 1.5, 4034), (1.5, -2.5, 2.4, 2.2, 1.3, 4035), (-4.0, -1.9, 1.4, 1.3, 0.85, 4036),
         (3.9, -1.8, 1.3, 1.2, 0.8, 4037), (-0.6, 2.7, 2.9, 2.5, 1.6, 4038), (2.0, 1.8, 2.4, 2.1, 1.3, 4039),
         (-2.6, 2.0, 2.4, 2.1, 1.3, 4040), (3.4, 1.4, 1.9, 1.7, 1.1, 4041))
ROCK_RINGS = [(0.0, 0.9, 7), (0.35, 1.0, 7), (0.7, 0.78, 6), (1.0, 0.36, 4)]


def palette():
    K.set_colour(OBS, "#26262C", rough=0.35)
    K.set_colour(OBS_MID, "#353D55", rough=0.35)
    K.set_colour(ROCK, "#968680", rough=0.92)        # lifted toward the sheet swatch #9A8882
    K.set_colour(ROCK_COOL, "#8E8483", rough=0.92)


def crystal(a, label, origin=None):
    """One obsidian crystal: a 6-7-sided faceted shaft, widest about a third of the way up, tapering to a sharp
    lopsided point, with a flat joining surface underneath; a thin chamfer in the edge tone along its edges."""
    _, x, y, R, H, lx, ly, tw, seed, z0 = next(c for c in CRYSTALS if c[0] == label)
    rng = random.Random(seed)
    if origin is not None:
        x, y, lx, ly = origin[0], origin[1], 0.0, 0.0
    base = Vector((x, y, z0 - 1.2 if origin is None else 0.0))    # sunk 1.2 into the rocks
    axis = Vector((lx, ly, 1.0)).normalized()
    m = Matrix.Rotation(math.acos(max(-1.0, min(1.0, axis.z))), 3,                    # true lean angle
                        Vector((-axis.y, axis.x, 0)).normalized() if abs(axis.z) < 0.9999 else Vector((1, 0, 0)))
    m = m @ Matrix.Rotation(tw, 3, "Z")
    sides = rng.choice((6, 7))
    pts = []
    for h, rf, n_ in ((0.0, 0.72, sides), (0.3, 1.0, sides), (0.72, 0.58, sides - 1)):
        off = rng.uniform(0, 6.28)
        for k in range(n_):
            t = off + 2 * math.pi * k / n_ + rng.uniform(-0.12, 0.12)
            r = R * rf * rng.uniform(0.86, 1.06)
            pts.append(base + m @ Vector((math.cos(t) * r, math.sin(t) * r * 0.82, H * h)))
    pts.append(base + m @ Vector((R * 0.16, R * 0.05, H)))                    # short chisel tip, off-centre
    pts.append(base + m @ Vector((-R * 0.22, -R * 0.04, H * 0.96)))
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    vs = [v for v in vs if v.is_valid and v.link_faces]
    faces = K.faces_of(vs)
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    a._finish(vs, OBS)
    # no edge chamfer: the sheet's edges are "thin, sharp, broad plane, no micro detail"; their light edge
    # tone is the specular catch of the glassy faces (roughness 0.35), so the obsidian stays two colours
    allv = vs
    ei = -1
    # broad mid-tone blue facet patches (the sheet's Mid Tone), by noise over the crystal, not by facing
    main = [f for f in K.faces_of(allv) if f.material_index != ei]
    nf = K.noise_field(scale=0.35, seed=seed)
    mi = a._mi(OBS_MID)
    for f in main:
        if nf(f.calc_center_median()) > -0.08:                       # about half the faces in the mid tone
            f.material_index = mi
    K.texture(a, allv, amp=0.04, scale=0.5, jitter=0.03, seed=seed)
    return allv


def rocks(a, at_origin=False):
    out = []
    for x, y, w, d, h, seed in ROCKS:
        loc = (x, y, 0)
        w, d, h = w * 1.15, d * 1.15, h * 1.4          # a fuller, taller ring (rocks about a third of the height)
        vs = K.hull_rock(a, (w, d, h), loc=loc, seed=seed, mat=ROCK, rings=ROCK_RINGS, jitter=0.06,
                         rot=0.37 * seed % 3.0, keep_bottom=True)
        K.blend(a, vs, ROCK, ROCK_COOL, K.noise_field(scale=0.3, seed=seed), level=0.15, width=0.4, steps=1)
        K.texture(a, vs, amp=0.04, scale=0.4, jitter=0.04, seed=seed)
        out += vs
    return out


def hero(a):
    rocks(a)
    for c in CRYSTALS:
        crystal(a, c[0])
    # nothing below the ground: the sunk crystal bases are trimmed by the union's floor cut in build()


NOTES = {
    "Obsidian": "obsidian resource: five sharp faceted blue-black crystals (three tall, two small at the front) "
                "growing out of a cluster of rounded grey base rocks; thin lighter edge tone, mid-tone blue facet "
                "patches; one closed mesh",
    "ObsidianCrystalA": "Obsidian Chunk A (tall left): faceted crystal, flat joining surface underneath",
    "ObsidianCrystalB": "Obsidian Chunk B (tall centre): the tallest faceted crystal",
    "ObsidianCrystalC": "Obsidian Chunk C (tall right): faceted crystal",
    "ObsidianCrystalD": "Obsidian Chunk D (small front right): faceted crystal",
    "ObsidianCrystalE": "Obsidian Chunk E (small front left): faceted crystal",
    "ObsidianRockCluster": "Base Rock (cluster): rounded faceted grey rocks with recessed joining surfaces",
}


def floor_cut(o):
    """Cut everything below z = 0 (the crystals' sunk bases) and cap the hole flat: a planar base."""
    import bpy
    bm = bmesh.new()
    bm.from_mesh(o.data)
    # the ground is where the rocks' flat bottoms are (the asset may have been lifted because a leaning
    # crystal dipped below it): the most common z of the down-facing flat faces
    flat = [round(f.calc_center_median().z, 3) for f in bm.faces if f.normal.z < -0.99]
    z0 = max(set(flat), key=flat.count) if flat else 0.0
    res = bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces), plane_co=(0, 0, z0),
                                 plane_no=(0, 0, -1), clear_outer=True)
    # anything the bisect left below the plane (e.g. a stray vertex of a face lying across it) goes too
    below = [v for v in bm.verts if v.co.z < z0 - 1e-4]
    if below:
        bmesh.ops.delete(bm, geom=below, context="VERTS")
    for v in bm.verts:                       # snap the base exactly onto the ground plane, then move it to z = 0
        if v.co.z < z0 + 0.02:
            v.co.z = z0
        v.co.z -= z0
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
    boundary = [e for e in bm.edges if e.is_boundary]
    if boundary:
        bmesh.ops.holes_fill(bm, edges=boundary)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=0.004)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()


def build(render=True):
    M.coll(NUM, TITLE)
    palette()
    specs = [("Obsidian", "hero", hero, 4000, "hull")]
    # ObsidianCrystalA-E / ObsidianRockCluster: the kit's R02 sheet owns ObsidianChunk* and ObsidianBaseRock
    specs += [(f"ObsidianCrystal{c[0]}", "part", (lambda L: lambda a: crystal(a, L, origin=(0, 0)))(c[0]), 1000, "hull")
              for c in CRYSTALS]
    specs += [("ObsidianRockCluster", "part", lambda a: rocks(a), 1000, "hull")]
    objs = [M.mk(SHEET, n, fn, subject=TITLE, role=r, notes=NOTES[n], budget=b, collision=c)
            for n, r, fn, b, c in specs]
    audits = []
    for o in objs:
        if o.get("kit_role") == "hero":
            M.union_loose(o)
            floor_cut(o)
        audits.append(M.finish(o, union=False))
    M.display(NUM, objs, TITLE)
    out = {"audit": audits, "problems": K.check(objs)}
    if render:
        hero_o, parts = objs[0], objs[1:]
        saved = M.explode(parts, {})
        try:
            hx, hy = hero_o.location.x, hero_o.location.y
            for o, c in zip(parts[:5], CRYSTALS):
                o.location = (hx + 40 + c[1] * 1.6, hy + c[2] * 1.2, 4.5 + (0 if c[0] in "ABC" else -2.0))
            parts[5].location = (hx + 40, hy, 0)
            out["views"] = M.views(NUM, [hero_o], extra={"exploded": (parts, -14, 12)})
        finally:
            M.restore(saved)
            M.display(NUM, objs, TITLE)
    return out
