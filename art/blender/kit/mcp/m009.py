"""009 Iron Meteor (references/009.png): a big dark faceted meteorite split into thick shell pieces along jagged
seams. The seams are real gaps through the shell: their walls step down from a dark lip to an orange floor, which
is the glowing metal core below. A smaller lobe bulges out at the front left, and a ring of pale impact rocks sits
round the foot.

    import importlib, kit_models, m009; importlib.reload(kit_models); importlib.reload(m009); m009.build()

Stage 1 (rework, see M009_spec.md). Everything is built in one shared build frame (studs; front is -Y, ground
z = 0). Directions are measured from the main mass's centre C0 with _dir(az, el): az -90 is the front, 0 is +X
(right), 90 the back and 180 the left.

- Outer: two convex hulls, Main and Lobe, unioned. Their facets are the shell's outside.
- Core (IronMeteorCore): the Main hull inset by T along every facet plane, so the shell is exactly T thick
  everywhere on the main mass (the lobe bulge is thicker, and solid down to the core).
- Seam network: four meridian seams (lobe seam, front-right, back-right, back-left) and a crown ring. Each seam is a
  polyline of nodes (az, el, G); G is the lip-to-lip gap in studs, and G <= 0 means closed (the pieces fuse there).
- Open seams are cut by tube cutters: the cross-section is a gap G wide at the surface and 0.55 G at the floor, with
  edge rows at 0.25 and 0.55 of the shell thickness (the lip, ember and floor bands stage 4 colours) and a lip
  chamfer on the main side. Each tube goes through the shell into the core, and ends taper to a line.
- Shell pieces: outer, intersected with each piece's sector cone (bounded by the seam centre lines), minus the
  cutters and minus the core grown by CORE_GAP. Six pieces: Crown, Lobe, Front, Right, Back and BackLeft (the strip
  between the back-left seam and the lobe's back crease, LOBE_BACK; verifier round 1). Only Lobe is
  exported (IronMeteorShellPiece; the chunky one, as the sheet's Shell Piece Detail). The others are temporary
  objects for the exploded render.
- Hero (IronMeteorDeposit): outer minus the cutters, plus the core, floor-cut at z = 0 (the floor shows the core's
  disc ringed by the shell's cut), plus the impact rim: transformed copies of IronMeteorImpactRock. The hero uses
  the same outer, cutters and core as the pieces, so each piece is exactly a sub-volume of the hero's shell. It is
  not literally pasted from the five pieces, because neighbours meet at the closed seams with coincident cut faces
  (the exact-boolean pitfall); see M009_spec.md.

Stage 4 (palette, TARGETS, calibrate, colour_all): calibrated keys painted by build-frame position fields on the
finished meshes. The crack grades by depth through the cutters' face bands: a dark solid lip, a deep red ember band,
orange walls and a hot floor (the last three Neon, unshaded in previews as in Roblox). The shell takes broad facet
patches (dark .. plain .. light), soot along the open seams and a darker foot; the rocks broad patches; Tint per facet.

Stages 5+6 (SEAM_LIGHT, HEAT_FX, EMBER_FX, SOCKETS, _vfx): the glow is the four Neon keys; the hero carries three
heat_glow sockets (faint shimmer: the lobe seam's jog, with the one warm shadowed PointLight, its upper run and the
back-right seam) and two sparse embers sockets (the lobe seam's upper run, the front-right seam's top), all just
outside the seam lips.

A kit sheet owns `IronMeteor`, so the hero is `IronMeteorDeposit`.
"""
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_line_line
from mathutils.kdtree import KDTree

import kit_mcp as K
import kit_models as M
import m011
import m012

NUM, TITLE, SHEET = 9, "Iron Meteor", "M009"
# placeholder keys per region (stage 4 calibrates them)
SHELL, SHELL_CUT = "m009_shell", "m009_shell_cut"           # outside; shell-thickness cut faces and floor ring
LIP, EMBER = "m009_seam_lip", "m009_seam_ember"             # seam wall bands: 0-0.25 T, 0.25-0.55 T
CORE, HOT = "m009_core", "m009_core_hot"                    # wall band 0.55 T-T, core part, floor disc; seam floor
IMPACT = "m009_impact"
# stage 4: the patch and depth keys
SHELL_LIGHT, SHELL_DARK = "m009_shell_light", "m009_shell_dark"     # broad facet patches, soot and ground band
CORE_DEEP = "m009_core_deep"                # the core part's lower facets, the shell piece's inner (hollow) face,
                                            # the hero's floor disc (the core's underside)
SEAM_DEEP = "m009_seam_deep"                # a deep red glow: the lobe seam's walls below the lip (SEAM_COOL)
IMPACT_LIGHT, IMPACT_DARK = "m009_impact_light", "m009_impact_dark"

# ---- masses (build frame) -----------------------------------------------------------------------------------------
# (a broad, squat boulder, as the sheet's hero view: wider than tall, the lobe a big chunky block of few facets)
C0 = Vector((0.5, 0.6, 3.3))
MAIN = dict(centre=C0, radii=(4.8, 4.7, 4.6), seed=9001, n=40, top=0.97, wobble=(0.9, 1.07))
LOBE = dict(centre=Vector((-3.1, -1.5, 2.35)), radii=(2.9, 2.65, 2.6), seed=9002, n=18, top=1.0, wobble=(0.93, 1.05))
T = 0.6                     # shell thickness on the main mass
CORE_GAP = 0.05             # the pieces' hollow is this much smaller than the core (they overlap it, so the shell
                            # piece sits tight on the core; the hero's shell is exactly T)
FLOOR_DEEP = 0.4            # the cutters reach this far into the core
FLOOR_FRAC = 0.55           # gap width at the floor, as a share of the lip-to-lip gap G
ROWS = (0.55, 0.25)         # wall edge rows, as fractions of the local shell thickness (floor | ember | lip bands)
CHAMFER = (0.12, 0.08)      # the main-side lip's chamfer: depth (studs) and extra set-back at the surface (G >= 0.3)
STEP = 6.0                  # seams are resampled to nodes at most this many degrees apart
BOTTOM = -72.0              # the pieces' sectors end at this elevation (below ground everywhere)

# ---- seam network: nodes (az, el, G), az continuous along each seam ------------------------------------------------
# lobe seam: the far-left closed end, the upper run over the lobe's top (crown | lobe), the corner at L_JUNCTION,
# then the descent down the crease between the lobe and the main mass (front | lobe), open into the ground
# (the upper run follows the crease along the lobe's top, el 15-18 from C0, from its middle to its front right
# corner; the descent the crease down its front right side, az 230-243, drifting onto the main mass below el -15 as
# the sheet's front view does)
LOBE_UPPER = ((204, 14, 0.0), (212, 17, 0.25), (222, 18, 0.32), (230, 15, 0.40))
LOBE_DESCENT = ((230, 15, 0.40), (236, 8, 0.42), (242, 3, 0.55), (238, -3, 0.45), (243, -11, 0.42),
                (249, -19, 0.55), (256, -28, 0.5), (258, -45, 0.5), (258, BOTTOM, 0.5))
# the other three: front-right about az -55, back-right about 50 and back-left about 128 (the sheet's front, hero,
# rear and rear three-quarter views; its side and top views disagree with these and with each other)
# (verifier round 1: the front-right seam turned 6-7 degrees towards the hero camera (az -118), from az -52..-65 to
# -58..-71, so its far wall faces front34 instead of sitting on the limb. The front view caps the turn: the crack
# must stay at x >= 0.70 there, i.e. cos(el) cos(az) >= 0.31 at el 28-41)
FR_SEAM = ((302, 52, -0.1), (302, 42, 0.52), (295, 28, 0.62), (300, 18, 0.62), (293, 6, 0.56), (290, -5, 0.28),
           (289, -18, -0.1), (289, -45, -0.1), (289, BOTTOM, -0.1))
BR_SEAM = ((402, 50, -0.1), (402, 31, -0.02), (398, 19, 0.36), (406, 9, 0.46), (400, -3, 0.38), (404, -26, 0.42),
           (403, -50, 0.4), (403, BOTTOM, 0.4))
# (verifier round 1: the back-left seam meets the crown ring at el 26, not 50, so the Lobe piece's top edge stays at
# el 14-26: its strip up the back-left to the crown read as a comma's tail)
BL_FULL = ((481, 26, 0.0), (478, 20, 0.26), (476, 13, 0.36), (484, 6, 0.46), (478, -5, 0.4), (482, -26, 0.42),
           (481, -50, 0.4), (482, BOTTOM, 0.4))
# the pieces meet the crown ring at its jog, el 6: above that the seam (still cut, BL_FULL) parts the Crown from the
# Back, so the Lobe piece's back edge runs low behind the lobe with no spike up the seam
BL_SEAM = BL_FULL[3:]
# the crown ring, all closed, from the lobe seam's corner round the right and the back to the lobe seam's far end
CROWN_FRONT = ((230, 15, -0.1), (244, 28, -0.1), (262, 40, -0.1), (282, 48, -0.1), (302, 52, -0.1))
CROWN_RIGHT = ((302, 52, -0.1), (324, 55, -0.1), (350, 50, -0.1), (378, 54, -0.1), (402, 50, -0.1))
CROWN_BACK = ((402, 50, -0.1), (426, 55, -0.1), (450, 47, -0.1), (467, 35, -0.1)) + BL_FULL[:4]
# (it dips to el 0-6 behind the lobe: at el 20-26 the Lobe piece's thin strip of main shell there stood higher than
# the lobe's own top, z 5.0 against 4.7, and still read as a horn)
CROWN_LEFT = ((484, 6, -0.1), (502, 2, -0.1), (526, 0, -0.1), (550, 4, -0.1), (564, 14, -0.1))
# (verifier round 1) a closed seam down the lobe's back crease, from the upper run's closed end to the ground: the
# Lobe piece is the lobe's own sector (az about 180-258), chunky as the sheet's Shell Piece Detail. Before, it ran on
# round the main mass's lower shell to the back-left seam (az 124), a long curved strip that read as a tail; that strip
# is now its own piece, BackLeft (exploded render only)
LOBE_BACK = ((204, 14, -0.1), (196, 2, -0.1), (186, -12, -0.1), (180, -32, -0.1), (179, -52, -0.1),
             (179, BOTTOM, -0.1))
# proud far side (verifier round 1): along an open seam, a plate on side A (the side away from the hero camera)
# stands `lift` proud of the main surface at the lip, falling back flush `width` studs out, so that side's wall rises
# above the near lip and faces the camera, as the lobe seam's step does. Tapered with the gap (none where it closes).
PROUD = {"FrontRight": dict(lift=0.10, width=1.6)}   # (0.12-0.20 tried: the riser added dark lip / ember, not width;
                                                    # the lip then measures 0.07-0.11 proud, as the lobe step)
# per-seam wall rows (default ROWS): front34 sees the front-right seam at a grazing angle, mostly its far wall, so its
# lip band is thin (0-0.07 T), its ember band shallow (0.07-0.14 T) and the orange core band below it deeper (from
# there the camera sees about 0.38 down the far wall); the gradient is the same
SEAM_ROWS = {"FrontRight": (0.14, 0.07)}
# (and no lip chamfer on it: the chamfer is on side A, the far side, and with the proud riser its dark bevel was the
# widest band front34 saw)
SEAM_CHAMFER = {"FrontRight": (-0.02, 0.0)}
# ... and that chamfer row, put at the surface (0.02 above it), parts off the proud far side's riser, which glows ember
# (front34 sees the riser whole: as lip it was the widest dark band in the crack). Edge order as _EDGE_MATS.
SEAM_MATS = {"FrontRight": (CORE, EMBER, LIP, EMBER, LIP, LIP, LIP, EMBER, CORE, CORE)}
OPEN_SEAMS = {"Lobe": LOBE_UPPER + LOBE_DESCENT[1:], "FrontRight": FR_SEAM, "BackRight": BR_SEAM,
              "BackLeft": BL_FULL}
PIECES = ("Crown", "Lobe", "Front", "Right", "Back", "BackLeft")
EXPORT_PIECE = "Lobe"         # the chunky rounded piece, as the sheet's Shell Piece Detail (main session, stage 2)

# ---- impact rim ----------------------------------------------------------------------------------------------------
# a squat, broad slab of a stone (the sheet's rim rocks are low and wide, with a broad sloping top)
ROCK = dict(size=(2.6, 2.1, 1.25), seed=9101, rings=[(0.0, 0.92, 7), (0.3, 1.0, 7), (0.7, 0.84, 6), (1.0, 0.52, 4)])
# (az from C0, scale x, y, z, turn deg, mirror, tuck into the meteor's foot in studs)
RIM = ((-62, 1.35, 1.35, 1.45, 20, False, 0.45), (-96, 1.12, 1.15, 1.22, 75, True, 0.4),
       (-128, 0.95, 1.0, 1.0, 140, False, 0.4), (-158, 0.88, 0.92, 0.92, 200, True, 0.35),
       (-188, 0.95, 0.95, 0.9, 260, False, 0.35), (-30, 0.92, 0.95, 1.0, 310, True, 0.35),
       (0, 0.86, 0.86, 0.86, 15, False, 0.35), (32, 0.82, 0.9, 0.8, 95, True, 0.35),
       (63, 0.86, 0.86, 0.9, 170, False, 0.35), (95, 0.9, 0.86, 0.85, 230, True, 0.35),
       (127, 0.82, 0.86, 0.85, 290, False, 0.35), (160, 0.86, 0.9, 0.9, 340, True, 0.35))
# (verifier round 1: from above the rocks hid under the meteor's bulge; on the sheet the rim rings outside it, out to
# 1.2-1.4 x the meteor's width.) Every rim rock's outer edge is pushed out to RIM_OUT beyond the bulge (_bulge; push
# at most RIM_PUSH_MAX), its inner edge kept in the foot: its centre moves push / 2 and it grows by push across. The
# stones sit at least STONE_OUT beyond the bulge. RIM_PUSH: extra push per rock (az -> studs)
RIM_OUT, RIM_PUSH_MAX, STONE_OUT = 1.3, 1.0, 0.8
RIM_PUSH = {}
# small stones in gaps and just outside the ring: (az, scale, distance beyond the meteor's foot, turn)
STONES = ((-78, 0.42, 2.0, 40), (-143, 0.36, 1.9, 100), (47, 0.4, 1.9, 200), (112, 0.34, 1.8, 300))


NEON = 1.0                  # emission of the glow keys: the exporter's Neon threshold, and no more (a stronger
                            # emission only washes the Blender preview towards yellow-white)
EMBER_EMIT = NEON           # the ember band glows too (Neon, deep red): unlit, it rendered #3B2121-#542B26 and
                            # left the crack's median dark red-brown in the front, side, rear and rear34 views, where
                            # the sheet's is bright orange; only the lip stays a solid, unlit dark edge


def palette():
    # stage 4: base colours calibrated so the kit studio render matches the sheet AS RENDERED (K.calibrate on the
    # test dome, VFX off; targets, calibrated hexes and re-measures in M009_spec.md, "Stage 4"). Sheet swatches:
    # Rock Shell #3E3C41, Metal Core (Inner Faces) #877E7C, Impact Rock #AD998E, Crack / Core #F55E21.
    # (the Neon keys render unshaded, emission only: _glow_mats; so their hexes are the sheet's colours and what
    # Roblox's Neon shows)
    K.set_colour(SHELL, "#43424A", rough=0.88)          # renders #5E595D (sheet #5C575C)
    K.set_colour(SHELL_LIGHT, "#51505D", rough=0.88)    # #6E6973 (#68646D + 6)
    K.set_colour(SHELL_DARK, "#322E33", rough=0.9)      # #4A4445 (#474143)
    K.set_colour(SHELL_CUT, "#726B69", rough=0.9)       # #988A81 (#998B81, the cross-section's cut wall)
    K.set_colour(LIP, "#500E0E", rough=0.8)             # dome #6E312E (target #6F332E: see TARGETS)
    K.set_colour(EMBER, "#B73C1C", rough=0.7, emit=EMBER_EMIT)  # #C23515 (#C33615)
    K.set_colour(CORE, "#E5642A", rough=0.5, emit=NEON)         # #F86223 (#F55E21)
    K.set_colour(HOT, "#FB8D24", rough=0.5, emit=NEON)          # #FF911D (#FD911C)
    K.set_colour(CORE_DEEP, "#BF4520", rough=0.5, emit=NEON)    # #CB3F19 (#CD3F18)
    K.set_colour(SEAM_DEEP, "#963623", rough=0.6, emit=NEON)    # #9B2F1C (#9D311A)
    K.set_colour(IMPACT, "#786A66", rough=0.92)         # #A0887D (#A18A7D)
    K.set_colour(IMPACT_LIGHT, "#887E7A", rough=0.92)   # #B5A296 (#B8A498)
    K.set_colour(IMPACT_DARK, "#645D5E", rough=0.92)    # #857873 (#877974)
    for k in TARGETS:
        _restyle(k)
    _glow_mats()


def _restyle(key):
    """Drop an FB_ material whose node set no longer matches its key's emission (flintkit builds emissive keys
    without the Tint node, and set_colour never clears an emission), so flintkit makes it afresh."""
    mat = bpy.data.materials.get("FB_" + key)
    if mat and mat.node_tree:
        tinted = any(n.type == "MIX" for n in mat.node_tree.nodes)
        if tinted == (K.fk().palette_entry(key)[3] > 0):
            bpy.data.materials.remove(mat)


def _glow_mats():
    """Blender preview of the Neon keys (emission >= NEON) as Roblox shows Neon: the key's own colour, unshaded (the
    BSDF's base colour black and no specular, so only the emission shows). The exported hex is unchanged."""
    for mat in bpy.data.materials:
        if not (mat.name.startswith("FB_m009_") and mat.node_tree):
            continue
        if list(mat.get("flintkit_spec", [0, 0, 0]))[2] < NEON:
            continue
        b = mat.node_tree.nodes.get("Principled BSDF")
        for l in list(b.inputs["Base Color"].links):
            mat.node_tree.links.remove(l)
        b.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)
        if "Specular IOR Level" in b.inputs:
            b.inputs["Specular IOR Level"].default_value = 0.0


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS), with the Neon preview kept on every round. Stone keys are sampled
    unfiltered (the test box lies wholly on the dome; K.sample's sat < 0.18 stone filter drops the warm rock, which
    the studio renders peach at sat 0.28, so the loop chased the background). Returns {key: (hex, rendered)}."""
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
        for k in keys:          # the material exists (and is restyled) before the first render
            K.fk().material(k)
        _glow_mats()
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        K.set_colour, K.sample = set0, sample0
        _drop_calib()


def _drop_calib():
    """K.calibrate removes its test dome object but not its mesh: purge the orphan T_Calib meshes that carry only
    this model's keys (left behind, they were the only users of keys the build no longer uses)."""
    gone = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")
            and all(x is None or x.name.startswith("FB_m009_") for x in m.materials)]
    for m in gone:
        bpy.data.meshes.remove(m)
    return len(gone)


# calibration targets (sheet, as rendered; sampled in M009_spec.md 2a): key -> (sRGB, kind)
# (shell_light: the sheet's hero top facets #68646D + 6 levels, verifier round 1: the top facets and the front view
# rendered 12 levels under the sheet)
TARGETS = {SHELL: ((0x5C, 0x57, 0x5C), "stone"), SHELL_LIGHT: ((0x6E, 0x6A, 0x73), "stone"),
           SHELL_DARK: ((0x47, 0x41, 0x43), "stone"), SHELL_CUT: ((0x99, 0x8B, 0x81), "stone"),
           # the lip sits in the crack's shade: its dome target is the sheet's lip (#4E2B2A) scaled in linear light by
           # sheet / ours at the crack's 15th percentile (#592D28 / #3E2624), so in the crack it renders as the sheet's
           LIP: ((0x6F, 0x33, 0x2E), "vivid"),
           # ember: the sheet's crack at its 30th percentile on the hero's right seam (#C33615). The front view's 30th
           # percentile (#9D311A) was tried first: the ember band is what the front, side, rear and rear34 views see
           # most of, and their crack medians came out ember red (#8B2D1D-#9B2F1C) where the sheet's are orange
           # (#D23C10-#DE400F)
           EMBER: ((0xC3, 0x36, 0x15), "vivid"),
           # core: the "Crack / Core" swatch itself (Neon shows one flat colour, as a swatch does). The hero crack's
           # median (#E34515) was tried first: the core part then rendered #E24919 against the exploded core's
           # #FA601D, and the hero crack (a mix of all four bands) stayed below the sheet's median
           CORE: ((0xF5, 0x5E, 0x21), "vivid"), HOT: ((0xFD, 0x91, 0x1C), "vivid"),
           CORE_DEEP: ((0xCD, 0x3F, 0x18), "vivid"), IMPACT: ((0xA1, 0x8A, 0x7D), "stone"),
           # seam_deep: the sheet's crack at its 30th percentile in the front view (#9D311A): dark enough (R < 170)
           # that it no longer counts as orange, so the wide lobe seam stops doubling the sheet's orange share
           SEAM_DEEP: ((0x9D, 0x31, 0x1A), "vivid"),
           IMPACT_LIGHT: ((0xB8, 0xA4, 0x98), "stone"), IMPACT_DARK: ((0x87, 0x79, 0x74), "stone")}


# ---- geometry helpers ----------------------------------------------------------------------------------------------
def _dir(az, el):
    a, e = math.radians(az), math.radians(el)
    return Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))


def _cloud(centre, radii, seed, n, top=1.0, wobble=(0.93, 1.05)):
    """Evenly spread, lumpy points on an ellipsoid (a Fibonacci sphere): the meteor's broad facets. top squashes
    the upper half (a broader, flatter crown)."""
    rng = random.Random(seed)
    c = Vector(centre)
    pts = []
    for k in range(n):
        z = 1 - 2 * (k + 0.5) / n
        r = math.sqrt(1 - z * z)
        th = k * 2.39996 + rng.uniform(-0.12, 0.12)
        s = rng.uniform(*wobble)
        pts.append(c + Vector((math.cos(th) * r * radii[0], math.sin(th) * r * radii[1],
                               z * radii[2] * (top if z > 0 else 1.0))) * s)
    return pts


def _hull_bm(pts):
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def _planes(bm):
    """Outward (normal, offset) planes of a closed convex bmesh, coplanar faces merged (each facet's normal is
    turned to face away from the centroid, whatever the hull's winding)."""
    c = sum((v.co for v in bm.verts), Vector()) / len(bm.verts)
    out = []
    for f in bm.faces:
        if f.calc_area() < 1e-9:
            continue
        n = f.normal.copy()
        h = n.dot(f.verts[0].co)
        if h - n.dot(c) < 0:
            n, h = -n, -h
        if not any(n.dot(m) > 1 - 1e-6 and abs(h - g) < 1e-5 for m, g in out):
            out.append((n, h))
    return out


def _clip_poly(poly, n, h):
    """Sutherland-Hodgman: the part of a 3D polygon with n.x <= h, and the points where it crosses the plane."""
    out, cut = [], []
    for i, p in enumerate(poly):
        q = poly[(i + 1) % len(poly)]
        sp, sq = n.dot(p) - h, n.dot(q) - h
        if sp <= 0:
            out.append(p)
        if (sp < 0) != (sq < 0) and abs(sp - sq) > 1e-12:
            x = p.lerp(q, sp / (sp - sq))
            out.append(x)
            cut.append(x)
    return out, cut


def _inset(pts, d, merge=0.3):
    """The convex hull of pts with every facet plane moved in by d (an exact constant-thickness inset): the hull's
    faces clipped by each inset plane in turn, each cut capped with the polygon of its crossing points."""
    bm = _hull_bm(pts)
    planes = _planes(bm)
    polys = [[v.co.copy() for v in f.verts] for f in bm.faces]
    bm.free()
    for n, h in planes:
        h -= d
        new, cut = [], []
        for poly in polys:
            p, c = _clip_poly(poly, n, h)
            if len(p) >= 3:
                new.append(p)
            cut += c
        if len(cut) >= 3:
            c0 = sum(cut, Vector()) / len(cut)
            u = (cut[0] - c0).normalized()
            w = n.cross(u)
            cut.sort(key=lambda q: math.atan2((q - c0).dot(w), (q - c0).dot(u)))
            new.append(cut)
        polys = new
    # the inset leaves clusters of near points where a corner of many facets was cut back: each cluster becomes one
    # point (broad facets, as on the sheet's core; the thickness stays within a few hundredths of d)
    groups = []
    for poly in polys:
        for q in poly:
            g = next((g for g in groups if (g[0] / g[1] - q).length < merge), None)
            if g:
                g[0] += q
                g[1] += 1
            else:
                groups.append([q.copy(), 1])
    return [s / n for s, n in groups]


# (verifier round 1: the core's disc on the underside was 0.32 of the rim's width, the sheet's 0.4) the core's bottom
# is flattened: its points below z1 move out from the meteor's axis, up to `grow` x at the ground and below, but never
# closer than `margin` to the main hull (so the shell ring round the floor disc stays at least that wide)
# (the margin binds: at z = 0 the main hull is only about 2.9 from the axis, so the disc tops out near 4.8 x 4.1)
# (z1 1.0: from 2.0 the hull's facets carried the bulge up to el -15 and the seams there lost depth, 0.52-0.57)
FLAT = dict(z1=1.0, grow=0.7, margin=0.45)


def _flatten(pts, main_pl, margin):
    out = []
    for p in pts:
        f = min(1.0, max(0.0, (FLAT["z1"] - p.z) / FLAT["z1"]))
        q = Vector((p.x - C0.x, p.y - C0.y, 0.0))
        if f <= 0 or q.length < 1e-6:
            out.append(p.copy())
            continue
        d = q.normalized()
        s = _span(main_pl, Vector((C0.x, C0.y, p.z)), d)
        lim = (s[1] - margin) if s else q.length
        r = max(q.length, min(q.length * (1 + FLAT["grow"] * f), lim))
        out.append(Vector((C0.x + d.x * r, C0.y + d.y * r, p.z)))
    return out


_GEO = {}


def _geo():
    """Hull points and planes of the masses, the core and the pieces' hollow (cached per parameter set)."""
    key = (tuple(C0), str(MAIN), str(LOBE), T, CORE_GAP, str(FLAT))
    if _GEO.get("key") != key:
        g = {"key": key}
        g["main"] = _cloud(MAIN["centre"], MAIN["radii"], MAIN["seed"], MAIN["n"], MAIN["top"], MAIN["wobble"])
        g["lobe"] = _cloud(LOBE["centre"], LOBE["radii"], LOBE["seed"], LOBE["n"], LOBE["top"], LOBE["wobble"])
        bm = _hull_bm(g["main"])
        main_pl = _planes(bm)
        bm.free()
        g["core"] = _flatten(_inset(g["main"], T), main_pl, FLAT["margin"])
        g["hollow"] = _flatten(_inset(g["main"], T + CORE_GAP), main_pl, FLAT["margin"] + CORE_GAP)
        for k in ("main", "lobe", "core", "hollow"):
            bm = _hull_bm(g[k])
            g[k + "_pl"] = _planes(bm)
            bm.free()
        _GEO.clear()
        _GEO.update(g)
    return _GEO


def _span(planes, p, d):
    """(entry, exit) distances of the ray p + t d through a convex polyhedron, or None."""
    t0, t1 = -1e9, 1e9
    for n, h in planes:
        nd, s = n.dot(d), h - n.dot(p)
        if abs(nd) < 1e-12:
            if s < 0:
                return None
            continue
        t = s / nd
        if nd > 0:
            t1 = min(t1, t)
        else:
            t0 = max(t0, t)
    return (t0, t1) if t0 <= t1 else None


def _rho(d, p=None):
    """Distance from p (default C0) to the outer surface (main or lobe) along d: the farthest exit."""
    g = _geo()
    p = C0 if p is None else p
    best = 0.0
    for k in ("main_pl", "lobe_pl"):
        s = _span(g[k], p, d)
        if s and s[1] > best:
            best = s[1]
    return best


def _rho_core(d):
    return _span(_geo()["core_pl"], C0, d)[1]


def _resample(nodes, step=STEP):
    """Nodes (az, el, G) -> (direction, G) at most `step` degrees apart (az, el and G interpolated linearly)."""
    out = []
    for (a0, e0, g0), (a1, e1, g1) in zip(nodes, nodes[1:]):
        k = max(1, math.ceil(math.degrees(_dir(a0, e0).angle(_dir(a1, e1))) / step))
        for i in range(k):
            t = i / k
            out.append((_dir(a0 + (a1 - a0) * t, e0 + (e1 - e0) * t), g0 + (g1 - g0) * t))
    out.append((_dir(nodes[-1][0], nodes[-1][1]), nodes[-1][2]))
    return out


def _arc(a0, a1, el=BOTTOM, step=10.0):
    """Nodes along a constant elevation from az a0 to a1 (both ends included)."""
    k = max(1, math.ceil(abs(a1 - a0) / step))
    return [(_dir(a0 + (a1 - a0) * i / k, el), -0.1) for i in range(k + 1)]


# ---- shell pieces: sector loops ------------------------------------------------------------------------------------
def _loops():
    """Each piece's boundary as a closed loop of directions (seam centre lines)."""
    up, de = _resample(LOBE_UPPER), _resample(LOBE_DESCENT)
    fr, br, bl = _resample(FR_SEAM), _resample(BR_SEAM), _resample(BL_SEAM)
    cf, cr, cb, cl = (_resample(c) for c in (CROWN_FRONT, CROWN_RIGHT, CROWN_BACK, CROWN_LEFT))
    lb = _resample(LOBE_BACK)
    d = lambda seq: [n[0] for n in seq]
    loops = {
        "Crown": d(cf[:-1] + cr[:-1] + cb[:-1] + cl[:-1] + up[:-1]),
        "Lobe": d(up[::-1][:-1] + lb[:-1] + _arc(LOBE_BACK[-1][0], LOBE_DESCENT[-1][0])[:-1] + de[::-1][:-1]),
        "BackLeft": d(cl[::-1][:-1] + bl[:-1] + _arc(BL_SEAM[-1][0] - 360, LOBE_BACK[-1][0])[:-1] + lb[::-1][:-1]),
        "Front": d(cf[:-1] + fr[:-1] + _arc(FR_SEAM[-1][0], LOBE_DESCENT[-1][0])[:-1] + de[::-1][:-1]),
        "Right": d(cr[:-1] + br[:-1] + _arc(BR_SEAM[-1][0], FR_SEAM[-1][0])[:-1] + fr[::-1][:-1]),
        "Back": d(cb[:-1] + bl[:-1] + _arc(BL_SEAM[-1][0], BR_SEAM[-1][0])[:-1] + br[::-1][:-1]),
    }
    return loops


def cone(a, piece, R=11.0):
    """The piece's sector: a star-shaped solid from C0 out to radius R through its boundary loop, capped."""
    loop = _loops()[piece]
    bm = a.bm
    apex = bm.verts.new(C0)
    ring = [bm.verts.new(C0 + q * R) for q in loop]
    mid = sum(loop, Vector()).normalized()
    cap = bm.verts.new(C0 + mid * R)
    n = len(ring)
    for i in range(n):
        bm.faces.new((apex, ring[i], ring[(i + 1) % n]))
        bm.faces.new((cap, ring[(i + 1) % n], ring[i]))
    vs = [apex, cap] + ring
    fs = K.faces_of(vs)
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    if sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs) < 0:
        bmesh.ops.reverse_faces(bm, faces=fs)
    a._finish(vs, SHELL_CUT, tint=1.0)
    return vs


# ---- seam cutters --------------------------------------------------------------------------------------------------
def _runs(nodes):
    """The open stretches of a resampled seam: lists of (direction, G) with G > 0 inside, each closed end a node with
    G = 0 at the interpolated crossing."""
    runs, cur = [], None
    for i, (d, g) in enumerate(nodes):
        if g > 0:
            if cur is None:
                cur = []
                if i > 0:
                    d0, g0 = nodes[i - 1]
                    cur.append((d0.lerp(d, g0 / (g0 - g)).normalized(), 0.0))
            cur.append((d, g))
        elif cur is not None:
            d0, g0 = nodes[i - 1]
            cur.append((d0.lerp(d, g0 / (g0 - g)).normalized(), 0.0))
            runs.append(cur)
            cur = None
    if cur:
        runs.append(cur)
    return runs


def _profile(run, j, rows_f=ROWS, chamfer=CHAMFER):
    """Cross-section points of the cutter at node j: side A (the main / lower side, with the lip chamfer) and side B,
    each from the deep row up: [deep, floor-row, lip-row, chamfer-row, out]."""
    d, G = run[j]
    segs = []
    if j > 0:
        segs.append((run[j - 1][0], d))
    if j < len(run) - 1:
        segs.append((d, run[j + 1][0]))
    ns = []
    for u, v in segs:
        s = d.cross(v - u)
        s -= d * s.dot(d)
        ns.append(s.normalized())
    nav = sum(ns, Vector()).normalized()
    side = nav / max(0.62, min(x.dot(nav) for x in ns))           # mitred at the jogs, so walls stay parallel
    rho, rc = _rho(d), _rho_core(d)
    # (clamped: below ground the flattened core comes within 0.45 of the surface, and a thinner shell would put the
    # 0.25 row above the chamfer row and fold the tube)
    th = max(rho - rc, 0.55)
    half = G / 2

    def w(f):
        return half * (1 - (1 - FLOOR_FRAC) * f)
    # the lid sits well above the surface on both sides (the lobe side can stand far proud of the centre line)
    top = max(rho, _rho((C0 + d * rho + side * (half + 0.3) - C0).normalized()),
              _rho((C0 + d * rho - side * (half + 0.3) - C0).normalized())) + 0.8
    slope = (half - w(1.0)) / th
    w_out = half + slope * (top - rho)
    cd, cx = chamfer
    c = cx * min(1.0, G / 0.3)
    w_ch = w(cd / th)
    w_ch_out = half + c + (top - rho) * (half + c - w_ch) / cd

    def P(r, off):
        return C0 + d * r + side * off
    # (the deep row carries the wall's slope on below the core's surface, so the floor the core shows between the
    # walls is FLOOR_FRAC x G wide)
    rows = ((rc - FLOOR_DEEP, max(0.0, w(1.0 + FLOOR_DEEP / th))), (rho - rows_f[0] * th, w(rows_f[0])),
            (rho - rows_f[1] * th, w(rows_f[1])), (rho - cd, w_ch))
    A = [P(r, o) for r, o in rows] + [P(top, w_ch_out)]
    B = [P(r, -o) for r, o in rows] + [P(top, -w_out)]
    return A, B


# materials of the profile's edges, side A deep -> out, then the lid, then side B out -> deep, then the bottom
_EDGE_MATS = (CORE, EMBER, LIP, LIP, LIP, LIP, LIP, EMBER, CORE, CORE)


def _tube(a, run, rows_f=ROWS, chamfer=CHAMFER, edge_mats=None):
    edge_mats = edge_mats or _EDGE_MATS
    bm = a.bm
    profs = []
    for j in range(len(run)):
        A, B = _profile(run, j, rows_f, chamfer)
        if run[j][1] <= 1e-9:               # a closed end: the two walls meet in one line
            va = [bm.verts.new(p) for p in A]
            vb = va
        else:
            va = [bm.verts.new(p) for p in A]
            vb = [bm.verts.new(p) for p in B]
        profs.append(va + vb[::-1])
    faces = []
    mats = {k: a._mi(k) for k in set(edge_mats) | {CORE}}
    n = len(profs[0])
    for j in range(len(profs) - 1):
        p, q = profs[j], profs[j + 1]
        for k in range(n):
            quad = [p[k], p[(k + 1) % n], q[(k + 1) % n], q[k]]
            uniq = []
            for v in quad:
                if v not in uniq:
                    uniq.append(v)
            if len(uniq) < 3:
                continue
            f = bm.faces.new(uniq)
            f.material_index = mats[edge_mats[k]]
            faces.append(f)
    for p in (profs[0], profs[-1]):         # open ends (into the ground): capped
        uniq = list(dict.fromkeys(p))
        if len(uniq) == n:
            f = bm.faces.new(uniq)
            f.material_index = mats[CORE]
            faces.append(f)
    vs = list({v for f in faces for v in f.verts})
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    # (recalc can settle on the inside-out winding for a thin tube: check the enclosed volume's sign)
    if sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in faces) < 0:
        bmesh.ops.reverse_faces(bm, faces=faces)
    bmesh.ops.triangulate(bm, faces=[f for f in faces if f.is_valid and len(f.verts) > 4])
    for f in K.faces_of(vs):
        f.smooth = False
        for l in f.loops:
            l[a.tint_layer] = (1.0, 1.0, 1.0, 1.0)
    return vs


def cutters(a):
    """Every open seam's cutter (separate closed tubes)."""
    out = []
    for name, nodes in OPEN_SEAMS.items():
        for run in _runs(_resample(nodes)):
            out += _tube(a, run, SEAM_ROWS.get(name, ROWS), SEAM_CHAMFER.get(name, CHAMFER), SEAM_MATS.get(name))
    return out


# ---- solids --------------------------------------------------------------------------------------------------------
def _hull(a, pts, mat):
    vs = [a.bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(a.bm, input=vs)
    for v in vs:
        if v.is_valid and not v.link_faces:
            a.bm.verts.remove(v)
    vs = [v for v in vs if v.is_valid]
    bmesh.ops.recalc_face_normals(a.bm, faces=K.faces_of(vs))
    a._finish(vs, mat, tint=1.0)
    return vs


def _side(run, j):
    """Unit side vector at node j of a run, pointing to side A (as _profile's, without the mitre)."""
    d = run[j][0]
    u, v = run[max(j - 1, 0)][0], run[min(j + 1, len(run) - 1)][0]
    s = d.cross(v - u)
    s -= d * s.dot(d)
    return s.normalized()


def proud(a):
    """PROUD plates: per open run, a lofted solid on side A. Cross-section at each node: the lip edge (on the seam's
    centre line, inside the gap the cutter takes) `lift` above the main surface, a middle row on the surface at
    width / 2 lifted 0.45 x lift (so the plate follows the curve), the far edge 0.04 under the surface at `width`,
    and the same three 0.35 below the surface. lift scales with G / 0.3 and is -0.03 (buried) where the gap closes."""
    out = []
    bm = a.bm
    for name, pr in PROUD.items():
        for run in _runs(_resample(OPEN_SEAMS[name])):
            profs = []
            n_run = len(run)
            for j, (d, G) in enumerate(run):
                # the middle and far rows follow the seam smoothed over +-3 nodes (on the jogs' raw offsets the far
                # rows folded over each other on the inside of each bend)
                win = range(max(0, j - 3), min(n_run, j + 4))
                ds = sum((run[i][0] for i in win), Vector()).normalized()
                s = sum((_side(run, i) for i in win), Vector())
                s = (s - ds * s.dot(ds)).normalized()
                t = min(1.0, G / 0.3)
                lift = pr["lift"] * t - 0.03 * (1 - t)
                rho, rs = _rho(d), _rho(ds)
                dm = (ds * rs + s * pr["width"] / 2).normalized()
                df = (ds * rs + s * pr["width"]).normalized()
                rm, rf = _rho(dm), _rho(df)
                pts = [C0 + d * (rho + lift), C0 + dm * (rm + 0.45 * lift), C0 + df * (rf - 0.04),
                       C0 + df * (rf - 0.35), C0 + dm * (rm - 0.35), C0 + d * (rho - 0.35)]
                profs.append([bm.verts.new(p) for p in pts])
            faces = []
            n = 6
            for p, q in zip(profs, profs[1:]):
                for k in range(n):
                    faces.append(bm.faces.new((p[k], p[(k + 1) % n], q[(k + 1) % n], q[k])))
            faces += [bm.faces.new(profs[0]), bm.faces.new(profs[-1][::-1])]
            vs = [v for p in profs for v in p]
            bmesh.ops.recalc_face_normals(bm, faces=faces)
            if sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in faces) < 0:
                bmesh.ops.reverse_faces(bm, faces=faces)
            bmesh.ops.triangulate(bm, faces=faces, quad_method="BEAUTY", ngon_method="BEAUTY")
            a._finish(vs, SHELL, tint=1.0)
            out += vs
    return out


def outer(a):
    g = _geo()
    return _hull(a, g["main"], SHELL) + _hull(a, g["lobe"], SHELL)


def _outer_obj(name):
    """The outer as a temporary build-frame object: the two hulls unioned, then the PROUD plates. (One union_loose
    over all three shells came out empty in the exact solver; the plates' own union is clean.)"""
    o = _tmp(name, outer)
    M.union_loose(o)
    _bool(o, _tmp("_m009_proud", proud), "UNION")
    return o


def core(a, mat=CORE):
    return _hull(a, _geo()["core"], mat)


def hollow(a):
    return _hull(a, _geo()["hollow"], CORE)


def core_part(a):
    """The Metal Core part: the core itself (the hollow it fills), centred at the origin by mk."""
    return core(a, CORE)


def impact_rock(a):
    vs = K.hull_rock(a, ROCK["size"], seed=ROCK["seed"], mat=IMPACT, rings=ROCK["rings"], jitter=0.07,
                     keep_bottom=True)
    return vs


def _foot(az, z=0.7):
    """Horizontal distance from the meteor's axis (C0's x, y) to its surface at height z, towards az."""
    d = Vector((math.cos(math.radians(az)), math.sin(math.radians(az)), 0.0))
    return _rho(d, Vector((C0.x, C0.y, z)))


def _bulge(az):
    """The meteor's widest horizontal reach from its axis towards az (any height): what hides the rim from above."""
    return max(_foot(az, z * 0.3) for z in range(0, 22))


def _rim_matrices():
    out = []
    w, dp, _ = ROCK["size"]
    for az, sx, sy, sz, rot, mirror, tuck in RIM:
        half = 0.5 * (w * sx + dp * sy) / 2
        foot = _foot(az)
        # the push that brings the outer edge RIM_OUT beyond the bulge (capped), plus any fixed extra
        p = min(RIM_PUSH_MAX, max(0.0, _bulge(az) + RIM_OUT - (foot + 2 * half - tuck))) + RIM_PUSH.get(az, 0.0)
        k = (half + p / 2) / half
        sx, sy = sx * k, sy * k
        r = foot + half - tuck + p / 2
        loc = Vector((C0.x + math.cos(math.radians(az)) * r, C0.y + math.sin(math.radians(az)) * r, 0.0))
        out.append(Matrix.Translation(loc) @ Matrix.Rotation(math.radians(rot), 4, "Z")
                   @ Matrix.Diagonal((sx, -sy if mirror else sy, sz, 1.0)))
    for az, s, extra, rot in STONES:
        r = max(_foot(az, 0.3) + extra, _bulge(az) + STONE_OUT)
        loc = Vector((C0.x + math.cos(math.radians(az)) * r, C0.y + math.sin(math.radians(az)) * r, 0.0))
        out.append(Matrix.Translation(loc) @ Matrix.Rotation(math.radians(rot), 4, "Z")
                   @ Matrix.Diagonal((s, s, s * 1.1, 1.0)))
    return out


# ---- object plumbing -----------------------------------------------------------------------------------------------
def _tmp(name, fn):
    """fn's geometry as a temporary object in the build frame (origin at the build frame's origin)."""
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    a = K.fk().Asset(name, "probe", tint_var=0.0)
    fn(a)
    return a.finish(collection=M.coll(NUM, TITLE), mark_asset=False, origin=None)


def _bool(o, other, op, remove=True, self_x=False):
    m = o.modifiers.new("B", "BOOLEAN")
    m.operation, m.solver, m.object = op, "EXACT", other
    m.use_self, m.material_mode = self_x, "TRANSFER"
    with M._override(o):
        bpy.ops.object.modifier_apply(modifier=m.name)
    if remove:
        me = other.data
        bpy.data.objects.remove(other, do_unlink=True)
        if me.users == 0:
            bpy.data.meshes.remove(me)


def _paste(a, o, mat4=None, tint=1.0):
    """Copy a finished object's mesh (materials by palette key, Tint times tint) into an Asset through mat4."""
    mat4 = mat4 or Matrix.Identity(4)
    src = bmesh.new()
    src.from_mesh(o.data)
    layer = src.loops.layers.float_color.get("Tint")
    mis = [a._mi(m.get("flintkit_key") or m.name[3:]) for m in o.data.materials]
    vmap = {v: a.bm.verts.new(mat4 @ v.co) for v in src.verts}
    flip = mat4.to_3x3().determinant() < 0
    for f in src.faces:
        vs = [vmap[v] for v in f.verts]
        loops = list(f.loops)
        if flip:
            vs.reverse()
            loops.reverse()
        nf = a.bm.faces.new(vs)
        nf.material_index = mis[f.material_index] if mis else 0
        nf.smooth = False
        for l, nl in zip(loops, nf.loops):
            t = (l[layer][0] if layer else 1.0) * tint
            nl[a.tint_layer] = (t, t, t, 1.0)
    src.free()
    return list(vmap.values())


def _slot(o, key):
    me = o.data
    for i, m in enumerate(me.materials):
        if (m.get("flintkit_key") or m.name[3:]) == key:
            return i
    me.materials.append(K.fk().material(key))
    return len(me.materials) - 1


def _core_section():
    """The core's cross-section at z = 0: a convex polygon (2D points, counter-clockwise)."""
    poly = [Vector((-50, -50)), Vector((50, -50)), Vector((50, 50)), Vector((-50, 50))]
    for n, h in _geo()["core_pl"]:
        n2 = Vector((n.x, n.y))
        if n2.length < 1e-9:
            continue
        out = []
        for i, p in enumerate(poly):
            q = poly[(i + 1) % len(poly)]
            sp, sq = n2.dot(p) - h, n2.dot(q) - h
            if sp <= 0:
                out.append(p)
            if (sp < 0) != (sq < 0):
                out.append(p.lerp(q, sp / (sp - sq)))
        poly = out
    return poly


def _floor(o, split=None):
    """Cut everything below z = 0 (build frame) and fill the base flat with SHELL_CUT. With split (a convex 2D
    polygon), the floor faces inside it take CORE: the core's disc on the underside."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces), dist=1e-5,
                           plane_co=(0, 0, 0), plane_no=(0, 0, -1), clear_outer=True)
    below = [v for v in bm.verts if v.co.z < -1e-4]
    if below:
        bmesh.ops.delete(bm, geom=below, context="VERTS")
    for v in bm.verts:
        if abs(v.co.z) < 1e-4:
            v.co.z = 0.0
    bnd = [e for e in bm.edges if e.is_boundary]
    tint = bm.loops.layers.float_color.get("Tint")
    cut = _slot(o, SHELL_CUT)
    if bnd:
        res = bmesh.ops.holes_fill(bm, edges=bnd)
        for f in res["faces"]:
            f.material_index = cut
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def floor_faces():
        return [f for f in bm.faces if all(abs(v.co.z) < 1e-5 for v in f.verts)]
    if split:
        n = len(split)
        for i in range(n):
            p, q = split[i], split[(i + 1) % n]
            e = (q - p).normalized()
            fl = floor_faces()
            geom = fl + list({x for f in fl for x in f.edges}) + list({v for f in fl for v in f.verts})
            bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=(p.x, p.y, 0.0),
                                   plane_no=(e.y, -e.x, 0.0))
        ci = _slot(o, CORE)

        def inside(c):
            return all((split[(i + 1) % n] - split[i]).cross(Vector((c.x, c.y)) - split[i]) >= -1e-6
                       for i in range(n))
        fl = floor_faces()
        for f in fl:
            f.material_index = ci if inside(f.calc_center_median()) else cut
        edges = [e for e in {x for f in fl for x in f.edges} if len(e.link_faces) == 2
                 and all(x in fl for x in e.link_faces)]
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.0), verts=list({v for f in fl for v in f.verts}),
                                 edges=edges, delimit={"MATERIAL"})
    if tint:
        for f in floor_faces():
            for l in f.loops:
                l[tint] = (1.0, 1.0, 1.0, 1.0)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    bm.to_mesh(o.data)
    bm.free()


def _shells(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    n = M._shells(bm)
    bm.free()
    return n


def _sliver_pass(o):
    """Stage 2's sliver pass (m011._clean): needles, caps and specks the booleans leave, moving no vertex more than
    0.18 studs and keeping the ground plane flat."""
    log = m011._clean(o, m011._plane_lock((0.0,)), max_move=m011.CLEAN_MOVE)
    # a collapse next to a narrow crack tip can fold two triangles onto each other (a zero-volume fin): drop both,
    # then mend any edge left on more than two faces
    bm = bmesh.new()
    bm.from_mesh(o.data)
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
    log["fins"] = len(fins) // 2
    log["nonmanifold_left"] = M.repair_nonmanifold(o)
    log["forced"] = m012._force_slivers(o, lim=3.0)
    return log


# ---- stage 2: polish (after M.finish) --------------------------------------------------------------------------------
POLISH_LIM = 5.0            # no corner under this many degrees, except where the fix would move a seam-wall row
POLISH_TOL = 0.08           # a flip may move the surface by at most this much (studs; 0 on a flat facet). The last
                            # sliver (4.6 deg, a shell facet ending on the lobe seam's lip) needs a 0.074 crease shift
POLISH_STEPS = (0.01, 0.02, 0.035, 0.05, 0.08)      # nudge sizes (studs)
WALL_KEYS = (LIP, EMBER)    # the seam walls' bands: every vert on one of their faces is a row vert (lip line, chamfer
                            # row, 0.25 and 0.55 rows) and never moves; edges between two keys are never flipped


def _wall_verts(o, bm):
    keys = [(m.get("flintkit_key") or m.name[3:]) for m in o.data.materials]
    wall = {i for i, k in enumerate(keys) if k in WALL_KEYS}
    return {v for f in bm.faces if f.material_index in wall for v in f.verts}


def _flip_thin(bm, f, lim):
    """Flip whichever edge of the thin triangle f gives the best pair (both new triangles better than the old pair's
    worst, facing the same way, the surface moving at most POLISH_TOL); edges between two keys stay."""
    best = None
    for e in f.edges:
        if len(e.link_faces) != 2 or any(len(x.verts) != 3 for x in e.link_faces):
            continue
        g = next(x for x in e.link_faces if x is not f)
        if g.material_index != f.material_index:
            continue
        A, B = e.verts
        c = next(v for v in f.verts if v not in e.verts)
        d = next(v for v in g.verts if v not in e.verts)
        if bm.edges.get((c, d)):
            continue
        p1, p2 = intersect_line_line(A.co, B.co, c.co, d.co) or (A.co, A.co)
        if (p1 - p2).length > POLISH_TOL:
            continue
        nav = f.normal + g.normal
        ns = [m011._normal(q) for q in ([A.co, c.co, d.co], [c.co, B.co, d.co])]
        if nav.length < 1e-9 or min(n.length for n in ns) < 1e-12:
            continue
        d1, d2 = (n.normalized().dot(nav.normalized()) for n in ns)
        if d1 * d2 <= 0 or min(abs(d1), abs(d2)) < 0.5:
            continue
        old = min(m011._fmin(f), m011._fmin(g))
        new = min(m011._min_angle([A.co, c.co, d.co]), m011._min_angle([c.co, B.co, d.co]))
        if new > old and (best is None or new > best[0]):
            best = (new, e)
    return bool(best and bmesh.ops.rotate_edges(bm, edges=[best[1]], use_ccw=False)["edges"])


def _nudge_free(bm, f, lim, locked):
    """Move one unlocked corner of f by up to 0.08 studs (ground verts stay on the ground) to the spot that opens
    every face round it past lim, turning none of them more than about 25 degrees."""
    best = None
    nf = f.normal.copy()
    for v in f.verts:
        if v in locked:
            continue
        ring = list(v.link_faces)
        old = [x.normal.copy() for x in ring]
        es = [(w.co - v.co).normalized() for w in f.verts if w is not v and (w.co - v.co).length > 1e-9]
        dirs = [nf, -nf] + es + [-x for x in es] + [nf.cross(x).normalized() for x in es] + \
               [-nf.cross(x).normalized() for x in es]
        home = v.co.copy()
        for s in POLISH_STEPS:
            for dv in dirs:
                p = home + dv * s
                if abs(home.z) < 1e-4:
                    p.z = home.z
                v.co = p
                worst, ok = math.pi, True
                for x, n0 in zip(ring, old):
                    x.normal_update()
                    if x.normal.length < 1e-9 or x.normal.dot(n0) < 0.9:
                        ok = False
                        break
                    worst = min(worst, m011._fmin(x))
                if ok and worst > lim and (best is None or s < best[0] or (s == best[0] and worst > best[1])):
                    best = (s, worst, v, p.copy())
            v.co = home
            for x in ring:
                x.normal_update()
            if best:
                break
    if best:
        best[2].co = best[3]
        for x in best[2].link_faces:
            x.normal_update()
        return True
    return False


def _polish(o):
    """Stage 2: every face a triangle, then each corner under POLISH_LIM opened by a near-flat flip or a small nudge
    of a corner that is not on a seam wall (the wall rows are colour geometry, so they stay exactly where stage 1
    put them); the origin back at the bottom centre (sockets follow). Returns counts and what is left."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    split = m012._tri_quads(bm)
    locked = _wall_verts(o, bm)
    lim = math.radians(POLISH_LIM)
    log = {"split": split, "flip": 0, "nudge": 0}
    for _ in range(8):
        bad = sorted((f for f in bm.faces if m011._fmin(f) < lim), key=m011._fmin)
        if not bad:
            break
        changed = False
        for f in bad:
            if not f.is_valid or m011._fmin(f) >= lim:
                continue
            if _flip_thin(bm, f, lim):
                log["flip"] += 1
                changed = True
            elif _nudge_free(bm, f, lim, locked):
                log["nudge"] += 1
                changed = True
        if not changed:
            break
    left = [f for f in bm.faces if m011._fmin(f) < lim]
    log["left"] = len(left)
    log["left_on_wall"] = sum(1 for f in left if any(v in locked for v in f.verts))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    me = o.data
    xs, ys, zs = ([v.co[i] for v in me.vertices] for i in range(3))
    off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
    if off.length > 1e-6:
        for v in me.vertices:
            v.co -= off
        for c in o.children:
            c.location -= off
    me.update()
    log["min_deg"] = m012._thin(o, POLISH_LIM)["min_deg"]
    return log


def _uv(o):
    """Stage 3: the UVs re-made on the polished mesh (45 degree Smart UV islands, each re-unwrapped ANGLE_BASED,
    margin 0.008), any folded faces cut free and unwrapped again (m012._uv_unfold); returns M.uv_stats."""
    M.smart_uv(o, **UV)
    cut = m012._uv_unfold(o)
    s = M.uv_stats(o)
    s["cut_free"] = cut
    return s


def _inner_shells(o):
    """Shells of o lying inside another of its shells (ray parity from each shell's centre): hidden geometry."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    tree = BVHTree.FromBMesh(bm)
    inner = 0
    for k in range(n):
        fs = [f for f in bm.faces if ids[f.index] == k]
        c = sum((f.calc_center_median() for f in fs), Vector()) / len(fs)
        own = {f.index for f in fs}
        hits, p, d = 0, c.copy(), Vector((0.31, 0.17, 0.93)).normalized()
        for _ in range(200):
            loc, _, idx, _ = tree.ray_cast(p, d)
            if loc is None:
                break
            hits += idx not in own
            p = loc + d * 1e-4
        inner += hits % 2
    bm.free()
    return inner


def _self_hits(o):
    """Pairs of faces that cross each other without sharing a vertex (interpenetration left by the unions)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    n = 0
    for a, b in tree.overlap(tree):
        if a < b and not set(bm.faces[a].verts) & set(bm.faces[b].verts):
            n += 1
    bm.free()
    return n


# ---- pieces, hero --------------------------------------------------------------------------------------------------
def piece_obj(piece):
    """One shell piece as a temporary build-frame object: outer x sector - cutters - hollow, floor-cut."""
    o = _outer_obj(f"_m009_piece_{piece}")
    _bool(o, _tmp("_m009_cone", lambda a: cone(a, piece)), "INTERSECT")
    # the hollow before the cutters (the other order collapsed the Back piece to two faces in the exact solver);
    # self-intersection on for the cutters: at the lobe seam's corner the wide lids above the surface overlap
    _bool(o, _tmp("_m009_hollow", hollow), "DIFFERENCE")
    _bool(o, _tmp("_m009_cut", cutters), "DIFFERENCE", self_x=True)
    if min((o.matrix_world @ v.co).z for v in o.data.vertices) < 0:
        _floor(o)
    M.union_loose(o)
    return o


def hero_obj(rock):
    """The hero as a temporary build-frame object: (outer - cutters) + core, floor-cut with the core's disc, plus
    the impact rim (copies of the finished rock part)."""
    o = _outer_obj("_m009_hero")
    _bool(o, _tmp("_m009_cut", cutters), "DIFFERENCE", self_x=True)
    _bool(o, _tmp("_m009_core", lambda a: core(a, HOT)), "UNION")
    _floor(o, split=_core_section())
    rim = _tmp("_m009_rim", lambda a: [_paste(a, rock, m @ _rock_frame(rock)) for m in _rim_matrices()])
    for p in M.split_loose(rim) + [rim]:
        _bool(o, p, "UNION")
    M.union_loose(o)
    return o


def _rock_frame(rock):
    return Matrix.Identity(4)       # the rock part's mesh is bottom-centred at its origin already


def _cleanup_tmp():
    for o in [o for o in bpy.data.objects if o.name.startswith("_m009_")]:
        me = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if me and me.users == 0:
            bpy.data.meshes.remove(me)


# ---- stages 5+6: lighting and VFX (M009_spec.md, "Stage 5+6") -------------------------------------------------------
# The glow itself is the four Neon keys (ember, core, core_x_hot_50, hot; emission NEON); the lip stays solid. Blender
# lights don't export: the in-game light is the heat_glow sockets' PointLights. Every socket is a point (az, el, out)
# measured from C0: `out` studs beyond the main mass's surface (_rho) along that direction, so it sits in the open
# just outside a seam lip (BVH clearance from the hero, measured: see the spec).
# Lights. Warm, small and shadowed (the old one sat inside the meteor without shadows and lit the whole rim peach):
# one, 0.8 out from the lobe seam's widest jog (the sheet's brightest crack, facing the front three-quarter view).
# Flicker on (a lava seam, not a crystal). Range x vfx_scale (1.0 here). No second light at the back: a dimmer one
# (0.4, range 5, shadows) outside the back-right seam changed the rear / rear34 shell, crack and rocks by at most 1
# level in the preview; the Neon seams carry the rear views, and a shadowed PointLight is not free in Roblox.
SEAM_LIGHT = dict(color="#FF7A22", brightness=0.7, range=6.0, flicker=True, shadows=True)
# Heat shimmer: faint, small soft-glow puffs drifting up off the seam (the sheet draws no halo, smoke or bloom: size
# 0.5-0.8 and 0.78+ transparent, so the crack always shows through), in the sheet's crack orange (#FC8917 -> #F75610).
HEAT_FX = {"name": "Heat", "texture": "glow_soft", "color": ["#FC8917", "#F75610"], "size": [0.5, 0.8],
           "transparency": [0.78, 1.0], "lifetime": [0.8, 1.3], "rate": 2.5, "speed": [0.4, 0.7], "spread": 8,
           "light_emission": 1.0}
# Embers: sparse, small hot-orange dots rising off the seam (rate 1.5-3, size 0.18 -> 0.05, spread 20; the spawn box
# a 0.3 cube, so every spawn point is within 0.26 of the socket, which is about 0.3 out from the lip).
EMBER_FX = {"name": "Embers", "texture": "ember_dot", "color": ["#FDBD40", "#F75610"], "size": [0.18, 0.05],
            "transparency": [0.0, 1.0], "lifetime": [1.0, 2.0], "speed": [1.0, 2.0], "spread": 20,
            "light_emission": 1.0, "drag": 0.8, "acceleration": [0, 0.8, 0], "shape": [0.3, 0.3, 0.3]}
# (kind, (az, el, out), heat/ember emitter overrides, light or None). Shapes are Roblox (x, height, depth); every
# box's spawn points sampled on a 5^3 grid lie outside the hero (BVH parity; see the spec).
SOCKETS = (
    ("heat_glow", (242, 3, 0.8), {"shape": [0.5, 0.4, 0.5]}, SEAM_LIGHT),     # lobe seam: the descent's widest jog
    ("heat_glow", (222, 18, 0.4), {"rate": 2.0, "shape": [0.5, 0.3, 0.5]}, None),   # lobe seam: the upper run
    ("heat_glow", (406, 9, 0.6), {"rate": 1.5, "shape": [0.5, 0.4, 0.5]}, None),    # back-right seam's jog (rear views)
    ("embers", (218, 18, 0.3), {"rate": 3.0}, None),                           # lobe seam: the upper run
    ("embers", (302, 42, 0.3), {"rate": 1.5}, None),                           # front-right seam: its top
    # (moved with the seam's 9 degree turn, verifier round 1)
)


def _fx_point(az, el, out):
    d = _dir(az, el)
    return tuple(round(c, 3) for c in C0 + d * (_rho(d) + out))


def _vfx():
    """Stages 5+6: the hero's sockets (kind, build-frame loc, overrides) for M.mk's fx (SOCKETS)."""
    fx = []
    for kind, at, em, light in SOCKETS:
        base = HEAT_FX if kind == "heat_glow" else EMBER_FX
        ov = {"emitters": [dict(base, **em)]}
        if kind == "heat_glow":
            ov["light"] = dict(light) if light else None
        fx.append((kind, _fx_point(*at), ov))
    return fx


# ---- stage 4: materials, colour and texture ------------------------------------------------------------------------
# Applied to the finished meshes (after stage 2's polish and stage 3's UVs: no geometry or UV changes). Every field is
# a position in the shared build frame (mesh coords + the object's m009_offset), so the shell piece and the hero's
# shell carry the same colouring where they coincide. No colour is ever chosen by which way a face points.
#
# The crack, from the outside in, by depth below the local outer surface (the cutters' face rows are the depth bands):
#   shell -> (soot: the shell fragments along an open seam, a step or two darker) -> seam_lip (0-0.25 T, the lip
#   chamfer: dark, unlit) -> seam_ember (0.25-0.55 T: dark ember red, faint glow) -> core (0.55 T-T: the orange walls,
#   Neon) -> the hot floor (the core's surface between the walls, Neon). The floor is hot where the gap is wide and
#   cools to core orange towards each tapered end (by the seam's local gap G).
# broad light / dark facet patches: noise at each hull facet's centre (so a facet is one colour on the hero and the
# piece), with a dead zone round 0 so plain shell stays the commonest tone (about 45 % plain, 25-30 % each way)
# (bias: verifier round 1, the front view and the top facets rendered 12 levels under the sheet; a lift of the whole
# noise field gives more light facets, by position as before)
SHELL_TONE = dict(scale=0.3, seed=9041, amp=2.0, dead=0.1, bias=0.15)
SOOT = (0.3, 0.9, 0.35)     # shell fragments whose centre is within 0.3 of an open seam's lip: tone -0.35, fading
                            # out by 0.9 studs (and with the gap: none where the seam has closed)
GROUND = (1.2, 2.4, 0.25)   # the meteor's foot among the rocks: tone -0.25 below z 1.2, fading out by z 2.4
HOT_G = (0.30, 0.46)        # the floor: core orange where G <= 0.30, core_x_hot_50 between, hot where G >= 0.46
# verifier round 1: with crack B widened, front34 and front showed 6.8 % / 7.3 % orange against the sheet's 3.6 % /
# 3.7 %, most of it the wide lobe seam's walls. Its walls below the lip glow a deep red instead (lip -> deep red ->
# its graded orange / hot floor): still a depth gradient, but only the floor counts as orange. Crack B (FrontRight)
# and the back seams (the rear views' orange share already matched) keep the full lip -> ember -> core walls.
# {seam: {band key: (cooler key, where the seam's local gap G is below this)}}. Tried: the lobe's whole walls deep
# red: orange share 4.6 / 4.7 % (VFX on), but the hero's main crack went deep red (median #9B301D against the sheet's
# #E24515); only its ember band: 6.1 / 6.3 %, barely cooler (the ember counts as orange). So the ember band goes deep
# red all along, and the core band too except where the seam is widest (G >= 0.47: its jogs, over the hot floor).
# Thresholds 0.40 / 0.43 / 0.47 / 0.52 gave front34 5.1 / 4.9 / 4.7 / 4.5 % (VFX off); the crack's median is deep red
# with any of them (the sheet's crack is narrower and orange; ours is wider, so its glow has to be cooler to cover a
# like area).
# Coordinator's call (cracks must be apparent): the ember band only, so the lobe crack's median stays orange.
SEAM_COOL = {"Lobe": {EMBER: (SEAM_DEEP, 9.0)}}
ROCK_TONE = dict(scale=0.75, seed=9051, amp=1.6, dead=0.08)     # broad light / dark patches (the rock's own frame)
ROCK_GROUND = (0.15, 0.4, 0.0)  # (a darker ground band by height: off. On a 44-tri stone the low ring is the
                                # down-facing ring, so it read as painted shade: K.check corr 0.82)
ROCK_VAR = (0.92, 1.07)     # each rim copy's overall Tint (the sheet's rocks vary in tone, rock to rock)
# the core part: height + broad noise, ranked by area (noise strong enough that the hot patch is an irregular
# group of upper facets, not a band: up 1.0 / noise 0.5 drew a saw-toothed hot cap)
# (up 0.7 / ranks 0.64, 0.8 put the big top facet hot and the part rendered #FF901C against the sheet's #FA601D)
CORE_FIELD = dict(up=0.4, noise=1.0, scale=0.35, seed=9061)
CORE_RANKS = (0.22, 0.76, 0.88)     # below: deep; then core; then core_x_hot_50; above: hot (the hot upper patch)
MOTTLE = {"shell": dict(amp=0.08, scale=0.42, seed=9043), "cut": dict(amp=0.05, scale=0.5, seed=9044),
          "rock": dict(amp=0.06, scale=0.9, seed=9045)}
# K.check's baked-shading test correlates colour with facing; the seam walls' depth bands are steep faces whose
# colour follows their depth, so they may trip it. Waived with this reason where it does:
SHADING_OK = ("seam wall bands graded by depth below the lip (the sheet's lip -> ember -> orange -> hot gradient, "
              "M009_spec.md stage 4); the shell's patches follow broad position noise, not facing")


def _mix(k1, k2, t):
    """K.mix_key, keeping the parents' emission (mix_key makes every in-between key solid): a mix of two Neon keys
    stays Neon."""
    key = K.mix_key(k1, k2, t)
    if key not in (k1, k2):
        f = K.fk()
        e1, e2, e = f.palette_entry(k1), f.palette_entry(k2), f.palette_entry(key)
        emit = e1[3] + (e2[3] - e1[3]) * round(t, 2)
        if emit > 0 and e[3] != emit:
            K.set_colour(key, e[0], rough=e[1], emit=emit)
    return key


def _ladder(base, dark, light, t):
    """A tone in -1..1 -> base, or a quarter-step mix towards dark (t < 0) or light (t > 0)."""
    t = round(max(-1.0, min(1.0, t)) * 4) / 4
    return base if t == 0 else _mix(base, light, t) if t > 0 else _mix(base, dark, -t)


def _dead(n, tone):
    """amp x the noise beyond a dead zone round 0 (tone: amp, dead)."""
    return tone["amp"] * math.copysign(max(0.0, abs(n) - tone["dead"]), n)


def _ramp(x, a, b):
    """0 at a, 1 at b, clamped (a > b allowed)."""
    return min(1.0, max(0.0, (x - a) / (b - a)))


def _hull_facets():
    """(normal, offset, centre) of every facet of the Main and Lobe hulls: the outer surface's facets."""
    g = _geo()
    if "facets" not in g:
        out = []
        for k in ("main", "lobe"):
            bm = _hull_bm(g[k])
            for n, h in g[k + "_pl"]:
                vs = [v.co.copy() for v in bm.verts if abs(n.dot(v.co) - h) < 1e-4]
                out.append((n, h, sum(vs, Vector()) / len(vs)))
            bm.free()
        g["facets"] = out
    return g["facets"]


def _facet_centre(f, c):
    """The centre of the outer hull facet the face f (build-frame centre c) lies on, or c if none. (Loose
    tolerances: the sliver passes and the polish tilt small fragments by a few degrees and move them by up to a few
    hundredths of a stud.)"""
    best = None
    for n, h, fc in _hull_facets():
        s = n.dot(f.normal) - abs(n.dot(c) - h)
        if n.dot(f.normal) > 0.95 and abs(n.dot(c) - h) < 0.08 and (best is None or s > best[0]):
            best = (s, fc)
    return best[1] if best else c


def _seams():
    """Every open seam's centre line as unit directions from C0 (1 degree apart) with the gap G there."""
    g = _geo()
    if "seam_kd" not in g:
        pts, names = [], []
        for name, nodes in OPEN_SEAMS.items():
            for run in _runs(_resample(nodes, step=1.0)):
                pts += run
                names += [name] * len(run)
        kd = KDTree(len(pts))
        for i, (d, _) in enumerate(pts):
            kd.insert(d, i)
        kd.balance()
        g["seam_kd"], g["seam_g"], g["seam_name"] = kd, [x for _, x in pts], names
    return g["seam_kd"], g["seam_g"]


def _seam_name(c):
    """The open seam nearest c (by direction from C0)."""
    kd, _ = _seams()
    return _geo()["seam_name"][kd.find((c - C0).normalized())[1]]


def _cool(p, faces):
    """SEAM_COOL: on the listed seams, the wall bands' keys swapped for cooler ones (faces picked by nearest seam)."""
    n = 0
    for f in faces:
        swap = SEAM_COOL.get(_seam_name(p.at(f)), {}).get(p.key(f))
        if swap and _seam_at(p.at(f))[1] < swap[1]:
            f.material_index = p._mi(swap[0])
            n += 1
    return n


def _seam_at(c):
    """(distance over the surface from c to the nearest open seam's lip, the gap G there) in studs."""
    kd, gs = _seams()
    d = (c - C0).normalized()
    _, i, chord = kd.find(d)
    g = gs[i]
    return chord * _rho(d) - g / 2, g


def _centre(p, g):
    a = sum(f.calc_area() for f in g) or 1.0
    return sum((f.calc_center_median() * f.calc_area() for f in g), Vector()) / a + p.off


def _tint_groups(p, groups, amp, scale, seed, extra=None):
    """Broad Tint mottling, one value per facet group (each facet stays one flat tone: no per-triangle confetti):
    1 + amp x broad noise at the group's centre, times extra(group) if given."""
    nf = K.noise_field(scale=scale, seed=seed)
    for g in groups:
        k = 1.0 + amp * 1.6 * nf(_centre(p, g))
        if extra:
            k *= extra(g)
        for f in g:
            for l in f.loops:
                t = l[p.tint_layer][0] * k
                l[p.tint_layer] = (t, t, t, 1.0)


def _shell_tone(c_facet, c_frag, nf):
    """The shell's tone at a fragment: broad patches (noise at its hull facet's centre), minus the soot along an
    open seam and the ground band at the foot (both at the fragment's own centre)."""
    t = _dead(nf(c_facet), SHELL_TONE) + SHELL_TONE["bias"]
    dl, g = _seam_at(c_frag)
    s0, s1, sd = SOOT
    t -= sd * _ramp(dl, s1, s0) * min(1.0, g / 0.3)
    z0, z1, gd = GROUND
    t -= gd * _ramp(c_frag.z, z1, z0)
    return t


def _colour_shell(p, faces):
    """The shell's outside: per coplanar fragment, a step on the shell ladder (dark .. plain .. light), then Tint."""
    nf = K.noise_field(scale=SHELL_TONE["scale"], seed=SHELL_TONE["seed"])
    groups = m012._facets(faces)
    for g in groups:
        c = _centre(p, g)
        key = _ladder(SHELL, SHELL_DARK, SHELL_LIGHT, _shell_tone(_facet_centre(g[0], c), c, nf))
        mi = p._mi(key)
        for f in g:
            f.material_index = mi
    _tint_groups(p, groups, **MOTTLE["shell"])
    return len(groups)


def _colour_cut(p, faces):
    """Shell-thickness cut faces: the grey "Metal Core (Inner Faces)" swatch, broad Tint only."""
    _tint_groups(p, m012._facets(faces), **MOTTLE["cut"])


def _paint(o, off):
    """m011._Paint with every Tint reset to 1 first (the booleans interpolate the corner colours, so a few split
    faces arrived with uneven Tint; this way each face ends up one flat tone and the pass is repeatable)."""
    p = m011._Paint(o, off=off)
    for f in p.bm.faces:
        for l in f.loops:
            l[p.tint_layer] = (1.0, 1.0, 1.0, 1.0)
    return p


def _counts(p):
    out = {}
    for f in p.bm.faces:
        out[p.key(f)] = out.get(p.key(f), 0) + 1
    return out


def colour_piece(o, off):
    """A shell piece: the shell's outside and cut faces, the seam walls' depth bands as built, the hollow (the
    piece's inner face, which lies on the core) core_deep."""
    p = _paint(o, off)
    by = {}
    for f in p.bm.faces:
        by.setdefault(p.key(f), []).append(f)
    _colour_shell(p, by.get(SHELL, []))
    _colour_cut(p, by.get(SHELL_CUT, []))
    hol = _geo()["hollow_pl"]
    deep = p._mi(CORE_DEEP)
    walls = list(by.get(EMBER, []))
    for f in by.get(CORE, []):
        c = p.at(f)
        d = (c - C0).normalized()
        if abs(_span(hol, C0, d)[1] - (c - C0).length) < 0.03:
            f.material_index = deep
        else:
            walls.append(f)
    _cool(p, walls)
    out = _counts(p)
    p.done()
    return out


def colour_hero(o, off, rock):
    """The hero: the shell, the cut floor ring, the hot floor graded along each seam by its gap, and the rim rocks
    (each copy takes the rock part's own colouring, through the copy's transform, times its own Tint)."""
    p = _paint(o, off)
    by = {}
    for f in p.bm.faces:
        by.setdefault(p.key(f), []).append(f)
    _colour_shell(p, by.get(SHELL, []))
    _colour_cut(p, by.get(SHELL_CUT, []))
    # the floor disc (the core's underside, on the ground) takes a deeper glow than the core (the sheet's underside
    # core is #E54A18, a step deeper); the walls of the SEAM_COOL seams cool
    # (on the ember key, not core_deep: one fewer Neon piece on the hero, for a face never seen in game)
    disc = [f for f in by.get(CORE, []) if all(abs(v.co.z + p.off.z) < 1e-4 for v in f.verts)]
    for f in disc:
        f.material_index = p._mi(EMBER)
    ds = set(disc)
    _cool(p, by.get(EMBER, []) + [f for f in by.get(CORE, []) if f not in ds])
    lo, hi = HOT_G
    floor = {}
    for f in by.get(HOT, []):
        t = _ramp(_seam_at(p.at(f))[1], lo, hi)
        k = CORE if t < 0.25 else HOT if t > 0.75 else _mix(CORE, HOT, 0.5)
        if k == CORE:       # the cooled seams' floor ends cool on to their walls' deep red
            k = SEAM_COOL.get(_seam_name(p.at(f)), {}).get(CORE, (CORE,))[0]
        floor[k] = floor.get(k, 0) + 1
        f.material_index = p._mi(k)
    # the rim: the rock part's colouring per copy (nearest copy surface, then the part face under the point)
    part = rock.data
    pkeys = [m.get("flintkit_key") or m.name[3:] for m in part.materials]
    ptint = part.color_attributes.get("Tint")
    tint_of = [1.0] * len(part.polygons)
    if ptint:
        for pl in part.polygons:
            tint_of[pl.index] = ptint.data[pl.loop_start].color[0]
    tree = BVHTree.FromPolygons([v.co for v in part.vertices], [list(pl.vertices) for pl in part.polygons])
    mats = _rim_matrices()
    invs = [m.inverted() for m in mats]
    rng = random.Random(9052)
    var = [rng.uniform(*ROCK_VAR) for _ in mats]
    for f in by.get(IMPACT, []):
        c = p.at(f)
        best = None
        for i, mi in enumerate(invs):
            loc, _, idx, dist = tree.find_nearest(mi @ c)
            # (distance in the copy's own frame, scaled back roughly to studs)
            dw = ((mats[i] @ loc) - c).length if loc is not None else 1e9
            if best is None or dw < best[0]:
                best = (dw, i, idx)
        _, i, idx = best
        f.material_index = p._mi(pkeys[part.polygons[idx].material_index])
        t = tint_of[idx] * var[i]
        for l in f.loops:
            l[p.tint_layer] = (t, t, t, 1.0)
    out = _counts(p)
    out["_floor"] = floor
    p.done()
    return out


def colour_rock(o):
    """The Impact Rock part (its own frame): broad light / dark patches and a darker ground-contact band, by
    position, per facet; then Tint."""
    p = _paint(o, (0, 0, 0))
    faces = list(p.bm.faces)
    H = max(v.co.z for v in p.bm.verts) or 1.0
    nf = K.noise_field(scale=ROCK_TONE["scale"], seed=ROCK_TONE["seed"])
    z0, z1, gd = ROCK_GROUND
    groups = m012._facets(faces)
    for g in groups:
        c = _centre(p, g)
        t = _dead(nf(c), ROCK_TONE) - gd * _ramp(c.z / H, z1, z0)
        mi = p._mi(_ladder(IMPACT, IMPACT_DARK, IMPACT_LIGHT, t))
        for f in g:
            f.material_index = mi
    _tint_groups(p, groups, **MOTTLE["rock"])
    out = _counts(p)
    p.done()
    return out


def colour_core(o, off):
    """The Metal Core part: deep orange low down, core orange, and a hot patch over the upper facets (height plus
    broad noise, ranked by area, one key per facet). All Neon: no Tint."""
    p = _paint(o, off)
    faces = list(p.bm.faces)
    zs = [v.co.z + p.off.z for v in p.bm.verts]
    z0, z1 = min(zs), max(zs)
    nf = K.noise_field(scale=CORE_FIELD["scale"], seed=CORE_FIELD["seed"])
    groups = []
    for g in m012._facets(faces):
        c = _centre(p, g)
        groups.append((CORE_FIELD["up"] * (c.z - z0) / (z1 - z0) + CORE_FIELD["noise"] * nf(c),
                       sum(f.calc_area() for f in g), g))
    groups.sort(key=lambda x: x[0])
    total = sum(x[1] for x in groups)
    acc = 0.0
    r0, r1, r2 = CORE_RANKS
    for _, area, g in groups:
        r = (acc + area / 2) / total
        acc += area
        k = CORE_DEEP if r < r0 else CORE if r < r1 else _mix(CORE, HOT, 0.5) if r < r2 else HOT
        mi = p._mi(k)
        for f in g:
            f.material_index = mi
    out = _counts(p)
    p.done()
    return out


def colour_all(hero, shell, core_o, rock, pieces, offs):
    """Stage 4 on every object (parts first: the hero's rocks copy the rock part's colouring)."""
    out = {"IronMeteorImpactRock": colour_rock(rock)}
    out["IronMeteorCore"] = colour_core(core_o, offs["core"])
    out["IronMeteorShellPiece"] = colour_piece(shell, offs["shell"])
    out["IronMeteorDeposit"] = colour_hero(hero, offs["hero"], rock)
    for p, o in pieces.items():             # the exploded render's build-frame pieces (not exported)
        colour_piece(o, (0, 0, 0))
    _glow_mats()
    probs = K.check([hero, shell, core_o, rock])
    for o in (hero, shell):
        if any(x.startswith(o.name + ":") and "lighting is painted" in x for x in probs):
            o["kit_shading_ok"] = SHADING_OK
        elif "kit_shading_ok" in o:
            del o["kit_shading_ok"]
    return out


NOTES = {
    "IronMeteorDeposit":"iron meteorite deposit: a big dark faceted meteor split into thick shell pieces along jagged "
                         "seams; the seams are real gaps through the shell, dark at the lip and glowing orange down "
                         "to the metal core at their floor; a smaller lobe at the front left, a ring of pale impact "
                         "rocks round the foot; seams and core glow",
    "IronMeteorShellPiece": "Rock Shell Piece (reusable): a thick curved segment of the meteor's shell, dark rock "
                            "outside, orange inner face, the shell thickness showing at its cut ends and stepped "
                            "seam walls along its open edges",
    "IronMeteorCore": "Metal Core: faceted glowing orange ball, the hollow the shell pieces close round",
    "IronMeteorImpactRock": "Impact Rock (reusable): pale faceted stone of the impact rim",
}
# stage 3: 45 degree islands kept on every object (min_angle; smart_uv's fallback took the hero down to 35 degrees and
# 416 islands), the few faces the unwrap folds cut free by _uv instead (hero: 5 faces, 348 islands)
UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)


def build(render=True):
    M.coll(NUM, TITLE)
    palette()
    _GEO.clear()
    _cleanup_tmp()
    rock = M.mk(SHEET, "IronMeteorImpactRock", impact_rock, subject=TITLE, role="part",
                notes=NOTES["IronMeteorImpactRock"], budget=1000, collision="hull")
    core_o = M.mk(SHEET, "IronMeteorCore", core_part, subject=TITLE, role="part", notes=NOTES["IronMeteorCore"],
                  budget=1000, collision="hull")
    pieces = {p: piece_obj(p) for p in PIECES}
    cleaned = {}
    for p, o in pieces.items():
        cleaned[p] = _sliver_pass(o)
    shell = M.mk(SHEET, "IronMeteorShellPiece", lambda a: _paste(a, pieces[EXPORT_PIECE]), subject=TITLE,
                 role="part", notes=NOTES["IronMeteorShellPiece"], budget=1000, collision="hull")
    h_tmp = hero_obj(rock)
    cleaned["hero"] = _sliver_pass(h_tmp)
    hero = M.mk(SHEET, "IronMeteorDeposit", lambda a: _paste(a, h_tmp), subject=TITLE, role="hero",
                notes=NOTES["IronMeteorDeposit"], budget=4000, collision="hull", fx=_vfx())
    # build frame = mesh coords + offset (each object's bottom centre in the build frame, as mk re-centred it; the
    # later re-centring by finish / polish moves under 0.01 stud)
    offs = {"hero": _bottom_centre([v.co for v in h_tmp.data.vertices]),
            "shell": _bottom_centre([v.co for v in pieces[EXPORT_PIECE].data.vertices]),
            "core": _bottom_centre(_geo()["core"])}
    bpy.data.objects.remove(h_tmp, do_unlink=True)
    objs = [hero, shell, core_o, rock]
    polish, uvs, audits = {}, {}, []
    for o in objs:
        M.finish(o, union=False, uv=False)
        polish[o.name] = _polish(o)                 # stage 2
        uvs[o.name] = _uv(o)                        # stage 3
        a = M.audit(o)
        a["inner_shells"], a["self_hits"] = _inner_shells(o), _self_hits(o)
        audits.append(a)
    for k, o in (("hero", hero), ("shell", shell), ("core", core_o)):
        o["m009_offset"] = tuple(offs[k])
    colour = colour_all(hero, shell, core_o, rock, pieces, offs)    # stage 4
    M.display(NUM, objs, TITLE)
    out = {"audit": audits, "polish": polish, "uv": uvs, "cleaned": cleaned, "colour": colour,
           "problems": K.check(objs)}
    try:
        if render:
            out["views"] = render_views(objs, pieces)
    finally:
        _cleanup_tmp()
        out["dropped"] = _drop_unused(objs)
    return out


def _bottom_centre(pts):
    return Vector([(min(p[i] for p in pts) + max(p[i] for p in pts)) / 2 for i in range(2)]
                  + [min(p[2] for p in pts)])


def _drop_unused(objs):
    """Purge M009's orphans: meshes named after its objects or its temporaries, and unused FB_m009_ materials.
    Returns what went."""
    names = {o.name for o in objs}
    calib = _drop_calib()           # first, so the keys only the calibration domes used go with the materials below
    meshes = [m for m in bpy.data.meshes if m.users == 0 and (m.name.split(".")[0] in names
                                                              or m.name.startswith("_m009_"))]
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m009_")]
    out = {"meshes": len(meshes), "calib_meshes": calib, "materials": sorted(m.name for m in mats)}
    for m in meshes:
        bpy.data.meshes.remove(m)
    for m in mats:
        bpy.data.materials.remove(m)
    for o in objs:
        if o.data.name != o.name and o.name not in bpy.data.meshes:
            o.data.name = o.name
    return out


# the exploded shot (the sheet: the five pieces pulled out round the core, the rim rocks below)
EXPL_PULL = 4.8          # each piece moves this far out from C0 along its sector's middle direction (horizontal part)
EXPL_CROWN = 4.2         # the crown rises this far (verifier round 1: at 3.2 / 2.8 the pieces nearly touched the core)
EXPL_LIFT = 3.0
EXPL_ROCKS = 10


def render_views(objs, pieces):
    hero, shell, core_o, rock = objs
    saved = M.explode(objs[1:], {})
    shown = []
    try:
        hx, hy = hero.location.x, hero.location.y
        base = Vector((hx + 40, hy, 0.0))
        core_o.location = base + Vector((0, 0, EXPL_LIFT))
        bpy.context.view_layer.update()
        # the core's centre in the world; each piece's C0 is put there, then pulled out along its sector
        ws = [core_o.matrix_world @ v.co for v in core_o.data.vertices]
        cc = Vector([(min(p[i] for p in ws) + max(p[i] for p in ws)) / 2 for i in range(3)])
        cc_build = Vector([(min(p[i] for p in _geo()["core"]) + max(p[i] for p in _geo()["core"])) / 2
                           for i in range(3)])
        loops = _loops()
        for p, o in pieces.items():
            mid = sum(loops[p], Vector()).normalized()
            pull = Vector((mid.x, mid.y, 0.0)).normalized() * EXPL_PULL if p != "Crown" else Vector((0, 0, EXPL_CROWN))
            o.location = cc - cc_build + pull
            shown.append(o)
        shell.location = (hx + 80, hy, 0)
        for i in range(EXPL_ROCKS):
            c = bpy.data.objects.new(f"_m009_expl_rock{i}", rock.data)
            rock.users_collection[0].objects.link(c)
            # two loose rows in front of and below the core, as on the sheet
            row, k = divmod(i, EXPL_ROCKS // 2)
            s = 0.85 + 0.4 * ((i * 7) % 5) / 4
            c.location = base + Vector((-8.0 + 16.0 * (k + 0.5 * row) / (EXPL_ROCKS // 2), -5.5 - 2.6 * row, 0.0))
            ang = 1.7 * i
            c.rotation_euler = (0, 0, ang * 1.7)
            c.scale = (s, s, s)
            shown.append(c)
        rock.location = (hx + 80 + 6, hy, 0)
        bpy.context.view_layer.update()
        # (the exported piece is the Lobe: its outside faces the front left, its hollow the back right)
        extra = {"exploded": ([core_o] + shown, -14, 22), "part_shell": ([shell], -45, 20),
                 "part_shell_in": ([shell], 140, 25), "part_core": ([core_o], -20, 12), "part_rock": ([rock], -20, 15)}
        return M.views(NUM, [hero], extra=extra)
    finally:
        for c in shown:
            if c.name.startswith("_m009_expl_"):
                bpy.data.objects.remove(c, do_unlink=True)
        M.restore(saved)
        M.display(NUM, objs, TITLE)
