"""Build the Flintborn lobby map from the asset libraries.

    "D:/Steam/steamapps/common/Blender/blender.exe" --background --factory-startup \
        --python art/blender/scripts/build_lobby.py

Every prop is a *linked* instance: the libraries in art/blender/assets are linked
with relative paths and each placed object is a new local object that shares the
library mesh, so rebuilding a sheet updates the lobby on the next file load. The
ground (plateau, plaza, paths, stepping stones, river water, apron, rug, rail
fence) is built here with flintkit.Asset and is not marked as an asset.

Layout follows art/reference/lobby_map.png (it wins over LAYOUT.md where they
differ): the camera and the palisade oval were solved against the master's wall
outline, and plan_layout() puts every zone where the master shows it by projecting its
frame position (MASTER, % of the frame) back into the scene (fit_on_frame).

Every render runs the overlay check: each zone anchor is projected with
world_to_camera_view and printed next to its master target, and a 50/50 blend of the
render and the master is written (--overlay PATH, default renders/lobby_overlay.png).
Other flags: --audit DIR (mesh-overlap and NPC-clearance audits plus close-ups),
--no-audit-renders, --closeups DIR (wall, market and totem close-ups), --no-render.
Origin = the bonfire. +Y = north (Deploy gate), +X = east. 1 unit = 1 stud.
"""

import json
import math
import os
import random
import sys
import time

import bmesh
import bpy
import numpy as np
from mathutils import Euler, Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # art/blender
sys.path.insert(0, os.path.join(ROOT, "lib"))
import flintkit as fk  # noqa: E402

try:
    import vfx  # noqa: E402
except Exception as exc:  # another agent may be mid-edit
    print("vfx import failed:", exc)
    vfx = None

ASSET_DIR = os.path.join(ROOT, "assets")
OUT_BLEND = os.path.join(ROOT, "lobby", "FlintbornLobby.blend")
RENDER_DIR = os.path.join(ROOT, "renders")
LIBS = ["01_buildings.blend", "02_fences_towers.blend", "03_furnishings.blend",
        "04_weapons_tools.blend", "05_trees_plants.blend", "06_rocks_runes_camp.blend",
        "07_terrain_kit.blend"]

SEED = 1729
RNG = random.Random(SEED)
RES = (1672, 941)

# Layout scale: the whole camp (palisade oval, plateau rim, zone positions, paths, camera
# distance) is spread out by this factor for more room between buildings. Building and
# prop sizes do not change. Every hard-coded layout coordinate below is written in the
# original (reference-solved) units and multiplied by LS.
LS = 1.2

# Camera at the master's ~38 degree pitch (building fronts read, not just roofs), with
# distance and the palisade oval solved together against the master's wall outline (gate
# base, NW fence behind the totem, SW/SE stretches, south entrance posts, W/E extremes)
# and the bonfire at 44% down. The wall half-width keeps the expanded camp's 86 studs.
CAM = dict(loc=(0.0, -227.39 * LS, 171.01 * LS), pitch_deg=38.0, lens=66.0)

# Palisade oval: superellipse |x/rx|^n + |(y-cy)/ry|^n = 1 (fitted to the master outline;
# the squarer n gives the corners more room)
WALL = dict(rx=71.83 * LS, ry=47.42 * LS, cy=-10.52 * LS, n=3.37)
# Plateau rim (cliff lip)
RIM = dict(rx=100.0 * LS, ry=95.0 * LS, cy=16.0 * LS, n=2.5)
LOW_Z = -16.0          # lower ground beyond the cliffs
WALL_S = 1.25          # gate scale (reference gate is chunky)
PLAZA_R = 16.5 * LS   # dirt ring ~3 studs past the bench circle; the grass islands start there

# ---------------------------------------------------------------------------
# Small maths helpers
# ---------------------------------------------------------------------------


def smoothstep(e0, e1, x):
    t = min(max((x - e0) / (e1 - e0), 0.0), 1.0)
    return t * t * (3 - 2 * t)


_NG = random.Random(SEED + 1)
_NOISE = [[_NG.random() for _ in range(256)] for _ in range(256)]


def vn(x, y):
    """Smooth value noise in [0, 1]."""
    xi, yi = math.floor(x), math.floor(y)
    fx, fy = x - xi, y - yi
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a = _NOISE[yi % 256][xi % 256]
    b = _NOISE[yi % 256][(xi + 1) % 256]
    c = _NOISE[(yi + 1) % 256][xi % 256]
    d = _NOISE[(yi + 1) % 256][(xi + 1) % 256]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def se_F(x, y, p, scale=1.0):
    return (abs(x) / (p["rx"] * scale)) ** p["n"] + (abs(y - p["cy"]) / (p["ry"] * scale)) ** p["n"]


def seg_dist(poly, x, y):
    best = 1e9
    for (ax, ay), (bx, by) in zip(poly, poly[1:]):
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / L2))
        px, py = ax + t * dx - x, ay + t * dy - y
        best = min(best, px * px + py * py)
    return math.sqrt(best)


def chaikin(pts, it=2):
    for _ in range(it):
        out = [pts[0]]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            out += [(0.75 * ax + 0.25 * bx, 0.75 * ay + 0.25 * by), (0.25 * ax + 0.75 * bx, 0.25 * ay + 0.75 * by)]
        out.append(pts[-1])
        pts = out
    return pts


class Curve:
    """Polyline with arc-length lookup."""

    def __init__(self, pts, closed=False):
        self.pts = [Vector((p[0], p[1])) for p in pts]
        if closed:
            self.pts.append(self.pts[0].copy())
        self.closed = closed
        self.cum = [0.0]
        for a, b in zip(self.pts, self.pts[1:]):
            self.cum.append(self.cum[-1] + (b - a).length)
        self.length = self.cum[-1]

    def at(self, s):
        if self.closed:
            s %= self.length
        s = min(max(s, 0.0), self.length)
        lo, hi = 0, len(self.cum) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if self.cum[mid] <= s:
                lo = mid
            else:
                hi = mid
        seg = self.cum[hi] - self.cum[lo]
        t = 0.0 if seg == 0 else (s - self.cum[lo]) / seg
        return self.pts[lo].lerp(self.pts[hi], t)

    def tangent(self, s, ds=0.5):
        d = self.at(s + ds) - self.at(s - ds)
        return d.normalized()


def se_curve(p, N=3000, scale=1.0):
    pts = []
    for k in range(N):
        t = 2 * math.pi * k / N
        c, s = math.cos(t), math.sin(t)
        pts.append((p["rx"] * scale * math.copysign(abs(c) ** (2 / p["n"]), c),
                    p["cy"] + p["ry"] * scale * math.copysign(abs(s) ** (2 / p["n"]), s)))
    return Curve(pts, closed=True)


def project(x, y, z):
    """Pixel position of a world point in the LobbyCam render."""
    p = math.radians(CAM["pitch_deg"])
    vx, vy, vz = x - CAM["loc"][0], y - CAM["loc"][1], z - CAM["loc"][2]
    depth = vy * math.cos(p) - vz * math.sin(p)
    up = vy * math.sin(p) + vz * math.cos(p)
    k = CAM["lens"] / 36 * RES[0]
    return RES[0] / 2 + k * vx / depth, RES[1] / 2 - k * up / depth


def unproject(u, v, z=0.0):
    """World (x, y) on the plane `z` that the LobbyCam shows at frame (u %, v %) from the
    top-left. Zones are placed with this from the master's frame positions."""
    p = math.radians(CAM["pitch_deg"])
    k = CAM["lens"] / 36 * RES[0]
    px = (u / 100 * RES[0] - RES[0] / 2) / k
    py = (RES[1] / 2 - v / 100 * RES[1]) / k
    d = (px, math.cos(p) + py * math.sin(p), -math.sin(p) + py * math.cos(p))
    t = (z - CAM["loc"][2]) / d[2]
    return CAM["loc"][0] + t * d[0], CAM["loc"][1] + t * d[1]


def hides_camp(x, y, height):
    """True if a tree here would cover the south wall in the LobbyCam view."""
    if y > WALL["cy"] + 5:
        return False
    xc = max(-WALL["rx"] + 0.5, min(WALL["rx"] - 0.5, x))
    yw = WALL["cy"] - WALL["ry"] * (1 - (abs(xc) / WALL["rx"]) ** WALL["n"]) ** (1 / WALL["n"])
    if y > yw:  # beside the wall rather than in front of it
        return False
    top_v = project(x, y, height)[1]
    base_v = project(xc, yw, 0)[1]
    margin = 25 if abs(x) < 18 else (70 if abs(x) < 45 else 95)
    return top_v < base_v - margin


def face_to(x, y, tx, ty):
    """Z rotation that turns an asset's front (-Y) from (x, y) toward (tx, ty)."""
    return math.atan2(ty - y, tx - x) + math.pi / 2


def local(cx, cy, rot, lx, ly):
    c, s = math.cos(rot), math.sin(rot)
    return cx + c * lx - s * ly, cy + s * lx + c * ly


# ---------------------------------------------------------------------------
# Ground height
# ---------------------------------------------------------------------------

# The river spills over a waterfall in the cliff ridge behind the forge (top-right of
# the view), runs across the plateau's NE corner under a footbridge and drops off the
# east rim through a second waterfall.
UWF_POS = (79.0 * LS, 58.0 * LS)
UWF_ROT = math.atan2(-60 - 58.0, 20 - 79.0) + math.pi / 2       # face the camera side (SW)
UWF_FRONT = (math.sin(UWF_ROT), -math.cos(UWF_ROT))
UWF_POOL = (UWF_POS[0] + UWF_FRONT[0] * 8.5, UWF_POS[1] + UWF_FRONT[1] * 8.5)
RIVER_MID = [(80 * LS, 46 * LS), (88 * LS, 36 * LS), (101 * LS, 25 * LS)]  # last point on the rim
RIVER_PTS = chaikin([UWF_POOL] + RIVER_MID, 2)
RIVER = Curve(RIVER_PTS)
RIVER_W = 4.5
RIVER_Z = -2.1   # bank tiles (top 3, water 0.9) then meet the plateau grass flush


def init_river():
    """Put the pool (and so the river's start) where the WaterfallCliff tile's pool really is."""
    global UWF_POOL, RIVER_PTS, RIVER
    info = tile_info("WaterfallCliff")
    if "pool" in info:
        UWF_POOL = local(UWF_POS[0], UWF_POS[1], UWF_ROT, *info["pool"])
    RIVER_PTS = chaikin([UWF_POOL] + RIVER_MID, 2)
    RIVER = Curve(RIVER_PTS)


def h(x, y):
    """Plateau ground height."""
    r = math.hypot(x, y)
    amp = 0.25 + 0.35 * smoothstep(20 * LS, 45 * LS, r)
    v = amp * (vn(x / 20 + 3.1, y / 20 + 7.7) - 0.5) * 2 + 0.12 * (vn(x / 6 + 40, y / 6 + 11) - 0.5)
    if x > 55 * LS and y > 15 * LS:
        d = seg_dist(RIVER_PTS, x, y)
        if d < 10:
            v = min(v, (RIVER_Z - 0.8) * smoothstep(6.5, 4.0, d))
        dp = math.hypot(x - UWF_POOL[0], y - UWF_POOL[1])
        if dp < 12:
            v = min(v, (RIVER_Z - 0.6) * (1 - smoothstep(8, 12, dp)))
    return v


WF = {}  # waterfall placement, filled in terrain()
LOW_RIVER = []


def h_low(x, y):
    v = LOW_Z
    if WF:
        d = math.hypot(x - WF["x"], y - WF["y"])
        if d < 24:
            v = min(v, LOW_Z - 3.0 + 3.0 * smoothstep(14, 24, d))
    if LOW_RIVER:
        d = seg_dist(LOW_RIVER, x, y)
        if d < 12:
            v = min(v, LOW_Z - 3.5 + 3.5 * smoothstep(5, 12, d))
    return v


# ---------------------------------------------------------------------------
# Dirt layout (signed distance: < 0 is dirt)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# West side layout: Elder's totem, quest board and market (shared by the paths below)
# ---------------------------------------------------------------------------

CAM_XY = (CAM["loc"][0], CAM["loc"][1])


def face_view(x, y, w_plaza=0.2):
    """Yaw that turns an asset's front (-Y) toward the main camera, swung `w_plaza` of the
    way toward the plaza centre. The reference shows the totem, the rune stelae and the
    quest board square to the viewer and only slightly turned to the plaza; facing the
    bonfire outright would show them ~55 degrees side-on in the main view."""
    a_cam = face_to(x, y, *CAM_XY)
    d = (face_to(x, y, 0.0, 0.0) - a_cam + math.pi) % (2 * math.pi) - math.pi
    return a_cam + w_plaza * d


# Master frame targets in % of the frame from the top-left, read off art/reference/lobby_map.png.
# A point target is (u, v); a box target (u0, u1, v0, v1) is compared with the projected
# extent of the object's mesh. Zones are placed so their anchor lands on these (fit_on_frame),
# and the overlay check (measure_anchors) reports how close each one ends up.
MASTER = {
    "Totem base": (21.5, 28.0), "Totem top": (21.5, 8.8),
    "Rune stone L": (16.0, 28.0), "Rune stone R": (26.0, 22.0),
    "Brazier": (24.5, 24.0), "Quest board": (33.5, 23.0), "Elder": (29.5, 29.0),
    "Stall thatch": (18.0, 42.0), "Stall banner": (11.0, 50.0), "Stall red": (24.0, 45.5),
    "Stall tan": (19.0, 63.0), "Market label": (22.0, 56.0),
    "Watch platform": (4.5, 39.0), "SW watchtower": (9.5, 73.0),
    "Bonfire": (50.0, 44.0), "Arrival stones": (50.0, 77.8), "South entrance": (50.0, 90.5),
    "Deploy gate": (44.0, 57.0, 0.0, 22.0), "Forge": (62.0, 98.0, 0.0, 38.0),
    "Vault": (66.0, 96.0, 42.0, 72.0),
}
FRAME_EXTRA = {  # placement targets that are not reported zones
    "Brazier L": (19.0, 30.8), "Brazier R": (24.2, 24.6), "Elder tree": (10.5, 21.0), "Market barrels": (31.5, 49.5),
    "Market table": (32.5, 60.0),
}

TOTEM = dict(x=-44.2 * LS, y=16.3 * LS, s=1.95)  # refitted in plan_layout(); s: the master's totem rises to ~9%
TOTEM["rot"] = face_view(TOTEM["x"], TOTEM["y"])
QUEST = dict(x=-21.5 * LS, y=23.0 * LS, s=1.85)
QUEST["rot"] = face_view(QUEST["x"], QUEST["y"])


def totem_local(lx, ly):
    return local(TOTEM["x"], TOTEM["y"], TOTEM["rot"], lx, ly)


def quest_local(lx, ly):
    return local(QUEST["x"], QUEST["y"], QUEST["rot"], lx, ly)


# Market: a tight cluster of four stalls round a small market square against the W wall,
# each stall on its master frame position (fit_on_frame), turned toward the square (and
# partly to the camera so the counters read). plan_layout() then pushes stalls apart until
# every pair has a 6+ stud gap; in front of every counter is a clear 7.5-stud customer
# lane, and the merchant stands inside the stall behind the counter.
# (asset, scale, master role, how far the front turns from the square toward the camera)
# (the canopy stalls turn most of the way to the camera so their pennant fringe reads)
MARKET_STALLS = [("ThatchMarketStall", 1.05, "thatch", 0.4), ("HideMarketStall", 1.15, "banner", 0.75),
                 ("HideMarketStall", 0.85, "red", 0.8), ("HideMarketStall", 0.85, "tan", 1.0)]
MARKET_ROLES = tuple(r for _, _, r, _ in MARKET_STALLS)   # which master stall each one stands for
MARKET_LANE = 7.5
MARKET_GAP = 6.0
MARKET_LABEL = None   # ground point under the master's "Market" label: the market square
STALLS = []           # (asset, x, y, rot, scale, front, half width, half depth), set in plan_layout
# merchant spot inside each stall, unscaled stall-local (x, y): clear of shelves and posts
MERCHANT_SPOT = {"ThatchMarketStall": (-2.0, 2.6), "HideMarketStall": (1.0, 2.2)}


def merchant_spot(stall, nm, ss):
    """Unscaled stall-local merchant spot: MERCHANT_SPOT, or the nearest point behind the
    counter where the NPC cylinder clears the (scaled) stall mesh exactly."""
    bvh, verts = world_bvh(stall, 0.0)
    bx, by = MERCHANT_SPOT[nm]
    cands = sorted(((bx + dx * 0.25, by + dy * 0.25) for dx in range(-12, 13) for dy in range(-4, 13)),
                   key=lambda p: math.hypot(p[0] - bx, p[1] - by))
    for lx, ly in cands:
        wx, wy = local(stall.location.x, stall.location.y, stall.rotation_euler.z, lx * ss, ly * ss)
        z = stall.location.z + floor_z(nm, lx, ly, top=2.0) * ss
        cyl = _cylinder_bvh(wx, wy, z + 0.3, z + NPC_H, NPC_R)
        if cyl.overlap(bvh):
            continue
        if any((v.x - wx) ** 2 + (v.y - wy) ** 2 < NPC_R ** 2 and z + 0.3 < v.z < z + NPC_H for v in verts):
            continue
        return lx, ly
    return bx, by
_STALL_BB = {"ThatchMarketStall": (6.72, 4.37), "HideMarketStall": (6.91, 3.75)}  # half width, half depth


def market_stalls():
    """(asset, x, y, rot, scale, front, half width, half depth) of each stall."""
    return STALLS


def market_lanes():
    """One straight customer lane in front of each counter: its centre line, padded 1 stud
    past the stall ends."""
    out = []
    for nm, x, y, rot, ss, f, hw, hd in STALLS:
        ly = -(hd + MARKET_LANE / 2) + 0.5   # dirt runs right up under the counter
        out.append([local(x, y, rot, -hw - 1.0, ly), local(x, y, rot, hw + 1.0, ly)])
    return out


def in_lane(x, y, r):
    """True if a prop of radius r at (x, y) would stand in a customer lane."""
    return any(seg_dist(ln, x, y) - r < MARKET_LANE / 2 for ln in market_lanes())


def market_lane_poly():
    """Kept for the audit views: the lane of the first stall."""
    return market_lanes()[0]


def _S(pts):
    return [(x * LS, y * LS) for x, y in pts]


PATHS = []   # (polyline, width), filled by plan_paths() once the zones are placed
PADS = []    # (cx, cy, rx, ry, rot): dirt aprons in front of each building


def _pct(co):
    u, v = project(*co)
    return 100.0 * u / RES[0], 100.0 * v / RES[1]


_LOCAL_VERTS = {}


def _anchor_uv(asset, x, y, rot, sc, anchor, z=None):
    """Projected anchor (frame %) of an asset placed at (x, y) and its world height."""
    if asset not in _LOCAL_VERTS:
        _LOCAL_VERTS[asset] = [v.co.copy() for v in A[asset].data.vertices]
    zz = h(x, y) if z is None else z
    if anchor == "base":
        return _pct((x, y, zz)), zz
    M = Matrix.LocRotScale(Vector((x, y, zz)), Euler(rot), Vector(sc))
    lv = _LOCAL_VERTS[asset]
    if anchor == "roof":   # centre of the canopy / roof: the top 40% of the mesh
        top = max(v.z for v in lv)
        lv = [v for v in lv if v.z > 0.6 * top]
        anchor = "centre"
    vs = [M @ v for v in lv]
    if anchor == "centre":
        c = [(min(v[i] for v in vs) + max(v[i] for v in vs)) / 2 for i in range(3)]
        return _pct(c), c[2]
    uv = [_pct(v) for v in vs]   # "box": centre of the projected extent
    return (((min(u for u, _ in uv) + max(u for u, _ in uv)) / 2, (min(v for _, v in uv) + max(v for _, v in uv)) / 2),
            sum(v.z for v in vs) / len(vs))


def fit_on_frame(asset, target, sc, rot_fn, anchor="centre", z=None, it=6):
    """(x, y, euler) that puts the asset's anchor on frame target (u %, v %): start from the
    ground point under the target, then shift by the back-projected residual a few times."""
    sc = tuple(sc) if isinstance(sc, (tuple, list)) else (sc, sc, sc)
    x, y = unproject(*target, 0.0)
    for _ in range(it):
        rot = rot_fn(x, y)
        (u, v), za = _anchor_uv(asset, x, y, rot, sc, anchor, z)
        tx, ty = unproject(*target, za)
        mx, my = unproject(u, v, za)
        x, y = x + tx - mx, y + ty - my
    return x, y, rot_fn(x, y)


def _rect_pts(x, y, rot, hw, hd):
    return [local(x, y, rot, sx * hw, sy * hd) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def _rect_sep(a, b):
    """Signed separating-axis distance between two rotated rectangles (x, y, rot, hw, hd):
    > 0 a lower bound on the clear gap, < 0 the penetration depth (smooth for optimising)."""
    best = -1e9
    for r in (a, b):
        for ang in (r[2], r[2] + math.pi / 2):
            ax = (math.cos(ang), math.sin(ang))
            spans = []
            for x, y, rot, hw, hd in (a, b):
                c = x * ax[0] + y * ax[1]
                e = hw * abs(math.cos(rot - ang)) + hd * abs(math.sin(rot - ang))
                spans.append((c - e, c + e))
            best = max(best, max(spans[1][0] - spans[0][1], spans[0][0] - spans[1][1]))
    return best


def _rect_gap(a, b):
    """Clear distance between two rotated rectangles (x, y, rot, hw, hd); 0 if they overlap."""
    pa, pb = _rect_pts(*a), _rect_pts(*b)

    def inside(p, r):
        x, y, rot, hw, hd = r
        c, s = math.cos(-rot), math.sin(-rot)
        u, v = c * (p[0] - x) - s * (p[1] - y), s * (p[0] - x) + c * (p[1] - y)
        return abs(u) <= hw and abs(v) <= hd
    if any(inside(p, b) for p in pa) or any(inside(p, a) for p in pb):
        return 0.0
    d = min(seg_dist([pb[i], pb[(i + 1) % 4]], *p) for p in pa for i in range(4))
    return min(d, min(seg_dist([pa[i], pa[(i + 1) % 4]], *p) for p in pb for i in range(4)))


def _nelder(f, x0, step, iters):
    """Plain Nelder-Mead minimiser (no scipy in Blender's Python)."""
    n = len(x0)
    step = step if isinstance(step, (list, tuple)) else [step] * n
    pts = [list(x0)] + [[x0[j] + (step[i] if j == i else 0.0) for j in range(n)] for i in range(n)]
    vals = [f(q) for q in pts]
    for _ in range(iters):
        order = sorted(range(n + 1), key=lambda i: vals[i])
        pts, vals = [pts[i] for i in order], [vals[i] for i in order]
        c = [sum(q[i] for q in pts[:-1]) / n for i in range(n)]
        xr = [2 * c[i] - pts[-1][i] for i in range(n)]
        fr = f(xr)
        if fr < vals[0]:
            xe = [3 * c[i] - 2 * pts[-1][i] for i in range(n)]
            fe = f(xe)
            pts[-1], vals[-1] = (xe, fe) if fe < fr else (xr, fr)
        elif fr < vals[-2]:
            pts[-1], vals[-1] = xr, fr
        else:
            xc = [(c[i] + pts[-1][i]) / 2 for i in range(n)]
            fc = f(xc)
            if fc < vals[-1]:
                pts[-1], vals[-1] = xc, fc
            else:
                for j in range(1, n + 1):
                    pts[j] = [(pts[0][i] + pts[j][i]) / 2 for i in range(n)]
                    vals[j] = f(pts[j])
    return pts[min(range(n + 1), key=lambda i: vals[i])]


def plan_layout():
    """Place every zone on its master frame position (needs the libraries linked)."""
    global MARKET_LABEL
    gz = lambda x, y: (0.0, 0.0, face_view(x, y))  # noqa: E731
    # Elder's totem: base centre on the master's, square to the viewer
    x, y, r = fit_on_frame("EldersTotemTall", MASTER["Totem base"], TOTEM["s"], gz, anchor="base")
    TOTEM.update(x=x, y=y, rot=r[2])
    x, y, r = fit_on_frame("QuestBoard", MASTER["Quest board"], QUEST["s"], gz)
    QUEST.update(x=x, y=y, rot=r[2])
    # forge / vault: centre of the projected silhouette on the centre of the master's box
    for D, nm, key in ((FORGE, "AncestralForge", "Forge"), (VAULT, "VaultHall", "Vault")):
        t = MASTER[key]
        x, y, _ = fit_on_frame(nm, ((t[0] + t[1]) / 2, (t[2] + t[3]) / 2), D["s"],
                               lambda x_, y_, r_=D["rot"]: (0.0, 0.0, r_), anchor="box")
        D.update(x=x, y=y)
    ARRIVAL.update(zip(("x", "y"), unproject(*MASTER["Arrival stones"], 0.0)))
    # market square under the label, stalls round it
    MARKET_LABEL = unproject(*MASTER["Market label"], 0.0)
    lx, ly = MARKET_LABEL
    STALLS.clear()
    rot_fns, offs = [], []
    for nm, ss, role, w_cam in MARKET_STALLS:
        def rot_fn(x_, y_, w=w_cam):
            a_sq = face_to(x_, y_, lx, ly)
            d = (face_to(x_, y_, *CAM_XY) - a_sq + math.pi) % (2 * math.pi) - math.pi
            return a_sq + w * d
        x, y, r = fit_on_frame(nm, MASTER["Stall " + role], ss, lambda x_, y_, f_=rot_fn: (0.0, 0.0, f_(x_, y_)),
                               anchor="roof")
        hw, hd = _STALL_BB[nm][0] * ss, _STALL_BB[nm][1] * ss
        # roof centre relative to the stall origin (world), to project candidates quickly
        M = Matrix.LocRotScale(Vector((x, y, h(x, y))), Euler(r), Vector((ss, ss, ss)))
        lv = _LOCAL_VERTS[nm]
        top = max(v.z for v in lv)
        roof = [M @ v for v in lv if v.z > 0.6 * top]
        c = Vector([(min(v[i] for v in roof) + max(v[i] for v in roof)) / 2 for i in range(3)])
        offs.append(c - Vector((x, y, 0.0)))
        rot_fns.append(rot_fn)
        STALLS.append([nm, x, y, r[2], ss, None, hw, hd])
    # 6-stud gaps with the least frame error: minimise the (near-minimax) frame error of all
    # four roof centres with a steep penalty on any gap under MARKET_GAP
    targets = [MASTER["Stall " + role] for _, _, role, _ in MARKET_STALLS]

    ns = len(STALLS)

    def cost(p):
        # p: x, y per stall, then a yaw tweak per stall (at most ~25 degrees off the facing rule)
        rects = [(p[2 * i], p[2 * i + 1], rot_fns[i](p[2 * i], p[2 * i + 1]) + p[2 * ns + i], st[6], st[7])
                 for i, st in enumerate(STALLS)]
        e = sum(4000.0 * max(0.0, abs(p[2 * ns + i]) - 0.35) ** 2 + 0.5 * p[2 * ns + i] ** 2 for i in range(ns))
        for i, (t, o) in enumerate(zip(targets, offs)):
            u, v = _pct((p[2 * i] + o.x, p[2 * i + 1] + o.y, o.z))
            e += ((u - t[0]) ** 2 + (v - t[1]) ** 2) ** 3
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                g = _rect_sep(rects[i], rects[j])
                if g < MARKET_GAP + 0.15:
                    e += 1e5 * (MARKET_GAP + 0.15 - g) ** 2
        return e
    p = [v for st in STALLS for v in (st[1], st[2])] + [0.0] * ns
    for step in (2.0, 0.6, 0.2, 0.6, 0.1):
        p = _nelder(cost, p, [step] * (2 * ns) + [0.1 * step] * ns, 2500)
    for i, st in enumerate(STALLS):
        x, y = p[2 * i], p[2 * i + 1]
        r = rot_fns[i](x, y) + p[2 * ns + i]
        STALLS[i] = (st[0], x, y, r, st[4], (math.sin(r), -math.cos(r)), st[6], st[7])
    for i, a in enumerate(STALLS):
        gaps = [_rect_gap((a[1], a[2], a[3], a[6], a[7]), (b[1], b[2], b[3], b[6], b[7]))
                for j, b in enumerate(STALLS) if j != i]
        print(f"market stall {MARKET_ROLES[i]:6s} at ({a[1]:6.1f}, {a[2]:6.1f}) yaw {math.degrees(a[3]):6.1f}"
              f"  min gap {min(gaps):4.1f}")
    plan_paths()


ARRIVAL = dict(x=0.0, y=-37.0 * LS)


def plan_paths():
    def F(lx, ly):
        return local(FORGE["x"], FORGE["y"], FORGE["rot"], lx * FORGE["s"], ly * FORGE["s"])

    def V(lx, ly):
        return local(VAULT["x"], VAULT["y"], VAULT["rot"], lx * VAULT["s"], ly * VAULT["s"])
    lanes = market_lanes()
    lane_mid = [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in lanes]
    gy = WALL["cy"] + WALL["ry"]
    PATHS[:] = [  # (polyline, width): a ring road round the benches plus 9-10-stud paths to every zone,
        # leaving four large grass islands in the quadrants (reference)
        ([(0, 12 * LS), (0, gy - 8), (1.2, gy + 5), (3 * LS, 56 * LS), (-2 * LS, 72 * LS), (-3 * LS, 97 * LS),
          (-3 * LS, 113 * LS)], 8.5 * LS),                                                  # N: gate, out to the arch
        (_S([(-9, 11)]) + [quest_local(0.0, -5.5), totem_local(5.0, -11.0), totem_local(-1.0, -10.5)], 9.0),  # NW
        (_S([(-14, -3)]) + [MARKET_LABEL], 9.0),                                             # W: plaza to the market
        ([(0, -12 * LS), (ARRIVAL["x"], ARRIVAL["y"]), (0, WALL["cy"] - WALL["ry"] + 3)], 8.0 * LS),  # S
        (_S([(11, -8)]) + [V(0.0, -8.72 - 6.0)], 8.5 * LS),                                 # SE: vault hall
        (_S([(12, 6)]) + [F(0.0, -8.57 - 11.0)], 8.5 * LS),                                # NE: forge
        ([(-12 * LS, gy - 10), (0, gy - 6.5), (12 * LS, gy - 8.5)], 6.0 * LS),             # threshold inside the gate
    ] + [(ln, MARKET_LANE + 2.0) for ln in lanes] + [([MARKET_LABEL, m], 7.0) for m in lane_mid]
    PADS[:] = [
        F(0.0, -8.57 - 6.5) + (17 * LS, 6.0 * LS, FORGE["rot"]),       # forge stairs
        V(0.0, -8.72 - 4.5) + (11 * LS, 6 * LS, VAULT["rot"]),         # vault front
        totem_local(1.5, -9.5) + (9.5, 5.0, TOTEM["rot"]),             # totem front: the elder's spot and the braziers
        quest_local(0.0, -4.0) + (6.0, 3.5, QUEST["rot"]),             # in front of the quest board
        (ARRIVAL["x"], ARRIVAL["y"] - 1.0, 11 * LS, 9 * LS, 0),        # arrival
        (MARKET_LABEL[0], MARKET_LABEL[1], 9.0, 7.0, 0.0),             # the market square
    ]
    # market: a trodden walkway behind each stall, so the merchants walk round from the
    # customer lane to their spot behind the counter
    for nm, x, y, rot, ss, f, hw, hd in STALLS:
        PADS.append(local(x, y, rot, 0.0, hd + 1.6) + (hw + 0.5, 2.3, rot))
    # the whole market cluster stands on trodden dirt (master), so goods, not shrubs, fill it
    mx = sum(st[1] for st in STALLS) / len(STALLS)
    my = sum(st[2] for st in STALLS) / len(STALLS)
    R = max(math.hypot(st[1] - mx, st[2] - my) + st[6] for st in STALLS) + 2.0
    PADS.append((mx, my, R, R * 0.9, 0.0))


def dirt_sdf(x, y):
    n = (vn(x / 5.0 + 17, y / 5.0 + 3) - 0.5) * 2.6
    d = math.hypot(x, y) * (1 + 0.04 * math.sin(3 * math.atan2(y, x) + 1)) - PLAZA_R
    for poly, w in PATHS:
        d = min(d, seg_dist(poly, x, y) - w / 2)
    for cx, cy, rx, ry, rot in PADS:
        c, s = math.cos(-rot), math.sin(-rot)
        u, v = c * (x - cx) - s * (y - cy), s * (x - cx) + c * (y - cy)
        d = min(d, (math.hypot(u / rx, v / ry) - 1) * min(rx, ry))
    return d + n


# ---------------------------------------------------------------------------
# Scene, collections, libraries
# ---------------------------------------------------------------------------

COLL_NAMES = ["Terrain", "Palisade", "DeployGate", "Plaza", "EldersTotem", "Forge", "VaultHall",
              "Market", "ArrivalStones", "Watchtowers", "Forest", "River", "Dressing"]
C = {}
STATS = {"instances": 0, "tris": 0, "own_tris": 0, "sockets": 0, "added_sockets": 0}
KEEP = []  # (x, y, r) keep-out discs for dressing and trees
_COUNTERS = {}
_TRIS = {}
_BVH = {}
A = {}  # asset name -> linked library object


def setup_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
    # Save first so libraries link with paths relative to the lobby file.
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    root = bpy.data.collections.new("Lobby")
    bpy.context.scene.collection.children.link(root)
    C["Lobby"] = root
    for n in COLL_NAMES:
        c = bpy.data.collections.new(n)
        root.children.link(c)
        C[n] = c


def load_libraries():
    for fname in LIBS:
        path = os.path.join(ASSET_DIR, fname)
        for attempt in range(12):
            try:
                with bpy.data.libraries.load(path, link=True, relative=True) as (src, dst):
                    dst.objects = list(src.objects)
                objs = [o for o in dst.objects if o is not None]
                meshes = [o for o in objs if o.type == "MESH"]
                if not meshes:
                    raise RuntimeError("no meshes yet")
                for o in meshes:
                    A[o.name] = o
                print(f"linked {fname}: {len(meshes)} meshes")
                break
            except Exception as exc:
                print(f"load {fname} failed ({exc}); retry {attempt + 1}")
                time.sleep(15)
        else:
            raise RuntimeError(f"could not load {fname}")


def tris_of(src):
    me = src.data
    if me.name not in _TRIS:
        _TRIS[me.name] = sum(len(p.vertices) - 2 for p in me.polygons)
    return _TRIS[me.name]


def floor_z(asset, lx, ly, top=4.0):
    """Height of an asset's floor below `top` at its local (lx, ly), unscaled."""
    src = A[asset]
    if asset not in _BVH:
        me = src.data
        _BVH[asset] = BVHTree.FromPolygons([v.co.copy() for v in me.vertices],
                                           [tuple(p.vertices) for p in me.polygons])
    hit = _BVH[asset].ray_cast(Vector((lx, ly, top)), Vector((0, 0, -1)))
    return hit[0].z if hit[0] is not None else 0.0


def _mesh_of(o):
    return A[o["lobby_asset"]].data if o.get("lobby_asset") else o.data


def world_bvh(o, inset=0.03):
    """BVH of an object's triangles in world space, every vertex pulled `inset` studs
    inward along its normal, so surfaces that merely touch do not count as intersecting."""
    me = _mesh_of(o)
    M = Matrix.LocRotScale(o.location, o.rotation_euler, o.scale)
    verts = [M @ (v.co - v.normal * inset) for v in me.vertices]
    return BVHTree.FromPolygons(verts, [tuple(p.vertices) for p in me.polygons], all_triangles=False), verts


def world_min_z(o):
    me = _mesh_of(o)
    M = Matrix.LocRotScale(o.location, o.rotation_euler, o.scale)
    return min((M @ v.co).z for v in me.vertices)


def rest_on(o, surface_z, gap=0.01):
    """Drop an object so its lowest vertex sits on surface_z (no floating, no sinking)."""
    o.location.z += surface_z + gap - world_min_z(o)


def settle(o, supports, drop=3.0, steps=14):
    """Lower an object from its current height until it just touches the supports (exact
    mesh test, binary search): it ends resting on whatever is highest under it."""
    hi = o.location.z
    lo = hi - drop
    if hits(o, supports, inset=0.0):
        return o
    for _ in range(steps):
        mid = (lo + hi) / 2
        o.location.z = mid
        if hits(o, supports, inset=0.0):
            lo = mid
        else:
            hi = mid
    o.location.z = hi + 0.01
    return o


def hits(o, others, inset=0.03):
    b, _ = world_bvh(o, inset)
    return any(b.overlap(world_bvh(q, inset)[0]) for q in others)


_TILE = {}


def tile_info(name):
    """Measure a terrain-kit tile at build time (no hard-coded heights), so a rebuilt kit
    with different tile heights or organic outlines still lands flush with the plateau.

    top / low   : the highest and lowest walkable levels (z of up-facing area peaks)
    lip_y       : local y of the top level's front (-Y) edge, i.e. where the cliff drops
    lip_x       : local x of the top level's left (-X) edge (outer corners drop on -X too)
    water_top / water_low / water_mid : levels of up-facing water faces
    shore_y     : local y of the water's back (+Y) edge (river banks: where land begins)
    pool        : local (x, y) centre of the lowest water (waterfall pool)
    """
    if name in _TILE:
        return _TILE[name]
    me = A[name].data
    ups, water = [], []
    for p in me.polygons:
        if p.normal.z < 0.75 or p.area < 1e-4:
            continue
        mname = me.materials[p.material_index].name if me.materials and me.materials[p.material_index] else ""
        c = p.center
        if "water" in mname:
            water.append((c, p.area))
        elif not any(k in mname for k in ("leaf", "pine", "bark", "wood", "fire", "ember")):
            ups.append((c, p.area))
    hist = {}
    for c, a in ups:
        k = round(c.z * 2) / 2
        hist[k] = hist.get(k, 0.0) + a
    tot = sum(hist.values()) or 1.0
    levels = sorted(z for z, a in hist.items() if a > 0.08 * tot)

    def refine(z0):  # area-weighted mean height of the faces in that level
        sel = [(c.z, a) for c, a in ups if abs(c.z - z0) <= 0.5]
        return sum(z * a for z, a in sel) / sum(a for _, a in sel) if sel else z0

    top = refine(max(levels)) if levels else max(c.z for c, _ in ups)
    low = refine(min(levels)) if levels else 0.0

    def pct(vals, q):
        vals = sorted(vals)
        return vals[min(len(vals) - 1, max(0, int(q * len(vals))))] if vals else 0.0

    top_faces = [c for c, _ in ups if abs(c.z - top) < 1.2]
    info = dict(top=top, low=low,
                lip_y=pct([c.y for c in top_faces if abs(c.x) < 7] or [c.y for c in top_faces], 0.03),
                lip_x=pct([c.x for c in top_faces if abs(c.y) < 7] or [c.x for c in top_faces], 0.03))
    if water:
        wz = [c.z for c, _ in water]
        info.update(water_top=max(wz), water_low=min(wz), water_mid=pct(wz, 0.5),
                    shore_y=pct([c.y for c, _ in water], 0.97))
        lowest = [c for c, _ in water if c.z < min(wz) + 0.6]
        info["pool"] = (sum(c.x for c in lowest) / len(lowest), sum(c.y for c in lowest) / len(lowest))
        hi = [c for c, _ in water if c.z > max(wz) - 1.0]
        info["water_lip_y"] = pct([c.y for c in hi], 0.03)
    _TILE[name] = info
    print("tile", name, {k: (tuple(round(x, 2) for x in v) if isinstance(v, tuple) else round(v, 2)) for k, v in info.items()})
    return info


def uniq(prefix):
    _COUNTERS[prefix] = _COUNTERS.get(prefix, 0) + 1
    return f"{prefix}_{_COUNTERS[prefix]:03d}"


def copy_sockets(src, inst, scale):
    n = 0
    for c in src.children:
        if not c.get("vfx_kind"):
            continue
        e = bpy.data.objects.new(f"VFX_{c['vfx_kind']}_{inst.name}", None)
        e.empty_display_type = c.empty_display_type
        e.empty_display_size = c.empty_display_size
        for coll in inst.users_collection:
            coll.objects.link(e)
        e.parent = inst
        e.matrix_parent_inverse = c.matrix_parent_inverse.copy()
        e.location = c.location.copy()
        e.rotation_euler = c.rotation_euler.copy()
        e.scale = c.scale.copy()
        for k in c.keys():
            e[k] = c[k]
        # the Empty inherits the instance scale; scale the effect with it
        e["vfx_scale"] = float(c.get("vfx_scale", 1.0)) * scale
        n += 1
    return n


def _auto_sockets(asset, inst, scale):
    """Fallback for library objects that should carry effects but have none yet."""
    if vfx is None:
        return 0
    me = A[asset].data
    fire = [p for p in me.polygons if me.materials and me.materials[p.material_index]
            and me.materials[p.material_index].name.startswith("FB_fire")]
    if not fire:
        return 0
    kind = {"PalisadeTorchPost": "torch_fire", "TorchPost": "torch_fire", "DeployGate": "torch_fire",
            "StoneBrazier": "brazier_fire", "Campfire": "campfire", "AncestralForge": "forge_fire",
            "SmeltingFurnace": "forge_fire"}.get(asset)
    if kind is None:
        return 0
    groups = {}
    for p in fire:  # split left / right halves for twin torches
        key = int(p.center.x > 0) if asset == "DeployGate" else 0
        groups.setdefault(key, []).append(p.center)
    n = 0
    for pts in groups.values():
        c = sum(pts, Vector()) / len(pts)
        c.z = min(p.z for p in pts)
        e = vfx.add(inst, kind, tuple(c), scale=scale)
        e.name = f"VFX_{kind}_{inst.name}"
        n += 1
    STATS["added_sockets"] += n
    return n


def put(asset, x, y, rz=0.0, s=1.0, coll="Dressing", name=None, z=None, rx=0.0, ry=0.0,
        zoff=0.0, keep=0.9, low=False):
    src = A[asset]
    o = bpy.data.objects.new(name or uniq(asset), src.data)
    C[coll].objects.link(o)
    sc = s if isinstance(s, (tuple, list)) else (s, s, s)
    if z is not None:
        zz = z
    elif low:
        zz = h_low(x, y)
    else:
        zz = ground_under(src, x, y, rz, sc)
    o.location = (x, y, zz + zoff)
    o.rotation_euler = (rx, ry, rz)
    o.scale = sc
    o["lobby_asset"] = asset
    n = copy_sockets(src, o, sc[0])
    if n == 0:
        n = _auto_sockets(asset, o, sc[0])
    STATS["sockets"] += n
    STATS["instances"] += 1
    STATS["tris"] += tris_of(src)
    if keep:
        d = src.dimensions
        KEEP.append((x, y, 0.5 * max(d.x * sc[0], d.y * sc[1]) * keep))
    return o


def put_clear(asset, x, y, rz, s, coll, name, others, max_r=5.0):
    """put() at (x, y), or at the nearest spot on a widening spiral where its mesh does not
    intersect `others` (exact test), so a prop keeps its frame position as far as it can."""
    o = put(asset, x, y, rz, s, coll, name)
    sc = tuple(o.scale)
    for r in np.arange(0.0, max_r, 0.35):
        n = max(1, int(2 * math.pi * r / 0.5))
        for k in range(n):
            a = 2 * math.pi * k / n
            px, py = x + r * math.cos(a), y + r * math.sin(a)
            o.location = (px, py, ground_under(A[asset], px, py, rz, sc))
            if not hits(o, others):
                KEEP[-1] = (px, py, KEEP[-1][2])
                return o
    print("put_clear: no clear spot for", name)
    return o


def ground_under(src, x, y, rz, sc):
    """Lowest plateau height under an object's footprint (centre, corners, edge midpoints),
    so nothing floats on the uneven ground; the high side just beds in slightly."""
    if "Tree" in src.name:  # trunk footprint only, not the canopy
        return h(x, y)
    bb = src.bound_box
    x0, x1 = min(v[0] for v in bb) * sc[0], max(v[0] for v in bb) * sc[0]
    y0, y1 = min(v[1] for v in bb) * sc[1], max(v[1] for v in bb) * sc[1]
    pts = [(0, 0), (x0, y0), (x1, y0), (x0, y1), (x1, y1), (x0, 0), (x1, 0), (0, y0), (0, y1)]
    return min(h(*local(x, y, rz, px * 0.85, py * 0.85)) for px, py in pts)


def free(x, y, r=0.0):
    for kx, ky, kr in KEEP:
        if (x - kx) ** 2 + (y - ky) ** 2 < (kr + r) ** 2:
            return False
    return True


def own(asset_obj):
    """Book-keeping for meshes built here."""
    STATS["own_tris"] += asset_obj["tris"]
    return asset_obj


# ---------------------------------------------------------------------------
# Ground meshes (flintkit Asset, not marked as assets)
# ---------------------------------------------------------------------------


def _paint(a, face, mat, var=0.05):
    """Material + a smooth, low-frequency hand-painted brightness wash (no per-cell mosaic)."""
    face.material_index = a._mi(mat)
    face.smooth = False
    for lp in face.loops:
        co = lp.vert.co
        t = 1.0 + var * 2.2 * (vn(co.x / 9.0 + 31, co.y / 9.0 + 47) - 0.5) + var * 0.8 * (vn(co.x / 2.5, co.y / 2.5) - 0.5)
        lp[a.tint_layer] = (t, t, t, 1.0)


def build_plateau():
    a = fk.Asset("Ground_Plateau", "Ground", seed=SEED)
    bm = a.bm
    rim = se_curve(RIM, N=4000)
    M, NR = 300, 64
    O = Vector((0, RIM["cy"]))
    rims = [rim.at(rim.length * j / M) for j in range(M)]
    rings = []
    centre = bm.verts.new((O.x, O.y, h(O.x, O.y)))
    for i in range(1, NR + 1):
        s = (i / NR) ** 0.9
        ring = []
        for j in range(M):
            p = O + (rims[j] - O) * s
            ring.append(bm.verts.new((p.x, p.y, h(p.x, p.y))))
        rings.append(ring)
    faces = []
    for j in range(M):
        faces.append(bm.faces.new((centre, rings[0][j], rings[0][(j + 1) % M])))
    for i in range(NR - 1):
        r0, r1 = rings[i], rings[i + 1]
        for j in range(M):
            faces.append(bm.faces.new((r0[j], r1[j], r1[(j + 1) % M], r0[(j + 1) % M])))
    for f in faces:
        _paint_grass(a, f)
    return own(a.finish(collection=C["Terrain"], mark_asset=False, origin="NONE"))


# Grass colour: one palette green, varied through the RGB Tint by value noise at three scales
# (big soft patches, medium mottling, fine speckle), from a deeper olive-green in the dips to
# a sun-dried yellow-green on the highs, like the painted reference ground. No per-face
# material switching, so there is no triangle checker; faces are smooth-shaded so the gentle
# height bumps read as soft light and shade instead of facets.
GRASS_DARK = (0.60, 0.72, 0.45)
GRASS_LIGHT = (0.88, 0.84, 0.58)


def grass_tint(x, y, bias=0.0):
    w = (0.55 * vn(x / 24 + 11, y / 24 + 5) + 0.30 * vn(x / 9 + 3, y / 9 + 77)
         + 0.15 * vn(x / 3 + 19, y / 3 + 2) + bias)
    t = smoothstep(0.22, 0.78, w)
    return tuple(d + (l - d) * t for d, l in zip(GRASS_DARK, GRASS_LIGHT))


def _paint_grass(a, face, mat="grass_ground"):
    face.material_index = a._mi(mat)
    face.smooth = True
    for lp in face.loops:
        co = lp.vert.co
        # the forest band outside the palisade sits darker, under the canopy
        inside = se_F(co.x, co.y, WALL)
        bias = -0.4 * smoothstep(1.0, 1.25, inside)
        lp[a.tint_layer] = (*grass_tint(co.x, co.y, bias), 1.0)


def build_lower_ground():
    a = fk.Asset("Ground_Lowland", "Ground", seed=SEED + 2)
    bm = a.bm
    step = 6.0
    # sized from the plateau rim, so a larger camp just gets a larger lowland
    xs = np.arange(-2.64 * RIM["rx"], 2.64 * RIM["rx"] + 1, step)
    ys = np.arange(RIM["cy"] - 2.76 * RIM["ry"], RIM["cy"] + 3.05 * RIM["ry"] + 1, step)
    V = [[bm.verts.new((x, y, h_low(x, y))) for x in xs] for y in ys]
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            f = bm.faces.new((V[j][i], V[j][i + 1], V[j + 1][i + 1], V[j + 1][i]))
            c = f.calc_center_median()
            if c.z < LOW_Z - 1.2:
                _paint(a, f, "earth" if c.z > LOW_Z - 2.6 else "sand", 0.05)
            else:
                _paint_grass(a, f)
    return own(a.finish(collection=C["Terrain"], mark_asset=False, origin="NONE"))


def implicit_mesh(name, fn, bbox, step, mat, zfun, coll, var=0.05, mat_fn=None):
    """Mesh of the region fn(x, y) < 0, cut cell by cell from a grid (smooth contour)."""
    a = fk.Asset(name, "Ground", seed=SEED + len(name))
    bm = a.bm
    x0, y0, x1, y1 = bbox
    xs = [x0 + i * step for i in range(int((x1 - x0) / step) + 2)]
    ys = [y0 + j * step for j in range(int((y1 - y0) / step) + 2)]
    vals = [[fn(x, y) for x in xs] for y in ys]
    cache = {}

    def V(x, y):
        k = (round(x, 3), round(y, 3))
        if k not in cache:
            cache[k] = bm.verts.new((x, y, zfun(x, y)))
        return cache[k]

    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            cs = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            cv = [vals[cj][ci] for ci, cj in cs]
            if all(v >= 0 for v in cv):
                continue
            pts = []
            for k in range(4):
                (ai, aj), (bi, bj) = cs[k], cs[(k + 1) % 4]
                va, vb = cv[k], cv[(k + 1) % 4]
                if va < 0:
                    pts.append((xs[ai], ys[aj]))
                if (va < 0) != (vb < 0):
                    # interpolate from the lower-index corner so neighbours agree
                    if (ai, aj) <= (bi, bj):
                        t = va / (va - vb)
                        pts.append((xs[ai] + (xs[bi] - xs[ai]) * t, ys[aj] + (ys[bj] - ys[aj]) * t))
                    else:
                        t = vb / (vb - va)
                        pts.append((xs[bi] + (xs[ai] - xs[bi]) * t, ys[bj] + (ys[aj] - ys[bj]) * t))
            vs = []
            for p in pts:
                v = V(*p)
                if v not in vs:
                    vs.append(v)
            if len(vs) >= 3:
                try:
                    f = bm.faces.new(vs)
                except ValueError:
                    continue
                c = f.calc_center_median()
                _paint(a, f, mat_fn(c.x, c.y) if mat_fn else mat, var)
    return own(a.finish(collection=coll, mark_asset=False, origin="NONE"))


def build_dirt():
    """Muted ochre-tan earth: the `sand` palette colour, washed smoothly toward `dirt`
    through the Tint attribute (so there are no hard cell edges between the two)."""
    bbox = (-1.19 * WALL["rx"], WALL["cy"] - 1.34 * WALL["ry"], 1.19 * WALL["rx"], RIM["cy"] + 1.06 * RIM["ry"])
    o = implicit_mesh("Ground_DirtPlazaPaths", dirt_sdf, bbox, 1.0, "sand",
                      lambda x, y: h(x, y) + 0.07, C["Plaza"], var=0.0)
    sand, dirt = fk.hex_rgb(fk.PALETTE["sand"][0]), fk.hex_rgb(fk.PALETTE["dirt"][0])
    ratio = [d / s for d, s in zip(dirt, sand)]
    me = o.data
    layer = me.color_attributes["Tint"]
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            w = 0.5 + 0.4 * vn(co.x / 10 + 70, co.y / 10 + 20) + 0.2 * (vn(co.x / 3 + 5, co.y / 3 + 9) - 0.5)
            w = min(max(w, 0.0), 0.9)
            # trodden mottling: broad darker patches plus fine grain (reference dirt is not flat)
            b = 0.62 + 0.18 * vn(co.x / 6 + 13, co.y / 6 + 41) + 0.1 * vn(co.x / 2.2, co.y / 2.2)
            b *= 1.0 - 0.28 * smoothstep(0.62, 0.85, vn(co.x / 1.3 + 7, co.y / 1.3 + 3))  # darker trodden blotches
            layer.data[li].color = tuple(b * (1 + (r - 1) * w) for r in ratio) + (1.0,)
    return o


def build_pebbles():
    """Scattered pebbles over the plaza and paths."""
    a = fk.Asset("Ground_Pebbles", "Ground", seed=SEED + 6)
    rng = random.Random(SEED + 6)
    n = 0
    for _ in range(6000):
        x = rng.uniform(-1.1 * WALL["rx"], 1.1 * WALL["rx"])
        y = rng.uniform(WALL["cy"] - 1.2 * WALL["ry"], RIM["cy"] + 0.88 * RIM["ry"])
        if dirt_sdf(x, y) > -0.6 or (abs(x) < 2.5 and y > 20 * LS):
            continue
        s = rng.uniform(0.25, 0.75)
        a.rock((s * rng.uniform(1.0, 1.6), s, s * 0.55), loc=(x, y, h(x, y) + 0.02),
               rot=(0, 0, rng.uniform(0, 6.28)), mat=rng.choice(["stone", "stone_light", "stone_dark"]),
               subdiv=1, rough=0.12, facets=12, sink=0.35)
        n += 1
        if n >= int(420 * LS * LS):
            break
    return own(a.finish(collection=C["Plaza"], mark_asset=False, origin="NONE"))


def build_stepping_stones():
    """A small cluster of flat flagstones just inside the Deploy gate."""
    a = fk.Asset("Ground_GateFlagstones", "Ground", seed=SEED + 5)
    rng = random.Random(SEED + 5)
    gy = WALL["cy"] + WALL["ry"]   # the gate stands on the wall line
    y = gy - 15.6  # from just inside the gate to its sill
    while y < gy - 3.0:
        for side in (-3.2, 0.0, 3.2):
            x = side + rng.uniform(-0.6, 0.6)
            sx, sy = rng.uniform(2.6, 3.6), rng.uniform(2.0, 2.8)
            a.rock((sx, sy, 0.55), loc=(x, y, h(x, y) + 0.02), rot=(0, 0, rng.uniform(-0.5, 0.5)),
                   mat=rng.choice(["stone", "stone_light"]), subdiv=1, rough=0.1, facets=10, sink=0.3)
        y += rng.uniform(3.0, 3.8)
    return own(a.finish(collection=C["DeployGate"], mark_asset=False, origin="NONE"))


def build_ribbon(name, poly, half_w, zf, coll, mats=("water_shallow", "water", "water_shallow"),
                 step=2.0):
    a = fk.Asset(name, "Water", seed=SEED + 9)
    bm = a.bm
    cur = Curve(poly)
    n = max(2, int(cur.length / step))
    fr = (-1.0, -0.62, 0.62, 1.0)
    rows = []
    for k in range(n + 1):
        s = cur.length * k / n
        p, t = cur.at(s), cur.tangent(s)
        nrm = Vector((-t.y, t.x))
        w = half_w * (1 + 0.08 * math.sin(s * 0.3))
        rows.append([bm.verts.new((p.x + nrm.x * w * f, p.y + nrm.y * w * f, zf(s))) for f in fr])
    for k in range(n):
        for c in range(3):
            f = bm.faces.new((rows[k][c], rows[k][c + 1], rows[k + 1][c + 1], rows[k + 1][c]))
            _paint(a, f, mats[c], 0.02)
    return own(a.finish(collection=coll, mark_asset=False, origin="NONE"))


def build_rug(x, y, z, rot, size=(7.5, 5.5)):
    a = fk.Asset("VaultHall_RedRug", "Ground", seed=SEED + 13)
    a.box((size[0], size[1], 0.12), loc=(0, 0, 0.06), mat="cloth_red", bevel=0.04)
    a.box((size[0] * 0.62, size[1] * 0.55, 0.13), loc=(0, 0, 0.07), mat="cloth_cream", bevel=0.02)
    a.box((size[0] * 0.5, size[1] * 0.42, 0.14), loc=(0, 0, 0.075), mat="cloth_red")
    o = a.finish(collection=C["VaultHall"], mark_asset=False, origin="BOTTOM")
    o.location = (x, y, z)
    o.rotation_euler = (0, 0, rot)
    return own(o)


# ---------------------------------------------------------------------------
# Terrain kit: cliffs, waterfall, river banks, forest floor
# ---------------------------------------------------------------------------


def terrain():
    rim = se_curve(RIM, N=4000)
    O = Vector((0, RIM["cy"]))

    # waterfall where the river meets the east rim
    end = Vector(RIVER_PTS[-1])
    best_s = min((s for s in np.arange(0, rim.length, 0.5)), key=lambda s: (rim.at(s) - end).length)
    p = rim.at(best_s)
    t = rim.tangent(best_s)
    outward = Vector((t.y, -t.x))
    if outward.dot(p - O) < 0:
        outward = -outward
    rot = math.atan2(outward.y, outward.x) + math.pi / 2   # local -Y -> outward
    wfi = tile_info("WaterfallCliff")
    c = p + outward * wfi.get("water_lip_y", 4.0)          # top-water lip on the rim
    WF.update(x=c.x, y=c.y, rot=rot, s=best_s, px=p.x, py=p.y)
    put("WaterfallCliff", c.x, c.y, rot, 1.0, "River", "River_WaterfallCliff",
        z=RIVER_Z - wfi.get("water_top", 19.2), keep=0)
    pool = Vector(local(c.x, c.y, rot, *wfi.get("pool", (0, -9))))
    LOW_RIVER[:] = chaikin([(pool.x, pool.y), (pool.x + outward.x * 30, pool.y + outward.y * 30),
                            (pool.x + 70, pool.y - 30), (pool.x + 120, pool.y - 90), (pool.x + 150, pool.y - 200)], 2)

    # cliff ring
    north_exit = Vector((-3 * LS, RIM["cy"] + RIM["ry"]))
    s = 0.0
    step = 22.0  # rounded tile outlines: overlap neighbours well so corners close up
    corners = []
    for ang in (45, 135, 225, 315):  # superellipse "corners"
        a = math.radians(ang)
        cc, ss = math.cos(a), math.sin(a)
        q = Vector((RIM["rx"] * math.copysign(abs(cc) ** (2 / RIM["n"]), cc),
                    RIM["cy"] + RIM["ry"] * math.copysign(abs(ss) ** (2 / RIM["n"]), ss)))
        corners.append(min(np.arange(0, rim.length, 0.5), key=lambda s_: (rim.at(s_) - q).length))
    n_tiles = int(rim.length / step)
    k = 0
    for i in range(n_tiles):
        s = rim.length * i / n_tiles
        p = rim.at(s)
        t = rim.tangent(s)
        outward = Vector((t.y, -t.x))
        if outward.dot(p - O) < 0:
            outward = -outward
        d_wf = min(abs(s - WF["s"]), rim.length - abs(s - WF["s"]))
        if d_wf < 22:
            continue
        if (p - north_exit).length < 20:
            rot = math.atan2(outward.y, outward.x) + math.pi / 2
            sw = tile_info("EarthSwitchback")
            cpos = p + outward * 12
            put("EarthSwitchback", cpos.x, cpos.y, rot, 1.0, "Terrain", "Terrain_EarthSwitchback", z=-sw["top"], keep=0)
            continue
        near_corner = min(min(abs(s - cs), rim.length - abs(s - cs)) for cs in corners)
        k += 1
        if near_corner < step / 2:
            rot = math.atan2(outward.y, outward.x) + math.radians(135)
            oc = tile_info("CliffOuterCorner")
            off = Vector((oc["lip_x"] - 0.7, oc["lip_y"] - 0.7))  # lip just past the rim, under the grass edge
            off.rotate(Matrix.Rotation(rot, 2))
            cpos = p - off
            put("CliffOuterCorner", cpos.x, cpos.y, rot, 1.0, "Terrain", uniq("Terrain_CliffOuterCorner"),
                z=-oc["top"] - 0.3, keep=0)
        else:
            rot = math.atan2(outward.y, outward.x) + math.pi / 2
            cs = tile_info("CliffSection")
            cpos = p + outward * (cs["lip_y"] + 1.0)        # lip (local y < 0) 1 stud past the rim
            put("CliffSection", cpos.x, cpos.y, rot + RNG.uniform(-0.03, 0.03), 1.0, "Terrain",
                uniq("Terrain_CliffSection"), z=-cs["top"] - 0.3 + RNG.uniform(-0.2, 0.0), keep=0)
        # stepped shelves at the foot of some cliffs
        if k % 3 == 1:
            q = p + outward * 14
            put("RockShelfTwoLevels", q.x, q.y, math.atan2(outward.y, outward.x) + math.pi / 2, 1.0, "Terrain",
                uniq("Terrain_RockShelf"), z=LOW_Z - tile_info("RockShelfTwoLevels")["low"], keep=0)

    # upper ridge: cliffs facing the camp beyond the forest (grey rock at the top of the
    # view, behind the forge and at the top-left), the north path passing through a rock arch
    ridge = _S([(-82, 68), (-58, 84), (-31, 93), (25, 86), (52, 71)])
    for x, y in ridge:
        put("CliffSection", x, y, face_to(x, y, 0, -10 * LS) + RNG.uniform(-0.05, 0.05), 1.0, "Terrain",
            uniq("Terrain_RidgeCliff"), z=-tile_info("CliffSection")["low"] - 0.4, keep=0)
        KEEP.append((x, y, 14))
    ax_, ay_ = -3 * LS - 2.0, 97 * LS   # opening (local x ~ +2) sits on the north path
    put("RockArch", ax_, ay_, 0.0, 1.0, "Terrain", "Terrain_RockArch_NorthPath",
        z=-tile_info("RockArch")["low"] - 0.3, keep=0)
    KEEP.append((ax_, ay_, 14))
    put("WaterfallCliff", UWF_POS[0], UWF_POS[1], UWF_ROT, 1.0, "River", "River_WaterfallCliff_Ridge",
        z=RIVER_Z + 0.3 - tile_info("WaterfallCliff").get("water_low", 1.5), keep=0)
    KEEP.append((UWF_POS[0], UWF_POS[1], 15))

    # river banks on the plateau
    L = RIVER.length
    for s in np.arange(9, L - 12, 16):
        p, t = RIVER.at(s), RIVER.tangent(s)
        nl = Vector((-t.y, t.x))
        for side in (1, -1):
            away = nl * side
            rb = tile_info("Riverbank")
            cpos = p + away * (RIVER_W - rb.get("shore_y", 3.5))
            rot = math.atan2(away.y, away.x) - math.pi / 2
            corners = [Vector(local(cpos.x, cpos.y, rot, cx_, cy_)) for cx_ in (-16, 16) for cy_ in (-12, 12)]
            if max(se_F(c_.x, c_.y, RIM) for c_ in corners) > 0.985:
                continue  # would hang out over the cliff rim
            put("Riverbank", cpos.x, cpos.y, rot, 1.0, "River", uniq("River_Riverbank"),
                z=RIVER_Z - rb.get("water_mid", 2.2), keep=0)
    build_ribbon("River_WaterUpper", RIVER_PTS + [(WF["px"], WF["py"])], RIVER_W,
                 lambda s: RIVER_Z + 0.02, C["River"])
    build_ribbon("River_WaterLower", LOW_RIVER, 7.0, lambda s: LOW_Z - 2.4, C["River"])
    # footbridge across the river just below the ridge waterfall
    s_b = RIVER.length * 0.16
    p, t = RIVER.at(s_b), RIVER.tangent(s_b)
    put("FootbridgeSmall", p.x, p.y, math.atan2(t.y, t.x) + math.pi / 2, 1.0, "River", "River_FootbridgeSmall",
        z=0.1, keep=5)
    KEEP.append((p.x, p.y, 9))
    for i, (dx, dy, nm, sc) in enumerate([(-9, 4, "SplitBoulder", 0.9), (8, 9, "LowBoulder", 0.8), (-6, -9, "LowBoulder", 0.7)]):
        put(nm, UWF_POOL[0] + dx, UWF_POOL[1] + dy, RNG.uniform(0, 6.28), sc, "River", f"River_PoolRock_{i + 1}",
            zoff=-0.6, keep=1.0)


def build_rim_skirt():
    """A rock skirt hanging from the plateau edge all the way round, just inside the cliff
    tiles: wherever rounded tile corners leave a gap, you see rock, never sky or a floating
    grass edge."""
    a = fk.Asset("Terrain_RimSkirt", "Ground", seed=SEED + 16)
    bm = a.bm
    rim = se_curve(RIM, N=4000)
    O = Vector((0, RIM["cy"]))
    M = 360
    top, bot = [], []
    for j in range(M):
        p = rim.at(rim.length * j / M)
        q = O + (p - O) * (1 - 0.4 / (p - O).length)
        z = h(q.x, q.y) - 0.15
        jit = 0.6 * (vn(j * 0.7, 3.3) - 0.5)
        top.append(bm.verts.new((q.x, q.y, z)))
        bot.append(bm.verts.new((q.x + jit, q.y + jit, LOW_Z - 1.5)))
    for j in range(M):
        k = (j + 1) % M
        f = bm.faces.new((top[j], top[k], bot[k], bot[j]))
        _paint(a, f, "stone_dark" if (j // 3) % 2 else "stone", 0.06)
    return own(a.finish(collection=C["Terrain"], mark_asset=False, origin="NONE"))


def forest_floor_tiles():
    rng = random.Random(SEED + 21)
    for gx in range(-8, 9):
        for gy in range(-8, 10):
            x, y = gx * 32 + 16, gy * 32
            f = se_F(x, y, RIM)
            corners = [se_F(x + dx, y + dy, RIM) for dx in (-16, 16) for dy in (-16, 16)]
            if min(corners) > 1.08 and f < 2.4:
                if WF and math.hypot(x - WF["x"], y - WF["y"]) < 40:
                    continue
                if LOW_RIVER and seg_dist(LOW_RIVER, x, y) < 26:
                    continue
                put("ForestFloor", x, y, rng.choice([0, 1, 2, 3]) * math.pi / 2, 1.0, "Forest",
                    uniq("Forest_ForestFloor"), z=LOW_Z - tile_info("ForestFloor")["top"] + 0.05, keep=0)
    # a few on the plateau band north of the wall
    for x, y in _S([(-45, 52)]):
        put("ForestFloor", x, y, rng.choice([0, 1, 2, 3]) * math.pi / 2, 1.0, "Forest",
            uniq("Forest_ForestFloor"), z=h(x, y) - tile_info("ForestFloor")["top"] + 0.05, keep=0)


# ---------------------------------------------------------------------------
# Palisade
# ---------------------------------------------------------------------------

# x, y are refitted to the master in plan_layout(); the vault turns more square to the view
# (the master shows its long thatch ridge almost side-on)
FORGE = dict(x=41.0 * LS, y=23.0 * LS, rot=math.radians(-20), s=1.4)
VAULT = dict(x=40.0 * LS, y=-22.5 * LS, rot=math.radians(-28), s=1.2)


def in_rect(x, y, cx, cy, rot, hx, hy):
    c, s = math.cos(-rot), math.sin(-rot)
    u, v = c * (x - cx) - s * (y - cy), s * (x - cx) + c * (y - cy)
    return abs(u) < hx and abs(v) < hy


GATE_HALF = 16.9    # DeployGate half width (13.11 x WALL_S) plus clearance
SOUTH_FRAME_U = 38.5   # the south entrance's torch posts stand at 38.5 % / 61.5 % across (master)


def wall_blocked(p):
    if abs(p.x) < GATE_HALF and p.y > 0:
        return "gate"
    if in_rect(p.x, p.y, FORGE["x"], FORGE["y"], FORGE["rot"], 30.3 * FORGE["s"] / 2 + 0.6, 17 * FORGE["s"] / 2 + 0.6):
        return "forge"
    for tx, ty, trot, hx, hy in TOWERS:  # towers stand in the wall line: no stake passes through them
        if in_rect(p.x, p.y, tx, ty, trot, hx + 1.2, hy + 1.2):
            return "tower"
    return None


TOWERS = []  # (x, y, rot, half x, half y) of each watchtower footprint


# Master-style wall (sheet 02): a tall, dense palisade of PalisadeSection bays with a thick
# flat-topped main post on a stone footing centred on every join, hiding the bay ends (the
# kit's tiling). Bay ends stop POST_IN short of the join, so neighbouring bays never touch
# each other; the bay ends sit inside their post, which the overlap audit records as an
# intentional join contact (wall_join / wall_joins tags), not as an overlap.
PIECE_S = 1.2      # wall piece scale along and across the wall (low plank bays and rails: uniform)
SECTION_H = 11.0   # stake height: about two characters, as tall as the stall roofs (master)
POST_S = 1.15      # main posts: 13.9 studs, rising ~25% above the stakes (master)
POST_IN = 0.5      # bay ends stop this far short of the join, inside the post log
BAY_STEP = 11.5    # target join spacing along the wall (a true-width bay between posts)
JOINT = 0.25       # clear gap between a run's end post and the gate / tower / forge
POSTS = {"main": "PalisadeMainPost", "banner": "PalisadeMainPostBanner", "torch": "PalisadeMainPostTorch"}
POST_FOOT = {}     # post asset -> (footing centre x, footing centre y, footing width along the wall)
POST_HALF = 0.0    # half a post's footing along the wall plus the joint
BAY = 10.0         # section length (true studs)
BANNER_EVERY = 3   # a banner post every few joins along each run (the master's rhythm)


def measure_wall_pieces():
    """Footing size and centre of each main post from its mesh (the footing is off-centre
    on the log)."""
    global POST_HALF
    for nm in POSTS.values():
        foot = [v.co for v in A[nm].data.vertices if v.co.z < 3.0]
        x0, x1 = min(v.x for v in foot), max(v.x for v in foot)
        y0, y1 = min(v.y for v in foot), max(v.y for v in foot)
        POST_FOOT[nm] = ((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0)
    POST_HALF = max(w for _, _, w in POST_FOOT.values()) * POST_S / 2 + JOINT
    print(f"palisade: join step ~{BAY_STEP:.1f}, stake top {SECTION_H:.1f}, post top "
          f"{A['PalisadeMainPost'].dimensions.z * POST_S:.1f} studs (1.6x character = 8.8)")


def _wall_front(rot, mid):
    """Turn a wall piece so its dressed front (-Y) faces the camera side of the wall: the
    inside on the north, east and west, the outside on the south arc, as in the master."""
    front = Vector((math.sin(rot), -math.cos(rot)))
    return rot + math.pi if front.dot(Vector(CAM_XY) - mid) < 0 else rot


def palisade():
    measure_wall_pieces()
    wall = se_curve(WALL, N=4000)
    O = Vector((0, WALL["cy"]))
    ds = 0.25
    S = PIECE_S
    samples = [(s, wall_blocked(wall.at(s))) for s in np.arange(0, wall.length, ds)]
    # forced joins on the south arc: torch posts where the master has the entrance posts,
    # a main post on the axis between the rails
    south_s = [s for s, _ in samples if wall.at(s).y < WALL["cy"] - 0.6 * WALL["ry"]]
    sx_post = None
    for s in south_s:
        p = wall.at(s)
        if p.x < 0 and _pct((p.x, p.y, h(p.x, p.y)))[0] >= SOUTH_FRAME_U:
            sx_post = -p.x
            break
    forced = {}
    for xt, kind in ((-sx_post, "torch"), (0.0, "main"), (sx_post, "torch")):
        forced[min(south_s, key=lambda s_: abs(wall.at(s_).x - xt))] = kind
    # rotate so we start inside a gap
    i0 = next(i for i, (_, b) in enumerate(samples) if b)
    samples = samples[i0:] + samples[:i0]
    runs = []
    cur = None
    prev_gap = samples[0][1]
    for s, b in samples:
        if b is None and cur is None:
            cur = [s, s, prev_gap, None]
        elif b is None:
            cur[1] = s
        elif cur is not None:
            cur[3] = b
            runs.append(cur)
            cur = None
        if b:
            prev_gap = b
    if cur is not None:
        cur[3] = samples[0][1]
        runs.append(cur)

    # superellipse "corners": a torch post on the join nearest each (master)
    corners = []
    for ang in (45, 135, 225, 315):
        a_ = math.radians(ang)
        cc, ss_ = math.cos(a_), math.sin(a_)
        corners.append(Vector((WALL["rx"] * math.copysign(abs(cc) ** (2 / WALL["n"]), cc),
                               WALL["cy"] + WALL["ry"] * math.copysign(abs(ss_) ** (2 / WALL["n"]), ss_))))
    posts, bays = [], []   # posts: [s, kind]; bays: (join index a, join index b, kind)
    south_x = sx_post
    for s0, s1, g0, g1 in runs:
        L = (s1 - s0) % wall.length + ds
        if L < 2 * POST_HALF:
            continue
        # anchor joins: both run ends (a post just clear of the gate / tower / forge) and any
        # forced south-entrance join inside the run; equal steps of ~BAY_STEP between them
        anchors = [(s0 + POST_HALF, None), (s0 + L - POST_HALF, None)]
        for sf, kind in forced.items():
            rel = (sf - s0) % wall.length
            if POST_HALF < rel < L - POST_HALF:
                anchors.append((s0 + rel, kind))
        anchors.sort()
        run = [[anchors[0][0], anchors[0][1] or "main"]]
        for (sa, _), (sb, kb) in zip(anchors, anchors[1:]):
            n = max(1, round((sb - sa) / BAY_STEP))
            run += [[sa + (sb - sa) * k / n, "main"] for k in range(1, n)] + [[sb, kb or "main"]]
        forced_k = {k for k, (s, kind) in enumerate(run) if any(abs(s - (s0 + (sf - s0) % wall.length)) < 0.01
                                                                for sf in forced)}
        # torch + banner flank the Deploy gate; a banner on the next join outside each south torch
        for end, g in ((0, g0), (len(run) - 1, g1)):
            if g == "gate":
                run[end][1] = "torch"
                nb = 1 if end == 0 else len(run) - 2
                if 0 < nb < len(run) - 1 and nb not in forced_k:
                    run[nb][1] = "banner"
        for k in forced_k:
            if run[k][1] == "torch":
                out = k - 1 if wall.at(run[k][0]).x < 0 else k + 1
                if 0 <= out < len(run) and out not in forced_k:
                    run[out][1] = "banner"
        plain = 0
        for k, p in enumerate(run):
            if p[1] != "main" or k in forced_k:
                continue
            if any((wall.at(p[0]) - c).length < BAY_STEP / 2 for c in corners):
                p[1] = "torch"
                continue
            plain += 1
            nbrs = [run[j][1] for j in (k - 1, k + 1) if 0 <= j < len(run)]
            if plain % BANNER_EVERY == 0 and "banner" not in nbrs and 0 < k < len(run) - 1:
                p[1] = "banner"
        base = len(posts)
        posts += run
        for k in range(len(run) - 1):
            ma, mb = wall.at(run[k][0]), wall.at(run[k + 1][0])
            m = wall.at((run[k][0] + run[k + 1][0]) / 2)
            kind = "PalisadeSection"
            south = m.y < WALL["cy"] - 0.6 * WALL["ry"]
            if south and abs(m.x) < south_x:
                kind = "LogRailFence"         # log rails across the south entrance (master)
            elif south and (abs(abs(ma.x) - south_x) < 0.5 or abs(abs(mb.x) - south_x) < 0.5):
                kind = "PalisadeSectionLow"   # low plank bays either side of it (master)
            else:
                u, v = _pct((m.x, m.y, h(m.x, m.y)))
                if 83.0 < u < 95.0 and 74.0 < v < 88.0:
                    kind = "LogRailFence"     # braced rails on the SE stretch by the vault (master)
            bays.append((base + k, base + k + 1, kind))
    count = 0
    pieces_all = []
    for ja, jb, kind in bays:
        a_, b_ = wall.at(posts[ja][0] + POST_IN), wall.at(posts[jb][0] - POST_IN)
        mid, d = (a_ + b_) / 2, b_ - a_
        rot = _wall_front(math.atan2(d.y, d.x), mid)
        count += 1
        rail = kind == "LogRailFence" and mid.y < WALL["cy"] - 0.6 * WALL["ry"] and abs(mid.x) < south_x
        nm_obj = f"Palisade_SouthRail_{count:03d}" if rail else f"Palisade_{count:03d}_{kind.replace('Palisade', '')}"
        sz = SECTION_H / A["PalisadeSection"].dimensions.z * RNG.uniform(0.97, 1.03) if kind == "PalisadeSection" else S
        o = put(kind, mid.x, mid.y, rot, (d.length / BAY, S, sz), "Palisade", nm_obj, zoff=-0.15, keep=0)
        o["wall_joins"] = [ja, jb]
        pieces_all.append((kind, mid, rot))
    for j, (s, kind) in enumerate(posts):
        p, t = wall.at(s), wall.tangent(s)
        nm = POSTS[kind]
        rot = _wall_front(math.atan2(t.y, t.x), p)
        fx, fy, _ = POST_FOOT[nm]
        x, y = local(p.x, p.y, rot, -fx * POST_S, -fy * POST_S)   # footing centred on the wall line
        count += 1
        o = put(nm, x, y, rot, POST_S, "Palisade", f"Palisade_{count:03d}_{nm.replace('Palisade', '')}",
                zoff=-0.15, keep=0)
        o["wall_join"] = j
        KEEP.append((p.x, p.y, 2.8))
        pieces_all.append((nm, p, rot))
    print(f"palisade: {len(bays)} bays, {len(posts)} posts ("
          + ", ".join(f"{k} {sum(1 for _, kk in posts if kk == k)}" for k in POSTS) + "), "
          + ", ".join(f"{k} {sum(1 for *_, kk in bays if kk == k)}" for k in ("PalisadeSection", "PalisadeSectionLow", "LogRailFence")))
    # boulders half buried along the base, inside and out
    bnames = ["LowBoulder", "SplitBoulder", "LongBoulder", "LowBoulder", "SplitBoulder", "TallBoulder"]
    s = 0.0
    side = 1
    while s < wall.length:
        p = wall.at(s)
        if wall_blocked(p) is None:
            t = wall.tangent(s)
            inward = Vector((-t.y, t.x))
            if inward.dot(O - p) < 0:
                inward = -inward
            nm = RNG.choice(bnames)
            sc = (RNG.uniform(0.4, 0.68) if side < 0 else RNG.uniform(0.32, 0.55)) if nm != "TallBoulder" else RNG.uniform(0.3, 0.42)
            # clear the stakes: panel half-depth + the rock's radius
            half = max(A[n].dimensions.y for n in ("PalisadeSection", *POSTS.values())) * PIECE_S * 1.05 / 2
            rad = 0.5 * max(A[nm].dimensions.x, A[nm].dimensions.y) * sc * 0.8
            q = p + inward * (side * (half + rad + 0.5 + RNG.uniform(0, 0.6)))
            if free(q.x, q.y, rad + 0.3):
                put(nm, q.x, q.y, RNG.uniform(0, 6.28), sc, "Palisade", uniq("Palisade_Boulder"),
                    zoff=-0.4, keep=0.7)
        side = -side
        s += RNG.uniform(2.4, 4.0)
    # grass and ferns tucked against the base (standing in for ivy)
    s = 0.0
    while s < wall.length:
        p = wall.at(s)
        if wall_blocked(p) is None:
            t = wall.tangent(s)
            inward = Vector((-t.y, t.x))
            if inward.dot(O - p) < 0:
                inward = -inward
            for off in (RNG.uniform(1.7, 2.5), -RNG.uniform(1.8, 2.6)):
                q = p + inward * off
                if off > 0 and not free(q.x, q.y, 0.3):
                    continue
                nm = RNG.choice(["FernLeafy", "GrassTuftLarge", "FernLeafy", "GrassClumpSmall", "BroadLeafHerb"])
                put(nm, q.x, q.y, RNG.uniform(0, 6.28), RNG.uniform(0.8, 1.2), "Palisade", uniq("Palisade_BaseFern"), keep=0)
        s += RNG.uniform(2.6, 4.2)
    return pieces_all


# ---------------------------------------------------------------------------
# Zones
# ---------------------------------------------------------------------------


RACK = {}


def _rack_geometry():
    """Lower rail (top height, depth) and the peg positions on it, read from the rack mesh."""
    if RACK:
        return RACK
    me = A["WeaponRack"].data
    ups = [(p.center.copy(), p.area) for p in me.polygons if p.normal.z > 0.8]
    rail = max((c for c, a in ups if 0.8 < c.z < 2.4 and a > 0.8), key=lambda c: c.z)
    raw = sorted(c.x for c, a in ups if rail.z + 0.2 < c.z < rail.z + 0.7 and abs(c.y - rail.y) < 0.3 and a > 0.05)
    pegs = []
    for px_ in raw:  # merge the faces of one peg
        if not pegs or px_ - pegs[-1] > 0.3:
            pegs.append(px_)
    gaps = [(a + b) / 2 for a, b in zip(pegs, pegs[1:])]
    if pegs:
        step = (pegs[-1] - pegs[0]) / max(1, len(pegs) - 1)
        gaps = [pegs[0] - step / 2] + gaps + [pegs[-1] + step / 2]
    RACK.update(rail_y=rail.y, rail_z=rail.z, gaps=gaps or [-1.6, 0.0, 1.6])
    print("rack", {k: (round(v, 2) if isinstance(v, float) else [round(g, 2) for g in v]) for k, v in RACK.items()})
    return RACK


BLADED = {"IronAxe", "StoneAxeBasic", "StoneAxeBroadHead", "IronPickaxe", "StonePickaxeDouble", "StoneWarClub",
          "TimberClubBone", "BlacksmithHammer"}


def rack_with_tools(x, y, rot, coll, prefix, tools, z=None):
    """WeaponRack with tools stood in the gaps between the lower-rail pegs, butts resting on
    the rail and shafts leaned back until they touch the upper rail. Every candidate pose is
    tested against the rack and the tools already placed with exact mesh intersection, so
    nothing passes through the rack and nothing floats."""
    rack = put("WeaponRack", x, y, rot, 1.0, coll, f"{prefix}_WeaponRack{uniq(prefix + 'Rack')[-2:]}", z=z)
    g = _rack_geometry()
    near = [q for q in bpy.data.objects if q.type == "MESH" and q is not rack and _audit_kind(q) == "solid"
            and ((q.location.xy - rack.location.xy).length < 9.0 or q.get("lobby_asset") is None)]
    others = [rack] + near  # the rack plus whatever stands near it (stairs, crates, walls)
    order = sorted(g["gaps"], key=lambda gx: -abs(gx))  # outer gaps first, spread out
    used = []
    for tn in tools:
        o = put(tn, x, y, rot, 1.0, coll, f"{prefix}_{tn}{uniq(prefix + tn)[-2:]}", keep=0, z=rack.location.z)
        placed = False
        for gx in order:
            if any(abs(gx - u) < 1.2 for u in used):
                continue
            # butt on the ground in front of the rack, shaft leaned back between the pegs
            # until it rests against the rails
            for dy, spin in [(dy, sp) for dy in (-0.6, -0.7, -0.8, -0.95)
                             for sp in ((math.pi / 2, -math.pi / 2, 0.0) if tn in BLADED else (0.0,))]:
                px, py = local(x, y, rot, gx, g["rail_y"] + dy)
                o.location = (px, py, rack.location.z)
                rest_on(o, rack.location.z)  # same support as the rack (ground or the forge landing)
                best, touched = None, False
                for th in np.arange(0.0, 0.42, 0.02):
                    M = Matrix.Rotation(rot, 3, "Z") @ Matrix.Rotation(-th, 3, "X") @ Matrix.Rotation(spin, 3, "Z")
                    o.rotation_euler = M.to_euler("XYZ")
                    if hits(o, others):
                        touched = True
                        break
                    best = M
                if best is not None and touched:
                    o.rotation_euler = best.to_euler("XYZ")
                    placed = True
                    break
            if placed:
                used.append(gx)
                others.append(o)
                break
        if not placed:  # no clean pose: leave it out rather than clip or float
            bpy.data.objects.remove(o, do_unlink=True)
            STATS["instances"] -= 1
            STATS["tris"] -= tris_of(A[tn])


def lay_on(base_obj, tn, lx, ly, yaw, coll, name, sc=1.0, others=(), top=8.0):
    """Lay a tool flat on a table/bench top: rotated onto its side, then dropped until its
    lowest vertex sits on the surface measured under it (the first surface below `top`,
    unscaled local height, so a stall counter is found under its canopy)."""
    bs = base_obj.scale[0]   # (lx, ly) are in the base asset's unscaled local studs
    tx, ty = local(base_obj.location.x, base_obj.location.y, base_obj.rotation_euler.z, lx * bs, ly * bs)
    surf = on_top(base_obj["lobby_asset"], base_obj, lx, ly, top=top)
    o = put(tn, tx, ty, yaw, sc, coll, name, z=surf + 2.0, rx=math.pi / 2, keep=0)
    rest_on(o, surf + 1.5)
    return settle(o, [base_obj, *others], drop=3.0)


def on_top(base_asset, base_obj, lx, ly, top=8.0):
    """World z of the surface of a placed object at its local (lx, ly) (unscaled)."""
    s = base_obj.scale[2]
    return base_obj.location.z + floor_z(base_asset, lx, ly, top=top) * s


# ---------------------------------------------------------------------------
# NPC stand spots: an Empty NPC_<role> per character, a clear cylinder 3 studs across and
# 6 tall reserved round it (KEEP disc for dressing; audited in audit_npc_clearance), and a
# grey 5.5-stud capsule placeholder in "NPC Placeholders" so the spot reads in renders.
# ---------------------------------------------------------------------------

NPC_R, NPC_H = 1.5, 6.0
NPC_SPOTS = {}   # role -> (x, y, z, yaw)


def npc_spot(role, x, y, yaw=0.0, z=None):
    NPC_SPOTS[role] = (x, y, h(x, y) if z is None else z, yaw)
    KEEP.append((x, y, NPC_R + 0.7))


def build_npcs():
    spots = bpy.data.collections.new("NPC Spots")
    holders = bpy.data.collections.new("NPC Placeholders")
    C["Lobby"].children.link(spots)
    C["Lobby"].children.link(holders)
    C["NPC Spots"], C["NPC Placeholders"] = spots, holders
    for role, (x, y, z, yaw) in NPC_SPOTS.items():
        e = bpy.data.objects.new(f"NPC_{role}", None)
        e.empty_display_type = "SINGLE_ARROW"   # arrow up; the placeholder's nose shows the facing
        e.empty_display_size = 2.0
        e.location = (x, y, z)
        e.rotation_euler = (0, 0, yaw)
        e["npc_role"] = role
        e["clear_radius"] = NPC_R
        e["clear_height"] = NPC_H
        spots.objects.link(e)
        a = fk.Asset(f"NPCPlaceholder_{role}", "NPC", seed=SEED + len(role), tint_var=0.0)
        a.cyl(1.0, 1.0, 3.5, sides=12, loc=(0, 0, 1.0), mat="stone_light")
        a.ico(1.0, loc=(0, 0, 1.0), mat="stone_light", subdiv=2)
        a.ico(1.0, loc=(0, 0, 4.5), mat="stone_light", subdiv=2)
        a.box((0.45, 0.5, 0.35), loc=(0, -0.9, 4.55), mat="stone_dark")   # nose: the facing (-Y)
        o = own(a.finish(collection=holders, mark_asset=False, origin="NONE"))
        o.location = (x, y, z + 0.02)
        o.rotation_euler = (0, 0, yaw)
        o["npc_role"] = role
    print(f"npcs: {len(NPC_SPOTS)} spots " + ", ".join(f"{r} ({v[0]:.1f}, {v[1]:.1f})" for r, v in NPC_SPOTS.items()))


def zone_gate():
    gy = WALL["cy"] + WALL["ry"]   # on the wall line
    put("DeployGate", 0, gy, 0.0, WALL_S, "DeployGate", "DeployGate", zoff=-0.1)
    for sx, side in ((-1, "W"), (1, "E")):
        put("TorchPost", 9.5 * sx, gy - 8.0, 0.0, 1.0, "DeployGate", f"DeployGate_TorchPost_{side}")
    build_stepping_stones()


def zone_plaza():
    fire = put("Campfire", 0, 0, 0.3, 1.5, "Plaza", "Plaza_Campfire")
    ring_r = 0.5 * max(A["Campfire"].dimensions.x, A["Campfire"].dimensions.y) * 1.5
    bench_r = max(12.5 * LS, ring_r + A["LogBench"].dimensions.y * 1.4 / 2 + 5.0)
    for i in range(6):
        a = math.radians(i * 60 + 2)
        x, y = bench_r * math.cos(a), bench_r * math.sin(a)
        # thicker logs: 1.4x in diameter, same length
        put("LogBench", x, y, face_to(x, y, 0, 0), (1.0, 1.4, 1.4), "Plaza", f"Plaza_LogBench_{i + 1}")
    for i, (x, y) in enumerate(_S([(-15, 10), (-16, -14), (14, 13), (14, -14), (-7.5, -24), (7.5, -24), (-7, 20)])):
        put("TorchPost", x, y, RNG.uniform(0, 6), 1.0, "Plaza", f"Plaza_TorchPost_{i + 1}")
    put("Stump", -8.0 * LS, -17.5 * LS, 0.4, 1.0, "Plaza", "Plaza_Stump_1")


# Upright rune stelae beside the totem, centred on the master's two big stones (the tall
# one left of the totem, the other right of it by the wall). (master key, height, width)
STELAE = (("Rune stone L", 7.5, 5.0), ("Rune stone R", 9.5, 4.4))
STELA_T = 1.25   # thickness scale of the slab


def frame_ground(key, z_above=0.0, it=3):
    """Ground (x, y) whose point `z_above` studs over the plateau shows at the frame target."""
    t = MASTER.get(key) or FRAME_EXTRA[key]
    x, y = unproject(*t, z_above)
    for _ in range(it):
        x, y = unproject(*t, h(x, y) + z_above)
    return x, y


def stela_xy():
    return [frame_ground(key, 0.55 + height / 2) for key, height, width in STELAE]


def zone_totem():
    tx, ty, rot, s = TOTEM["x"], TOTEM["y"], TOTEM["rot"], TOTEM["s"]
    # Front (-Y) square to the main camera, swung 20% toward the bonfire (face_view), so the
    # face, beak and diamond read head-on as in the reference.
    put("EldersTotemTall", tx, ty, rot, s, "EldersTotem", "EldersTotem")
    # Standing rune stelae. The ElongatedRuneStone slab (8 x 5 x 1.6, glyph carved in its top
    # +Z face, glyph "up" along +Y) is turned up with rx = +90 deg: local +Y (glyph up) becomes
    # world +Z and the carved face looks along -Y, the front, which face_view() turns to the
    # camera. A non-uniform scale makes each stone taller than wide; it stands truly vertical
    # on a low stone footing.
    d = A["ElongatedRuneStone"].dimensions
    t = d.z * STELA_T
    foot = fk.Asset("EldersTotem_StelaFootings", "Ground", seed=SEED + 15)
    stelae = []
    for (x, y), (_key, height, width) in zip(stela_xy(), STELAE):
        rz = face_view(x, y)
        fx, fy = local(x, y, rz, 0.0, -t / 2)       # the slab spans local y 0..-t after the turn
        g = min(h(*local(fx, fy, rz, u, v)) for u in (-width / 2 - 0.5, 0, width / 2 + 0.5) for v in (-t / 2 - 0.7, t / 2 + 0.7))
        foot.stone_block((width + 1.0, t + 1.4, 0.9), loc=(fx, fy, g + 0.1), rot=(0, 0, rz),
                         mat="stone_dark", jitter=0.0)
        stelae.append((x, y, rz, (width / d.x, height / d.y, STELA_T), g + 0.55, height))
    own(foot.finish(collection=C["EldersTotem"], mark_asset=False, origin="NONE"))
    for i, (x, y, rz, sc, fz, height) in enumerate(stelae):
        st = put("ElongatedRuneStone", x, y, rz, sc, "EldersTotem", f"EldersTotem_RuneStela_{i + 1}",
                 rx=math.pi / 2, z=fz + height / 2, keep=0)
        rest_on(st, fz)  # stands on the footing top, not sunk into it
        KEEP.append((x, y, 0.5 * sc[0] * d.x + 0.8))
    # fire bowls either side of the totem where the master has them: one in front of the
    # left stone, one between the totem and the right stone
    ob = bpy.data.objects
    near = [ob["EldersTotem"], ob["EldersTotem_StelaFootings"]] + [ob[f"EldersTotem_RuneStela_{i + 1}"] for i in range(len(STELAE))]
    for i, key in enumerate(("Brazier L", "Brazier R")):
        x, y = frame_ground(key, A["StoneBrazier"].dimensions.z / 2)
        near.append(put_clear("StoneBrazier", x, y, rot, 1.0, "EldersTotem", f"EldersTotem_Brazier_{i + 1}", near))
    x, y = totem_local(-6.0, -9.0)
    put_clear("ClayStoragePot", x, y, rot, 0.9, "EldersTotem", "EldersTotem_Pot_1", near)
    # the elder stands in front of the totem, toward the plaza and the quest board
    ex, ey = frame_ground("Elder", 2.75)
    npc_spot("Elder", ex, ey, yaw=face_view(ex, ey, w_plaza=0.5))
    # quest board, squared to the viewer like the totem, a torch at its left end and the
    # quest giver beside it (the board front stays free for readers)
    qx, qy, qr = QUEST["x"], QUEST["y"], QUEST["rot"]
    put("QuestBoard", qx, qy, qr, QUEST["s"], "EldersTotem", "EldersTotem_QuestBoard")
    npc_spot("QuestGiver", *quest_local(7.9, -2.2), yaw=qr)
    put("TorchPost", *quest_local(-6.6, 1.4), 0.0, 1.0, "EldersTotem", "EldersTotem_TorchPost")
    put("Barrel", *quest_local(10.8, 1.6), qr, 1.0, "EldersTotem", "EldersTotem_Barrel_1")
    put("SupplyCrate", *quest_local(12.4, -1.9), qr, 0.9, "EldersTotem", "EldersTotem_Crate_1")
    # the big broadleaf behind and left of the totem, outside the wall (master)
    x, y = frame_ground("Elder tree")
    while se_F(x, y, WALL) < 1.25:
        x, y = x - 0.4, y + 0.6
    put("BroadleafTreeWideOld", x, y, 0.6, 1.0, "EldersTotem", "EldersTotem_ElderTree")


def build_forge_stairs(cx, cy, rot, front):
    """Wide stone landing in front of the furnace mouth and four steps down to the yard.
    `front` is the forge's front face (local y, scaled); the landing starts there."""
    a = fk.Asset("Forge_StoneStairs", "Ground", seed=SEED + 12)
    rng = random.Random(SEED + 12)
    g = h(cx, cy)  # one flat base so the landing is a single level for the props on it
    f = front - 0.1  # just in front of the forge's front face
    tiers = [(f, f - 4.8, 1.45, 34.0), (f - 4.8, f - 7.0, 1.1, 34.0), (f - 7.0, f - 9.2, 0.75, 31.0),
             (f - 9.2, f - 11.4, 0.4, 28.0)]
    for y0, y1, top, width in tiers:
        n = int(width / 3.4)
        for i in range(n):
            lx = -width / 2 + (i + 0.5) * width / n + rng.uniform(-0.1, 0.1)
            ly = (y0 + y1) / 2
            x, y = local(cx, cy, rot, lx, ly)
            hz = top + 0.6
            a.stone_block((width / n - 0.1, abs(y1 - y0) - 0.08, hz), loc=(x, y, g + top - hz / 2),
                          rot=(0, 0, rot + rng.uniform(-0.03, 0.03)), jitter=0.0,
                          mat=rng.choice(["stone", "stone_light", "stone", "stone_dark"]))
    own(a.finish(collection=C["Forge"], mark_asset=False, origin="NONE"))
    return f, 1.45


def zone_forge():
    fx, fy, rot, s = FORGE["x"], FORGE["y"], FORGE["rot"], FORGE["s"]
    forge = put("AncestralForge", fx, fy, rot, s, "Forge", "Forge_AncestralForge", keep=0)
    KEEP.append((fx, fy, 22))
    KEEP.append(local(fx, fy, rot, -14, 0) + (12,))
    KEEP.append(local(fx, fy, rot, 14, 0) + (12,))
    front = min(v[1] for v in A["AncestralForge"].bound_box) * s
    f0, top = build_forge_stairs(fx, fy, rot, front)
    gz = h(fx, fy)

    def L(lx, ly):
        return local(fx, fy, rot, lx, ly)

    # The final forge mesh carries its own deep-orange fire in the arch; add the missing
    # forge_fire socket on its fire bed so the light spills over the stairs.
    me = A["AncestralForge"].data
    bed = [p.center for p in me.polygons
           if me.materials[p.material_index] and me.materials[p.material_index].name in ("FB_ember", "FB_fire_outer")
           and p.center.z < 3.0 and abs(p.center.x) < 4.5]
    bc = (sum(bed, Vector()) / len(bed)) if bed else Vector((0, 0.5, 0.8))
    if vfx is not None and not any(c.get("vfx_kind") == "forge_fire" for c in forge.children):
        e = vfx.add(forge, "forge_fire", (bc.x, bc.y, bc.z + 0.3), scale=s)
        e.name = "VFX_forge_fire_Forge_AncestralForge"
        STATS["sockets"] += 1
        STATS["added_sockets"] += 1
    land = gz + top  # landing height (flat stone, so it is the support for everything on it)
    x, y = L(-0.5, f0 - 2.6)
    put("AnvilLarge", x, y, rot + 0.2, 1.4, "Forge", "Forge_Anvil", z=land)
    npc_spot("Blacksmith", *L(5.0, f0 - 3.2), yaw=rot + 0.6, z=land)   # by the anvil, on the landing
    x, y = L(-11.5, f0 - 2.4)
    bench = put("CraftingWorkbench", x, y, rot - 0.05, 1.0, "Forge", "Forge_Workbench", z=land)
    on_bench = []
    for tn, dx, dy, rz in (("BlacksmithHammer", -1.8, -0.4, 1.45), ("StoneKnife", 1.0, 0.5, 1.75)):
        on_bench.append(lay_on(bench, tn, dx, dy, rot + rz, "Forge", f"Forge_Bench{tn}", others=on_bench))
    x, y = L(10.5, f0 - 2.6)
    rack_with_tools(x, y, rot, "Forge", "Forge", ["IronAxe", "StonePickaxeDouble", "IronSpear", "StoneAxeBroadHead"],
                    z=land)
    x, y = L(21.5, f0 - 3.5)
    put("SmeltingFurnace", x, y, rot - 0.3, 1.0, "Forge", "Forge_SmeltingFurnace")
    for i, (lx, ly) in enumerate([(22.5, f0 - 10.0), (25.5, f0 - 8.5)]):
        x, y = L(lx, ly)
        put("Barrel", x, y, RNG.uniform(0, 6), 1.0, "Forge", f"Forge_Barrel_{i + 1}")


def zone_vault():
    vx, vy, rot, s = VAULT["x"], VAULT["y"], VAULT["rot"], VAULT["s"]
    hall = put("VaultHall", vx, vy, rot, s, "VaultHall", "VaultHall", keep=0)
    KEEP.append((vx, vy, 17))

    def L(lx, ly):  # unscaled vault-local -> world
        return local(vx, vy, rot, lx * s, ly * s)

    # chests in a row just inside the open gable front, as in the master. Further back
    # (local y > ~0) the roof hides them from LobbyCam; y = -3 is clear of it.
    for i, (nm, lx, ly, dr, cs) in enumerate([("LargeChest", -4.2, -3.0, 0.06, 1.1),
                                              ("OpenChest", 0.3, -2.6, -0.04, 1.1),
                                              ("LargeChest", 4.4, -3.0, -0.04, 1.1)]):
        x, y = L(lx, ly)
        put(nm, x, y, rot + dr, cs, "VaultHall", f"VaultHall_{nm}_{i + 1}",
            z=on_top("VaultHall", hall, lx, ly, top=5.0), keep=0)
    # warm lantern glow inside the open hall so the chests read (preview light only)
    x, y = L(0.4, 0.0)
    lt = bpy.data.objects.new("VaultHall_InteriorGlow", bpy.data.lights.new("VaultHall_InteriorGlow", "POINT"))
    lt.data.energy = 1800
    lt.data.color = fk.hex_rgb("#FFB066")
    lt.data.shadow_soft_size = 2.0
    lt.location = (x, y, hall.location.z + 7.0)
    C["VaultHall"].objects.link(lt)
    x, y = L(0.4, -6.3)  # in front of the chests, toward the entrance
    build_rug(x, y, on_top("VaultHall", hall, 0.4, -6.3, top=5.0) + 0.01, rot, size=(7.0, 4.2))
    front = min(v[1] for v in A["VaultHall"].bound_box)
    x, y = L(-6.5, front - 3.2)
    put("LedgerLectern", x, y, rot + 0.35, 1.0, "VaultHall", "VaultHall_LedgerLectern")
    x, y = L(-12.0, front - 2.6)
    rack_with_tools(x, y, rot + 0.15, "VaultHall", "VaultHall", ["IronSpear", "StoneSpear", "WoodenSpear", "IronShortSword"])
    x, y = L(9.0, front - 2.4)
    rack_with_tools(x, y, rot - 0.15, "VaultHall", "VaultHall", ["StoneWarClub", "TimberClubBone", "WoodenBowSimple", "WoodenBowLaminated"])
    for i, lx in enumerate((-4.0, 4.6)):
        x, y = L(lx, front - 2.4)
        put("TorchPost", x, y, 0.0, 1.0, "VaultHall", f"VaultHall_TorchPost_{i + 1}")
    npc_spot("VaultKeeper", *L(-1.4, front - 1.7), yaw=rot)   # at the entrance, beside the rug
    side = max(v[0] for v in A["VaultHall"].bound_box)
    x, y = L(-side - 2.4, 2.0)
    put("StorageCabinet", x, y, rot - 0.4, 1.0, "VaultHall", "VaultHall_StorageCabinet")
    x, y = L(-side - 2.0, -4.0)
    put("Barrel", x, y, 0.4, 1.0, "VaultHall", "VaultHall_Barrel_1")
    x, y = L(-side - 2.2, -7.2)
    put("SupplyCrate", x, y, rot, 0.9, "VaultHall", "VaultHall_Crate_1")


def stall_counter(nm):
    """Local y and height of a market stall's counter top (front-most surface 2.5-4.6 high)."""
    bb = A[nm].bound_box
    y0 = min(v[1] for v in bb)
    ly = y0
    while ly < 0:
        z = floor_z(nm, 0.2, ly, top=5.0)
        if 2.5 < z < 4.6:
            return ly + 0.35, z
        ly += 0.2
    return None, None


def _goods_on_table(bench, wr):
    for tn, dx, sc in (("WovenBasket", -1.6, 0.65), ("ClayStoragePot", 1.6, 0.5), ("StoneKnife", 0.2, 1.0)):
        if tn == "StoneKnife":   # along the table edge, behind the basket and the pot
            lay_on(bench, tn, -0.4, -1.1, wr + math.pi / 2, "Market", uniq("Market_Table" + tn))
            continue
        tx, ty = local(bench.location.x, bench.location.y, wr, dx, 0)
        surf = on_top("CraftingWorkbench", bench, dx, 0)
        o = put(tn, tx, ty, wr, sc, "Market", uniq("Market_Table" + tn), z=surf + 1.5, keep=0)
        settle(o, [bench], drop=3.0)


def build_sacks(name, x, y, rot, n, seed):
    """A small heap of tied grain sacks (built here: the kit has none)."""
    a = fk.Asset(name, "Prop", seed=seed)
    rng = random.Random(seed)
    for k in range(n):
        lx, ly = (k - (n - 1) / 2) * 1.9, rng.uniform(-0.3, 0.3)
        hgt = rng.uniform(2.2, 2.6)
        a.rock((1.9, 1.7, hgt), loc=(lx, ly, hgt / 2 - 0.05), rot=(0, 0, rng.uniform(-0.4, 0.4)),
               mat=rng.choice(["wicker", "parchment", "wicker"]), subdiv=2, rough=0.06, facets=0, sink=0.0)
        a.torus(0.42, 0.11, loc=(lx, ly, hgt - 0.2), mat="rope", seg=10, rseg=4)
        a.cyl(0.38, 0.16, 0.45, sides=7, loc=(lx, ly, hgt - 0.08), mat="wicker")
    o = a.finish(collection=C["Market"], mark_asset=False, origin="BOTTOM")
    o.location = (x, y, h(x, y) - 0.05)
    o.rotation_euler = (0, 0, rot)
    return own(o)


def _rect_circle_gap(rect, x, y, r):
    x0, y0, rot, hw, hd = rect
    c, s = math.cos(-rot), math.sin(-rot)
    u, v = c * (x - x0) - s * (y - y0), s * (x - x0) + c * (y - y0)
    du, dv = max(0.0, abs(u) - hw), max(0.0, abs(v) - hd)
    return math.hypot(du, dv) - r


def dress_market_stacks(stalls):
    """Busy master-style market: stacked crates, barrels and sack heaps beside and behind
    every stall. A spot is used only if it keeps every other stall MARKET_GAP away (the
    passages stay 6 studs), stays out of all customer lanes, clear of the NPC spots and the
    wall line, and its mesh touches nothing already placed (exact test)."""
    wd = wall_dist_fn()
    rects = [(st[1], st[2], st[3], st[6], st[7]) for st in stalls]
    solids = [o for o in bpy.data.objects if o.type == "MESH" and _audit_kind(o) == "solid"
              and (o.location.xy - Vector(MARKET_LABEL)).length < 45]
    placed = 0

    def ok_spot(i, x, y, r):
        if in_lane(x, y, r) or wd(x, y) < r + 3.2:
            return False
        gaps = [_rect_circle_gap(rc, x, y, r) for rc in rects]
        # never in a passage between two stalls (it would narrow the 6-stud gap), never
        # touching a stall, and beside another stall than its own only with a full gap
        if min(gaps) < 0.3 or sum(1 for g in gaps if g < MARKET_GAP) >= 2:
            return False
        if i >= 0 and any(g < MARKET_GAP for j, g in enumerate(gaps) if j != i):
            return False
        return all(math.hypot(x - nx, y - ny) > NPC_R + r + 0.3 for nx, ny, _, _ in NPC_SPOTS.values())

    def try_put(objs_fn):
        made = objs_fn()
        if any(hits(o, solids) for o in made):
            for o in made:
                if o.get("lobby_asset"):
                    STATS["instances"] -= 1
                    STATS["tris"] -= tris_of(A[o["lobby_asset"]])
                else:
                    STATS["own_tris"] -= o.get("tris", 0)
                bpy.data.objects.remove(o, do_unlink=True)
            return False
        solids.extend(made)
        return True

    for i, (nm, x, y, rot, ss, f, hw, hd) in enumerate(stalls):
        # candidate spots in stall-local studs: beside each end (behind the counter line)
        # and along the back; (lx, ly, what)
        cands = []
        for side in (1, -1):
            cands += [(side * (hw + 2.0), -hd + 1.8, "stack"), (side * (hw + 2.4), hd - 1.4, "barrels"),
                      (side * (hw + 2.2), 0.4, "sacks"), (side * (hw + 2.2), -hd + 5.6, "sacks")]
        cands += [(-hw * 0.6, hd + 2.3, "sacks"), (hw * 0.6, hd + 2.3, "stack"), (0.0, hd + 2.4, "barrels"),
                  (-hw * 0.6, hd + 5.6, "stack"), (hw * 0.6, hd + 5.4, "barrels")]
        for lx, ly, what in cands:
            px, py = local(x, y, rot, lx, ly)
            r = {"stack": 1.8, "barrels": 2.6, "sacks": 2.9}[what]
            if not ok_spot(i, px, py, r):
                continue
            yaw = rot + RNG.uniform(-0.25, 0.25)
            if what == "stack":
                def mk(px=px, py=py, yaw=yaw):
                    c1 = put("SupplyCrate", px, py, yaw, 0.9, "Market", uniq("Market_StackCrate"), keep=1.0)
                    c2 = put("SupplyCrate", px, py, yaw + 0.3, 0.75, "Market", uniq("Market_StackCrate"),
                             z=c1.location.z + A["SupplyCrate"].dimensions.z * 0.9 + 0.01, keep=0)
                    b = put("WovenBasket", px, py, yaw, 0.55, "Market", uniq("Market_StackBasket"),
                            z=c2.location.z + A["SupplyCrate"].dimensions.z * 0.75 + 0.01, keep=0)
                    return [c1, c2, b]
            elif what == "barrels":
                def mk(px=px, py=py, yaw=yaw):
                    b1 = put("Barrel", *local(px, py, yaw, -1.4, 0.0), yaw, 0.85, "Market", uniq("Market_StackBarrel"), keep=1.0)
                    b2 = put("Barrel", *local(px, py, yaw, 1.45, 0.25), yaw, 0.8, "Market", uniq("Market_StackBarrel"), keep=1.0)
                    return [b1, b2]
            else:
                def mk(px=px, py=py, yaw=yaw, k=placed):
                    o = build_sacks(f"Market_Sacks_{i + 1}_{k}", px, py, yaw, 2 + (k % 2), SEED + 300 + 7 * i + k)
                    KEEP.append((px, py, 2.0))
                    return [o]
            if try_put(mk):
                placed += 1
    # then single goods packed round each stall's sides and back (every free 2.6 studs):
    # barrels, crates, pots, baskets on crates; the front stays open for the lane
    small = [("Barrel", 0.85, 1.45), ("SupplyCrate", 0.85, 1.55), ("ClayStoragePot", 0.75, 1.1),
             ("crate+basket", 0.8, 1.5), ("Barrel", 0.8, 1.35), ("WovenBasket", 0.7, 1.1)]
    singles = 0
    for i, (nm, x, y, rot, ss, f, hw, hd) in enumerate(stalls):
        k = i
        spots = [(sx * (hw + 0.6 + 1.5), ly) for sx in (1, -1) for ly in np.arange(hd - 1.4, -hd, -2.6)]
        spots += [(lx, hd + 0.6 + 1.5) for lx in np.arange(-hw + 1.4, hw, 2.6)]
        for lx, ly in spots:
            an, sc_, r = small[k % len(small)]
            px, py = local(x, y, rot, lx, ly)
            if not ok_spot(i, px, py, r):
                continue
            yaw = rot + RNG.uniform(-0.5, 0.5)

            def mk(an=an, sc_=sc_, px=px, py=py, yaw=yaw):
                if an == "crate+basket":
                    c = put("SupplyCrate", px, py, yaw, sc_, "Market", uniq("Market_GoodsCrate"), keep=1.0)
                    b = put("WovenBasket", px, py, yaw + 0.4, 0.55, "Market", uniq("Market_GoodsBasket"),
                            z=c.location.z + A["SupplyCrate"].dimensions.z * sc_ + 0.01, keep=0)
                    return [c, b]
                return [put(an, px, py, yaw, sc_, "Market", uniq("Market_Goods" + an), keep=1.0)]
            if try_put(mk):
                singles += 1
                k += 1
    placed += singles
    # a goods bench and sack heaps out in the market square, wherever they fit between the
    # lanes and passages (master: the square is busy with goods)
    benches = sq_sacks = 0
    grid = [(dx, dy) for dx in range(-14, 15, 2) for dy in range(-12, 13, 2)]
    grid.sort(key=lambda d: math.hypot(*d))
    for dx, dy in grid:
        px, py = MARKET_LABEL[0] + dx, MARKET_LABEL[1] + dy
        if benches == 0 and ok_spot(-1, px, py, 3.3):
            yaw = face_view(px, py, w_plaza=0.3)

            def mk(px=px, py=py, yaw=yaw):
                return [put("CraftingWorkbench", px, py, yaw, 1.0, "Market", "Market_SquareBench")]
            if try_put(mk):
                _goods_on_table(bpy.data.objects["Market_SquareBench"], yaw)
                benches = 1
                continue
        hug = min(_rect_circle_gap(rc, px, py, 2.2) for rc in rects) < 3.0   # against a stall, not out in the grass
        if benches and sq_sacks < 4 and hug and ok_spot(-1, px, py, 2.2):
            yaw = RNG.uniform(0, 6.28)

            def mk(px=px, py=py, yaw=yaw, k=placed):
                return [build_sacks(f"Market_Sacks_sq_{k}", px, py, yaw, 2, SEED + 400 + k)]
            if try_put(mk):
                KEEP.append((px, py, 2.2))
                placed += 1
                sq_sacks += 1
    print(f"market dressing: {placed} stacks / barrel pairs / sack heaps beside the stalls, {benches} square bench")


def zone_market():
    """Four stalls round the market square (see plan_layout): every prop is squared to its
    stall (yaw = stall yaw), nothing stands in the customer lane in front of the counters,
    the 6+ stud gaps between stalls stay passable, and each merchant has a clear spot
    inside the stall behind the counter."""
    stalls = market_stalls()
    for ln in market_lanes():
        lane = Curve(ln)
        s = 0.0
        while s <= lane.length:   # keep the customer lanes clear of goods and plants
            p = lane.at(s)
            KEEP.append((p.x, p.y, MARKET_LANE / 2 + 0.75))
            s += 2.0
    for i, (nm, x, y, rot, ss, f, hw, hd) in enumerate(stalls):
        stall = put(nm, x, y, rot, ss, "Market", f"Market_{nm}_{i + 1}", keep=0)
        stall["market_role"] = MARKET_ROLES[i]
        KEEP.append((x, y, hw + 0.5))

        def L(lx, ly, x=x, y=y, rot=rot):
            return local(x, y, rot, lx, ly)

        mx, my = merchant_spot(stall, nm, ss)
        npc_spot(f"Merchant_{i + 1}", *L(mx * ss, my * ss), yaw=rot,
                 z=stall.location.z + floor_z(nm, mx, my, top=2.0) * ss)
        # stock behind the two big stalls: a crate (with a basket on its lid) and a barrel
        if i < 2:   # (each skipped if it would stand in a neighbour's customer lane)
            cx_, cy_ = L(-hw + 2.2, hd + 2.0)
            if not in_lane(cx_, cy_, 1.7):
                crate = put("SupplyCrate", cx_, cy_, rot, 0.95, "Market", uniq("Market_SupplyCrate"), keep=1.0)
                put("WovenBasket", cx_, cy_, rot, 0.7, "Market", uniq("Market_WovenBasket"),
                    z=crate.location.z + A["SupplyCrate"].dimensions.z * crate.scale[2], keep=0)
            if not in_lane(*L(hw - 2.2, hd + 2.0), 1.6):
                put("Barrel", *L(hw - 2.2, hd + 2.0), rot, 0.95, "Market", uniq("Market_Barrel"), keep=1.0)
        # one pot or basket at the -X end, in the back half of the gap
        if i < 2:
            pn = ("ClayStoragePot", "WovenBasket")[i]
            r = 0.5 * A[pn].dimensions.x * 0.9
            if not in_lane(*L(-(hw + r + 0.4), hd - r - 0.3), r):
                put(pn, *L(-(hw + r + 0.4), hd - r - 0.3), rot, 0.9, "Market", uniq("Market_" + pn), keep=1.0)
        cy, cz = stall_counter(nm)  # goods packed along the whole counter (master)
        if cy is not None:
            hw_u = _STALL_BB[nm][0]
            goods = ["ClayStoragePot", "WovenBasket", "tool", "ClayStoragePot", "WovenBasket", "ClayStoragePot", "tool"]
            lx, j, on_counter = -hw_u + 1.3, i, []
            while lx < hw_u - 1.2:
                z = floor_z(nm, lx, cy, top=5.0)
                gn = goods[j % len(goods)]
                j += 1
                if 2.5 < z < 4.6:
                    if gn == "tool":
                        tn = ("StoneKnife", "StoneAxeBasic", "IronShortSword", "StoneKnife")[(i + j) % 4]
                        o = lay_on(stall, tn, lx, cy - 0.2, rot + math.pi / 2, "Market",
                                   uniq("Market_Counter" + tn), sc=0.8, others=on_counter, top=z + 0.6)
                    else:
                        px, py = L(lx * ss, cy * ss)
                        sc_ = 0.45 if gn == "ClayStoragePot" else 0.5
                        o = put(gn, px, py, rot + RNG.uniform(-0.4, 0.4), sc_, "Market",
                                uniq("Market_Counter" + gn), z=stall.location.z + z * ss + 0.01, keep=0)
                    if hits(o, [stall] + on_counter):   # leave out anything that would clip the stall
                        STATS["instances"] -= 1
                        STATS["tris"] -= tris_of(A[o["lobby_asset"]])
                        bpy.data.objects.remove(o, do_unlink=True)
                    else:
                        on_counter.append(o)
                lx += 1.75 if gn != "tool" else 2.3
    # the master's red banner on a post at the front-left corner of the banner stall
    nm, x, y, rot, ss, f, hw, hd = stalls[1]
    put("PalisadeMainPostBanner", *local(x, y, rot, -hw - 3.2, -hd + 3.0), rot, 0.8, "Market", "Market_BannerPost")
    # a second goods table beyond the banner stall's -X end, squared to it, clear of the
    # stalls, the SW tower yard and the lanes
    solid = [o for o in list(C["Market"].objects) + list(C["Watchtowers"].objects) if o.type == "MESH"]
    wdist = wall_dist_fn()
    for dx in (0.0, 1.5, -1.5, 3.0, -3.0, 4.5):
        tx_, ty_ = local(x, y, rot, -hw - 6.8 + dx, 3.2)
        if in_lane(tx_, ty_, 3.1) or wdist(tx_, ty_) < 3.2 + 3.5:
            continue
        bench = put("CraftingWorkbench", tx_, ty_, rot, 1.0, "Market", "Market_GoodsTable_2")
        if hits(bench, solid):
            bpy.data.objects.remove(bench, do_unlink=True)
            STATS["instances"] -= 1
            STATS["tris"] -= tris_of(A["CraftingWorkbench"])
            KEEP.pop()
            continue
        _goods_on_table(bench, rot)
        break
    # goods spilling from the stalls toward the plaza (master): a barrel pair, and a goods
    # table with a tool rack beside it, squared to the camera view and kept out of the
    # customer lanes.
    nm, x, y, rot, ss, f, hw, hd = stalls[2]   # barrel pair beside the red stall, behind its counter line
    for k, (lx, ly) in enumerate(((hw + 2.4, 0.4), (hw + 2.9, 3.6))):
        put("Barrel", *local(x, y, rot, lx, ly), rot, 1.0, "Market", f"Market_YardBarrel_{k + 1}")
    wx, wy = frame_ground("Market table", 1.6)
    wr = face_view(wx, wy, w_plaza=0.5)
    bench = put("CraftingWorkbench", wx, wy, wr, 1.0, "Market", "Market_GoodsTable_1")
    _goods_on_table(bench, wr)
    rx_, ry_ = local(wx, wy, wr, 6.2, 1.0)
    rack_with_tools(rx_, ry_, wr, "Market", "Market",
                    ["StoneAxeBasic", "StoneSpear", "WoodenBowSimple", "StonePickaxeDouble"])
    dress_market_stacks(stalls)
    # lane check: nothing but plants may stand in a customer lane
    lanes = market_lanes()
    for o in C["Market"].objects:
        if o.type != "MESH" or not o.get("lobby_asset") or o.get("market_role"):
            continue
        r = 0.5 * max(A[o["lobby_asset"]].dimensions.x * o.scale[0], A[o["lobby_asset"]].dimensions.y * o.scale[1])
        for k, ln in enumerate(lanes):
            d = seg_dist(ln, o.location.x, o.location.y) - r
            if d < MARKET_LANE / 2 and not o.name.startswith("Market_Counter"):
                print(f"MARKET LANE BLOCKED: {o.name} {d:.1f} studs from lane {k + 1} centre")


def zone_arrival():
    ax, ay = ARRIVAL["x"], ARRIVAL["y"]
    # the concentric-diamond slab lies flat and square to the camera
    put("LargeRuneStone", ax, ay, 0.0, 1.3, "ArrivalStones", "ArrivalStones_LargeRuneStone", zoff=-0.45)
    for i in range(8):
        a = math.radians(i * 45 + 22.5)
        x, y = ax + 11.8 * LS * math.cos(a), ay + 9.0 * LS * math.sin(a)
        nm = "SteppingStone" if i % 2 == 0 else "ElongatedRuneStone"
        sc = RNG.uniform(0.6, 0.72) if nm == "SteppingStone" else RNG.uniform(0.5, 0.58)
        # rune slabs lie flat with the glyph's up (local +Y) pointing straight away from the
        # camera, so the carving reads upright in the main view
        rz = face_to(x, y, *CAM_XY) if nm == "ElongatedRuneStone" else a + math.pi / 2
        put(nm, x, y, rz, sc, "ArrivalStones", f"ArrivalStones_RingStone_{i + 1}", zoff=-0.5)
    put("StoneBrazier", 15.5 * LS, -28.5 * LS, 0.0, 1.0, "ArrivalStones", "ArrivalStones_Brazier")
    npc_spot("Greeter", ax, ay + 7.4, yaw=0.0)   # on the path just north of the big stone, facing the entrance


def _half_extents(o):
    bb = A[o["lobby_asset"]].bound_box
    hx = max(abs(v[0]) for v in bb) * o.scale[0]
    hy = max(abs(v[1]) for v in bb) * o.scale[1]
    return (o.location.x, o.location.y, o.rotation_euler.z, hx, hy)


def wall_inward_yaw(x, y):
    """Yaw that turns an asset's front (-Y) along the wall's inward normal at (x, y) on the
    wall line, so the asset stands square to the palisade."""
    gx = WALL["n"] * abs(x) ** (WALL["n"] - 1) / WALL["rx"] ** WALL["n"] * math.copysign(1, x)
    gy = WALL["n"] * abs(y - WALL["cy"]) ** (WALL["n"] - 1) / WALL["ry"] ** WALL["n"] * math.copysign(1, y - WALL["cy"])
    return math.atan2(-gy, -gx) + math.pi / 2


def zone_towers():
    # Both towers stand in the wall line, square to the wall and facing into the camp (the
    # wall breaks round them); each slides along the wall to where its silhouette centre
    # comes closest to the master's.
    wall = se_curve(WALL, N=1500)

    def on_wall(asset, sc, insets, target, quadrant):
        best = None
        for inset in insets:
            for k in range(0, len(wall.pts) - 1, 2):
                p = wall.pts[k]
                if not quadrant(p.x, p.y):
                    continue
                rz = wall_inward_yaw(p.x, p.y)
                x, y = p.x + inset * math.sin(rz), p.y - inset * math.cos(rz)
                (u, v), _ = _anchor_uv(asset, x, y, (0.0, 0.0, rz), (sc, sc, sc), "centre")
                e = (u - target[0]) ** 2 + (v - target[1]) ** 2 + 0.02 * inset   # prefer standing in the wall line
                if best is None or e < best[0]:
                    best = (e, x, y, rz)
        return best[1:]
    # W: roofed watch post in the west wall line north of the market (master: far left)
    x, y, rz = on_wall("WatchtowerRoofed", 0.72, (1.5,), MASTER["Watch platform"],
                       lambda x_, y_: x_ < 0 and abs(y_ - WALL["cy"]) < 0.8 * WALL["ry"])
    w = put("WatchtowerRoofed", x, y, rz, 0.72, "Watchtowers", "Watchtowers_WatchtowerRoofedW")
    TOWERS.append(_half_extents(w))
    # SW: open stilted deck in the south-west wall line, below the market
    x, y, rz = on_wall("WatchtowerTall", 1.15, (2.0, 4.0, 6.0, 8.0, 10.0), MASTER["SW watchtower"],
                       lambda x_, y_: x_ < -0.3 * WALL["rx"] and y_ < WALL["cy"])
    w = put("WatchtowerTall", x, y, rz, 1.15, "Watchtowers", "Watchtowers_WatchtowerTallSW")
    TOWERS.append(_half_extents(w))
    KEEP.append((x, y, 9.5))   # no tree canopy through the deck
    put("Barrel", *local(x, y, w.rotation_euler.z, 7.0, -3.0), w.rotation_euler.z, 1.0, "Watchtowers",
        "Watchtowers_Barrel")


# ---------------------------------------------------------------------------
# Plants and forest
# ---------------------------------------------------------------------------

PLANTS = [("GrassTuftLarge", 4.0), ("GrassClumpSmall", 4.0), ("FernLeafy", 1.3), ("WildflowerWhite", 1.6),
          ("BroadLeafHerb", 0.9), ("ShrubLowWide", 0.45), ("BerryBush", 0.3), ("ShrubTallDense", 0.2)]
BUSHES = [("ShrubLowWide", 2.0), ("ShrubTallDense", 1.5), ("BerryBush", 1.2), ("FernLeafy", 1.5),
          ("GrassTuftLarge", 1.0), ("BroadLeafHerb", 1.0), ("WildflowerWhite", 0.7)]
SOUTH_ISLAND = [("WildflowerWhite", 3.0), ("GrassClumpSmall", 2.0), ("GrassTuftLarge", 1.5)]
SOUTH_BAND = [("FernLeafy", 2.0), ("GrassTuftLarge", 2.0), ("BroadLeafHerb", 1.2), ("WildflowerWhite", 1.0),
              ("ShrubLowWide", 0.6), ("ShrubTallDense", 0.4), ("BerryBush", 0.25)]
TREES = [("BroadleafTreeStout", 1.2), ("BroadleafTreeTall", 1.1), ("BroadleafTreeWideOld", 0.5),
         ("BroadleafTreeLeaning", 0.7), ("PineTreeShortWide", 1.0), ("PineTreeTallNarrow", 1.2),
         ("PineTreeMature", 1.1), ("PineTreeYoung", 0.8)]


def pick(table, rng=RNG):
    tot = sum(w for _, w in table)
    r = rng.uniform(0, tot)
    for n, w in table:
        r -= w
        if r <= 0:
            return n
    return table[-1][0]


class Poisson:
    def __init__(self, r):
        self.r, self.cell, self.g = r, r, {}

    def ok(self, x, y, r=None):
        r = r or self.r
        gx, gy = int(math.floor(x / self.cell)), int(math.floor(y / self.cell))
        for i in range(gx - 2, gx + 3):
            for j in range(gy - 2, gy + 3):
                for px, py in self.g.get((i, j), ()):
                    if (px - x) ** 2 + (py - y) ** 2 < r * r:
                        return False
        return True

    def add(self, x, y):
        self.g.setdefault((int(math.floor(x / self.cell)), int(math.floor(y / self.cell))), []).append((x, y))


def wall_dist_fn():
    wall = se_curve(WALL, N=1200)
    arr = np.array([(p.x, p.y) for p in wall.pts])
    return lambda x, y: float(np.min(np.hypot(arr[:, 0] - x, arr[:, 1] - y)))


def build_grass_tufts():
    """Dense ground cover for the grass: thousands of tiny low-poly tufts (3-5 thin blades,
    dark at the root, sun-yellow at the tip) and small white and yellow flower heads, all in
    one mesh, so the open grass reads busy and hand-painted like the reference instead of
    flat. Placement follows the plateau and palisade variables, so a bigger camp just gets
    more of it."""
    a = fk.Asset("Ground_GrassTufts", "Ground", seed=SEED + 51)
    bm, tl = a.bm, a.tint_layer
    rng = random.Random(SEED + 51)
    gi = a._mi("grass_ground")
    fl = {"flower_white": a._mi("flower_white"), "flower_yellow": a._mi("flower_yellow")}
    xr, y0, y1 = 1.02 * WALL["rx"], WALL["cy"] - 1.08 * WALL["ry"], WALL["cy"] + 1.05 * WALL["ry"]
    area = 2 * xr * (y1 - y0)
    n_tuft = n_flower = 0
    for _ in range(int(area / 1.1)):
        x, y = rng.uniform(-xr, xr), rng.uniform(y0, y1)
        f_in = se_F(x, y, WALL)
        if f_in > 1.12 or dirt_sdf(x, y) < 0.35 or not free(x, y, 0.3):
            continue
        if f_in > 0.97 and rng.random() < 0.6:  # thinner right at the palisade foot
            continue
        z = h(x, y)
        patch = vn(x / 9 + 3, y / 9 + 77)
        if rng.random() < 0.012 + 0.03 * patch:  # flower head
            mat = "flower_yellow" if rng.random() < 0.35 else "flower_white"
            r = rng.uniform(0.16, 0.24)
            c = Vector((x, y, z + rng.uniform(0.25, 0.5)))
            rot0 = rng.uniform(0, math.tau)
            ring = [bm.verts.new(c + Vector((math.cos(rot0 + k * math.tau / 10) * r * (1 if k % 2 == 0 else 0.45),
                                             math.sin(rot0 + k * math.tau / 10) * r * (1 if k % 2 == 0 else 0.45),
                                             0.0))) for k in range(10)]
            mid = bm.verts.new(c + Vector((0, 0, 0.03)))
            for k in range(10):
                f = bm.faces.new((mid, ring[k], ring[(k + 1) % 10]))
                f.material_index = fl[mat]
                for lp in f.loops:
                    lp[tl] = (1.0, 1.0, 1.0, 1.0)
            n_flower += 1
            continue
        if rng.random() > 0.35 + 0.6 * patch:  # clumped: denser in the lusher patches
            continue
        base_t = grass_tint(x, y)
        nb = rng.randint(3, 5)
        az0 = rng.uniform(0, math.tau)
        hgt = rng.uniform(0.5, 1.0)
        for k in range(nb):
            az = az0 + k * math.tau / nb + rng.uniform(-0.4, 0.4)
            lean = rng.uniform(0.15, 0.5)
            d = Vector((math.cos(az), math.sin(az), 0.0))
            side = Vector((-d.y, d.x, 0.0)) * rng.uniform(0.07, 0.11)
            root = Vector((x, y, z - 0.05)) + d * rng.uniform(0.0, 0.12)
            tip = root + d * hgt * lean + Vector((0, 0, hgt * rng.uniform(0.8, 1.1)))
            f = bm.faces.new((bm.verts.new(root - side), bm.verts.new(root + side), bm.verts.new(tip)))
            f.material_index = gi
            dark = [c * 0.84 for c in base_t]
            lit = [c * 1.12 for c in base_t]
            for lp, col in zip(f.loops, (dark, dark, lit)):
                lp[tl] = (col[0], col[1], col[2] * 0.9, 1.0)
        n_tuft += 1
    for f in bm.faces:
        f.smooth = False
    print(f"grass tufts: {n_tuft} tufts, {n_flower} flowers")
    return own(a.finish(collection=C["Dressing"], mark_asset=False, origin="NONE"))


def dressing():
    rng = random.Random(SEED + 31)
    wd = wall_dist_fn()
    pz = Poisson(2.3)
    n_path = 0
    build_grass_tufts()
    # scatter bounds come from the palisade oval, so they follow a resized camp
    xr, y0, y1 = 0.97 * WALL["rx"], WALL["cy"] - 0.95 * WALL["ry"], WALL["cy"] + 0.95 * WALL["ry"]
    # along path and plaza edges
    for _ in range(int(9000 * LS * LS)):
        x, y = rng.uniform(-xr, xr), rng.uniform(y0, y1)
        if se_F(x, y, WALL) > 0.93:
            continue
        d = dirt_sdf(x, y)
        if not (0.3 < d < 3.2):
            continue
        if not free(x, y, 0.8) or not pz.ok(x, y):
            continue
        pz.add(x, y)
        nm = pick(SOUTH_ISLAND if (y < -6 * LS and abs(x) < 30 * LS) else PLANTS, rng)
        put(nm, x, y, rng.uniform(0, 6.28), rng.uniform(0.8, 1.2), "Dressing", uniq("Dressing_" + nm), keep=0)
        n_path += 1
        if n_path > 280 * LS:
            break
    # grass patches between the paths: clumps and tufts (denser than before: the
    # reference's open grass is busy with small tufts and flowers)
    for _ in range(int(6000 * LS * LS)):
        x, y = rng.uniform(-xr, xr), rng.uniform(y0, y1)
        if se_F(x, y, WALL) > 0.9 or dirt_sdf(x, y) < 2.0:
            continue
        if not free(x, y, 1.0) or not pz.ok(x, y, 3.6):
            continue
        pz.add(x, y)
        nm = pick(SOUTH_ISLAND if (y < -6 * LS and abs(x) < 30 * LS) else PLANTS, rng)
        put(nm, x, y, rng.uniform(0, 6.28), rng.uniform(0.85, 1.3), "Dressing", uniq("Dressing_" + nm), keep=0)
    # shrub clusters in the middle of the four grass islands
    for cx, cy, nmax in ((-14 * LS, 15 * LS, 3), (12 * LS, 19 * LS, 3), (-15 * LS, -21 * LS, 3), (14 * LS, -21 * LS, 3)):
        for k in range(rng.randint(nmax - 1, nmax)):
            x, y = cx + rng.uniform(-3.5, 3.5), cy + rng.uniform(-2.5, 2.5)
            if dirt_sdf(x, y) < 1.0 or not free(x, y, 1.0):
                continue
            nm = rng.choice(["ShrubLowWide", "BerryBush", "ShrubTallDense", "ShrubLowWide", "FernLeafy"])
            put(nm, x, y, rng.uniform(0, 6.28), rng.uniform(0.9, 1.25), "Dressing", uniq("Dressing_" + nm), keep=0)
    # along the wall, inside and outside
    wall = se_curve(WALL, N=3000)
    O = Vector((0, WALL["cy"]))
    s = 0.0
    while s < wall.length:
        p = wall.at(s)
        t = wall.tangent(s)
        inward = Vector((-t.y, t.x))
        if inward.dot(O - p) < 0:
            inward = -inward
        for off in (rng.uniform(2.2, 4.8), -rng.uniform(2.4, 6.0)):
            q = p + inward * off
            if wall_blocked(q) == "forge" or (off > 0 and not free(q.x, q.y, 0.7)):
                continue
            if abs(q.x) < 17 * LS and q.y > 20 * LS:  # keep the gate threshold clear
                continue
            if dirt_sdf(q.x, q.y) < 0.3 and off > 0:
                continue
            if not pz.ok(q.x, q.y, 1.8):
                continue
            pz.add(q.x, q.y)
            nm = pick(SOUTH_BAND if (off < 0 and q.y < WALL["cy"] - 30 * LS) else BUSHES, rng)
            put(nm, q.x, q.y, rng.uniform(0, 6.28), rng.uniform(0.8, 1.25), "Dressing", uniq("Dressing_" + nm), keep=0)
        s += rng.uniform(2.2, 3.6)
    return wd


def forest(wd):
    rng = random.Random(SEED + 41)
    pt = Poisson(7.5)
    north_path = PATHS[0][0]
    n_up = 0
    # grey rock outcrops in the band outside the wall (sides and front), as in the reference
    rock_pts = []
    rocks = [("LowBoulder", 2.0), ("SplitBoulder", 1.5), ("TallBoulder", 0.8), ("LongBoulder", 1.0)]
    pr = Poisson(8.5)
    for _ in range(int(6000 * LS)):
        x, y = rng.uniform(-84 * LS, 84 * LS), rng.uniform(-80 * LS, 40 * LS)
        if se_F(x, y, WALL) < 1.0 or se_F(x, y, RIM) > 0.97 or wd(x, y) < 4.0:
            continue
        if not (abs(x) > 50 * LS or y < -45 * LS) or seg_dist(PATHS[3][0], x, y) < 6:
            continue
        nm, sc = pick(rocks, rng), rng.uniform(0.6, 1.25)
        if wd(x, y) < 0.5 * max(A[nm].dimensions.x, A[nm].dimensions.y) * sc + 6.0:  # clear of the wall boulders
            continue
        rr = 0.5 * max(A[nm].dimensions.x, A[nm].dimensions.y) * sc
        if hides_camp(x, y, A[nm].dimensions.z * sc) or not pr.ok(x, y, max(8.5, 2.0 * rr)) or not free(x, y, rr):
            continue
        pr.add(x, y)
        pt.add(x, y)
        rock_pts.append((x, y, rr))
        put(nm, x, y, rng.uniform(0, 6.28), sc, "Forest", uniq("Forest_" + nm), keep=0, zoff=-0.5)
    # plateau band between the wall and the rim
    for _ in range(int(12000 * LS)):
        x, y = rng.uniform(-100 * LS, 100 * LS), rng.uniform(-80 * LS, 110 * LS)
        if se_F(x, y, WALL) < 1.0 or se_F(x, y, RIM) > 0.95:
            continue
        if wd(x, y) < 6.5:
            continue
        if seg_dist(north_path, x, y) < 9 or seg_dist(RIVER_PTS, x, y) < 10:
            continue
        if wall_blocked(Vector((x, y))) == "forge" or not free(x, y, 3.0):
            continue
        north = y > 30 * LS
        if north and (abs(x) < 24 * LS or (y > 62 * LS and abs(x) < 70 * LS)):
            continue  # thin canopy north of the gate so the path and the ridge cliffs read
        if not pt.ok(x, y, 11.0 if north else None):
            continue
        nm, sc = pick(TREES, rng), rng.uniform(0.85, 1.15)
        if hides_camp(x, y, A[nm].dimensions.z * sc):
            nm, sc = "PineTreeYoung", rng.uniform(0.85, 1.0)
            if hides_camp(x, y, A[nm].dimensions.z * sc):
                continue
        canopy = 0.5 * max(A[nm].dimensions.x, A[nm].dimensions.y) * sc
        if wd(x, y) < 0.85 * canopy + 1.0:
            continue  # canopy would reach into the palisade
        if not free(x, y, 0.85 * canopy) or not pt.ok(x, y, max(7.5, 0.8 * canopy)):
            continue
        if any(math.hypot(x - rx_, y - ry_) < rr_ + 0.85 * canopy for rx_, ry_, rr_ in rock_pts):
            continue  # canopy over a building, or crowding the bigger final trees
        pt.add(x, y)
        put(nm, x, y, rng.uniform(0, 6.28), sc, "Forest", uniq("Forest_" + nm), keep=0, zoff=-0.2)
        n_up += 1
    # pines along the bottom edge of the view (allowed to overlap the wall foot a little)
    n_pine = 0
    for _ in range(4000):
        x, y = rng.uniform(-80 * LS, 80 * LS), rng.uniform(-76 * LS, -60 * LS)
        if abs(x) < 14 * LS or se_F(x, y, RIM) > 0.95 or not pt.ok(x, y, 8.0):
            continue
        nm = rng.choice(["PineTreeYoung", "PineTreeShortWide", "PineTreeYoung", "PineTreeTallNarrow"])
        sc = rng.uniform(0.75, 1.0)
        if wd(x, y) < 0.5 * A[nm].dimensions.x * sc + 3.0 or not free(x, y, 0.45 * A[nm].dimensions.x * sc):
            continue   # lower branches clear the wall posts and the boulders at its foot
        if any(math.hypot(x - rx_, y - ry_) < rr_ + max(0.45 * A[nm].dimensions.x * sc, 3.0)
               for rx_, ry_, rr_ in rock_pts):  # lower branches must clear the boulders
            continue
        xc = max(-WALL["rx"] + 0.5, min(WALL["rx"] - 0.5, x))
        yw = WALL["cy"] - WALL["ry"] * (1 - (abs(xc) / WALL["rx"]) ** WALL["n"]) ** (1 / WALL["n"])
        if project(x, y, A[nm].dimensions.z * sc)[1] < project(xc, yw, 0)[1] - 110:
            continue
        pt.add(x, y)
        put(nm, x, y, rng.uniform(0, 6.28), sc, "Forest", uniq("Forest_" + nm), keep=0, zoff=-0.2)
        n_pine += 1
        if n_pine >= 14:
            break
    # lowland forest beyond the cliffs
    pl = Poisson(12.0)
    n_low = 0
    for _ in range(9000):
        x, y = rng.uniform(-230 * LS, 230 * LS), rng.uniform(-200 * LS, 260 * LS)
        f = se_F(x, y, RIM)
        if f < 1.25 or se_F(x, y, RIM, scale=2.1) > 1.0:
            continue
        if WF and math.hypot(x - WF["x"], y - WF["y"]) < 26:
            continue
        if LOW_RIVER and seg_dist(LOW_RIVER, x, y) < 12:
            continue
        if not pl.ok(x, y):
            continue
        nm, sc = pick(TREES, rng), rng.uniform(0.85, 1.15)
        if hides_camp(x, y, LOW_Z + A[nm].dimensions.z * sc):
            continue
        pl.add(x, y)
        put(nm, x, y, rng.uniform(0, 6.28), sc, "Forest", uniq("Forest_" + nm), keep=0,
            low=True, zoff=-0.3)
        n_low += 1
    # understory in the plateau band
    pu = Poisson(5.2)
    for _ in range(int(5000 * LS * LS)):
        x, y = rng.uniform(-100 * LS, 100 * LS), rng.uniform(-80 * LS, 110 * LS)
        if se_F(x, y, WALL) < 1.0 or se_F(x, y, RIM) > 0.97 or wd(x, y) < 5.5:
            continue
        if seg_dist(RIVER_PTS, x, y) < 8 or seg_dist(north_path, x, y) < 5.5:
            continue
        if wall_blocked(Vector((x, y))) == "forge" or not pu.ok(x, y):
            continue
        pu.add(x, y)
        nm = pick(SOUTH_BAND if y < WALL["cy"] - 30 * LS else BUSHES, rng)
        put(nm, x, y, rng.uniform(0, 6.28), rng.uniform(0.9, 1.4), "Forest", uniq("Forest_" + nm), keep=0)
    # a few fallen logs and stumps in the woods
    for i in range(10):
        for _ in range(200):
            x, y = rng.uniform(-80 * LS, 80 * LS), rng.uniform(-78 * LS, 72 * LS)
            if not (free(x, y, 5.0) and pr.ok(x, y, 9.0) and pt.ok(x, y, 9.0)):
                continue
            if se_F(x, y, WALL) > 1.15 and se_F(x, y, RIM) < 0.9 and wd(x, y) > 8 and seg_dist(RIVER_PTS, x, y) > 9:
                nm = rng.choice(["FallenLog", "Stump", "Stump", "CutLog"])
                put(nm, x, y, rng.uniform(0, 6.28), 1.0, "Forest", uniq("Forest_" + nm), keep=0)
                pr.add(x, y)
                break
    print(f"trees: plateau {n_up}, lowland {n_low}")


# ---------------------------------------------------------------------------
# Camera, light, render
# ---------------------------------------------------------------------------


def camera_and_light():
    scene = bpy.context.scene
    cam = bpy.data.objects.new("LobbyCam", bpy.data.cameras.new("LobbyCam"))
    cam.data.lens = CAM["lens"]
    cam.data.sensor_fit = "HORIZONTAL"
    cam.data.sensor_width = 36
    cam.data.clip_end = 3000
    cam.location = CAM["loc"]
    cam.rotation_euler = (math.radians(90 - CAM["pitch_deg"]), 0, 0)
    C["Lobby"].objects.link(cam)
    scene.camera = cam

    top = bpy.data.objects.new("LobbyCamTop", bpy.data.cameras.new("LobbyCamTop"))
    top.data.type = "ORTHO"
    top.data.ortho_scale = 200 * LS
    top.data.clip_end = 3000
    top.location = (0, -9 * LS, 300)
    C["Lobby"].objects.link(top)

    light_and_grade(scene)
    return cam, top


# Look development: warm late-afternoon sun with soft shadows, a warm-neutral sky fill that
# keeps the shade saturated green rather than blue-grey, horizon-scan AO/bounce in the
# crevices, and a plain Standard view transform (no contrast look) so the greens stay rich
# without the hard facet contrast. Tuned against art/reference/lobby_map.png crops.
LOOK = dict(sun_energy=4.6, sun_color="#FFD69A", sun_angle=9.0, sun_rot=(50, 0, -81),
            fill_energy=0.3, fill_color="#E4EBD6", sky_color="#C6D2CC", sky_strength=0.55,
            look="Medium Contrast", exposure=0.05, gi_distance=6.0)


def light_and_grade(scene):
    L = LOOK
    sun = bpy.data.objects.new("LobbySun", bpy.data.lights.new("LobbySun", "SUN"))
    sun.data.energy = L["sun_energy"]
    sun.data.color = fk.hex_rgb(L["sun_color"])
    sun.data.angle = math.radians(L["sun_angle"])
    if hasattr(sun.data, "use_shadow_jitter"):
        sun.data.use_shadow_jitter = True  # true soft penumbrae from the sun's angle
    sun.rotation_euler = tuple(math.radians(v) for v in L["sun_rot"])
    C["Lobby"].objects.link(sun)
    fill = bpy.data.objects.new("LobbySkyFill", bpy.data.lights.new("LobbySkyFill", "SUN"))
    fill.data.energy = L["fill_energy"]
    fill.data.color = fk.hex_rgb(L["fill_color"])
    fill.data.angle = math.radians(40)
    fill.data.use_shadow = False
    fill.rotation_euler = (math.radians(55), 0, math.radians(60))
    C["Lobby"].objects.link(fill)

    world = bpy.data.worlds.new("LobbySky")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*fk.hex_rgb(L["sky_color"]), 1)
    bg.inputs["Strength"].default_value = L["sky_strength"]
    if hasattr(world, "light_settings"):
        world.light_settings.distance = L["gi_distance"]  # horizon-scan AO reach

    scene.render.engine = "BLENDER_EEVEE"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    if L["look"] != "None":
        try:
            scene.view_settings.look = L["look"]
        except TypeError:
            pass
    scene.view_settings.exposure = L["exposure"]
    scene.render.resolution_x, scene.render.resolution_y = RES
    scene.render.resolution_percentage = 100
    try:
        scene.eevee.taa_render_samples = 32
    except AttributeError:
        pass
    # Eevee (5.x): screen-space ray tracing with horizon-scan fast GI gives the ambient
    # occlusion in crevices plus a little green bounce under canopies and eaves.
    for attr, val in (("use_shadows", True), ("shadow_ray_count", 2), ("shadow_step_count", 8),
                      ("use_raytracing", True), ("ray_tracing_method", "SCREEN"), ("use_fast_gi", True),
                      ("fast_gi_method", "GLOBAL_ILLUMINATION"), ("fast_gi_distance", L["gi_distance"]),
                      ("fast_gi_quality", 0.5), ("fast_gi_resolution", "2"), ("gi_diffuse_bounces", 2)):
        if hasattr(scene.eevee, attr):
            try:
                setattr(scene.eevee, attr, val)
            except Exception as exc:
                print("eevee setting skipped:", attr, exc)


def render(cam, path):
    scene = bpy.context.scene
    scene.camera = cam
    scene.render.filepath = path
    scene.render.image_settings.file_format = "PNG"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.render.render(write_still=True)


# ---------------------------------------------------------------------------
# Audit: interpenetration report and low-angle close-ups per zone
# ---------------------------------------------------------------------------

PLANTS_SOFT = {"GrassTuftLarge", "GrassClumpSmall", "FernLeafy", "WildflowerWhite", "BroadLeafHerb", "ShrubLowWide",
               "BerryBush", "ShrubTallDense"}
TERRAIN_TILES = {"ForestFloor", "Riverbank", "WaterfallCliff", "CliffSection", "CliffOuterCorner", "CliffInnerCorner",
                 "RockShelfTwoLevels", "EarthSwitchback", "RockArch", "GrassRamp", "RockyLakeshore", "CaveEntrance"}
ROCKS = {"LowBoulder", "SplitBoulder", "LongBoulder", "TallBoulder"}


def _audit_kind(o):
    a = o.get("lobby_asset")
    if a is None:  # meshes built here: only the solid props take part
        return "solid" if (o.name in ("Forge_StoneStairs", "VaultHall_RedRug", "EldersTotem_StelaFootings")
                           or o.name.startswith(("NPCPlaceholder_", "Market_Sacks"))) else None
    if a in PLANTS_SOFT or a in TERRAIN_TILES:
        return None
    if "Tree" in a:
        return "tree"
    if a in ROCKS:
        return "rock"
    return "solid"


def audit_overlaps(path, inset=0.03):
    """Exact mesh-intersection audit. For every pair of solid instances whose world bounding
    boxes overlap, both meshes go into world-space BVH trees (every vertex pulled `inset`
    studs in along its normal, so a prop resting on a surface does not count) and
    BVHTree.overlap() lists intersecting triangles. Skipped by design: ground and terrain
    tiles (everything stands on them), soft plants, tree-tree and rock-rock (natural clumps)."""
    objs = []
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name.startswith("VFXPreview") or o.location.z < -8:
            continue
        k = _audit_kind(o)
        if k:
            objs.append((o, k))
    data = {}
    for o, k in objs:
        bvh, verts = world_bvh(o, inset)
        lo = Vector((min(v.x for v in verts), min(v.y for v in verts), min(v.z for v in verts)))
        hi = Vector((max(v.x for v in verts), max(v.y for v in verts), max(v.z for v in verts)))
        data[o.name] = (bvh, lo, hi, k, o)
    grid = {}
    for n, (_, lo, hi, _, _) in data.items():
        for i in range(int(lo.x // 16), int(hi.x // 16) + 1):
            for j in range(int(lo.y // 16), int(hi.y // 16) + 1):
                grid.setdefault((i, j), set()).add(n)
    pairs = set()
    for cell in grid.values():
        for a in cell:
            for b in cell:
                if a < b:
                    pairs.add((a, b))
    out, joins = [], 0
    for a, b in sorted(pairs):
        ba, la, ha, ka, oa = data[a]
        bb, lb, hb, kb, ob = data[b]
        if any(la[i] > hb[i] or lb[i] > ha[i] for i in range(3)):
            continue
        if ka == kb and ka in ("tree", "rock"):
            continue
        n = len(ba.overlap(bb))
        # intentional: a wall bay's end inside the main post on its own join (kit tiling)
        if n and any(p.get("wall_join") is not None and q.get("wall_joins") is not None
                     and p["wall_join"] in list(q["wall_joins"]) for p, q in ((oa, ob), (ob, oa))):
            joins += 1
            continue
        if n:
            c = (oa.location + ob.location) / 2
            out.append((n, a, b, c))
    out.sort(key=lambda t: -t[0])
    with open(path, "w") as f:
        for n, a, b, c in out:
            f.write(f"{n:5d} tris  {a}  <->  {b}   at ({c.x:.1f}, {c.y:.1f}, {c.z:.1f})\n")
    print(f"audit (mesh): {len(objs)} solids, {len(pairs)} candidate pairs, {len(out)} intersecting, "
          f"{joins} intentional wall-join contacts (bay ends inside their own post) -> {path}")
    return out


def _cylinder_bvh(x, y, z0, z1, r, n=24):
    vs, fs = [], []
    for k in range(n):
        a = 2 * math.pi * k / n
        vs += [Vector((x + r * math.cos(a), y + r * math.sin(a), z0)), Vector((x + r * math.cos(a), y + r * math.sin(a), z1))]
    for k in range(n):
        j = (k + 1) % n
        fs.append((2 * k, 2 * j, 2 * j + 1, 2 * k + 1))
    fs += [tuple(2 * k for k in range(n)), tuple(2 * k + 1 for k in range(n))]
    return BVHTree.FromPolygons(vs, fs)


def audit_npc_clearance(path):
    """Every NPC spot needs a clear cylinder NPC_R x NPC_H standing on its support (0.3 studs
    of floor tolerance). Any mesh other than the ground surfaces and the spot's own
    placeholder that cuts the cylinder wall/caps (BVH overlap) or has a vertex inside it
    is reported, plants and grass included. Walking access: the dirt SDF at the spot
    (< 0: on a path or apron) and the distance to the nearest dirt within 8 studs."""
    ground = ("Ground_", "Terrain_RimSkirt", "River_Water")
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith(ground)
              and not o.name.startswith("VFXPreview") and o.library is None]   # not the linked library originals
    lines, blocked = [], 0
    for role, (x, y, z, yaw) in NPC_SPOTS.items():
        z0, z1 = z + 0.3, z + NPC_H
        cyl = _cylinder_bvh(x, y, z0, z1, NPC_R)
        hits_ = []
        for o in meshes:
            if o.name == f"NPCPlaceholder_{role}":
                continue
            src = A[o["lobby_asset"]] if o.get("lobby_asset") else o
            M = Matrix.LocRotScale(o.location, o.rotation_euler, o.scale)
            bb = [M @ Vector(c) for c in src.bound_box]
            if min(v.x for v in bb) > x + NPC_R or max(v.x for v in bb) < x - NPC_R or \
               min(v.y for v in bb) > y + NPC_R or max(v.y for v in bb) < y - NPC_R or \
               min(v.z for v in bb) > z1 or max(v.z for v in bb) < z0:
                continue
            bvh, verts = world_bvh(o, 0.0)
            inside = any((v.x - x) ** 2 + (v.y - y) ** 2 < NPC_R ** 2 and z0 < v.z < z1 for v in verts)
            if inside or cyl.overlap(bvh):
                hits_.append(o.name)
        d0 = dirt_sdf(x, y)
        near = min((math.hypot(dx, dy) for dx in range(-8, 9) for dy in range(-8, 9)
                    if dirt_sdf(x + dx, y + dy) < 0), default=99.0)
        blocked += bool(hits_)
        lines.append(f"{'BLOCKED' if hits_ else 'clear  '}  NPC_{role:13s} ({x:7.2f}, {y:7.2f}, {z:5.2f})  yaw {math.degrees(yaw):6.1f}"
                     f"  dirt_sdf {d0:5.2f}  nearest_path {near:4.1f}  {', '.join(hits_)}")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"audit (npc): {len(NPC_SPOTS)} spots, {blocked} blocked -> {path}")
    for ln in lines:
        print("  " + ln)
    return blocked


AUDIT_VIEWS = {  # name: (camera position, look-at target), low angles to check ground contact
    "gate": ((0, 6, 9), (0, 30, 5)),
    "plaza": ((14, -22, 13), (0, 0, 1)),
    "totem": ((-18, 2, 9), (-40, 18, 4)),
    "forge": ((20, -10, 11), (40, 14, 4)),
    "vault": ((8, -12, 11), (38, -25, 3)),
    "vault_front": ((21, -41, 9), (40, -22.5, 2.5)),
    "market": ((-10, -4, 10), (-40, -15, 3)),
    "arrival": ((0, -16, 12), (0, -42, 1)),
    "towers": ((-24, -20, 18), (-50, -17, 7)),
    "wall_south_outside": ((-22, -88, 15), (-22, -50, 4)),
    "wall_east_outside": ((98, -26, 15), (62, -12, 4)),
    "river": ((58, 12, 32), (76, 50, 2)),
}


def west_views():
    """West-side close-ups: from the main camera's direction (to judge facing as the player
    sees it) and from standing height."""
    cam = Vector(CAM["loc"])

    def from_cam(t, dist):
        t = Vector(t)
        return (tuple(t + (cam - t).normalized() * dist), tuple(t))

    def ground(pos, tgt):
        return (tuple(pos), tuple(tgt))

    v = {}
    tx, ty = TOTEM["x"], TOTEM["y"]
    v["west_totem_cam"] = from_cam((tx + 2, ty - 2, 7.0), 46)
    p = totem_local(-3.0, -30.0)
    v["west_totem_ground"] = ground((p[0], p[1], 6.5), (tx, ty, 7.0))
    for k, ((x, y), (_key, hgt, wid)) in enumerate(zip(stela_xy(), STELAE)):
        p = local(x, y, face_view(x, y), 0.0, -12.0)
        v[f"west_stela_{k + 1}_ground"] = ground((p[0], p[1], 3.0), (x, y, hgt * 0.5))
    v["west_quest_cam"] = from_cam((QUEST["x"], QUEST["y"] - 2, 3.0), 30)
    p = quest_local(-2.0, -15.0)
    v["west_quest_ground"] = ground((p[0], p[1], 3.2), (QUEST["x"] - 2, QUEST["y"], 3.0))
    st = market_stalls()
    mx = sum(s_[1] for s_ in st) / len(st)
    my = sum(s_[2] for s_ in st) / len(st)
    v["west_market_cam"] = from_cam((mx + 4, my - 2, 2.0), 72)
    v["west_market_top"] = ground((mx + 10, my - 8, 82), (mx + 4, my - 2, 0))
    lane = market_lane_poly()
    a, b = Vector(lane[0]), Vector(lane[-1])
    v["west_market_lane_ground"] = ground((a.x + (a - b).normalized().x * 6, a.y + (a - b).normalized().y * 6, 3.6),
                                          (b.x, b.y, 2.5))
    for k, (nm, x, y, rot, ss, f, hw, hd) in enumerate(st):
        v[f"west_stall_{k + 1}_ground"] = ground((x + f[0] * (hd + 13), y + f[1] * (hd + 13), 4.2), (x, y, 3.2))
    for nm in ("Watchtowers_WatchtowerRoofedW", "Watchtowers_WatchtowerTallSW"):
        o = bpy.data.objects.get(nm)
        if o:
            v[f"west_{nm.split('_')[1]}_cam"] = from_cam(tuple(o.location + Vector((0, 0, 5))), 48)
    v["west_arrival_cam"] = from_cam((0.0, -37.0 * LS, 0.5), 44)
    v["west_overview_cam"] = from_cam((-44.0, -6.0, 0.0), 125)
    for role in ("Elder", "QuestGiver", "Greeter", "VaultKeeper", "Blacksmith"):
        if role in NPC_SPOTS:
            x, y, z, yaw = NPC_SPOTS[role]
            v[f"west_npc_{role}_cam"] = from_cam((x, y, z + 2.5), 22)
    return v


def audit_renders(out_dir):
    scene = bpy.context.scene
    cam = bpy.data.objects.new("AuditCam", bpy.data.cameras.new("AuditCam"))
    cam.data.lens = 30
    cam.data.clip_end = 2000
    scene.collection.objects.link(cam)
    old = (scene.render.resolution_x, scene.render.resolution_y)
    scene.render.resolution_x, scene.render.resolution_y = 1000, 560
    try:
        scene.eevee.taa_render_samples = 16
    except AttributeError:
        pass
    os.makedirs(out_dir, exist_ok=True)
    sc3 = lambda p: (p[0] * LS, p[1] * LS, p[2])  # noqa: E731  (views were set up before LS)
    views = {f"audit_{k}": (sc3(a), sc3(b)) for k, (a, b) in AUDIT_VIEWS.items()}
    views.update(west_views())
    # close-ups of the fixes: paired south torches, both towers, every weapon rack
    objs = bpy.data.objects
    torches = [o for o in objs if "PostTorch" in o.name and o.name.startswith("Palisade_")
               and abs(o.location.x) < 24 and o.location.y < -40]
    for side, grp in (("west", [o for o in torches if o.location.x < 0]), ("east", [o for o in torches if o.location.x > 0])):
        if not grp:
            continue
        t = sum((o.location for o in grp), Vector()) / len(grp) + Vector((0, 0, 7.5))
        sx = -1 if side == "west" else 1
        views[f"fix_south_torches_{side}_outside"] = (tuple(t + Vector((sx * 5, -12, 2.5))), tuple(t))
        views[f"fix_south_torches_{side}_inside"] = (tuple(t + Vector((-sx * 4, 11, 1.5))), tuple(t))
    for o in objs:
        a = o.get("lobby_asset", "")
        if a.startswith("Watchtower"):
            t = o.location + Vector((0, 0, 6))
            d = (Vector((0, -10, 0)) - o.location).normalized()
            views[f"fix_{o.name}"] = (tuple(t + d * 24 + Vector((0, 0, 9))), tuple(t))
            views[f"fix_{o.name}_wallside"] = (tuple(t - d * 22 + Vector((0, 0, 12))), tuple(t))
        if a == "WeaponRack":
            t = o.location + Vector((0, 0, 2.6))
            rz = o.rotation_euler.z
            f = Vector((math.sin(rz), -math.cos(rz), 0))
            views[f"fix_rack_{o.name}"] = (tuple(t + f * 8 + Vector((2.5, 0, 2.5))), tuple(t))
    # terrain fit: the cliff rim from outside, the river, both waterfalls and the bridge
    rim = se_curve(RIM, N=2000)
    Oc = Vector((0, RIM["cy"]))
    for deg in (0, -40, -90, -140, 180, 140):
        a = math.radians(deg)
        c_, s_ = math.cos(a), math.sin(a)
        p = Vector((RIM["rx"] * math.copysign(abs(c_) ** (2 / RIM["n"]), c_),
                    RIM["cy"] + RIM["ry"] * math.copysign(abs(s_) ** (2 / RIM["n"]), s_)))
        o2 = (p - Oc).normalized()
        out = Vector((o2.x, o2.y, 0))
        tgt = Vector((p.x, p.y, -6))
        views[f"fix_rim_{deg}"] = (tuple(tgt + out * 46 + Vector((0, 0, 14))), tuple(tgt))
    if WF:
        w = Vector((WF["x"], WF["y"], -8))
        out = (w.xy - Oc).normalized()
        views["fix_waterfall_rim"] = (tuple(w + Vector((out.x, out.y, 0)) * 42 + Vector((0, 0, 10))), tuple(w))
    u = Vector((UWF_POS[0], UWF_POS[1], 6))
    views["fix_waterfall_ridge"] = (tuple(u + Vector((UWF_FRONT[0], UWF_FRONT[1], 0)) * 34 + Vector((0, 0, 8))), tuple(u))
    br = bpy.data.objects.get("River_FootbridgeSmall")
    if br:
        b = br.location + Vector((0, 0, 1.5))
        views["fix_bridge"] = (tuple(b + Vector((-13, -11, 7))), tuple(b))
    views["fix_river"] = ((70, 20, 24), (86, 38, 0))
    for name, (pos, tgt) in views.items():
        cam.location = Vector(pos)
        cam.rotation_euler = (Vector(tgt) - cam.location).to_track_quat("-Z", "Y").to_euler()
        render(cam, os.path.join(out_dir, f"{name}.png"))
    scene.render.resolution_x, scene.render.resolution_y = old
    bpy.data.objects.remove(cam, do_unlink=True)


# ---------------------------------------------------------------------------
# Overlay check: measured zone anchors against art/reference/lobby_map.png
# ---------------------------------------------------------------------------

REF_IMG = os.path.join(os.path.dirname(ROOT), "reference", "lobby_map.png")


def _uv(scene, cam, co):
    from bpy_extras.object_utils import world_to_camera_view
    p = world_to_camera_view(scene, cam, Vector(co))
    return 100.0 * p.x, 100.0 * (1.0 - p.y)


def _world_verts(o):
    me = _mesh_of(o)
    M = Matrix.LocRotScale(o.location, o.rotation_euler, o.scale)
    return [M @ v.co for v in me.vertices]


def _centre(o):
    vs = _world_verts(o)
    return Vector(tuple((min(v[i] for v in vs) + max(v[i] for v in vs)) / 2 for i in range(3)))


def measure_anchors(scene, cam):
    """World anchor of every zone, projected to frame % with world_to_camera_view."""
    ob = bpy.data.objects.get
    got = {}

    def pt(name, co):
        if co is not None:
            got[name] = _uv(scene, cam, co)

    def box(name, objs):
        objs = [o for o in objs if o is not None]
        if not objs:
            return
        uv = [_uv(scene, cam, v) for o in objs for v in _world_verts(o)]
        got[name] = (min(u for u, _ in uv), max(u for u, _ in uv), min(v for _, v in uv), max(v for _, v in uv))

    t = ob("EldersTotem")
    if t:
        vs = _world_verts(t)
        pt("Totem base", (t.location.x, t.location.y, min(v.z for v in vs)))
        pt("Totem top", (t.location.x, t.location.y, max(v.z for v in vs)))
    for k, nm in (("Rune stone L", "EldersTotem_RuneStela_1"), ("Rune stone R", "EldersTotem_RuneStela_2")):
        if ob(nm):
            pt(k, _centre(ob(nm)))
    if ob("EldersTotem_Brazier_2"):
        pt("Brazier", _centre(ob("EldersTotem_Brazier_2")))
    if ob("EldersTotem_QuestBoard"):
        pt("Quest board", _centre(ob("EldersTotem_QuestBoard")))
    if "Elder" in NPC_SPOTS:
        x, y, z, _ = NPC_SPOTS["Elder"]
        pt("Elder", (x, y, z + 2.75))
    for k, role in (("Stall thatch", "thatch"), ("Stall banner", "banner"), ("Stall red", "red"), ("Stall tan", "tan")):
        o = next((q for q in bpy.data.objects if q.get("market_role") == role), None)
        if o:   # the master marks were read off the roof / canopy centres
            got[k] = _anchor_uv(o["lobby_asset"], o.location.x, o.location.y, tuple(o.rotation_euler),
                                tuple(o.scale), "roof", z=o.location.z)[0]
    if MARKET_LABEL:
        pt("Market label", (MARKET_LABEL[0], MARKET_LABEL[1], h(*MARKET_LABEL)))
    for k, nm in (("Watch platform", "Watchtowers_WatchtowerRoofedW"), ("SW watchtower", "Watchtowers_WatchtowerTallSW")):
        if ob(nm):
            pt(k, _centre(ob(nm)))
    pt("Bonfire", (0.0, 0.0, h(0, 0)))
    if ob("ArrivalStones_LargeRuneStone"):
        pt("Arrival stones", ob("ArrivalStones_LargeRuneStone").location)
    rails = [q for q in bpy.data.objects if q.name.startswith("Palisade_SouthRail")]
    if rails:
        pt("South entrance", sum((_centre(q) for q in rails), Vector()) / len(rails))
    box("Deploy gate", [ob("DeployGate")])
    box("Forge", [ob("Forge_AncestralForge")])
    box("Vault", [ob("VaultHall")])
    return got


def anchor_report(got):
    lines, worst = [], 0.0
    for k, tgt in MASTER.items():
        m = got.get(k)
        if m is None:
            lines.append(f"  {k:15s} target {tgt}  MISSING")
            continue
        f = lambda v: "(" + ", ".join(f"{x:5.1f}" for x in v) + ")"  # noqa: E731
        if len(tgt) == 4:
            # box zones: the anchor is the silhouette centre (the gate: its base on the wall
            # line, since the master's gate runs off the top of the frame); the extents are
            # shown to compare silhouettes (building sizes are kept, so they may differ)
            if k == "Deploy gate":
                mc, tc = ((m[0] + m[1]) / 2, m[3]), ((tgt[0] + tgt[1]) / 2, tgt[3])
            else:
                mc, tc = ((m[0] + m[1]) / 2, (m[2] + m[3]) / 2), ((tgt[0] + tgt[1]) / 2, (tgt[2] + tgt[3]) / 2)
            err = max(abs(a - b) for a, b in zip(mc, tc))
            size = max(abs(a - b) for a, b in zip(m, tgt))
            extra = f"  anchor {f(mc)} vs {f(tc)}, extent off by up to {size:.1f}"
        else:
            err, extra = max(abs(a - b) for a, b in zip(m, tgt)), ""
        worst = max(worst, err)
        lines.append(f"  {k:15s} measured {f(m):30s} target {f(tgt):30s} err {err:4.1f}{'  <-- OFF' if err > 2.0 else ''}{extra}")
    lines.append(f"  worst error {worst:.1f}% of frame")
    return lines


def write_overlay(render_path, out_path, got):
    """50/50 blend of the LobbyCam render and the master, target (green) and measured (red)
    anchors marked, so silhouettes and positions can be compared directly."""
    def load(p):
        img = bpy.data.images.load(p, check_existing=False)
        W, H = img.size
        a = np.array(img.pixels[:], dtype=np.float32).reshape(H, W, 4)
        bpy.data.images.remove(img)
        return a
    a, b = load(render_path), load(REF_IMG)
    if a.shape != b.shape:
        print("overlay: size mismatch", a.shape, b.shape)
        return
    c = 0.5 * a + 0.5 * b
    c[..., 3] = 1.0
    H, W = c.shape[:2]

    def mark(u, v, col, r=7):
        x, y = int(u / 100 * W), H - 1 - int(v / 100 * H)   # pixels are stored bottom row first
        if 0 <= x < W and 0 <= y < H:
            c[max(0, y - 1):y + 2, max(0, x - r):x + r + 1, :3] = col
            c[max(0, y - r):y + r + 1, max(0, x - 1):x + 2, :3] = col

    def rect(u0, u1, v0, v1, col):
        cl = lambda v, n: max(0, min(n - 1, int(v)))  # noqa: E731
        x0, x1 = cl(u0 / 100 * W, W), cl(u1 / 100 * W, W)
        y0, y1 = cl(H - 1 - v1 / 100 * H, H), cl(H - 1 - v0 / 100 * H, H)
        c[y0:y1 + 1, x0, :3] = col
        c[y0:y1 + 1, x1, :3] = col
        c[y0, x0:x1 + 1, :3] = col
        c[y1, x0:x1 + 1, :3] = col

    for k, tgt in MASTER.items():
        m = got.get(k)
        if len(tgt) == 2:
            mark(*tgt, (0.1, 1.0, 0.1))
            if m:
                mark(*m, (1.0, 0.1, 0.1))
        else:
            rect(*tgt, (0.1, 1.0, 0.1))
            if m:
                rect(*m, (1.0, 0.1, 0.1))
    o = bpy.data.images.new("lobby_overlay", W, H, alpha=True)
    o.pixels = c.ravel()
    o.filepath_raw = out_path
    o.file_format = "PNG"
    o.save()
    bpy.data.images.remove(o)
    print("overlay ->", out_path)


def closeup_renders(out_dir):
    """Close-ups for the owner's review: three wall stretches, the market and the totem,
    each seen from the lobby camera's side (wall_south, wall_nw, wall_east, market, totem)."""
    scene = bpy.context.scene
    cam = bpy.data.objects.new("CloseupCam", bpy.data.cameras.new("CloseupCam"))
    cam.data.lens = 35
    cam.data.clip_end = 2000
    scene.collection.objects.link(cam)
    old = (scene.render.resolution_x, scene.render.resolution_y)
    scene.render.resolution_x, scene.render.resolution_y = 1400, 788
    camv = Vector(CAM["loc"])

    def from_cam(t, dist, lift=0.0):
        t = Vector(t)
        return t + (camv - t).normalized() * dist + Vector((0, 0, lift)), t
    ys = WALL["cy"] - WALL["ry"]
    xe = WALL["rx"] * 0.97
    views = {
        "wall_south": from_cam((0.0, ys, 5.0), 62),
        "wall_nw": from_cam((-0.8 * WALL["rx"], WALL["cy"] + 0.74 * WALL["ry"], 5.0), 56),
        "wall_east": (Vector((xe - 36, WALL["cy"] - 66, 52)), Vector((xe - 2, WALL["cy"] - 14, 3.0))),
        "market": from_cam((MARKET_LABEL[0], MARKET_LABEL[1] + 4, 3.0), 78),
        "totem": from_cam((TOTEM["x"] + 6, TOTEM["y"], 6.0), 52),
    }
    os.makedirs(out_dir, exist_ok=True)
    for name, (pos, tgt) in views.items():
        cam.location = pos
        cam.rotation_euler = (tgt - pos).to_track_quat("-Z", "Y").to_euler()
        render(cam, os.path.join(out_dir, f"{name}.png"))
    scene.render.resolution_x, scene.render.resolution_y = old
    bpy.data.objects.remove(cam, do_unlink=True)


def main():
    t0 = time.time()
    setup_scene()
    load_libraries()
    init_river()          # the pool position comes from the WaterfallCliff tile itself
    plan_layout()         # every zone on its master frame position, then the paths to them
    build_plateau()
    build_dirt()
    build_pebbles()
    terrain()
    build_rim_skirt()
    build_lower_ground()  # after terrain(): it carves around the waterfall pool and outflow
    zone_gate()
    zone_plaza()
    zone_forge()
    zone_vault()
    zone_totem()
    zone_towers()         # before the market, so market dressing keeps clear of the SW tower
    zone_market()
    zone_arrival()
    build_npcs()
    palisade()
    forest_floor_tiles()
    wd = dressing()
    forest(wd)
    cam, top = camera_and_light()
    try:
        made = vfx.realize(bpy.context.scene) if vfx and hasattr(vfx, "realize") else []
        print(f"vfx.realize: {len(made)} preview objects")
    except Exception as exc:
        print("vfx.realize failed:", exc)
    STATS["total_tris"] = STATS["tris"] + STATS["own_tris"]
    audit_dir = None
    if "--audit" in sys.argv:
        audit_dir = sys.argv[sys.argv.index("--audit") + 1]
        STATS["overlaps"] = len(audit_overlaps(os.path.join(audit_dir, "audit_overlaps.txt")))
        STATS["npc_blocked"] = audit_npc_clearance(os.path.join(audit_dir, "audit_npc_clearance.txt"))
    scene = bpy.context.scene
    scene["lobby_stats"] = json.dumps(STATS)
    print("STATS", json.dumps(STATS))
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, compress=True, relative_remap=True)
    got = measure_anchors(scene, cam)
    print("ANCHORS (frame %, from top-left)")
    for ln in anchor_report(got):
        print(ln)
    if "--no-render" not in sys.argv:
        render(cam, os.path.join(RENDER_DIR, "lobby_map.png"))
        ov = sys.argv[sys.argv.index("--overlay") + 1] if "--overlay" in sys.argv else os.path.join(RENDER_DIR, "lobby_overlay.png")
        write_overlay(os.path.join(RENDER_DIR, "lobby_map.png"), ov, got)
        render(top, os.path.join(RENDER_DIR, "lobby_map_top.png"))
        scene.camera = cam
        bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, compress=True, relative_remap=True)
    if "--closeups" in sys.argv:
        closeup_renders(sys.argv[sys.argv.index("--closeups") + 1])
    if audit_dir and "--no-audit-renders" not in sys.argv:
        audit_renders(audit_dir)
    print(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
