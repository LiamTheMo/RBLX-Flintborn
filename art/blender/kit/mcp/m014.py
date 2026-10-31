"""014 Starstone (references/014.png): a cyan, skewed hexagonal gem (the Starlight Core) wedged in the cleft between
two big leaning rock shells - a tall, chunky, diamond-section Left Shell and a long thick Right Shell slab that falls
to the right and back and hangs over the crystal - with a ring of eleven faceted dome rocks round the foot.

    import importlib, kit_models, m014; importlib.reload(kit_models); importlib.reload(m014); m014.build()

Parts as on the sheet's exploded view, each built by its own function (studs; front -Y, ground z = 0). The R04 kit
sheet owns Starstone / StarstoneStoneShell / StarstoneStarlightCore / StarstoneBaseRock, hence:
- StarlightCore (core): convex hull of staggered rings (an off-centre apex ridge, a tilted shoulder ring, a low belt
  ring, a taper ring, a blunt bottom point), coplanar hull triangles merged into broad facets, then BEAUTY
  triangulated. Built upright, axis bottom at the origin.
- StarstoneShellLeft (shell_left): hull of five rings on a lopsided diamond / hexagon footprint (a front ridge between
  a narrow shade face and a broad lit face), a blunt chisel top. Built upright, base centre at the origin.
- StarstoneShellRight (shell_right): a long thick slab lying along +X (upper end at +X, roof +Z): one body hull of a
  chamfered 8-point section along its length (roof and sides unbroken) with its bottom raised, and a keel at full
  depth under the lower part, unioned, so the underside alone has a broad concave step (the crystal tucks under the
  upper part). Built centred on the origin.
- StarstoneFootRock (foot_rock): the Base Rock, reusable. A faceted dome with an off-centre blunt crown, flat bottom.

The hero is pasted together from the finished part meshes (m011._paste; the eleven base rocks are scaled, turned,
some mirrored copies of the foot rock) and unioned into one closed shell, floor-cut flat at the ground.
Stages 5+6 (CAP_NEON, NEON_FACETS, CRYSTAL_LIGHT, HALO_POS, GLINTS, _vfx): two cap facets are Neon; the finished
hero carries a crystal_glow light, a crystal_halo and three ore_glint sockets fitted to the crystal's ridges.
Stage 1 gives one placeholder key per region (crystal cap / belt / taper, shell, foot rock); stage 4's colour()
regrades them by position fields (calibrated keys, blends, spill, Tint). See M014_spec.md ("Study (2a)", "Stage 1 -
Modelling", "Stage 4 - Materials, colour and texture").
"""
import math
import random

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

import kit_mcp as K
import kit_models as M
import m011
import m012

NUM, TITLE, SHEET = 14, "Starstone", "M014"
CORE, CORE_GLOW, CORE_LIGHT, CORE_DEEP = "m014_core", "m014_core_glow", "m014_core_light", "m014_core_deep"
SHELL, FOOT = "m014_shell", "m014_foot"
CRYSTAL_KEYS = (CORE, CORE_GLOW, CORE_LIGHT, CORE_DEEP)
OFF = "m014_offset"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
# Stage 3: the Smart UV island angle per object (min_angle = angle, so smart_uv never falls back; folds are cut free by
# m012._uv_unfold instead), ANGLE_BASED at 35 / 40 / 45 / 50 / 55 compared by uv_stats' worst / p95 conformal stretch:
# the lowest stretch, then the fewest islands. Hero 40 (1.113 / 1.005; 45: 1.117 / 1.030, 50: 1.333), right shell 40
# (1.002; 45: 1.049), left shell 50 (1.000 at 35-50, 7 islands), foot rock 50 (1.017 at 40-50, 11 islands), core 45
# (1.031 at 35-45, 10 islands; 50: 1.062). See M014_spec.md "Stage 2+3".
UV_ANGLE = {"StarstoneNode": 40.0, "StarstoneShellRight": 40.0, "StarstoneShellLeft": 50.0, "StarstoneFootRock": 50.0}


def _uv(o):
    a = UV_ANGLE.get(o.name, UV["angle"])
    return dict(UV, angle=a, min_angle=a)


POLISH_LIM = 5.0       # no corner under this many degrees on any part or the hero


SHELL_COOL, SHELL_INNER, SPILL, FOOT_DARK = "m014_shell_cool", "m014_shell_inner", "m014_spill", "m014_foot_dark"
CRYS_ROUGH, CAP_ROUGH, SHELL_ROUGH, FOOT_ROUGH = 0.28, 0.3, 0.9, 0.92
CRYS_SPEC = 0.25        # Specular IOR Level on every crystal key, mix keys too (flintkit's 0.5 washes lit facets white)
# (verifier round 1: 0.35 -> 0.25; 0.15 / 0.35 / 0.6 moved the clipped share by under 1 point but added a grey sheen:
# front median r 69 / 80 / 92, shade #1B96A7 / #2196A7 / #2696A6 against the sheet's #47E2EC / #1E9AAD)
# stage 5 (M014_spec.md, "Stage 5+6"): two of the cap's facets are Neon. NEON is the exporter's GLOW_EMISSION
# threshold and no more (a stronger emission only washes the Blender preview). A Neon part shows its hex unlit, so
# CAP_NEON is the sheet's cap colour (the exploded core's top band #7AFBFD - the f34 cap's lit #8EFCFE), not stage
# 4's lit fit.
NEON = 1.0
CAP_NEON = "#7AFBFD"
# Round 1 made the whole cap Neon (18 hero faces, 8 facets on the part): it read as one flat, unlit lid - a light
# bulb on top - in the top view (one #7BFFFF blob, where the sheet's top shows facets #158D9E-#91FCFE) and on the
# core part. So only the hero's largest visible cap facet (part normal (0.75, 0.13, 0.65), hero area 1.37) and its
# third (part (0, -0.82, 0.57), 0.71) glow; they don't touch, so the front-up facet between them (1.17, lit) keeps
# the cap's main ridge. The other cap faces take the crystal ladder (light at the top, core near the rock). Matched
# by normal in the core part's frame (NEON_TOL degrees), so the part and the hero glow on the same facets.
# (stage 1 fixes, verifier round 1: the cap was reshaped (a level apex ridge), so the facets were re-found the same
# way: by hero area the cap's facets are front-up (-0.01, -0.84, 0.55) 1.69, front-right (0.62, -0.67, 0.41) 1.64,
# right (0.89, 0.20, 0.42) 1.51, a smaller front-up one under the ridge 0.93, the left one 0.79. The first and third
# glow - the same front and right directions as before - meeting only at the ridge's +X corner, so the front-right
# facet between them stays lit and carries the cap's drop from the ridge to the right shoulder.)
# (final fix, verifier round 2: the core is now the kite gem. Its cap facets (on T / TB), by hero area: the slanted
# top face F-R-T 4.63, the left top face F-L1-T 1.22, the back-right K-R-TB 0.73, R-T-TB 0.53, two hidden. The broad
# top face stays lit (graded pale by height: the sheet's pale top face is lit, and a Neon top would be a flat lid,
# the light bulb round 1 warned of); the left top face and the back-right facet glow - they share no corner, one on
# each side of the top face.)
NEON_FACETS = ((-0.522, -0.779, 0.346), (0.567, 0.696, 0.44))
NEON_TOL = 4.0


def palette():
    # stage 4 (targets, calibrated hexes, re-measures and method in M014_spec.md, "Stage 4"): see PALETTE_NOTES.
    # stage 5: CORE_GLOW (only the NEON_FACETS, see colour()) is Neon: CAP_NEON at emission NEON, previewed unshaded
    # (_glow_mats); every other crystal key stays solid.
    for k, (hexcol, rough) in PALETTE.items():
        if k == CORE_GLOW:
            K.set_colour(k, CAP_NEON, rough=rough, emit=NEON)
        else:
            K.set_colour(k, hexcol, rough=rough)
    for k in PALETTE:
        if _restyle(k):
            K.fk().material(k)
    _crystal_spec()
    _glow_mats()


def _restyle(key):
    """Drop an FB_ material whose node set no longer matches its key's emission (flintkit builds emissive keys
    without the Tint node, and set_colour never clears an emission), so flintkit makes it afresh (m009._restyle)."""
    mat = bpy.data.materials.get("FB_" + key)
    if mat and mat.node_tree:
        tinted = any(n.type == "MIX" for n in mat.node_tree.nodes)
        if tinted == (K.fk().palette_entry(key)[3] > 0):
            bpy.data.materials.remove(mat)
            return True
    return False


def _neon(m):
    return list(m.get("flintkit_spec", [0, 0, 0]))[2] >= NEON


def _glow_mats():
    """Blender preview of the Neon keys (emission >= NEON) as Roblox shows Neon: the key's own colour, unshaded (the
    BSDF's base colour black and no specular, so only the emission shows). The exported hex is unchanged (m009)."""
    for mat in bpy.data.materials:
        if not (mat.name.startswith("FB_m014_") and mat.node_tree and _neon(mat)):
            continue
        b = mat.node_tree.nodes.get("Principled BSDF")
        for l in list(b.inputs["Base Color"].links):
            mat.node_tree.links.remove(l)
        b.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)
        if "Specular IOR Level" in b.inputs:
            b.inputs["Specular IOR Level"].default_value = 0.0


# calibration targets: the sheet's rendered medians (M014_spec.md §5.2 / §5.5), not the swatches. key -> (sRGB, kind)
TARGETS = {CORE_GLOW: ((0x7A, 0xFB, 0xFD), "vivid"), CORE_LIGHT: ((0x6E, 0xFB, 0xFD), "vivid"),
           CORE: ((0x53, 0xF4, 0xF6), "vivid"), CORE_DEEP: ((0x30, 0xC7, 0xD2), "vivid"),
           SHELL: ((0xA5, 0x94, 0x8F), "stone"), SHELL_COOL: ((0x8A, 0x83, 0x88), "stone"),
           SHELL_INNER: ((0x66, 0x64, 0x6A), "stone"), SPILL: ((0x69, 0x82, 0x8D), "stone"),
           FOOT: ((0x93, 0x82, 0x7D), "stone"), FOOT_DARK: ((0x6A, 0x60, 0x5E), "stone")}
# key -> (hex, roughness): the calibrated base colours (stage 1 placeholders were the §5.5 starting hexes)
# Pass 1, dome (calibrate(), each key rendered on the test dome within 4 levels of its target):
#   glow #5EF7FB, light #55F7FB, core #42BEC8, deep #259BAD, shell #7A7174, cool #67656E, inner #4C4D56,
#   spill #4E6472, foot #6D6466, foot dark #4F4A4C.
#   The crystal's glow and light keys clipped (g / b rendered 255), so their dome result is not a fit.
# Pass 2, hero (report() against sheet_stats(): the same regions, masked by a label render, at the sheet's angles):
#   rock: the dome hexes rendered 1.1-1.6x too dark in linear light on the hero (front #857775 against the sheet's
#   #9B8884, top #817674 against #9F918D, side #8E7E7B against #948383; the dome's top faces the key light, the
#   hero's walls don't). Every rock key x (1.38, 1.33, 1.26) per channel in linear: the geometric mean of the front,
#   side and top gains (1.34, 1.32, 1.32), a little warmer (the sheet's lit rock is warm beige, ours rendered mauve).
#   crystal: refitted by height band (the sheet's front bands #54CEE3 #5CF1FA #59F1F9 #32C9D6 #1CAEBE): the cap faces
#   the key light and clipped white-cyan (#7CFFFF), so its key drops well under the belt's; every key turned to hue
#   185-189 (b above g: the dome keys were 181, g = b) and the deep key more saturated (the sheet's lowest band r 28).
#   deep: #12ADC8 matched the hero's taper (#25B3C5 against the sheet's #22B4C4) but left the free core (exploded and
#   part shots) 30 levels under the sheet's exploded bottom band (#1EA7BB against #30C7D2); x1.15 in linear splits it.
#   spill: now mixed from the lit body (not the dark inner tone), so the key itself is a saturated teal (#4A7C90,
#   hue 197): its 25-75 % mixes render #788F9B-ish where the sheet's teal rock is #79858E (dome #5B727F rendered grey).
#   (stage 5: CORE_GLOW's #47B2C6 was the lit, non-emissive fit; palette() now sets the Neon cap to CAP_NEON.)
#   Verifier round 1 (A1, on stage 1's reshaped crystal, the crystal_glow light on): the crystal rendered one clipped
#   cyan blob (front median #4AFFFF, lit #5CFFFF, shade #2CCFE5; shade / lit 0.79; the sheet #47E2EC / #97FCFE /
#   #1A8D9E, 0.51). The light went to 0.45 and the solid keys were refitted with it on, by ladder group (a label render
#   per group): the light key pale aqua (r 0x84: its facets render r 140-150, their lit quartile g / b <= 250), the
#   core key under the clip at its median (was #40D2E6: the belt's own median clipped), the deep key a saturated deep
#   teal for the shade quartile. Was light #4ADCF0, core #40D2E6, deep #16B7D4.
PALETTE = {CORE_GLOW: ("#47B2C6", CAP_ROUGH), CORE_LIGHT: ("#84B0BA", CRYS_ROUGH), CORE: ("#34B0C8", CRYS_ROUGH),
           CORE_DEEP: ("#04889F", CRYS_ROUGH), SHELL: ("#8E8181", SHELL_ROUGH), SHELL_COOL: ("#78747B", SHELL_ROUGH),
           SHELL_INNER: ("#595860", SHELL_ROUGH), SPILL: ("#4A7C90", SHELL_ROUGH), FOOT: ("#7F7272", FOOT_ROUGH),
           FOOT_DARK: ("#5C5555", FOOT_ROUGH)}


def _crystal_spec():
    """CRYS_SPEC on every crystal material, the in-between keys too (flintkit makes new keys at specular 0.5)."""
    for m in bpy.data.materials:
        if m.name.startswith("FB_m014_core") and m.node_tree and not _neon(m):
            b = m.node_tree.nodes.get("Principled BSDF")
            if b and "Specular IOR Level" in b.inputs:
                b.inputs["Specular IOR Level"].default_value = CRYS_SPEC


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS), as m009 / m013: stone keys sampled unfiltered (the test box lies
    wholly on the dome; K.sample's sat < 0.18 stone filter drops warm rock), the crystal keys at CRYS_SPEC every
    round. Returns {key: (hex, rendered)}; the orphaned test-dome meshes are purged. The Neon cap (CORE_GLOW, stage 5)
    is not calibrated: it shows CAP_NEON unlit."""
    keys = keys or [k for k in TARGETS if k != CORE_GLOW]
    set0, sample0 = K.set_colour, K.sample

    def set_colour(key, hexcol, **kw):
        set0(key, hexcol, **kw)
        _crystal_spec()

    def sample(src, box, kind="green"):
        return M.sample(src, box, "all", paper=(255, 253, 240), tol=6) if kind == "stone" else \
            sample0(src, box, kind)
    K.set_colour, K.sample = set_colour, sample
    try:
        for k in keys:
            K.fk().material(k)
        _crystal_spec()
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        K.set_colour, K.sample = set0, sample0
        _drop_calib()


def _drop_calib():
    """K.calibrate removes its test dome object but not its mesh: purge the orphan T_Calib meshes carrying only this
    model's keys."""
    gone = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")
            and all(x is None or x.name.startswith("FB_m014_") for x in m.materials)]
    for m in gone:
        bpy.data.meshes.remove(m)
    return len(gone)


def _hull(a, pts, merge):
    """Convex hull of pts in a's bmesh, hull triangles within `merge` degrees of coplanar merged into broad facets,
    then BEAUTY-triangulated. Returns (verts, facet count before triangulation)."""
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
                                 edges=list({e for f in faces for e in f.edges}))
        vs = [v for v in vs if v.is_valid]
    facets = len(K.faces_of(vs))
    bmesh.ops.triangulate(a.bm, faces=[f for f in K.faces_of(vs) if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(a.bm, faces=K.faces_of(vs))
    return vs, facets


def _sector(th, seed, amp=0.05):
    """Broad radius jitter by angle (sectors, never per vertex)."""
    r = random.Random(seed)
    p1, p2 = r.uniform(0, 6.3), r.uniform(0, 6.3)
    return 1.0 + amp * math.sin(th + p1) + 0.6 * amp * math.sin(2 * th + p2)


# ---- Starlight Core -------------------------------------------------------------------------------------------------
# A kite gem, W 3.3 (x) x D 2.8 (y, front -Y) x 5.6 long (z), the convex hull of nine named corners (fractions of the
# half-width / half-depth / the length), so every facet is a broad deliberate plane:
# - T, the top corner (upper left), and R, the sharp right shoulder: the top edge T-R runs from upper left down to
#   the right; with F, the front corner, they make the broad slanted top face T-R-F (the sheet's pale top face);
# - F-R-B, the long front face tapering to the bottom point B; L1 / L2 the left shoulder and lower left, R2 the right
#   flank, TB / K the back: long flat sides tapering to the point.
# (final fix, verifier round 2: the ring-hull gem - shoulder, belt and taper rings, 29 merged facets - read as an egg
# from the front: widest in the middle, rounded at both ends, many small triangles. The sheet's gem is a kite: a
# broad slanted flat top face, sharp shoulders, long flat sides to a point.)
# Corners as seen from the front (az 0, el 13) are drawn straight from the sheet's front crystal (fractions of its
# bbox: T (0.15, 1.0), L1 (0, 0.88), R (0.94, 0.66), R2 (1.0, 0.32), B (0.69, 0), L2 (0.31, 0.05), front corner F
# (0.31, 0.5)); TB, K and KB give the back its depth. The hero places it nearly upright (CORE_AT), so the front view
# shows these proportions.
CORE_DIM = dict(w=3.7, d=2.8, h=5.4, seed=14001)
CORE_PTS = {"T": (-0.7, 0.14, 1.0), "L1": (-1.0, 0.2, 0.88), "R": (0.88, 0.0, 0.66), "R2": (1.0, 0.3, 0.32),
            "B": (0.38, 0.0, 0.0), "L2": (-0.38, 0.15, 0.05), "F": (-0.38, -1.0, 0.5), "TB": (-0.2, 0.7, 0.85),
            "K": (0.2, 1.0, 0.55), "KB": (0.1, 0.8, 0.15)}
CORE_CAP = ("T", "TB")       # faces on either of these corners are the cap (placeholder glow key)
CORE_TIP = ("B",)            # faces on the bottom point are the taper (placeholder deep key)
CORE_MERGE = 2.0
CORE_INFO = {}


def core_point(name):
    """A named core corner in the core's construction frame (axis bottom at the origin)."""
    x, y, z = CORE_PTS[name]
    return Vector((x * CORE_DIM["w"] / 2, y * CORE_DIM["d"] / 2, z * CORE_DIM["h"]))


def core(a):
    """Starlight Core, upright, the axis bottom at the origin; placeholder keys: cap (faces on T / TB) glow, the
    faces on the bottom point deep, the rest core."""
    names = list(CORE_PTS)
    vs, facets = _hull(a, [core_point(n) for n in names], CORE_MERGE)
    CORE_INFO["facets"] = facets
    a._finish(vs, CORE)
    at = {n: min(vs, key=lambda v: (v.co - core_point(n)).length) for n in names}
    cap = {at[n] for n in CORE_CAP}
    tip = {at[n] for n in CORE_TIP}
    gi, di = a._mi(CORE_GLOW), a._mi(CORE_DEEP)
    for f in K.faces_of(vs):
        fv = set(f.verts)
        if fv & cap:
            f.material_index = gi
        elif fv & tip:
            f.material_index = di
    return vs


# ---- Left Rock Shell ------------------------------------------------------------------------------------------------
# 4.5 W x 2.6 D x 6.7 H. Footprint (fractions of the half-width / half-depth, counter-clockwise from the front ridge):
# the ridge sits a third of the way across the front, so the shade face (left) is about 1/3 and the lit face 2/3.
LS = dict(w=5.2, d=3.4, h=6.7, seed=14011)
LS_FOOT = ((-0.3, -1.0), (1.0, -0.15), (0.55, 0.85), (-0.6, 0.9), (-1.25, 0.1))
# rings: (height fraction, scale, centre shift x, y as fractions of the half-sizes)
# (round 1: 0.93 / 0.66 at the waist / upper ring stood it up as a round-topped menhir; round 3: a 6-7 point footprint
# drawn in hard to a point made a smooth cone. Now a 5-corner lopsided diamond whose corners line up ring to ring
# (each side one broad plane, broken at the waist), a moderate draw-in and a blunt four-point chisel top.)
LS_RINGS = ((0.0, 0.94, 0.0, 0.0), (0.13, 1.0, 0.0, 0.0), (0.45, 0.9, 0.04, 0.03), (0.75, 0.75, 0.03, 0.08))
# blunt chisel top: (x, y fractions, height fraction); its short ridge slopes back
LS_TOP = ((-0.3, -0.4, 1.0), (0.3, -0.25, 0.98), (0.15, 0.45, 0.94), (-0.4, 0.35, 0.95))
LS_MERGE = 3.5
LS_INFO = {}


def shell_left(a):
    """Left Rock Shell, upright, base centre at the origin."""
    hw, hd, h, seed = LS["w"] / 2, LS["d"] / 2, LS["h"], LS["seed"]
    rng = random.Random(seed)
    pts = []
    for k, (fz, sc, sx, sy) in enumerate(LS_RINGS):
        for i, (x, y) in enumerate(LS_FOOT):
            th = math.atan2(y, x)
            j = _sector(th, seed, 0.03)
            dz = 0.0 if fz == 0.0 else rng.uniform(-0.02, 0.02) * h
            pts.append(Vector(((x * sc * j + sx) * hw, (y * sc * j + sy) * hd, fz * h + dz)))
    pts += [Vector((x * hw, y * hd, z * h)) for x, y, z in LS_TOP]
    vs, facets = _hull(a, pts, LS_MERGE)
    LS_INFO["facets"] = facets
    a._finish(vs, SHELL)
    return vs


# ---- Right Rock Shell -----------------------------------------------------------------------------------------------
# A long thick slab: 6.6 long (x, the upper end at +X) x 3.7 wide (y) x 2.6 thick (z, the roof up). Section: 8 points
# (fractions of the width / thickness): a broad roof, chamfered long edges, a narrower underside.
# (round 2: 3.3 x 2.4 with an 8-point section of near-equal chamfers read as a round log lying across the cleft;
# a boxier section - broad roof, steep sides, narrow chamfers - and a little more width and thickness read as the
# sheet's slab)
RS = dict(l=6.6, w=3.7, t=2.6, seed=14021)
RS_SEC = ((-0.41, 0.5), (0.41, 0.5), (0.5, 0.26), (0.47, -0.3), (0.3, -0.5), (-0.3, -0.5), (-0.47, -0.3),
          (-0.5, 0.26))
# stations along the whole slab: (x fraction from the lower end, width scale, thickness scale, z shift (fraction of
# t), y shift (fraction of w)): the blunt chamfered lower end, the full section, the upper-end wedge (the peak).
# (verifier round 1, B1: the round-1 build made the slab from two lobes with different sections - lobe B narrower,
# thinner and shifted up, with its own station twists - so the join showed as a stair-step across the roof and both
# sides in the rear, top and part renders. Now the body is ONE hull with one section along its length (no twists,
# one jitter per station point), so roof and sides run unbroken; its underside points sit RS_STEP higher, and a keel
# (the same section's underside points at full depth, its top buried inside the body) is unioned under the lower
# part up to RS_KEEL_END: the broad concave step is on the underside only.)
RS_STATIONS = ((0.0, 0.86, 0.84, -0.02, 0.0), (0.09, 1.0, 1.0, 0.0, 0.02), (0.45, 0.97, 0.97, -0.01, -0.01),
               (0.8, 0.97, 0.95, 0.0, 0.02), (1.0, 0.7, 0.46, 0.2, -0.02))
RS_UNDER = (4, 5)        # the section's two bottom points (z -0.5): the underside proper (the chamfer rows above
#                          them, and the sides, are the same on body and keel)
RS_CHAMFER = (3, 6)      # the lower chamfer points (z -0.3): the keel's top edge, just inside the body
RS_STEP = 0.12           # underside raised this fraction of t along the body ...
RS_KEEL_END = 0.42       # ... and kept at full depth by the keel from the lower end to here (the step)
RS_KEEL_IN = 0.012       # the keel's sides sit this fraction of w inside the body's (no coplanar faces in the union)
RS_MERGE = 3.0
RS_INFO = {}


def _rs_station(fx):
    """The body's station parameters at fx (linear between RS_STATIONS)."""
    for s0, s1 in zip(RS_STATIONS, RS_STATIONS[1:]):
        if s0[0] <= fx <= s1[0]:
            t = (fx - s0[0]) / (s1[0] - s0[0])
            return tuple(a + (b - a) * t for a, b in zip(s0, s1))
    return RS_STATIONS[-1]


def shell_right(a):
    """Right Rock Shell, lying along +X (the upper end at +X), roof +Z, centred on the origin: the body and the keel
    (two closed hulls; build() unions them)."""
    L, W, T, seed = RS["l"], RS["w"], RS["t"], RS["seed"]
    rng = random.Random(seed)
    jit = {i: [1.0 + rng.uniform(-0.03, 0.03) for _ in RS_SEC] for i in range(len(RS_STATIONS))}
    under = set(RS_UNDER)

    def ring(st, js, lift, inset=0.0, only=None):
        fx, sw, sth, zs, ys = st
        out = []
        for k, (y, z) in enumerate(RS_SEC):
            if only is not None and k not in only:
                continue
            zz = z + (lift if k in under else 0.0)
            out.append(Vector(((fx - 0.5) * L, y * W * (sw - inset) * js[k] + ys * W, zz * T * sth + zs * T)))
        return out
    body = [p for i, st in enumerate(RS_STATIONS) for p in ring(st, jit[i], RS_STEP)]
    vs, facets = _hull(a, body, RS_MERGE)
    a._finish(vs, SHELL)
    # keel: the underside at full depth from the lower end to RS_KEEL_END, its top a short way up inside the body
    # (the section's side points pulled in), the step end a little shallower so it reads as a broad slope
    keel = []
    stations = [(i, st) for i, st in enumerate(RS_STATIONS) if st[0] < RS_KEEL_END]
    stations.append((None, _rs_station(RS_KEEL_END)))
    for i, st in stations:
        js = jit[i] if i is not None else [1.0] * len(RS_SEC)
        lift = 0.0 if i is not None else RS_STEP * 0.4
        keel += ring(st, js, lift, inset=RS_KEEL_IN, only=under | set(RS_CHAMFER))
        fx, sw, sth, zs, ys = st
        keel += [Vector(((fx - 0.5) * L, s * 0.3 * W * sw + ys * W, 0.0 + zs * T)) for s in (-1, 1)]
    # the keel's lower-end face sits a hair inside the body's end (the body ends at x = -L/2)
    for p in keel:
        p.x = max(p.x, -0.5 * L + 0.03)
    kv, n = _hull(a, keel, RS_MERGE)
    a._finish(kv, SHELL)
    RS_INFO["facets"] = facets + n
    return vs + kv


# ---- Base Rock ------------------------------------------------------------------------------------------------------
FOOT_DIM = dict(size=(2.6, 2.4, 2.0), seed=14031)
# (round 1: a 0.30 / 3-point crown ring under a point apex peaked them into cones; the sheet's are broad domes)
FOOT_RINGS = [(0.0, 0.92, 7), (0.32, 1.0, 7), (0.66, 0.8, 6), (0.89, 0.46, 4), (1.0, 0.12, 1)]
FOOT_MERGE = 3.0
FOOT_INFO = {}


def foot_rock(a):
    """Base Rock: a faceted dome, small off-centre crown, flat bottom, bottom centre at the origin."""
    vs = K.hull_rock(a, FOOT_DIM["size"], seed=FOOT_DIM["seed"], mat=FOOT, rings=FOOT_RINGS, jitter=0.07,
                     lean=(0.16, 0.1), keep_bottom=True)
    faces = K.faces_of(vs)
    bmesh.ops.dissolve_limit(a.bm, angle_limit=math.radians(FOOT_MERGE), verts=vs,
                             edges=list({e for f in faces for e in f.edges}))
    vs = [v for v in vs if v.is_valid]
    FOOT_INFO["facets"] = len(K.faces_of(vs))
    bmesh.ops.triangulate(a.bm, faces=[f for f in K.faces_of(vs) if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(a.bm, faces=K.faces_of(vs))
    return vs


# ---- hero layout (build frame) --------------------------------------------------------------------------------------
# core: the axis bottom, then the lean (degrees: top towards -X, top towards +Y) and the twist about its own axis
# (verifier round 1, B4: twist -20 -> 0 with the new level apex ridge - its ridge lies within 3 deg of level in the
# az 0 / el 13 view at any twist from -30 to 20, and 0 fits the sheet's front top edge best (mean error 0.038 against
# 0.042 at -20); the base 0.1 lower keeps the apex no deeper in the slab (0.46 by nearest surface; 0.15 further
# forward took it to 0.40 but raised the side view's crystal share to 11.5 %, sheet 8.5) while the crystal still
# touches the left shell. Front share 17.3 %, side 10.0 % (probe, before the union).)
CORE_AT = dict(base=(0.75, -1.9, 0.35), lean_x=0.0, lean_y=5.0, twist=0.0, scale=1.08)
# left shell: base centre (sunk below the ground; the floor cut flattens it), yaw, lean to +X, lean back (degrees)
LS_AT = dict(base=(-2.6, 0.0, -0.25), yaw=-38.0, lean_x=5.0, lean_y=3.0)
# right shell: centre, heading of the fall from the upper end to the lower (deg from +X towards +Y), pitch of the
# long axis (deg), and a hint for the roof normal. The sheet's views agree on a slab whose long axis falls gently to
# the right and a little back (front view: its top edge runs down to the right at about 25-30 deg; top view: it
# spans X -1.3 ... +5.3, Y -0.4 ... +4.1), whose broad roof faces front-right-up (the front view's big lit face, the
# top view's roof) and whose width runs steeply from front-down to back-up (the side view's steep back flank, the
# rear view's broad back face). Its upper end overhangs the crystal's top; its front-lower edge runs just above and
# behind the crystal (the dark inner strip).
# (stage 2: the crystal's cap tucks through the slab's front-lower edge: its apex and back shoulder sit 0.66 / 0.82
# inside by nearest surface. Clearing it to 0.12 needs the slab moved about 1.0 off the crystal (0.41, 0.51, 0.76);
# tried, the hero grew 7.90 -> 8.66 tall, the front / side / rear profile errors rose 0.070 / 0.080 / 0.085 -> 0.099 /
# 0.121 / 0.131 and the crystal showed in the rear view (0.4 -> 4 %), so the tuck stays: a clean union crease.)
# (verifier round 1, B3: pitch 40 -> 47 and heading 14 -> 6, turned about the fixed upper end (-1.22, 0.4, 6.7):
# the slab's lower end comes down 0.4 and 0.6 forward, so its back half no longer stands high behind the peak in the
# side view (f 0.15 / 0.20: 0.64 / 0.79 -> 0.50 / 0.65, sheet 0.47 / 0.65); front and rear profiles unchanged or
# better.)
RS_AT = dict(centre=(1.018, 0.635, 4.287), heading=6.0, pitch=47.0, roof=(0.45, -0.7, 0.55))
# base rocks: (label, centre x, y, W, D, H, yaw deg, mirror)
ROCKS = (
    # (round 1: the spec's sizes left gaps between neighbours - seven loose shells - and its small rocks taller
    # than wide read as spikes: every rock a little wider so neighbours overlap, the small ones squat)
    # (verifier round 1, B3: in the side view (az -90, el 13) a rock far out at +X appears about 2.3 studs higher
    # than one at -X, so the back-right rock B3 at the very back stood at 0.38-0.44 of the height where the sheet's
    # back is 0.17-0.25. B3 moved forward (4.6, 3.3 -> 4.7, 2.4; still the rear view's right-end rock) and lower
    # (1.8 -> 1.0), B2 2.8 -> 2.0, the small B5 behind B1 at -X is now the back-most rock, and B1 is 0.3 forward,
    # shallower and 3.9 tall (it still fills the rear view's centre-right; the rear profile is unchanged))
    ("F1", 0.0, -3.3, 4.6, 3.2, 2.1, 10.0, False),
    ("F2", -2.8, -2.6, 2.9, 2.5, 1.8, -40.0, True),
    ("F3", -4.9, -1.3, 2.2, 2.0, 1.6, 75.0, False),
    ("F4", 3.2, -2.6, 3.0, 2.8, 3.0, 140.0, False),
    ("F5", 4.6, -1.2, 2.2, 2.1, 1.9, 200.0, True),
    ("F6", 4.6, -3.2, 1.1, 1.0, 0.7, 30.0, False),
    ("B1", -1.2, 2.0, 6.0, 2.9, 3.9, 190.0, True),
    ("B2", 3.4, 2.0, 3.2, 3.0, 2.0, 250.0, False),
    ("B3", 4.7, 2.4, 1.9, 1.8, 1.0, 300.0, True),
    ("B4", -4.5, 1.5, 2.0, 1.9, 1.7, 110.0, False),
    ("B5", -3.2, 3.35, 1.6, 1.4, 0.8, 20.0, True),
)
ROCK_SINK = 0.3        # the rocks go this far below the ground; the hero's floor cut makes the base one flat plane


def _frame(o):
    """Part mesh coordinates -> the part's own build frame."""
    return Matrix.Translation(Vector(o[OFF]))


def _part_dims(o):
    m = _frame(o)
    ps = [m @ v.co for v in o.data.vertices]
    return Vector([max(p[i] for p in ps) - min(p[i] for p in ps) for i in range(3)])


def _core_matrix():
    c = CORE_AT
    r = (Matrix.Rotation(math.radians(-c["lean_y"]), 4, "X") @ Matrix.Rotation(math.radians(-c["lean_x"]), 4, "Y")
         @ Matrix.Rotation(math.radians(c["twist"]), 4, "Z"))
    return Matrix.Translation(c["base"]) @ r @ Matrix.Diagonal((c["scale"],) * 3 + (1.0,))


def _ls_matrix():
    c = LS_AT
    r = (Matrix.Rotation(math.radians(-c["lean_y"]), 4, "X") @ Matrix.Rotation(math.radians(c["lean_x"]), 4, "Y")
         @ Matrix.Rotation(math.radians(c["yaw"]), 4, "Z"))
    return Matrix.Translation(c["base"]) @ r


def _rs_matrix():
    """The part's +X (towards the upper end) points up the slab, against its fall (heading, pitch); its roof (+Z)
    turns as close to the roof hint as stays square to the long axis."""
    c = RS_AT
    h, p = math.radians(c["heading"]), math.radians(c["pitch"])
    fall = Vector((math.cos(p) * math.cos(h), math.cos(p) * math.sin(h), -math.sin(p)))
    x = -fall
    z = Vector(c["roof"]).normalized()
    z = (z - x * z.dot(x)).normalized()
    y = z.cross(x)
    r = Matrix((x, y, z)).transposed().to_4x4()
    return Matrix.Translation(c["centre"]) @ r


def _rock_matrix(k, part):
    _, x, y, w, d, h, yaw, mirror = ROCKS[k]
    pd = _part_dims(part)
    pre = Matrix.Diagonal((-1.0, 1.0, 1.0, 1.0)) if mirror else Matrix.Identity(4)
    return (Matrix.Translation((x, y, -ROCK_SINK)) @ Matrix.Rotation(math.radians(yaw), 4, "Z") @
            Matrix.Diagonal((w / pd.x, d / pd.y, (h + ROCK_SINK) / pd.z, 1.0)) @ pre @ _frame(part))


def placements():
    """name -> (part object name, matrix from the part's mesh coordinates into the hero's build frame)."""
    core_o = bpy.data.objects["StarlightCore"]
    ls = bpy.data.objects["StarstoneShellLeft"]
    rs = bpy.data.objects["StarstoneShellRight"]
    rock = bpy.data.objects["StarstoneFootRock"]
    out = {"ShellLeft": (ls.name, _ls_matrix() @ _frame(ls)),
           "ShellRight": (rs.name, _rs_matrix() @ _frame(rs)),
           "Core": (core_o.name, _core_matrix() @ _frame(core_o))}
    for k, r in enumerate(ROCKS):
        out[r[0]] = (rock.name, _rock_matrix(k, rock))
    return out


def hero(a):
    for name, (part, m) in placements().items():
        m011._paste(a, bpy.data.objects[part], m)


PARTS = (("StarlightCore", core), ("StarstoneShellLeft", shell_left), ("StarstoneShellRight", shell_right),
         ("StarstoneFootRock", foot_rock))

NOTES = {
    "StarstoneNode": "starstone resource node: a cyan skewed hexagonal gem (the Starlight Core) wedged in the cleft "
                     "between two big leaning rock shells (a tall diamond-section left shell, a long thick right slab "
                     "falling to the right and back over the crystal), eleven faceted dome rocks round the foot; one "
                     "closed mesh, flat base. Glow: two facets of the crystal's cap are Neon (pale cyan). VFX: "
                     "crystal_glow (steady "
                     "teal PointLight in front of the crystal's belt, shadows on), crystal_halo (the faint pale cyan "
                     "starlight halo behind the model) and 3 ore_glint (sparse pale cyan twinkles on the cap ridge, "
                     "the right shoulder and the left belt ridge)",
    "StarlightCore": "Starlight Core (reusable): skewed hexagonal gem - short slanted cap with an off-centre apex and "
                     "a long ridge, broad six-facet belt, long taper to a blunt point",
    "StarstoneShellLeft": "Left Rock Shell (reusable): tall chunky slab, lopsided diamond section (narrow shade face, "
                          "broad lit face), blunt chisel top, flat base",
    "StarstoneShellRight": "Right Rock Shell (reusable): long thick slab, broad roof, chamfered long edges, a chamfered "
                           "wedge upper end, a blunt lower end, a broad concave step on the underside",
    "StarstoneFootRock": "Base Rock (reusable): faceted dome, small off-centre crown, flat bottom",
}


# ---- cleanup (as M013's stage-run passes, with this model's offset key) ---------------------------------------------
def _bottom_centre(o):
    return m012._bottom_centre(o)


def _finish(o):
    """M.finish, then any crumbs, holes or faces under 3 degrees fixed and finish run again; the part's build-frame
    offset follows the re-centring."""
    o[OFF] = list(Vector(o[OFF]) + _bottom_centre(o))
    res = M.finish(o, union=False, uv=_uv(o))
    for _ in range(3):
        crumbs = m012._drop_inner(o)
        if not (crumbs or m012._thin(o)["under"] or res["nonmanifold_edges"] or res["boundary_edges"]):
            break
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bnd = [e for e in bm.edges if e.is_boundary]
        if bnd:
            if not bmesh.ops.holes_fill(bm, edges=bnd)["faces"]:
                bmesh.ops.contextual_create(bm, geom=bnd)
            bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY")
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(o.data)
        bm.free()
        M.repair_nonmanifold(o)
        m012._force_slivers(o)
        o[OFF] = list(Vector(o[OFF]) + _bottom_centre(o))
        res = M.finish(o, union=False, uv=_uv(o))
    return res


def _polish(o):
    """All faces triangles, every corner opened past POLISH_LIM, origin at the bottom centre (offset follows), UVs
    re-made on the final mesh."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    split = m012._tri_quads(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    forced = m012._force_slivers(o, lim=POLISH_LIM)
    bc = _bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
        o[OFF] = list(Vector(o[OFF]) + bc)
    o.data.update()
    M.smart_uv(o, **_uv(o))
    return {"split": split, "forced": forced, "uv_cut": m012._uv_unfold(o)}


def _dissolve_ears(o):
    """A vert on only two edges whose two faces are a speck triangle and the n-gon wrapped round it (a union ear):
    dissolve it first, so triangulating the n-gon can't clip the same ear twice (as M013)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    ears = [v for v in bm.verts if len(v.link_edges) == 2 and len(v.link_faces) == 2
            and any(len(f.verts) == 3 for f in v.link_faces)]
    if ears:
        bmesh.ops.dissolve_verts(bm, verts=ears)
        bm.to_mesh(o.data)
    bm.free()
    return len(ears)


def _self_hits(o):
    """Pairs of faces that cross each other without sharing a vertex (as m009 / m013). Returns (count, up to 5 pairs
    with their centres in the build frame)."""
    from mathutils.bvhtree import BVHTree
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    off = Vector(o.get(OFF, (0.0, 0.0, 0.0)))
    pairs = [(a, b) for a, b in tree.overlap(tree)
             if a < b and not set(bm.faces[a].verts) & set(bm.faces[b].verts)]
    where = [(a, b, [round(c, 2) for c in bm.faces[a].calc_center_median() + off]) for a, b in pairs[:5]]
    bm.free()
    return len(pairs), where


def _floor_cut(o, z0):
    """m004.floor_cut, but the ground cap is scan-filled over every boundary loop at once (bmesh triangle_fill), so
    a loop enclosed by another - a little pocket open to the ground where several rocks and a shell ring round an
    uncovered spot - stays a hole in the cap instead of getting its own cap face over the outer one (round 4: eight
    crossing face pairs, coplanar caps at (-3.2, 1.2, 0))."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces), plane_co=(0, 0, z0),
                           plane_no=(0, 0, -1), clear_outer=True)
    below = [v for v in bm.verts if v.co.z < z0 - 1e-4]
    if below:
        bmesh.ops.delete(bm, geom=below, context="VERTS")
    for v in bm.verts:
        if v.co.z < z0 + 0.02:
            v.co.z = z0
        v.co.z -= z0
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
    bnd = [e for e in bm.edges if e.is_boundary]
    if bnd:
        bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=bnd, normal=(0.0, 0.0, -1.0))
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=0.004)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()


def _clean_mesh(o, planes):
    """Union leftovers: ears, closed pockets, slivers and caps (planes stay flat), last-resort sliver collapse."""
    ears = _dissolve_ears(o)
    pockets = m012._drop_inner(o)
    log = m011._clean(o, m011._plane_lock(planes), max_move=m011.CLEAN_MOVE)
    pockets += m012._drop_inner(o)
    log["ears"] = ears
    log["pockets"] = pockets
    log["forced"] = m012._force_slivers(o)
    return log


# ---- measurement: orthographic silhouettes against the sheet's study tables (M014_spec.md §1 / §2) -------------------
# The sheet's top profiles (f = 0, 0.05 ... 1.0; heights as fractions of the view's apparent height). The side table
# runs back (f 0) to front (f 1): the sheet's side camera has the front on its right, i.e. our azimuth -90.
SHEET_PROFILES = {
    "front": (.12, .24, .38, .57, .71, .83, .85, .79, .80, .98, 1.0, .97, .93, .90, .86, .82, .79, .75, .39, .27, .12),
    "side": (.08, .17, .25, .47, .65, .76, .86, .93, .99, .99, .92, .85, .80, .76, .71, .67, .62, .38, .29, .23, .09),
    "rear": (.09, .18, .24, .59, .65, .71, .77, .82, .88, .94, .99, .96, .84, .81, .85, .79, .71, .62, .44, .25, .12),
}
SHEET_STATS = {"front": dict(aspect=1.41, share=0.160, span_w=(0.43, 0.74), span_h=(0.18, 0.75)),
               "side": dict(aspect=1.03, share=0.085, span_w=(0.57, 0.84), span_h=(0.21, 0.80)),
               "rear": dict(aspect=1.32, share=0.0),
               "top": dict(aspect=1.00, share=0.179, span_w=(0.31, 0.74), span_h=(0.26, 0.77))}
SHEET_VIEWS = {"front": (0.0, 13.0), "side": (-90.0, 13.0), "rear": (180.0, 13.0), "top": (0.0, 75.0)}


def _raster(o, az, el, res=220):
    """Orthographic label image of o from (azimuth, elevation): 0 empty, 1 rock, 2 crystal (z-buffered)."""
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
    keys = [(m.get("flintkit_key") or m.name[3:]) if m else "" for m in me.materials]
    for p in me.polygons:
        lb = 2 if keys[p.material_index].startswith("m014_core") else 1     # crystal keys and their mixes
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


def silhouette(o, az, el, res=220):
    """Top profile (21 samples), W : H, crystal share and spans of o from (azimuth, elevation), orthographic."""
    lab = _raster(o, az, el, res)
    H, W = lab.shape
    filled = lab > 0
    prof = []
    for k in range(21):
        c = min(W - 1, int(round(k / 20 * (W - 1))))
        rows = np.nonzero(filled[:, c])[0]
        prof.append(round(float(rows.max() / (H - 1)), 2) if len(rows) else 0.0)
    cr = lab == 2
    out = {"aspect": round(W / H, 2), "profile": prof, "share": round(float(cr.sum() / filled.sum()), 3)}
    if cr.any():
        cols, rows = np.nonzero(cr.any(axis=0))[0], np.nonzero(cr.any(axis=1))[0]
        out["span_w"] = (round(cols.min() / (W - 1), 2), round(cols.max() / (W - 1), 2))
        out["span_h"] = (round(rows.min() / (H - 1), 2), round(rows.max() / (H - 1), 2))
    return out


def measure(o=None):
    """The hero's silhouettes at the sheet's camera elevations against SHEET_PROFILES / SHEET_STATS: per view the
    profile, the mean and worst absolute profile error, aspect, crystal share and spans."""
    o = o or bpy.data.objects["StarstoneNode"]
    out = {}
    for v, (az, el) in SHEET_VIEWS.items():
        s = silhouette(o, az, el)
        if v in SHEET_PROFILES:
            err = [abs(a - b) for a, b in zip(s["profile"], SHEET_PROFILES[v])]
            s["prof_err"] = (round(sum(err) / len(err), 3), round(max(err), 2))
        s["sheet"] = SHEET_STATS[v]
        out[v] = s
    return out


def _gaps():
    """Stage 1 check: for each placed piece, the distance to its nearest neighbour (negative: they overlap) and how
    deep the core sinks into each shell (max distance of core verts inside), from the placements' BVHs."""
    from mathutils.bvhtree import BVHTree
    trees, pts = {}, {}
    for name, (part, m) in placements().items():
        o = bpy.data.objects[part]
        vs = [m @ v.co for v in o.data.vertices]
        polys = [list(p.vertices) for p in o.data.polygons]
        if m.to_3x3().determinant() < 0:
            polys = [p[::-1] for p in polys]
        trees[name] = BVHTree.FromPolygons(vs, polys)
        pts[name] = vs
    out = {}
    for n, t in trees.items():
        touch = sorted(k for k, u in trees.items() if k != n and t.overlap(u))
        out[n] = touch
    # the core against the shells: how far its verts reach inside each (signed by the face normal)
    sink = {}
    for sh in ("ShellLeft", "ShellRight"):
        deep = 0.0
        near = 9.0
        for p in pts["Core"]:
            loc, nrm, _, d = trees[sh].find_nearest(p)
            if loc is None:
                continue
            if (p - loc).dot(nrm) < 0:
                deep = max(deep, d)
            else:
                near = min(near, d)
        sink[sh] = {"inside": round(deep, 2), "nearest_outside": round(near, 2)}
    return {"touching": out, "core_sink": sink}


# ---- stage 4: colour regions, blends and Tint -----------------------------------------------------------------------
# colour() rewrites only the face keys and the Tint layer of a finished mesh (geometry and UVs untouched). A face's
# region comes from its key family (m014_core* crystal, m014_shell* shell, m014_foot* base rock; every mix key keeps
# its first parent's prefix), its piece from the hero placements (the nearest piece of that region by box norm; a
# part is its own piece). Every field is a position: the core's own part frame for the crystal, the shared hero build
# frame for the shells (a part's faces are mapped into it through its placement, so part and hero match face for
# face), each rock's own frame plus the hero frame for the base rocks. No colour is ever chosen by facing.
STEPS = 3               # K.blend's mode="blend": 25 / 50 / 75 % in-between keys
# crystal (all but the cap's NEON_FACETS, which stay CORE_GLOW: stage 5's Neon facets, on real edges), in the
# core's part frame: u = height fraction + CRYS_LATERAL x the position towards the apex side (-X) + CRYS_NOISE x broad
# noise. Deep -> core over CRYS_DEEP_BAND, core -> light over CRYS_LIGHT_BAND (one 9-step ladder, so neighbouring
# facets differ by a step, never palest against deepest).
CRYS_LATERAL, CRYS_NOISE, CRYS_SCALE, CRYS_SEED = 0.12, 0.08, 0.5, 14061
CRYS_DEEP_BAND = (0.15, 0.40)
CRYS_LIGHT_BAND = (0.48, 0.66)
# contact: a crystal face within d of the rock surface goes no lighter than ladder step i (0 deep ... 4 core ... 8)
CRYS_CONTACT = ((0.15, 2), (0.3, 4))
# shells, by d = distance from the visible crystal surface (hero BVH of the crystal faces):
# inner (the dark cool rock in the cleft): on the right shell, the faces that hang over the crystal - in its own
# frame the slab's front side below the roof (front-side fraction > OVERHANG[0], height fraction < OVERHANG[1]: the
# front-lower chamfer row, the sheet's dark strip above the crystal) and its underside (height fraction <
# OVERHANG[2]) - by INNER; the left shell only along its contact strip (its lit face runs right up to the crystal on
# the sheet, light beige, so it is not darkened)
# (round 1: INNER (0.3 / 0.8 / 1.2 -> 75 / 50 / 25 %) on the slab's lower half by height only missed the chamfer row
# (its faces sit at 0.5-0.9 of the slab's height): the strip rendered #9C8982 against the sheet's #616068)
INNER = ((0.3, 0.75), (1.0, 0.75), (1.6, 0.5), (2.0, 0.25))
OVERHANG = (0.8, 0.9, 0.35)
INNER_CONTACT = (0.3, 0.5)
# teal spill (the crystal's light on the rock; shells and base rocks): within d -> mix towards SPILL, from the dark
# tone (shells SHELL_INNER, base rocks FOOT_DARK, so every mix key keeps its region's prefix)
# (verifier round 1, C1: (0.15 / 0.3 / 0.45) mixed from the lit body covered 4 % of the crystal's pixel count in the
# front view, median #7B939A, where the sheet's teal rock is 14 % and #596D75: the bands are twice as wide and dark)
# The faces are broad, so the share jumps with the bands: (0.3 / 0.6 / 0.9) gave 45 % (top view 118 %), (0.25 / 0.5 /
# 0.7) 31 %, (0.2 / 0.4 / 0.6) 21 %, (0.18 / 0.35 / 0.52) 9 % in the front view.
SPILL_RAMP = ((0.2, 0.75), (0.4, 0.5), (0.6, 0.25))
# shell feet among the base rocks: hero z below -> mix towards FOOT_DARK
SHELL_FEET = ((0.6, 0.5), (1.3, 0.25))
# broad warm <-> cool weathering on the shells' open faces
WEATHER = dict(scale=0.2, level=0.3, width=0.5, cap=0.75, seed=14063)
# base rocks: crown (above FOOT_CROWN of the rock's height) 25 % towards SHELL, so they blend into the shells; the
# ground-contact row (below FOOT_CONTACT) 25 % towards FOOT_DARK; crevices (within d of another piece) by CREVICE;
# every piece's flat bottom / the hero's floor cap FOOT_DARK
FOOT_CROWN, FOOT_CONTACT, FOOT_MIX = 0.7, 0.3, 0.25
CREVICE = ((0.15, 0.5), (0.3, 0.25))
# Tint: a per-piece level (neighbouring rocks and the two shells differ slightly) x broad mottling
PIECE_TINT = {"Core": 1.0, "ShellLeft": 1.02, "ShellRight": 0.98, "F1": 1.0, "F2": 0.97, "F3": 1.03, "F4": 0.99,
              "F5": 1.02, "F6": 0.97, "B1": 1.01, "B2": 0.97, "B3": 1.03, "B4": 0.98, "B5": 1.02, "rock": 1.0}
MOTTLE = {"rock": dict(amp=0.05, scale=0.45, jitter=0.015, seed=14065),
          "crystal": dict(amp=0.02, scale=0.9, jitter=0.0, seed=14066)}
# K.check's baked-shading test correlates a face's brightness with its facing. The crystal passes (0 on the core);
# the rock trips it only through two position regions the sheet shows, waived with the reason (as M011 / M013):
_FOOT_TONE = ("the flat underside / floor cap is the Base Rock foot tone (the sheet's underside view renders "
              "#6A5F5D, its Base Rock swatch #666262 is that ground-contact tone, not the rocks' body); it is the "
              "ground contact, chosen by position (z = 0 / the part's flat bottom), not by light")
SHADING_OK = {
    "StarstoneNode": _FOOT_TONE + ". With the floor cap at the body tone the hero scores 0.28 (under the gate)",
    "StarstoneShellLeft": _FOOT_TONE + "; its feet among the base rocks go 25-50 % towards it by height (spec §5.6)",
    "StarstoneFootRock": _FOOT_TONE + "; its ground-contact row goes 25 % towards it by height, its crown 25 % "
                                      "towards the shell tone (spec §5.6)",
    "StarstoneShellRight": "the slab's underside and front-lower chamfer row hang over the crystal: the sheet's dark "
                           "cool inner face (#616068 in the front three-quarter, #69686B in the junction close-up) "
                           "by position in the slab's own frame and distance to the crystal, not by light",
}


def _q(t):
    return round(min(1.0, max(0.0, t)) * (STEPS + 1)) / (STEPS + 1)


def _step(d, ramp):
    """The mix of the first (threshold, mix) in ramp with d below the threshold, else 0."""
    for lim, t in ramp:
        if d < lim:
            return t
    return 0.0


def _ladder():
    return ([CORE_DEEP] + [K.mix_key(CORE_DEEP, CORE, t) for t in (0.25, 0.5, 0.75)] + [CORE] +
            [K.mix_key(CORE, CORE_LIGHT, t) for t in (0.25, 0.5, 0.75)] + [CORE_LIGHT])


def _region(key):
    return "crystal" if key.startswith("m014_core") else "shell" if key.startswith("m014_shell") else "foot"


class _Piece:
    """One placed piece: hero build frame -> the part's own build frame, with the part's bounds there."""

    def __init__(self, label, part, m, seed):
        self.label, self.part, self.m = label, part, m
        self.inv = _frame(part) @ m.inverted()
        ps = [_frame(part) @ v.co for v in part.data.vertices]
        self.lo = Vector([min(p[i] for p in ps) for i in range(3)])
        self.hi = Vector([max(p[i] for p in ps) for i in range(3)])
        r = random.Random(seed)
        self.noise_off = Vector((r.uniform(0, 50), r.uniform(0, 50), r.uniform(0, 50)))

    def local(self, c):
        return self.inv @ c

    def norm(self, c):
        q = self.local(c)
        mid, half = (self.lo + self.hi) / 2, (self.hi - self.lo) / 2
        return max(abs(q[i] - mid[i]) / max(half[i], 1e-6) for i in range(3))

    def u(self, c):
        q = self.local(c)
        return (q.z - self.lo.z) / (self.hi.z - self.lo.z)


def _pieces():
    out = {}
    for k, (label, (part, m)) in enumerate(placements().items()):
        out[label] = _Piece(label, bpy.data.objects[part], m, 14070 + k)
    return out


def _trees():
    """BVHs in the hero build frame: the hero's visible crystal surface, its rock surface, and each placed piece."""
    from mathutils.bvhtree import BVHTree
    h = bpy.data.objects["StarstoneNode"]
    off = Vector(h[OFF])
    keys = [(m.get("flintkit_key") or m.name[3:]) for m in h.data.materials]
    vs = [v.co + off for v in h.data.vertices]
    cry = [list(p.vertices) for p in h.data.polygons if _region(keys[p.material_index]) == "crystal"]
    rock = [list(p.vertices) for p in h.data.polygons if _region(keys[p.material_index]) != "crystal"]
    out = {"crystal": BVHTree.FromPolygons(vs, cry), "rock": BVHTree.FromPolygons(vs, rock), "pieces": {}}
    for label, (part, m) in placements().items():
        o = bpy.data.objects[part]
        out["pieces"][label] = BVHTree.FromPolygons([m @ v.co for v in o.data.vertices],
                                                    [list(p.vertices) for p in o.data.polygons])
    return out


ROCK_LABELS = tuple(r[0] for r in ROCKS)
PART_PIECE = {"StarlightCore": "Core", "StarstoneShellLeft": "ShellLeft", "StarstoneShellRight": "ShellRight"}


def _classify(o, p, pieces):
    """Per face: (region, piece, hero-frame centre or None for the generic rock part, on the piece's flat bottom /
    the hero floor)."""
    hero = o.name == "StarstoneNode"
    generic = None
    if o.name == "StarstoneFootRock":
        generic = _Piece("rock", o, Matrix.Identity(4), 14069)
    out = {}
    for f in p.bm.faces:
        reg = _region(p.key(f))
        if hero:
            c = p.at(f)
            labels = ("Core",) if reg == "crystal" else ("ShellLeft", "ShellRight") if reg == "shell" else ROCK_LABELS
            pc = min((pieces[k] for k in labels), key=lambda x: x.norm(c))
            floor = all(abs(v.co.z + p.off.z) < 1e-3 for v in f.verts)
        elif generic:
            pc, c = generic, None
            floor = False
        else:
            pc = pieces[PART_PIECE[o.name]]
            c = pc.m @ f.calc_center_median()
            floor = False
        if not hero and reg != "crystal":
            # a part's flat bottom (in the hero it is below the floor cut)
            m = pc.m if c is not None else Matrix.Identity(4)
            floor = all(pc.local(m @ v.co).z < pc.lo.z + 1e-3 for v in f.verts)
        out[f] = (reg, pc, c if c is not None else f.calc_center_median(), floor, c is not None)
    return out


def _tint(p, f, level, mottle, pos):
    """Tint = the piece's level x broad mottling (patches about 1/scale studs, at pos) x a little per-face jitter."""
    from mathutils import noise
    m = MOTTLE[mottle]
    r = random.Random(m["seed"])
    off = Vector((r.uniform(0, 100), r.uniform(0, 100), r.uniform(0, 100)))
    jit = random.Random(hash((round(pos.x, 3), round(pos.y, 3), round(pos.z, 3)))).uniform(-m["jitter"], m["jitter"]) \
        if m["jitter"] else 0.0
    k = level * (1.0 + m["amp"] * 1.6 * noise.noise(pos * m["scale"] + off) + jit)
    for l in f.loops:
        l[p.tint_layer] = (k, k, k, 1.0)


def _neon_face(o, pc, f):
    """Stage 5: is cap face f on one of the NEON_FACETS (matched by its normal in the core part's own frame, so the
    hero and the StarlightCore part glow on the same facets)? The other cap faces take the crystal ladder."""
    n = f.normal if o.name == "StarstoneNode" else pc.m.to_3x3() @ f.normal
    n = (pc.inv.to_3x3() @ n).normalized()
    return any(n.angle(Vector(k).normalized()) < math.radians(NEON_TOL) for k in NEON_FACETS)


def colour(o, pieces=None, trees=None):
    """Stage 4 on a finished M014 object (hero or part). Returns the face count per key."""
    pieces = pieces or _pieces()
    trees = trees or _trees()
    p = m011._Paint(o, off=o[OFF])
    cls = _classify(o, p, pieces)
    lad = _ladder()
    nf_c = K.noise_field(scale=CRYS_SCALE, seed=CRYS_SEED)
    nf_w = K.noise_field(scale=WEATHER["scale"], seed=WEATHER["seed"])
    for f, (reg, pc, c, floor, framed) in cls.items():
        if reg == "crystal":
            q = pc.local(c)
            if not (p.key(f) == CORE_GLOW and _neon_face(o, pc, f)):
                mid, half = (pc.lo + pc.hi) / 2, (pc.hi - pc.lo) / 2
                u = (pc.u(c) + CRYS_LATERAL * -(q.x - mid.x) / half.x + CRYS_NOISE * nf_c(q))
                if u < CRYS_DEEP_BAND[1]:
                    i = round(_q((u - CRYS_DEEP_BAND[0]) / (CRYS_DEEP_BAND[1] - CRYS_DEEP_BAND[0])) * 4)
                else:
                    i = 4 + round(_q((u - CRYS_LIGHT_BAND[0]) / (CRYS_LIGHT_BAND[1] - CRYS_LIGHT_BAND[0])) * 4)
                d = trees["rock"].find_nearest(c)[3]
                for lim, top in CRYS_CONTACT:
                    if d is not None and d < lim:
                        i = min(i, top)
                        break
                f.material_index = p._mi(lad[i])
            _tint(p, f, PIECE_TINT["Core"], "crystal", q)
            continue
        if floor:
            f.material_index = p._mi(FOOT_DARK)
            _tint(p, f, PIECE_TINT.get(pc.label, 1.0), "rock", pc.local(c) + pc.noise_off)
            continue
        d = trees["crystal"].find_nearest(c)[3] if framed else 9.0
        ts = _step(d, SPILL_RAMP)
        if reg == "shell":
            q = pc.local(c)
            if pc.label == "ShellRight":
                fz = (q.z - pc.lo.z) / (pc.hi.z - pc.lo.z)
                fy = (q.y - pc.lo.y) / (pc.hi.y - pc.lo.y)
                over = (fy > OVERHANG[0] and fz < OVERHANG[1]) or fz < OVERHANG[2]
                ti = _step(d, INNER) if over else 0.0
            else:
                ti = INNER_CONTACT[1] if d < INNER_CONTACT[0] else 0.0
            tf = _step(c.z, SHELL_FEET)
            if ts:
                key = K.mix_key(SHELL_INNER, SPILL, ts)
            elif ti:
                key = K.mix_key(SHELL, SHELL_INNER, ti)
            elif tf:
                key = K.mix_key(SHELL, FOOT_DARK, tf)
            else:
                tc = min(WEATHER["cap"], _q((nf_w(c) - (WEATHER["level"] - WEATHER["width"] / 2)) / WEATHER["width"]))
                key = K.mix_key(SHELL, SHELL_COOL, tc)
            f.material_index = p._mi(key)
            _tint(p, f, PIECE_TINT[pc.label], "rock", c)
            continue
        # base rock
        u = pc.u(c)         # (the generic rock part's "hero frame" is its own mesh frame)
        crev = 0.0
        if framed:
            dn = min(t.find_nearest(c)[3] or 9.0 for k, t in trees["pieces"].items() if k != pc.label)
            crev = _step(dn, CREVICE)
        if ts:
            key = K.mix_key(FOOT_DARK, SPILL, ts)
        elif u > FOOT_CROWN and not crev:
            key = K.mix_key(FOOT, SHELL, FOOT_MIX)
        else:
            key = K.mix_key(FOOT, FOOT_DARK, max(crev, FOOT_MIX if u < FOOT_CONTACT else 0.0))
        f.material_index = p._mi(key)
        _tint(p, f, PIECE_TINT.get(pc.label, 1.0), "rock", pc.local(c) + pc.noise_off)
    counts = {}
    for f in p.bm.faces:
        counts[p.key(f)] = counts.get(p.key(f), 0) + 1
    p.done()
    _crystal_spec()
    return counts


def colour_all(objs=None):
    """colour() on the hero first (it carries the placeholder keys the trees are built from), then each part."""
    objs = objs or [bpy.data.objects[n] for n in ("StarstoneNode", "StarlightCore", "StarstoneShellLeft",
                                                    "StarstoneShellRight", "StarstoneFootRock")]
    pieces = _pieces()
    trees = _trees()
    out = {o.name: colour(o, pieces, trees) for o in objs}
    for o in objs:
        if o.name in SHADING_OK:
            o["kit_shading_ok"] = SHADING_OK[o.name]
        elif "kit_shading_ok" in o:
            del o["kit_shading_ok"]
    return out


# ---- stage 4 measurement: our renders against the sheet, per region ---------------------------------------------------
LABEL_RGB = {"cap": (1.0, 0.0, 0.0), "crystal": (0.0, 0.0, 1.0), "ShellLeft": (0.0, 1.0, 0.0),
             "ShellRight": (1.0, 1.0, 0.0), "foot": (1.0, 0.0, 1.0), "spill": (0.0, 1.0, 1.0)}


def _labels(o):
    """Per polygon index: the stage 4 region label (cap, crystal, ShellLeft, ShellRight, foot; any rock face with a
    spill key: spill)."""
    p = m011._Paint(o, off=o[OFF])
    cls = _classify(o, p, _pieces())
    out = {}
    for f, (reg, pc, c, floor, framed) in cls.items():
        out[f.index] = ("cap" if p.key(f) == CORE_GLOW else "crystal") if reg == "crystal" else \
            "spill" if "spill" in p.key(f) else pc.label if reg == "shell" else "foot"
    p.bm.free()
    return out


def _label_render(o, path, az, el):
    """o rendered with flat emission label colours (same verts, so the same framing as its colour render)."""
    lab = _labels(o)
    me = o.data.copy()
    tmp = bpy.data.objects.new("_m014_labels", me)
    o.users_collection[0].objects.link(tmp)
    tmp.matrix_world = o.matrix_world
    mats = []
    try:
        me.materials.clear()
        for name, rgb in LABEL_RGB.items():
            m = bpy.data.materials.new("_m014_label_" + name)
            m.use_nodes = True
            nt = m.node_tree
            nt.nodes.clear()
            em = nt.nodes.new("ShaderNodeEmission")
            em.inputs["Color"].default_value = (*rgb, 1.0)
            em.inputs["Strength"].default_value = 1.0
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
    """Label image -> {label: bool mask}, eroded by one pixel (no anti-aliased edges)."""
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


def _hexs(c):
    return "#" + "".join(f"{int(round(x)):02X}" for x in c)


def _stats(sel):
    """median / lit quartile / shade quartile (by mean brightness) of an (n, 3) sRGB 0-255 array."""
    if len(sel) < 20:
        return None
    lum = sel.mean(axis=1)
    lo, hi = np.percentile(lum, 25), np.percentile(lum, 75)
    return (_hexs(np.median(sel, axis=0)), _hexs(np.median(sel[lum >= hi], axis=0)),
            _hexs(np.median(sel[lum <= lo], axis=0)), int(len(sel)))


def _bands(img, mask, n=5):
    """Medians of mask's pixels in n height bands of its own bbox (top band first). img rows top-down."""
    rows = np.nonzero(mask.any(axis=1))[0]
    if not len(rows):
        return []
    r0, r1 = rows.min(), rows.max() + 1
    out = []
    for k in range(n):
        a, b = r0 + (r1 - r0) * k // n, r0 + (r1 - r0) * (k + 1) // n
        sel = img[a:b][mask[a:b]]
        out.append(_hexs(np.median(sel, axis=0)) if len(sel) else None)
    return out


SHEET_PATH = "D:/Projects/Roblox/RBLX-Flintborn/art/blender/assets/references/014.png"
# sheet boxes per compared view (M014_spec.md §1); f34 is the sheet's "front three-quarter" = a front view
SHEET_BOXES = {"front": (18, 525, 282, 718), "f34": (40, 106, 530, 430), "side": (287, 525, 508, 718),
               "rear": (512, 525, 768, 718), "top": (776, 522, 995, 718), "exploded_core": (285, 860, 420, 1065)}
REPORT_VIEWS = {"front_sheet": (0, 13), "side_sheet": (-90, 13), "rear_sheet": (180, 13), "top_el75": (0, 75),
                "front34": (-28, 12)}


def _top_down(px):
    return (np.clip(px[::-1, :, :3], 0, 1) * 255).astype(np.float64)


def sheet_stats():
    """The sheet's crystal (cyan mask) and rock (rock mask) per view box: stats and crystal bands."""
    img = _top_down(K.NS["KIT"]["load_px"](SHEET_PATH))
    out = {}
    for v, (x0, y0, x1, y1) in SHEET_BOXES.items():
        c = img[y0:y1, x0:x1]
        r, g, b = c[..., 0], c[..., 1], c[..., 2]
        mx, mn = c.max(axis=2), c.min(axis=2)
        sat = (mx - mn) / np.maximum(mx, 1)
        cyan = (mx > 90) & (b > r + 45) & (g > r + 35) & (sat > 0.28)
        paper = np.abs(c - np.array([0xF3, 0xED, 0xE5])).max(axis=2) <= 16
        rock = ~paper & (mx < 235) & (sat < 0.25) & ~cyan
        out[v] = {"crystal": _stats(c[cyan]), "rock": _stats(c[rock]), "crystal_bands": _bands(c, cyan),
                  "rock_bands": _bands(c, rock)}
    return out


# §5.2's sheet regions, each compared in our render of the same view: (name, our view, sheet view bbox, box, mask)
SHEET_BBOX = {"f34": (45, 107, 522, 428), "front": (18, 531, 277, 715), "side": (295, 525, 493, 717),
              "rear": (512, 528, 760, 716), "top": (792, 526, 981, 715)}
OUR_VIEW = {"f34": "front_sheet", "front": "front_sheet", "side": "side_sheet", "rear": "rear_sheet",
            "top": "top_el75"}
REGIONS = (("crystal f34 cap", "f34", (265, 185, 370, 265), "crystal"),
           ("crystal f34 belt", "f34", (280, 265, 395, 315), "crystal"),
           ("crystal f34 taper", "f34", (290, 315, 390, 363), "crystal"),
           ("crystal side", "side", (408, 563, 462, 677), "crystal"),
           ("crystal top", "top", (850, 570, 931, 665), "crystal"),
           ("left shell f34 lit face", "f34", (170, 170, 250, 300), "rock"),
           ("left shell f34 shade face", "f34", (105, 200, 160, 320), "rock"),
           ("right shell f34 roof", "f34", (320, 120, 440, 220), "rock"),
           ("inner face above the crystal", "f34", (240, 150, 300, 200), "rock"),
           ("rock right of the crystal", "f34", (400, 180, 440, 280), "rock"),
           ("base rock f34 front centre", "f34", (225, 350, 385, 420), "rock"),
           ("base rock f34 right dome", "f34", (375, 295, 470, 400), "rock"),
           ("shells front", "front", (40, 535, 250, 650), "rock"),
           ("base rocks front", "front", (20, 655, 277, 715), "rock"),
           ("shell side", "side", (320, 530, 450, 650), "rock"),
           ("base rocks side", "side", (295, 655, 493, 717), "rock"),
           ("shells rear", "rear", (540, 530, 740, 640), "rock"),
           ("base rocks rear", "rear", (512, 650, 760, 716), "rock"))


def _sheet_masks(c):
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    mx, mn = c.max(axis=2), c.min(axis=2)
    sat = (mx - mn) / np.maximum(mx, 1)
    cyan = (mx > 90) & (b > r + 45) & (g > r + 35) & (sat > 0.28)
    paper = np.abs(c - np.array([0xF3, 0xED, 0xE5])).max(axis=2) <= 16
    return {"crystal": cyan, "rock": ~paper & (mx < 235) & (sat < 0.25) & ~cyan}


def regions(out_dir=None):
    """REGIONS: the sheet box against the same box mapped through each view's model bbox into our render (from
    report()'s files). Returns [(name, sheet stats, our stats)]; plus the spill: the sheet's teal rock pixels within
    5 px of the crystal (f34) against our spill-key pixels (front_sheet)."""
    out_dir = out_dir or K.TEMP_ROOT + "m014_s4"
    kit = K.NS["KIT"]
    sheet = _top_down(kit["load_px"](SHEET_PATH))
    ours = {}
    for v in set(OUR_VIEW.values()):
        img = _top_down(kit["load_px"](f"{out_dir}/{v}.png"))
        mk = _label_mask(kit["load_px"](f"{out_dir}/{v}_lab.png")[::-1])
        cr = mk["cap"] | mk["crystal"]
        rk = mk["ShellLeft"] | mk["ShellRight"] | mk["foot"] | mk["spill"]
        rows, cols = np.nonzero((cr | rk).any(axis=1))[0], np.nonzero((cr | rk).any(axis=0))[0]
        ours[v] = (img, {"crystal": cr, "rock": rk, "spill": mk["spill"]},
                   (cols.min(), rows.min(), cols.max() + 1, rows.max() + 1))
    out = []
    for name, sv, (x0, y0, x1, y1), kind in REGIONS:
        c = sheet[y0:y1, x0:x1]
        s = _stats(c[_sheet_masks(c)[kind]])
        bx0, by0, bx1, by1 = SHEET_BBOX[sv]
        img, mk, (ox0, oy0, ox1, oy1) = ours[OUR_VIEW[sv]]
        fx = lambda x: int(round(ox0 + (x - bx0) / (bx1 - bx0) * (ox1 - ox0)))
        fy = lambda y: int(round(oy0 + (y - by0) / (by1 - by0) * (oy1 - oy0)))
        a, b, cc, d = fx(x0), fy(y0), fx(x1), fy(y1)
        out.append((name, s, _stats(img[b:d, a:cc][mk[kind][b:d, a:cc]])))
    # spill: sheet rock-ish pixels with a teal cast next to the crystal (f34)
    x0, y0, x1, y1 = SHEET_BOXES["f34"]
    c = sheet[y0:y1, x0:x1]
    m = _sheet_masks(c)
    near = np.zeros_like(m["crystal"])
    for dy in range(-5, 6):
        for dx in range(-5, 6):
            near |= np.roll(np.roll(m["crystal"], dy, axis=0), dx, axis=1)
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    teal = near & ~m["crystal"] & (b > r + 8) & (g > r)
    img, mk, _ = ours["front_sheet"]
    out.append(("teal spill (sheet f34 / our front)", _stats(c[teal]), _stats(img[mk["spill"]])))
    return out


def report(views=None, out_dir=None, light=True):
    """Render the hero (colour + labels) at the compare views and measure each region: crystal (all, cap, bands),
    left shell, right shell, base rocks, spill faces. With light, the hero's sockets are realised as lights only (the
    crystal_glow PointLight; no particle stand-ins), as the game shows it. Returns {view: {region: (median, lit,
    shade, n)}}."""
    import os
    h = bpy.data.objects["StarstoneNode"]
    out_dir = out_dir or K.TEMP_ROOT + "m014_s4"
    os.makedirs(out_dir, exist_ok=True)
    kit = K.NS["KIT"]
    old = kit["CELL"]
    kit["CELL"] = (480, 400)
    out = {}
    sc = bpy.context.scene
    if light:
        kit["vfx"].realize(sc, [h], particles=False)
    try:
        for v, (az, el) in (views or REPORT_VIEWS).items():
            pc = kit["render_group"]([h], f"{out_dir}/{v}.png", az, el)
            pl = _label_render(h, f"{out_dir}/{v}_lab.png", az, el)
            img = _top_down(kit["load_px"](pc))
            masks = _label_mask(kit["load_px"](pl)[::-1])
            cr = masks["cap"] | masks["crystal"]
            rk = masks["ShellLeft"] | masks["ShellRight"] | masks["foot"]
            r = {k: _stats(img[m]) for k, m in masks.items()}
            r["crystal_all"] = _stats(img[cr])
            r["rock_all"] = _stats(img[rk])
            r["shells"] = _stats(img[masks["ShellLeft"] | masks["ShellRight"]])
            r["crystal_bands"] = _bands(img, cr)
            r["rock_bands"] = _bands(img, rk)
            r["share"] = round(float(cr.sum()) / max(1, int((cr | rk).sum())), 3)
            r["spill_share"] = round(float(masks["spill"].sum()) / max(1, int(cr.sum())), 3)   # of crystal pixels
            lum = img[cr].mean(axis=1) if cr.any() else np.zeros(1)
            r["shade_lit"] = round(float(np.percentile(lum, 12.5) / max(np.percentile(lum, 87.5), 1e-3)), 2)
            # clipped (g or b >= 254) share of the solid crystal's pixels (the Neon cap renders its hex unlit)
            nc = masks["crystal"]
            r["clip"] = round(float((img[nc][:, 1:] >= 254).any(axis=1).mean()), 3) if nc.any() else 0.0
            out[v] = r
    finally:
        kit["CELL"] = old
        if light:
            kit["vfx"].clear(sc)
    return out


# ---- stages 5+6: light and VFX sockets on the hero (M014_spec.md §6 and "Stage 5+6") -------------------------------
# All points are in the build frame (front -Y, ground z 0); _vfx() adds them to the FINISHED hero at
# build point - h[OFF] (hero-local studs), so the glint boxes are fitted to the final mesh, not a probe.
# crystal_glow: one steady teal PointLight in the open in front of the crystal's belt, above F1. Gives the self-lit
# shade side and the teal spill in Roblox, which keys alone can't guarantee under in-game light. The study's
# (0.9, -3.6, 3.6) is 0.72 stud from the belt (0.80 for the preview light, which sits 0.25 above its socket).
# Tried with vfx on (report(), front / f34): at (0.9, -3.8, 3.6) (0.91 clear) brightness 1.0 the belt's lower bands
# went #3DD5E3 / #27BBCE -> #40FFFF / #28D6EE (sheet #32C9D6 / #1CAEBE), a hot patch on the facets facing the light;
# 0.6 there still #3EF1FF. Here, 1.80 stud from the nearest surface (the belt), brightness 0.7: #3EEDFE / #27CAE1,
# spread evenly; the spill median #7D8D99 -> #7E8E9B (sheet #79858E), the rock +1-2 levels. Any teal light lifts the
# crystal's g / b, so it stays soft. Shadows on, so the shells keep it off the rear.
# (verifier round 1, A1: 0.7 -> 0.45, so the light no longer lifts the belt into clipped g / b; stage 4's crystal keys
# are refitted with this light on)
CRYSTAL_LIGHT = dict(pos=(0.9, -4.6, 4.0), color="#6EF2F8", brightness=0.45, range=12.0, shadows=True)
# crystal_halo: the sheet's "Starlight Glow" panel (a pale cyan starburst behind the whole model, ~1.3x its width).
# Behind the crystal's centre, inside the rock, so the rock in front hides the billboard's middle and the glow shows
# round the silhouette. The kind's defaults are this sheet's values (vfx.KINDS["crystal_halo"]).
# (verifier round 1, C2: at (0.6, -0.6, 4.2) the socket sat 0.86 inside the rock and its 12-14 stud camera-facing
# billboards cut through the shells. vfx.py's emitter spec has no ZOffset key (the README's spec -> ParticleEmitter
# table has none, and the exporter passes the spec through unchanged), so the socket moved instead: behind the model,
# outside the rock (3.5 studs clear; the model's back is at y 4.1), 2.4 behind its back. From the front (az 0, el 4-13)
# and the front three-quarter (az -28, el 12) every hero vertex inside the largest billboard (14 x 14) is in front of
# it (margins 1.6 / 2.2 / 0.1 studs), so the rock hides the middle and the glow shows round the silhouette; seen
# from el 13 it centres between the crystal's middle and its top (the sheet's "upper half"). From the rear and from
# above it sits in front of / over the rock: a faint additive veil (transparency >= 0.82), as any billboard there.)
# (final fix, verifier round 2: from the rear the 12-14 stud billboards at (0.6, 6.5, 3.4), behind the model, sat in
# front of the rock as a cyan haze. The crystal_halo kind places its socket inside the asset: now inside the hero's
# solid right behind the crystal, at its mid-height, 0.74 stud from the nearest surface (ray parity: inside), so the
# rock hides the billboard's middle from every side and the glow shows round the silhouette.)
HALO_POS = (0.9, 0.3, 3.4)
# ore_glint: the sheet's pale ridge glints, on three crystal ridges (hero edges between two crystal faces), each
# (ridge end a, ridge end b, where along it, rate / s, peak size). a and b snap to the nearest hero crystal vertices.
# The box is the ridge from t - GLINT_REACH to t + GLINT_REACH studs along it, padded by GLINT_PAD, so every spawn
# point is within about 0.3 stud of the ridge. (The cap's apex itself is in the right shell's union crease, so the
# cap glint sits a quarter of the way down the cap's main ridge, clear of the slab.)
# (stage 1 fixes: the ends are given in the core's own construction frame - the ridge's +X end, the +X / back
# shoulder points, the left belt ridge - and placed through _core_matrix(), so they follow any change of the core's
# placement; round 1 gave them in the hero frame.)
# (final fix, verifier round 2: the ends are the kite gem's named corners (CORE_PTS) - the top edge T-R, the front
# ridge F-R from the front corner up to the right shoulder (the sheet's brightest ridge), and the left ridge F-L1.)
GLINTS = (("cap ridge", "T", "R", 0.4, 0.5, 0.6),
          ("shoulder ridge", "F", "R", 0.7, 0.35, 0.45),
          ("left ridge", "F", "L1", 0.5, 0.25, 0.45))
GLINT_REACH = 0.3       # (0.4 left the cap box's corners 0.43 off the crystal: the cap ridge runs diagonally)
GLINT_PAD = 0.06
GLINT = {"name": "Glint", "texture": "spark_diamond", "color": ["#F2FFFF", "#8CF8FD"], "transparency": [0.1, 1.0],
         "lifetime": [0.5, 0.8], "speed": [0, 0], "spread": 0, "light_emission": 1.0, "rotation": [0, 90]}


def _glint_boxes(h):
    """[(label, lo, hi, rate, size)] in the build frame, fitted to h's crystal ridges (GLINTS)."""
    off = Vector(h[OFF])
    mats = [m.name if m else "" for m in h.data.materials]
    bm = bmesh.new()
    bm.from_mesh(h.data)
    cry = [v for v in bm.verts if any("_core" in mats[f.material_index] for f in v.link_faces)]
    out = []
    cm = _core_matrix()
    for label, a, b, t, rate, size in GLINTS:
        a, b = (cm @ (core_point(x) if isinstance(x, str) else Vector(x)) for x in (a, b))
        va = min(cry, key=lambda v: (v.co + off - a).length)
        vb = min(cry, key=lambda v: (v.co + off - b).length)
        pa, pb = va.co + off, vb.co + off
        n = (pb - pa).length
        s0, s1 = max(0.0, t - GLINT_REACH / n), min(1.0, t + GLINT_REACH / n)
        pts = [pa.lerp(pb, s0), pa.lerp(pb, s1)]
        lo = Vector([min(p[i] for p in pts) - GLINT_PAD for i in range(3)])
        hi = Vector([max(p[i] for p in pts) + GLINT_PAD for i in range(3)])
        out.append((label, lo, hi, rate, size))
    bm.free()
    return out


def _vfx(h):
    """Stages 5+6: the hero's sockets, light first, then the halo and the glints. Returns the sockets."""
    off = Vector(h[OFF])
    light = {k: CRYSTAL_LIGHT[k] for k in ("color", "brightness", "range", "shadows")}
    light["flicker"] = False
    made = [K.socket(h, "crystal_glow", Vector(CRYSTAL_LIGHT["pos"]) - off, light=light),
            K.socket(h, "crystal_halo", Vector(HALO_POS) - off)]
    for label, lo, hi, rate, size in _glint_boxes(h):
        d = hi - lo
        em = dict(GLINT, rate=rate, size=[0, size, 0],
                  shape=[round(d.x, 2), round(d.z, 2), round(d.y, 2)])    # Roblox XYZ: x, height, depth
        made.append(K.socket(h, "ore_glint", Vector([round(c, 3) for c in (lo + hi) / 2]) - off, emitters=[em]))
    return made


def build(render=True):
    M.coll(NUM, TITLE)
    palette()
    objs, cleaned = {}, {}
    for name, fn in PARTS:
        o = M.mk(SHEET, name, fn, subject=TITLE, role="part", notes=NOTES[name], budget=1000, collision="hull")
        o[OFF] = list(M._build_offset(fn))
        if fn is shell_right:
            M.union_loose(o)
            cleaned[name] = _clean_mesh(o, ())      # no flat plane on the slab
        _finish(o)
        cleaned.setdefault(name, {})["polish"] = _polish(o)
        objs[name] = o
    h = M.mk(SHEET, "StarstoneNode", hero, subject=TITLE, role="hero", notes=NOTES["StarstoneNode"], budget=4000,
             collision="hull")
    hoff = M._build_offset(hero)
    h[OFF] = list(hoff)
    M.union_loose(h)
    _floor_cut(h, -hoff.z)
    h[OFF] = list(Vector((hoff.x, hoff.y, 0.0)))
    cleaned["StarstoneNode"] = _clean_mesh(h, (0.0,))
    _finish(h)
    cleaned["StarstoneNode"]["polish"] = _polish(h)
    sockets = _vfx(h)            # stages 5+6, on the finished hero (the parts carry none)
    order = [h] + [objs[n] for n, _ in PARTS]
    # stage 4: the hero first (the trees come from its placeholder keys), then each part, by the same fields
    coloured = colour_all(order)
    M.display(NUM, order, TITLE)
    dropped = _drop_unused(order)
    out = {"audit": [{k: M.audit(o)[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges",
                                                     "boundary_edges", "normals", "ngons", "materials")}
                     for o in order],
           "thin": {o.name: m012._thin(o, 3.0) for o in order},
           "facets": {"core": CORE_INFO.get("facets"), "shell_left": LS_INFO.get("facets"),
                      "shell_right": RS_INFO.get("facets"), "foot_rock": FOOT_INFO.get("facets")},
           "cleaned": cleaned, "dropped": dropped, "gaps": _gaps(), "colour": coloured, "problems": K.check(order),
           "shading": {o.name: o.get("kit_baked_shading") for o in order}}
    out["self_hits"] = {o.name: _self_hits(o) for o in order}
    out["problems"] += [f"{n}: {c} crossing face pairs {w}" for n, (c, w) in out["self_hits"].items() if c]
    # stage 3: the final UV layer of every object (no overlaps or flips allowed)
    out["uv"] = {o.name: M.uv_stats(o) for o in order}
    out["problems"] += [f"{n}: {s['overlap_pairs']} UV overlaps, {s['flipped']} flipped" for n, s in out["uv"].items()
                        if s["overlap_pairs"] or s["flipped"]]
    out["measure"] = measure(h)
    out["sockets"] = [(s.name, s["vfx_kind"], [round(c, 3) for c in s.location]) for s in sockets]
    if render:
        out["views"] = render_views(order)
    return out


def _drop_unused(objs):
    names = {o.name for o in objs}
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.split(".")[0] in names]
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m014_")]
    out = {"meshes": len(meshes), "materials": sorted(m.name for m in mats)}
    for m in meshes:
        bpy.data.meshes.remove(m)
    for m in mats:
        bpy.data.materials.remove(m)
    for o in objs:
        if o.data.name != o.name and o.name not in bpy.data.meshes:
            o.data.name = o.name
    return out


# exploded shot, as the sheet lays it out: the base-rock ring in place, the left shell lifted up and out to the left,
# the core lifted straight up out of the cleft, the right shell lifted up and out to the right (each a temporary
# linked copy of its part at its hero placement, moved by (dx, dy, dz))
# (round 1's (-2.2, 0, 3.2) / (0.4, -0.6, 5.2) / (2.6, 0.6, 4.2) left the core touching the right shell in the shot)
EXPLODE = {"ShellLeft": (-3.6, -0.4, 3.8), "Core": (0.0, -1.4, 6.4), "ShellRight": (6.2, 0.2, 4.6)}


def preview():
    """Iteration shots of the hero at the sheet's angles only (front, side with the front on the right, rear, top
    at 75, and the kit's front three-quarter), into the model's render folder (M014_views.png is then this set
    until the next full build)."""
    h = bpy.data.objects["StarstoneNode"]
    return _views(NUM, [h], names=("front34",), extra={
        "front_sheet": ([h], 0, 13), "side_sheet": ([h], -90, 13), "rear_sheet": ([h], 180, 13),
        "top_el75": ([h], 0, 75)}, vfx=False)


def _views(*a, **kw):
    """M.views with the crystal_halo's preview shown only in shots whose name contains "halo". Its stand-in is a few
    faceted blobs about 10 studs across that veil the whole model (a Roblox billboard behind the crystal, depth-tested
    against the rock, does not), so the compare set is rendered without it and one extra shot shows it."""
    kit = K.NS["KIT"]
    rg = kit["render_group"]

    def render_group(group, path, *ra, **rkw):
        show = "halo" in path.rsplit("/", 1)[-1]
        for o in bpy.data.objects:
            if o.name.startswith(kit["vfx"].PREVIEW_PREFIX) and "crystal_halo" in str(o.get("vfx_socket", "")):
                o.hide_render = not show
        return rg(group, path, *ra, **rkw)
    kit["render_group"] = render_group
    try:
        return M.views(*a, **kw)
    finally:
        kit["render_group"] = rg


def render_views(objs):
    h = objs[0]
    parts = objs[1:]
    saved = M.explode(parts, {})
    shown = []
    try:
        x0, y0 = h.location.x + 40, h.location.y
        for name, (part, m) in placements().items():
            src = bpy.data.objects[part]
            c = bpy.data.objects.new(f"_m014_expl_{name}", src.data)
            src.users_collection[0].objects.link(c)
            c.matrix_world = Matrix.Translation(Vector((x0, y0, 0.0)) + Vector(EXPLODE.get(name, (0, 0, 0)))) @ m
            shown.append(c)
        bpy.context.view_layer.update()
        extra = {"front_sheet": ([h], 0, 13), "side_sheet": ([h], -90, 13), "side_right_el13": ([h], 90, 13),
                 "rear_sheet": ([h], 180, 13), "top_el75": ([h], 0, 75), "exploded": (shown, -12, 14)}
        for o in parts:
            extra["part_" + o.name.replace("Starstone", "").replace("Starlight", "").lower()] = ([o], -25, 18)
        extra["front34_halo"] = ([h],) + M.VIEWS["front34"]      # the one shot with the halo's stand-in
        return _views(NUM, [h], extra=extra)
    finally:
        for c in shown:
            bpy.data.objects.remove(c, do_unlink=True)
        M.restore(saved)
        M.display(NUM, objs, TITLE)
