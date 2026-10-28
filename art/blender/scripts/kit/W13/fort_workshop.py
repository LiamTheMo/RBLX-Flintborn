"""W13 row 4: Fort Workshop (open canvas-roofed workshop shed) and its parts/variants."""
import math

import bmesh
from mathutils import Vector

SUBJECT = "FortWorkshop"
ROW = 4
HERO_AZIMUTH = -22
HERO_ELEVATION = 14  # a little lower than default so the camera sees under the canopy
SIDE_AZIMUTH = 60   # front-right three-quarter: shows the lit right half wall and open front

PALETTE = {
    "w13_timber": ("#A9612C", 0.85, 0, 0),
    "w13_canvas": ("#E6D2A4", 0.95, 0, 0),
    "w13_stone": ("#8A9199", 0.9, 0, 0),
    "w13_banner": ("#C3262A", 0.8, 0, 0),
    "w13_moss": ("#4C9A3C", 0.9, 0, 0),
    "w13_glass": ("#2E4256", 0.4, 0, 0),
    "w13_lantern_glow": ("#FFB23A", 0.4, 0, 1.5),
}

T, C, S, B, M, G, L = ("w13_timber", "w13_canvas", "w13_stone", "w13_banner", "w13_moss",
                       "w13_glass", "w13_lantern_glow")

# shed layout (studs)
PX, PY = 5.9, 4.9          # post centres
FLOOR_Z0, FLOOR_T = 0.5, 0.8
FZ = FLOOR_Z0 + FLOOR_T    # floor top 1.3
FOOT_H = 1.6
ZF, ZB, ZR = 9.7, 11.6, 13.8  # canvas height at front / back post line, ridge peak
LIGHT = {"color": "#FFB23A", "brightness": 1.0, "range": 10, "flicker": True}


# ---------------------------------------------------------------- helpers

def bx(a, size, loc, mat=T, rot=(0, 0, 0), bevel=0.05, jitter=0.0):
    """Box sitting on loc's z (bottom), centred in x/y."""
    return a.box(size, loc=(loc[0], loc[1], loc[2] + size[2] / 2), rot=rot, mat=mat,
                 bevel=bevel, jitter=jitter)


def rail(a, p1, p2, w, h, mat=T):
    """Square timber between two points that differ in (y, z) or (x, z)."""
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    mid = (p1 + p2) / 2
    if abs(d.x) > abs(d.y):
        ang = math.atan2(d.z, d.x)
        return a.box((d.length, w, h), loc=mid, rot=(0, -ang, 0), mat=mat, bevel=0.04)
    ang = math.atan2(d.z, d.y)
    return a.box((w, d.length, h), loc=mid, rot=(ang, 0, 0), mat=mat, bevel=0.04)


def finish(a):
    xs = [v.co.x for v in a.bm.verts]
    ys = [v.co.y for v in a.bm.verts]
    zs = [v.co.z for v in a.bm.verts]
    off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
    return a.finish(), off


def socket(vfx, o, off, p):
    vfx.add(o, "heat_glow", tuple(Vector(p) - off), scale=0.5, light=dict(LIGHT))


def canvas(a, cx=0.0, cy=0.0, hw=7.4, hd=6.4, zf=ZF, zb=ZB, pyf=-PY, pyb=PY, ridge=0.35,
           droop=0.7, lip=0.45, nx=8, ny=8, th=0.18, zr=None, tr=0.55, rings=4):
    """Hip-tent canvas: four sloped panels meeting at a peak (high toward the back),
    built as rings around the apex so the hip ridges run cleanly to the corners.
    The front hem sags between the front posts and a short hem hangs all round."""
    zr = zr if zr is not None else ZR
    bm = a.bm
    ay = pyf + tr * (pyb - pyf)
    apex = Vector((cx, ay, zr))
    x0, x1, y0, y1 = cx - hw, cx + hw, cy - hd, cy + hd

    def zfront(y):
        return zf + (zr - zf) * ((y - pyf) / (pyb - pyf)) / tr

    def zback(y):
        return zr - (zr - zb) * (((y - pyf) / (pyb - pyf)) - tr) / (1 - tr)

    zc_f, zc_b = zfront(y0) - 0.2, zback(y1) - 0.2      # corner heights

    def zside(y):
        return zc_f + (zc_b - zc_f) * (y - y0) / (y1 - y0)

    # perimeter, counter-clockwise from the front-left corner
    pts = []
    for i in range(nx):
        x = x0 + (x1 - x0) * i / nx
        u = (x - cx) / hw
        pts.append((x, y0, zc_f - droop * (1 - u * u), lip))
    for j in range(ny):
        y = y0 + (y1 - y0) * j / ny
        pts.append((x1, y, zside(y), lip * 0.8))
    for i in range(nx):
        x = x1 - (x1 - x0) * i / nx
        pts.append((x, y1, zc_b, lip * 0.8))
    for j in range(ny):
        y = y1 - (y1 - y0) * j / ny
        pts.append((x0, y, zside(y), lip * 0.8))
    n = len(pts)
    top = [[bm.verts.new(apex)]]
    for k in range(1, rings + 1):
        s = k / rings
        top.append([bm.verts.new(apex.lerp(Vector(p[:3]), s)) for p in pts])
    # hanging hem ring
    top.append([bm.verts.new((p[0] + (0.03 if p[0] >= x1 else -0.03 if p[0] <= x0 else 0),
                              p[1] + (0.03 if p[1] >= y1 else -0.03 if p[1] <= y0 else 0),
                              p[2] - p[3])) for p in pts])
    bot = [[bm.verts.new((v.co.x, v.co.y, v.co.z - th)) for v in ring] for ring in top]
    faces = []
    for (T_, rev) in ((top, False), (bot, True)):
        for i in range(n):
            f = (T_[0][0], T_[1][i], T_[1][(i + 1) % n])
            faces.append(bm.faces.new(f[::-1] if rev else f))
        for k in range(1, len(T_) - 1):
            for i in range(n):
                f = (T_[k][i], T_[k + 1][i], T_[k + 1][(i + 1) % n], T_[k][(i + 1) % n])
                faces.append(bm.faces.new(f[::-1] if rev else f))
    last = len(top) - 1
    for i in range(n):
        i2 = (i + 1) % n
        faces.append(bm.faces.new((top[last][i], bot[last][i], bot[last][i2], top[last][i2])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    verts = [v for ring in top + bot for v in ring]
    a._finish(verts, C)


def post(a, x, y, z0, h, w=1.3):
    bx(a, (w, w, h), (x, y, z0))
    bx(a, (w + 0.35, w + 0.35, 0.55), (x, y, z0 + h), bevel=0.07)


def footing(a, x, y, z0=0.0, size=(2.5, 2.5, 1.6)):
    a.stone_block(size, loc=(x, y, z0 + size[2] / 2), mat=S)


def floor(a, cx=0.0, cy=0.0, w=14.0, d=12.0, z0=0.0, t=0.8, n=7):
    pw = w / n
    for i in range(n):
        x = cx - w / 2 + pw * (i + 0.5)
        dz = a.rng.uniform(-0.04, 0.04)
        bx(a, (pw - 0.12, d, t + dz), (x, cy, z0), bevel=0.06)
    # edge boards across the planks
    for yy in (cy - d / 2 + 0.35, cy + d / 2 - 0.35):
        bx(a, (w, 0.7, 0.12), (cx, yy, z0 + t), bevel=0.03)


def half_wall(a, x0, x1, y0, y1, z0, h=3.5, n=4, th=0.5):
    """Plank panel from (x0,y0) to (x1,y1) (axis aligned), horizontal planks."""
    ph = (h - 0.3) / n
    along_x = abs(x1 - x0) > abs(y1 - y0)
    for k in range(n):
        z = z0 + k * ph + 0.02
        off = 0.06 if k % 2 else -0.06            # alternate boards step in/out so each reads
        tilt = 0.06 if k % 2 else -0.04
        if along_x:
            bx(a, (abs(x1 - x0), th, ph - 0.16), ((x0 + x1) / 2, y0 + off, z), rot=(tilt, 0, 0),
               bevel=0.07)
        else:
            bx(a, (th, abs(y1 - y0), ph - 0.16), (x0 + off, (y0 + y1) / 2, z), rot=(0, tilt, 0),
               bevel=0.07)
    zt = z0 + n * ph
    if along_x:
        bx(a, (abs(x1 - x0), th + 0.3, 0.32), ((x0 + x1) / 2, y0, zt), bevel=0.05)
    else:
        bx(a, (th + 0.3, abs(y1 - y0), 0.32), (x0, (y0 + y1) / 2, zt), bevel=0.05)


def lantern(a, x, y, z):
    """Hanging lantern, glass centre at z."""
    a.cyl(0.36, 0.36, 0.72, sides=6, loc=(x, y, z - 0.36), mat=L)
    a.cyl(0.48, 0.48, 0.14, sides=6, loc=(x, y, z - 0.5), mat=T)
    a.cyl(0.52, 0.12, 0.42, sides=6, loc=(x, y, z + 0.36), mat=T)
    for k in range(3):
        ang = k * 2 * math.pi / 3 + 0.5
        a.box((0.08, 0.08, 0.72), loc=(x + 0.37 * math.cos(ang), y + 0.37 * math.sin(ang), z), mat=T)
    a.torus(0.16, 0.04, loc=(x, y, z + 0.9), rot=(math.pi / 2, 0, 0), mat=T, seg=6, rseg=3)


def hook_arm(a, x, y, z, dy=-1.6):
    """Bracket arm out of a post face with a curved hook; returns lantern glass centre."""
    ey = y + dy
    bx(a, (0.36, abs(dy), 0.36), (x, y + dy / 2, z), bevel=0.03)
    rail(a, (x, y - 0.1, z - 1.0), (x, y + dy * 0.65, z + 0.05), 0.26, 0.26)   # knee brace
    a.tube_loop([(x, ey + 0.15, z), (x, ey - 0.05, z - 0.1), (x, ey - 0.1, z - 0.3),
                 (x, ey, z - 0.45)], 0.06, mat=T, rseg=4, closed=False)
    return (x, ey, z - 1.45)


def bench(a, x, y, z0, w=6.0, d=2.5, h=3.0, tools=True, lamp=True):
    top_t = 0.35
    bx(a, (w, d, top_t), (x, y, z0 + h - top_t), bevel=0.06)
    for sx in (-1, 1):
        for sy in (-1, 1):
            bx(a, (0.4, 0.4, h - top_t), (x + sx * (w / 2 - 0.35), y + sy * (d / 2 - 0.3), z0), bevel=0.03)
    bx(a, (w - 0.6, d - 0.5, 0.2), (x, y, z0 + 0.6), bevel=0.03)        # shelf
    bx(a, (w - 0.6, 0.25, 0.4), (x, y - d / 2 + 0.3, z0 + h - top_t - 0.4), bevel=0.02)  # apron
    zt = z0 + h
    if tools:
        # anvil-like block on a stump
        bx(a, (1.3, 0.9, 0.6), (x - 1.7, y + 0.1, zt), mat=S, bevel=0.05)
        bx(a, (1.9, 1.0, 0.45), (x - 1.7, y + 0.1, zt + 0.6), mat=S, bevel=0.05)
        a.poly_prism([(0, 0), (0.9, 0.15), (0.9, 0.28), (0, 0.45)], 0.8,
                     loc=(x - 0.75, y + 0.5, zt + 0.6), rot=(math.pi / 2, 0, 0), mat=S)
        # vise at the right end
        bx(a, (0.6, 0.6, 0.35), (x + 2.4, y - 0.7, zt), mat=S, bevel=0.03)
        bx(a, (0.25, 0.7, 0.5), (x + 2.2, y - 0.7, zt + 0.35), mat=S, bevel=0.02)
        bx(a, (0.25, 0.7, 0.5), (x + 2.6, y - 0.7, zt + 0.35), mat=S, bevel=0.02)
        bx(a, (0.9, 0.1, 0.1), (x + 2.4, y - 1.15, zt + 0.5), mat=S, bevel=0.0)
        # hammer and chisel
        bx(a, (1.2, 0.16, 0.16), (x + 0.2, y - 0.6, zt), rot=(0, 0, 0.3), bevel=0.0)
        bx(a, (0.22, 0.45, 0.24), (x + 0.75, y - 0.43, zt), mat=S, rot=(0, 0, 0.3), bevel=0.02)
        bx(a, (0.9, 0.12, 0.12), (x + 0.6, y + 0.4, zt), mat=S, rot=(0, 0, -0.4), bevel=0.0)
        # tongs / tools leaning on the back
        for k, tx in enumerate((x - 0.2, x + 0.4, x + 1.0)):
            bx(a, (0.12, 0.12, 1.3 + 0.2 * k), (tx, y + d / 2 - 0.25, zt), mat=S, bevel=0.0)
            bx(a, (0.36, 0.14, 0.3), (tx, y + d / 2 - 0.25, zt + 1.3 + 0.2 * k), mat=S, bevel=0.02)
    if lamp:
        lantern(a, x + 1.6, y + 0.4, zt + 0.5)


def tool_rack(a, x, y, z):
    """Board on the back wall with grey tools hanging from it."""
    bx(a, (4.6, 0.25, 0.5), (x, y, z + 1.6), bevel=0.03)
    for sx in (-2.15, 2.15):   # uprights standing on the half-wall cap
        bx(a, (0.3, 0.3, 2.1), (x + sx, y + 0.1, z), bevel=0.02)
    for k, tx in enumerate((-1.7, -0.9, -0.1, 0.7, 1.5)):
        ln = 1.4 + 0.25 * (k % 3)
        bx(a, (0.14, 0.14, ln), (x + tx, y - 0.25, z + 1.8 - ln), mat=S, bevel=0.0)
        bx(a, (0.5 if k % 2 else 0.3, 0.16, 0.36), (x + tx, y - 0.25, z + 1.8 - ln), mat=S, bevel=0.02)


def crate(a, x, y, z0, s=2.5, rot=0.0):
    a.box((s - 0.1, s - 0.1, s - 0.1), loc=(x, y, z0 + s / 2), rot=(0, 0, rot), mat=T, bevel=0.06)
    for zz in (0.25, s - 0.25):
        a.box((s + 0.06, s + 0.06, 0.3), loc=(x, y, z0 + zz), rot=(0, 0, rot), mat=T, bevel=0.03)
    for sx in (-1, 1):
        for sy in (-1, 1):
            c, sn = math.cos(rot), math.sin(rot)
            ox, oy = sx * (s / 2 - 0.1), sy * (s / 2 - 0.1)
            a.box((0.3, 0.3, s), loc=(x + ox * c - oy * sn, y + ox * sn + oy * c, z0 + s / 2),
                  rot=(0, 0, rot), mat=T, bevel=0.03)


def barrel(a, x, y, z0, r=1.1, h=2.8):
    a.cyl(r * 0.88, r, h / 2, sides=10, loc=(x, y, z0), mat=T)
    a.cyl(r, r * 0.88, h / 2, sides=10, loc=(x, y, z0 + h / 2), mat=T)
    for zz in (0.35, h - 0.55):
        rr = r * (0.93 if zz < h / 2 else 0.93) + 0.04
        a.cyl(rr, rr, 0.2, sides=10, loc=(x, y, z0 + zz), mat=T)


def sack(a, x, y, z0, r=0.8):
    a.ico((r, r * 0.85, r * 1.05), loc=(x, y, z0 + r * 0.95), mat=M, subdiv=1, jitter=0.06)
    a.cyl(0.25, 0.12, 0.35, sides=5, loc=(x, y, z0 + r * 1.85), mat=M)


def log_stack(a, x0, y0, z0, counts, r=0.45, length=2.4, axis="y"):
    """Rows of logs; counts per row bottom-up, centred on x0 (logs along `axis`)."""
    pitch = r * 2.05
    for row, n in enumerate(counts):
        z = z0 + r + row * r * 1.75
        for k in range(n):
            off = (k - (n - 1) / 2) * pitch + a.rng.uniform(-0.05, 0.05)
            rr = r * a.rng.uniform(0.9, 1.05)
            if axis == "y":
                a.beam((x0 + off, y0 - length / 2, z), (x0 + off, y0 + length / 2, z), rr, sides=7,
                       mat=T, end_mat=T)
            else:
                a.beam((x0 - length / 2, y0 + off, z), (x0 + length / 2, y0 + off, z), rr, sides=7,
                       mat=T, end_mat=T)


def log_rack(a, x, y, z0, w=4.0, d=3.0, h=3.5, counts=(4, 3, 3, 2)):
    for sx in (-1, 1):
        for sy in (-1, 1):
            bx(a, (0.35, 0.35, h), (x + sx * (w / 2 - 0.2), y + sy * (d / 2 - 0.2), z0), bevel=0.03)
        bx(a, (0.3, d, 0.3), (x + sx * (w / 2 - 0.2), y, z0 + 0.2), bevel=0.02)
        bx(a, (0.3, d, 0.3), (x + sx * (w / 2 - 0.2), y, z0 + h - 0.3), bevel=0.02)
    bx(a, (w, 0.3, 0.3), (x, y + d / 2 - 0.2, z0 + h - 0.3), bevel=0.02)
    log_stack(a, x, y, z0 + 0.35, counts, r=0.42, length=d - 0.2)


def banner(a, x, y, z_top, w=2.4, h=5.5):
    """Red hanging banner, front face toward -y at `y`; top rod at z_top."""
    a.cyl(0.12, 0.12, w + 0.6, sides=6, loc=(x - (w + 0.6) / 2, y - 0.1, z_top),
          rot=(0, math.pi / 2, 0), mat=T)
    tail = 0.9
    pts = [(-w / 2, 0), (-w / 2, -h + tail), (0, -h), (w / 2, -h + tail), (w / 2, 0)]
    # poly_prism local XY -> world X,Z ; extrusion local +Z -> world -Y
    a.poly_prism(pts, 0.14, loc=(x, y, z_top - 0.1), rot=(math.pi / 2, 0, 0), mat=B)
    zc = z_top - 0.1 - h * 0.48
    dw, dh = w * 0.36, h * 0.2
    a.poly_prism([(0, -dh), (dw, 0), (0, dh), (-dw, 0)], 0.06, loc=(x, y - 0.14, zc),
                 rot=(math.pi / 2, 0, 0), mat=C)
    a.poly_prism([(0, -dh * 0.62), (dw * 0.62, 0), (0, dh * 0.62), (-dw * 0.62, 0)], 0.06,
                 loc=(x, y - 0.2, zc), rot=(math.pi / 2, 0, 0), mat=B)
    a.poly_prism([(0, -dh * 0.25), (dw * 0.25, 0), (0, dh * 0.25), (-dw * 0.25, 0)], 0.06,
                 loc=(x, y - 0.26, zc), rot=(math.pi / 2, 0, 0), mat=C)
    bx(a, (w * 0.8, 0.06, 0.22), (x, y - 0.17, z_top - 0.1 - h * 0.14), mat=C, bevel=0.0)


def dressing(a, spots):
    """Rubble stones ('r') and leafy grass clumps ('g') at ground level."""
    for kind, x, y, s in spots:
        x, y = x * 0.9, max(y, -6.9)      # keep scatter tight to the deck (~15 x 13 bounds)
        if kind == "r":
            a.rock((s, s * 0.85, s * 0.6), loc=(x, y, 0), mat=S, subdiv=1, facets=10)
        else:
            a.leaf_cluster(s, loc=(x, y, 0), mat=M, lobes=6, squash=0.6, floor=0.0)


def shed(a, back_wall=True, side_wall=True, banner_at=(2.2,), front_banner=None,
         hook_left=True):
    """Common structure.  Returns the lantern glass centre."""
    floor(a, 0, 0, 14.0, 12.0, FLOOR_Z0, FLOOR_T)
    # under-floor sill stones
    for x in (-2.8, 2.8):
        for y in (-5.3, 5.3):
            a.stone_block((1.6, 1.0, FLOOR_Z0 + 0.05), loc=(x, y, (FLOOR_Z0 + 0.05) / 2), mat=S)
    # step plank entry
    bx(a, (6.0, 1.3, 0.35), (0, -6.6, 0.25), bevel=0.05)
    for sx in (-2.4, 2.4):
        bx(a, (0.6, 1.0, 0.3), (sx, -6.6, 0.0), mat=S, bevel=0.05)
    zat = None
    # footings + posts
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * PX, sy * PY
            footing(a, x, y)
            top = (ZF + 0.9) if sy < 0 else (ZB + 1.3)
            post(a, x, y, FOOT_H, top - FOOT_H)
    # beams under the canvas: front, back, side rails
    zfb, zbb = ZF - 0.55, ZB - 0.55
    bx(a, (2 * PX + 1.0, 0.8, 0.85), (0, -PY, zfb - 0.85), bevel=0.05)
    bx(a, (2 * PX + 1.0, 0.8, 0.85), (0, PY, zbb - 0.85), bevel=0.05)
    for sx in (-1, 1):
        rail(a, (sx * PX, -PY - 0.4, zfb - 0.42), (sx * PX, PY + 0.4, zbb - 0.42), 0.7, 0.75)
        # knee braces at the front posts
        rail(a, (sx * PX, -PY, zfb - 2.6), (sx * (PX - 1.8), -PY, zfb - 0.8), 0.4, 0.4)
    rail(a, (-PX, PY, zbb - 3.0), (-PX + 1.8, PY, zbb - 0.9), 0.4, 0.4)
    rail(a, (PX, PY, zbb - 3.0), (PX - 1.8, PY, zbb - 0.9), 0.4, 0.4)
    canvas(a, cy=0.1, hd=5.5, hw=6.8, droop=0.6, lip=0.2, ridge=0.2)
    # half walls
    if back_wall:
        half_wall(a, -PX + 0.65, PX - 0.65, PY, PY, FZ)
    if side_wall:
        half_wall(a, PX, PX, -PY + 0.65, PY - 0.65, FZ)
        bx(a, (0.8, 0.8, 3.8), (PX, 0.0, FZ), bevel=0.04)
    for bxp in banner_at:
        banner(a, bxp, PY - 0.45, ZB - 0.35)
    if front_banner is not None:
        banner(a, front_banner, -PY - 0.45, zfb - 0.95, w=2.0, h=4.6)
    hx = -PX if hook_left else PX
    lp = hook_arm(a, hx, -PY - 0.65, ZF - 0.3, dy=-1.1)
    lantern(a, *lp)
    return lp


# ---------------------------------------------------------------- assets

def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []
    note_l = "heat_glow socket (#FFB23A, 0.5) = lantern glow; lantern glass is emissive w13_lantern_glow"

    # ---- hero
    a = fk.Asset("FortWorkshop", "W13 FortWorkshop")
    lp = shed(a)
    bench(a, 0.4, 1.4, FZ)
    tool_rack(a, 0.4, PY - 0.55, FZ + 3.5)
    crate(a, -3.4, -2.6, FZ, 2.3, rot=0.1)
    sack(a, -3.4, -2.6, FZ + 2.3, 0.8)
    barrel(a, -4.5, 0.6, FZ, 0.85, 2.2)
    log_stack(a, -4.0, 3.6, FZ, (2, 1), r=0.45, length=2.4)
    crate(a, 4.4, -2.6, FZ, 1.4, rot=-0.15)
    dressing(a, [("r", -7.6, -6.4, 0.9), ("r", 7.4, -6.2, 0.7), ("r", -2.8, -7.4, 0.6),
                 ("g", -8.0, -4.8, 0.9), ("g", 6.2, -7.2, 0.8), ("g", -7.8, 3.0, 0.8)])
    o, off = finish(a)
    socket(vfx, o, off, lp)
    out.append(kit.tag(o, "hero", collision="precise", budget=8000,
                       notes="Walkable open-front workshop deck. " + note_l))

    # ---- parts
    a = fk.Asset("WorkshopCanvasRoof", "W13 FortWorkshop")
    canvas(a, hw=8.0, hd=7.0, zf=1.0, zb=2.6, zr=4.0, pyf=-5.5, pyb=5.5)
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500, notes="Slanted canvas canopy"))

    a = fk.Asset("WorkshopRoofBeam", "W13 FortWorkshop")
    bx(a, (14.0, 0.8, 0.85), (0, 0, 0.18), bevel=0.05)
    for sx in (-1, 1):
        bx(a, (1.2, 1.2, 1.2), (sx * 6.6, 0, 0), bevel=0.08)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="Roof beam"))

    a = fk.Asset("WorkshopPost", "W13 FortWorkshop")
    post(a, 0, 0, 0, 10.45)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="Post with cap"))

    a = fk.Asset("WorkshopHalfWall", "W13 FortWorkshop")
    half_wall(a, -2.5, 2.1, 0, 0, 0, h=3.5, th=0.6)
    bx(a, (0.8, 0.8, 3.8), (2.3, 0, 0), bevel=0.04)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="Half wall panel"))

    a = fk.Asset("WorkshopFloor", "W13 FortWorkshop")
    floor(a, 0, 0, 14.0, 12.0, 0.0, 0.8)
    out.append(kit.tag(a.finish(), "part", collision="precise", budget=1500, notes="Walkable plank floor"))

    a = fk.Asset("WorkshopBanner", "W13 FortWorkshop")
    banner(a, 0, 0, 5.6)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500, notes="Red banner"))

    a = fk.Asset("WorkshopLanternHook", "W13 FortWorkshop")
    bx(a, (0.8, 0.8, 8.6), (0, 0, 0), bevel=0.04)
    bx(a, (1.0, 1.0, 0.4), (0, 0, 8.6), bevel=0.05)
    lp = hook_arm(a, 0, -0.4, 8.2, dy=-1.4)
    lantern(a, *lp)
    o, off = finish(a)
    socket(vfx, o, off, lp)
    out.append(kit.tag(o, "part", collision="hull", budget=1500, notes="Hook post. " + note_l))

    a = fk.Asset("WorkshopWorkTable", "W13 FortWorkshop")
    bench(a, 0, 0, 0)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="Work table with tools"))

    a = fk.Asset("WorkshopLogRack", "W13 FortWorkshop")
    log_rack(a, 0, 0, 0)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="Log rack"))

    a = fk.Asset("WorkshopCrateBarrel", "W13 FortWorkshop")
    crate(a, -1.3, 0, 0, 2.5)
    barrel(a, 1.45, 0, 0, 1.1, 2.8)
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500, notes="Crate and barrel"))

    a = fk.Asset("WorkshopBaseStone", "W13 FortWorkshop")
    footing(a, 0, 0)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="Post footing stone"))

    # ---- A. Carpenter Bay
    a = fk.Asset("WorkshopCarpenterBay", "W13 FortWorkshop")
    lp = shed(a, banner_at=())
    bench(a, 0.0, PY - 1.75, FZ, tools=False, lamp=False)
    zt = FZ + 3.0
    for k in range(3):   # boards lying on the bench
        bx(a, (4.6, 1.0, 0.2), (-0.8, PY - 2.2 + 0.25 * k, zt + 0.2 * k), rot=(0, 0, 0.06 * k), bevel=0.02)
    # big upright saw on the bench: grey blade with a timber handle, facing front
    a.poly_prism([(0, 0), (3.0, 0.0), (3.0, 0.5), (0, 1.3)], 0.12, loc=(0.6, PY - 1.6, zt + 0.05),
                 rot=(math.pi / 2, 0, 0), mat=S)
    bx(a, (0.9, 0.35, 1.1), (3.85, PY - 1.66, zt + 0.05), bevel=0.04)
    # boards leaning against the back half wall
    for k, lx in enumerate((-4.6, -3.9, -3.2, 3.4, 4.1)):
        bx(a, (0.6, 0.22, 5.2 + 0.3 * (k % 2)), (lx, PY - 0.75, FZ), rot=(-0.12, 0, 0.04 * k - 0.08),
           bevel=0.03)
    # sawhorse front-centre with a long plank across it
    sx0, sy0 = 1.6, -3.0
    bx(a, (3.4, 0.55, 0.5), (sx0, sy0, FZ + 2.2), bevel=0.04)
    for ex in (-1.3, 1.3):
        for ey in (-1, 1):
            rail(a, (sx0 + ex, sy0 + ey * 0.9, FZ), (sx0 + ex, sy0, FZ + 2.25), 0.3, 0.3)
    bx(a, (5.0, 1.1, 0.22), (sx0 + 0.3, sy0, FZ + 2.7), rot=(0, 0, 0.12), bevel=0.02)
    # stacked lumber at the left front (boards along x, crosswise layers)
    for k in range(7):
        bx(a, (3.6, 2.2, 0.32), (-4.0 + (k % 2) * 0.12, -3.4, FZ + k * 0.34), rot=(0, 0, 0.04 * (k % 3)),
           bevel=0.05)
    dressing(a, [("r", -7.6, -6.4, 0.9), ("r", 7.3, -6.3, 0.7),
                 ("g", -8.0, -4.6, 0.9), ("g", 6.4, -7.2, 0.8)])
    o, off = finish(a)
    socket(vfx, o, off, lp)
    out.append(kit.tag(o, "variant", collision="precise", budget=8000,
                       notes="Carpenter bay: saw bench, sawhorse, lumber, no banner. " + note_l))

    # ---- B. Storage Shed
    a = fk.Asset("WorkshopStorageShed", "W13 FortWorkshop")
    lp = shed(a, banner_at=())
    # big wall of log ends filling the back of the bay (ends face the front)
    log_stack(a, -0.4, 1.2, FZ, (8, 7, 7, 6, 4), r=0.6, length=5.4)
    # side rack stacked full on the right, ends facing front
    log_rack(a, 3.9, -2.4, FZ, w=3.0, d=3.0, h=4.0, counts=(3, 3, 2, 2))
    # loose log pile at the left front
    log_stack(a, -4.4, -2.6, FZ, (3, 2), r=0.5, length=2.6)
    barrel(a, -1.6, -3.6, FZ, 0.75, 1.9)
    dressing(a, [("r", -7.6, -6.4, 0.9), ("r", 7.4, -6.2, 0.7),
                 ("g", -8.0, -4.6, 0.9), ("g", 6.2, -7.2, 0.8)])
    o, off = finish(a)
    socket(vfx, o, off, lp)
    out.append(kit.tag(o, "variant", collision="precise", budget=8000,
                       notes="Storage shed: log stacks and racks. " + note_l))

    # ---- C. Trader Bay
    a = fk.Asset("WorkshopTraderBay", "W13 FortWorkshop")
    lp = shed(a, banner_at=(), front_banner=-PX + 1.7, hook_left=False)
    bench(a, 0.6, -2.6, FZ, w=6.5, d=2.0, h=3.0, tools=False, lamp=False)
    zt = FZ + 3.0
    crate(a, -1.6, -2.5, zt, 0.9, rot=0.2)
    crate(a, -0.4, -2.7, zt, 0.7, rot=-0.1)
    bx(a, (1.0, 0.7, 0.6), (1.0, -2.6, zt), bevel=0.05)
    a.cyl(0.3, 0.3, 0.6, sides=6, loc=(2.0, -2.4, zt), mat=S)
    a.cyl(0.22, 0.22, 0.8, sides=6, loc=(2.6, -2.8, zt), mat=G)
    sack(a, 3.1, -2.3, zt, 0.55)
    crate(a, 4.2, 3.2, FZ, 2.0, rot=0.1)
    crate(a, 1.0, 3.6, FZ, 1.6, rot=-0.1)
    sack(a, -3.6, 3.4, FZ, 0.9)
    barrel(a, -1.4, 3.6, FZ, 0.8, 2.0)
    dressing(a, [("r", -7.6, -6.4, 0.9), ("r", 7.4, -6.2, 0.7),
                 ("g", -8.0, -4.6, 0.9), ("g", 6.2, -7.2, 0.8)])
    o, off = finish(a)
    socket(vfx, o, off, lp)
    out.append(kit.tag(o, "variant", collision="precise", budget=8000,
                       notes="Trader bay: counter with goods, front-left banner. " + note_l))
    return out
