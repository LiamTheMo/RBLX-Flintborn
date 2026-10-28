"""R03 row 4: Amber resource node (faceted amber nodule cradled in chunky split wood)."""
import math

SUBJECT = "Amber"
ROW = 4
HERO_AZIMUTH = -22

PALETTE = {
    "r03_amber": ("#F28A1C", 0.3, 0, 0.5),  # Amber nodule and Raw Amber drops. Saturated orange with warm glow; yellow highlights come from lighting and facet variation only.
    "r03_amber_wood": ("#7A4A2B", 0.9, 0, 0),  # Chunky split-wood slabs and logs cradling the amber. Warm mid chocolate brown, rough.
}

AMBER = "r03_amber"
WOOD = "r03_amber_wood"
CHIPS = ["#F28A1C", "#FFB347"]
GLINT = ["#FFF1C8", "#FFC266"]


def _clamp(verts):
    for v in verts:
        if v.is_valid and v.co.z < 0.0:
            v.co.z = 0.0
    return verts


def _tint_faces(a, verts, var=0.04):
    """Small random per-face tint (+/-4%), never by height or facing."""
    faces = {f for v in verts if v.is_valid for f in v.link_faces}
    for f in faces:
        k = 1.0 + a.rng.uniform(-var, var)
        for lp in f.loops:
            c = lp[a.tint_layer]
            lp[a.tint_layer] = (c[0] * k, c[1] * k, c[2] * k, 1.0)


def piece(a, p1, p2, w, t, sides=6, taper=0.9, jag=0.22, cut=0.0, roll=0.0):
    """One chunk of split wood from p1 to p2: an irregular flattened polygon section
    (w wide, t thick), tapering, with jagged broken ends; cut slants the far end."""
    dx, dy, dz = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
    L = math.sqrt(dx * dx + dy * dy + dz * dz)
    verts = a.cyl(1.0, taper, L, sides=sides, mat=WOOD)
    cr, sr = math.cos(roll), math.sin(roll)
    radial = {}
    for v in verts:
        top = v.co.z > L / 2
        key = round(math.atan2(v.co.y, v.co.x), 2)
        k = radial.setdefault(key, a.rng.uniform(0.72, 1.15))  # same split line along the length
        k *= a.rng.uniform(0.94, 1.06)
        x, y = v.co.x * w / 2 * k, v.co.y * t / 2 * k
        v.co.x, v.co.y = x * cr - y * sr, x * sr + y * cr
        if top:
            v.co.z += a.rng.uniform(-jag, jag * 0.3) - cut * (v.co.x / w + 0.5)
        else:
            v.co.z += a.rng.uniform(-jag * 0.3, jag)
    theta = math.atan2(math.hypot(dx, dy), dz)
    yaw = math.atan2(dy, dx)
    a.transform(verts, p1, (0, theta, yaw))
    _tint_faces(a, verts)
    return _clamp(verts)


def log(a, p1, p2, w, t, segs=3, roll=0.0, sides=8):
    """Long split log: several overlapping kinked split slabs along p1->p2."""
    pts = []
    for i in range(segs + 1):
        f = i / segs
        off = 0.0 if i in (0, segs) else 0.18
        pts.append([p1[j] + (p2[j] - p1[j]) * f + a.rng.uniform(-off, off) for j in range(3)])
    d = [(p2[j] - p1[j]) / segs * 0.14 for j in range(3)]
    for i in range(segs):
        q1 = [pts[i][j] - d[j] for j in range(3)]
        q2 = [pts[i + 1][j] + d[j] for j in range(3)]
        s = a.rng.uniform(0.9, 1.05)
        piece(a, q1, q2, w * s, t * a.rng.uniform(0.9, 1.05), sides=sides, taper=a.rng.uniform(0.85, 1.0),
              jag=0.3, cut=a.rng.uniform(-0.3, 0.3), roll=roll + a.rng.uniform(-0.25, 0.25))


def spike(a, base, h, w, t, lean=(0.0, 0.0), cut=1.2, taper=0.55, sides=6, roll=0.0, splinter=True):
    """Upright broken split slab: tapering, slanted broken top."""
    top = (base[0] + lean[0], base[1] + lean[1], h + cut * 0.5)
    piece(a, (base[0], base[1], -0.1), top, w, t, sides=sides, taper=taper, jag=0.25, cut=cut, roll=roll)
    if splinter and h > 1.5:
        # a thinner split-off splinter along one face: stepped, broken split-wood look
        ox, oy = -math.sin(roll) * t * 0.35, math.cos(roll) * t * 0.35
        piece(a, (base[0] + ox, base[1] + oy, -0.1),
              (base[0] + lean[0] * 1.1 + ox, base[1] + lean[1] * 1.1 + oy, h * 0.82 + cut * 0.4),
              w * 0.55, t * 0.55, sides=5, taper=0.5, jag=0.3, cut=-cut * 0.8, roll=roll + 0.3)


def chunk(a, base, h, w, t, roll=0.0, cut=0.5):
    piece(a, (base[0], base[1], -0.1), (base[0] + 0.1, base[1], h + cut * 0.5), w, t, sides=6,
          taper=0.8, jag=0.15, cut=cut, roll=roll)


def nodule(a, loc, rot=(0, 0, 0), r=(2.55, 2.3, 3.35), subdiv=3, facets=6.0, jitter=0.09):
    """Egg-shaped faceted amber gem, centred on loc."""
    verts = a.ico(r, mat=AMBER, subdiv=subdiv, jitter=jitter, facets=facets, face_tint_var=0.06)
    for v in verts:
        tz = v.co.z / r[2]
        s = 1.0 - 0.13 * tz
        v.co.x *= s
        v.co.y *= s
    a.transform(verts, loc, rot)
    return _clamp(verts)


def drop(a, dims, cuts):
    """Angular raw amber chunk: jittered ico with planar cuts, scaled to dims, lying flat."""
    verts = a.ico((1.0, 1.0, 1.0), mat=AMBER, subdiv=2, jitter=0.16, facets=0.0, face_tint_var=0.07)
    for n, c in cuts:
        ln = math.sqrt(sum(x * x for x in n))
        n = [x / ln for x in n]
        for v in verts:
            dd = v.co.x * n[0] + v.co.y * n[1] + v.co.z * n[2]
            if dd > c:
                v.co.x -= (dd - c) * n[0]
                v.co.y -= (dd - c) * n[1]
                v.co.z -= (dd - c) * n[2]
    for v in verts:
        if v.co.z < -0.6:
            v.co.z = -0.6
    mn = [min(v.co[i] for v in verts) for i in range(3)]
    mx = [max(v.co[i] for v in verts) for i in range(3)]
    for v in verts:
        for i in range(3):
            v.co[i] = (v.co[i] - mn[i]) / (mx[i] - mn[i]) * dims[i] - (dims[i] / 2 if i < 2 else 0)
    return verts


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []

    # ---------------- hero ----------------
    a = fk.Asset("AmberNode", "R03 Amber")
    nodule(a, (0.1, 0.4, 5.0), (0.06, 0.14, 0.2))
    # long diagonal front log (high left -> low front-right, ~23 deg), two overlapping split layers
    log(a, (-3.5, -1.4, 3.2), (3.4, -3.0, 0.2), 2.4, 1.8, segs=4, roll=0.1)
    log(a, (-2.9, -0.5, 2.6), (2.6, -1.9, 0.8), 1.8, 1.4, segs=2, roll=0.5)
    # lower front-left slab under the high end of the log
    log(a, (-3.5, -2.4, 0.6), (-0.6, -3.2, 0.5), 1.8, 1.3, segs=2, roll=0.2)
    # ring slabs (back, right, left)
    log(a, (-2.8, 2.6, 0.8), (2.7, 2.8, 1.4), 2.0, 1.6, segs=2, roll=-0.2)
    log(a, (3.0, -1.6, 0.7), (2.9, 2.4, 1.1), 1.8, 1.4, segs=2, roll=0.3)
    log(a, (-3.2, -0.8, 0.8), (-2.9, 2.5, 1.2), 1.8, 1.4, segs=2, roll=-0.3)
    # upright broken spikes: left ~5, right-back ~6.5 (split pairs)
    spike(a, (-2.9, 0.0), 5.6, 2.4, 1.6, lean=(-0.3, 0.1), cut=1.3, roll=0.3)
    spike(a, (-2.3, 1.4), 4.2, 1.7, 1.3, lean=(-0.2, 0.3), cut=1.0, roll=-0.4)
    spike(a, (2.6, 1.3), 6.6, 2.6, 1.7, lean=(0.3, 0.2), cut=1.5, roll=0.3)
    spike(a, (1.6, 2.3), 4.8, 1.7, 1.3, lean=(0.1, 0.3), cut=1.0, roll=-0.2)
    spike(a, (3.1, -0.9), 3.4, 1.7, 1.3, lean=(0.3, -0.1), cut=0.9, roll=-0.6)
    # front-left chunks and a couple of chips
    chunk(a, (-3.1, -3.1), 1.6, 1.8, 1.4, roll=0.4)
    chunk(a, (-1.8, -3.6), 1.1, 1.3, 1.0, roll=-0.3)
    chunk(a, (-3.6, -2.0), 2.0, 1.2, 1.2, roll=0.2)
    piece(a, (0.3, -3.5, 0.0), (1.5, -3.7, 0.8), 0.9, 0.5, cut=0.2)
    piece(a, (2.2, 2.0, 0.0), (1.0, 3.2, 0.7), 1.0, 0.5, cut=0.2)
    piece(a, (-2.2, -2.3, 2.9), (0.2, -2.9, 2.0), 1.0, 0.6, sides=5, cut=0.3, roll=0.6)   # split chip on the log
    piece(a, (1.0, -2.6, 1.9), (2.6, -3.2, 1.0), 0.9, 0.5, sides=5, cut=-0.3, roll=-0.5)
    o = a.finish()
    vfx.add(o, "harvest_hit", (0, -2.5, 3), color=CHIPS)
    vfx.add(o, "ore_glint", (0, -2, 4.5), scale=0.8, color=GLINT)
    vfx.add(o, "heat_glow", (0, 0, 4), color=["#FFB347", "#F28A1C"],
            emitters=[
                {"name": "Heat", "texture": "glow_soft", "color": ["#FFB347", "#F28A1C"], "size": [2.0, 2.6],
                 "transparency": [0.75, 1.0], "lifetime": [1.2, 1.8], "rate": 1.5, "speed": [0.1, 0.3],
                 "spread": 10, "light_emission": 1.0},
                {"name": "Motes", "texture": "dust_mote", "color": ["#FFD27A", "#F28A1C"], "size": [0.25, 0.1],
                 "transparency": [0.3, 1.0], "lifetime": [2.0, 3.0], "rate": 1.2, "speed": [0.2, 0.5],
                 "spread": 40, "light_emission": 1.0},
            ],
            light={"color": "#FFA23A", "brightness": 0.6, "range": 9, "flicker": False})
    out.append(kit.tag(o, "hero", collision="hull", budget=4000,
                       notes="harvest_hit: amber chips on the front strike face; ore_glint: twinkle on the "
                             "glossy nodule front; heat_glow: soft warm amber light + motes at the nodule core"))

    # ---------------- parts ----------------
    a = fk.Asset("AmberNodule", "R03 Amber")
    nodule(a, (0, 0, 3.25), (0.0, 0.1, 0.2), r=(2.5, 2.25, 3.25))
    o = a.finish()
    vfx.add(o, "ore_glint", (0, -2, 3.5), scale=0.8, color=GLINT)
    out.append(kit.tag(o, "part", collision="hull", budget=1500, notes="ore_glint: glossy nodule twinkle"))

    a = fk.Asset("AmberWoodBase", "R03 Amber")
    log(a, (-3.3, -0.9, 1.5), (3.2, 0.8, 0.5), 2.3, 1.8, segs=3, roll=0.1)
    log(a, (-2.6, 0.0, 0.9), (2.4, 1.5, 0.6), 1.7, 1.3, segs=2, roll=0.5)
    log(a, (-3.2, -2.0, 0.5), (-0.6, -2.3, 0.45), 1.6, 1.2, segs=2, roll=0.2)
    spike(a, (-3.2, -0.6), 3.7, 2.2, 1.6, lean=(-0.4, 0.1), cut=0.9, roll=0.3)
    spike(a, (3.1, 0.9), 4.0, 2.3, 1.6, lean=(0.35, 0.2), cut=0.9, roll=0.4)
    chunk(a, (-1.1, -2.1), 1.0, 1.3, 1.0, roll=0.4)
    chunk(a, (1.3, 2.0), 1.1, 1.3, 1.0, roll=-0.3)
    piece(a, (-1.8, -1.5, 2.2), (0.4, -1.0, 1.6), 0.9, 0.5, sides=5, cut=0.3, roll=0.6)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="hull", budget=2000, notes="wood cradle"))

    a = fk.Asset("AmberSideWood", "R03 Amber")
    spike(a, (0, 0), 2.1, 1.9, 1.8, lean=(0.1, 0.0), cut=0.8, taper=0.72, sides=7, roll=0.3, splinter=False)
    chunk(a, (0.65, -0.6), 0.7, 0.6, 0.5, roll=0.5, cut=0.3)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="hull", budget=600, notes="small split stump"))

    # ---------------- drops ----------------
    a = fk.Asset("RawAmberDrop", "R03 Amber")
    drop(a, (1.5, 1.1, 1.1), [((1, 0.3, 0.6), 0.55), ((-0.6, -1, 0.4), 0.6), ((0.2, 0.9, 1), 0.6),
                              ((-1, 0.4, 0.2), 0.7), ((0.5, -0.8, -0.3), 0.7), ((0, 0, 1), 0.75)])
    o = a.finish()
    out.append(kit.tag(o, "drop", collision="box", budget=300, notes="raw amber chunk"))

    a = fk.Asset("RawAmberDropB", "R03 Amber")
    a.rng.seed(7)
    drop(a, (1.2, 1.0, 1.4), [((0.8, -0.5, 1), 0.55), ((-1, 0.2, 0.5), 0.6), ((0.3, 1, -0.2), 0.65),
                              ((0.1, -1, 0.6), 0.6), ((1, 0.6, -0.3), 0.7), ((0, 0, 1), 0.7), ((-0.7, -0.6, 0.8), 0.6)])
    o = a.finish()
    out.append(kit.tag(o, "drop", collision="box", budget=300, notes="raw amber chunk B"))

    # ---------------- depleted ----------------
    a = fk.Asset("AmberDepleted", "R03 Amber")
    log(a, (-3.5, -1.6, 0.85), (3.4, -2.1, 0.3), 2.0, 1.2, segs=3, roll=0.15)
    log(a, (-2.8, 1.5, 0.5), (2.8, -0.1, 0.8), 1.5, 1.1, segs=2, roll=-0.3)   # crossing slab behind
    spike(a, (-1.5, 0.3), 2.2, 2.1, 1.1, lean=(-0.25, 0.05), cut=0.5, roll=0.15)
    spike(a, (1.4, 0.0), 2.2, 2.0, 1.1, lean=(0.25, 0.05), cut=-0.5, roll=-0.15)
    chunk(a, (-3.3, -2.3), 1.1, 1.2, 1.0, roll=0.4)
    chunk(a, (3.4, -0.3), 0.8, 0.9, 0.8, roll=-0.4)
    o = a.finish()
    vfx.add(o, "harvest_deplete", (0, 0, 0.5), color=CHIPS)
    out.append(kit.tag(o, "depleted", collision="hull", budget=2000,
                       notes="Depleted (Base); harvest_deplete: amber chip burst at base centre"))
    return out
