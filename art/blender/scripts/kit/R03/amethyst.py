"""R03 Amethyst: cracked-open geode resource node, parts, drops and depleted base.

The shell is built from chamfered prism slabs (flat planes, crisp edges) instead of
subdivided boulders so it reads as the reference's chiselled low-poly slabs.
"""
import math
import random

import bmesh
from mathutils import Euler, Vector

SUBJECT = "Amethyst"
ROW = 3
SIDE_AZIMUTH = 90

PALETTE = {
    "r03_rock": ("#8C7E78", 0.9, 0, 0),
    "r03_amethyst": ("#8A4BC9", 0.25, 0, 0.35),
    "r03_geode_dark": ("#3B2358", 0.9, 0, 0),
}

ROCK, GEM, DARK = "r03_rock", "r03_amethyst", "r03_geode_dark"
D = math.radians


def chunk(a, outline, rings, to_world, mat, rng, jit=0.07):
    """Faceted prism: `outline` (u, v) points, `rings` [(w, scale, slope_u, slope_v)].
    Each ring is the outline scaled about its centroid and jittered in-plane (caps stay planar)."""
    n = len(outline)
    cu = sum(p[0] for p in outline) / n
    cv = sum(p[1] for p in outline) / n
    bm = a.bm
    loops = []
    for ring in rings:
        w, s = ring[0], ring[1]
        su = ring[2] if len(ring) > 2 else 0.0
        sv = ring[3] if len(ring) > 3 else 0.0
        loop = []
        for (u, v) in outline:
            uu = cu + (u - cu) * s + rng.uniform(-jit, jit)
            vv = cv + (v - cv) * s + rng.uniform(-jit, jit)
            ww = w + su * (uu - cu) + sv * (vv - cv)
            loop.append(bm.verts.new(to_world(uu, vv, ww)))
        loops.append(loop)
    faces = [bm.faces.new(list(reversed(loops[0]))), bm.faces.new(loops[-1])]
    for l0, l1 in zip(loops, loops[1:]):
        for i in range(n):
            faces.append(bm.faces.new((l0[i], l0[(i + 1) % n], l1[(i + 1) % n], l1[i])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    verts = [v for l in loops for v in l]
    a._finish(verts, mat)
    return verts


def sector(rin, rout, t0, t1, zc=0.0, xc=0.0, mid=True):
    """Annular-sector outline in the XZ plane; angle 0 = top, +90 = +X."""
    pts = []
    ts = [t0, (t0 + t1) / 2, t1] if mid else [t0, t1]
    for t in ts:
        pts.append((xc + rout[0] * math.sin(D(t)), zc + rout[1] * math.cos(D(t))))
    for t in (t1, t0):
        pts.append((xc + rin[0] * math.sin(D(t)), zc + rin[1] * math.cos(D(t))))
    return pts


def blob_outline(rng, sx, sy, n=6, ang=0.0, cx=0.0, cy=0.0):
    """Irregular convex-ish polygon of half-sizes sx, sy, rotated by ang about z."""
    pts = []
    ca, sa = math.cos(ang), math.sin(ang)
    for i in range(n):
        t = 2 * math.pi * i / n + rng.uniform(-0.25, 0.25)
        r = rng.uniform(0.88, 1.05)
        x, y = sx * r * math.cos(t), sy * r * math.sin(t)
        pts.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return pts


def block(a, rng, cx, cy, sx, sy, h, ang=0.0, mat=ROCK, n=5, slope=(0.0, 0.0), top=0.68):
    """Chunky low rock: straight-ish sides, slanted chamfer and a flat, tilted top."""
    out = blob_outline(rng, sx, sy, n, D(ang), cx, cy)
    su, sv = slope
    rings = [(0.0, 0.97), (h * 0.42, 1.07, su * 0.3, sv * 0.3),
             (h * 0.8, 0.93 + rng.uniform(-0.04, 0.04), su * 0.7 + rng.uniform(-0.08, 0.08), sv * 0.7),
             (h, top, su, sv)]
    return chunk(a, out, rings, lambda u, v, w: (u, v, w), mat, rng)


def arch_slabs(a, rng, edges, rin, rout, zc, y0, y1, mat=ROCK, tilt=0.0, xc=0.0, gap=1.2,
               front=0.78, back=0.9):
    """Ring of chamfered slabs between consecutive `edges` angles, extruded y0..y1, then
    tilted about X by `tilt` degrees (top goes back, +Y)."""
    ct, st = math.cos(D(tilt)), math.sin(D(tilt))

    def tw(u, v, w):
        return (u, w * ct + v * st, -w * st + v * ct)

    rough = front < 1.0
    for i, (t0, t1) in enumerate(zip(edges, edges[1:])):
        if rough:
            k = rng.uniform(0.94, 1.08)
            ro = (rout[0] * k, rout[1] * k)
            ri = (rin[0] * rng.uniform(0.97, 1.03), rin[1] * rng.uniform(0.97, 1.03))
            a0, a1 = t0 + gap, t1 - gap
            out = []
            # outer edge: 4 points with random radial bumps -> irregular chiselled outline
            for f, bump in ((0.0, rng.uniform(0.93, 1.0)), (0.33, rng.uniform(1.0, 1.1)),
                            (0.67, rng.uniform(0.98, 1.1)), (1.0, rng.uniform(0.93, 1.0))):
                t = D(a0 + (a1 - a0) * f)
                out.append((xc + ro[0] * bump * math.sin(t), zc + ro[1] * bump * math.cos(t)))
            for t in (D(a1), D((a0 + a1) / 2 + rng.uniform(-5, 5)), D(a0)):
                k2 = rng.uniform(0.97, 1.04)
                out.append((xc + ri[0] * k2 * math.sin(t), zc + ri[1] * k2 * math.cos(t)))
            yf = y0 + rng.uniform(-0.25, 0.2)
            d = y1 - yf
            rings = [(yf, front + rng.uniform(-0.05, 0.05), rng.uniform(-0.18, 0.18), rng.uniform(-0.18, 0.18)),
                     (yf + 0.22 * d, 1.0), (yf + 0.6 * d, 0.97, rng.uniform(-0.1, 0.1), 0.0), (y1, back)]
        else:
            out = sector(rin, rout, t0 + gap, t1 - gap, zc, xc)
            rings = [(y0, 1.0), (y1, 1.0)]
        chunk(a, out, rings, tw, mat, rng)


def plate(a, rng, rx, rz, zc, y0, y1, mat, tilt=0.0, n=10, xc=0.0, half=False, s1=0.9):
    """Elliptic (or half-elliptic) plate in XZ extruded along y, tilted like the arch."""
    ct, st = math.cos(D(tilt)), math.sin(D(tilt))

    def tw(u, v, w):
        return (u, w * ct + v * st, -w * st + v * ct)

    if half:
        out = [(xc + rx * math.sin(D(t)), zc + rz * math.cos(D(t)))
               for t in [90 - 180 * i / (n - 1) for i in range(n)]]
    else:
        out = [(xc + rx * math.sin(2 * math.pi * i / n), zc + rz * math.cos(2 * math.pi * i / n))
               for i in range(n)]
    chunk(a, out, [(y0, 1.0), (y1, s1)], tw, mat, rng, jit=0.05)


def crystal(a, base, r, h, rot=(0, 0, 0), tip=0.3, sides=6):
    """Hexagonal prism with a pointed faceted tip; `h` is the total height."""
    tip_h = h * tip
    body = h - tip_h
    a.cyl(r, r * 1.05, body, sides=sides, loc=base, rot=rot, mat=GEM, jitter=0.02)
    top = Vector(base) + (Vector((0, 0, body)) @ Euler(rot).to_matrix().transposed())
    a.cyl(r * 1.05, 0.0, tip_h, sides=sides, loc=tuple(top), rot=rot, mat=GEM, cap=False)


def clamp_floor(a):
    for v in a.bm.verts:
        if v.co.z < 0:
            v.co.z = 0.0


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []
    glint_emitters = [
        {"name": "Glint", "texture": "spark_diamond", "color": ["#F4E6FF", "#B47CFF"], "size": [0, 0.28, 0],
         "transparency": [0.05, 1.0], "lifetime": [0.4, 0.7], "rate": 0.7, "speed": [0, 0], "spread": 0,
         "light_emission": 1.0, "rotation": [0, 90], "shape": [2.2, 1.2, 3.0]},
        {"name": "Motes", "texture": "dust_mote", "color": ["#C79BFF", "#9A5CE6"], "size": [0.09, 0.03],
         "transparency": [0.45, 1.0], "lifetime": [2, 3.2], "rate": 1.2, "speed": [0.1, 0.25], "spread": 180,
         "light_emission": 1.0, "shape": [2.6, 1.6, 2.6]},
    ]
    glow_light = {"color": "#9A5CE6", "brightness": 0.9, "range": 10, "flicker": False}
    chips = ["#A86BE0", "#8A4BC9"]

    # ---------------- HERO ----------------
    a = fk.Asset("AmethystNode", "R03 Amethyst", seed=31)
    rng = random.Random(31)
    TILT, ZC = 24, 3.55
    RIN, ROUT = (2.35, 2.65), (3.95, 3.85)
    # shell: 7 chamfered slabs around a wide oval opening, tilted back so the pit shows from above
    arch_slabs(a, rng, [-150, -98, -48, 4, 54, 104, 150],
               RIN, ROUT, ZC, -1.4, 2.0, tilt=TILT, gap=-2.5, front=0.8, back=0.62)
    # back of the dome (tucked inside the tapered slab backs so the shell reads rounded)
    plate(a, rng, 3.1, 3.0, ZC, 1.0, 2.3, ROCK, tilt=TILT, n=9, s1=0.7)
    # dark cavity lining: inner wall band behind a grey ~0.8 rim, and the back face
    arch_slabs(a, rng, [-150, -90, -30, 30, 90, 150], (RIN[0] - 0.15, RIN[1] - 0.15),
               (RIN[0] + 0.12, RIN[1] + 0.12), ZC, -0.55, 0.85, mat=DARK, tilt=TILT, gap=0,
               front=1.0, back=1.0)
    plate(a, rng, RIN[0] + 0.1, RIN[1] + 0.1, ZC, 0.65, 0.85, DARK, tilt=TILT, n=9, s1=1.0)
    # cavity floor
    chunk(a, blob_outline(rng, 2.5, 1.6, 8, 0, 0, -0.1), [(0.0, 1.0), (1.15, 0.95)],
          lambda u, v, w: (u, v, w), DARK, rng)
    # crystals: tall centre, two side ones leaning out ~24 deg, a small outer one, two small front
    crystal(a, (0, -0.3, 1.0), 1.1, 4.6, (D(-2), 0, 0), tip=0.32)
    crystal(a, (-1.4, -0.4, 1.0), 0.85, 3.3, (D(6), D(-22), 0))
    crystal(a, (1.4, -0.4, 1.0), 0.85, 3.3, (D(6), D(22), 0))
    crystal(a, (2.05, 0.1, 1.0), 0.5, 2.4, (D(4), D(38), 0))
    crystal(a, (-0.6, -1.3, 1.0), 0.52, 2.0, (D(16), D(-14), 0))
    crystal(a, (0.62, -1.35, 1.0), 0.47, 1.85, (D(16), D(16), 0))
    # front-bottom lip crescent: three chunky flat-topped rocks
    block(a, rng, -2.6, -2.2, 2.0, 1.35, 2.1, ang=-30, slope=(0.12, -0.2), n=5, top=0.62)
    block(a, rng, 0.0, -2.75, 1.9, 1.2, 1.85, ang=8, slope=(-0.08, -0.22), n=5, top=0.62)
    block(a, rng, 2.6, -2.2, 2.0, 1.35, 2.2, ang=24, slope=(-0.12, -0.2), n=5, top=0.62)
    clamp_floor(a)
    o = a.finish()
    o["kit_shading_ok"] = "r03_geode_dark is the cavity lining, a separate material from the grey shell"
    vfx.add(o, "harvest_hit", (0, -3, 2.5), scale=0.6, color=chips)
    vfx.add(o, "ore_glint", (0, -1, 3), emitters=glint_emitters, light=glow_light)
    out.append(kit.tag(o, "hero", collision="precise", budget=4500,
                       notes="Hollow geode node. harvest_hit: amethyst chips on the front strike face; "
                             "ore_glint: small violet twinkles + motes + soft violet PointLight on the big crystal."))

    # ---------------- PARTS ----------------
    a = fk.Asset("AmethystTopShell", "R03 Amethyst", seed=32)
    rng = random.Random(32)
    arch_slabs(a, rng, [-96, -50, -4, 46, 96], (2.45, 1.95), (3.95, 3.4), 0.0, -2.2, 1.6, gap=-2.5, back=0.75)
    plate(a, rng, 3.85, 3.3, 0.0, 1.2, 2.2, ROCK, n=8, half=True, s1=0.85)
    # hollow dark underside (separate inner surface)
    arch_slabs(a, rng, [-96, -32, 32, 96], (2.3, 1.8), (2.52, 2.02), 0.0, -1.6, 1.25, mat=DARK,
               gap=0, front=1.0, back=1.0)
    plate(a, rng, 2.45, 1.95, 0.0, 1.05, 1.25, DARK, n=8, half=True, s1=1.0)
    clamp_floor(a)
    o = a.finish()
    o["kit_shading_ok"] = "hollow underside is the cavity lining r03_geode_dark, a separate material"
    out.append(kit.tag(o, "part", collision="precise", budget=1800,
                       notes="Top half-dome shell: arched roof slab with a dark hollow underside."))

    a = fk.Asset("AmethystBottomShell", "R03 Amethyst", seed=33)
    rng = random.Random(33)
    block(a, rng, -2.75, 0.35, 1.3, 1.7, 2.9, ang=-12, slope=(0.1, -0.08))
    block(a, rng, -1.2, -1.45, 1.5, 1.1, 2.4, ang=-18, slope=(0.0, -0.12))
    block(a, rng, 1.2, -1.45, 1.5, 1.1, 2.2, ang=14, slope=(0.0, -0.12))
    block(a, rng, 2.75, 0.35, 1.3, 1.7, 2.7, ang=10, slope=(-0.1, -0.08))
    chunk(a, blob_outline(rng, 2.3, 1.5, 8, 0, 0, 0.3), [(0.0, 1.0), (0.7, 0.95)],
          lambda u, v, w: (u, v, w), DARK, rng)
    clamp_floor(a)
    o = a.finish()
    o["kit_shading_ok"] = "inner floor is the cavity lining r03_geode_dark, a separate material"
    out.append(kit.tag(o, "part", collision="precise", budget=1800, notes="Bottom U-shaped shell basin."))

    for name, r, h, rot in [("AmethystCrystal", 0.75, 4.0, (0, 0, 0)),
                            ("AmethystCrystalB", 0.62, 3.5, (0, D(-14), 0)),
                            ("AmethystCrystalC", 0.58, 3.0, (0, D(14), 0)),
                            ("AmethystCrystalD", 0.45, 2.0, (0, D(5), 0))]:
        a = fk.Asset(name, "R03 Amethyst", seed=hash(name) % 1000)
        crystal(a, (0, 0, 0), r, h, rot, tip=0.3)
        clamp_floor(a)
        o = a.finish()
        out.append(kit.tag(o, "part", collision="box", budget=700, notes="Single amethyst crystal."))

    # ---------------- DROPS ----------------
    a = fk.Asset("AmethystCrystalDrop", "R03 Amethyst", seed=41)
    a.ico((0.7, 0.5, 0.5), (0, 0, 0.5), (D(10), D(-15), D(20)), mat=GEM, subdiv=2, jitter=0.14, facets=12)
    clamp_floor(a)
    o = a.finish()
    out.append(kit.tag(o, "drop", collision="box", budget=300, notes="Amethyst nugget drop."))

    a = fk.Asset("AmethystCrystalDropB", "R03 Amethyst", seed=42)
    a.ico((0.55, 0.5, 0.7), (0, 0, 0.7), (D(-8), D(12), D(30)), mat=GEM, subdiv=2, jitter=0.14, facets=12)
    clamp_floor(a)
    o = a.finish()
    out.append(kit.tag(o, "drop", collision="box", budget=300, notes="Upright amethyst nugget drop."))

    # ---------------- DEPLETED ----------------
    a = fk.Asset("AmethystDepleted", "R03 Amethyst", seed=51, tint_var=0.04)
    rng = random.Random(51)
    block(a, rng, -2.9, -0.2, 1.1, 1.3, 1.6, ang=-25, slope=(0.08, -0.1))
    block(a, rng, -1.3, -1.8, 1.3, 1.0, 1.35, ang=-8, slope=(0.0, -0.12))
    block(a, rng, 0.5, -2.1, 1.1, 0.95, 1.2, ang=12, slope=(0.0, -0.12))
    block(a, rng, -2.3, 1.6, 1.1, 0.9, 1.3, ang=25, slope=(0.0, 0.1))
    chunk(a, blob_outline(rng, 1.9, 1.4, 8, 0, -1.0, -0.2), [(0.0, 1.0), (0.45, 0.95)],
          lambda u, v, w: (u, v, w), DARK, rng)
    # cracked shell half-ring standing at the back-right (~3.5 high)
    arch_slabs(a, rng, [-92, -45, 0, 45, 92], (1.05, 2.0), (2.05, 3.5), 0.0, 0.0, 2.2, xc=1.85, gap=-2.5, back=0.75)
    arch_slabs(a, rng, [-90, -30, 30, 90], (0.92, 1.88), (1.1, 2.06), 0.0, 0.5, 2.0, mat=DARK, xc=1.85,
               gap=0, front=1.0, back=1.0)
    # rubble
    block(a, rng, 3.3, -1.6, 0.5, 0.42, 0.6, ang=20)
    block(a, rng, 1.9, -2.6, 0.42, 0.36, 0.5, ang=-15)
    block(a, rng, -3.5, 1.9, 0.45, 0.4, 0.5, ang=5)
    clamp_floor(a)
    o = a.finish()
    o["kit_shading_ok"] = "empty cavity lining r03_geode_dark, a separate material"
    vfx.add(o, "harvest_deplete", (0, 0, 0.5), scale=0.6)
    out.append(kit.tag(o, "depleted", collision="precise", budget=2500,
                       notes="Broken empty geode base. harvest_deplete: rock burst at base centre."))
    return out
