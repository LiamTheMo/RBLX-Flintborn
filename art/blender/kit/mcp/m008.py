"""008 Azurite (references/008.png): chunky bright-blue azurite crystals (a main crystal, a large side crystal on
the left, two on the right) growing out from behind a big peaked base rock with side rocks.

    import importlib, m008; importlib.reload(m008); m008.build()

Parts as on the sheet: Main Crystal (x1), Side Crystal (x1 left, x2 right; one reusable part), Base Rock (x1),
Side Rock (x2). The hero is their union.
"""
import math
import random

import bmesh
from mathutils import Matrix, Vector

import kit_mcp as K
import kit_models as M
import m004

NUM, TITLE, SHEET = 8, "Azurite", "M008"
AZ_LIGHT, AZ_MID, AZ_DARK = "m008_azurite_light", "m008_azurite_mid", "m008_azurite_dark"
ROCK_L, ROCK_M, ROCK_D = "m008_rock_light", "m008_rock_mid", "m008_rock_dark"

# crystals: (label, x, y, radius, height, lean x, lean y, twist, seed, base z)
CRYSTALS = (("Main", 0.3, 1.0, 2.35, 8.4, 0.02, 0.08, 0.2, 8011, 2.0),
            ("Left", -2.6, 0.5, 2.25, 7.0, -0.42, 0.05, 0.5, 8012, 1.6),
            ("Right", 2.9, 0.6, 1.8, 5.6, 0.45, 0.06, -0.4, 8013, 1.5),
            ("RightFront", 3.3, -1.0, 1.45, 4.4, 0.5, -0.2, 0.9, 8014, 1.2))
# rocks: (label, x, y, w, d, h, seed, rings)
PEAK = [(0.0, 1.0, 7), (0.35, 0.9, 7), (0.7, 0.55, 6), (1.0, 0.15, 3)]
ROUND = [(0.0, 0.9, 7), (0.35, 1.0, 7), (0.7, 0.78, 6), (1.0, 0.36, 4)]
ROCKS = (("Base", 0.0, -1.6, 6.6, 4.6, 4.2, 8031, PEAK), ("SideL", -4.0, -1.0, 2.8, 2.5, 2.2, 8032, ROUND),
         ("SideR", 4.1, -1.4, 2.6, 2.3, 2.0, 8033, ROUND), ("Back", -0.4, 2.6, 4.2, 3.0, 2.6, 8034, ROUND),
         ("BackL", -3.4, 2.0, 2.4, 2.1, 1.8, 8035, ROUND), ("BackR", 2.6, 2.4, 2.4, 2.2, 1.7, 8036, ROUND))


def palette():
    K.set_colour(AZ_LIGHT, "#2FB4EA", rough=0.4)
    K.set_colour(AZ_MID, "#1689D8", rough=0.4)
    K.set_colour(AZ_DARK, "#0E62B0", rough=0.4)
    K.set_colour(ROCK_L, "#A39089", rough=0.92)
    K.set_colour(ROCK_M, "#8A7973", rough=0.92)
    K.set_colour(ROCK_D, "#716560", rough=0.92)


def crystal(a, label, origin=None):
    """One azurite crystal: a fat six-sided prism (width about 0.55 of its height) with a short faceted top of
    three planes to a blunt point; flat root. The three blues are broad facet regions (by noise, not facing)."""
    _, x, y, R, H, lx, ly, tw, seed, z0 = next(c for c in CRYSTALS if c[0] == label)
    rng = random.Random(seed)
    if origin is not None:
        x, y, lx, ly, z0 = origin[0], origin[1], 0.0, 0.0, 1.2
    base = Vector((x, y, z0 - 1.2))
    axis = Vector((lx, ly, 1.0)).normalized()
    m = Matrix.Rotation(math.acos(max(-1.0, min(1.0, axis.z))), 3,
                        Vector((-axis.y, axis.x, 0)).normalized() if abs(axis.z) < 0.9999 else Vector((1, 0, 0)))
    m = m @ Matrix.Rotation(tw, 3, "Z")
    radii = [R * rng.uniform(0.86, 1.08) for _ in range(6)]
    pts = []
    for h, f in ((0.0, 0.78), (0.14, 1.0), (0.66, 1.0), (0.82, 0.62)):
        for k in range(6):
            t = 2 * math.pi * k / 6
            pts.append(base + m @ Vector((math.cos(t) * radii[k] * f, math.sin(t) * radii[k] * f * 0.88, H * h)))
    pts.append(base + m @ Vector((R * 0.1, R * 0.05, H)))
    pts.append(base + m @ Vector((-R * 0.22, 0.0, H * 0.95)))
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    vs = [v for v in vs if v.is_valid and v.link_faces]
    bmesh.ops.recalc_face_normals(bm, faces=K.faces_of(vs))
    a._finish(vs, AZ_MID)
    nf = K.noise_field(scale=0.35, seed=seed)
    li, di = a._mi(AZ_LIGHT), a._mi(AZ_DARK)
    for f in K.faces_of(vs):
        v = nf(f.calc_center_median())
        if v > 0.2:
            f.material_index = li
        elif v < -0.25:
            f.material_index = di
    K.texture(a, vs, amp=0.03, scale=0.5, jitter=0.025, seed=seed)
    return vs


def rocks(a, which=None, at_origin=False):
    out = []
    for label, x, y, w, d, h, seed, rings in ROCKS:
        if which is not None and label not in which:
            continue
        vs = K.hull_rock(a, (w, d, h), loc=(0, 0, 0) if at_origin else (x, y, 0), seed=seed, mat=ROCK_M,
                         rings=rings, jitter=0.06, rot=0.37 * seed % 3.0, keep_bottom=True)
        nf = K.noise_field(scale=0.3, seed=seed)
        lm, dm = a._mi(ROCK_L), a._mi(ROCK_D)
        for f in K.faces_of(vs):
            v = nf(f.calc_center_median())
            if v > 0.2:
                f.material_index = lm
            elif v < -0.25:
                f.material_index = dm
        K.texture(a, vs, amp=0.04, scale=0.4, jitter=0.04, seed=seed)
        out += vs
    return out


def hero(a):
    rocks(a)
    for c in CRYSTALS:
        crystal(a, c[0])


NOTES = {
    "Azurite": "azurite crystal node: four chunky bright-blue faceted crystals (main, a large left one, two on the "
               "right) growing out from behind a big peaked base rock with side rocks; three blues and three rock "
               "tones as broad facet regions; one closed mesh",
    "AzuriteMainCrystal": "Main Crystal: fat six-sided azurite crystal with a short faceted top, flat root",
    "AzuriteSideCrystal": "Side Crystal (reusable for all three side crystals): fat six-sided azurite crystal",
    "AzuriteBaseRock": "Base Rock: big peaked faceted rock that the crystals grow behind",
    "AzuriteSideRock": "Side Rock (reusable, x2): rounded faceted rock",
}


def build(render=True):
    M.coll(NUM, TITLE)
    palette()
    specs = [("Azurite", "hero", hero, 4000, "hull"),
             ("AzuriteMainCrystal", "part", lambda a: crystal(a, "Main", origin=(0, 0)), 1000, "hull"),
             ("AzuriteSideCrystal", "part", lambda a: crystal(a, "Left", origin=(0, 0)), 1000, "hull"),
             ("AzuriteBaseRock", "part", lambda a: rocks(a, ("Base",), True), 1000, "hull"),
             ("AzuriteSideRock", "part", lambda a: rocks(a, ("SideL",), True), 1000, "hull")]
    objs = [M.mk(SHEET, n, fn, subject=TITLE, role=r, notes=NOTES.get(n.replace("M008", ""), ""), budget=b,
                 collision=c) for n, r, fn, b, c in specs]
    audits = []
    for o in objs:
        if o.get("kit_role") == "hero":
            M.union_loose(o)
            m004.floor_cut(o)
        audits.append(M.finish(o, union=False))
    M.display(NUM, objs, TITLE)
    out = {"audit": audits, "problems": K.check(objs)}
    if render:
        hero_o, main_o, side_o, base_o, srock_o = objs
        saved = M.explode(objs[1:], {})
        try:
            hx, hy = hero_o.location.x, hero_o.location.y
            main_o.location = (hx + 40, hy + 0.5, 5.0)
            side_o.location = (hx + 40 - 5.0, hy, 4.0)
            base_o.location = (hx + 40, hy - 1.0, 0)
            srock_o.location = (hx + 40 - 5.5, hy - 2.0, 0)
            out["views"] = M.views(NUM, [hero_o], extra={"exploded": (objs[1:], -12, 12)})
        finally:
            M.restore(saved)
            M.display(NUM, objs, TITLE)
    return out
