"""011 Amethyst (references/011.png): a geode cave: a thick-walled hollow faceted rock dome open to the front, its
cavity bare shaded stone, a cluster of purple crystals standing inside on the cave floor, and a low lip of rock
slabs across the mouth.

    import importlib, m011; importlib.reload(m011); m011.build()

Parts as on the sheet: Top Shell (the hollow dome), Bottom Shell (the rock lip), Crystal (reusable, x4+). The hero
is the dome with its cavity and mouth carved out (kit_models.carve; the cut faces take the cave stone), then the
crystals and lip rocks joined in and unioned. The R03 kit sheet owns AmethystTopShell/BottomShell/Crystal, so the
parts are AmethystShellTop, AmethystShellBottom and AmethystShard.
"""
import math
import random

import bmesh
from mathutils import Matrix, Vector

import kit_mcp as K
import kit_models as M
import m004

NUM, TITLE, SHEET = 11, "Amethyst", "M011"
LIGHT, MID, DARK = "m011_crystal_light", "m011_crystal_mid", "m011_crystal_dark"
ROCK, ROCK_DARK, CAVE, CAVE_DARK = "m011_rock", "m011_rock_dark", "m011_cave", "m011_cave_dark"

SHELL_SIZE = (10.2, 8.8, 8.2)
SHELL_RINGS = [(0.0, 0.9, 12), (0.18, 1.0, 13), (0.42, 0.99, 13), (0.64, 0.92, 12), (0.82, 0.74, 10),
               (0.95, 0.46, 7), (1.0, 0.2, 4)]
# cutters: the inner cavity (centre, radii, seed), walls about 1.5 thick; and the mouth, a flat cut through the
# dome's front (a point on the plane, its tilt back from vertical in degrees), so the opening's rim is a broad flat
# band of stone all round, as on the sheet (a rounded scoop thins the wall to a knife edge at the rim). The cut
# leans back, so the crystals also show from above as on the sheet's top view.
CAVITY = ((0.0, -0.3, 3.9), (3.4, 2.8, 3.1), 11051)
MOUTH = ((0.0, -2.8, 0.0), 20.0)
# crystals: (label, x, y, radius, height, lean x, lean y, twist, seed)
CRYSTALS = (("Main", 0.0, -0.4, 1.5, 6.4, 0.0, -0.05, 0.2, 11011),
            ("Left", -1.7, -0.7, 1.3, 5.0, -0.28, -0.15, 0.6, 11012),
            ("Right", 1.7, -0.7, 1.25, 4.7, 0.28, -0.15, -0.4, 11013),
            ("RightFar", 2.4, 0.0, 1.0, 3.7, 0.3, -0.05, 0.9, 11014),
            ("Front", 0.6, -1.9, 1.0, 3.0, 0.05, -0.35, 0.3, 11015),
            ("FrontLeft", -1.4, -1.8, 1.0, 3.4, -0.2, -0.3, 0.8, 11017),
            ("BackLeft", -1.0, 0.6, 0.9, 3.9, -0.15, 0.1, 1.1, 11016))
CRYSTAL_Z = 0.5             # crystal roots, sunk into the cave floor
# the bottom shell: low rocks across the mouth (x, y, w, d, h, seed)
# two big slabs across the mouth (meeting in the middle) and one each side, as on the sheet
LIP = ((-2.4, -3.2, 5.0, 3.4, 2.6, 11031), (2.4, -3.3, 5.0, 3.4, 2.5, 11032), (-4.2, -0.9, 3.2, 3.6, 2.6, 11034),
       (4.2, -0.8, 3.1, 3.5, 2.5, 11035))
LIP_RINGS = [(0.0, 0.95, 6), (0.5, 1.0, 6), (0.85, 0.9, 6), (1.0, 0.68, 5)]   # blocky, flat-topped slabs


def palette():
    K.set_colour(LIGHT, "#C097DD", rough=0.4)      # sheet swatches: light #C097DD, mid #924EC3, dark #5F3289
    K.set_colour(MID, "#924EC3", rough=0.4)
    K.set_colour(DARK, "#5F3289", rough=0.4)
    K.set_colour(ROCK, "#9E8F8B", rough=0.92)      # "Rock" #9E8F8B
    K.set_colour(ROCK_DARK, "#8D7F7C", rough=0.92)
    # the cave inside is bare stone, a shade darker than the outside (only the crystals are purple)
    K.set_colour(CAVE, "#857774", rough=0.92)
    K.set_colour(CAVE_DARK, "#736764", rough=0.92)


def shell(a):
    """The outer dome: a broad faceted rock, flat bottom."""
    vs = K.hull_rock(a, SHELL_SIZE, seed=11001, mat=ROCK, rings=SHELL_RINGS, jitter=0.07, rot=0.2,
                     keep_bottom=True)
    K.blend(a, vs, ROCK, ROCK_DARK, K.noise_field(scale=0.25, seed=11001), level=0.15, width=0.4, steps=1)
    K.texture(a, vs, amp=0.05, scale=0.3, jitter=0.04, seed=11001)
    return vs


def _blob(a, centre, radii, seed, mat, n=26):
    rng = random.Random(seed)
    c = Vector(centre)
    pts = []
    for k in range(n):
        z = 1 - 2 * (k + 0.5) / n
        r = math.sqrt(1 - z * z)
        th = k * 2.39996 + rng.uniform(-0.12, 0.12)
        s = rng.uniform(0.94, 1.05)
        pts.append(c + Vector((math.cos(th) * r * radii[0], math.sin(th) * r * radii[1], z * radii[2])) * s)
    vs = [a.bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(a.bm, input=vs)
    vs = [v for v in vs if v.is_valid and v.link_faces]
    bmesh.ops.recalc_face_normals(a.bm, faces=K.faces_of(vs))
    a._finish(vs, mat)
    return vs


def _front_cut(a, point, tilt, mat):
    """Everything in front of the mouth plane, as a big box (the cut face it leaves is the flat rim)."""
    t = math.radians(tilt)
    n = Vector((0.0, -math.cos(t), math.sin(t)))           # out of the mouth: forward and a little up
    u = Vector((1.0, 0.0, 0.0))
    w = n.cross(u)
    p0 = Vector(point)
    pts = [p0 + n * d + u * x + w * y for d in (0.0, 20.0) for x in (-20.0, 20.0) for y in (-20.0, 20.0)]
    vs = [a.bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(a.bm, input=vs)
    vs = [v for v in vs if v.is_valid and v.link_faces]
    bmesh.ops.recalc_face_normals(a.bm, faces=K.faces_of(vs))
    a._finish(vs, mat)
    return vs


def cave_cutter(a):
    """The cavity (its faces become the cave's bare stone inside, two tones as broad facet patches) and the flat
    front cut (its face becomes the rim, in the outside rock)."""
    vs = _blob(a, *CAVITY, CAVE)
    nf = K.noise_field(scale=0.45, seed=11053)
    di = a._mi(CAVE_DARK)
    for f in K.faces_of(vs):
        if nf(f.calc_center_median()) > 0.05:
            f.material_index = di
    _front_cut(a, *MOUTH, ROCK)


def crystal(a, label, at_origin=False):
    """One amethyst crystal: a six-sided prism with a long pointed tip and a short point at the root (the sheet's
    loose crystals are doubly terminated); three purples as broad facet regions (by noise, not facing)."""
    _, x, y, R, H, lx, ly, tw, seed = next(c for c in CRYSTALS if c[0] == label)
    rng = random.Random(seed)
    z0 = CRYSTAL_Z
    if at_origin:
        x, y, lx, ly, z0 = 0.0, 0.0, 0.0, 0.0, 0.0
    base = Vector((x, y, z0))
    axis = Vector((lx, ly, 1.0)).normalized()
    m = Matrix.Rotation(math.acos(max(-1.0, min(1.0, axis.z))), 3,
                        Vector((-axis.y, axis.x, 0)).normalized() if abs(axis.z) < 0.9999 else Vector((1, 0, 0)))
    m = m @ Matrix.Rotation(tw, 3, "Z")
    radii = [R * rng.uniform(0.86, 1.08) for _ in range(6)]
    pts = [base + m @ Vector((0, 0, 0))]
    for h in (0.14, 0.62):
        for k in range(6):
            t = 2 * math.pi * k / 6
            pts.append(base + m @ Vector((math.cos(t) * radii[k], math.sin(t) * radii[k] * 0.9, H * h)))
    pts.append(base + m @ Vector((R * 0.05, 0.0, H)))
    vs = [a.bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(a.bm, input=vs)
    vs = [v for v in vs if v.is_valid and v.link_faces]
    bmesh.ops.recalc_face_normals(a.bm, faces=K.faces_of(vs))
    a._finish(vs, MID)
    nf = K.noise_field(scale=0.6, seed=seed)
    li, di = a._mi(LIGHT), a._mi(DARK)
    for f in K.faces_of(vs):
        v = nf(f.calc_center_median())
        if v > 0.2:
            f.material_index = li
        elif v < -0.3:
            f.material_index = di
    K.texture(a, vs, amp=0.02, scale=0.6, jitter=0.02, seed=seed)
    return vs


def crystals(a):
    for c in CRYSTALS:
        crystal(a, c[0])


def lip(a, at_origin=False):
    out = []
    for x, y, w, d, h, seed in LIP:
        vs = K.hull_rock(a, (w, d, h), loc=(x, y - (-3.5 if at_origin else 0), 0), seed=seed, mat=ROCK,
                         rings=LIP_RINGS, jitter=0.07, rot=0.3 * (seed % 5), keep_bottom=True)
        K.blend(a, vs, ROCK, ROCK_DARK, K.noise_field(scale=0.3, seed=seed), level=0.15, width=0.4, steps=1)
        K.texture(a, vs, amp=0.05, scale=0.4, jitter=0.04, seed=seed)
        out += vs
    return out


RIM_TUBE = 0.85             # the rolled rim: tube radius, and how far it sits out from the cavity's edge
RIM_OUT = 0.55


def _mouth_frame():
    t = math.radians(MOUTH[1])
    n = Vector((0.0, -math.cos(t), math.sin(t)))
    u = Vector((1.0, 0.0, 0.0))
    return Vector(MOUTH[0]), n, u, n.cross(u)


def rim_roll(a, segs=16, sides=6):
    """The mouth's lip: a thick, rounded, faceted roll of stone right round the opening (a low-poly torus that
    follows the cavity's edge on the cut plane and bulges forward), so the lip is chunky and round, not a thin
    edge."""
    p0, n, u, w = _mouth_frame()
    c, radii, seed = CAVITY
    c = Vector(c)
    cp = c - n * n.dot(c - p0)                          # the cavity's centre, on the cut plane
    rng = random.Random(seed + 7)

    def inside_cavity(q):
        d = q - c
        return (d.x / radii[0]) ** 2 + (d.y / radii[1]) ** 2 + (d.z / radii[2]) ** 2 < 1.0

    rows = []
    for i in range(segs):
        th = 2 * math.pi * i / segs
        r_dir = u * math.cos(th) + w * math.sin(th)
        lo, hi = 0.0, 8.0                               # the cavity's edge along r_dir (bisection)
        for _ in range(24):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if inside_cavity(cp + r_dir * mid) else (lo, mid)
        centre = cp + r_dir * (lo + RIM_OUT) + n * 0.15
        tube = RIM_TUBE * rng.uniform(0.88, 1.1)
        ring = []
        for k in range(sides):
            ph = 2 * math.pi * k / sides
            ring.append(centre + (r_dir * math.cos(ph) + n * math.sin(ph)) * tube)
        rows.append(ring)
    bm = a.bm
    vrows = [[bm.verts.new(q) for q in ring] for ring in rows]
    faces = []
    for i in range(segs):
        r0, r1 = vrows[i], vrows[(i + 1) % segs]
        for k in range(sides):
            faces.append(bm.faces.new((r0[k], r0[(k + 1) % sides], r1[(k + 1) % sides], r1[k])))
    vs = [v for row in vrows for v in row]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    a._finish(vs, ROCK)
    K.blend(a, vs, ROCK, ROCK_DARK, K.noise_field(scale=0.35, seed=seed + 7), level=0.15, width=0.4, steps=1)
    K.texture(a, vs, amp=0.05, scale=0.5, jitter=0.04, seed=seed + 7)
    return vs


def inside(a):
    crystals(a)
    lip(a)


NOTES = {
    "Amethyst": "amethyst geode: a thick-walled hollow faceted rock dome open to the front, its cavity bare stone, seven "
                "purple crystals (a tall main one fanned by smaller ones) on the cave floor, and a low lip of rocks "
                "across the mouth; one closed mesh",
    "AmethystShellTop": "Top Shell: the thick-walled hollow faceted dome, bare stone inside",
    "AmethystShellBottom": "Bottom Shell: the low lip of rocks across the cave mouth",
    "AmethystShard": "Crystal (reusable): six-sided purple crystal with a long pointed tip and a short root point",
}


def build(render=True):
    M.coll(NUM, TITLE)
    palette()
    specs = [("Amethyst", "hero", shell, 4000, "hull"),
             ("AmethystShellTop", "part", shell, 1000, "hull"),
             ("AmethystShellBottom", "part", lambda a: lip(a, True), 1000, "hull"),
             ("AmethystShard", "part", lambda a: crystal(a, "Main", True), 1000, "hull")]
    objs = [M.mk(SHEET, n, fn, subject=TITLE, role=r, notes=NOTES[n], budget=b, collision=c)
            for n, r, fn, b, c in specs]
    audits = []
    for o in objs:
        if o.name in ("Amethyst", "AmethystShellTop"):
            M.carve(o, shell, cave_cutter)
            M.merge_in(o, shell, rim_roll)
        if o.get("kit_role") == "hero":
            M.merge_in(o, shell, inside)
            M.union_loose(o)
            m004.floor_cut(o)
        audits.append(M.finish(o, union=o.name in ("AmethystShellTop", "AmethystShellBottom")))
    M.display(NUM, objs, TITLE)
    out = {"audit": audits, "problems": K.check(objs)}
    if render:
        hero_o, top_o, bottom_o, shard_o = objs
        saved = M.explode(objs[1:], {})
        try:
            hx, hy = hero_o.location.x, hero_o.location.y
            top_o.location = (hx + 40, hy + 1.0, 5.0)
            bottom_o.location = (hx + 40, hy - 4.0, 0)
            shard_o.location = (hx + 40 + 6.5, hy - 2.0, 1.0)
            out["views"] = M.views(NUM, [hero_o], extra={"exploded": (objs[1:], -14, 12)})
        finally:
            M.restore(saved)
            M.display(NUM, objs, TITLE)
    return out
