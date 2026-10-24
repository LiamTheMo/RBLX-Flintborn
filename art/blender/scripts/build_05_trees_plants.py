"""Build sheet 05: Trees & Plants (16 assets) for Flintborn.

Run headless:
    blender --background --factory-startup --python art/blender/scripts/build_05_trees_plants.py

Notes on the kit:
- bmesh icosphere subdivisions: 1 = bare icosahedron (20 tris), 2 = 80, 3 = 320.
- Creating an icosphere can invalidate BMVert/BMFace references taken from
  earlier parts of the same Asset, so faces that need a later pass are tagged
  with temporary int layers ("fb_grp", "fb_fam") instead of kept in lists. Both
  layers are created before any geometry, because adding a layer also
  reallocates the faces.
- Foliage and bark are "painted" per facet from the palette by how much each
  facet faces the studio key light (front-left-top), with a little noise, so the
  lit side reads yellow-green and the shaded side dark, as on the sheet.
"""

import math
import os
import random
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Euler, Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "lib"))
import flintkit as fk  # noqa: E402

TAU = 2 * math.pi
Z = Vector((0, 0, 1))

# Final width (X) x height (Z) in studs. Proportions follow the reference sheet,
# within 25% of the README scale table.
SIZES = {
    "BroadleafTreeStout": (19.8, 17.6), "BroadleafTreeTall": (21.5, 20.5),
    "BroadleafTreeWideOld": (30, 21), "BroadleafTreeLeaning": (20, 19.5),
    "PineTreeShortWide": (16.5, 17.5), "PineTreeTallNarrow": (15.5, 23),
    "PineTreeMature": (20.5, 19.5), "PineTreeYoung": (9, 14),
    "ShrubLowWide": (7, 4.2), "ShrubTallDense": (5.6, 5.2), "BerryBush": (6.2, 4.3),
    "BroadLeafHerb": (4, 2.5), "GrassTuftLarge": (3.3, 1.9), "GrassClumpSmall": (2, 1.4),
    "WildflowerWhite": (3.3, 2.3), "FernLeafy": (4.2, 2.4),
}

# Depth (Y) of each asset in the previous build; fit_size keeps the new depth
# within about 20% of it, since the lobby places these assets.
DEPTH0 = {
    "BroadleafTreeStout": 11.7, "BroadleafTreeTall": 10.4, "BroadleafTreeWideOld": 14.8,
    "BroadleafTreeLeaning": 10.1, "PineTreeShortWide": 15.1, "PineTreeTallNarrow": 13.2,
    "PineTreeMature": 16.6, "PineTreeYoung": 10.3, "ShrubLowWide": 5.3, "ShrubTallDense": 4.9,
    "BerryBush": 5.3, "BroadLeafHerb": 2.6, "GrassTuftLarge": 2.6, "GrassClumpSmall": 1.7,
    "WildflowerWhite": 2.5, "FernLeafy": 3.8,
}

# Direction *towards* the painted light: upper left, a little more from the side
# than the studio key (front-left-top), so the facets the camera sees split into
# lit and shaded halves the way the sheet paints them.
LIGHT = Vector((-0.75, -0.32, 0.58)).normalized()

# Facet-painting families: palette keys from darkest to lightest band, the
# brightness Tint multiplier of each band, the cut points between bands on
# dot(normal, LIGHT), and the per-facet noise. The bands are tuned so the studio render matches the
# sheet's olive greens and mid-brown bark.
F_LEAF, F_WOOD, F_PINE, F_PLANT, F_GRASS, F_GROOVE = 1, 2, 3, 4, 5, 6
FAMILIES = {
    F_LEAF: (("pine_dark", "leaf_dark", "grass_dark", "grass_ground"), (0.55, 0.62, 0.76, 0.86),
             (0.0, 0.3, 0.74), 0.14),
    F_WOOD: (("wood_dark", "wood", "bark"), (0.8, 0.85, 0.85), (0.2, 0.7), 0.18),
    F_GROOVE: (("wood_dark", "wood_dark", "wood"), (0.75, 0.88, 0.9), (0.25, 0.72), 0.18),
    F_PINE: (("pine_dark", "pine_dark", "grass_dark"), (0.5, 0.66, 0.7), (0.05, 0.6), 0.14),
    F_PLANT: (("pine_dark", "leaf_dark", "grass_dark", "grass_ground"), (0.6, 0.74, 0.84, 0.9),
              (-0.4, -0.1, 0.35), 0.16),
    F_GRASS: (("leaf_dark", "grass_ground", "grass_light"), (0.7, 0.8, 0.85), (0.0, 0.45), 0.15),
}
F_FLOWERLEAF = 7
FAMILIES[F_FLOWERLEAF] = (("pine_dark", "leaf_dark", "grass_dark", "leaf_light"),
                         (0.6, 0.7, 0.8, 0.86), (-0.15, 0.25, 0.7), 0.16)
F_HERB = 8
FAMILIES[F_HERB] = (("pine_dark", "leaf_dark", "grass_dark", "leaf_light"),
                   (0.62, 0.74, 0.86, 0.92), (-0.15, 0.22, 0.6), 0.14)
TWO_SIDED = {F_PLANT}

# Foliage is not split into contrasting palette bands any more: every foliage facet keeps
# one palette green and gets a continuous RGB Tint instead, so canopies read as soft
# gradients (lit warm yellow-green on top, deeper cooler green underneath) the way the
# reference paints them, with only gentle facet-to-facet steps. Per family:
#   (material, shadow RGB, lit RGB, facing range (lo, hi) on dot(normal, LIGHT),
#    weight of the face's own up-facing (per-lobe top light), canopy height gradient
#    (bottom, top) multipliers, per-facet noise)
SOFT = {
    F_LEAF: ("leaf", (0.50, 0.70, 0.48), (1.06, 1.03, 0.70), (-0.55, 0.85), 0.45, (0.60, 1.08), 0.12),
    F_PINE: ("pine", (0.48, 0.56, 0.50), (1.20, 1.15, 0.88), (-0.45, 0.7), 0.15, (0.72, 1.04), 0.08),
    F_PLANT: ("leaf", (0.70, 0.78, 0.68), (1.06, 1.04, 0.88), (-0.4, 0.6), 0.3, (0.82, 1.04), 0.06),
    F_GRASS: ("leaf_light", (0.58, 0.68, 0.56), (1.06, 1.04, 0.86), (-0.2, 0.6), 0.2, (0.32, 1.0), 0.06),
    F_FLOWERLEAF: ("leaf", (0.66, 0.74, 0.66), (1.06, 1.04, 0.88), (-0.3, 0.7), 0.3, (0.80, 1.04), 0.06),
    F_HERB: ("leaf", (0.66, 0.74, 0.66), (1.08, 1.05, 0.88), (-0.3, 0.7), 0.3, (0.80, 1.04), 0.05),
}
# shrubs: deeper greens and more ball-to-ball contrast than the tree canopies
SHRUB_SOFT = {F_LEAF: ("leaf", (0.38, 0.52, 0.42), (0.90, 1.0, 0.90), (-0.5, 0.8), 0.5, (0.56, 0.92), 0.12)}
# bark: warm the painted wood bands toward the reference's darker red-brown trunks
WOOD_WARM = (0.84, 0.74, 0.64)


def _smooth01(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------------------
# Generic helpers (all take an fk.Asset)
# ---------------------------------------------------------------------------


def new_asset(name, category, seed=None):
    a = fk.Asset(name, category, seed=seed)
    a.bm.faces.layers.int.new("fb_grp")
    a.bm.faces.layers.int.new("fb_fam")
    return a


def fam_mark(a, faces, fam):
    lay = a.bm.faces.layers.int["fb_fam"]
    for f in faces:
        f[lay] = fam
    return faces


def mark_verts(a, verts, fam):
    return fam_mark(a, fk._faces_of(verts), fam)


def paint(a, faces, mat, tint=None, var=0.06, fam=0):
    """Assign a palette material, a per-face Tint and a painting family."""
    mi = a._mi(mat)
    t = tint if tint is not None else 1.0 + a.rng.uniform(-a.tint_var, a.tint_var)
    for f in faces:
        f.material_index = mi
        f.smooth = False
        ft = t * (1.0 + a.rng.uniform(-var, var))
        for loop in f.loops:
            loop[a.tint_layer] = (ft, ft, ft, 1.0)
    if fam:
        fam_mark(a, faces, fam)
    return faces


def relight(a, overrides=None):
    """Paint every family-tagged facet dark/mid/light by how it faces the key."""
    bm = a.bm
    lay = bm.faces.layers.int["fb_fam"]
    fams = dict(FAMILIES)
    fams.update(overrides or {})
    soft = dict(SOFT)
    soft.update(getattr(a, "soft", {}))  # per-asset soft-shading overrides (shrubs)
    tl = a.tint_layer
    # height range of each soft family, for the canopy's bottom-to-top gradient
    zr = {}
    for f in bm.faces:
        k = f[lay]
        if k in soft and not (overrides and k in overrides):
            z = f.calc_center_median().z
            lo, hi = zr.get(k, (z, z))
            zr[k] = (min(lo, z), max(hi, z))
    for f in bm.faces:
        k = f[lay]
        if not k:
            continue
        f.normal_update()
        if k in soft and not (overrides and k in overrides):
            mat, dark, lit, (s0, s1), up_w, (g0, g1), noise = soft[k]
            n = f.normal
            s = n.dot(LIGHT)
            if k in TWO_SIDED:
                s = max(s, -s - 0.15)
            s = (1 - up_w) * s + up_w * n.z
            w = _smooth01((s - s0) / (s1 - s0))
            lo, hi = zr[k]
            zn = (f.calc_center_median().z - lo) / max(hi - lo, 1e-4)
            g = g0 + (g1 - g0) * _smooth01(zn)
            j = 1.0 + a.rng.uniform(-noise, noise)
            base = f.loops[0][tl][0]
            rgb = [base * g * j * (dk + (lt - dk) * w) for dk, lt in zip(dark, lit)]
            f.material_index = a._mi(mat)
            for loop in f.loops:
                loop[tl] = (*rgb, 1.0)
            continue
        mats, tints, cuts, noise = fams[k]
        s = f.normal.dot(LIGHT)
        if k in TWO_SIDED:  # thin leaves: the underside reads lit like the top
            s = max(s, -s - 0.15)
        s += a.rng.uniform(-noise, noise)
        band = sum(s >= c for c in cuts)
        f.material_index = a._mi(mats[band])
        t = f.loops[0][tl][0] * tints[band]
        warm = WOOD_WARM if k in (F_WOOD, F_GROOVE) else (1.0, 1.0, 1.0)
        for loop in f.loops:
            loop[tl] = (t * warm[0], t * warm[1], t * warm[2], 1.0)


def new_face(bm, verts):
    out = []
    for v in verts:
        if not out or out[-1] is not v:
            out.append(v)
    if len(out) > 1 and out[0] is out[-1]:
        out.pop()
    if len(out) < 3:
        return None
    try:
        return bm.faces.new(out)
    except ValueError:
        return None


def floor_clamp(a, z=0.0):
    """Drop the temporary layers and flatten anything below the ground."""
    for name in ("fb_grp", "fb_fam"):
        lay = a.bm.faces.layers.int.get(name)
        if lay is not None:
            a.bm.faces.layers.int.remove(lay)
    for v in a.bm.verts:
        if v.co.z < z:
            v.co.z = z


def compact_materials(a):
    """Drop material slots that no face uses any more (after relight)."""
    used = sorted({f.material_index for f in a.bm.faces})
    remap = {old: new for new, old in enumerate(used)}
    for f in a.bm.faces:
        f.material_index = remap[f.material_index]
    a.mats = [a.mats[i] for i in used]


def finish(a, overrides=None):
    relight(a, overrides)
    compact_materials(a)
    floor_clamp(a)
    return a.finish()


def polar(r, az, z):
    return Vector((r * math.cos(az), r * math.sin(az), z))


def bezier(p0, p1, p2, n):
    p0, p1, p2 = Vector(p0), Vector(p1), Vector(p2)
    return [(1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2
            for t in (i / (n - 1) for i in range(n))]


def _frames(pts):
    n = len(pts)
    tans = [(pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized() for i in range(n)]
    up = Z if abs(tans[0].z) < 0.9 else Vector((1, 0, 0))
    nrm = tans[0].cross(up).normalized()
    out = []
    for i in range(n):
        if i:
            axis = tans[i - 1].cross(tans[i])
            if axis.length > 1e-6:
                nrm = Matrix.Rotation(tans[i - 1].angle(tans[i]), 3, axis.normalized()) @ nrm
            nrm = (nrm - tans[i] * nrm.dot(tans[i])).normalized()
        out.append((tans[i], nrm, tans[i].cross(nrm)))
    return out


def trunk(a, pts, radii, sides=16, flare=(), lobes=5, lobe_amp=0.6, grooves=4,
          groove_depth=0.16, twist=0.22, rough=0.03, mat="bark", streak="wood_dark",
          caps=(True, True), fam=F_WOOD):
    """Faceted trunk/branch tube. `flare` = per-ring buttress strength from the
    base (rounded root lobes); `grooves` spiral up the trunk as fluting, and the
    groove faces stay dark bark streaks."""
    bm = a.bm
    pts = [Vector(p) for p in pts]
    frames = _frames(pts)
    phase = a.rng.uniform(0, TAU)
    rings = []
    for i, (t, nrm, bi) in enumerate(frames):
        f = flare[i] if i < len(flare) else 0.0
        ring = []
        for j in range(sides):
            loc = TAU * j / sides
            th = loc + twist * i
            r = radii[i]
            if f:
                lob = ((1 + math.cos(lobes * (th - phase))) / 2) ** 2
                r *= 1 + f * (0.3 + lobe_amp * lob)
            if grooves:
                g = ((1 + math.cos(grooves * loc)) / 2) ** 6
                r *= 1 - groove_depth * g
            r *= 1 + a.rng.uniform(-rough, rough)
            ring.append(bm.verts.new(pts[i] + r * (math.cos(th) * nrm + math.sin(th) * bi)))
        rings.append(ring)
    body, dark = [], []
    per = sides // grooves if grooves else 0
    for i in range(len(rings) - 1):
        r1, r2 = rings[i], rings[i + 1]
        for j in range(sides):
            k = (j + 1) % sides
            fc = bm.faces.new((r1[j], r1[k], r2[k], r2[j]))
            (dark if per and streak and j % per == 0 else body).append(fc)
    if caps[0]:
        body.append(bm.faces.new(list(reversed(rings[0]))))
    if caps[1]:
        body.append(bm.faces.new(rings[-1]))
    t = 1.0 + a.rng.uniform(-a.tint_var, a.tint_var)
    paint(a, body, mat, t, 0.08, fam=fam)
    if dark:
        paint(a, dark, streak, t, 0.06, fam=F_GROOVE if fam else 0)


def tube(a, pts, radii, sides=5, mat="bark", caps=(True, True), fam=F_WOOD):
    trunk(a, pts, radii, sides=sides, grooves=0, rough=0.04, mat=mat, streak=None,
          caps=caps, fam=fam)


def lobe(a, c, r, subdiv=2, jitter=0.09, fam=F_LEAF, mat="leaf"):
    if isinstance(r, (int, float)):
        r = (r, r * 0.95, r * 0.92)
    verts = a.ico(r, c, mat=mat, subdiv=subdiv, jitter=jitter, face_tint_var=0.06,
                  rot=(a.rng.uniform(0, TAU), a.rng.uniform(0, TAU), a.rng.uniform(0, TAU)))
    mark_verts(a, verts, fam)
    return verts


def leaf(a, base, d0, length, width, curl=0.6, fold=0.3, segs=4, thick=0.025,
         profile="lance", mats=("leaf", "leaf_dark"), side=None, tint=None, var=0.05,
         bend=None, widths=None, fwd=None, fam=F_PLANT, twist=0.0):
    """Closed, folded low-poly leaf/blade (V-fold midrib). d0 = start direction;
    `curl` (rad) bends it down along its length (about `side`), distributed by
    `bend` weights. `widths` overrides the half-width per station (as fractions
    of `width`). `twist` turns the blade about its own axis toward the viewer
    (-Y) without changing the direction it bends."""
    bm = a.bm
    d = Vector(d0).normalized()
    sa = Vector(side).normalized() if side is not None else d.cross(Z)
    if sa.length < 1e-4:
        sa = Vector((1, 0, 0))
    sa.normalize()
    bend = bend or [1.0] * segs
    bsum = sum(bend)
    if twist:
        cands = [(Matrix.Rotation(s, 3, d) @ sa).cross(d).y for s in (twist, -twist)]
        twist = twist if cands[0] <= cands[1] else -twist
    c = Vector(base)
    step = length / segs
    stations = []
    for k in range(segs + 1):
        t = k / segs
        if widths is not None:
            w = width * widths[k]
        elif profile == "lance":
            w = width * math.sin(math.pi * min(1.0, t ** 0.75)) ** 0.9 if 0 < t < 1 else 0.0
            if k == 0:
                w = width * 0.15
        elif profile == "blade":
            w = width * (1 - t) ** 0.8
        elif profile == "round":
            w = width * math.sin(math.pi * t) ** 0.45
        else:  # "oval"
            w = width * math.sin(math.pi * t) ** 0.6
        wa = (Matrix.Rotation(twist, 3, d) @ sa).normalized() if twist else sa.copy()
        u = wa.cross(d).normalized()
        stations.append((c.copy(), u.copy(), w, d.copy(), wa))
        if k < segs:
            c = c + d * step
            d = (Matrix.Rotation(-curl * bend[k] / bsum, 3, sa) @ d).normalized()
    top, bot, lft, rgt = [], [], [], []
    for k, (p, u, w, dk, wa) in enumerate(stations):
        if w < 1e-4:
            v = bm.verts.new(p)
            top.append(v); bot.append(v); lft.append(v); rgt.append(v)
            continue
        th = thick * (0.4 + 0.6 * min(1.0, w / max(width, 1e-4)))
        off = dk * (fwd[k] if fwd is not None else 0.0)
        top.append(bm.verts.new(p + u * th))
        bot.append(bm.verts.new(p - u * th))
        lft.append(bm.verts.new(p + off + wa * w + u * fold * w))
        rgt.append(bm.verts.new(p + off - wa * w + u * fold * w))
    up_f, dn_f, half2 = [], [], []
    for k in range(segs):
        f = new_face(bm, (top[k], lft[k], lft[k + 1], top[k + 1]))
        f and up_f.append(f)
        f = new_face(bm, (top[k], top[k + 1], rgt[k + 1], rgt[k]))
        f and half2.append(f)
        f = new_face(bm, (bot[k], bot[k + 1], lft[k + 1], lft[k]))
        f and dn_f.append(f)
        f = new_face(bm, (bot[k], rgt[k], rgt[k + 1], bot[k + 1]))
        f and dn_f.append(f)
    t = tint if tint is not None else 1.0 + a.rng.uniform(-a.tint_var, a.tint_var)
    paint(a, up_f, mats[0], t, var, fam=fam)
    paint(a, half2, mats[1], t, var, fam=fam)
    paint(a, dn_f, mats[2] if len(mats) > 2 else mats[1], t * 0.95, var, fam=fam)
    return stations


def dir_from(az, pitch):
    return Vector((math.cos(pitch) * math.cos(az), math.cos(pitch) * math.sin(az),
                   math.sin(pitch)))


def side_of(az):
    """Horizontal leaf side axis for azimuth az (curl then droops outward)."""
    return Vector((math.sin(az), -math.cos(az), 0.0))


# ---------------------------------------------------------------------------
# Broadleaf trees: thick fluted trunk + clusters of faceted icosphere lobes,
# all laid out from the reference sheet (x, z in studs, y = depth, front -Y).
# ---------------------------------------------------------------------------


def roots(a, base, trunk_r, n, reach, height, r0):
    """Buttress roots: thick tapering tubes that arc from the lower trunk out and
    down into the ground."""
    base = Vector(base)
    phase = a.rng.uniform(0, TAU)
    for k in range(n):
        az = phase + TAU * k / n + a.rng.uniform(-0.25, 0.25)
        rk = reach * a.rng.uniform(0.8, 1.1)
        top = base + polar(trunk_r * 0.55, az, height * a.rng.uniform(0.85, 1.1))
        mid = base + polar(trunk_r * 1.05, az, height * 0.3)
        end = base + polar(rk, az, -0.15)
        trunk(a, bezier(top, mid, end, 5), [r0, r0 * 0.9, r0 * 0.72, r0 * 0.5, r0 * 0.3],
              sides=6, grooves=0, rough=0.05, twist=0.0, caps=(False, True))


def broadleaf(name, trunk_spec, branches, lobes, knots=(), grow=1.0, root_spec=None):
    a = new_asset(name, "Trees")
    trunk(a, **trunk_spec)
    if root_spec:
        roots(a, trunk_spec["pts"][0], trunk_spec["radii"][0], *root_spec)
    for spec in branches:
        pts, r0, r1 = spec[:3]
        n = 5
        pts = bezier(*pts, n) if len(pts) == 3 else [Vector(p) for p in pts]
        n = len(pts)
        rad = [r0 + (r1 - r0) * i / (n - 1) for i in range(n)]
        trunk(a, pts, rad, sides=8, grooves=2, groove_depth=0.1, twist=0.3,
              caps=(False, True))
    for c, r in lobes:
        lobe(a, c, tuple(x * grow for x in r))
    for c, r in knots:  # dark knot holes in the bark
        a.ico(r, c, mat="wood_dark", subdiv=1, tint=0.6)
    return finish(a)


def build_broadleaf_stout():
    zs = [0, 0.35, 0.9, 1.7, 2.8, 4.2, 5.8, 7.4, 9.0, 10.5]
    rad = [2.4, 2.25, 2.1, 1.98, 1.9, 1.86, 1.84, 1.78, 1.65, 1.45]
    spec = dict(pts=[(0, 0, z) for z in zs], radii=rad, flare=(0.35, 0.2, 0.08),
                lobes=6, lobe_amp=0.7, grooves=5, groove_depth=0.1, twist=0.1, sides=16)
    br = [
        (((-1.3, -0.1, 4.6), (-3.0, -0.2, 5.2), (-4.3, -0.3, 7.2)), 0.66, 0.44),
        (((1.3, -0.1, 4.9), (3.0, -0.2, 5.6), (4.1, -0.4, 7.4)), 0.64, 0.44),
    ]
    lobes = [
        ((0.4, 0.6, 11.6), (6.0, 4.9, 4.5)),     # big top-centre dome
        ((-2.6, 1.4, 12.3), (3.6, 3.4, 3.4)),    # top-left bump, behind
        ((3.4, 1.0, 12.8), (3.6, 3.3, 3.4)),     # top-right shoulder
        ((-6.0, -0.4, 9.3), (4.3, 4.0, 4.1)),    # left
        ((4.5, -1.3, 9.4), (3.9, 3.6, 3.8)),     # right front
        ((7.4, 1.0, 10.8), (3.0, 3.0, 3.6)),     # far right, behind
        ((-3.4, 2.4, 10.4), (3.6, 3.2, 3.5)),    # back filler
        ((2.2, 2.6, 10.0), (3.8, 3.2, 3.6)),     # back filler
    ]
    knots = [((0.25, -1.8, 3.4), (0.22, 0.18, 0.34))]
    return broadleaf("BroadleafTreeStout", spec, br, lobes, knots, root_spec=(5, 3.4, 2.3, 0.9))


def build_broadleaf_tall():
    pts = [(0, 0, 0), (0, 0, 0.35), (0, 0, 0.9), (0.05, 0, 1.8), (0.1, 0, 3.2),
           (0.15, 0, 5.0), (0.1, 0, 7.0), (0.0, 0, 9.0), (-0.1, 0, 11.0), (-0.1, 0, 12.6)]
    rad = [2.2, 2.05, 1.88, 1.74, 1.65, 1.56, 1.45, 1.3, 1.12, 0.96]
    spec = dict(pts=pts, radii=rad, flare=(0.4, 0.22, 0.08), lobes=5, lobe_amp=0.7,
                grooves=5, groove_depth=0.11, twist=0.15, sides=16)
    br = [
        (((-0.6, 0, 4.9), (-2.6, -0.1, 6.0), (-4.2, -0.2, 7.8)), 0.76, 0.46),
        (((0.7, 0, 7.4), (3.0, -0.1, 8.7), (4.9, -0.2, 9.9)), 0.7, 0.44),
        (((-0.2, 0, 12.2), (-1.3, 0, 13.2), (-2.4, 0.3, 14.6)), 0.74, 0.52),
        (((0.1, 0, 12.2), (1.3, 0, 13.4), (2.4, 0.3, 14.8)), 0.72, 0.52),
    ]
    lobes = [
        ((-2.8, 0.2, 16.0), (4.0, 3.3, 2.9)),    # crown left
        ((0.9, 0.4, 16.5), (4.6, 3.7, 3.0)),     # crown centre (highest)
        ((4.1, 0.2, 15.6), (3.1, 2.7, 2.6)),     # crown right
        ((-0.2, 2.0, 16.2), (3.8, 2.8, 2.8)),    # crown back filler
        ((-6.7, -0.3, 10.3), (4.6, 4.0, 4.3)),   # left lobe
        ((-3.4, -0.4, 9.0), (2.0, 1.9, 1.9)),    # left lobe, inner bump
        ((6.8, -0.2, 10.8), (4.5, 4.0, 4.2)),    # right lobe
        ((3.6, 0.2, 10.6), (2.0, 1.9, 1.9)),     # right lobe, inner bump
    ]
    knots = [((0.35, -1.6, 3.6), (0.18, 0.15, 0.34))]
    return broadleaf("BroadleafTreeTall", spec, br, lobes, knots, grow=1.1,
                     root_spec=(5, 3.3, 2.1, 0.82))


def build_broadleaf_wide_old():
    zs = [0, 0.5, 1.2, 2.1, 3.2, 4.5, 6.0, 7.6, 9.2, 10.6]
    pts = [(-0.4 + 0.2 * math.sin(z * 0.45), 0.12 * math.cos(z * 0.4), z) for z in zs]
    rad = [3.35, 3.25, 3.12, 3.02, 2.92, 2.8, 2.66, 2.46, 2.16, 1.84]
    spec = dict(pts=pts, radii=rad, flare=(0.55, 0.4, 0.22, 0.08), lobes=6,
                lobe_amp=0.9, grooves=6, groove_depth=0.2, twist=0.3, sides=20)
    br = [
        (((-1.5, 0, 6.6), (-4.8, -0.3, 6.6), (-8.2, -0.4, 7.4)), 1.25, 0.6),
        (((1.6, 0, 5.4), (5.6, -0.4, 6.6), (8.8, -0.4, 10.4)), 1.3, 0.6),
        (((6.2, -0.5, 7.6), (8.6, -0.6, 7.7), (10.6, -0.5, 8.6)), 0.55, 0.35),
        (((-0.8, 0, 9.8), (-2.8, 0, 11.0), (-4.4, 0.3, 12.8)), 1.1, 0.65),
        (((0.4, 0, 9.8), (1.8, 0, 11.2), (2.6, 0.3, 12.8)), 1.05, 0.65),
    ]
    lobes = [
        ((-0.3, 0.5, 15.8), (5.6, 5.0, 5.0)),    # top centre
        ((-4.0, 0.0, 15.2), (3.4, 3.0, 3.2)),    # top centre, left shoulder
        ((3.4, -0.2, 15.4), (3.4, 3.0, 3.0)),    # top centre, right shoulder
        ((-6.0, 0.6, 17.0), (2.4, 2.3, 2.3)),    # top-left knob
        ((5.4, 0.4, 16.0), (2.2, 2.2, 3.0)),     # top-right knob
        ((-8.5, -0.6, 9.2), (4.8, 4.2, 3.9)),    # left main
        ((-11.0, -0.4, 9.4), (2.8, 2.6, 2.8)),   # left main, outer
        ((-12.6, 0.0, 10.8), (2.5, 2.6, 2.6)),   # far left upper
        ((-12.4, 0.2, 8.0), (2.2, 2.4, 2.2)),    # far left lower
        ((-8.8, 0.6, 13.4), (2.7, 2.5, 2.4)),    # left top
        ((-8.9, 0.8, 5.9), (2.0, 1.9, 1.7)),     # left underside
        ((9.0, -0.3, 12.6), (4.6, 4.0, 3.4)),    # right top
        ((11.0, -0.6, 10.8), (2.8, 2.6, 2.6)),   # right, outer
        ((12.6, 0.0, 9.2), (2.7, 2.7, 3.6)),     # far right
        ((5.4, 1.0, 9.2), (2.2, 2.2, 2.0)),      # right, behind
        ((-3.2, 2.4, 13.0), (3.6, 3.2, 3.2)),    # back fillers
        ((3.4, 2.2, 13.6), (3.6, 3.2, 3.2)),
    ]
    return broadleaf("BroadleafTreeWideOld", spec, br, lobes, grow=1.16,
                     root_spec=(6, 6.2, 3.8, 1.5))


def build_broadleaf_leaning():
    # S-curve: leans left off the root flare, straightens, then bends up into the crown
    pts = [(3.5, 0, 0), (3.45, 0, 0.4), (3.25, 0, 1.2), (2.8, 0, 2.4), (1.8, 0, 4.4),
           (0.9, 0, 6.4), (0.3, 0, 8.4), (-0.3, 0, 10.3), (-1.0, 0, 11.9), (-1.5, 0.1, 13.2),
           (-1.7, 0.2, 14.4)]
    rad = [2.5, 2.32, 2.14, 1.94, 1.72, 1.54, 1.36, 1.2, 1.06, 0.95, 0.86]
    spec = dict(pts=pts, radii=rad, flare=(0.4, 0.2, 0.06), lobes=5, lobe_amp=0.7,
                grooves=4, groove_depth=0.12, twist=0.2, sides=14)
    br = [
        (((0.8, 0, 6.2), (-2.0, -0.1, 6.0), (-4.7, -0.2, 6.9)), 0.62, 0.36),
        (((1.0, 0, 7.6), (3.1, -0.1, 9.2), (4.8, -0.2, 11.6)), 0.58, 0.32),
        (((3.6, -0.15, 9.9), (5.0, -0.2, 10.6), (6.4, -0.2, 11.4)), 0.32, 0.24),
        (((2.6, 0, 3.8), (4.2, -0.1, 4.6), (5.4, -0.2, 6.2)), 0.44, 0.28),
    ]
    lobes = [
        ((-5.0, 0.4, 15.4), (2.9, 2.7, 2.6)),    # top cluster
        ((-2.4, -0.6, 16.6), (3.3, 3.0, 2.9)),
        ((0.8, 0.5, 15.9), (2.9, 2.7, 2.7)),
        ((-1.8, -1.6, 14.2), (2.8, 2.5, 2.5)),
        ((1.9, -0.9, 14.2), (2.1, 2.0, 1.9)),
        ((-2.4, 1.8, 14.8), (2.8, 2.4, 2.4)),
        ((-4.4, -1.2, 13.9), (2.2, 2.0, 2.0)),
        ((-7.6, 0.4, 7.7), (2.6, 2.4, 2.3)),     # left cluster
        ((-5.4, -0.9, 8.8), (2.4, 2.2, 2.1)),
        ((-5.6, 0.8, 6.4), (2.1, 1.9, 1.8)),
        ((-6.6, -0.5, 6.0), (1.9, 1.8, 1.7)),
        ((5.0, 0.6, 13.3), (2.2, 2.0, 2.0)),     # right upper cluster
        ((7.8, -0.6, 12.8), (2.5, 2.3, 2.3)),
        ((6.4, 0.2, 11.5), (2.0, 1.9, 1.8)),
        ((6.2, -0.8, 7.1), (2.3, 2.2, 2.1)),     # right lower cluster
        ((7.4, 0.8, 6.3), (1.9, 1.8, 1.7)),
        ((5.4, 0.6, 6.0), (1.7, 1.7, 1.6)),
    ]
    return broadleaf("BroadleafTreeLeaning", spec, br, lobes, grow=1.25,
                     root_spec=(4, 3.0, 1.9, 0.78))


# ---------------------------------------------------------------------------
# Pines: a few broad stacked skirts with drooping tips over a stout trunk
# ---------------------------------------------------------------------------


def pine_tier(a, zb, apex, R, tips=8, droop=0.09, notch=0.82, jag=0.03):
    """One cone skirt with a scalloped hem of broad drooping tips. Each tip flap
    bends at a raised shoulder ring, so the skirt bulges and then droops at the
    hem like the sheet's, instead of reading as a flat cone."""
    bm = a.bm
    h = apex - zb
    yaw = a.rng.uniform(0, TAU)
    top_v = bm.verts.new((0, 0, apex))
    outer, shoulder, mid = [], [], []
    n = 2 * tips
    for k in range(n):
        th = yaw + TAU * k / n + a.rng.uniform(-0.04, 0.04)
        if k % 2 == 0:
            rr = R * (1 + a.rng.uniform(-jag, jag))
            z = zb - droop * h * a.rng.uniform(0.8, 1.2)
        else:
            rr = R * notch
            z = zb + h * 0.06
        outer.append(bm.verts.new(polar(rr, th, z)))
        shoulder.append(bm.verts.new(polar(rr * 0.74, th, zb + h * (0.22 if k % 2 == 0 else 0.25))))
        mid.append(bm.verts.new(polar(rr * 0.42, th, zb + h * 0.46 + (0.03 * h if k % 2 else 0))))
    centre = bm.verts.new((0, 0, zb + h * 0.2))
    faces = []
    for k in range(n):
        j = (k + 1) % n
        faces.append(bm.faces.new((top_v, mid[k], mid[j])))
        faces.append(bm.faces.new((mid[k], shoulder[k], shoulder[j], mid[j])))
        faces.append(bm.faces.new((shoulder[k], outer[k], outer[j], shoulder[j])))
        faces.append(bm.faces.new((outer[j], outer[k], centre)))
    paint(a, faces, "pine", var=0.05, fam=F_PINE)


def pine(name, H, W, bottoms, widths, trunk_r, tips=8, droop=0.09):
    """bottoms/widths: hem height (fraction of H) and hem width (fraction of W)
    of each skirt, top skirt first."""
    a = new_asset(name, "Trees")
    zb = [b * H for b in bottoms]
    R = [w * W / 2 for w in widths]
    ztop = zb[-2] if len(zb) > 1 else zb[-1] + 1
    zs = [0, 0.3, 0.8, zb[-1] * 0.8 + 0.6, zb[-1] + 1.2, ztop]
    radii = [trunk_r * 1.12, trunk_r * 1.02, trunk_r * 0.96, trunk_r * 0.9, trunk_r * 0.82,
             trunk_r * 0.6]
    trunk(a, [(0, 0, z) for z in zs], radii, sides=9, flare=(0.28, 0.1, 0.02), lobes=4,
          lobe_amp=0.6, grooves=3, groove_depth=0.12, twist=0.12)
    for i in range(len(zb)):
        # lower skirts are squat cones whose tops hide under the skirt above, so
        # each hem steps out clearly from the one above it
        apex = H if i == 0 else zb[i - 1] + 0.5 * ((H if i == 1 else zb[i - 2]) - zb[i - 1])
        # more, finer tips on the wider skirts, as on the sheet
        n_tips = max(6, round(tips * (0.55 + 0.75 * R[i] / R[-1])))
        pine_tier(a, zb[i], apex, R[i], tips=n_tips, droop=droop)
    return finish(a)


# ---------------------------------------------------------------------------
# Shrubs: many small faceted balls on a dome shell, inner faces culled
# ---------------------------------------------------------------------------


def stems(a, count, spread, height, r=0.1, z0=0.0, front=0.0):
    """Woody stems fanning up from the root crown; `front` biases them toward -Y
    so they show between the lowest balls."""
    az0 = a.rng.uniform(0, TAU)
    for k in range(count):
        az = az0 + TAU * k / count + a.rng.uniform(-0.25, 0.25)
        base = polar(spread * 0.2 * a.rng.uniform(0.3, 1.0), az, z0)
        top = polar(spread * a.rng.uniform(0.7, 1.0), az, height * a.rng.uniform(0.85, 1.1))
        top.y -= front * spread
        mid = base.lerp(top, 0.5) + Vector((0, 0, height * 0.08))
        tube(a, [base, mid, top], [r, r * 0.85, r * 0.6], sides=4)


def shell_points(centre, radii, count, zmin, zmax=1.0):
    golden = math.pi * (3 - 5 ** 0.5)
    frac = (zmax - zmin) / 2
    total = int(count / frac + 0.5)
    pts = []
    for i in range(total):
        zz = 1 - 2 * (i + 0.5) / total
        if zz < zmin or zz > zmax:
            continue
        rr = math.sqrt(1 - zz * zz)
        th = golden * i
        d = Vector((rr * math.cos(th), rr * math.sin(th), zz))
        pts.append((Vector((centre[0] + radii[0] * d.x, centre[1] + radii[1] * d.y,
                            centre[2] + radii[2] * d.z)), d))
    return pts


def ball(a, c, r, out_dir=None, cull=-0.15, subdiv=2, jitter=0.05, fam=F_LEAF,
         mat="leaf", tint=None, poke=False):
    """Closed faceted leaf ball. With `out_dir`, only the outward-facing half is
    subdivided to the icosphere-2 look; the side turned into the bush (hidden by
    the neighbouring balls) keeps the coarse icosahedron facets, which saves
    about a third of the triangles without opening any holes."""
    if out_dir is None:
        verts = a.ico((r, r, r * 0.95), c, mat=mat, subdiv=subdiv, jitter=jitter,
                      face_tint_var=0.06, tint=tint,
                      rot=(a.rng.uniform(0, TAU), a.rng.uniform(0, TAU), a.rng.uniform(0, TAU)))
        mark_verts(a, verts, fam)
        return
    bm = a.bm
    n0 = len(bm.verts)
    verts = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)["verts"]
    rot = Euler((a.rng.uniform(0, TAU), a.rng.uniform(0, TAU), a.rng.uniform(0, TAU)))
    bmesh.ops.rotate(bm, verts=verts, cent=(0, 0, 0), matrix=rot.to_matrix())
    front = [f for f in fk._faces_of(verts) if f.calc_center_median().normalized().dot(out_dir) > cull]
    if poke:  # cheaper: split each outward face into three around a raised centre
        bmesh.ops.poke(bm, faces=front)
    else:
        edges = list({e for f in front for e in f.edges})
        bmesh.ops.subdivide_edges(bm, edges=edges, cuts=1, use_grid_fill=True)
    bm.verts.ensure_lookup_table()
    verts = [bm.verts[i] for i in range(n0, len(bm.verts))]
    for v in verts:
        v.co = v.co.normalized() * (1 + a.rng.uniform(-jitter, jitter))
    a.transform(verts, c, (0, 0, 0), (r, r, r * 0.95))
    a._finish(verts, mat, tint, 0.0, 0.06)
    faces = fk._faces_of(verts)
    hidden = core_hidden(a, faces)
    fam_mark(a, [f for f in faces if f not in hidden], fam)
    if hidden:
        bmesh.ops.delete(bm, geom=list(hidden), context="FACES")


def ball_dome(a, centre, radii, count, rmin, rmax, zmin, big_every=4, cull=-0.25, zmax=1.0,
              skip=None, poke_small=True):
    pts = shell_points(centre, radii, count, zmin, zmax)
    for i, (p, d) in enumerate(pts):
        if skip and skip(d):
            continue
        big = i % big_every == 0
        r = a.rng.uniform(rmax * 0.92, rmax * 1.08) if big else a.rng.uniform(rmin, rmax * 0.85)
        out = Vector((d.x / radii[0], d.y / radii[1], d.z / radii[2])).normalized()
        ball(a, p + d * a.rng.uniform(-0.16, 0.02), r, out_dir=out, cull=cull,
             poke=poke_small and not big)
    return pts


def core(a, c, r):
    """Dark closed inner mass of the bush, shaded like the balls so the gaps read
    as leafy crevices. Ball faces buried inside it can never be seen, so later
    balls drop them (see core_hidden)."""
    a._core = (Vector(c), Vector(r))
    verts = a.ico(r, c, mat="leaf_dark", subdiv=2, jitter=0.0, tint=0.72, face_tint_var=0.08)
    return mark_verts(a, verts, F_LEAF)


def core_hidden(a, faces, k=0.9):
    """Faces whose every corner lies inside the core ellipsoid (shrunk to its
    flat-faceted inner radius)."""
    spec = getattr(a, "_core", None)
    if spec is None:
        return set()
    c, r = spec

    def inside(p):
        q = p - c
        return (q.x / r.x) ** 2 + (q.y / r.y) ** 2 + (q.z / r.z) ** 2 < k * k

    return {f for f in faces if all(inside(v.co) for v in f.verts)}


def build_shrub_low_wide():
    a = new_asset("ShrubLowWide", "Plants")
    a.soft = SHRUB_SOFT
    stems(a, 5, 2.4, 1.2, r=0.12, front=0.25)
    core(a, (0.1, 0, 1.15), (2.65, 1.5, 2.15))
    ball_dome(a, (0.1, 0, 1.15), (2.85, 1.7, 2.35), 24, 0.64, 0.92, zmin=-0.2,
              big_every=3, cull=0.12)
    # a lower ring of balls around the hem, raised so stems show between them
    for k in range(6):
        az = -math.pi / 2 + (k - 2.5) * 0.62 + a.rng.uniform(-0.1, 0.1)
        p = Vector((3.0 * math.cos(az) * 0.95, 1.85 * math.sin(az), 0.8))
        ball(a, p, a.rng.uniform(0.55, 0.66),
             out_dir=Vector((math.cos(az), math.sin(az), -0.2)).normalized(), cull=0.12)
    return finish(a)


def build_shrub_tall_dense():
    a = new_asset("ShrubTallDense", "Plants")
    a.soft = SHRUB_SOFT
    stems(a, 6, 1.5, 1.7, r=0.11, front=0.25)
    core(a, (0, 0, 2.85), (1.82, 1.57, 1.92))
    # leave the bottom-front open so the stems show, as on the sheet
    ball_dome(a, (0, 0, 2.85), (2.0, 1.75, 2.1), 30, 0.58, 0.8, zmin=-0.8, big_every=4,
              cull=0.12, skip=lambda d: d.z < -0.6 and d.y < -0.25 and abs(d.x) < 0.4)
    return finish(a)


def build_berry_bush():
    a = new_asset("BerryBush", "Plants")
    a.soft = SHRUB_SOFT
    stems(a, 6, 1.7, 1.3, r=0.11, front=0.25)
    centre, radii = Vector((0, 0, 1.95)), (2.5, 1.95, 1.7)
    core(a, centre, (2.32, 1.77, 1.52))
    ball_dome(a, centre, radii, 22, 0.62, 0.84, zmin=-0.5, big_every=4, cull=0.12,
              skip=lambda d: d.z < -0.3 and d.y < -0.3 and abs(d.x) < 0.35)
    # clusters of three berries on the front and top, as on the sheet
    spots = [(-0.55, 0.95), (0.35, 1.1), (0.45, 0.55), (-0.85, 0.35), (-0.15, 0.3),
             (0.7, 0.12)]
    for az_off, el in spots:
        az = -math.pi / 2 + az_off
        d = Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
        p = centre + Vector((d.x * radii[0], d.y * radii[1], d.z * radii[2])) + d * 0.5
        t1 = d.cross(Z).normalized() if abs(d.z) < 0.98 else Vector((1, 0, 0))
        t2 = d.cross(t1)
        r = 0.19
        ang0 = a.rng.uniform(0, TAU)
        for k in range(3):
            ang = ang0 + TAU * k / 3
            q = p + (math.cos(ang) * t1 + math.sin(ang) * t2) * r * 1.1
            a.ico(r * a.rng.uniform(0.92, 1.08), q, mat="berry", subdiv=1, tint=1.0,
                  rot=(a.rng.uniform(0, 3), a.rng.uniform(0, 3), 0))
    return finish(a)


# ---------------------------------------------------------------------------
# Ground plants
# ---------------------------------------------------------------------------


def build_broad_leaf_herb():
    a = new_asset("BroadLeafHerb", "Plants")
    r = a.rng
    # (azimuth deg, pitch deg, length, half-width, curl, bend weights, face twist)
    hook = [0.05, 0.08, 0.15, 0.9, 2.2, 0.6]
    arch = [0.2, 0.4, 0.7, 1.0, 1.2, 1.2]
    specs = [
        (-35, 87, 2.5, 0.42, 1.3, hook, 0.2),    # tall back-left, tip folds right
        (-12, 86, 2.5, 0.44, 1.4, hook, 0.2),    # tall back-right, tip folds right
        (-100, 78, 1.5, 0.38, 2.1, hook, 0.1),   # front-left, tip folds forward
        (-72, 80, 1.65, 0.39, 2.2, hook, 0.1),  # front-centre, tip folds forward
        (-158, 56, 2.2, 0.33, 0.6, arch, 0.8),   # left upper
        (184, 42, 2.0, 0.31, 0.75, arch, 0.8),  # left lower
        (-20, 50, 2.25, 0.33, 0.55, arch, 0.8),  # right upper
        (-42, 38, 1.8, 0.31, 0.85, arch, 0.7),  # right lower front
        (-135, 34, 1.1, 0.26, 0.5, arch, 0.5),   # bottom-left small
        (-55, 46, 1.05, 0.27, 0.9, arch, 0.4),   # bottom-right small
        (-88, 60, 1.2, 0.28, 1.2, arch, 0.2),    # bottom-front small
        (105, 74, 2.1, 0.29, 0.8, arch, 0.3),    # back filler
        (150, 58, 1.8, 0.28, 0.7, arch, 0.5),    # back-left filler
        (40, 60, 1.8, 0.28, 0.7, arch, 0.5),     # back-right filler
    ]
    for azd, p, L, W, curl, bend, tw in specs:
        az = math.radians(azd + r.uniform(-3, 3))
        d = dir_from(az, math.radians(p + r.uniform(-2, 2)))
        base = polar(0.1, az, 0.0) + Vector((0, 0.08, 0))
        leaf(a, base, d, L, W, curl=curl, fold=0.58, segs=7, thick=0.045,
             mats=("leaf", "leaf_dark"), bend=bend + [bend[-1]], side=side_of(az), twist=tw,
             widths=[0.3, 0.66, 0.9, 1.0, 1.0, 0.92, 0.62, 0.0], fam=F_HERB)
    return finish(a)


def grass(name, blades, seed):
    """blades: (base xy, azimuth, pitch deg, length, half-width, curl, kink)."""
    a = new_asset(name, "Plants", seed=seed)
    for (bx, by), az, p, L, W, curl, kink in blades:
        d = dir_from(az, math.radians(p))
        bend = [0.2, 0.3, 0.45, 0.6, 0.7] if not kink else [0.05, 0.1, 0.4, 1.6, 0.9]
        tw = 0.7 * abs(math.cos(az))
        leaf(a, Vector((bx, by, 0.0)), d, L, W, curl=curl + kink, fold=0.5, segs=5,
             thick=0.07, mats=("leaf_light", "leaf", "leaf_dark"), bend=bend,
             side=side_of(az), twist=tw, widths=[0.85, 1.0, 1.0, 0.92, 0.62, 0.0], fam=F_GRASS)
    return finish(a)


def tuft_blades(r, n, rx, ry, L0, L1, W0, W1, kink_p):
    """A wide oval tuft: most blades stand nearly upright; only the ones rooted at
    the ends of the oval lean and arch outward. A few short front blades kink
    forward at the tip."""
    blades = []
    for i in range(n):
        u = -1 + 2 * (i + 0.5) / n + r.uniform(-0.04, 0.04)
        row = i % 3  # back, middle, front
        fy = (0.8, 0.0, -0.8)[row] * r.uniform(0.6, 1.1)
        bx, by = u * rx * (1 - 0.25 * abs(fy)), fy * ry
        e = abs(u) ** 2.0
        az = math.atan2(fy * 0.8 + r.uniform(-0.15, 0.15), u * 1.4 + r.uniform(-0.15, 0.15))
        p = 88 - 46 * e - 10 * abs(fy) + r.uniform(-4, 4)
        L = (L1 - (L1 - L0) * e) * r.uniform(0.9, 1.04) * (0.92 if row == 2 else 1.0)
        curl = 0.15 + 1.0 * e + r.uniform(0, 0.2)
        kink = 0.0
        if row == 2 and abs(u) < 0.7 and r.random() < kink_p:
            kink, L, p = r.uniform(0.5, 0.7), L * 0.75, r.uniform(78, 84)
            az = -math.pi / 2 + r.uniform(-0.6, 0.6)
        blades.append(((bx, by), az, p, L, r.uniform(W0, W1), curl, kink))
    return blades


def build_grass_tuft_large():
    r = random.Random(1305)
    return grass("GrassTuftLarge", tuft_blades(r, 20, 0.95, 0.75, 1.35, 2.0, 0.17, 0.2, 0.45),
                 seed=1305)


def build_grass_clump_small():
    r = random.Random(1406)
    return grass("GrassClumpSmall", tuft_blades(r, 15, 0.52, 0.48, 0.85, 1.45, 0.1, 0.12, 0.35),
                 seed=1406)


def daisy(a, c, n, petals=5, R=0.3):
    """Flat daisy head: broad rounded petals around a domed yellow centre."""
    bm = a.bm
    n = Vector(n).normalized()
    t1 = n.cross(Z if abs(n.z) < 0.95 else Vector((1, 0, 0))).normalized()
    t2 = n.cross(t1)
    c = Vector(c)
    rot0 = a.rng.uniform(0, TAU)
    outline = []
    w = TAU / petals
    for i in range(petals):
        base = rot0 + i * w
        for off, rr in ((-0.5, 0.32), (-0.36, 0.86), (-0.15, 1.0), (0.15, 1.0), (0.36, 0.86)):
            ang = base + off * w
            cup = 0.14 * rr
            outline.append(c + (math.cos(ang) * t1 + math.sin(ang) * t2) * R * rr + n * cup * R)
    ring = [bm.verts.new(p) for p in outline]
    top = bm.verts.new(c + n * 0.03)
    bot = bm.verts.new(c - n * 0.05)
    faces = []
    m = len(ring)
    for i in range(m):
        j = (i + 1) % m
        faces.append(bm.faces.new((top, ring[i], ring[j])))
        faces.append(bm.faces.new((bot, ring[j], ring[i])))
    paint(a, faces, "flower_white", 1.0, 0.04)
    a.ico((R * 0.33, R * 0.33, R * 0.22), c + n * R * 0.14, mat="flower_yellow", subdiv=1,
          tint=1.0, rot=n.to_track_quat("Z", "Y").to_euler())


def build_wildflower_white():
    a = new_asset("WildflowerWhite", "Plants")
    r = a.rng
    # a leafy mound of broad pointed leaves: (azimuth deg, base radius, height,
    # pitch deg, size) - front leaves low and leaning toward the viewer, side
    # leaves spreading wide, back and centre leaves higher and more upright
    leaves = [(-90, 0.35, 0.35, 30, 0.75), (-60, 0.4, 0.25, 25, 0.75), (-120, 0.4, 0.25, 25, 0.75),
              (-75, 0.25, 0.7, 45, 0.65), (-105, 0.25, 0.75, 45, 0.65), (-40, 0.45, 0.5, 35, 0.7),
              (-140, 0.45, 0.5, 35, 0.7), (0, 0.75, 0.3, 22, 0.85), (180, 0.75, 0.3, 22, 0.85),
              (-15, 0.4, 0.8, 40, 0.7), (195, 0.4, 0.8, 40, 0.7), (20, 0.65, 0.15, 12, 0.8),
              (160, 0.65, 0.15, 12, 0.8), (60, 0.35, 0.6, 45, 0.7), (120, 0.35, 0.6, 45, 0.7),
              (90, 0.2, 0.95, 60, 0.65), (40, 0.3, 1.0, 55, 0.6), (140, 0.3, 1.0, 55, 0.6),
              (-90, 0.1, 1.1, 65, 0.55), (-30, 0.15, 1.05, 60, 0.55), (-150, 0.15, 1.05, 60, 0.55)]
    for azd, rad, z, pitch, size in leaves:
        az = math.radians(azd + r.uniform(-8, 8))
        size *= r.uniform(0.92, 1.08)
        base = polar(rad, az, z)
        tube(a, [polar(0.06, az, 0.0), base], [0.035, 0.03], sides=3, mat="leaf_dark",
             caps=(False, False), fam=0)
        d = dir_from(az, math.radians(pitch + r.uniform(-5, 5)))
        leaf(a, base, d, size, size * 0.46, curl=0.45, fold=0.32, segs=4, thick=0.025,
             widths=[0.3, 0.85, 1.0, 0.72, 0.0], mats=("leaf", "leaf_dark"), side=side_of(az),
             twist=0.3, var=0.06, fam=F_FLOWERLEAF)
    heads = [(-0.2, -0.1, 2.25), (-0.95, -0.2, 1.72), (0.6, -0.2, 1.82), (1.2, -0.1, 1.45),
             (-0.5, -0.5, 1.25), (0.22, -0.5, 1.4)]
    sizes = [0.28, 0.27, 0.28, 0.25, 0.21, 0.21]
    for i, ((hx, hy, hz), R) in enumerate(zip(heads, sizes)):
        top = Vector((hx, hy, hz))
        base = Vector((hx * 0.3, hy * 0.3, 0.0))
        mid = base.lerp(top, 0.5) + Vector((r.uniform(-0.05, 0.05), r.uniform(-0.05, 0.05), 0))
        tube(a, [base, mid, top], [0.045, 0.04, 0.036], sides=4, mat="leaf_dark",
             caps=(False, True), fam=0)
        if i < 4:  # a leaf part-way up the taller stems
            d = Vector((hx + 0.01, hy - 0.25, 0)).normalized()
            az = math.atan2(d.y, d.x)
            leaf(a, base.lerp(top, 0.6), dir_from(az, math.radians(50)), 0.5, 0.17, curl=0.4,
                 fold=0.3, segs=2, profile="lance", mats=("leaf", "leaf_dark"),
                 side=side_of(az), twist=0.5, fam=F_FLOWERLEAF)
        daisy(a, top, Vector((hx * 0.25, hy * 0.4 - 0.6, 1.0)), petals=5, R=R)
    return finish(a)


def frond(a, base, az, pitch, L, curl, pairs=7, span=0.52, segs=6, tw=0.0):
    """Fern frond: thin rachis with discrete, forward-angled leaflets (pinnae),
    each folded along its midrib."""
    bm = a.bm
    d = dir_from(az, pitch)
    sa = side_of(az)  # the frond arches outward about this axis
    c = Vector(base)
    step = L / segs
    pts, tans = [c.copy()], [d.copy()]
    for k in range(segs):
        w = 0.4 + 1.2 * k / segs
        c = c + d * step
        d = (Matrix.Rotation(-curl * w / segs, 3, sa) @ d).normalized()
        pts.append(c.copy())
        tans.append(d.copy())
    tube(a, pts, [0.045 - 0.028 * i / segs for i in range(segs + 1)], sides=3, mat="leaf",
         caps=(False, False), fam=F_PLANT)

    def at(t):
        x = t * segs
        i = min(int(x), segs - 1)
        f = x - i
        return pts[i].lerp(pts[i + 1], f), tans[i].lerp(tans[i + 1], f).normalized()

    t0, t1 = 0.2, 0.96
    gap = (t1 - t0) / pairs
    for k in range(pairs + 1):
        t = t0 + gap * k
        x = (t - t0) / (t1 - t0)
        env = max(0.3, math.sin(math.pi * min(1.0, 0.3 + 0.7 * x)) ** 0.5)
        p, tg = at(t)
        # leaflets lie in a plane twisted about the rachis toward the viewer
        sl = sa
        if tw:
            cands = [(Matrix.Rotation(s, 3, tg) @ sa).cross(tg).y for s in (tw, -tw)]
            sl = (Matrix.Rotation(tw if cands[0] <= cands[1] else -tw, 3, tg) @ sa).normalized()
        u = sl.cross(tg).normalized()
        terminal = k == pairs
        for s in ((1,) if terminal else (1, -1)):
            if terminal:
                e, ln = tg, span * L * 0.3
            else:
                e = (s * sl * 0.82 + tg * 0.55 + u * 0.16).normalized()
                ln = span * L * 0.46 * env
            # leaflet base width along the rachis, narrowing with the leaflets toward the tip
            b = gap * L * (1.12 * (0.55 + 0.45 * env) if not terminal else 0.7)
            f2 = tg - e * tg.dot(e)
            f2 = f2.normalized() if f2.length > 1e-4 else sl.copy()
            n2 = e.cross(f2).normalized()
            if n2.dot(u) < 0:
                n2 = -n2
            lift = n2 * ln * 0.08
            quad_pts = [p - f2 * b * 0.5,                       # base back
                        p + f2 * b * 0.5,                       # base front
                        p + e * ln * 0.78 + f2 * b * 0.42,      # front shoulder (tooth)
                        p + e * ln + f2 * b * 0.1 + lift,       # blunt tip
                        p + e * ln * 0.86 - f2 * b * 0.34,      # back shoulder
                        p + lift * 0.4]                         # midrib base
            for off, flip in ((Vector(), False), (-n2 * 0.014, True)):
                v = [bm.verts.new(q + off) for q in quad_pts]
                quads = [(v[5], v[1], v[2], v[3]), (v[5], v[3], v[4], v[0])]
                faces = [bm.faces.new(tuple(reversed(q)) if flip else q) for q in quads]
                paint(a, faces, "leaf", var=0.05, fam=F_PLANT)


def build_fern_leafy():
    """Nine arching fronds of separate forward-angled leaflets."""
    a = new_asset("FernLeafy", "Plants")
    r = a.rng
    # (azimuth deg, pitch deg, length, curl, face twist)
    specs = [(-100, 86, 2.45, 0.5, 0.0), (-55, 82, 2.35, 1.0, 0.5), (-18, 72, 2.3, 1.6, 0.8),
             (10, 64, 2.3, 2.0, 0.9), (-168, 72, 2.6, 1.8, 0.9), (-142, 58, 2.1, 2.1, 0.8),
             (-75, 72, 2.2, 2.4, 0.3), (-36, 58, 1.9, 2.0, 0.6), (118, 78, 2.2, 1.2, 0.5)]
    for azd, pd, L, curl, tw in specs:
        az = math.radians(azd + r.uniform(-4, 4))
        frond(a, polar(0.12, az, 0.0), az, math.radians(pd), L, curl, pairs=7, tw=tw)
    return finish(a)


# ---------------------------------------------------------------------------
# Sizing and rendering
# ---------------------------------------------------------------------------


def fit_size(obj, width, height):
    """Scale the finished mesh about its bottom-centre origin to the target size
    (XY uniformly by the X width, Z by the height)."""
    dims = obj.dimensions
    sxy, sz = width / dims.x, height / dims.z
    obj.data.transform(Matrix.Diagonal((sxy, sxy, sz, 1.0)))
    # keep the depth within the linked-lobby tolerance of the previous build
    lo, hi = 0.78 * DEPTH0[obj.name], 1.22 * DEPTH0[obj.name]
    dy = dims.y * sxy
    if not lo <= dy <= hi:
        obj.data.transform(Matrix.Diagonal((1.0, min(max(dy, lo), hi) / dy, 1.0, 1.0)))
    obj.data.update()
    bpy.context.view_layer.update()
    d = obj.dimensions
    obj["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    if obj.asset_data:
        obj.asset_data.description = (f"Flintborn {obj['flintkit_category']}: {obj.name} "
                                      f"({obj['studs']} studs)")
    return sxy, sz


def frame_tight(obj, azimuth, elevation, margin=1.1):
    scene = bpy.context.scene
    cam = bpy.data.objects["FB_Cam"]
    # frame the actual silhouette (every vertex), like the sheet's tight cells
    corners = [obj.matrix_world @ v.co for v in obj.data.vertices]
    centre = sum(corners, Vector()) / len(corners)
    az, el = math.radians(azimuth), math.radians(elevation)
    D = Vector((math.sin(az), -math.cos(az), math.tan(el))).normalized()
    rot = (-D).to_track_quat("-Z", "Y")
    right, up = rot @ Vector((1, 0, 0)), rot @ Vector((0, 1, 0))
    aspect = scene.render.resolution_x / scene.render.resolution_y
    tx = math.tan(cam.data.angle / 2) / margin
    ty = tx / aspect
    xs = [(c - centre).dot(right) for c in corners]
    ys = [(c - centre).dot(up) for c in corners]
    centre = centre + right * (max(xs) + min(xs)) / 2 + up * (max(ys) + min(ys)) / 2
    dist = 0.0
    for c in corners:
        p = c - centre
        pz = p.dot(D)
        dist = max(dist, abs(p.dot(right)) / tx + pz, abs(p.dot(up)) / ty + pz)
    cam.location = centre + D * dist
    cam.rotation_euler = rot.to_euler()
    bpy.data.objects["FB_Ground"].location = (centre.x, centre.y, min(c.z for c in corners))


def render_cells(objs, views, path, cols=4, cell=(384, 288), samples=32):
    scene = bpy.context.scene
    fk._studio(scene)
    bpy.data.objects["FB_Cam"].data.lens = 100
    scene.render.resolution_x, scene.render.resolution_y = cell
    scene.render.resolution_percentage = 100
    try:
        scene.eevee.taa_render_samples = samples
    except AttributeError:
        pass
    base, _ = os.path.splitext(path)
    cell_paths = []
    for i, o in enumerate(objs):
        for other in objs:
            other.hide_render = other is not o
        az, el, margin = views[o.name]
        frame_tight(o, az, el, margin)
        p = f"{base}_cells/{i + 1:02d}_{o.name}.png"
        os.makedirs(os.path.dirname(p), exist_ok=True)
        scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        cell_paths.append(p)
    for o in objs:
        o.hide_render = False
    rows = math.ceil(len(objs) / cols)
    w, h = cell
    sheet = np.ones((rows * h, cols * w, 4), dtype=np.float32)
    for i, p in enumerate(cell_paths):
        img = bpy.data.images.load(p, check_existing=False)
        px = np.array(img.pixels[:], dtype=np.float32).reshape(img.size[1], img.size[0], 4)
        rr, cc = divmod(i, cols)
        y0 = (rows - 1 - rr) * h
        sheet[y0:y0 + h, cc * w:cc * w + w] = px[:h, :w]
        bpy.data.images.remove(img)
    out = bpy.data.images.new("FB_Sheet", cols * w, rows * h, alpha=True)
    out.pixels = sheet.ravel()
    out.filepath_raw = path
    out.file_format = "PNG"
    out.save()
    bpy.data.images.remove(out)
    return path


def main():
    fk.reset_file()
    objs = [
        build_broadleaf_stout(),
        build_broadleaf_tall(),
        build_broadleaf_wide_old(),
        build_broadleaf_leaning(),
        pine("PineTreeShortWide", 17.5, 16.5, (0.64, 0.39, 0.2), (0.46, 0.81, 1.0), 1.85),
        pine("PineTreeTallNarrow", 23, 15.5, (0.75, 0.56, 0.35, 0.17), (0.41, 0.59, 0.78, 1.0),
             1.6),
        pine("PineTreeMature", 19.5, 20.5, (0.88, 0.71, 0.41, 0.19), (0.22, 0.46, 0.78, 1.0),
             2.2),
        pine("PineTreeYoung", 14, 9, (0.73, 0.5, 0.27), (0.42, 0.65, 1.0), 1.2, tips=7),
        build_shrub_low_wide(),
        build_shrub_tall_dense(),
        build_berry_bush(),
        build_broad_leaf_herb(),
        build_grass_tuft_large(),
        build_grass_clump_small(),
        build_wildflower_white(),
        build_fern_leafy(),
    ]
    for o in objs:
        sxy, sz = fit_size(o, *SIZES[o.name])
        print(f"FB05 {o.name:24s} tris={o['tris']:5d} studs={o['studs']} fit=xy {sxy:.2f} z {sz:.2f}")
    fk.layout_row(objs)
    fk.save(os.path.join(ROOT, "assets", "05_trees_plants.blend"))
    # the sheet is drawn with almost no perspective: a long lens, low for trees
    views = {o.name: ((-18, 8, 1.05) if o.name.startswith("Pine") else (-18, 11, 1.05))
             if o["flintkit_category"] == "Trees" else (-20, 16, 1.06) for o in objs}
    render_cells(objs, views, os.path.join(ROOT, "renders", "05_trees_plants.png"))
    print("FB05 done")


main()
