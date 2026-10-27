"""W13 row 2: Guard Lodge - plank hut with a pitched canvas roof.

Ridge runs along Y (gables face -Y front / +Y back). The reference draws the
hero from the front-right, so HERO_AZIMUTH = +22 (window wall +X faces camera).
"""
import math

from mathutils import Vector

SUBJECT = "GuardLodge"
ROW = 2
HERO_AZIMUTH = 46   # reference draws the hero from the front-RIGHT (see goals file)
SIDE_AZIMUTH = 62   # reference SIDE cell is a side-on three-quarter, not a flat elevation

PALETTE = {
    "w13_timber": ("#A9612C", 0.85, 0, 0),
    "w13_canvas": ("#E6D2A4", 0.95, 0, 0),
    "w13_stone": ("#8A9199", 0.9, 0, 0),
    "w13_moss": ("#4C9A3C", 0.9, 0, 0),
    "w13_glass": ("#2E4256", 0.4, 0, 0),
    "w13_lantern_glow": ("#FFB23A", 0.4, 0, 1.5),
}

T, C, S, M, G, L = ("w13_timber", "w13_canvas", "w13_stone", "w13_moss",
                    "w13_glass", "w13_lantern_glow")
SLOPE = 0.98         # roof rise per stud of run (steep tent roof)
OVER = 1.0           # eave overhang past the side walls
EAVE_Z = 8.1         # canvas height at the eave edge
WALL_TOP = 8.6
FLOOR_Z = 1.6
FOOT_H = 1.4
CB = 1.8             # corner footing block height
DOOR_W, DOOR_H = 4.5, 7.5


# ---------------------------------------------------------------- helpers
def sheet(a, pts, offs, mat):
    """Closed thin slab from a grid of top points and per-point thickness offsets."""
    import bmesh
    bm = a.bm
    R, Cn = len(pts), len(pts[0])
    top = [[bm.verts.new(pts[i][j]) for j in range(Cn)] for i in range(R)]
    bot = [[bm.verts.new(tuple(p - o for p, o in zip(pts[i][j], offs[i][j])))
            for j in range(Cn)] for i in range(R)]
    faces = []
    for i in range(R - 1):
        for j in range(Cn - 1):
            faces.append(bm.faces.new((top[i][j], top[i + 1][j], top[i + 1][j + 1], top[i][j + 1])))
            faces.append(bm.faces.new((bot[i][j], bot[i][j + 1], bot[i + 1][j + 1], bot[i + 1][j])))
    ring = ([(0, j) for j in range(Cn)] + [(i, Cn - 1) for i in range(1, R)]
            + [(R - 1, j) for j in range(Cn - 2, -1, -1)] + [(i, 0) for i in range(R - 2, 0, -1)])
    for k in range(len(ring)):
        (i1, j1), (i2, j2) = ring[k], ring[(k + 1) % len(ring)]
        faces.append(bm.faces.new((top[i2][j2], bot[i2][j2], bot[i1][j1], top[i1][j1])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    verts = [v for row in top for v in row] + [v for row in bot for v in row]
    return a._finish(verts, mat)


def ridge_z(hx):
    return EAVE_Z + SLOPE * (hx + OVER)


def canvas_z(x, hx):
    return ridge_z(hx) - SLOPE * abs(x)


def roof(a, hx, hy, rz=None, torn=None, scallops=3):
    """Pitched canvas, ridge along Y, sag between supports, scalloped eave hem."""
    rz = ridge_z(hx) if rz is None else rz
    ex = hx + OVER
    plate_u = (hx - 0.3) / ex
    nv = 12
    rng = a.rng
    for sx in (-1, 1):
        u0 = 0.0
        if torn:
            u0 = torn[0] if sx < 0 else torn[1]
        us = [u0 + (plate_u - u0) * k / 4 for k in range(5)] + [(plate_u + 1) / 2, 1.0]
        pts, offs = [], []
        for ui, u in enumerate(us):
            row, orow = [], []
            for j in range(nv + 1):
                v = j / nv
                uu = u
                if torn and ui == 0:
                    uu = u + rng.uniform(0.0, 0.09)
                if uu <= plate_u:
                    sag = 0.32 * math.sin(math.pi * uu / plate_u) * (0.45 + 0.55 * math.sin(math.pi * v))
                else:
                    sag = 0.3 * ((uu - plate_u) / (1 - plate_u)) ** 1.4
                x = sx * ex * uu
                z = rz + 0.12 - SLOPE * ex * uu - sag
                row.append((x, -(hy + 1.0) + (2 * hy + 2.0) * v, z))
                orow.append((0, 0, 0.14))
            pts.append(row)
            offs.append(orow)
        last = pts[-1]
        row, orow = [], []
        for j in range(nv + 1):
            v = j / nv
            drop = 0.25 + 0.3 * abs(math.sin(scallops * math.pi * v))
            x, y, z = last[j]
            row.append((x + sx * 0.06, y, z - drop))
            orow.append((sx * 0.14, 0, 0))
        pts.append(row)
        offs.append(orow)
        sheet(a, pts, offs, C)


def place(a, verts, loc, rotz):
    a.transform(verts, loc, (0, 0, rotz))
    return verts


def window_local(a, w=2.5):
    """Window facing -Y on a wall at y=0, centred x=0, z=0 (local)."""
    vs = []
    h = w / 2
    vs += a.box((w - 0.2, 0.12, w - 0.2), (0, -0.04, 0), mat=G)
    vs += a.plank((w + 0.4, 0.35, 0.32), (0, -0.15, h + 0.05), mat=T)
    vs += a.plank((w + 0.4, 0.35, 0.32), (0, -0.15, -h - 0.05), mat=T)
    vs += a.plank((0.32, 0.35, w + 0.1), (-h - 0.05, -0.15, 0), mat=T)
    vs += a.plank((0.32, 0.35, w + 0.1), (h + 0.05, -0.15, 0), mat=T)
    vs += a.box((0.16, 0.2, w - 0.2), (0, -0.12, 0), mat=T)
    vs += a.box((w - 0.2, 0.2, 0.16), (0, -0.12, 0), mat=T)
    vs += a.plank((w + 0.8, 0.7, 0.24), (0, -0.3, -h - 0.3), mat=T)
    return vs


def awning_local(a, w=3.5, out=1.6, z0=0.0, wall=True):
    """Canvas awning hanging from y=0 at height z0 out to -out (local)."""
    nv = 8
    pts, offs = [], []
    for k, t in enumerate((0.0, 0.5, 1.0)):
        row, orow = [], []
        for j in range(nv + 1):
            v = j / nv
            sag = 0.12 * math.sin(math.pi * t) * math.sin(math.pi * v)
            row.append((-w / 2 + w * v, -out * t, z0 - 0.55 * t - sag))
            orow.append((0, 0, 0.1))
        pts.append(row)
        offs.append(orow)
    row, orow = [], []
    for j in range(nv + 1):
        v = j / nv
        row.append((-w / 2 + w * v, -out - 0.04, z0 - 0.55 - 0.3 - 0.2 * abs(math.sin(2 * math.pi * v))))
        orow.append((0, -0.1, 0))
    pts.append(row)
    offs.append(orow)
    start = len(a.bm.verts)
    sheet(a, pts, offs, C)
    a.bm.verts.ensure_lookup_table()
    vs = [a.bm.verts[i] for i in range(start, len(a.bm.verts))]
    # raised stripe bands (same canvas, read as stripes through their edges)
    tilt = math.atan2(0.55, out)
    ln = math.hypot(0.55, out) + 0.1
    for k in range(4):
        xs = -w / 2 + w * (k + 0.5) / 4
        vs += a.box((w / 8, ln, 0.1), (xs, -out / 2, z0 - 0.275 + 0.02), rot=(tilt, 0, 0), mat=C)
    for sx in (-1, 1):
        vs += a.beam((sx * (w / 2 - 0.3), 0.0, z0 - 1.0), (sx * (w / 2 - 0.3), -out + 0.15, z0 - 0.5),
                     0.09, sides=5, mat=T, end_mat=T)
    if wall:
        vs += a.plank((w + 0.3, 0.25, 0.3), (0, -0.05, z0 + 0.05), mat=T)
    return vs


def lantern_local(a, z):
    """Lantern on a bracket; wall at y=0, lantern hangs at (0, -0.95, z)."""
    vs = []
    vs += a.box((0.3, 0.2, 1.6), (0, -0.1, z + 0.75), mat=T)
    vs += a.box((0.2, 1.05, 0.2), (0, -0.55, z + 1.4), mat=T)
    vs += a.box((0.08, 0.08, 0.35), (0, -0.95, z + 1.15), mat=T)
    vs += a.box((0.5, 0.5, 0.7), (0, -0.95, z), mat=L)
    vs += a.box((0.72, 0.72, 0.12), (0, -0.95, z - 0.41), mat=T)
    for dx in (-0.29, 0.29):
        for dy in (-0.29, 0.29):
            vs += a.box((0.1, 0.1, 0.8), (dx, -0.95 + dy, z), mat=T)
    vs += a.cyl(0.55, 0.06, 0.45, sides=4, loc=(0, -0.95, z + 0.36), rot=(0, 0, math.pi / 4), mat=T)
    return vs


def door_local(a, w=DOOR_W, h=DOOR_H, faces=(-1,)):
    """Plank door with X brace; hinge at local x=0, panel spans +x, outer face -Y, base z=0."""
    vs = []
    n = 4
    pw = w / n
    for i in range(n):
        vs += a.plank((pw - 0.04, 0.3, h), (pw * (i + 0.5), 0, h / 2), mat=T, bevel=0.05)
    dz = h - 1.6 - 0.55
    dx = w - 0.6
    ln = math.hypot(dx, dz)
    ang = math.atan2(dz, dx)
    for fy in faces:
        for zz in (0.8, h - 0.8):
            vs += a.plank((w - 0.3, 0.2, 0.55), (w / 2, fy * 0.24, zz), mat=T, bevel=0.04)
        for sgn in (1, -1):
            vs += a.plank((ln, 0.16, 0.42), (w / 2, fy * 0.25, h / 2), rot=(0, -sgn * ang, 0), mat=T, bevel=0.03)
        vs += a.box((0.25, 0.12, 0.12), (w - 0.5, fy * 0.4, h * 0.48), mat=T)
    return vs


def crate(a, loc, s=1.8):
    x, y, z = loc
    a.box((s * 0.94, s * 0.94, s * 0.94), (x, y, z + s / 2), mat=T)
    for zz in (z + 0.1, z + s - 0.1):
        a.box((s, s, 0.2), (x, y, zz), mat=T)
    for dx in (-1, 1):
        for dy in (-1, 1):
            a.box((0.2, 0.2, s), (x + dx * (s / 2 - 0.1), y + dy * (s / 2 - 0.1), z + s / 2), mat=T)
    a.box((s * 1.25, 0.12, 0.2), (x, y - s / 2 - 0.01, z + s / 2), rot=(0, math.atan2(s * 0.8, s * 0.8), 0), mat=T)


def barrel(a, loc, r=0.72, h=1.7):
    x, y, z = loc
    a.cyl(r * 0.9, r * 0.9, h, sides=10, loc=(x, y, z), mat=T)
    a.cyl(r, r, h * 0.55, sides=10, loc=(x, y, z + h * 0.22), mat=T)
    for zz in (0.2, h - 0.35):
        a.cyl(r * 1.04, r * 1.04, 0.14, sides=10, loc=(x, y, z + zz), mat=T, cap=False)


def ladder(a, base, top, width=1.2, rungs=7):
    bx, by, bz = base
    tx, ty, tz = top
    for dy in (-width / 2, width / 2):
        a.beam((bx, by + dy, bz + 0.05), (tx, ty + dy, tz), 0.13, sides=5, mat=T, end_mat=T)
    for k in range(rungs):
        t = (k + 0.6) / (rungs + 0.4)
        a.box((0.16, width, 0.16), (bx + (tx - bx) * t, by + (ty - by) * t, bz + (tz - bz) * t), mat=T)


def bbox_off(a):
    xs = [v.co.x for v in a.bm.verts]
    ys = [v.co.y for v in a.bm.verts]
    zs = [v.co.z for v in a.bm.verts]
    return Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))


# ---------------------------------------------------------------- lodge
def footing(a, hx, hy, rng, mossy=False):
    corners = [(sx * (hx - 0.3), sy * (hy - 0.3)) for sx in (-1, 1) for sy in (-1, 1)]
    for (cx, cy) in corners:
        a.stone_block((2.0, 2.0, CB), (cx, cy, CB / 2), mat=S)
    # runs between corner blocks
    for sy in (-1, 1):
        span = 2 * hx - 2.3
        n = max(2, round(span / 2.3))
        L = span / n
        for i in range(n):
            x = -hx + 1.15 + L * (i + 0.5)
            hh = FOOT_H + rng.uniform(-0.05, 0.05)
            a.stone_block((L - 0.1, 1.05, hh), (x, sy * (hy - 0.3), hh / 2), mat=S)
    for sx in (-1, 1):
        span = 2 * hy - 2.3
        n = max(2, round(span / 2.3))
        L = span / n
        for i in range(n):
            y = -hy + 1.15 + L * (i + 0.5)
            hh = FOOT_H + rng.uniform(-0.05, 0.05)
            a.stone_block((1.05, L - 0.1, hh), (sx * (hx - 0.3), y, hh / 2), mat=S)


def gable_wall(a, hx, hy, sy, door, missing=(), open_front=False):
    """Front (sy=-1) or back (sy=+1) wall: vertical planks up into the gable."""
    yc = sy * (hy - 0.3)
    jamb = DOOR_W / 2 + 0.6
    door_top = FLOOR_Z + DOOR_H
    if open_front:
        sections = [(-hx + 0.6, hx - 0.6, door_top + 0.8)]
    elif door:
        sections = [(-hx + 0.6, -jamb, FOOT_H), (-jamb, jamb, door_top + 0.8), (jamb, hx - 0.6, FOOT_H)]
    else:
        sections = [(-hx + 0.6, hx - 0.6, FOOT_H)]
    idx = 0
    for (x0, x1, zb) in sections:
        span = x1 - x0
        n = max(1, round(span / 1.1))
        w = span / n
        for i in range(n):
            xc = x0 + w * (i + 0.5)
            top = max(WALL_TOP, canvas_z(abs(xc) + w / 2, hx) - 0.3)
            idx += 1
            if idx in missing:
                continue
            if top - zb > 0.2:
                a.plank((w - 0.05, 0.5, top - zb), (xc, yc, (top + zb) / 2), mat=T, bevel=0.05)
    # horizontal beam across the gable (also the door lintel) and king post
    zb = door_top + 0.4 if (door or open_front) else WALL_TOP - 0.4
    a.plank((2 * hx - 1.0, 0.45, 0.8), (0, sy * (hy + 0.12), zb), mat=T, bevel=0.06)
    rz = ridge_z(hx)
    a.plank((0.6, 0.42, rz - 0.6 - (zb + 0.4)), (0, sy * (hy + 0.12), (rz - 0.6 + zb + 0.4) / 2), mat=T, bevel=0.05)
    # barge rafters under the canvas edge
    for sx in (-1, 1):
        a.beam((0, sy * (hy + 0.35), rz - 0.3), (sx * (hx + 0.9), sy * (hy + 0.35), canvas_z(hx + 0.9, hx) - 0.4),
               0.26, sides=5, mat=T, end_mat=T)


def side_wall(a, hx, hy, sx, low=None, missing=(), lean=None):
    xc = sx * (hx - 0.25)
    span = 2 * hy - 1.2
    n = round(span / 1.05)
    w = span / n
    top = low if low else WALL_TOP
    for i in range(n):
        if i in missing:
            continue
        yc = -hy + 0.6 + w * (i + 0.5)
        if lean is not None and i == lean:
            a.plank((0.5, w - 0.05, top - FOOT_H - 0.6), (xc + sx * 0.6, yc, (top + FOOT_H) / 2 - 0.4),
                    rot=(0, sx * 0.22, 0.1), mat=T, bevel=0.05)
            continue
        a.plank((0.5, w - 0.05, top - FOOT_H), (xc, yc, (top + FOOT_H) / 2), mat=T, bevel=0.05)
    # top plate and a rail
    a.plank((0.8, 2 * hy + 0.6, 0.75), (sx * (hx - 0.3), 0, WALL_TOP + 0.3), mat=T, bevel=0.06)
    if not low:
        a.plank((0.35, 2 * hy - 1.3, 0.45), (sx * (hx + 0.12), 0, 2.9), mat=T, bevel=0.05)


def corner_posts(a, hx, hy):
    ptop = canvas_z(hx - 0.3, hx) + 0.55
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * (hx - 0.3), sy * (hy - 0.3)
            a.plank((1.1, 1.1, ptop - CB), (x, y, (ptop + CB) / 2), mat=T, bevel=0.07)
            a.plank((1.45, 1.45, 1.2), (x, y, ptop + 0.55), mat=T, bevel=0.1)


def ridge(a, hx, hy):
    rz = ridge_z(hx)
    a.beam((0, -hy - 0.9, rz - 0.3), (0, hy + 0.9, rz - 0.3), 0.32, sides=6, mat=T, end_mat=T)
    a.cyl(0.42, 0.34, 0.55, sides=8, loc=(0, -hy - 0.55, rz - 0.05), mat=S)
    a.plank((1.0, 1.0, 1.0), (0, hy + 0.55, rz + 0.25), mat=T, bevel=0.08)


def steps(a, hy, broken=False, x=0.0, w=5.4):
    y0 = -hy - 0.2
    if broken:
        a.plank((5.0, 1.1, 0.35), (0.3, y0 - 2.0, 0.25), rot=(0.12, 0.15, 0.05), mat=T)
        a.plank((2.4, 1.1, 0.3), (-1.2, y0 - 0.65, 0.85), mat=T)
        a.plank((2.2, 1.1, 0.3), (1.4, y0 - 0.9, 0.6), rot=(0.3, -0.1, 0.12), mat=T)
        a.plank((0.4, 2.2, 0.9), (-2.4, y0 - 1.2, 0.45), mat=T)
        return
    a.plank((w, 1.2, 0.55), (x, y0 - 1.95, 0.275), mat=T, bevel=0.06)
    a.plank((w, 1.2, 1.1), (x, y0 - 0.75, 0.55), mat=T, bevel=0.06)
    for sx in (-1, 1):
        a.plank((0.4, 2.4, 1.15), (x + sx * (w / 2 + 0.15), y0 - 1.35, 0.57), mat=T, bevel=0.05)


def interior(a, hx, hy, bench=False):
    a.box((2 * hx - 1.1, 2 * hy - 1.1, 0.25), (0, 0, FLOOR_Z - 0.125), mat=T)
    yi = hy - 0.55 - 0.5
    for zz in (4.4, 6.4):
        a.plank((min(6.0, 2 * hx - 2.5), 1.0, 0.22), (0.6, yi, zz), mat=T, bevel=0.04)
    for xx in (-2.0, 3.2):
        if abs(xx) < hx - 1:
            a.box((0.3, 0.9, 0.5), (xx, yi + 0.05, 4.05), mat=T)
    a.box((0.9, 0.8, 0.8), (-0.6, yi, 4.91), mat=T)
    a.box((0.8, 0.7, 0.7), (0.6, yi, 4.86), mat=T)
    a.box((0.6, 0.6, 0.6), (1.6, yi, 6.81), mat=T)
    if bench:
        a.plank((1.0, 4.5, 0.3), (hx - 2.0, 0, FLOOR_Z + 1.5), mat=T)
        for yy in (-1.8, 1.8):
            a.box((0.6, 0.3, 1.4), (hx - 2.0, yy, FLOOR_Z + 0.7), mat=T)


def dressing(a, spots, moss_spots):
    for (x, y, s) in spots:
        a.rock((s, s * 0.85, s * 0.65), (x, y, s * 0.3), mat=S, subdiv=1, facets=10, sink=0.0)
    for (x, y, r) in moss_spots:
        a.leaf_cluster(r, (x, y, r * 0.5), mat=M, lobes=6, squash=0.7, floor=0.0)


def lodge(a, hx=7.0, hy=6.0, mode="hero"):
    rng = a.rng
    rz = ridge_z(hx)
    footing(a, hx, hy, rng)
    interior(a, hx, hy)
    corner_posts(a, hx, hy)
    yf = -hy + 0.3
    if mode == "abandoned":
        gable_wall(a, hx, hy, -1, door=True, missing=(5, 7))
        gable_wall(a, hx, hy, 1, door=False, missing=(4,))
        side_wall(a, hx, hy, -1)
        side_wall(a, hx, hy, 1, missing=(6,), lean=7)
    else:
        gable_wall(a, hx, hy, -1, door=(mode != "open"), open_front=(mode == "open"))
        gable_wall(a, hx, hy, 1, door=False)
        side_wall(a, hx, hy, -1)
        side_wall(a, hx, hy, 1)
    if mode == "open":
        # open front: half wall + counter on the left/centre, walk-in gap on the right
        gx = 1.8
        span = gx - (-hx + 0.6)
        n = round(span / 1.1)
        w = span / n
        for i in range(n):
            xc = -hx + 0.6 + w * (i + 0.5)
            a.plank((w - 0.05, 0.5, 4.3 - FOOT_H), (xc, yf, (4.3 + FOOT_H) / 2), mat=T, bevel=0.05)
        a.plank((span + 0.5, 1.5, 0.3), (-hx + 0.6 + span / 2, yf - 0.35, 4.45), mat=T, bevel=0.05)
        for px in (-1.6, gx + 0.3):
            a.plank((0.7, 0.7, FLOOR_Z + DOOR_H - 1.6), (px, yf, (FLOOR_Z + DOOR_H + 1.6) / 2), mat=T, bevel=0.05)
        # bench in front of the counter
        a.plank((5.0, 1.0, 0.3), (-3.4, yf - 1.9, 2.0), mat=T, bevel=0.04)
        for bx in (-5.4, -1.4):
            a.box((0.35, 0.8, 1.85), (bx, yf - 1.9, 0.925), mat=T)
        # goods on the counter
        crate(a, (-4.6, yf - 0.2, 4.6), s=0.9)
        a.box((0.6, 0.5, 0.5), (-3.2, yf - 0.3, 4.85), mat=T)
        a.plank((hx - 0.6 - gx + 0.2, 1.0, 0.22), ((gx + hx - 0.6) / 2, yf - 0.1, FLOOR_Z - 0.05), mat=T)
        steps(a, hy, x=(gx + hx - 0.6) / 2, w=hx - 0.6 - gx)
    else:
        for sx in (-1, 1):
            a.plank((0.6, 0.85, DOOR_H), (sx * (DOOR_W / 2 + 0.3), yf - 0.05, FLOOR_Z + DOOR_H / 2), mat=T, bevel=0.06)
        a.plank((DOOR_W + 1.2, 1.0, 0.22), (0, yf - 0.1, FLOOR_Z - 0.05), mat=T)
        dv = door_local(a, faces=(-1, 1))
        if mode == "abandoned":
            a.transform(dv, (DOOR_W / 2 - 0.05, yf - 0.55, FLOOR_Z + 0.05), (0, 0.05, -math.radians(72)))
        else:
            # ajar ~22 deg outward on the right hinge: centred X-brace door, dark gap beside it
            a.transform(dv, (DOOR_W / 2 - 0.1, yf - 0.45, FLOOR_Z + 0.02), (0, 0, math.pi + math.radians(22)))
        steps(a, hy, broken=(mode == "abandoned"))
    ridge(a, hx, hy)
    if mode == "abandoned":
        for y in (-hy + 0.3, -hy / 2, 0, hy / 2, hy - 0.3):
            for sx in (-1, 1):
                a.beam((0, y, rz - 0.35), (sx * (hx - 0.1), y, canvas_z(hx - 0.1, hx) - 0.35), 0.2, sides=5,
                       mat=T, end_mat=T)
        roof(a, hx, hy, torn=(0.34, 0.24))
    else:
        roof(a, hx, hy)
    sock = None
    wy = 0.5
    wsx = 1      # reference cell A also shows the window on the +X wall
    wrot = -math.pi / 2 if wsx < 0 else math.pi / 2
    if mode != "abandoned":
        wv = window_local(a)
        place(a, wv, (wsx * hx, wy, 4.75), wrot)
        av = awning_local(a, out=1.35, z0=7.45)
        place(a, av, (wsx * hx, wy, 0), wrot)
    else:
        wv = window_local(a)
        place(a, wv, (hx, wy + 1.2, 5.2), math.pi / 2)
    if mode != "abandoned":
        lv = lantern_local(a, 5.5)
        lx = -1.6 if mode == "open" else -DOOR_W / 2 - 1.35
        ly = -hy - 0.05 if mode == "open" else -hy
        place(a, lv, (lx, ly, 0), 0)
        sock = (lx, ly - 0.95, 5.5)
    if mode == "hero":
        crate(a, (-hx + 0.6, -hy - 1.7, 0), s=1.9)
        crate(a, (-hx + 0.7, -hy - 1.6, 1.9), s=1.1)
        barrel(a, (-hx + 2.75, -hy - 2.3, 0))
        dressing(a, [(hx + 1.0, -hy - 0.7, 0.9), (hx + 1.3, -hy + 1.6, 0.55), (hx + 0.9, hy - 1.5, 0.7),
                     (-hx - 1.0, hy - 1.0, 0.8), (-hx - 1.0, -hy - 0.3, 0.6), (3.6, -hy - 2.4, 0.5)],
                 [(hx + 0.8, -hy + 3.2, 0.75), (hx + 0.9, hy - 3.0, 0.6), (-hx - 0.9, 1.5, 0.7),
                  (-hx - 2.6, -hy - 0.6, 0.6)])
    elif mode == "narrow":
        dressing(a, [(hx + 0.8, -hy - 0.6, 0.7), (-hx - 0.9, hy - 1.2, 0.6), (hx + 0.7, hy - 1.0, 0.55)],
                 [(-hx - 0.7, -hy + 1.4, 0.6), (hx + 0.8, -hy + 2.5, 0.55)])
    elif mode == "open":
        barrel(a, (hx + 1.4, hy - 1.2, 0))
        dressing(a, [(hx + 0.9, -hy - 0.7, 0.7), (-hx - 0.9, hy - 1.0, 0.6)],
                 [(-hx - 0.7, -hy + 1.5, 0.6), (hx + 0.8, 0.0, 0.55)])
    elif mode == "abandoned":
        ladder(a, (hx + 2.4, -hy + 2.2, 0), (hx + 0.5, -hy + 2.2, WALL_TOP + 0.6))
        dressing(a, [(hx + 1.1, -hy - 0.8, 0.8), (-2.8, -hy - 3.0, 0.6), (-hx - 0.8, hy - 0.8, 0.7)],
                 [(sx * (hx - 0.3) + sx * 0.5, sy * (hy - 0.3) + sy * 0.5, 0.6)
                  for sx in (-1, 1) for sy in (-1, 1)] + [(0.0, -hy - 0.1, 0.45)])
        for (x, y) in ((-5.5, -3.0), (6.0, 2.5), (-4.0, 4.0)):
            z = canvas_z(x, hx) - 0.1
            a.leaf_cluster(0.7, (x, y, z), mat=M, lobes=6, squash=0.45)
        for (x, y) in ((-5.0, -hy - 0.15), (4.6, -hy - 0.15)):
            pts = [(x, y, canvas_z(abs(x), hx) - 0.4), (x + 0.3, y - 0.05, 7.0), (x - 0.2, y, 5.0),
                   (x + 0.25, y - 0.05, 2.8), (x, y, 1.6)]
            a.tube_loop(pts, 0.14, mat=M, rseg=4, closed=False)
            a.leaf_cluster(0.4, (x + 0.2, y - 0.1, 6.2), mat=M, lobes=5, squash=0.7)
        pts = [(hx + 0.15, 3.5, WALL_TOP + 0.2), (hx + 0.2, 3.0, 7.0), (hx + 0.15, 3.6, 4.5), (hx + 0.2, 3.2, 2.0)]
        a.tube_loop(pts, 0.14, mat=M, rseg=4, closed=False)
    return sock


# ---------------------------------------------------------------- parts
def part_roof(fk):
    a = fk.Asset("GuardLodgeCanvasRoof", "W13 GuardLodge canvas roof")
    hx, hy = 7.0, 6.0
    rz = 7.3
    shift = rz - ridge_z(hx)
    start = len(a.bm.verts)
    roof(a, hx, hy)
    a.beam((0, -hy - 0.9, ridge_z(hx) - 0.3), (0, hy + 0.9, ridge_z(hx) - 0.3), 0.32, sides=6, mat=T, end_mat=T)
    for sy in (-1, 1):
        for sx in (-1, 1):
            a.beam((0, sy * (hy + 0.35), ridge_z(hx) - 0.3),
                   (sx * (hx + 0.9), sy * (hy + 0.35), canvas_z(hx + 0.9, hx) - 0.4), 0.26, sides=5, mat=T, end_mat=T)
    a.bm.verts.ensure_lookup_table()
    a.transform([a.bm.verts[i] for i in range(start, len(a.bm.verts))], (0, 0, shift))
    ez = canvas_z(hx - 0.3, hx) + shift
    for sx in (-1, 1):
        for sy in (-1, 1):
            a.plank((0.8, 0.8, ez + 0.4), (sx * (hx - 0.3), sy * (hy - 0.3), (ez + 0.4) / 2), mat=T)
    return a.finish()


def part_beam(fk):
    a = fk.Asset("GuardLodgeRoofBeam", "W13 GuardLodge roof beam")
    a.beam((-6.6, 0, 0.55), (6.6, 0, 0.55), 0.4, sides=7, mat=T, end_mat=T)
    for sx in (-1, 1):
        a.plank((1.1, 1.1, 1.1), (sx * 6.6, 0, 0.55), mat=T, bevel=0.1)
    for xx in (-3.0, 3.0):
        a.beam((xx, 0, 0.55), (xx + 0.9, 0, 0.55 + 0.3), 0.18, sides=5, mat=T, end_mat=T)
    return a.finish()


def part_wall_panel(fk):
    a = fk.Asset("GuardLodgeWallPanel", "W13 GuardLodge wall panel")
    for i in range(4):
        a.plank((0.97, 0.6, 7.6 + 0.2 * (i % 2)), (-1.5 + i, 0, 3.8 + 0.1 * (i % 2)), mat=T, bevel=0.05)
    a.plank((0.9, 0.9, 8.4), (-2.45, -0.1, 4.2), mat=T, bevel=0.07)
    a.plank((4.4, 0.4, 0.45), (0, -0.45, 6.2), mat=T)
    a.plank((4.0, 0.9, 0.22), (0, -0.75, 4.6), mat=T)
    a.plank((3.6, 1.3, 0.3), (0.1, -1.4, 2.4), mat=T)
    for xx in (-1.4, 1.6):
        a.box((0.3, 1.0, 2.25), (xx, -1.4, 1.125), mat=T)
    a.box((0.6, 0.6, 0.6), (1.0, -0.8, 5.01), mat=T)
    return a.finish()


def part_shelf(fk):
    a = fk.Asset("GuardLodgeInteriorShelf", "W13 GuardLodge interior shelf")
    a.plank((0.6, 0.6, 6.0), (-1.2, 0.4, 3.0), mat=T, bevel=0.05)
    a.plank((2.9, 1.6, 0.25), (0.1, 0.0, 2.4), mat=T)
    a.plank((2.9, 1.2, 0.22), (0.1, 0.2, 4.6), mat=T)
    a.box((0.25, 1.4, 2.4), (1.4, 0.0, 1.2), mat=T)
    crate(a, (-0.3, 0.0, 2.52), s=1.0)
    crate(a, (0.85, -0.05, 2.52), s=0.85)
    return a.finish()


def part_floor(fk):
    a = fk.Asset("GuardLodgeFloor", "W13 GuardLodge floor")
    for (x, y) in [(sx * 6.0, sy * 5.0) for sx in (-1, 0, 1) for sy in (-1, 1)]:
        a.stone_block((1.3, 1.3, 0.7), (x, y, 0.35), mat=S)
    n = 9
    for i in range(n):
        y = -6 + 12 / n * (i + 0.5)
        a.plank((14.0, 12 / n - 0.06, 0.3), (0, y, 0.85), mat=T, bevel=0.05)
    for yy in (-5.0, 5.0):
        a.box((13.4, 0.5, 0.4), (0, yy, 0.5), mat=T)
    return a.finish()


def part_rear_wall(fk):
    a = fk.Asset("GuardLodgeRearWall", "W13 GuardLodge rear wall")
    for i in range(3):
        a.plank((0.97, 0.6, 7.6), (-0.8 + i, 0, 3.8), mat=T, bevel=0.05)
    a.plank((1.0, 0.8, 8.0), (1.5, 0, 4.0), mat=T, bevel=0.07)
    a.plank((1.3, 1.3, 1.0), (1.5, 0, 8.5), mat=T, bevel=0.1)
    a.plank((3.6, 0.35, 0.45), (0.0, -0.4, 5.5), mat=T)
    return a.finish()


def part_side_wall(fk):
    a = fk.Asset("GuardLodgeSideWall", "W13 GuardLodge side wall")
    n = 11
    for i in range(n):
        a.plank((1.0, 0.6, 7.8), (-5.5 + 1.0 * i, 0, 3.9), mat=T, bevel=0.05)
    a.plank((0.9, 0.9, 8.4), (6.3, 0, 4.2), mat=T, bevel=0.07)
    a.plank((12.0, 0.8, 0.7), (0.3, 0, 8.0), mat=T)
    a.plank((11.0, 0.35, 0.45), (0.0, -0.45, 3.0), mat=T)
    return a.finish()


def part_doorframe(fk):
    a = fk.Asset("GuardLodgeDoorframe", "W13 GuardLodge doorframe")
    for sx in (-1, 1):
        a.plank((0.7, 1.0, 7.5), (sx * 2.4, 0, 3.75), mat=T, bevel=0.06)
    a.plank((5.5, 1.0, 1.0), (0, 0, 8.0), mat=T, bevel=0.07)
    a.plank((5.0, 1.0, 0.2), (0, 0, 0.1), mat=T)
    return a.finish()


def part_door(fk):
    a = fk.Asset("GuardLodgeDoor", "W13 GuardLodge door")
    door_local(a, h=7.5)
    return a.finish()


def part_awning(fk):
    a = fk.Asset("GuardLodgeWindowAwning", "W13 GuardLodge window awning")
    awning_local(a, w=3.5, out=1.8, z0=1.4)
    return a.finish()


def part_window(fk):
    a = fk.Asset("GuardLodgeWindow", "W13 GuardLodge window")
    window_local(a)
    a.box((2.6, 0.3, 2.6), (0, 0.12, 0), mat=T)
    return a.finish()


# ---------------------------------------------------------------- build
def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []
    specs = [
        ("GuardLodge", "hero", 7.0, "hero", "W13 GuardLodge"),
        ("GuardLodgeNarrow", "variant", 5.0, "narrow", "W13 GuardLodge narrow"),
        ("GuardLodgeOpenHut", "variant", 7.0, "open", "W13 GuardLodge open hut"),
        ("GuardLodgeAbandoned", "variant", 7.0, "abandoned", "W13 GuardLodge abandoned"),
    ]
    for name, role, hx, mode, cat in specs:
        a = fk.Asset(name, cat)
        sock = lodge(a, hx=hx, hy=6.0, mode=mode)
        off = bbox_off(a)
        o = a.finish()
        notes = "plank guard lodge, canvas roof, walkable doorway (precise collision)."
        if sock:
            vfx.add(o, "heat_glow", (sock[0] - off.x, sock[1] - off.y, sock[2] - off.z), scale=0.5,
                    color=["#FFB23A", "#FFB23A"])
            notes += " heat_glow socket = lantern glow beside the door (small warm orange)."
        else:
            notes += " no lantern / no VFX (abandoned)."
        out.append(kit.tag(o, role, collision="precise", budget=8000, notes=notes))
    parts = [
        (part_roof, "hull", "pitched canvas roof on ridge + rafters"),
        (part_beam, "box", "ridge beam with end caps"),
        (part_wall_panel, "box", "plank wall panel with rail, shelf and bench"),
        (part_shelf, "hull", "interior shelf with two small crates"),
        (part_floor, "precise", "plank floor on stone footing blocks"),
        (part_rear_wall, "box", "rear wall panel with corner post"),
        (part_side_wall, "box", "plank side wall with post"),
        (part_doorframe, "precise", "open door frame with lintel"),
        (part_door, "box", "plank door with X brace"),
        (part_awning, "hull", "canvas window awning with supports"),
        (part_window, "box", "window frame, glass panes and sill"),
    ]
    for fn, col, note in parts:
        out.append(kit.tag(fn(fk), "part", collision=col, budget=1500, notes=note))
    return out
