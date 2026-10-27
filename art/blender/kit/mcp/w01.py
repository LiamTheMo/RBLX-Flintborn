"""W01 Boulders, Rocks & Scatter: MCP builders (see kit_mcp.py for the shared tools).

    import importlib, w01; importlib.reload(w01); w01.boulder_row()
"""
import math
import random

import bpy
from mathutils import Vector

import kit_mcp as K

SHEET = "W01"
ROCK, MOSS, LEAF, PETAL, POLLEN = "w01_rock", "w01_moss", "w01_leaf", "w01_petal", "w01_pollen"
ROCK_COOL, ROCK_BASE = "w01_rock_cool", "w01_rock_base"      # cooler lavender-grey stone patches; damp earthy foot
ROCK_STAIN = "w01_rock_stain"                                # green-olive damp moss staining low on the faces
MOSS_LIME, LEAF_YOUNG = "w01_moss_lime", "w01_leaf_young"    # sunlit lime moss on top; new yellow-green leaves
MOSS_SUN = "w01_moss_sun"                                    # yellowest lime on the moss summits

# Barrel dome: near-vertical lower sides, broad rounded shoulder, a wide faceted top.
BARREL = [(0.0, 0.97, 11), (0.35, 1.0, 11), (0.62, 0.98, 10), (0.8, 0.9, 9), (0.93, 0.7, 7),
          (1.0, 0.45, 5)]
# Broad-based cone for upright rocks: wide foot, steady taper to a blunt top.
CONE = [(0.0, 1.0, 10), (0.2, 0.93, 10), (0.45, 0.78, 9), (0.68, 0.6, 8), (0.86, 0.45, 6), (1.0, 0.32, 5)]
# Tall tapering pillar for upright rocks and spires.
PILLAR = [(0.0, 1.0, 10), (0.25, 0.94, 10), (0.5, 0.8, 9), (0.72, 0.62, 8), (0.88, 0.42, 6), (1.0, 0.16, 4)]


def palette():
    # Calibrated 2026-10-27 with kit_mcp.calibrate(): each colour is chosen so the kit studio render
    # matches the master sheet's sampled colour (the studio's strong sun and contrast look brighten
    # everything, so base colours sit darker than the painted sheet). Check brightness in Studio.
    K.set_colour(ROCK, "#99897E")     # re-measured 2026-10-27 against the Boulder hero cell
    K.set_colour(ROCK_COOL, "#857D82")
    K.set_colour(ROCK_BASE, "#7A706C")
    K.set_colour(ROCK_STAIN, "#4F6A22")
    K.set_colour(MOSS, "#466101", low_spec=True)
    K.set_colour(MOSS_LIME, "#6E8803", low_spec=True)
    K.set_colour(MOSS_SUN, "#83950B", low_spec=True)
    K.set_colour(LEAF, "#385601", rough=0.85, low_spec=True)
    K.set_colour(LEAF_YOUNG, "#567902", rough=0.85, low_spec=True)
    K.set_colour(PETAL, "#F6F3EA", rough=0.7)
    K.set_colour(POLLEN, "#F2C230", rough=0.7)


def rock(a, size, loc=(0, 0, 0), seed=1, rings=BARREL, rot=0.0, lean=(0.0, 0.0), jitter=0.07, colour=True, shape=None,
         cuts=1, foot=True):
    """Faceted rock with real stone colouring: warm mauve base, broad cooler lavender-grey patches,
    a damp earthy band at the foot, and mottled Tint texture across the facets."""
    vs = K.hull_rock(a, size, loc=loc, seed=seed, mat=ROCK, rings=rings, jitter=jitter, rot=rot, lean=lean)
    if shape:
        shape(vs)                     # reshape (e.g. crease) before the split so the facets stay planar
    if colour:
        z0 = loc[2]
        # stone colour drifts warm -> cool from facet to facet (blend over whole facets), with a
        # gentle Tint texture per facet; then the facets are split (coplanar) so the damp foot
        # and any moss stain can fade smoothly up the faces
        K.blend(a, vs, ROCK, ROCK_COOL, K.noise_field(scale=0.18, seed=seed), level=0.25, width=0.5, steps=3)
        K.texture(a, vs, amp=0.05, scale=0.28, jitter=0.05, seed=seed)     # crisp tone step per facet
        vs = K.refine(a, vs, cuts)
        if foot:
            band = min(1.4, size[2] * 0.2)
            K.blend(a, vs, ROCK, ROCK_BASE, lambda c: -(c.z - z0), level=-band * 0.6, width=band, steps=2,
                    jitter=0.15, seed=seed)
    return vs


def crease(verts, angle, depth, width=0.35, top=0.85):
    """Push a rock's verts in along a vertical valley at angle (radians round its centre),
    fading out toward the crown, so the face reads as two merged masses."""
    if not verts:
        return
    cx = sum(v.co.x for v in verts) / len(verts)
    cy = sum(v.co.y for v in verts) / len(verts)
    z0 = min(v.co.z for v in verts)
    h = max(v.co.z for v in verts) - z0
    for v in verts:
        t = math.atan2(v.co.y - cy, v.co.x - cx)
        dt = (t - angle + math.pi) % (2 * math.pi) - math.pi
        if abs(dt) > width:
            continue
        zf = (v.co.z - z0) / h
        if zf > top:
            continue
        k = math.cos(dt / width * math.pi / 2) * (1 - zf / top) ** 0.5
        d = Vector((v.co.x - cx, v.co.y - cy)).normalized()
        v.co.x -= d.x * depth * k
        v.co.y -= d.y * depth * k


# Bold drum for the hero boulder: few points, so 15-25 big planar faces, near-vertical sides and a
# flat quiet top (verifier: the 53-point barrel read as a lumpy melted dome).
# crisp 8-sided drum, steep flanks, a low faceted crown rising to a blunt peak (a dead-flat plateau
# rendered darker than the sunward shoulders and read as a crater from above)
BOLD = [(0.0, 0.97, 8), (0.5, 1.0, 8), (0.8, 0.9, 7), (0.94, 0.62, 6), (1.0, 0.2, 3)]
BOLD_BLOCK = [(0.0, 1.0, 6), (0.5, 0.96, 6), (0.85, 0.72, 5), (1.0, 0.42, 3)]


def main_rock(a, s=1.0, seed=101):
    """Hero rock: a bold faceted drum with a soft crease down the front-left face."""
    return rock(a, (11.6 * s, 10.6 * s, 6.4 * s), seed=seed, rings=BOLD, rot=0.15, cuts=1, jitter=0.06, foot=False,
                shape=lambda vs: crease(vs, math.radians(-125), 0.7 * s))


def moss_cap(a, center, radius, seed, lobes=8, thick=0.45, layers=2, squash=(1.2, 0.85), angle=0.5):
    """Lime moss cap: a wide, flat, irregular lobed skirt draped over the crown and down past its
    edge, with a couple of lower lime mats laid off-centre on it (layered moss, not a rosette)."""
    v = K.drape(a, center, radius, MOSS, seed=seed, lobes=lobes, thick=thick, rings=2, crumple=0.05, scallop=0.2,
                squash=squash, angle=angle)
    # the mat is sunlit lime in the middle and fades to deeper moss at its draped edges (blend)
    cx, cy = center[0], center[1]
    K.blend(a, v, MOSS, MOSS_LIME, lambda c: -math.hypot(c.x - cx, c.y - cy), level=-radius * 0.3,
            width=radius * 0.35, steps=2)
    K.texture(a, v, amp=0.06, scale=0.6, seed=seed)
    rng = random.Random(seed)
    for k in range(layers):
        yaw = angle + math.pi * k + rng.uniform(-0.6, 0.6)
        r = radius * rng.uniform(0.25, 0.4)
        c = (center[0] + math.cos(yaw) * r, center[1] + math.sin(yaw) * r, center[2] + 20)
        v = K.drape(a, c, radius * rng.uniform(0.42, 0.52), MOSS_LIME, seed=seed + 7 + k, lobes=4, thick=thick * 0.55,
                    rings=2, lift=0.0, crumple=0.05, scallop=0.25, squash=(1.15, 0.8), angle=yaw)
        K.texture(a, v, amp=0.06, scale=0.6, seed=seed + k)


# Moss Cap as on the exploded view: three overlapping clumps, a wide one in the middle, a lower one
# to the left and one behind to the right; about 2:1 long, (x, y, radius, height, lobes, seed offset).
# Moss Cap as on the exploded view: one continuous THIN lobed mat about 2:1 long with sharp kinked lobes,
# its summit raised toward the left end. (x, y, z offset, radius, height, lobes, seed offset, squash x, y)
CAP_CLUMPS = ((0.0, 0.0, 0.0, 2.3, 0.45, 7, 0, 1.55, 0.85),)


def moss_cap_piece(a, loc=(0.0, 0.0, 0.0), s=1.0, rot=0.0, seed=111, clumps=CAP_CLUMPS):
    """The Moss Cap, modelled on its own (base at loc.z): a flat lobed slab with a darker green side
    band (the stem layer) and a faceted top that runs lime at one end to sun-yellow at the other.
    Returns all its verts (for conform())."""
    m = Vector(loc)
    out = []
    c, sn = math.cos(rot), math.sin(rot)
    along = Vector((c, sn, 0))
    for x, y, zo, r, h, lobes, k, sx, sy in clumps:
        p = m + Vector((x * c - y * sn, x * sn + y * c, 0)) * s
        tops, allv = K.moss_slab(a, (p.x, p.y, m.z + zo * s), r * s, h * s, MOSS_LIME, MOSS, seed=seed + 13 * k,
                                 lobes=lobes, band=0.12 * s, squash=(sx, sy), rot=rot, peak=(-0.3, 0.1), notch=0.34)
        # lime -> sun-yellow along the slab (a gradient over whole facets), with a little facet drift
        nf = K.noise_field(scale=0.7, seed=seed + k)
        K.blend(a, tops, MOSS_LIME, MOSS_SUN, lambda q: (q - m).dot(along) / (2.6 * s) + nf(q) * 0.25,
                level=0.1, width=1.1, steps=3)
        K.texture(a, allv, amp=0.05, scale=0.8, jitter=0.02, seed=seed + k)
        out += allv
    return out


# Leafy moss cap as on the master's hero and exploded view: 3-4 overlapping flat lobed mounds with an
# oak-leaf outline, lime with yellow sunlit crowns and a deeper green rim. (dx, dy, radius, height, lobes)
LEAFY_CAP = ((0.0, 0.0, 1.8, 0.75, 5), (-1.55, -0.4, 1.35, 0.62, 5), (1.5, 0.35, 1.35, 0.65, 5),
             (0.15, 1.3, 1.2, 0.58, 5), (-0.3, -1.35, 1.2, 0.55, 5))


def moss_mounds(a, loc=(0.0, 0.0, 0.0), s=1.0, rot=0.0, seed=111, mounds=LEAFY_CAP):
    """The Moss Cap modelled on its own (base at loc.z): chunky lobed moss mounds (leaf_cluster
    domes flattened to their height), lime with sun-yellow crowns fading to deeper moss at the rim.
    Returns all its verts (for conform())."""
    m = Vector(loc)
    c, sn = math.cos(rot), math.sin(rot)
    out = []
    for k, (dx, dy, r, h, lobes) in enumerate(mounds):
        p = m + Vector((dx * c - dy * sn, dx * sn + dy * c, 0)) * s
        vs = a.leaf_cluster(r * s, loc=(p.x, p.y, m.z), mat=MOSS_LIME, lobes=lobes, squash=h / r, facets=1,
                            depth=0.4, lobe_size=(0.65, 0.85), seed=seed + 7 * k, floor=m.z)
        z0, zt = m.z, m.z + h * s
        # rim deeper moss -> lime -> sun-yellow on the crowns (gradient over whole facets)
        K.blend(a, vs, MOSS, MOSS_LIME, lambda q, z0=z0, zt=zt: (q.z - z0) / (zt - z0), level=0.12, width=0.2,
                steps=1)
        K.blend(a, [v for v in vs if v.is_valid], MOSS_LIME, MOSS_SUN, lambda q, z0=z0, zt=zt: (q.z - z0) / (zt - z0),
                level=0.7, width=0.4, steps=2)
        K.texture(a, vs, amp=0.05, scale=0.9, jitter=0.02, seed=seed + k)
        out += vs
    return out


# Herb clump tiers for the plants round the rocks: (count, base height frac, length frac, pitch range).
# Broad round leaves rising from one root, outer ones lower and darker, inner ones upright and lime.
HERB_TIERS = ((7, 0.0, 0.66, (0.3, 0.55)), (6, 0.28, 0.62, (0.7, 1.0)), (4, 0.58, 0.52, (1.0, 1.3)))


def flower5(a, loc, r, seed, tilt=0.2):
    """Small white five-petal flower with a domed yellow centre (the white blooms in the clover)."""
    rng = random.Random(seed)
    y0 = rng.uniform(0, 6.28)
    for k in range(5):
        yaw = y0 + 2 * math.pi * k / 5
        K.leaf(a, loc, r, r * 0.95, PETAL, yaw=yaw, pitch=0.12 + tilt * math.cos(yaw - y0), fold=0.12, curl=0.15,
               thick=0.03, shape="round")
    a.cyl(r * 0.36, r * 0.2, r * 0.3, sides=6, loc=(loc[0], loc[1], loc[2] - 0.02), mat=POLLEN)


def stalk(a, p0, p1, r, mat):
    """Thin four-sided tapered stalk from p0 to p1 (a leaf petiole or flower stem)."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    rot = d.to_track_quat("Z", "Y").to_euler()
    return a.cyl(r, r * 0.6, d.length, sides=4, loc=tuple(p0), rot=tuple(rot), mat=mat)


def clover_head(a, top, size, yaw, tilt, mat, seed):
    """Three broad heart-round leaflets fanned from one point (a clover leaf), the fan tipped `tilt`
    radians outward toward yaw so its face shows from the side."""
    rng = random.Random(seed)
    out = []
    for j in range(3):
        ly = yaw + (j - 1) * 2.0 + rng.uniform(-0.15, 0.15)
        # leaflets pointing outward rise less than the one pointing back (the fan tips toward yaw)
        pitch = 0.12 + tilt * -math.cos(ly - yaw) * 0.9
        L = size * rng.uniform(0.9, 1.05)
        out += K.leaf(a, top, L, L * 0.95, mat, yaw=ly, pitch=pitch, fold=0.28, curl=0.1, thick=0.05 * size,
                      shape="heart", notch=0.0)
    return out


def herb(a, loc, size, seed, flowers=0, sprigs=8):
    """Clover clump as round the master's rocks: `sprigs` clover leaves (three round leaflets each) on
    short stems at stepped heights, the low outer ones mid green, the high inner ones lime, faces tipped
    outward; `flowers` small white blooms with yellow centres just above the leaves."""
    rng = random.Random(seed)
    x0, y0, z0 = loc
    out = []
    y_off = rng.uniform(0, 6.28)
    for k in range(sprigs):
        f = k / max(1, sprigs - 1)                  # 0 = low outer ... 1 = high inner
        yaw = y_off + k * 2.4 + rng.uniform(-0.2, 0.2)
        d = size * (0.42 - 0.32 * f) * rng.uniform(0.85, 1.1)
        h = size * (0.16 + 0.42 * f) * rng.uniform(0.9, 1.1)
        top = (x0 + math.cos(yaw) * d, y0 + math.sin(yaw) * d, z0 + h)
        stalk(a, (x0 + math.cos(yaw) * 0.05, y0 + math.sin(yaw) * 0.05, z0), top, size * 0.025,
              K.mix_key(LEAF, LEAF_YOUNG, 0.5))
        mat = K.mix_key(LEAF, LEAF_YOUNG, 0.5 if f < 0.35 else 1.0)
        out += clover_head(a, top, size * (0.42 - 0.08 * f), yaw, 0.35 * (1 - f) + 0.1, mat, seed + 7 * k)
    for i in range(flowers):
        t = rng.uniform(0, 6.28)
        r = size * rng.uniform(0.12, 0.28)
        top = (x0 + math.cos(t) * r, y0 + math.sin(t) * r, z0 + size * rng.uniform(0.72, 0.82))
        stalk(a, (x0, y0, z0), top, size * 0.02, LEAF_YOUNG)
        flower5(a, top, size * 0.22, seed + 17 * i)
    return out


def herb_bush(a, loc, size, seed, flowers=0, bright=False):
    """Clover clump as the master draws it round the rocks at gameplay scale: a small bushy mound of
    chunky round-lobed leaf clusters (broad facets), a wide mid-green base clump and 2-3 higher lime
    clumps stepping up, with `flowers` white blooms with yellow centres on top. bright: young-leaf to
    lime-moss greens (the sunnier clumps of the Rock Spire row) instead of leaf to young-leaf."""
    rng = random.Random(seed)
    x0, y0, z0 = loc
    out = []
    t0 = rng.uniform(0, 6.28)
    specs = [(0.0, 0.0, 0.0, 0.52, 0.62, 0.35),                      # (dx, dy, z, radius, squash, lime) x size
             (math.cos(t0) * 0.22, math.sin(t0) * 0.22, 0.28, 0.4, 0.7, 0.75),
             (math.cos(t0 + 2.3) * 0.25, math.sin(t0 + 2.3) * 0.25, 0.22, 0.36, 0.7, 0.6),
             (math.cos(t0 + 4.4) * 0.12, math.sin(t0 + 4.4) * 0.12, 0.5, 0.3, 0.75, 1.0)]
    for k, (dx, dy, dz, r, sq, lime) in enumerate(specs):
        mat = K.mix_key(LEAF_YOUNG, MOSS_LIME, lime) if bright else K.mix_key(LEAF, LEAF_YOUNG, lime)
        v = a.leaf_cluster(r * size * rng.uniform(0.9, 1.1), loc=(x0 + dx * size, y0 + dy * size, z0 + dz * size),
                           mat=mat, lobes=rng.choice((6, 7)), squash=sq, facets=1, depth=0.8, lobe_size=(0.5, 0.7),
                           seed=seed + 13 * k, floor=z0)
        K.texture(a, v, amp=0.05, scale=1.0, jitter=0.02, seed=seed + k)
        out += v
    for i in range(flowers):
        t = rng.uniform(0, 6.28)
        r = size * rng.uniform(0.1, 0.3)
        flower5(a, (x0 + math.cos(t) * r, y0 + math.sin(t) * r, z0 + size * 0.68), size * 0.2, seed + 17 * i)
    return out


def dress_herbs(a, rx, ry, clumps, pebbles, seed, cx=0.0, cy=0.0, bright=False):
    """Herb clumps [(angle, size, flowers)] and pebbles [(angle, size, dist)] round an ellipse
    (angle 0 = +X, -pi/2 = the front), as at the foot of the master's rocks."""
    for i, (t, s, fl) in enumerate(clumps):
        herb_bush(a, (cx + math.cos(t) * rx, cy + math.sin(t) * ry, 0), s, seed + i, flowers=fl, bright=bright)
    for i, (t, s, dist) in enumerate(pebbles):
        v = K.pebble(a, (s, s * 0.85, s * 0.62), (cx + math.cos(t) * rx * dist, cy + math.sin(t) * ry * dist, 0),
                     seed + 50 + i, (ROCK, ROCK_COOL, ROCK_BASE)[i % 3])
        K.texture(a, v, amp=0.08, scale=0.5, seed=seed + i)


def boulder_hero2(a):
    vs = main_rock(a)
    K.tag_part(a, vs, "rock")
    stain(a, vs, -2.2, spread=0.6, height=2.6, seed=113)
    place_mounds(a, (-0.3, 0.4), 1.0, 0.5, 111, on=K.part(a, "rock"))
    dress_herbs(a, 5.9, 5.3, ((-2.85, 3.0, 1), (-2.3, 2.5, 0), (-1.35, 2.3, 1), (-0.3, 2.1, 1), (0.15, 3.0, 0),
                              (0.9, 2.5, 0), (2.5, 2.5, 0)),
                ((-2.05, 2.1, 1.08), (-0.95, 1.9, 1.1), (-0.5, 1.2, 1.2), (0.55, 1.7, 1.1), (1.6, 1.5, 1.08),
                 (-2.6, 1.3, 1.12), (2.4, 1.2, 1.1), (1.2, 1.0, 1.15), (-1.7, 0.9, 1.22)), 140)


def boulder_hero(a):
    vs = main_rock(a)
    # damp green staining low on the front-left and right faces, fading up into the stone
    stain(a, vs, -2.0, seed=113)
    stain(a, vs, -0.2, spread=0.5, height=2.4, seed=114)
    place_cap(a, (-1.5, -0.4), 1.15, 0.6, 111)
    # clover mounds bunch at the left, front-left and right, as on the sheet; pebbles in the gaps
    dress(a, 6.1, 5.2, ((-2.75, 2.2, 2), (-2.35, 1.6, 1), (3.05, 2.0, 1), (-0.15, 1.8, 1), (0.4, 2.1, 2),
                        (1.5, 1.6, 0), (2.4, 1.7, 0)),
          ((-2.95, 1.5), (-1.3, 1.3), (-0.55, 1.1), (0.95, 1.4), (2.0, 1.0), (3.6, 1.2)), 140)


def strip_to(a, keep):
    """Delete every face not in the keep materials (build a part on its host, then lift it off)."""
    import bmesh
    idx = {a.mats.index(m) for m in keep if m in a.mats}
    bm = a.bm
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index not in idx], context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")


SMALL_CAP = ((0.0, 0.0, 1.6, 1.3, 8), (-1.4, -0.4, 1.2, 1.0, 7), (1.25, 0.5, 1.1, 0.95, 7))
TUFT_CAP = ((0.0, 0.0, 1.4, 1.2, 8), (1.0, 0.6, 1.0, 0.9, 7))
SIDE_TUFT = ((0.0, 0.0, 0.9, 0.7, 7),)
# Upright slab: angular, with a step in the outline part-way up and a leaning, kinked top.
UPRIGHT = [(0.0, 1.0, 8), (0.3, 0.92, 8), (0.6, 0.76, 7), (0.85, 0.52, 6), (1.0, 0.26, 4)]   # tapering, blunt point
# Slanted-top slab for the tall half of the split boulder.
SPLIT_TALL = [(0.0, 1.0, 7), (0.4, 0.86, 7), (0.72, 0.62, 6), (0.92, 0.36, 4), (1.0, 0.18, 2)]   # tapers to a small crown


def boulder_flat(a):
    vs = rock(a, (12.6, 9.2, 4.0), seed=171, rings=BOLD, rot=0.2, foot=False)
    K.tag_part(a, vs, "rock")
    stain(a, vs, -1.6, spread=0.55, height=1.8, seed=174)
    place_mounds(a, (0.3, 0.8), 1.0, 0.2, 173, mounds=SMALL_CAP, on=K.part(a, "rock"))
    dress_herbs(a, 6.6, 4.9, ((-2.85, 2.8, 1), (-2.3, 2.2, 0), (-1.6, 2.1, 0), (-0.4, 2.2, 0), (0.3, 2.2, 1),
                              (2.6, 2.2, 0), (3.1, 2.8, 0)),
                ((-1.4, 1.5, 1.12), (1.0, 1.4, 1.12), (-2.5, 1.1, 1.15), (2.2, 1.2, 1.15)), 180)


def boulder_upright(a):
    vs = rock(a, (7.6, 6.8, 13.0), seed=201, rings=UPRIGHT, rot=0.3, lean=(0.1, 0.05), jitter=0.05, foot=False,
              shape=lambda v: crease(v, math.radians(-60), 0.5, top=0.7))
    K.tag_part(a, vs, "rock")
    stain(a, vs, -2.3, spread=0.5, height=3.0, seed=205)      # damp moss low on the front-left
    place_mounds(a, (0.7, 0.3), 0.9, 0.4, 203, mounds=TUFT_CAP, on=K.part(a, "rock"))
    dress_herbs(a, 4.7, 4.1, ((-2.5, 3.2, 1), (-1.85, 2.8, 0), (-0.9, 2.8, 0), (0.1, 3.0, 1), (2.4, 2.8, 0),
                              (3.0, 3.2, 0), (1.2, 2.2, 0)),
                ((-1.3, 1.2, 1.15), (0.7, 1.0, 1.2), (-0.4, 0.8, 1.25)), 210)


def boulder_split(a):
    vs = rock(a, (6.6, 6.0, 9.4), loc=(-2.8, 0.2, 0), seed=231, rings=SPLIT_TALL, rot=0.2, lean=(0.18, 0.05), jitter=0.05,
              foot=False)
    K.tag_part(a, vs, "left")
    stain(a, vs, -2.2, spread=0.45, height=2.6, seed=235, cx=-2.8, cy=0.2)
    vs = rock(a, (6.0, 5.4, 5.8), loc=(3.1, -0.3, 0), seed=232, rings=BOLD_BLOCK, rot=-0.3, jitter=0.05, foot=False)
    K.tag_part(a, vs, "right")
    stain(a, vs, -0.6, spread=0.45, height=1.8, seed=236, cx=2.8, cy=-0.3)
    place_mounds(a, (-2.4, 0.4), 0.85, 0.3, 233, mounds=TUFT_CAP, on=K.part(a, "left"))
    place_mounds(a, (3.1, -0.1), 1.0, -0.4, 234, mounds=TUFT_CAP, on=K.part(a, "right"))
    dress_herbs(a, 5.6, 3.9, ((-2.6, 3.1, 1), (-1.9, 2.5, 0), (-0.3, 2.8, 0), (0.4, 2.5, 1), (2.8, 2.8, 0),
                              (1.6, 2.2, 0)),
                ((-1.6, 1.2, 1.15), (1.5, 1.1, 1.15), (-0.9, 0.9, 1.2)), 240)


def boulder_moss_part(a):
    """The moss cap alone, as modelled (the hero places this same piece on its crown)."""
    moss_mounds(a, (0.0, 0.0, 0.0), 1.0, 0.5, 111)


def boulder_main_part(a):
    vs = main_rock(a)
    stain(a, vs, -2.2, spread=0.6, height=2.6, seed=113)


BOULDER_NOTES = {
    "Boulder": "squat barrel-dome boulder with many large facets; leafy moss cap of 4 overlapping lobed mounds "
               "(lime, sun-yellow crowns, deeper moss rim); faint damp moss stain low on the front-left face; "
               "round-leaf herb clumps with white five-petal flowers and pebbles round the foot",
    "BoulderMainRock": "main rock alone (faint moss stain low on the front-left face); drop a BoulderMossCap on its crown",
    "BoulderMossCap": "moss cap: 4 overlapping lobed moss mounds; drop onto any rock top",
    "BoulderFlat": "Flat Boulder: wide and low, a 3-mound moss cap on the crown, herbs and pebbles",
    "BoulderUpright": "Upright Boulder: tall tapering cone with a moss tuft on top and a moss streak down its right "
                      "face, a small boulder at its foot, herbs with white flowers",
    "BoulderSplit": "Split Boulder: a tall rock and a squat rock with a crack between, a moss tuft on each, herbs",
}


def boulder_row(render=True):
    palette()
    # 5000: the clover dressing round the foot is most of the count (the rock itself is ~280 tris)
    specs = [("Boulder", "hero", boulder_hero2, 5000, "hull"),
             ("BoulderMainRock", "part", boulder_main_part, 1500, "hull"),
             ("BoulderMossCap", "part", boulder_moss_part, 1500, "none"),
             ("BoulderFlat", "variant", boulder_flat, 5000, "hull"),
             ("BoulderUpright", "variant", boulder_upright, 5000, "hull"),
             ("BoulderSplit", "variant", boulder_split, 5000, "hull")]
    objs = [K.mk(SHEET, n, fn, subject="Boulder", role=r, notes=BOULDER_NOTES[n], budget=b, collision=c)
            for n, r, fn, b, c in specs]
    # exploded cell: the moss cap floats above the main rock, as on the master
    rk, cap = objs[1], objs[2]
    cap.location = (rk.location.x - 0.8, rk.location.y + 0.4, rk.location.z + 9.0)
    for o in objs:
        if any(m.name == "FB_" + MOSS_LIME for m in o.data.materials):
            o["kit_shading_ok"] = ("moss clumps: the darker side band is the stem layer under the lime top "
                                   "(a material region, as on the master's exploded Moss Cap)")
    out = {"stats": K.stats(objs), "problems": K.check(objs)}
    if render:
        out["compare"] = K.render_row(SHEET, "boulder", 1, "Boulder", objs, vfx=True, SIDE_AZIMUTH=-90, HERO_ELEVATION=24)
    return out


# ---------------------------------------------------------------- Row 2: Rock Spire
# Tall obelisk: a few broad side facets and a chisel tip (two top points make a short ridge).
SPIRE = [(0.0, 1.0, 7), (0.3, 0.82, 7), (0.6, 0.6, 6), (0.86, 0.36, 5), (1.0, 0.12, 2)]   # tapers to an angled peak
# Shorter leaning pillar with a sloped, blunt top.
PILLAR_BLUNT = [(0.0, 1.0, 5), (0.45, 0.9, 5), (0.82, 0.66, 5), (1.0, 0.36, 3)]   # few points: sharp, angular


def spire_main(a, loc=(0, 0, 0), s=1.0, seed=301, h=11.6, w=7.0, lean=(0.06, 0.04), tilt=(0.0, 0.0)):
    """The Rock Spire main mesh, on its own: tall faceted obelisk with a chisel tip."""
    vs = K.hull_rock(a, (w * s, w * 0.82 * s, h * s), loc=loc, seed=seed, mat=ROCK, rings=SPIRE, jitter=0.05,
                     rot=0.4, lean=lean, tilt=tilt)
    return colour_rock(a, vs, (w * s, w * s, h * s), loc, seed)


def colour_rock(a, vs, size, loc, seed, cuts=1):
    """Same stone treatment as rock(): warm/cool facet drift, texture, coplanar split (cuts=0 skips
    it for small rocks), damp foot."""
    z0 = loc[2]
    K.blend(a, vs, ROCK, ROCK_COOL, K.noise_field(scale=0.18, seed=seed), level=0.05, width=0.5, steps=3)
    K.texture(a, vs, amp=0.05, scale=0.28, jitter=0.05, seed=seed)       # crisp tone step per facet
    if cuts:
        vs = K.refine(a, vs, cuts)
    if size[2] < 1.5:                 # pebbles: too few faces for a damp band (it would track facing)
        return vs
    band = min(1.4, size[2] * 0.12)
    K.blend(a, vs, ROCK, ROCK_BASE, lambda c: -(c.z - z0), level=-band * 0.6, width=band, steps=2, jitter=0.15,
            seed=seed)
    return vs


# Angular wedge chunk: broad foot, faces leaning in to a short ridge (a broken-off slab).
WEDGE = [(0.0, 1.0, 6), (0.4, 0.92, 6), (0.75, 0.64, 5), (1.0, 0.22, 3)]
# Chunky block for the big front boulder: few points, so broad bold facets and a flat-ish top.
BLOCK = [(0.0, 1.0, 6), (0.45, 0.97, 6), (0.8, 0.74, 5), (1.0, 0.42, 4)]
# Foot collar chunks round the spire (angle, distance, w, d, h, lean in, seed offset): a tight broken
# ring, tall pointed chunks at the sides, a big squat block in front, open at the back.
COLLAR = ((-1.7, 2.7, 4.4, 3.6, 3.2, 0.0, 0), (-2.5, 2.9, 3.0, 2.6, 3.4, 0.2, 1), (3.0, 2.9, 2.8, 2.6, 2.8, 0.2, 2),
          (-0.85, 2.9, 3.2, 2.8, 2.6, 0.1, 3), (-0.1, 3.0, 2.6, 2.4, 2.2, 0.15, 4), (2.3, 2.8, 2.4, 2.2, 3.0, 0.25, 5),
          (0.75, 3.0, 2.2, 2.0, 1.6, 0.1, 6))


def foot_collar(a, loc=(0, 0, 0), s=1.0, seed=320, rocks=COLLAR):
    """The Foot Collar, on its own: a tight broken ring of angular wedge chunks (set any spire inside)."""
    out = []
    for t, d, w, dp, h, lean, k in rocks:
        p = (loc[0] + math.cos(t) * d * s, loc[1] + math.sin(t) * d * s, loc[2])
        rings = BLOCK if h < 2.0 or k == 0 else WEDGE
        vs = K.hull_rock(a, (w * s, dp * s, h * s), loc=p, seed=seed + k, mat=ROCK, rings=rings, jitter=0.08,
                         rot=t + 0.4, lean=(-math.cos(t) * lean, -math.sin(t) * lean))
        out += colour_rock(a, vs, (w * s, dp * s, h * s), p, seed + k, cuts=0)
    return out


def side_pillars(a, s=1.0, seed=340):
    """The shorter pillars leaning on the spire: one on the left, a lower one behind on the right."""
    l = K.hull_rock(a, (4.6 * s, 4.0 * s, 7.4 * s), loc=(-3.4 * s, -0.6 * s, 0), seed=seed, mat=ROCK,
                    rings=PILLAR_BLUNT, jitter=0.06, rot=0.2, lean=(0.12, 0.0))
    K.tag_part(a, colour_rock(a, l, (4.6 * s, 4.0 * s, 7.4 * s), (0, 0, 0), seed), "pillar_l")
    r = K.hull_rock(a, (4.0 * s, 3.6 * s, 7.2 * s), loc=(3.3 * s, 0.2 * s, 0), seed=seed + 1, mat=ROCK,
                    rings=PILLAR_BLUNT, jitter=0.06, rot=-0.3, lean=(-0.1, 0.0))
    K.tag_part(a, colour_rock(a, r, (4.0 * s, 3.6 * s, 7.2 * s), (0, 0, 0), seed + 1), "pillar_r")
    return "pillar_l", "pillar_r"


# Rounded, chunky shoulder rocks stepping down from the spire (not slab pillars).
SHOULDER = [(0.0, 1.0, 7), (0.45, 0.94, 7), (0.78, 0.72, 6), (1.0, 0.4, 4)]

# Hero foot rocks round the spire, as on the master (angle, distance, w, d, h, rings, seed offset): a big
# flat-topped boulder in front, a medium one front-left, angular chunks at the sides, small ones at the back.
SPIRE_FOOT = ((-1.2, 4.0, 6.0, 5.0, 5.0, "block", 0), (-2.3, 4.2, 4.2, 3.6, 3.4, "block", 1),
              (2.95, 4.0, 3.2, 3.0, 2.6, "wedge", 2), (-0.2, 4.6, 3.4, 3.0, 2.6, "block", 3),
              (-0.6, 6.0, 1.9, 1.7, 1.4, "block", 4), (2.1, 3.7, 2.8, 2.4, 2.0, "wedge", 5),
              (1.05, 3.8, 2.8, 2.4, 1.9, "block", 6), (1.6, 3.6, 2.4, 2.2, 1.7, "wedge", 7))


def foot_rocks(a, loc=(0, 0, 0), s=1.0, seed=320, rocks=SPIRE_FOOT):
    """The Foot Collar: a broken ring of angular, flat-topped stone chunks round a spire's foot."""
    out = []
    for t, d, w, dp, h, kind, k in rocks:
        p = (loc[0] + math.cos(t) * d * s, loc[1] + math.sin(t) * d * s, loc[2])
        rings = BOLD_BLOCK if kind == "block" else WEDGE
        vs = K.hull_rock(a, (w * s, dp * s, h * s), loc=p, seed=seed + k, mat=ROCK, rings=rings, jitter=0.06,
                         rot=t + 0.4, lean=(-math.cos(t) * 0.08, -math.sin(t) * 0.08))
        out += colour_rock(a, vs, (w * s, dp * s, h * s), p, seed + k, cuts=0)
    return out


def spire_pillars(a, s=1.0, seed=340, hl=6.2, hr=4.8, which="lr"):
    """The two shorter pillars beside the spire: a tall one on the left, a lower one on the right, both
    with sloped flat tops (ledges for moss and clover)."""
    if "l" in which:
        l = K.hull_rock(a, (5.0 * s, 4.4 * s, hl * s), loc=(-3.7 * s, -1.4 * s, 0), seed=seed, mat=ROCK,
                        rings=SHOULDER, jitter=0.05, rot=0.2, lean=(0.1, 0.0))
        K.tag_part(a, colour_rock(a, l, (4.6 * s, 4.0 * s, hl * s), (0, 0, 0), seed), "pillar_l")
    if "r" in which:
        r = K.hull_rock(a, (4.6 * s, 4.0 * s, hr * s), loc=(3.6 * s, -0.8 * s, 0), seed=seed + 1, mat=ROCK,
                        rings=SHOULDER, jitter=0.05, rot=-0.3, lean=(-0.08, 0.0))
        K.tag_part(a, colour_rock(a, r, (4.0 * s, 3.6 * s, hr * s), (0, 0, 0), seed + 1), "pillar_r")


FLAT_TUFT = ((0.0, 0.0, 1.5, 0.55, 6), (1.1, 0.5, 1.1, 0.45, 5))      # low flat moss patch for ledges


def ledge_dressing(a, spots, seed):
    """Clover clumps and flat moss patches sitting on ledges: [(part, (x, y), size, kind, flowers)]."""
    for i, (part, xy, sz, kind, fl) in enumerate(spots):
        on = K.part(a, part)
        if kind == "moss":
            place_mounds(a, xy, sz, 0.3 * i, seed + 10 * i, mounds=FLAT_TUFT, on=on)
        else:
            z = K.top_at(a, xy, on=on)
            herb_bush(a, (xy[0], xy[1], z - 0.15), sz, seed + 10 * i, flowers=fl, bright=True)


def spire_flank_moss(a, sp, angle, z0, z1, seed):
    """A small flat lime moss patch on the spire's flank (moss growing on the face, as on the master)."""
    streak(a, sp, angle, z0, z1, spread=0.42, seed=seed, key=MOSS_LIME)


# The Foot Collar: a low ring of angular rocks round an empty centre where the spire stands
# (angle, distance, w, d, h, rings, seed offset).
# One fused jagged rim of big flat-topped angular blocks, tallest at the back, a notch at the front-right.
COLLAR_RING = ((1.57, 3.5, 4.6, 3.2, 4.4, "block", 0), (0.7, 3.6, 4.4, 3.2, 3.9, "block", 1),
               (2.45, 3.6, 4.4, 3.2, 3.7, "block", 2), (-0.2, 3.8, 4.2, 3.2, 3.0, "block", 3),
               (3.3, 3.8, 4.2, 3.2, 2.9, "block", 4), (-2.35, 3.9, 4.2, 3.2, 2.3, "block", 5))
# Stepped slabs leaning on the spire: (x, y, w, d, h, lean x, seed offset).
SLABS_LEFT = ((-3.4, -0.9, 4.2, 3.6, 6.4, 0.14, 0),)
SLABS_RIGHT = ((3.2, -0.2, 3.8, 3.2, 5.4, -0.12, 1), (4.6, -1.6, 3.0, 2.8, 3.4, -0.1, 2),
               (1.0, 3.0, 3.8, 3.2, 6.0, -0.02, 3))


def collar(a, s=1.0, seed=320, rocks=COLLAR_RING):
    return foot_rocks(a, s=s, seed=seed, rocks=rocks)


def slabs(a, specs, s=1.0, seed=340, name="slab"):
    """Angular stepped slabs with sloped flat tops leaning on the spire (tagged name0, name1, ...)."""
    for x, y, w, d, h, lx, k in specs:
        v = K.hull_rock(a, (w * s, d * s, h * s), loc=(x * s, y * s, 0), seed=seed + k, mat=ROCK, rings=PILLAR_BLUNT,
                        jitter=0.05, rot=0.25 * (k + 1), lean=(lx, 0.0))
        K.tag_part(a, colour_rock(a, v, (w * s, d * s, h * s), (0, 0, 0), seed + k), f"{name}{k}")


def front_boulder(a, s=1.0, seed=330, loc=(1.8, -4.9), size=(5.0, 4.4, 3.7), name="front"):
    """The big chunky boulder at the front of the foot."""
    w, d, h = size
    p = (loc[0] * s, loc[1] * s, 0)
    v = K.hull_rock(a, (w * s, d * s, h * s), loc=p, seed=seed, mat=ROCK, rings=BOLD, jitter=0.06, rot=0.5)
    K.tag_part(a, colour_rock(a, v, (w * s, d * s, h * s), p, seed), name)


def spire_hero(a):
    sp = spire_main(a, h=12.4, w=7.4)
    K.tag_part(a, sp, "spire")
    stain(a, sp, -2.4, spread=0.5, height=3.2, seed=364)
    spire_flank_moss(a, sp, -0.6, 6.4, 8.2, 365)
    slabs(a, SLABS_LEFT, seed=340, name="l")
    slabs(a, SLABS_RIGHT, seed=350, name="r")
    K.tag_part(a, collar(a), "collar")
    front_boulder(a)
    front_boulder(a, seed=331, loc=(-2.8, -4.3), size=(4.2, 3.8, 3.0), name="front_l")
    front_boulder(a, seed=332, loc=(-6.0, -1.6), size=(3.4, 3.0, 2.2), name="side_l")      # the foot steps
    front_boulder(a, seed=333, loc=(6.2, -2.4), size=(3.2, 2.8, 2.0), name="side_r")       # down outward
    ledge_dressing(a, (("l0", (-3.4, -1.0), 0.7, "moss", 0), ("l0", (-4.1, -2.0), 1.8, "herb", 0),
                       ("r1", (2.9, -0.4), 1.7, "herb", 0), ("r2", (4.6, -1.7), 1.5, "herb", 0),
                       ("front", (2.0, -4.6), 0.75, "moss", 0), ("front_l", (-2.8, -4.3), 0.6, "moss", 0),
                       ("collar", (-0.4, -3.6), 1.5, "herb", 0), ("r3", (1.6, 2.4), 1.5, "herb", 0)), 361)
    dress_herbs(a, 6.8, 6.0, ((-2.65, 2.3, 0), (-1.6, 2.0, 0), (-0.25, 2.0, 0), (2.6, 2.0, 0)),
                ((-1.9, 1.2, 1.12), (-0.4, 1.1, 1.12), (0.35, 1.0, 1.18), (2.9, 1.0, 1.1), (-2.8, 0.9, 1.1)), 370,
                bright=True)


def spire_part_main(a):
    sp = spire_main(a, h=12.4, w=7.4)
    stain(a, sp, -2.4, spread=0.5, height=3.2, seed=364)
    spire_flank_moss(a, sp, -0.6, 6.4, 8.2, 365)


def spire_collar_part(a):
    """The Foot Collar alone: a low ring of angular rocks round the empty centre, a moss patch on one."""
    K.tag_part(a, collar(a), "collar")
    for i, t in enumerate((-2.35, -0.2, 3.3)):
        place_mounds(a, (math.cos(t) * 3.8, math.sin(t) * 3.8), 0.6, 0.4 + t, 321 + i, mounds=FLAT_TUFT,
                     on=K.part(a, "collar"))


def spire_short(a):
    """Short Spire (stubby): a squat wide spire, a low slab, small foot rocks and clover."""
    sp = spire_main(a, h=7.6, w=6.0, seed=381)
    K.tag_part(a, sp, "spire")
    spire_flank_moss(a, sp, -0.6, 3.4, 5.4, 382)
    slabs(a, ((-2.9, -0.8, 3.4, 3.0, 4.2, 0.12, 0),), seed=383, name="l")
    K.tag_part(a, collar(a, s=0.8, seed=384), "collar")
    ledge_dressing(a, (("l0", (-3.1, -1.4), 1.5, "herb", 0), ("collar", (2.2, -2.0), 0.55, "moss", 0)), 385)
    dress_herbs(a, 5.2, 4.5, ((-2.5, 2.0, 0), (-1.4, 1.9, 0), (-0.3, 1.9, 0), (0.7, 1.8, 0), (2.7, 1.8, 0)),
                ((-1.2, 0.9, 1.15), (1.8, 0.8, 1.15)), 386, bright=True)


def spire_tall(a):
    """Tall Spire (high, narrow): a much taller spire, stepped slabs both sides, foot rocks."""
    sp = spire_main(a, h=16.0, w=7.0, seed=391)
    K.tag_part(a, sp, "spire")
    spire_flank_moss(a, sp, -1.4, 8.0, 11.0, 392)
    slabs(a, ((-3.3, -1.0, 4.0, 3.4, 8.0, 0.12, 0),), seed=393, name="l")
    slabs(a, ((3.1, -0.3, 3.6, 3.0, 6.4, -0.1, 1), (4.4, -1.6, 2.8, 2.6, 3.4, -0.1, 2)), seed=397, name="r")
    K.tag_part(a, collar(a, s=0.9, seed=394), "collar")
    ledge_dressing(a, (("l0", (-3.8, -1.6), 1.8, "herb", 0), ("r1", (2.9, -0.4), 1.6, "herb", 0),
                       ("l0", (-3.2, -0.9), 0.65, "moss", 0)), 395)
    dress_herbs(a, 5.6, 4.9, ((-2.5, 2.0, 0), (-1.3, 1.8, 0), (-0.2, 1.9, 0), (0.8, 1.8, 0), (2.6, 1.8, 0)),
                ((-1.1, 0.9, 1.15), (1.9, 0.8, 1.15)), 396, bright=True)


# Leaning spire: a tilted slab with a blunt chisel crown.
LEAN_SLAB = [(0.0, 1.0, 7), (0.35, 0.84, 7), (0.7, 0.6, 6), (0.9, 0.38, 5), (1.0, 0.16, 2)]


def spire_leaning(a):
    """Leaning Spire (tilted): a slab spire leaning ~12 degrees to the left with a blunt chisel top, a
    stepped slab on its right, a low rocky skirt."""
    vs = K.hull_rock(a, (6.4, 5.2, 11.6), seed=401, mat=ROCK, rings=LEAN_SLAB, jitter=0.05, rot=0.4,
                     lean=(-1.0, 0.05))
    sp = colour_rock(a, vs, (6.4, 6.4, 11.6), (0, 0, 0), 401)
    K.tag_part(a, sp, "spire")
    spire_flank_moss(a, sp, -0.5, 4.6, 7.0, 402)
    slabs(a, ((3.0, -0.4, 3.4, 3.0, 5.0, -0.1, 0),), s=0.9, seed=406, name="r")
    K.tag_part(a, collar(a, s=0.8, seed=403), "collar")
    ledge_dressing(a, (("r0", (2.7, -0.6), 1.6, "herb", 0), ("collar", (-2.4, -2.6), 1.5, "herb", 0)), 404)
    dress_herbs(a, 5.2, 4.5, ((-2.5, 2.0, 0), (-1.4, 1.9, 0), (-0.2, 1.9, 0), (0.6, 1.8, 0), (2.5, 2.0, 0)),
                ((-1.2, 0.9, 1.15), (1.8, 0.8, 1.15)), 405, bright=True)


SPIRE_NOTES = {
    "RockSpire": "tall faceted obelisk tapering to an angled peak, a lime moss patch on its front-right flank; an "
                 "angular slab at ~50% of its height on the left and stepped slabs on the right; a low ring of foot "
                 "rocks (the Foot Collar) and a big boulder in front; flat moss patches and lime clover clumps on the "
                 "ledges and round the base",
    "RockSpireMain": "spire main mesh alone (chunky obelisk, moss patch on the flank, damp stain low on the front-left)",
    "RockSpireFootCollar": "foot collar alone: low ring of angular rocks round an empty centre, a moss patch; set any "
                           "spire inside",
    "RockSpireShort": "Short Spire: stubby wide spire, a low slab, small foot rocks, clover",
    "RockSpireTall": "Tall Spire: high spire with stepped slabs both sides, moss on its flank, foot rocks, clover",
    "RockSpireLeaning": "Leaning Spire: slab spire tilted ~12 degrees to the left with a blunt chisel top, a slab on "
                        "its right, a low rocky skirt, clover",
}


def spire_row(render=True):
    palette()
    # 6000: a landmark rock (WorldModeling 16: 1500-5000 initially) whose dressing is most of the count
    specs = [("RockSpire", "hero", spire_hero, 6000, "hull"),
             ("RockSpireMain", "part", spire_part_main, 1500, "hull"),
             ("RockSpireFootCollar", "part", spire_collar_part, 1500, "hull"),
             ("RockSpireShort", "variant", spire_short, 5000, "hull"),
             ("RockSpireTall", "variant", spire_tall, 5000, "hull"),
             ("RockSpireLeaning", "variant", spire_leaning, 5000, "hull")]
    objs = [K.mk(SHEET, n, fn, subject="RockSpire", role=r, notes=SPIRE_NOTES[n], budget=b, collision=c)
            for n, r, fn, b, c in specs]
    # exploded cell: the spire floats above its foot collar, as on the master
    sp, col = objs[1], objs[2]
    sp.location = (col.location.x, col.location.y, col.location.z + 6.4)
    out = {"stats": K.stats(objs), "problems": K.check(objs)}
    if render:
        out["compare"] = K.render_row(SHEET, "rock_spire", 2, "RockSpire", objs, vfx=True, SIDE_AZIMUTH=-90,
                                      HERO_ELEVATION=22)
    return out


# ---------------------------------------------------------------- Row 3: Rock Cluster
# Upright egg for Rock A: wide shoulders high up, tapering to a narrow crown.
EGG = [(0.0, 0.92, 10), (0.3, 1.0, 10), (0.6, 0.94, 9), (0.8, 0.78, 8), (0.93, 0.52, 6), (1.0, 0.2, 3)]
# Gabled tall rock (Rock A): broad flat sides rising to a short ridge; few points, big facets.
GABLE = [(0.0, 1.0, 7), (0.4, 0.95, 7), (0.7, 0.8, 6), (0.88, 0.52, 5), (1.0, 0.14, 2)]
# Bulky low-facet boulder for Rock C and a coarse dome for Rock B.
BULK = [(0.0, 0.96, 8), (0.35, 1.0, 8), (0.65, 0.92, 7), (0.85, 0.7, 6), (1.0, 0.36, 4)]
# Squat dome for Rock B.
DOME_LOW = [(0.0, 0.97, 8), (0.3, 1.0, 8), (0.62, 0.86, 7), (0.85, 0.6, 6), (1.0, 0.28, 4)]


def cluster_rock(a, which, loc=(0, 0, 0), s=1.0, rot=0.0, seed=0, cap=True):
    """Rock A (tall upright egg), B (squat dome) or C (barrel), each a finished part with its own
    thin moss tuft and moss creeping up one face, as on the exploded view. Tagged as part `which`."""
    spec = {"A": ((7.0, 6.2, 10.4), GABLE, (0.04, 0.06), -2.6, 0.55),
            "B": ((7.2, 6.4, 4.8), DOME_LOW, (0.0, 0.0), -0.4, 0.5),
            "C": ((9.4, 8.0, 6.2), BULK, (-0.03, 0.02), -2.4, 0.6)}[which]
    size, rings, lean, side, cap_s = spec
    size = tuple(x * s for x in size)
    sd = seed or {"A": 411, "B": 421, "C": 431}[which]
    vs = rock(a, size, loc=loc, seed=sd, rings=rings, rot=rot, lean=lean)
    name = f"rock_{which}_{sd}"
    K.tag_part(a, vs, name)
    # leafy moss patches clinging up one face (thin mats laid on the face)
    for k, (dz, ds) in enumerate(((0.22, 0.42), (0.48, 0.32))):
        side_moss(a, K.part(a, name), side + rot + k * 0.25, size[2] * dz, ds * s, rot=1.3 + k, seed=sd + 5 + k,
                  cx=loc[0], cy=loc[1])
    if cap:
        place_cap(a, (loc[0] - 0.2 * s, loc[1] + 0.1 * s), cap_s * s, rot + 0.5, sd + 2, on=K.part(a, name))
    return name


CLUSTER_NOTES = {
    "RockCluster": "three interlocking independent boulders: tall upright Rock A behind, barrel Rock C front-left, "
                   "squat Rock B front-right; thin moss tufts on their crowns and moss creeping up their faces; "
                   "clover with daisies in the gaps; pebbles at the front",
    "RockClusterA": "Rock A alone: tall upright egg boulder with a moss tuft and moss up its left face",
    "RockClusterB": "Rock B alone: squat dome boulder with a moss tuft",
    "RockClusterC": "Rock C alone: barrel boulder with a moss tuft and moss up its left face",
    "RockClusterLinear": "Linear Cluster: two boulders in a row (low left, tall right) with clover and pebbles",
    "RockClusterCrescent": "Crescent Cluster: three boulders on a curve, clover and pebbles",
    "RockClusterTriangular": "Triangular Cluster: three boulders packed in a compact triangle, clover with a daisy",
}


def cluster_hero(a):
    cluster_rock(a, "A", (1.4, 2.4, 0))
    cluster_rock(a, "C", (-3.8, -0.7, 0), rot=0.3)
    cluster_rock(a, "B", (3.2, -3.0, 0), rot=-0.2)
    # clover in the gaps between the rocks and round the foot; pebbles at the front
    for i, (x, y, sz, fl) in enumerate(((7.3, 0.6, 2.1, 2), (-8.0, -1.9, 1.9, 1), (0.0, -4.6, 1.7, 1), (-1.6, 3.0, 1.4, 0),
                                        (-4.8, -4.8, 1.4, 1), (7.0, -4.2, 1.4, 0), (5.0, 4.0, 1.3, 0))):
        K.clover(a, (x, y, 0), sz, 450 + i, LEAF, flowers=fl, petal=PETAL, pollen=POLLEN, young_mat=LEAF_YOUNG)
    for i, (x, y, sz) in enumerate(((-5.2, -3.4, 1.6), (-0.4, -5.6, 1.5), (6.3, -1.3, 1.4), (0.9, -4.9, 0.9))):
        v = K.pebble(a, (sz, sz * 0.85, sz * 0.6), (x, y, 0), 470 + i, ROCK_COOL if i % 2 else ROCK)
        K.texture(a, v, amp=0.08, scale=0.5, seed=470 + i)


def cluster_linear(a):
    """Linear: three boulders stepping up in a row, low B left, C middle, tall A right."""
    cluster_rock(a, "B", (-6.2, -0.3, 0), s=0.7, rot=0.4, seed=480)
    cluster_rock(a, "C", (-1.4, 0.0, 0), s=0.8, rot=0.2, seed=481)
    cluster_rock(a, "A", (4.0, 0.4, 0), s=0.85, rot=-0.3, seed=482)
    dress(a, 8.6, 3.6, ((-2.7, 1.4, 1), (-0.4, 1.3, 0), (0.15, 1.4, 1), (2.9, 1.2, 0), (-1.6, 1.2, 0)),
          ((-1.2, 1.0), (-0.9, 0.7), (-1.9, 0.8)), 483)


def cluster_crescent(a):
    """Crescent: three boulders on a clear arc opening to the front, tall A at the centre-back."""
    cluster_rock(a, "C", (-6.4, -1.4, 0), s=0.72, rot=0.9, seed=491)
    cluster_rock(a, "A", (0.0, 1.6, 0), s=0.85, rot=0.0, seed=492)
    cluster_rock(a, "B", (6.4, -1.4, 0), s=0.8, rot=-0.9, seed=493)
    dress(a, 6.0, 4.0, ((-2.8, 1.4, 0), (-1.6, 1.3, 1), (-0.4, 1.4, 0), (0.6, 1.2, 0)), ((-1.3, 0.9), (-1.8, 0.7)), 494)


def cluster_triangular(a):
    cluster_rock(a, "A", (0.8, 1.6, 0), s=0.85, seed=501)
    cluster_rock(a, "C", (-2.3, -0.8, 0), s=0.75, rot=0.4, seed=502)
    cluster_rock(a, "B", (2.6, -1.9, 0), s=0.7, rot=-0.3, seed=503)
    dress(a, 4.6, 3.8, ((-2.6, 1.4, 1), (-1.5, 1.2, 1), (2.6, 1.4, 0), (0.0, 1.2, 0)), ((-1.1, 0.9), (-0.3, 0.7)), 504)


def cluster_row(render=True):
    palette()
    specs = [("RockCluster", "hero", cluster_hero, 4500, "hull"),
             ("RockClusterA", "part", lambda a: cluster_rock(a, "A"), 1500, "hull"),
             ("RockClusterB", "part", lambda a: cluster_rock(a, "B"), 1500, "hull"),
             ("RockClusterC", "part", lambda a: cluster_rock(a, "C"), 1500, "hull"),
             ("RockClusterLinear", "variant", cluster_linear, 4500, "hull"),
             ("RockClusterCrescent", "variant", cluster_crescent, 4500, "hull"),
             ("RockClusterTriangular", "variant", cluster_triangular, 4500, "hull")]
    objs = [K.mk(SHEET, n, fn, subject="RockCluster", role=r, notes=CLUSTER_NOTES[n], budget=b, collision=c)
            for n, r, fn, b, c in specs]
    # exploded cell: the moss cap floats above the main rock, as on the master
    rk, cap = objs[1], objs[2]
    cap.location = (rk.location.x - 0.8, rk.location.y + 0.4, rk.location.z + 9.0)
    for o in objs:
        if any(m.name == "FB_" + MOSS_LIME for m in o.data.materials):
            o["kit_shading_ok"] = ("moss clumps: the darker side band is the stem layer under the lime top "
                                   "(a material region, as on the master's exploded Moss Cap)")
    out = {"stats": K.stats(objs), "problems": K.check(objs)}
    if render:
        out["compare"] = K.render_row(SHEET, "rock_cluster", 3, "RockCluster", objs, vfx=True, SIDE_AZIMUTH=-90,
                                      HERO_ELEVATION=22)
    return out


# ---------------------------------------------------------------- Row 4: Pebble Scatter
SLAB = [(0.0, 0.94, 6), (0.62, 1.0, 6), (1.0, 0.8, 6)]      # low plate: one flat top plane, angular bevelled edges
CUBE = [(0.0, 1.0, 5), (0.6, 1.0, 5), (1.0, 0.72, 4)]                         # blocky wedge rock


def scatter_piece(a, kind, loc=(0, 0, 0), s=1.0, rot=0.0, seed=0, moss=True):
    """One Pebble Scatter piece, as on the exploded view, tagged as part `kind`:
    slab (big low flat slab, moss on one end), wedge (blocky rock with a moss tuft on top),
    round (rounded rock with moss low on one side), pebble, small (small stone)."""
    spec = {"slab": ((7.6, 4.6, 1.8), SLAB, 0), "wedge": ((3.2, 2.9, 2.5), CUBE, 1),
            "round": ((3.3, 3.0, 2.0), DOME_LOW, 2), "tall": ((3.4, 3.0, 3.3), WEDGE, 3),
            "pebble": ((1.6, 1.4, 1.1), K.PEBBLE, 4), "small": ((1.1, 1.0, 0.7), K.PEBBLE, 5)}
    size, rings, k = spec[kind]
    size = tuple(x * s for x in size)
    sd = seed or 600 + 10 * k
    big = kind in ("slab", "wedge", "round", "tall")
    vs = K.hull_rock(a, size, loc=loc, seed=sd, mat=ROCK, rings=rings, jitter=0.07, rot=rot)
    vs = colour_rock(a, vs, size, loc, sd, cuts=1 if big else 0)
    name = f"{kind}_{sd}_{loc[0]:.1f}"
    K.tag_part(a, vs, name)
    if moss and kind == "slab":
        side_moss(a, K.part(a, name), rot + math.pi, size[2] * 0.55, 0.28 * s, rot=0.4, seed=sd + 1, cx=loc[0], cy=loc[1])
    if moss and kind == "wedge":
        place_cap(a, (loc[0], loc[1]), 0.28 * s, rot + 0.3, sd + 2, on=K.part(a, name))
    if moss and kind in ("round", "tall"):
        stain(a, K.part(a, name), rot - 2.4, spread=0.7, height=size[2] * 0.6, seed=sd + 3, cx=loc[0], cy=loc[1])
    return name


def scatter(a, pieces, clumps, seed):
    """pieces = [(kind, x, y, s, rot)], clumps = [(x, y, size, flowers)] (clover with daisies)."""
    for kind, x, y, s, rot in pieces:
        scatter_piece(a, kind, (x, y, 0), s, rot)
    for i, (x, y, sz, fl) in enumerate(clumps):
        K.clover(a, (x, y, 0), sz, seed + i, LEAF, flowers=fl, petal=PETAL, pollen=POLLEN, young_mat=LEAF_YOUNG)


def pebble_hero(a):
    scatter(a, (("slab", -2.6, -1.0, 1.0, 0.25), ("tall", 0.2, 4.8, 0.95, 0.4), ("wedge", 6.4, 2.6, 0.9, -0.3),
                ("round", 4.4, -4.4, 0.9, 0.6), ("small", 2.6, 1.0, 1.0, 0.0), ("small", 8.2, -4.0, 0.9, 1.0)),
            ((-1.8, 3.6, 1.5, 2), (-6.4, 0.6, 1.5, 1), (-6.2, -2.0, 1.2, 0), (2.0, -2.4, 1.0, 1), (7.8, 3.8, 1.1, 2),
             (6.0, -3.4, 1.2, 2), (2.0, 4.6, 1.0, 0)), 640)


def pebble_sparse(a):
    scatter(a, (("slab", -1.2, -0.4, 0.75, 0.3), ("round", 3.2, 1.6, 0.8, 0.2), ("small", 1.8, -2.6, 1.0, 0.0)),
            ((-4.2, -1.2, 0.9, 0), (0.6, 1.8, 0.8, 0)), 650)


def pebble_medium(a):
    scatter(a, (("slab", -0.6, 0.0, 0.85, 0.2), ("wedge", 3.6, 2.6, 0.85, -0.4), ("round", 3.0, -2.4, 0.85, 0.5),
                ("pebble", -4.6, -2.2, 1.0, 0.0), ("small", 0.6, -3.0, 0.9, 0.0)),
            ((-4.2, 0.8, 1.2, 0), (0.4, 2.8, 1.1, 1), (5.6, 0.0, 1.0, 0), (-1.6, -3.0, 1.0, 1)), 660)


def pebble_dense(a):
    scatter(a, (("slab", -0.4, 0.0, 0.9, 0.2), ("wedge", 4.2, 2.8, 0.9, -0.4), ("round", 3.6, -2.6, 0.9, 0.5),
                ("tall", -3.4, 3.6, 0.8, 0.8), ("pebble", -5.0, -2.4, 1.0, 0.0), ("pebble", 0.6, 4.4, 0.9, 1.2),
                ("small", 0.8, -3.6, 1.0, 0.0), ("small", 6.4, 0.2, 0.9, 0.6), ("small", -5.6, 0.6, 0.8, 0.3)),
            ((-4.8, -0.6, 1.3, 1), (-1.0, 3.4, 1.2, 0), (2.0, 1.6, 1.0, 1), (6.4, 3.4, 1.1, 0), (6.0, -2.6, 1.2, 1),
             (-2.0, -3.6, 1.1, 0), (1.6, -1.6, 0.9, 0)), 670)


PEBBLE_NOTES = {
    "PebbleScatter": "ground scatter: big low flat slab with moss on one end, a tall angular rock behind, a blocky "
                     "wedge rock with a moss tuft, a rounded rock, small stones, clover clumps with white daisies",
    "PebbleFlatSlab": "flat slab alone: big low slab with broad flat top facets and moss on one end",
    "Pebble": "pebble alone",
    "PebbleWedgeRock": "wedge rock alone: blocky rock with a thin moss tuft on top",
    "PebbleRoundRock": "round rock alone: rounded rock with moss low on one side",
    "PebbleSmallStone": "small stone alone",
    "PebbleScatterSparse": "Sparse: 3 pieces (slab, round rock, small stones) with a little clover",
    "PebbleScatterMedium": "Medium: 5 pieces with clover and daisies",
    "PebbleScatterDense": "Dense: 8+ pieces with lots of clover and daisies",
}


def pebble_row(render=True):
    palette()
    specs = [("PebbleScatter", "hero", pebble_hero, 4500, "none"),
             ("PebbleFlatSlab", "part", lambda a: scatter_piece(a, "slab"), 1500, "hull"),
             ("Pebble", "part", lambda a: scatter_piece(a, "pebble"), 300, "none"),
             ("PebbleWedgeRock", "part", lambda a: scatter_piece(a, "wedge"), 1500, "hull"),
             ("PebbleRoundRock", "part", lambda a: scatter_piece(a, "round"), 1500, "hull"),
             ("PebbleSmallStone", "part", lambda a: scatter_piece(a, "small"), 300, "none"),
             ("PebbleScatterSparse", "variant", pebble_sparse, 3000, "none"),
             ("PebbleScatterMedium", "variant", pebble_medium, 4000, "none"),
             ("PebbleScatterDense", "variant", pebble_dense, 4500, "none")]
    objs = [K.mk(SHEET, n, fn, subject="PebbleScatter", role=r, notes=PEBBLE_NOTES[n], budget=b, collision=c)
            for n, r, fn, b, c in specs]
    # exploded cell: the moss cap floats above the main rock, as on the master
    rk, cap = objs[1], objs[2]
    cap.location = (rk.location.x - 0.8, rk.location.y + 0.4, rk.location.z + 9.0)
    for o in objs:
        if any(m.name == "FB_" + MOSS_LIME for m in o.data.materials):
            o["kit_shading_ok"] = ("moss clumps: the darker side band is the stem layer under the lime top "
                                   "(a material region, as on the master's exploded Moss Cap)")
    out = {"stats": K.stats(objs), "problems": K.check(objs)}
    if render:
        out["compare"] = K.render_row(SHEET, "pebble_scatter", 4, "PebbleScatter", objs, vfx=True, SIDE_AZIMUTH=-90,
                                      HERO_ELEVATION=24)
    return out
