"""011 Amethyst (references/011.png): a geode cave built from three reusable parts, as on the sheet's exploded view.

    import importlib, kit_models, m011; importlib.reload(kit_models); importlib.reload(m011); m011.build()

- Top Shell (AmethystShellTop): a thick hooded half-egg of stone. Its outside and inside are two faceted sheets on
  the same grid, joined at the mouth by a rounded lip three facets across (thick and round, never a knife edge) and
  underneath by a flat contact ring. One closed mesh, built directly (no booleans).
- Bottom Shell (AmethystShellBottom): the lower half of the same faceted stone egg (one convex rock: the user wants
  "a hollowed out stone/rock with amethyst in it"), its top the top shell's own contact ring behind the mouth and a
  low rounded lip in front, hollowed into a shallow rocky bowl round a small flat crystal seat.
- Crystal (AmethystShard): a doubly terminated six-sided crystal. The hero reuses it seven times, scaled, leaned and
  turned.

The hero is pasted together from the finished part meshes (each placed back into the shared build frame) and
unioned into one closed shell: the top shell sits exactly on the bottom shell's flat top (their coincident contact
faces cancel) and one exact self-union joins everything. Stage 2 cleanup (_clean): no slivers, specks, quads or
n-gons; see M011_spec.md. Stage 3 UVs: seams from Smart UV islands, unwrapped angle-based (UV). The R03 kit sheet owns AmethystTopShell/BottomShell/Crystal, hence these names.
Stage 4 colour (palette, colour_part, _crystal_light): calibrated keys blended across bands of faces by position
fields (never by facing) plus broad Tint mottling, applied to the finished meshes so geometry and UVs stay as they
were. The parts show bare stone as the sheet's exploded views do; the assembled hero adds the crystals' violet light
in the cave and at the seat. Targets and re-measures are in M011_spec.md.
Stage 5 lighting: no emissive faces (the crystals are lit, not luminous); one soft violet Studio PointLight in the
cave (STUDIO_LIGHT).
Stage 6 VFX: the hero carries that light as a crystal_glow socket in the cave (CAVE_LIGHT) and four ore_glint
sockets of sparse violet twinkles boxed tight round the lit crystals' tips (GLINTS); see _vfx.
"""
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector, noise
from mathutils.geometry import intersect_line_line, intersect_point_line
from mathutils.kdtree import KDTree

import kit_mcp as K
import kit_models as M

NUM, TITLE, SHEET = 11, "Amethyst", "M011"
LIGHT, MID, DARK = "m011_crystal_light", "m011_crystal_mid", "m011_crystal_dark"
ROCK, CAVE = "m011_rock", "m011_cave"
ROCK_COOL = "m011_rock_cool"      # cool grey weathering
CAVE_DEEP, GLOW = "m011_cave_deep", "m011_seat_glow"          # dark violet deep cave; violet bleed at the crystal roots
# the part builders hand out ROCK (outside) and CAVE (inside); stage 4 paints both as stone on the parts and uses CAVE
# and CAVE_DEEP only for the assembled hero's cave

# ---- shared build frame (studs; front is -Y, ground z = 0) --------------------------------------------------------
ZC = 4.2                    # contact plane: the top shell sits on the bottom shell's flat walls here
ZF = 1.6                    # the crystal seat: the bowl's flat floor inside the bottom shell
CENTRE = Vector((0.0, 0.6, ZC))
OUTER = (5.2, 4.3, 5.2)     # the top shell's outside: a full half-egg (x, y, z radii) standing on the contact plane
INNER = (3.95, 2.95, 3.8)   # its inside (the cave): walls about 1.25 at the sides, 1.35-1.4 at the back and top
INNER_BUMP = 0.3            # the cave's lumps, as a fraction of the outside's (a calm ceiling, not crinkled)
SUPER = 2.3                 # superellipsoid exponent: a fuller, broader dome than a plain ellipsoid
# The mouth faces the front, the dome coming forward over the crystals (the sheet's side and front three-quarter
# views; the coordinator after round 2: tilting it up 24 degrees turned the rock into a chair-back). It opens about
# 75 % of the width, and its sides bend back just enough that a few crystal tips show past the hood from 45 degrees
# behind, while the arch's feet stay in front of the egg's widest section (no notches in the rear view).
MOUTH_FOOT = Vector((0.0, 0.0, ZC))    # the mouth plane passes through here (the arch's feet) ...
MOUTH_LEAN = 4.0                       # ... leans forward this many degrees at the top (a slight hood) ...
MOUTH_CURVE = 0.022                    # ... and bends back at the sides by this x x^2 (studs), see _mouth_d ...
MOUTH_CURVE_UP = 0.07                 # ... more so higher up (full from 3 studs above the contact plane)
FOOT = 0.5                  # the arch's feet, where the rim leaves the hood less than this above the contact plane,
                            # are put down flat onto it (see _put_down)
EGG_LOW = 5.2            # below the contact plane the egg tucks in towards the ground (ellipse of this height)
POLE = Vector((0.0, 0.6, 0.8)).normalized()    # the sheets' grid pole: up and back, inside the shell
COLS = 24                   # grid columns round the shell (even, and COLS / 2 a multiple of CAP: the crown ring);
                            # 24 since the wider mouth took most of 18 and left the back too coarse to meet the
                            # bottom shell without a crease
OUT_F = (0.36, 0.64, 0.86, 1.0)        # outside rows, as fractions of the way from the pole to the rim
IN_F = (1.0, 0.72, 0.4)                # inside rows, from the rim back to the pole
LIP = (0.22, 0.5, 0.78)                # rows across the lip, outside -> inside
LIP_BULGE = 0.55            # how far the lip rolls forward out of the mouth plane (its roundness)
BUMP = 0.035                # broad lumpiness of the shell (fraction of radius)
JITTER, JITTER_RIM, JITTER_CAVE = 0.13, 0.06, 0.03      # per-vertex wander (studs) of the sheets and of the lip
ROW_SLIDE = 0.07            # per-column slide of the outside's rows along the surface (fraction of pole -> rim)
CAP, CAP_F = 3, 0.16       # the dome's crown: 3 verts this far (fraction of pole -> rim) from the pole, one broad
                            # triangle between them; no radial pole (see top_shell)

# The bottom shell is the lower half of the same stone egg (verifier round 1 and the user: "a hollowed out
# stone/rock with amethyst in it"; the old ring of slabs read as columns, a tub and pebbles). Its front, in front of
# the mouth, is the hollow's low thick lip:
# verifier round 2: a low crescent, open at the front - the lip's top is LIP_LOW in the middle and rises (power
# LIP_RISE of the distance out to the side) towards the arch's feet at the contact plane; lumpy (LIP_LUMP), with a
# V notch (NOTCH: bottom height, half width, top height) cut down to about 2.2 in the middle
LIP_LOW, LIP_RISE, LIP_LUMP = 2.5, 1.6, 0.1
# (verifier round 3: the V notch now runs right through into the hollow - stopping at y -1.2 it left a thin slit)
NOTCH = (2.2, 1.5, 4.0, 1.0)  # bottom height, half width, top height, how far back it runs (y)
FRONT_IN = 0.86             # the lip's top is drawn in this much over a bevel ring, so it is rounded, not a ledge
# broad bulges low on the egg (angle round the centre in degrees, height, radius scale), as extra hull points
BULGES = ((-95.0, 1.2, 1.03),)
# Verifier round 3: lumps fused into the one rock (each a rounded hull, unioned with the egg, so the creases between
# them are real concave seams; they overlap the egg by most of their size, so they read as the rock's own bulges, not
# loose stones): (name, x, y, width, depth, height, turn, seed)
# - the front lip: four broad, chunky bulges, heavily overlapping each other and buried in the egg (only their fronts
#   stand a few tenths proud), the V-dip between the middle two, about 30 % of the height: lumpy rock, not a row of
#   separate stones (a first try with smaller, prouder lumps read exactly as that row of pebbles);
# - two low foot lumps at the rear corners, a crease above each, the egg tapering in between them.
LUMPS = (("LipL", -3.05, -1.55, 3.6, 3.4, 3.0, 0.5, 11071), ("LipCL", -1.45, -2.05, 3.3, 3.4, 2.8, 0.1, 11072),
         ("LipCR", 1.45, -2.0, 3.3, 3.4, 2.75, -0.1, 11073), ("LipR", 3.1, -1.5, 3.6, 3.4, 3.05, -0.5, 11074),
         ("FootL", -3.1, 2.3, 3.6, 3.2, 1.8, 0.7, 11077), ("FootR", 3.15, 2.25, 3.6, 3.2, 1.9, -0.7, 11078))
# (horn lumps at the trough's ends, rising past the contact plane, were tried in round 4: in the hero's side view they
# stood as a columnar block under the crystals - the round-1 fault - so the ends are the egg's own shoulders rising to
# the arch's feet instead)
LUMP_RINGS = [(0.0, 0.86, 5), (0.42, 1.0, 6), (0.8, 0.9, 5), (1.0, 0.64, 4)]      # broad facets, rounded over
HORN_RINGS = LUMP_RINGS

# crystals in the hero: (label, x, y, scale xy, scale z, lean x, lean y, twist) - all copies of AmethystShard
# (round 2: the side and front crystals are longer, so their prism bodies show over the lip; round 3: the cluster sits
# 0.5 further back, inside the hollow under the dome)
CRYSTALS = (("Main", 0.0, -0.55, 1.12, 1.43, 0.0, -0.12, 0.15),
            ("Left", -1.95, -0.7, 1.08, 1.25, -0.4, -0.28, 0.7),
            # (round 4: the right pair lean further out and forward, and FarRight is bigger, so the cluster shows
            # clearly past the hood's flank from 45 degrees behind, as on the sheet's rear three-quarter)
            ("Right", 1.9, -0.65, 0.96, 1.2, 0.46, -0.32, -0.35),
            ("FarRight", 2.9, -0.1, 0.88, 1.2, 0.55, -0.38, 0.9),
            ("BackLeft", -1.25, 0.65, 0.76, 1.08, -0.24, -0.04, 1.2),
            ("BackRight", 1.3, 0.7, 0.72, 1.02, 0.26, -0.04, 0.5),
            ("Front", -0.15, -0.75, 0.68, 0.78, 0.02, -0.5, 0.3))
# the shard, as the sheet's loose crystal: six-sided and fat (about half as wide as long), a root point, a straight
# body, a pointed tip
SHARD = dict(r=1.25, root=1.1, body=2.6, tip=1.5, seed=11011)
# stage 3 UVs (every part and the hero): Smart UV islands at 45 degrees, made seams and re-unwrapped angle-based,
# packed with an exact 0.008 margin. Plain Smart UV at 66 degrees stretched up to 2.4x and folded islands over
# themselves on the bottom shell and the hero; this is the least stretch with no overlaps (see M011_spec.md)
UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008)


def palette():
    # stage 4: base colours calibrated so the kit studio render matches the sheet AS RENDERED (K.calibrate; targets
    # and re-measures in M011_spec.md). Sheet swatches: light #C097DD, mid #924EC3, dark #5F3289, rock #9E8F8B.
    K.set_colour(LIGHT, "#A253DD", rough=0.35)
    K.set_colour(MID, "#7A31B3", rough=0.35)
    K.set_colour(DARK, "#5F2A9C", rough=0.35)
    K.set_colour(ROCK, "#90817F", rough=0.92)
    K.set_colour(ROCK_COOL, "#878185", rough=0.92)
    K.set_colour(CAVE, "#86606F", rough=0.94)
    K.set_colour(CAVE_DEEP, "#4A3C3C", rough=0.94)
    K.set_colour(GLOW, "#8A3FB0", rough=0.92)


# ---- stage 4: colour regions, blends and Tint mottling ------------------------------------------------------------
# Applied to each finished part mesh (after its cleanup and UVs, so no geometry or UV changes); the hero inherits
# them through _paste, then gets the crystals' violet light in the cave on its own (finer, boolean-split) faces. Every field is a
# position in the shared build frame (part mesh coords + the part's m011_offset), so the top and bottom shells'
# patterns run on across their junction. No colour is ever chosen by which way a face points.
WEATHER = dict(scale=0.22, seed=11061, left=0.04, level=0.45, width=1.4)    # warm rock <-> cool grey, broad patches
                                                    # (subtle: at most a 50 % cool mix, so no one lump reads grey)
# hero cave, by depth in from the rim (studs, plus CAVE_NOISE x broad noise): rim stone -> dusky cave stone over the
# first band, cave stone -> deep violet over the second
CAVE_BANDS = ((0.0, 0.8), (0.8, 3.6))
CAVE_NOISE = 0.5
CAVE_BACK = (2.2, 4.2, 0.78)  # past 2.2 studs in, the deep cave's Tint falls to 0.78 by 4.2 (the darkest back wall)
# violet bleed on the stone round each crystal's lower body: reach out from its surface (studs) in the cave and on
# rock, the band's width, how far up the body counts, and the heights it may colour (the seat and the bowl round it,
# never the underside or the hood)
BLEED = dict(cave=1.3, rock=0.4, width=1.6, rock_width=0.6, up=1.0, low=ZF - 0.3, high=ZF + 1.6)
CRYSTAL_BANDS = ((DARK, MID, 0.38, 0.4), (MID, LIGHT, 0.74, 0.32))   # root dark -> body mid -> tip light (axis)
BACK_TINT = {"BackLeft": 0.9, "BackRight": 0.9}            # crystals deep in the cave read a step darker
# K.check's baked-shading test correlates colour with facing; two real colour regions trip it here (measured against
# the sheet in M011_spec.md, stage 4), so they are waived with the reason:
SHADING_OK = {
    "AmethystShard": "amethyst colour zoning along the crystal's axis (root dark -> body mid -> tip light, the sheet's "
                     "three crystal swatches); it follows height on the upright crystal, not the light. Rendered tip/"
                     "body/base match the sheet's",
    "Amethyst": "the crystals' axis colour zoning (see AmethystShard)",
}
MOTTLE = {"stone":dict(amp=0.07, scale=0.45, jitter=0.015, seed=11063),
          "crystal": dict(amp=0.035, scale=0.9, jitter=0.01, seed=11064)}

# ---- stage 5: lighting (see M011_spec.md, "Stage 5") ---------------------------------------------------------------
# No emissive faces: the sheet's crystals are lit, not luminous (their shade facets go dark violet), and a Neon part
# (emission >= 1.0) would flatten their light/mid/dark facets into one glowing colour. The crystals' light on the
# stone (the violet cave and the seat bleed) is painted by stage 4. In Roblox the deep cave gets almost no sky light,
# so one soft violet PointLight in the cave keeps it reading violet rather than black. Stage 6 builds it as the
# hero's crystal_glow socket (CAVE_LIGHT below).
# pos: from the hero's origin (bottom centre of its footprint), Blender studs (x right, y back, z up); in the cave
# behind the crystal cluster, under the dome: the most open point of the cave (stage 1 round 3 re-placed it when
# the cluster moved back under the hood: the old point was 0.41 from the main crystal; this one is 1.74 clear of
# every surface, BVH). In Roblox axes (x, z, -y) that is (0.0, 4.8, -1.26). Range scales with the placed model.
STUDIO_LIGHT = dict(kind="PointLight", pos=(0.0, 1.26, 4.8), color="#B06AF5", brightness=1.0, range=10.0,
                    shadows=True)

# ---- stage 6: VFX sockets on the hero (see M011_spec.md, "Stage 6") ------------------------------------------------
# M.mk's fx locations are in the shared build frame; mk and finish carry the sockets along with the mesh's re-centring,
# so a socket ends up at (build frame - the hero's offset) in hero-local studs, exactly like the mesh.
# - crystal_glow: STUDIO_LIGHT, built. CAVE_LIGHT is its point in the build frame: STUDIO_LIGHT's hero-local point
#   plus the hero's offset (hero-local = build frame - (0.0001, 0.4948, 0), measured on the round-3 build), so it
#   lands at about (0.0, 1.26, 4.8).
CAVE_LIGHT = (0.0, 1.75, 4.8)
# - ore_glint: sparse violet twinkles on the bright crystal tips the sheet shows (the light swatch / tip facets
#   #C064F7). One socket per lit crystal, its emitter box fitted to the top of the tip pyramid only: the point and
#   the shoulder ring moved GLINT_TIP of the way up to it, padded by GLINT_PAD, so every spawn point is within about
#   half a stud of the crystal (verifier round 2: bigger boxes, and one box over two crystals, twinkled in the air).
#   (crystals, rate per second, particle peak size in studs). The back crystals sit in the cave's shade and the small
#   front one is low in the crack, so they get none. About 1.25 twinkles a second in all, each 0.5-0.8 s: under one
#   on screen at a time.
GLINTS = ((("Main",), 0.5, 0.6), (("Left",), 0.35, 0.45), (("Right",), 0.25, 0.45), (("FarRight",), 0.15, 0.35))
GLINT_TIP = 0.5
GLINT_PAD = 0.05
GLINT = {"name": "Glint", "texture": "spark_diamond", "color": ["#F6EAFF", "#C064F7"], "transparency": [0.1, 1.0],
         "lifetime": [0.5, 0.8], "speed": [0, 0], "spread": 0, "light_emission": 1.0, "rotation": [0, 90]}


class _Paint:
    """A finished object's mesh as the small part of flintkit.Asset that the colour passes use (bm, tint_layer,
    _mi), so the palette keys and Tint are edited in place without touching geometry or UVs."""

    def __init__(self, o, off=None):
        self.o = o
        self.bm = bmesh.new()
        self.bm.from_mesh(o.data)
        self.bm.faces.ensure_lookup_table()
        self.tint_layer = self.bm.loops.layers.float_color.get("Tint")
        self.off = Vector(off if off is not None else o.get("m011_offset", (0, 0, 0)))
        self.keys = [m.get("flintkit_key") or m.name[3:] for m in o.data.materials]

    def _mi(self, key):
        if key not in self.keys:
            self.o.data.materials.append(K.fk().material(key))
            self.keys.append(key)
        return self.keys.index(key)

    def key(self, f):
        return self.keys[f.material_index]

    def at(self, f):
        """Face centre in the shared build frame."""
        return f.calc_center_median() + self.off

    def done(self):
        """Write back with only the slots in use. (K.drop_unused_slots remaps the indices and then clears the
        slots, and clearing the slots zeroes every face's index, so a mesh whose unused slot is not the last one
        came out all one colour; here the slots are rebuilt first and the indices written after.)"""
        used = sorted({f.material_index for f in self.bm.faces})
        remap = {old: new for new, old in enumerate(used)}
        for f in self.bm.faces:
            f.material_index = remap[f.material_index]
        me = self.o.data
        keep = [me.materials[i] for i in used]
        me.materials.clear()
        for m in keep:
            me.materials.append(m)
        self.bm.to_mesh(me)
        self.bm.free()


def _grade(p, faces, k1, k2, value, level, width, steps=3):
    """K.blend(mode="blend", steps=steps) over a given face list (K.blend picks faces by verts, which can't keep the
    rock and cave classes apart), by a per-face value(f): faces below level - width/2 get k1, above level + width/2
    k2, and the band between the in-between keys (K.mix_key), quantised to steps mixes."""
    for f in faces:
        t = min(1.0, max(0.0, (value(f) - (level - width / 2)) / width))
        t = round(t * (steps + 1)) / (steps + 1)
        f.material_index = p._mi(K.mix_key(k1, k2, t))


def _mottle(p, faces, amp, scale, jitter, seed):
    """K.texture in the build frame: broad low-frequency brightness patches (about 1/scale studs across) plus a
    little per-face jitter, multiplied into each face's Tint."""
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    for f in faces:
        k = 1.0 + amp * 1.6 * noise.noise(p.at(f) * scale + off) + rng.uniform(-jitter, jitter)
        for l in f.loops:
            t = l[p.tint_layer][0] * k
            l[p.tint_layer] = (t, t, t, 1.0)


def _rim_points(p, rock, cave):
    """The rock/cave boundary (the mouth's rim and the front lip's inner edge) as build-frame points. The contact
    plane is left out: there the cave runs on into the other shell's cave."""
    rv = {v for f in rock for v in f.verts}
    return [v.co + p.off for f in cave for v in f.verts if v in rv and v.co.z + p.off.z > ZC + 1e-3]


def _dist_to(p, faces, pts):
    """Distance (studs) from each face's centre to the nearest of pts."""
    if not pts:
        return {f: 9.0 for f in faces}
    kd = KDTree(len(pts))
    for i, q in enumerate(pts):
        kd.insert(q, i)
    kd.balance()
    return {f: kd.find(p.at(f))[2] for f in faces}


def _crystal_feet():
    """(foot, a point up the body, radius) of each crystal in the hero, in the build frame: the lower body, where
    the crystal stands in the seat."""
    out = []
    for label, _, _, sxy, *_ in CRYSTALS:
        m = _crystal_matrix(label)
        out.append((m @ Vector((0.0, 0.0, SHARD["root"])), m @ Vector((0.0, 0.0, SHARD["root"] + BLEED["up"])),
                    SHARD["r"] * sxy * 0.95))
    return out


_FEET = []
_RIM = []       # build-frame rim points, gathered from the shells while they are coloured (for the hero's pass)


def _bleed_field(c):
    """How close c is to a crystal's lower body: about 0 on its surface, negative further out (studs)."""
    if not _FEET:
        _FEET.extend(_crystal_feet())
    best = -99.0
    for a, b, r in _FEET:
        q, t = intersect_point_line(c, a, b)
        q = a if t < 0 else b if t > 1 else q
        best = max(best, r - (c - q).length)
    return best


def _foot_field(c):
    """How close c is to a crystal's base (the body's foot ring): about 0 on it, negative further out (studs)."""
    if not _FEET:
        _FEET.extend(_crystal_feet())
    return max(r - (c - a).length for a, _, r in _FEET)


_CAVE_TRIS = []  # build-frame polygons of the shells' cave faces (before they are painted as stone), for the hero


def _classes(p):
    """Stone faces (any rock key, or the builders' cave key) and crystal faces are told apart by key."""
    return [f for f in p.bm.faces if p.key(f).startswith((ROCK, CAVE, GLOW))]


def _stone_colour(p):
    """A shell's own stone, as the sheet's exploded parts show it: one plain stone outside and in (the underside view's
    inside is the same stone in shadow), with broad warm <-> cool weathering. No cave key and no violet: those are
    the crystals' light in the assembled hero (_crystal_light). The builders' cave faces are remembered (rim points,
    build-frame polygons) for the hero's pass before they are painted as stone."""
    stone = _classes(p)
    cave = [f for f in stone if p.key(f).startswith(CAVE)]
    rock = [f for f in stone if f not in set(cave)]
    _RIM.extend(_rim_points(p, rock, cave))
    _CAVE_TRIS.extend([v.co + p.off for v in f.verts] for f in cave)
    # weathering: broad warm <-> cool grey patches, a little cooler towards the left as on the sheet
    nf = K.noise_field(scale=WEATHER["scale"], seed=WEATHER["seed"])
    _grade(p, stone, ROCK, ROCK_COOL, lambda f: nf(p.at(f)) - WEATHER["left"] * p.at(f).x,
           WEATHER["level"], WEATHER["width"])
    return stone


def _cave_faces(p, stone):
    """The hero's faces lying on the shells' cave faces (the union splits them, but every piece stays on its
    polygon)."""
    from mathutils.bvhtree import BVHTree
    vs, polys = [], []
    for poly in _CAVE_TRIS:
        polys.append(list(range(len(vs), len(vs) + len(poly))))
        vs.extend(poly)
    tree = BVHTree.FromPolygons(vs, polys)
    out = []
    for f in stone:
        hit = tree.find_nearest(p.at(f))
        if hit[0] is not None and hit[3] < 1e-3:
            out.append(f)
    return out


def _crystal_light(p):
    """The assembled hero only: the crystals' light in the cave (the sheet's assembled views; the exploded parts show
    none). Across the rim the stone turns into dusky cave stone, which darkens to a deep, low-saturation violet
    further in and lower down; the stone round each crystal's lower body takes a vivid violet bleed (the sheet's
    crystal seat close-up)."""
    stone = _classes(p)
    cave = _cave_faces(p, stone)
    rock = [f for f in stone if f not in set(cave)]
    d = _dist_to(p, cave, _RIM)
    nf = K.noise_field(scale=0.5, seed=11065)
    # depth into the cave: distance in from the rim, with broad noise so the bands wander
    depth = {f: d[f] + CAVE_NOISE * nf(p.at(f)) for f in cave}
    lip = [f for f in cave if depth[f] < CAVE_BANDS[0][1]]
    _grade(p, lip, ROCK, CAVE, depth.get, sum(CAVE_BANDS[0]) / 2, CAVE_BANDS[0][1] - CAVE_BANDS[0][0])
    deep = [f for f in cave if depth[f] >= CAVE_BANDS[0][1]]
    _grade(p, deep, CAVE, CAVE_DEEP, depth.get, sum(CAVE_BANDS[1]) / 2, CAVE_BANDS[1][1] - CAVE_BANDS[1][0])
    # the back of the cave, furthest in, a little darker again (Tint, by depth: position, not facing)
    d0, d1, low = CAVE_BACK
    for f in deep:
        k = 1.0 - (1.0 - low) * min(1.0, max(0.0, (depth[f] - d0) / (d1 - d0)))
        for l in f.loops:
            t = l[p.tint_layer][0] * k
            l[p.tint_layer] = (t, t, t, 1.0)
    near = [f for f in cave if BLEED["low"] < p.at(f).z < BLEED["high"] and _bleed_field(p.at(f)) > -BLEED["cave"]]
    _grade(p, near, CAVE_DEEP, GLOW, lambda f: _bleed_field(p.at(f)), -BLEED["cave"] + BLEED["width"] / 2,
           BLEED["width"])
    # on rock only the faces right at a crystal's foot (within BLEED["rock"] of its base), graded to plain stone: the
    # lip's top and outer face stay stone
    near = [f for f in rock if _foot_field(p.at(f)) > -BLEED["rock"]]
    _grade(p, near, ROCK, GLOW, lambda f: _foot_field(p.at(f)), -BLEED["rock"] + BLEED["rock_width"] / 2,
           BLEED["rock_width"])


def colour_part(o):
    """Stage 4 colour on a finished part: the shells' stone and its weathering, or the crystal's axis gradient;
    then Tint mottling."""
    p = _Paint(o)
    if o.name == "AmethystShard":
        # root dark -> body mid -> tip light along the crystal's own axis (mesh z, root point at 0); the hero's
        # seven copies all carry it
        faces = list(p.bm.faces)
        top = max(v.co.z for v in p.bm.verts)
        h = {f: f.calc_center_median().z / top for f in faces}
        for k1, k2, level, width in CRYSTAL_BANDS:
            band = faces if k1 == DARK else [f for f in faces if h[f] > level - width / 2]
            _grade(p, band, k1, k2, h.get, level, width)
        _mottle(p, faces, **MOTTLE["crystal"])
    else:
        _mottle(p, _stone_colour(p), **MOTTLE["stone"])
    p.done()


# ---- top shell -----------------------------------------------------------------------------------------------------
def _mouth():
    t = math.radians(MOUTH_LEAN)
    return MOUTH_FOOT, Vector((0.0, -math.cos(t), -math.sin(t)))    # out of the mouth: forward, a little down


def _radius(d, radii, seed):
    """Distance from CENTRE to the ellipsoid along unit d, with broad lumps (none at the contact ring, so the two
    shells' outlines match there)."""
    t = 1.0 / sum(abs(d[i] / radii[i]) ** SUPER for i in range(3)) ** (1.0 / SUPER)
    if seed is None:
        return t
    off = Vector((seed % 97, seed % 89, seed % 83)) * 0.37
    # the lumps fade in over the lower 40 degrees (verifier round 2: at full strength just above the contact ring they
    # bulged the hood's foot out past the bottom shell, a belt round the rear)
    bump = BUMP * (INNER_BUMP if radii == INNER else 1.0)
    return t * (1.0 + bump * noise.noise(d * 2.2 + off) * min(1.0, d.z * 1.6) ** 2)


def _surf(d, radii, seed):
    return CENTRE + d * _radius(d, radii, seed)


def _mouth_d(p):
    """How far p is in front of the mouth (positive: in the opening). The mouth is the plane _mouth() bent back at
    the sides by MOUTH_CURVE x^2 (verifier round 2: the hood's sides are cut back and up, so from 45 degrees behind
    the opening and the crystals show past them, as on the sheet's rear three-quarter view)."""
    p0, n = _mouth()
    # verifier round 3: higher up the bend grows (MOUTH_CURVE_UP), so the hood's upper flanks are cut back and the
    # cluster shows past them from 45 degrees behind, while the arch's feet stay in front of the egg's widest section
    # (no notches in the rear view) and the centre of the dome still comes forward over the crystals
    up = min(1.0, max(0.0, (p.z - ZC) / 3.0))
    return (p - p0).dot(n) + (MOUTH_CURVE + MOUTH_CURVE_UP * up) * (p.x - p0.x) ** 2


def _in_hood(p):
    return p.z >= ZC - 1e-9 and _mouth_d(p) <= 0.0


def _basis():
    e1 = Vector((0.0, -POLE.z, POLE.y)).normalized()      # towards the front, over the top
    return e1, POLE.cross(e1)


def _dir(rho, beta):
    e1, e2 = _basis()
    return (POLE * math.cos(rho) + (e1 * math.cos(beta) + e2 * math.sin(beta)) * math.sin(rho)).normalized()


def _rim(beta, radii, seed):
    """How far (angle from the pole) the sheet reaches along column beta: the first point outside the shell."""
    step = math.radians(0.5)
    rho = step
    while rho < math.pi and _in_hood(_surf(_dir(rho, beta), radii, seed)):
        rho += step
    lo, hi = rho - step, rho
    for _ in range(30):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _in_hood(_surf(_dir(mid, beta), radii, seed)) else (lo, mid)
    return lo


_CACHE = {}


def _columns():
    """COLS column angles spaced evenly along the outside rim (the mouth's arch weighted a little more)."""
    key = (COLS, OUTER, INNER, ZC, MOUTH_LEAN, MOUTH_CURVE, MOUTH_CURVE_UP, tuple(MOUTH_FOOT), tuple(POLE), SUPER,
           BUMP)
    if key not in _CACHE:
        _CACHE.clear()
        _CACHE[key] = _columns_calc()
    return _CACHE[key]


def _put_down(p):
    """Where rim point p sits on the contact plane, or None for rim points higher up the arch.
    - A rim point on the plane stays there.
    - The arch's feet leave the hood through the mouth plane less than FOOT above the contact plane. They slide
      down the mouth plane onto it, so the hood's whole ring sits flat on the bottom shell right up to the mouth,
      with no wedge-shaped crack under the feet."""
    dz = p.z - ZC
    if dz < 0.03:
        return Vector((p.x, p.y, ZC))
    if dz >= FOOT:
        return None
    return Vector((p.x, p.y + dz * math.tan(math.radians(MOUTH_LEAN)), ZC))


def _contact(radii, seed):
    """The top shell's own points on the contact plane (outside or inside sheet), in column order: the bottom
    shell's matching ring uses exactly these, so the two shells meet without a step."""
    pts = []
    for beta in _columns():
        p = _put_down(_surf(_dir(_rim(beta, radii, seed), beta), radii, seed))
        if p is not None:
            pts.append(p)
    return pts


def _contact_ring(radii, seed, z, scale=1.0, extra=16):
    """A closed horizontal ring through the top shell's contact points, completed across the mouth by points on
    the same outline (they are what lies in front of the mouth plane), ordered by angle; at height z, scaled about
    the centre."""
    pts = _contact(radii, seed) + [q for q in _ellipse_ring(radii, ZC, extra) if _mouth_d(q) > 0.05]
    pts.sort(key=lambda q: math.atan2(q.y - CENTRE.y, q.x - CENTRE.x))
    return [Vector((CENTRE.x + (q.x - CENTRE.x) * scale, CENTRE.y + (q.y - CENTRE.y) * scale, z)) for q in pts]


def _columns_calc():
    n = 720
    bs = [2 * math.pi * k / n for k in range(n)]
    pts = [_surf(_dir(_rim(b, OUTER, 1), b), OUTER, 1) for b in bs]
    acc = [0.0]
    for k in range(n):
        p, q = pts[k], pts[(k + 1) % n]
        acc.append(acc[-1] + (q - p).length * (1.35 if min(p.z, q.z) > ZC + 0.05 else 1.0))
    total = acc[-1]
    out = []
    # start on the front centre of the arch so the grid is symmetric
    for j in range(COLS):
        target = total * j / COLS
        k = next(i for i in range(n) if acc[i + 1] >= target)
        f = (target - acc[k]) / max(acc[k + 1] - acc[k], 1e-9)
        out.append(bs[k] + f * (2 * math.pi / n))
    return out


def top_shell(a):
    rng = random.Random(11001)
    p0, n_m = _mouth()
    bm = a.bm
    cols = []
    was_raised = set()      # verts the foot snap put down (the random draws still follow the original layout)
    for j, beta in enumerate(_columns()):
        ro, ri = _rim(beta, OUTER, 1), _rim(beta, INNER, 2)
        # the outside's middle rows slide up or down the surface a little per column, so no row runs round the dome
        # as one level line (verifier round 2: a latitude crease round the rear); on the surface, so no bulge
        slide = random.Random(11004 + j)
        outer = [_surf(_dir(ro * f * (1 + (slide.uniform(-ROW_SLIDE, ROW_SLIDE) if 0 < f < 1 else 0.0)), beta),
                       OUTER, 1) for f in OUT_F]
        inner = [_surf(_dir(ri * f, beta), INNER, 2) for f in IN_F]
        po, pi = outer[-1], inner[0]
        fo, fi = _put_down(po), _put_down(pi)
        for p in (po, pi):
            if abs(p.z - ZC) < 0.03:
                p.z = ZC
        w = max(0.0, min(1.0, (min(po.z, pi.z) - ZC) / 2.0))       # lip roundness fades out at the feet
        lip = []
        for s in LIP:
            q = po.lerp(pi, s) + n_m * LIP_BULGE * w * math.sin(math.pi * s)
            q.z = max(q.z, ZC)
            lip.append(q)
        # irregular facets: the sheets' inner rows wander (the lip and the flat contact ring stay put)
        prof = outer + lip + inner
        for k, q in enumerate(prof):
            if q.z <= ZC + 1e-6:
                continue
            # (the outside's row just above the rim wanders little too: at full jitter it stood out past the bottom
            # shell, a belt round the rear - verifier round 2)
            amp = JITTER_RIM if k in (len(outer) - 2, len(outer) - 1, len(outer) + len(lip)) or len(outer) <= k < len(
                outer) + len(lip) else JITTER
            if k >= len(outer) + len(lip):
                amp = JITTER_CAVE       # the cave ceiling: calm broad facets (round 3: full jitter crinkled it)
            q += Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * amp
            q.z = max(q.z, ZC)
        raised = {k for k, q in enumerate(prof) if q.z > ZC + 1e-6}
        if fo is not None and fi is not None:
            # a contact column (the arch's feet included): rim and lip lie flat on the contact plane, in a straight
            # line from the outside to the inside
            po[:], pi[:] = fo, fi
            for s, q in zip(LIP, lip):
                q[:] = fo.lerp(fi, s)
        vs_col = [bm.verts.new(q) for q in prof]
        was_raised.update(vs_col[k] for k in raised if vs_col[k].co.z <= ZC + 1e-6)
        cols.append(vs_col)
    no, nl = len(OUT_F), len(LIP)
    faces_rock, faces_cave = [], []
    # the dome's crown (verifier round 1: one radial pole showed as a star of thin triangles from above), and the
    # cave ceiling's the same way (verifier round 2: the tilted-up mouth shows the ceiling, and its pole fan read as a
    # radial star there): see _crown
    cap = _crown(bm, cols, 0, 1, OUTER, 1, 11002, faces_rock)
    cap += _crown(bm, cols, -1, -2, INNER, 2, 11003, faces_cave)
    last = len(cols[0]) - 2             # the inside sheet's crown strip
    for j in range(COLS):
        c0, c1 = cols[j], cols[(j + 1) % COLS]
        for k in range(len(c0) - 1):
            if k in (0, last):      # the crowns' rings (above); the draw is kept so the stream stays as it was
                rng.random()
                continue
            # each quad as two triangles, the diagonal picked at random: big irregular triangular facets as on
            # the sheet, not latitude bands (the flat contact ring keeps quads). The feet's quads, flat now, still
            # take their draw, so every other diagonal stays where it was.
            q = (c0[k], c0[k + 1], c1[k + 1], c1[k])
            flat = all(v.co.z <= ZC + 1e-6 for v in q)
            r = rng.random() if not flat or any(v in was_raised for v in q) else 0.0
            if not flat:
                # verifier round 1: a random diagonal on a strongly bent quad folds it into a valley (a dark slit on
                # the dome). Take the diagonal that keeps the surface bulging away from the centre; the random pick
                # stays only where the quad is near flat
                r = _split_pick(q, r)
            if flat:
                fs = [bm.faces.new(q)]
            elif r < 0.5:
                fs = [bm.faces.new((q[0], q[1], q[2])), bm.faces.new((q[0], q[2], q[3]))]
            else:
                fs = [bm.faces.new((q[0], q[1], q[3])), bm.faces.new((q[1], q[2], q[3]))]
            (faces_cave if k >= no + nl else faces_rock).extend(fs)
    vs = [v for c in cols for v in c if v.is_valid] + cap
    bmesh.ops.recalc_face_normals(bm, faces=faces_rock + faces_cave)
    a._finish(vs, ROCK)
    ci = a._mi(CAVE)
    for f in faces_cave:
        f.material_index = ci
    # the flat contact ring is hidden (it sits on the bottom shell): where all of a lip vert's faces lie on it, the
    # vert is a collinear point in the middle of the ring, so dissolve it (one quad across the ring per column;
    # the end columns keep theirs, since the rolled lip of the arch needs them) and fan the two end gaps into
    # triangles
    on_ring = [v for c in cols for v in c[no:no + nl]
               if all(all(w.co.z <= ZC + 1e-6 for w in f.verts) for f in v.link_faces)]
    bmesh.ops.dissolve_verts(bm, verts=on_ring)
    for f in [f for f in bm.faces if len(f.verts) > 4]:
        _fan(bm, f)
    return [v for v in vs if v.is_valid]


def _crown(bm, cols, row, nxt, radii, seed, rng_seed, faces):
    """Close one sheet round the grid pole with a few broad irregular facets instead of a fan to one point:
    - row `row` keeps every other column only (a ring of COLS/2 verts), each pair of row `nxt`'s columns fanning to
      it; the other columns' verts of that row are removed;
    - inside the ring, CAP verts (CAP_F of the way from the pole to the rim, each over a group of the ring) and one
      broad facet across the middle.
    Its own random stream (rng_seed), so the rest of the shell keeps its draws. Returns the cap verts; the faces go
    into `faces` (their winding is fixed by the caller's recalc)."""
    cap_rng = random.Random(rng_seed)
    betas = _columns()
    ring = [cols[j][row] for j in range(0, COLS, 2)]
    nr = len(ring)
    for m in range(nr):
        j = 2 * m
        r0, r1 = cols[j][row], cols[(j + 2) % COLS][row]
        s0, s1, s2 = cols[j][nxt], cols[j + 1][nxt], cols[(j + 2) % COLS][nxt]
        faces.append(bm.faces.new((r0, s1, s0)))
        # the quad r0-r1-s2-s1 split along whichever diagonal keeps a ridge (round 3: a fixed split sank a valley
        # into the top of the dome)
        if _split_pick((r0, r1, s2, s1), 1.0) < 0.5:
            faces += [bm.faces.new((r0, r1, s2)), bm.faces.new((r0, s2, s1))]
        else:
            faces += [bm.faces.new((r0, r1, s1)), bm.faces.new((r1, s2, s1))]
    per = nr // CAP
    cap = []
    for k in range(CAP):
        beta = betas[(2 * per * k + per) % COLS] + cap_rng.uniform(-0.08, 0.08)
        q = _surf(_dir(_rim(beta, radii, seed) * CAP_F * cap_rng.uniform(0.92, 1.08), beta), radii, seed)
        amp = JITTER * 0.5 if radii == OUTER else JITTER_CAVE
        if radii == OUTER:
            # a touch proud of the surface, so the crown's broad facets meet the ring in ridges, never a valley
            # (round 3: one sank into a dark crease on top of the dome)
            q = CENTRE + (q - CENTRE) * 1.025
        cap.append(bm.verts.new(q + Vector([cap_rng.uniform(-1, 1) for _ in range(3)]) * amp))
    for k in range(CAP):
        g = [ring[(per * k + i) % nr] for i in range(per + 1)]
        for i in range(per):
            faces.append(bm.faces.new((cap[k], g[i], g[i + 1])))
        faces.append(bm.faces.new((cap[k], g[per], cap[(k + 1) % CAP])))
    faces.append(bm.faces.new(cap))
    for j in range(1, COLS, 2):
        bm.verts.remove(cols[j][row])
    return cap


def _split_pick(q, r, flat=0.04):
    """The diagonal for quad q (verts a, b, c, d): returns a value < 0.5 for a-c, >= 0.5 for b-d. The split whose
    fold is a ridge (the left-out corner lies on the centre's side of the other triangle's plane, the plane faced
    away from CENTRE) wins; within `flat` studs either way, the random draw r decides."""
    a, b, c, d = (v.co for v in q)
    out = ((a + b + c + d) / 4 - CENTRE).normalized()

    def lift(t0, t1, t2, other):
        n = (t1 - t0).cross(t2 - t0)
        if n.length < 1e-12:
            return 0.0
        n = n.normalized() * (1 if n.dot(out) >= 0 else -1)
        return (other - t0).dot(n)
    s_ac, s_bd = lift(a, b, c, d), lift(a, b, d, c)
    if max(abs(s_ac), abs(s_bd)) < flat:
        return r
    return 0.0 if s_ac < s_bd else 1.0


def _fan(bm, f):
    """Triangulate a flat face made of one collinear run of verts and two corners across from it (the contact
    ring's end gaps) without zero-area triangles: each half of the run fans to its nearer corner, and one
    triangle joins the run's middle to both corners."""
    vs = list(f.verts)
    n = len(vs)
    straight = [(vs[k - 1].co - vs[k].co).angle(vs[(k + 1) % n].co - vs[k].co) > math.pi - 1e-3 for k in range(n)]
    if sum(straight) != n - 4:
        bmesh.ops.triangulate(bm, faces=[f], quad_method="BEAUTY", ngon_method="BEAUTY")
        return
    s = next(k for k in range(n) if not straight[k] and straight[(k + 1) % n])     # the run's first end
    ring = vs[s:] + vs[:s]                       # polygon order: run (n - 2 verts), then the two corners
    line, (a0, a1) = ring[:n - 2], ring[n - 2:]  # a0 is next to the run's last vert, a1 next to its first
    half = len(line) // 2
    tris = [(line[i], line[i + 1], a1 if i < half else a0) for i in range(len(line) - 1)] + [(line[half], a0, a1)]
    mat, smooth = f.material_index, f.smooth
    tint = bm.loops.layers.float_color.get("Tint")
    col = tuple(f.loops[0][tint]) if tint else None
    bm.faces.remove(f)
    for t in tris:
        nf = bm.faces.new(t)
        nf.material_index, nf.smooth = mat, smooth
        if tint:
            for l in nf.loops:
                l[tint] = col


# ---- bottom shell --------------------------------------------------------------------------------------------------
def _ellipse_ring(radii, z, n, centre=CENTRE, scale=1.0, jitter=0.0, seed=0):
    """A horizontal ring with the top shell's own outline at the contact plane (same superellipse), scaled."""
    rng = random.Random(seed)
    out = []
    for k in range(n):
        th = 2 * math.pi * k / n
        d = Vector((math.cos(th), math.sin(th), 0.0))
        r = _radius(d, (radii[0], radii[1], 1.0), None) * scale * (1 + rng.uniform(-jitter, jitter))
        out.append(Vector((centre.x + d.x * r, centre.y + d.y * r, z)))
    return out


def _clip_behind_mouth(rings):
    """Points of closed rings clipped to the part behind the mouth (with the crossing points)."""
    out = []
    for ring in rings:
        for k, p in enumerate(ring):
            q = ring[(k + 1) % len(ring)]
            dp, dq = _mouth_d(p), _mouth_d(q)
            if dp <= 0:
                out.append(p)
            if (dp < 0) != (dq < 0):
                out.append(p.lerp(q, dp / (dp - dq)))
    return out


def _hull(a, pts, mat):
    vs = [a.bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(a.bm, input=vs)
    vs = [v for v in vs if v.is_valid and v.link_faces]
    bmesh.ops.recalc_face_normals(a.bm, faces=K.faces_of(vs))
    a._finish(vs, mat)
    return vs


def _rotated(ring, ang):
    c = CENTRE.to_2d().to_3d()
    rot = Matrix.Rotation(ang, 3, "Z")
    return [c + rot @ (q - c) for q in ring]


def _front_of_mouth(pts, margin):
    return [q for q in pts if _mouth_d(q) > margin]


def _egg_low(z):
    """The egg's horizontal scale at height z below the contact plane (the dome's superellipse, height EGG_LOW)."""
    return max(0.0, 1.0 - ((ZC - z) / EGG_LOW) ** SUPER) ** (1.0 / SUPER)


def _lip_z(q):
    """The front lip's top height over point q: LIP_LOW in the middle, rising towards the contact plane at the
    sides."""
    t = min(1.0, abs(q.x - CENTRE.x) / OUTER[0])
    return LIP_LOW + (ZC - 0.8 - LIP_LOW) * t ** LIP_RISE


def bottom_raw(a):
    """The bottom shell before its cut: the lower half of the same faceted stone egg as the top shell, one convex
    rock (the user: "a hollowed out stone/rock with amethyst in it"; no slabs, no blocks).
    - Behind the mouth its top is the top shell's own contact ring at ZC, so the two shells are one continuous
      stone: the egg carries on down from the hood (near-vertical just below the ring, so no crease), tucking in
      towards the ground.
    - In front of the mouth it is the hollow's low, thick front lip: its top at FRONT_Z (about 35 % of the height),
      rounded over by a bevel ring, sloping up to the arch's feet at the sides.
    - A few broad bulges low down break the egg into big irregular facets (the sheet's base lumps, as part of the
      one rock)."""
    rings = [_contact(OUTER, 1)]                                              # at ZC, behind the mouth
    rng = random.Random(11046)
    lip = _front_of_mouth(_ellipse_ring(OUTER, 0.0, 14, scale=FRONT_IN), 0.25)
    for q in lip:                       # the crescent's top: low in the middle, rising to the ends; lumpy
        q.z = _lip_z(q) + rng.uniform(-LIP_LUMP, LIP_LUMP)
    rings.append(lip)
    # the lip's shoulders rise to the arch's feet over a few facets (one hull plane there read as a flat ramp)
    c = CENTRE.to_2d().to_3d()
    for q in _rotated(_ellipse_ring(OUTER, 0.0, 22, scale=1.0, jitter=0.03, seed=11047), 0.07):
        dp = _mouth_d(Vector((q.x, q.y, ZC)))
        if 0.15 < dp < 2.2:
            f = (dp / 2.2) ** 0.45      # falls away quickly from the foot: no flat ledge beside the cut-back hood
            z = ZC - (ZC - _lip_z(q)) * f - 0.2
            # flush with the egg's side at the arch's foot, drawing in towards the lip's rounded top further forward
            xy = c + (q - c) * (1.0 - (1.0 - FRONT_IN) * f * 0.8)
            # (none crowding a contact point: a shoulder point a few tenths from one made needle facets)
            if all((Vector((xy.x, xy.y)) - p.to_2d()).length > 0.8 for p in rings[0]):
                rings.append([Vector((xy.x, xy.y, z))])
    bevel = _front_of_mouth(_rotated(_ellipse_ring(OUTER, 0.0, 16, scale=0.995, jitter=0.02, seed=11044), 0.1),
                            0.25)
    for q in bevel:
        q.z = _lip_z(q) - 0.75
    rings.append(bevel)
    # straight down from the contact ring first (the hood is vertical there too), so the two shells meet with no
    # step or belt (verifier round 2: a ring a little inside the contact ring read as a seam round the rear)
    # (round 3: rings on the contact points' own azimuths, on the egg's curve, so the facets just below the ring line
    # up with the hood's columns - a ring of other azimuths there made a sawtooth of shading, read as a seam)
    for z in (ZC - 0.7, ZC - 1.6):
        s = _egg_low(z)
        rings.append([Vector((CENTRE.x + (p.x - CENTRE.x) * s, CENTRE.y + (p.y - CENTRE.y) * s, z))
                      for p in _contact(OUTER, 1)])
    # the egg's lower half: the same superellipse curve as the dome (rounded, not a cylinder with a belt where it
    # meets the hood), staggered rings
    for i, z in enumerate((1.8, 0.8, 0.0)):
        s = max(0.0, 1.0 - ((ZC - z) / EGG_LOW) ** SUPER) ** (1.0 / SUPER)
        rings.append(_rotated(_ellipse_ring(OUTER, z, 14, scale=s, jitter=0.035, seed=11041 + i),
                              math.pi / 14 * (i % 2) + 0.2 * i))
    bulges = []
    for ang, z, s in BULGES:
        d = Vector((math.cos(math.radians(ang)), math.sin(math.radians(ang)), 0.0))
        r = _radius(d, (OUTER[0], OUTER[1], 1.0), None) * s
        bulges.append(Vector((CENTRE.x + d.x * r, CENTRE.y + d.y * r, z)))
    vs = _hull(a, [q for ring in rings for q in ring] + bulges, ROCK)
    # the hull leaves a few long needle triangles (under 3 degrees) where its rings are spaced unevenly: merge
    # facets within 2 degrees of each other and re-split them BEAUTY (same surface, broader triangles)
    faces = K.faces_of(vs)
    bmesh.ops.dissolve_limit(a.bm, angle_limit=math.radians(2.0), verts=vs,
                             edges=list({e for f in faces for e in f.edges}))
    faces = K.faces_of([v for v in vs if v.is_valid])
    bmesh.ops.triangulate(a.bm, faces=[f for f in faces if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    # the fused lumps (separate closed hulls here; build() unions them into the egg)
    for name, x, y, w, d, h, rot, seed in LUMPS:
        K.hull_rock(a, (w, d, h), loc=(x, y, 0), seed=seed, mat=ROCK, jitter=0.03, rot=rot, keep_bottom=True,
                    rings=HORN_RINGS if name.startswith("Horn") else LUMP_RINGS)


def bottom_cutter(a):
    """The hollow: a shallow rocky bowl. Its walls slope down from the cave's own outline at the contact plane (so
    the cave runs on from the top shell without a step) through an irregular middle ring to a small flat seat; at
    the front they lean back further, so the front lip is thick and its inside slopes too."""
    # (verifier round 3: a long trough, not a round pit - the seat and the middle ring are drawn out sideways)
    rings = [(_ellipse_ring((INNER[0] * 0.8, INNER[1] * 0.55), ZF, 11, jitter=0.08, seed=11043), -1.0),
             (_rotated(_ellipse_ring((INNER[0] * 0.95, INNER[1] * 0.8), ZF + 1.0, 12, jitter=0.07, seed=11045), 0.2),
              -1.65),
             (_contact_ring(INNER, 2, ZC), -2.3), (_contact_ring(INNER, 2, ZC + 2.0), -2.3)]
    pts = []
    for ring, front in rings:
        for q in ring:
            q.y = max(q.y, front)
            pts.append(q)
    _hull(a, pts, CAVE)
    # verifier round 2: a V notch down the middle of the front lip (the sheet's dip where its two front stones meet),
    # in outside rock; it runs right through into the hollow
    z0, w, z1, back = NOTCH
    _hull(a, [Vector((x, y, z)) for y in (-7.0, back) for x, z in ((0.0, z0), (-w, z1), (w, z1))], ROCK)


# ---- crystal -------------------------------------------------------------------------------------------------------
def shard(a):
    """One amethyst crystal: six-sided, a short root point, a straight body flaring very slightly, a pointed tip.
    Root point at the origin, axis +Z."""
    rng = random.Random(SHARD["seed"])
    r, root, body, tip = SHARD["r"], SHARD["root"], SHARD["body"], SHARD["tip"]
    radii = [r * rng.uniform(0.88, 1.08) for _ in range(6)]
    pts = [Vector((0.0, 0.0, 0.0))]
    # body foot, body top, and a shoulder part-way up the tip (the sheet's crystals break the tip into a ring of
    # bevel facets and the point)
    for z, s, tw in ((root, 0.94, 0.0), (root + body, 1.0, 0.0), (root + body + tip * 0.3, 0.8, 0.0)):
        for k in range(6):
            t = 2 * math.pi * k / 6 + rng.uniform(-0.06, 0.06) + tw
            pts.append(Vector((math.cos(t) * radii[k] * s, math.sin(t) * radii[k] * s * 0.92, z)))
    pts.append(Vector((r * 0.06, -r * 0.04, root + body + tip)))
    return _hull(a, pts, MID)


def _crystal_matrix(label):
    _, x, y, sxy, sz, lx, ly, tw = next(c for c in CRYSTALS if c[0] == label)
    axis = Vector((lx, ly, 1.0)).normalized()
    rot = axis.to_track_quat("Z", "Y").to_matrix().to_4x4() @ Matrix.Rotation(tw, 4, "Z")
    seat = ZF + 0.12 - SHARD["root"] * sz * axis.z       # the body's foot just above the seat; root point sunk
    return Matrix.Translation((x, y, seat)) @ rot @ Matrix.Diagonal((sxy, sxy, sz, 1.0))


# ---- assembly ------------------------------------------------------------------------------------------------------
def _paste(a, o, mat4, tint=1.0):
    """Copy a finished part's mesh (materials by palette key, Tint times `tint`) into an Asset, through mat4 (from
    the part's mesh coordinates into the build frame)."""
    src = bmesh.new()
    src.from_mesh(o.data)
    layer = src.loops.layers.float_color.get("Tint")
    mis =[a._mi(m.get("flintkit_key") or m.name[3:]) for m in o.data.materials]
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


def _frame(o):
    """Part mesh coordinates -> the shared build frame."""
    return Matrix.Translation(Vector(o["m011_offset"]))


def _bottom_centre(o):
    xs = [v.co.x for v in o.data.vertices]
    ys = [v.co.y for v in o.data.vertices]
    zs = [v.co.z for v in o.data.vertices]
    return Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))


def _finish_part(o, build_fn):
    """Record where the part's mesh sits in the build frame (mk's bottom-centre shift plus finish's re-centring),
    then clean it up."""
    o["m011_offset"] = list(M._build_offset(build_fn) + _bottom_centre(o))
    return M.finish(o, union=False, uv=UV)


def _tidy(o, angle=0.5):
    """Merge the coplanar slivers the booleans leave (same facets, same silhouette; under 0.5 degrees only), then
    re-triangulate the merged faces."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(angle), verts=bm.verts, edges=bm.edges,
                             delimit={"MATERIAL"})
    ng = [f for f in bm.faces if len(f.verts) > 4]
    bmesh.ops.triangulate(bm, faces=ng, quad_method="BEAUTY", ngon_method="BEAUTY")
    bm.to_mesh(o.data)
    bm.free()


def _min_angle(pts):
    """Smallest corner angle (radians) of a polygon given by its points."""
    out = math.pi
    for k, p in enumerate(pts):
        u, v = pts[k - 1] - p, pts[(k + 1) % len(pts)] - p
        out = min(out, u.angle(v) if u.length > 1e-9 and v.length > 1e-9 else 0.0)
    return out


def _fmin(f):
    return _min_angle([v.co for v in f.verts])


def _normal(pts):
    return sum(((pts[k] - pts[0]).cross(pts[k + 1] - pts[0]) for k in range(1, len(pts) - 1)), Vector())


def _tilt_ok(faces, moved):
    """True if moving verts (moved: {vert: new co}) neither flips nor folds any face in faces: a face may turn
    at most about 30 degrees (any amount up to 75 degrees if it is a speck under 0.02 square studs)."""
    for x in faces:
        n = _normal([moved.get(v, v.co) for v in x.verts])
        if n.length < 1e-12:
            return False
        d = n.normalized().dot(x.normal)
        if d < 0.25 or (d < 0.86 and x.calc_area() > 0.02):
            return False
    return True


def _plane_lock(planes, fixed=()):
    """movable(v, co) for _desliver: verts on one of the z planes may only slide within it; verts at the fixed
    points never move."""
    fixed = [Vector(p) for p in fixed]

    def movable(v, co):
        if any((v.co - p).length < 1e-4 for p in fixed):
            return False
        return all(abs(v.co.z - z) > 1e-4 or abs(co.z - z) < 1e-6 for z in planes)
    return movable


def _desliver(bm, movable, min_angle=3.0, max_move=0.06, speck=0.002, rounds=40):
    """Remove the needle, cap and speck faces the booleans leave where shells meet at grazing angles. No vertex
    moves more than max_move studs (far below what reads on screen), and movable(v, co) can forbid a move:
    - a needle (a short edge) or a speck (a face under `speck` square studs) collapses its shortest edge, onto
      whichever end (or the middle) the rules allow and that tilts the neighbours least;
    - a cap (one corner almost straight, no short edge) flips its long edge when that improves both triangles;
      otherwise it flips the edge and pulls the straight corner onto the old edge line;
    - any other thin face (a long facet, a strip on a flat face) flips an edge if that bends the surface by at most
      0.02 studs (_flip_free).
    Every change keeps the mesh manifold (link condition, and the flip refuses an edge that already exists).
    Returns counts of each fix and of the slivers left."""
    lim = math.radians(min_angle)
    log = {"collapse": 0, "flip": 0, "flatten": 0}
    for _ in range(rounds):
        bad = sorted((f for f in bm.faces if _fmin(f) < lim or f.calc_area() < speck), key=_fmin)
        changed = False
        for f in bad:
            if not f.is_valid or (_fmin(f) >= lim and f.calc_area() >= speck):
                continue
            if len(f.verts) > 3:
                bmesh.ops.triangulate(bm, faces=[f], quad_method="BEAUTY", ngon_method="BEAUTY")
                changed = True
                continue
            es = sorted(f.edges, key=lambda e: e.calc_length())
            short, long_ = es[0], es[-1]
            if short.calc_length() <= 2 * max_move and _collapse(bm, short, movable, log, max_move):
                changed = True
            elif 2 * f.calc_area() / long_.calc_length() <= max_move and _uncap(bm, f, long_, movable, log):
                changed = True
            elif _flip_free(bm, f, movable, log):
                changed = True
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-5)
        if not changed:
            break
    log["slivers_left"] = sum(1 for f in bm.faces if _fmin(f) < lim)
    log["specks_left"] = sum(1 for f in bm.faces if f.calc_area() < speck)
    return log


def _collapse(bm, e, movable, log, max_move):
    a, b = e.verts
    if any(len(x.verts) != 3 for x in e.link_faces):
        bmesh.ops.triangulate(bm, faces=[x for x in e.link_faces if len(x.verts) > 3])
        return True
    # link condition: the ends share exactly the opposite corners of the edge's faces (else non-manifold)
    na = {x.other_vert(a) for x in a.link_edges}
    nb = {x.other_vert(b) for x in b.link_edges}
    if len(e.link_faces) != 2:
        return False
    if len(na & nb) != 2:
        # a vert of the edge's faces on only three triangles (a point inside one triangle split three ways):
        # dissolve it instead, which drops it onto the plane through its three neighbours
        for v in [a, b] + [next(w for w in x.verts if w not in (a, b)) for x in e.link_faces]:
            if len(v.link_edges) != 3 or any(len(x.verts) != 3 for x in v.link_faces):
                continue
            r = [x.other_vert(v).co for x in v.link_edges]
            n = (r[1] - r[0]).cross(r[2] - r[0])
            if n.length < 1e-12:
                continue
            n.normalize()
            p = v.co - n * (v.co - r[0]).dot(n)
            if (p - v.co).length <= max_move and movable(v, p) and all(
                    abs(n.dot(x.normal)) > (0.86 if x.calc_area() > 0.02 else 0.25) for x in v.link_faces):
                bmesh.ops.dissolve_verts(bm, verts=[v])
                log["collapse"] += 1
                return True
        return False
    keep = [x for x in set(a.link_faces) | set(b.link_faces) if x not in e.link_faces]
    cands = [a.co.copy(), b.co.copy(), (a.co + b.co) / 2]
    for co in sorted(cands, key=lambda c: max((c - a.co).length, (c - b.co).length)):
        if max((co - a.co).length, (co - b.co).length) > max_move:
            continue
        if ((co - a.co).length < 1e-9 or movable(a, co)) and ((co - b.co).length < 1e-9 or movable(b, co)) \
                and _tilt_ok(keep, {a: co, b: co}):
            bmesh.ops.pointmerge(bm, verts=[a, b], merge_co=co)
            log["collapse"] += 1
            return True
    return False


def _uncap(bm, f, e, movable, log):
    c = next(v for v in f.verts if v not in e.verts)
    other = [x for x in e.link_faces if x is not f]
    if len(other) != 1:
        return False
    g = other[0]
    if len(g.verts) > 3:
        bmesh.ops.triangulate(bm, faces=[g], quad_method="BEAUTY")
        return True
    d = next(v for v in g.verts if v not in e.verts)
    A, B = e.verts
    t = (c.co - A.co).dot(B.co - A.co) / (B.co - A.co).length_squared
    p = A.co.lerp(B.co, t)
    old = min(_fmin(f), _fmin(g))
    nav = (f.normal + g.normal).normalized()

    def after(cc):
        # the two new triangles (A, c, d) and (c, B, d) must face the same way, along the old surface (their
        # winding here follows the edge's vert order, not the faces', so only the agreement in sign matters)
        ns = [_normal(q) for q in ([A.co, cc, d.co], [cc, B.co, d.co])]
        if min(n.length for n in ns) < 1e-12:
            return False, 0.0
        d1, d2 = (n.normalized().dot(nav) for n in ns)
        return d1 * d2 > 0 and min(abs(d1), abs(d2)) > 0.3, min(_min_angle(q) for q in
                                                                  ([A.co, cc, d.co], [cc, B.co, d.co]))
    ok, new = after(c.co)
    move = not (ok and new > old)
    if move:
        # flip and pull the corner onto the old edge: allowed if the move is permitted and still helps
        ok, new = after(p)
        if not (ok and new > old and 0.0 < t < 1.0 and movable(c, p)
                and _tilt_ok([x for x in c.link_faces if x is not f], {c: p})):
            return False
    if not bmesh.ops.rotate_edges(bm, edges=[e], use_ccw=False)["edges"]:
        return False
    if move:
        c.co = p
        log["flatten"] += 1
    else:
        log["flip"] += 1
    return True


def _flip_free(bm, f, movable, log, tol=0.02):
    """A thin face that is neither a needle nor a shallow cap (a long facet, or a strip on a flat crystal face or the
    seat): flip whichever of its edges gives the best pair of triangles, if the flip moves the surface by at most
    tol studs (the distance between the old and the new diagonal: 0 on a flat face) and both new triangles face
    the same way. Edges whose four corners are all pinned (the contact ring) are left alone."""
    best = None
    for e in f.edges:
        if len(e.link_faces) != 2 or any(len(x.verts) != 3 for x in e.link_faces):
            continue
        g = next(x for x in e.link_faces if x is not f)
        A, B = e.verts
        c = next(v for v in f.verts if v not in e.verts)
        d = next(v for v in g.verts if v not in e.verts)
        if not any(movable(v, v.co) for v in (A, B, c, d)):
            continue
        p1, p2 = intersect_line_line(A.co, B.co, c.co, d.co) or (A.co, A.co)
        if (p1 - p2).length > tol:
            continue
        nav = (f.normal + g.normal)
        ns = [_normal(q) for q in ([A.co, c.co, d.co], [c.co, B.co, d.co])]
        if nav.length < 1e-9 or min(n.length for n in ns) < 1e-12:
            continue
        d1, d2 = (n.normalized().dot(nav.normalized()) for n in ns)
        if d1 * d2 <= 0 or min(abs(d1), abs(d2)) < 0.3:
            continue
        old = min(_fmin(f), _fmin(g))
        new = min(_min_angle([A.co, c.co, d.co]), _min_angle([c.co, B.co, d.co]))
        if new > old and (best is None or new > best[0]):
            best = (new, e)
    if best and bmesh.ops.rotate_edges(bm, edges=[best[1]], use_ccw=False)["edges"]:
        log["flip"] += 1
        return True
    return False


# stage 1, verifier round 2: the round-2 rock's carve leaves a few needles whose short edge is 0.28-0.35 stud, out of
# reach of a 0.1 move (collapse needs short edge <= 2 x max_move); 0.18 clears them, still far below what reads
CLEAN_MOVE = 0.18


def _clean(o, movable, max_move=0.1):
    """Stage 2 sliver pass on a finished boolean result, written back to the mesh:
    - verts on only two edges (points left in the middle of a crease or rim, within max_move of the straight line
      through their neighbours) are dissolved: they shape nothing, and where the two faces at a narrow crevice
      both run through one, triangulating both faces would clip the same ear twice (a non-manifold fin);
    - quads and n-gons are triangulated (BEAUTY);
    - then _desliver."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    v2 = []
    for v in bm.verts:
        if len(v.link_edges) == 2 and all(len(f.verts) > 3 for f in v.link_faces) and movable(v, v.co):
            a, c = (e.other_vert(v) for e in v.link_edges)
            p, _ = intersect_point_line(v.co, a.co, c.co)
            if (p - v.co).length < max_move and (p.z == v.co.z or movable(v, p)):
                v2.append(v)
    bmesh.ops.dissolve_verts(bm, verts=v2)
    # quads too: the booleans leave concave and bent ones, whose split depends on whoever triangulates them
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    log = _desliver(bm, movable, min_angle=5.0, max_move=max_move)
    log["dissolved_v2"] = len(v2)
    bm.to_mesh(o.data)
    bm.free()
    return log


def _self_union(o):
    """One exact boolean union of everything in the hero at once, self intersection on. The crystals sink into the
    seat and into each other; the top shell's flat contact ring lies exactly on the bottom shell's flat top
    (Asset.finish has already welded their shared ring verts), so the coincident faces cancel and the outer and
    inner walls join along the shared ring with no seam band."""
    empty = bpy.data.collections.new("_m011_union")
    m = o.modifiers.new("U", "BOOLEAN")
    m.operation, m.solver, m.operand_type, m.collection = "UNION", "EXACT", "COLLECTION", empty
    m.use_self, m.material_mode = True, "TRANSFER"
    try:
        with M._override(o):
            bpy.ops.object.modifier_apply(modifier=m.name)
    finally:
        bpy.data.collections.remove(empty)


def hero(a):
    top = bpy.data.objects["AmethystShellTop"]
    bottom = bpy.data.objects["AmethystShellBottom"]
    sh = bpy.data.objects["AmethystShard"]
    vb = _paste(a, bottom, _frame(bottom))
    vt = _paste(a, top, _frame(top))
    # the top shell sits exactly on the bottom shell: one float value for the contact plane on both (the round
    # trip through each part's offset leaves the odd last-bit difference, which would make the faces only nearly
    # coplanar)
    ring_b = [v for v in vb if abs(v.co.z - ZC) < 1e-4]
    for v in vb + vt:
        if abs(v.co.z - ZC) < 1e-4:
            v.co.z = ZC
    # each of the top's ring verts onto its twin in the bottom shell, exactly
    kd = KDTree(len(ring_b))
    for i, v in enumerate(ring_b):
        kd.insert(v.co, i)
    kd.balance()
    twin = {}
    for v in vt:
        co, i, d = kd.find(v.co)
        if d < 1e-4:
            v.co = co
            twin[v] = ring_b[i]
    # where a face of the top's contact ring and one of the bottom's flat top have the same corners, the two cancel:
    # delete both now (Asset.finish welds the shared ring, and the weld would keep one of each such pair, leaving
    # a mesh that is no longer a closed volume)
    on_ring = set(ring_b)
    below = {frozenset(f.verts): f for v in ring_b for f in v.link_faces if on_ring.issuperset(f.verts)}
    pairs = []
    for f in {f for v in twin for f in v.link_faces}:
        corners = frozenset(twin.get(v) for v in f.verts)
        if corners in below:
            pairs += [f, below[corners]]
    bmesh.ops.delete(a.bm, geom=pairs, context="FACES")
    for c in CRYSTALS:
        _paste(a, sh, _crystal_matrix(c[0]) @ _frame(sh), tint=BACK_TINT.get(c[0], 1.0))


def _glint_fx(sh):
    """Stage 6 ore_glint sockets, (kind, build-frame loc, overrides) for M.mk's fx: per GLINTS entry, the box round
    the top of its crystals' tip pyramids (the point, and the shoulder ring moved GLINT_TIP of the way up to it,
    through _crystal_matrix), padded by GLINT_PAD. (A box over the whole shoulder ring, or over two crystals, left
    corners of empty air where twinkles floated off the crystals.)"""
    pts0 = [_frame(sh) @ v.co for v in sh.data.vertices]
    apex = max(pts0, key=lambda p: p.z)
    shoulder = SHARD["root"] + SHARD["body"] + 0.3 * SHARD["tip"]
    tips = [apex] + [p.lerp(apex, GLINT_TIP) for p in pts0 if abs(p.z - shoulder) < 0.05]
    out = []
    for labels, rate, size in GLINTS:
        pts = [_crystal_matrix(lb) @ p for lb in labels for p in tips]
        lo = Vector([min(p[i] for p in pts) - GLINT_PAD for i in range(3)])
        hi = Vector([max(p[i] for p in pts) + GLINT_PAD for i in range(3)])
        d = hi - lo
        em = dict(GLINT, rate=rate, size=[0, size, 0],
                  shape=[round(d.x, 2), round(d.z, 2), round(d.y, 2)])   # Roblox XYZ: x, height, depth
        out.append(("ore_glint", tuple(round(c, 3) for c in (lo + hi) / 2), {"emitters": [em]}))
    return out


def _vfx():
    """Stage 6: the hero's sockets (build frame), the cave light first."""
    light = {k: STUDIO_LIGHT[k] for k in ("color", "brightness", "range", "shadows")}
    light["flicker"] = False
    return [("crystal_glow", CAVE_LIGHT, {"light": light})] + _glint_fx(bpy.data.objects["AmethystShard"])


NOTES = {
    "Amethyst":"amethyst geode: one faceted stone boulder hollowed out, a thick rounded lip round the opening and a "
                "low rounded front lip, bare stone inside, seven purple crystals (copies of one shard) growing from "
                "the hollow's seat; one closed mesh. VFX: crystal_glow (steady violet PointLight in the cave, shadows on) and "
                "4 ore_glint (sparse violet twinkles on the main, left, right and far-right crystal tips)",
    "AmethystShellTop": "Top Shell: thick hooded half-egg of stone, rounded lip round the mouth, flat contact ring "
                        "underneath, bare stone inside",
    "AmethystShellBottom": "Bottom Shell: the lower half of the stone egg, a shallow rocky bowl; flat contact top "
                           "at the back and sides, a low rounded lip at the front, small flat crystal seat inside",
    "AmethystShard": "Crystal (reusable): six-sided purple crystal, short root point, long body, pointed tip",
}


def build(render=True):
    M.coll(NUM, TITLE)
    palette()
    top = M.mk(SHEET, "AmethystShellTop", top_shell, subject=TITLE, role="part", notes=NOTES["AmethystShellTop"],
               budget=1000, collision="hull")
    bottom = M.mk(SHEET, "AmethystShellBottom", bottom_raw, subject=TITLE, role="part",
                  notes=NOTES["AmethystShellBottom"], budget=1000, collision="hull")
    M.union_loose(bottom)
    M.carve(bottom, bottom_raw, bottom_cutter)
    _tidy(bottom)
    # slivers off; the ground and the contact top stay flat, and the contact ring points (where the top shell's
    # walls land) never move
    off = M._build_offset(bottom_raw)
    cleaned = {"AmethystShellBottom": _clean(bottom, _plane_lock(
        (0.0, ZC), [p - off for p in _contact(OUTER, 1) + _contact(INNER, 2)]), max_move=CLEAN_MOVE)}
    sh = M.mk(SHEET, "AmethystShard", shard, subject=TITLE, role="part", notes=NOTES["AmethystShard"],
              budget=1000, collision="hull")
    audits = {"AmethystShellTop": _finish_part(top, top_shell),
              "AmethystShellBottom": _finish_part(bottom, bottom_raw),
              "AmethystShard": _finish_part(sh, shard)}
    _RIM.clear()
    _CAVE_TRIS.clear()
    for o in (top, bottom, sh):         # stage 4: colour the finished parts (the hero inherits it through _paste)
        colour_part(o)
    h = M.mk(SHEET, "Amethyst", hero, subject=TITLE, role="hero", notes=NOTES["Amethyst"], budget=4000,
             collision="hull", fx=_vfx())
    _self_union(h)
    M.union_loose(h)            # one shell now: only its cleanup runs (merge, degenerate faces, specks, normals)
    cleaned["Amethyst"] = _clean(h, _plane_lock((0.0,)), max_move=CLEAN_MOVE)
    hoff = M._build_offset(hero) + _bottom_centre(h)       # hero mesh coords -> build frame (finish re-centres)
    audits["Amethyst"] = M.finish(h, union=False, uv=UV)
    p = _Paint(h, off=hoff)     # the crystals' violet light in the cave, on the hero's own faces (the union splits
    _crystal_light(p)           # the seat round the crystal roots into finer faces than the bottom shell has)
    p.done()
    for o in (h, top, bottom, sh):
        if o.name in SHADING_OK:
            o["kit_shading_ok"] = SHADING_OK[o.name]
        elif "kit_shading_ok" in o:
            del o["kit_shading_ok"]
    objs = [h, top, bottom, sh]
    M.display(NUM, objs, TITLE)
    dropped = _drop_unused(objs)
    out = {"audit": [audits[o.name] for o in objs], "cleaned": cleaned, "dropped": dropped,
           "problems": K.check(objs)}
    if render:
        out["views"] = render_views(objs)
    return out


def _drop_unused(objs):
    """Stage 2 housekeeping after a rebuild: remove this model's data nothing uses any more, i.e. the previous
    build's meshes (orphaned when mk replaced the objects) and the palette's mix keys no face ended up with
    (FB_m011_* materials with no users). Then name each mesh after its object."""
    names = {o.name for o in objs}
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.split(".")[0] in names]
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m011_")]
    out = {"meshes": len(meshes), "materials": sorted(m.name for m in mats)}
    for m in meshes:
        bpy.data.meshes.remove(m)
    for m in mats:
        bpy.data.materials.remove(m)
    for o in objs:
        if o.data.name != o.name and o.name not in bpy.data.meshes:
            o.data.name = o.name
    return out


def render_views(objs):
    h, top, bottom, sh = objs
    saved = M.explode(objs[1:], {})
    shown = []
    try:
        hx, hy = h.location.x, h.location.y
        x0 = hx + 40
        top.location = (x0 + _frame(top).translation.x, hy + _frame(top).translation.y, 11.6)
        bottom.location = (x0 + _frame(bottom).translation.x, hy + _frame(bottom).translation.y, 0)
        sh.location = (x0 + 0.1, hy - 0.8, 4.4 + EXPL_LIFT)
        # the sheet's exploded view lays out four crystals: the hero's variants of the one reusable shard, shown
        # as temporary linked copies (same mesh, the hero's scales and a lean), removed again below
        for name, dx, dz, sxy, sz, tilt in EXPLODED_CRYSTALS:
            c = bpy.data.objects.new(f"_m011_expl_{name}", sh.data)
            sh.users_collection[0].objects.link(c)
            c.location = (x0 + dx, hy - 0.8, dz + EXPL_LIFT)
            c.rotation_euler = (0.0, math.radians(tilt), 0.0)
            c.scale = (sxy, sxy, sz)
            shown.append(c)
        bpy.context.view_layer.update()
        # (verifier round 2: from 14 degrees the camera looked up into the raised top shell; the sheet looks down
        # on its dome)
        extra = {"exploded": (objs[1:] + shown, -14, 30), "part_top": ([top], -20, 22),
                 "part_top_under": ([top], 10, -40), "part_bottom": ([bottom], -20, 25), "part_shard": ([sh], -20, 12)}
        return M.views(NUM, [h], extra=extra)
    finally:
        for c in shown:
            bpy.data.objects.remove(c, do_unlink=True)
        M.restore(saved)
        M.display(NUM, objs, TITLE)


# the exploded shot's other three crystals (the sheet: a chunky leaning one left, a slimmer leaning one right and a
# small one low between): (name, x from the shot's centre, z, scale xy, scale z, lean about y in degrees)
EXPL_LIFT = 1.2     # the crystals float clear above the bottom shell, as on the sheet (verifier round 2)
EXPLODED_CRYSTALS = (("Chunky", -3.6, 4.6, 0.95, 0.68, -22.0), ("Slim", 4.0, 4.4, 0.72, 0.85, 14.0),
                     ("Small", 2.1, 3.6, 0.42, 0.4, 0.0))
