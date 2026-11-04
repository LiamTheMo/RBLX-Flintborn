"""Shared technical checks for the numbered models (STAGES.md stages 2-3 and 7): one call measures everything a
modeller reports and a verifier re-measures, and lists whatever misses a target.

    import sys; sys.path.insert(0, "<repo>/art/blender/kit/mcp")
    import kit_mcp; kit_mcp.install()
    import importlib, kit_verify as V; importlib.reload(V)
    objs = [bpy.data.objects[n] for n in ("TimberCabin", "TimberCabinRoofPanel")]
    r = V.run(objs, cls="building")
    r["problems"]        # [] means clean; every number is in r["objects"][name] and the optional sections

Read-only: nothing is moved, rebuilt or saved (kit_check=True runs K.check, which only writes its stats properties
"tris", "kit_baked_shading", ... onto the objects, as build() does).

Shells are labelled from the builder's piece register when the object carries one (o["mNNN_pieces"]: [kind, name,
centroid in the build frame] per shell, and o["mNNN_offset"]); otherwise kind = the shell's main material key
without the sheet prefix ("timber", "canvas") and name = "<kind>#<shell>". Kind matching in the options is by
substring ("rope" matches "rope_deep").

Frames: coordinates passed in the options (boxes, paths, points) and coordinates reported are in the build frame when
the object stores its offset (o["mNNN_offset"], the specs' numbers), else in the object's own mesh frame (origin at
the bottom centre). frame="local" forces the mesh frame. Every result says which frame it used.

run(objs, cls="asset", **opts). The hero is the first object with kit_role "hero" (else objs[0]); it gets `cls`,
parts get "part", variants `cls`.
  classes={name: cls}, budgets={name: tris}     per-object class / budget overrides
  size=(W, D, H) or {name: (W, D, H)}; size_tol=0.05 (or ((W, tol), (D, tol), (H, tol)))
  sockets=[kinds] (hero) or {name: [kinds]}       exact socket kinds wanted (sorted compare)
  stored=[props] (hero) or {name: [props]}        custom properties that must exist
  contact=0.03, chain=0.1, ground_z=0.0 (mesh frame), bury=0.05, bury_pairs={("rope", "rope"): 0.08},
  bury_edges=True (also sample edge midpoints; False = the builders' verts + face centres),
  thin=("canvas", "banner", "emblem", "cloth", "tarp", "sail", "flag")     pierce targets (kinds)
  thin_floor=0.3 (deg), uv_gap=0.0159, uv_border=0.0079, colour_limit=0.3, origin_tol=0.01, kit_check=True,
  frame="build" | "local"
Optional checks (each a dict, or True for defaults where that makes sense; "obj" names the object, default the hero):
  foliage=True | {"keys": ("leaf", "ivy", "frond"), "objs": [names], "els": (0, 5, 10, 20), "step": 5,
                  "limit": 0.10, "max_thick": 0.5}
      STAGES' 5-degree azimuth sweep with the whole-leaf rule: a leaf is edge-on when >= 75 % of its lobe (front)
      facets are within 15 deg of edge-on, or its projected front area is under 0.26 of face-on. Leaf shells are the
      shells whose kind contains a key and whose thickness ratio (PCA) is under max_thick.
  escape={"box": (lo, hi), "allow": {"door": (lo, hi)}, "spacing": 1.4, "dirs": 320, "clear": 0.15, "wall": 0.6,
          "step": 0.1, "seams": True, "floor": True}
      Inside light-escape scan: rays from a grid of enclosed points in the interior box (and lower-hemisphere rays
      just over its floor, and seam rays through each wall face and the floor along every vertex coordinate +-0.0007)
      that hit nothing. A ray is allowed when it leaves the interior box inside an `allow` box.
  walk={"paths": [[(x, y), (x, y), ...], ...], "proxy": "box" | "capsule" | ((hx, hy, z0, z1), ...), "ride": True,
        "feet_z": 0.0, "lift": 0.10, "skip": (name / kind prefixes left out of the clearance), "clear": 0.10,
        "turn": [(x, y, floor_z)], "max_rise": 1.0, "radius": 1.0, "height": 5.5}
      A 5.5-stud character proxy (default: the spec box, body 2 x 1 to 4.4 and a 1.1 head to 5.5) walks each path
      from feet_z; with ride its feet step onto the highest surface under its footprint that is at most max_rise above
      them (+ lift). Clearance to the nearest surface (shells in `skip` left out: the floors walked on), proxy /
      geometry intersections, headroom above the path, the rises met, and turning room (24 yaws) at `turn` points.
  seams={"pitch": (16, 0, 0), "with": "OtherModule", "tol": 0.001}
      Tiling: a copy offset by the pitch must not cross the original (or `with`, both ways: triangle pairs that
      intersect), the flat end faces must have the same outline over their common height (sliced at 41 levels, within
      0.002), and nothing may pass the seam planes at +-pitch/2 (build frame). Reports the gap at the seam and the
      closest approach. same_section=False reports the outline without judging it.
"""
import json
import math
import time

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import kit_mcp as K
import kit_models as M

CLASSES = {"part": 999, "prop": 999, "asset": 3999, "structure": 6000, "building": 8000}
CONTACT, CHAIN, BURY = 0.03, 0.1, 0.05
BURY_PAIRS = {("rope", "rope"): 0.08}            # rope turns crossing each other (m064 / m068 / m070 SINK_LIMIT)
THIN_KEYS = ("canvas", "banner", "emblem", "cloth", "tarp", "sail", "flag")
LEAF_KEYS = ("leaf", "ivy", "frond")
THIN_FLOOR = 0.3
PROXY = ((1.0, 0.5, 0.0, 4.4), (0.55, 0.5, 4.4, 5.5))     # (half across, half along, z0, z1): body, head
_PDIRS = (Vector((1.0, 0.0131, 0.0217)).normalized(), Vector((-0.0173, 1.0, 0.0119)).normalized(),
          Vector((0.0109, -0.0207, 1.0)).normalized())
EDGE15 = math.sin(math.radians(15))


def _r(x, n=3):
    return round(float(x), n)


def _v(v, n=3):
    return [round(float(c), n) for c in v]


def _parity_in(tree, p):
    """(m047) p is inside a closed surface if at least two of three skewed rays cross it an odd number of times."""
    votes = 0
    for d in _PDIRS:
        n, q = 0, p.copy()
        for _ in range(64):
            h = tree.ray_cast(q, d, 1000.0)
            if h[0] is None:
                break
            n += 1
            q = h[0] + d * 1e-4
        votes += n % 2
    return votes >= 2


def _inside(tree, p, eps=1e-4):
    """(inside, depth): the nearest-face side first (cheap), confirmed by ray parity."""
    loc, nrm, fi, d = tree.find_nearest(p)
    if loc is None or d < eps or (p - loc).dot(nrm) > 0:
        return False, 0.0
    return _parity_in(tree, p), d


def _fib(n, lower=False):
    ga = math.pi * (3.0 - math.sqrt(5.0))
    out = []
    for i in range(n):
        z = -(i + 0.5) / n if lower else 1.0 - 2.0 * (i + 0.5) / n
        r = math.sqrt(max(0.0, 1.0 - z * z))
        out.append(Vector((r * math.cos(ga * i), r * math.sin(ga * i), z)))
    return out


def _fmin(cs):
    """Smallest corner angle (radians) of a polygon's corner coordinates."""
    m, out = len(cs), math.pi
    for i in range(m):
        e1, e2 = cs[i - 1] - cs[i], cs[(i + 1) % m] - cs[i]
        if e1.length > 1e-9 and e2.length > 1e-9:
            out = min(out, e1.angle(e2))
        else:
            out = 0.0
    return out


def _box_hit(p, d, lo, hi, far=1e9):
    """Ray (p, d) against an axis box: (t_enter, t_exit) or None."""
    t0, t1 = 0.0, far
    for i in range(3):
        if abs(d[i]) < 1e-12:
            if p[i] < lo[i] or p[i] > hi[i]:
                return None
            continue
        a, b = (lo[i] - p[i]) / d[i], (hi[i] - p[i]) / d[i]
        if a > b:
            a, b = b, a
        t0, t1 = max(t0, a), min(t1, b)
        if t0 > t1:
            return None
    return t0, t1


def _in_box(p, lo, hi, pad=1e-4):
    return all(lo[i] - pad <= p[i] <= hi[i] + pad for i in range(3))


def _per(opt, name, hero_name, default=None):
    """An option given for the hero (plain value) or per object ({name: value})."""
    if isinstance(opt, dict):
        return opt.get(name, default)
    return opt if name == hero_name else default


# ---- one object, measured once ------------------------------------------------------------------------------------
class _Obj:
    """bmesh, shells (face lists, coordinates, boxes, lazy BVHs) and labels of one mesh object."""

    def __init__(self, o, frame="build"):
        self.o = o
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        self.bm = bm
        ids, n = M._shell_ids(bm)
        self.n = n
        self.fsh = [ids[f.index] for f in bm.faces]
        self.groups = [[] for _ in range(n)]
        for f in bm.faces:
            self.groups[ids[f.index]].append(f)
        self.sv, self.sp, self.lo, self.hi = [], [], [], []
        for fs in self.groups:
            vs = list({v for f in fs for v in f.verts})
            vi = {v: i for i, v in enumerate(vs)}
            co = [v.co.copy() for v in vs]
            self.sv.append(co)
            self.sp.append([[vi[v] for v in f.verts] for f in fs])
            self.lo.append(Vector((min(c.x for c in co), min(c.y for c in co), min(c.z for c in co))))
            self.hi.append(Vector((max(c.x for c in co), max(c.y for c in co), max(c.z for c in co))))
        self._trees = {}
        self._all = None
        offk = next((k for k in o.keys() if k.endswith("_offset") and len(o[k]) == 3), None) \
            if hasattr(o, "keys") else None
        self.offset_key = offk
        self.frame = "build" if (frame == "build" and offk) else "local"
        self.off = Vector(tuple(o[offk])) if self.frame == "build" else Vector()
        self.labels, self.registry = self._label(offk)

    def _label(self, offk):
        o = self.o
        pk = next((k for k in o.keys() if k.endswith("_pieces")), None)
        reg = []
        if pk and offk:
            try:
                reg = [(k, nm, Vector(c)) for k, nm, c in json.loads(o[pk])]
            except (ValueError, TypeError):
                reg = []
        off = Vector(tuple(o[offk])) if offk else Vector()
        mats = [m.name[3:] if m and m.name.startswith("FB_") else (m.name if m else "none") for m in o.data.materials]
        pre = (o.get("kit_sheet") or "").lower() + "_"
        labels, used = [], set()
        for k, fs in enumerate(self.groups):
            lab = None
            if reg:
                c = sum(self.sv[k], Vector()) / len(self.sv[k]) + off
                best = min(((i, (rc - c).length) for i, (_, _, rc) in enumerate(reg) if i not in used),
                           key=lambda x: x[1], default=(None, 9))
                if best[0] is not None and best[1] < 0.06:
                    used.add(best[0])
                    lab = tuple(reg[best[0]][:2])
            if lab is None:
                area = {}
                for f in fs:
                    mi = min(f.material_index, len(mats) - 1) if mats else 0
                    area[mi] = area.get(mi, 0.0) + f.calc_area()
                key = mats[max(area, key=area.get)] if mats else "none"
                key = key[len(pre):] if pre != "_" and key.startswith(pre) else key
                lab = (key, f"{key}#{k}")
            labels.append(lab)
        return labels, bool(reg)

    def tree(self, k):
        t = self._trees.get(k)
        if t is None:
            t = self._trees[k] = BVHTree.FromPolygons(self.sv[k], self.sp[k])
        return t

    def all_tree(self):
        if self._all is None:
            self._all = BVHTree.FromBMesh(self.bm)
        return self._all

    def sub_tree(self, keep):
        """BVH of the shells k with keep(k), and the shell of each of its faces."""
        cos, polys, owner = [], [], []
        for k in range(self.n):
            if not keep(k):
                continue
            base = len(cos)
            cos += self.sv[k]
            polys += [[base + i for i in p] for p in self.sp[k]]
            owner += [k] * len(self.sp[k])
        return (BVHTree.FromPolygons(cos, polys) if polys else None), owner

    def L(self, p):
        """An option point (frame) -> mesh frame."""
        return Vector(p) - self.off

    def F(self, p):
        """A mesh-frame point -> the report frame."""
        return _v(Vector(p) + self.off)

    def name(self, k):
        return self.labels[k][1]

    def free(self):
        self.bm.free()


# ---- per-object checks ----------------------------------------------------------------------------------------------
AUDIT_KEYS = ("tris", "faces", "verts", "ngons", "nonmanifold_edges", "nonmanifold_verts", "boundary_edges",
              "wire_edges", "loose_verts", "zero_area_faces", "dup_verts", "shells", "normals")


def _basic(X, budget, size, size_tol, origin_tol, P):
    o = X.o
    au = M.audit(o)
    out = {k: au[k] for k in AUDIT_KEYS}
    out["bowties"] = au["nonmanifold_verts"]
    out["budget"] = budget
    out["kit_budget"] = o.get("kit_budget")
    out["size"] = [_r(d) for d in o.dimensions]
    out["origin_offset"] = au["origin_offset"]
    rot_ok = o.matrix_basis.to_3x3().to_quaternion().angle < 1e-6
    out["transforms_applied"] = bool(rot_ok and all(abs(s - 1) < 1e-6 for s in o.scale))
    out["modifiers"] = [m.name for m in o.modifiers]
    out["custom_normals"] = o.data.has_custom_normals
    nm = o.name
    if out["tris"] > budget:
        P.append(f"{nm}: {out['tris']} tris over the budget {budget}")
    for k in ("ngons", "nonmanifold_edges", "bowties", "boundary_edges", "wire_edges", "loose_verts",
              "zero_area_faces", "dup_verts"):
        if out[k]:
            P.append(f"{nm}: {k} {out[k]}")
    if out["normals"] != "outward":
        P.append(f"{nm}: normals {out['normals']}")
    ox, oy, oz = au["origin_offset"]
    if abs(ox) > origin_tol or abs(oy) > origin_tol or abs(oz) > 0.005:
        P.append(f"{nm}: origin not at the bottom centre (offset {au['origin_offset']})")
    if not out["transforms_applied"]:
        P.append(f"{nm}: transforms not applied (rotation {_v(o.rotation_euler)}, scale {_v(o.scale)})")
    if out["modifiers"]:
        P.append(f"{nm}: modifiers {out['modifiers']}")
    if out["custom_normals"]:
        P.append(f"{nm}: custom split normals")
    if size:
        tols = size if isinstance(size[0], (tuple, list)) else [(s, size_tol) for s in size]
        for (tgt, tol), got, ax in zip(tols, o.dimensions, "WDH"):
            if abs(got - tgt) > tol + 1e-6:
                P.append(f"{nm}: {ax} {got:.3f} outside {tgt} +- {tol}")
    return out


def _shells(X, P):
    """Per shell: winding errors (edge direction), self-intersecting face pairs, signed volume, faces whose normal
    points inward by ray parity; and the smallest face corner."""
    rows = []
    tot = {"winding_errors": 0, "self_hits": 0, "parity_inward": 0, "negative_volume": 0}
    for k, fs in enumerate(X.groups):
        es = {e for f in fs for e in f.edges}
        wind = sum(1 for e in es if e.is_manifold and not e.is_contiguous)
        tree = X.tree(k)
        polys = X.sp[k]
        hits = sum(1 for a, b in tree.overlap(tree) if a < b and not set(polys[a]) & set(polys[b]))
        vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs) / 3.0
        bad = 0
        for f in fs:
            if f.calc_area() < 1e-6:
                continue
            if _parity_in(tree, f.calc_center_median() + f.normal * 1e-3):
                bad += 1
        tot["winding_errors"] += wind
        tot["self_hits"] += hits
        tot["parity_inward"] += bad
        tot["negative_volume"] += vol <= 0
        if wind or hits or bad or vol <= 0:
            rows.append({"shell": k, "name": X.name(k), "winding_errors": wind, "self_hits": hits,
                         "parity_inward": bad, "volume": _r(vol, 5)})
    nm = X.o.name
    for r in rows:
        P.append(f"{nm} shell {r['shell']} ({r['name']}): winding {r['winding_errors']}, self-hits {r['self_hits']}, "
                 f"parity-inward {r['parity_inward']}, volume {r['volume']}")
    if X.registry:
        un = sum(1 for k in range(X.n) if X.labels[k][1].startswith(X.labels[k][0] + "#"))
        tot["unmatched_to_register"] = un
    angs = [_fmin([v.co for v in f.verts]) for f in X.bm.faces]
    tot["min_corner_deg"] = _r(math.degrees(min(angs)), 3) if angs else None
    tot["corners_under_3deg"] = sum(1 for a in angs if a < math.radians(3))
    tot["bad_shells"] = rows[:20]
    kinds = {}
    for k in range(X.n):
        kk = kinds.setdefault(X.labels[k][0], {"n": 0, "tris": 0})
        kk["n"] += 1
        kk["tris"] += sum(len(f.verts) - 2 for f in X.groups[k])
    tot["kinds"] = kinds
    return tot


def _contact(X, tol, chain, ground_z, P):
    """No floating shells (STAGES): each shell's nearest gap to another shell (0 where their triangles cross) or the
    ground, and whether it chains by contact (<= tol) to a grounded shell. Long faces are sampled too."""
    n = X.n
    tree = X.all_tree()
    fsh = X.fsh
    near = {}

    def add(s, p):
        for loc, nrm, fi, d in tree.find_nearest_range(p, chain):
            t = fsh[fi]
            if t != s:
                kk = (s, t) if s < t else (t, s)
                if d < near.get(kk, 9.0):
                    near[kk] = d
    for k in range(n):
        for co in X.sv[k]:
            add(k, co)
    for f in X.bm.faces:
        cs = [v.co for v in f.verts]
        if len(cs) < 3:
            continue
        L = max((cs[i] - cs[i - 1]).length for i in range(len(cs)))
        if L < 0.6:
            continue
        m = int(math.ceil(L / 0.3))
        s = fsh[f.index]
        for t in range(1, len(cs) - 1):
            a, b, c = cs[0], cs[t], cs[t + 1]
            for i in range(m + 1):
                for j in range(m + 1 - i):
                    if (i, j) in ((0, 0), (m, 0), (0, m)):
                        continue
                    add(s, a + (b - a) * (i / m) + (c - a) * (j / m))
    for i, j in tree.overlap(tree):
        a, b = fsh[i], fsh[j]
        if a != b:
            near[(min(a, b), max(a, b))] = 0.0
    ground = {k for k in range(n) if X.lo[k].z - ground_z <= tol}
    gap = [9.0] * n
    for (a, b), d in near.items():
        gap[a] = min(gap[a], d)
        gap[b] = min(gap[b], d)
    for k in ground:
        gap[k] = 0.0
    if n == 1:
        gap = [0.0]

    def unchained(t):
        adj = {k: set() for k in range(n)}
        for (a, b), d in near.items():
            if d <= t:
                adj[a].add(b)
                adj[b].add(a)
        seen = set(ground) if ground else {min(range(n), key=lambda k: X.lo[k].z)}
        stack = list(seen)
        while stack:
            k = stack.pop()
            for m_ in adj[k]:
                if m_ not in seen:
                    seen.add(m_)
                    stack.append(m_)
        return [k for k in range(n) if k not in seen]
    flo = [k for k in range(n) if gap[k] > tol]
    unch = unchained(tol)
    out = {"shells": n, "floating": len(flo), "floating_names": [X.name(k) for k in flo][:20],
           "worst_gap": _r(max([gap[k] for k in flo], default=0.0)),
           "unchained": len(unch), "unchained_names": [X.name(k) for k in unch][:20],
           "unchained_at_chain": len(unchained(chain)), "grounded": len(ground),
           "lowest_z": _r(min(lo.z for lo in X.lo) if n else 0.0)}
    if flo or unch:
        P.append(f"{X.o.name}: floating {out['floating_names']}, unchained {out['unchained_names']}")
    return out


def _bury_limit(ka, kb, limit, pairs):
    for (a, b), lim in pairs.items():
        if a in ka and b in kb:
            return lim
    return limit


def _bury(X, limit, pairs, edges, P):
    """Nothing buried (STAGES): per shell pair, the deepest sample point of one (verts, face centres and, with edges,
    edge midpoints) inside the other (nearest-face side, confirmed by ray parity), against the limit; and shells
    wholly inside others. (The m064-m070 builders sample verts and face centres only; edge midpoints find edges
    sunk deeper than either end.)"""
    n = X.n
    pts = []
    for k in range(n):
        fs = X.groups[k]
        es = {e for f in fs for e in f.edges} if edges else ()
        pts.append(list(X.sv[k]) + [f.calc_center_median() for f in fs] +
                   [(e.verts[0].co + e.verts[1].co) / 2 for e in es])
    worst, over, hidden = {}, [], []
    lo, hi = X.lo, X.hi
    for s in range(n):
        inside_any = [False] * len(pts[s])
        for t in range(n):
            if s == t or any(hi[s][i] < lo[t][i] - 1e-4 or lo[s][i] > hi[t][i] + 1e-4 for i in range(3)):
                continue
            tree = X.tree(t)
            dmax = 0.0
            for j, p in enumerate(pts[s]):
                if not _in_box(p, lo[t], hi[t]):
                    continue
                ins, d = _inside(tree, p)
                if ins:
                    inside_any[j] = True
                    dmax = max(dmax, d)
            if dmax <= 0:
                continue
            ka, kb = X.labels[s][0], X.labels[t][0]
            key = f"{ka}>{kb}"
            worst[key] = max(worst.get(key, 0.0), dmax)
            lim = _bury_limit(ka, kb, limit, pairs)
            if dmax > lim + 1e-3:
                over.append({"shell": X.name(s), "in": X.name(t), "depth": _r(dmax)})
        if n > 1 and all(inside_any):
            hidden.append(X.name(s))
    out = {"worst_by_kind": {k: _r(v) for k, v in sorted(worst.items(), key=lambda kv: -kv[1])[:15]},
           "deepest": _r(max(worst.values(), default=0.0)), "over_limit": over[:20], "fully_hidden": hidden[:20],
           "buried": len(over) + len(hidden)}
    if out["buried"]:
        P.append(f"{X.o.name}: buried {over[:6]} hidden {hidden[:6]}")
    return out


def _pierce(X, thin_keys, P):
    """Thin sheets hide pass-throughs from the bury check: count every other shell's edges that cross a thin shell's
    surface twice (in one side, out the other)."""
    thin = [k for k in range(X.n) if any(t in X.labels[k][0] for t in thin_keys)]
    out = {"thin_shells": len(thin), "edges": {}}
    if not thin:
        return out
    ts = set(thin)
    tree, _ = X.sub_tree(lambda k: k in ts)
    for k in range(X.n):
        if k in ts:
            continue
        lo, hi = X.lo[k], X.hi[k]
        bad = 0
        for e in {e for f in X.groups[k] for e in f.edges}:
            p, q = e.verts[0].co, e.verts[1].co
            d = q - p
            L = d.length
            if L < 1e-6:
                continue
            d = d / L
            hits, t0 = 0, 0.0
            while t0 < L and hits < 2:
                h = tree.ray_cast(p + d * (t0 + 1e-4), d, L - t0 - 1e-4)
                if h[0] is None:
                    break
                hits += 1
                t0 = (h[0] - p).length + 1e-4
            bad += hits >= 2
        if bad:
            out["edges"][X.name(k)] = bad
    out["pierced_by"] = len(out["edges"])
    if out["edges"]:
        P.append(f"{X.o.name}: edges passing through thin sheets {dict(list(out['edges'].items())[:8])}")
    return out


def _uv(o, gap, border, P):
    u = M.uv_stats(o)
    if u.get("uv_layer") is None:
        P.append(f"{o.name}: no UV layer")
        return u
    keep = {k: u[k] for k in ("uv_layer", "islands", "overlap_pairs", "overlap_cross_island", "flipped", "min_gap",
                              "border", "density", "stretch_conformal_p95") if k in u}
    keep["uv_layers"] = [x.name for x in o.data.uv_layers]
    if u["overlap_pairs"] or u["flipped"]:
        P.append(f"{o.name}: UV overlaps {u['overlap_pairs']} flipped {u['flipped']}")
    if u["min_gap"] is not None and u["min_gap"] < gap:
        P.append(f"{o.name}: UV island gap {u['min_gap']} under {gap}")
    if u["border"] < border:
        P.append(f"{o.name}: UV border {u['border']} under {border}")
    return keep


def _hexv(h):
    h = (h or "#808080").lstrip("#")
    return max(int(h[i:i + 2], 16) for i in (0, 2, 4)) / 255.0


def _wcorr(x, y, w):
    mx, my = np.average(x, weights=w), np.average(y, weights=w)
    sx = math.sqrt(np.average((x - mx) ** 2, weights=w))
    sy = math.sqrt(np.average((y - my) ** 2, weights=w))
    if sx < 1e-6 or sy < 1e-6:
        return 0.0
    return float(np.average((x - mx) * (y - my), weights=w) / (sx * sy))


def _colour(X, limit, P):
    """Colour by role, never by facing (STAGES stage 4). Per material, the area-weighted correlation of the face Tint
    with the face normal (x, y, z, |z|), worst axis: `within` takes each shell's own mean Tint out first, so per-piece
    tints (a role or random per piece) don't count and only shading painted across a piece's faces does (judged);
    `raw` is the plain correlation (reported). The whole object's value (material V x Tint) against the normal is
    reported only (role colours such as pale cut ends may follow facing legitimately)."""
    o = X.o
    me = o.data
    if not me.polygons:
        return {}
    tint = me.color_attributes.get("Tint")
    n = len(me.polygons)
    t = np.ones(n)
    if tint is not None and tint.domain == "CORNER":
        c = np.zeros(len(tint.data) * 4, np.float32)
        tint.data.foreach_get("color", c)
        c = c.reshape(-1, 4)[:, 0]
        ls = np.zeros(n, np.int64)
        lt = np.zeros(n, np.int64)
        me.polygons.foreach_get("loop_start", ls)
        me.polygons.foreach_get("loop_total", lt)
        t = np.array([c[a:a + b].mean() for a, b in zip(ls, lt)])
    nrm = np.zeros(n * 3, np.float32)
    me.polygons.foreach_get("normal", nrm)
    nrm = nrm.reshape(-1, 3)
    area = np.zeros(n, np.float32)
    me.polygons.foreach_get("area", area)
    mi = np.zeros(n, np.int64)
    me.polygons.foreach_get("material_index", mi)
    axes = {"x": nrm[:, 0], "y": nrm[:, 1], "z": nrm[:, 2], "|z|": np.abs(nrm[:, 2])}
    tot = area.sum() or 1.0
    sh = np.array(X.fsh)
    resid = t.copy()
    for key_ in set(zip(sh.tolist(), mi.tolist())):
        sel = (sh == key_[0]) & (mi == key_[1])
        resid[sel] = t[sel] - np.average(t[sel], weights=np.maximum(area[sel], 1e-9))
    per = {}
    worst = (0.0, None)
    for k, m in enumerate(me.materials):
        sel = mi == k
        if sel.sum() < 12 or area[sel].sum() < 0.05 * tot:
            continue
        key = m.name[3:] if m and m.name.startswith("FB_") else (m.name if m else "none")
        raw = {ax: _wcorr(t[sel], v[sel], area[sel]) for ax, v in axes.items()}
        win = {ax: _wcorr(resid[sel], v[sel], area[sel]) for ax, v in axes.items()}
        ax = max(win, key=lambda a: abs(win[a]))
        axr = max(raw, key=lambda a: abs(raw[a]))
        spread = math.sqrt(np.average(resid[sel] ** 2, weights=area[sel]))
        pieces = len(set(sh[sel].tolist()))
        per[key] = {"within": _r(win[ax]), "axis": ax, "within_spread": _r(spread, 4), "raw": _r(raw[axr]),
                    "raw_axis": axr, "faces": int(sel.sum()), "shells": pieces}
        # judged only where shading painted inside pieces could show and the sample means something: >= 24 faces
        # over >= 4 shells and a Tint spread of >= 1.5 % (one small box's position mottling is not facing)
        if sel.sum() >= 24 and pieces >= 4 and spread >= 0.015 and abs(win[ax]) > abs(worst[0]):
            worst = (win[ax], key)
    val = np.array([_hexv(me.materials[min(i, len(me.materials) - 1)].get("flintkit_hex"))
                    if len(me.materials) else 0.5 for i in mi]) * t
    whole = {ax: _r(_wcorr(val, v, area)) for ax, v in axes.items()}
    out = {"tint_vs_normal": per, "worst": _r(worst[0]), "worst_material": worst[1], "value_vs_normal": whole}
    if abs(worst[0]) > limit and not o.get("kit_shading_ok"):
        P.append(f"{o.name}: Tint follows the face normal on {worst[1]} (corr {worst[0]:.2f} > {limit})")
    return out


def _sockets_stored(X, want_kinds, want_props, P):
    o = X.o
    socks = [c for c in o.children_recursive if c.get("vfx_kind")]
    pre = (o.get("kit_sheet") or "").lower() + "_"
    stored = {}
    for k in o.keys():
        if pre != "_" and k.startswith(pre) and not k.endswith(("_pieces", "_ropes", "_leaves")):
            v = o[k]
            v = v.to_dict() if hasattr(v, "to_dict") else v.to_list() if hasattr(v, "to_list") else v
            stored[k] = v
    out = {"sockets": [{"kind": c["vfx_kind"], "at": X.F(c.matrix_local.translation)} for c in socks],
           "glow_keys": sorted({m.name[3:] for m in o.data.materials
                                if m and list(m.get("flintkit_spec", [0, 0, 0]))[2] > 0}),
           "stored": stored}
    if want_kinds is not None:
        got = sorted(c["vfx_kind"] for c in socks)
        if got != sorted(want_kinds):
            P.append(f"{o.name}: sockets {got} ({sorted(want_kinds)} wanted)")
    for p in want_props or ():
        if p not in o.keys():
            P.append(f"{o.name}: stored point {p} missing")
    return out


# ---- optional checks ------------------------------------------------------------------------------------------------
def _leaves(X, keys, max_thick):
    out, skipped = [], 0
    for k in range(X.n):
        kind = X.labels[k][0]
        if not any(key in kind for key in keys):
            continue
        co = np.array([tuple(c) for c in X.sv[k]])
        if len(co) < 3:
            continue
        w, vec = np.linalg.eigh(np.cov((co - co.mean(axis=0)).T))
        if w[0] < 0 or math.sqrt(max(w[0], 0) / max(w[2], 1e-12)) > max_thick:
            skipped += 1
            continue
        nL = Vector(vec[:, 0])
        A = [f.normal * f.calc_area() for f in X.groups[k]]
        best = None
        for s in (1, -1):
            top = [a for a in A if a.length > 1e-9 and a.normalized().dot(nL * s) > 0.3]
            ta = sum(a.length for a in top)
            if best is None or ta > best[0] + 1e-9:
                best = (ta, top, nL * s)
        ta, top, nn = best
        if not top:
            continue
        out.append({"name": X.name(k), "n": nn, "top": np.array([tuple(a) for a in top]), "top_area": ta,
                    "face_on": sum(a.dot(nn) for a in top)})
    return out, skipped


def _foliage(X, opt, P):
    keys = opt.get("keys", LEAF_KEYS)
    lv, skipped = _leaves(X, keys, opt.get("max_thick", 0.5))
    res = {"leaves": len(lv), "skipped_thick": skipped}
    if not lv:
        return res
    tot = sum(l["face_on"] for l in lv)
    limit = opt.get("limit", 0.10)
    for el in opt.get("els", (0, 5, 10, 20)):
        worst, worst_az, plane = 0.0, None, 0.0
        for az in range(0, 360, opt.get("step", 5)):
            a_, e_ = math.radians(az), math.radians(el)
            v = np.array((math.sin(a_) * math.cos(e_), -math.cos(a_) * math.cos(e_), math.sin(e_)))
            edge = pl = 0.0
            for l in lv:
                d = l["top"] @ v
                ln = np.linalg.norm(l["top"], axis=1)
                near = ln[np.abs(d) < EDGE15 * ln].sum()
                if near >= 0.75 * l["top_area"] or np.abs(d).sum() < 0.26 * l["face_on"]:
                    edge += l["face_on"]
                if abs(l["n"].dot(Vector(v))) < EDGE15:
                    pl += l["face_on"]
            if edge / tot > worst:
                worst, worst_az = edge / tot, az
            plane = max(plane, pl / tot)
        res[f"e{el}"] = {"worst_whole_edge_on_pct": _r(100 * worst, 1), "at_az": worst_az,
                         "mean_plane_edge_on_max_pct": _r(100 * plane, 1)}
        if worst > limit:
            P.append(f"{X.o.name}: {100 * worst:.1f} % of leaf area wholly edge-on at az {worst_az}, e {el} "
                     f"(limit {100 * limit:.0f} %)")
    return res


def _escape(X, opt, P):
    tree = X.all_tree()
    lo, hi = X.L(opt["box"][0]), X.L(opt["box"][1])
    allow = {k: (X.L(a) - Vector((0.05,) * 3), X.L(b) + Vector((0.05,) * 3)) for k, (a, b) in
             (opt.get("allow") or {}).items()}
    out = {"frame": X.frame, "rays": 0, "escapes": {}, "examples": {}}
    up, down = Vector((0, 0, 1)), Vector((0, 0, -1))

    def enclosed(p, clear):
        if tree.ray_cast(p, up, 500.0)[0] is None or tree.ray_cast(p, down, 500.0)[0] is None:
            return False
        return tree.find_nearest(p)[3] > clear

    def cast(p, d):
        out["rays"] += 1
        if tree.ray_cast(p, d, 500.0)[0] is not None:
            return
        hit = _box_hit(p, d, lo, hi)
        q = p + d * (hit[1] if hit else 0.0)
        reg = next((k for k, (a, b) in allow.items() if _in_box(q, a, b, 0.0)), None)
        if reg is None:
            ax = [abs(q[i] - lo[i]) for i in range(3)] + [abs(q[i] - hi[i]) for i in range(3)]
            reg = ("x-", "y-", "z-", "x+", "y+", "z+")[ax.index(min(ax))]
        out["escapes"][reg] = out["escapes"].get(reg, 0) + 1
        ex = out["examples"].setdefault(reg, [])
        if len(ex) < 6:
            ex.append(X.F(q))
    sp = opt.get("spacing", 1.4)
    cnt = [max(2, int(math.ceil((hi[i] - lo[i]) / sp)) + 1) for i in range(3)]
    pts = []
    for i in range(cnt[0]):
        for j in range(cnt[1]):
            for k in range(cnt[2]):
                p = Vector((lo.x + (hi.x - lo.x) * i / (cnt[0] - 1), lo.y + (hi.y - lo.y) * j / (cnt[1] - 1),
                            lo.z + (hi.z - lo.z) * k / (cnt[2] - 1)))
                if enclosed(p, opt.get("clear", 0.15)):
                    pts.append(p)
    dirs = _fib(opt.get("dirs", 320))
    for p in pts:
        for d in dirs:
            cast(p, d)
    out["points"] = len(pts)
    if opt.get("floor", True):
        low = _fib(opt.get("dirs", 320) // 2, lower=True)
        nf = 0
        cx, cy = max(2, int((hi.x - lo.x) / 1.0) + 1), max(2, int((hi.y - lo.y) / 1.0) + 1)
        for i in range(cx):
            for j in range(cy):
                p = Vector((lo.x + 0.2 + (hi.x - lo.x - 0.4) * i / (cx - 1),
                            lo.y + 0.2 + (hi.y - lo.y - 0.4) * j / (cy - 1), lo.z + 0.05))
                if enclosed(p, 0.02):
                    nf += 1
                    for d in low:
                        cast(p, d)
        out["floor_points"] = nf
    if opt.get("seams", True):
        wall, step, offs = opt.get("wall", 0.6), opt.get("step", 0.1), (-0.0007, 0.0007)
        vco = [v.co for v in X.bm.verts]
        faces = [(0, -1), (0, 1), (1, -1), (1, 1), (2, -1)]          # (axis, side): four walls and the floor
        nseam = 0
        for ax, sg in faces:
            c = lo[ax] if sg < 0 else hi[ax]
            others = [i for i in range(3) if i != ax]
            sel = [v for v in vco if -0.05 <= (v[ax] - c) * sg <= wall + 0.05 and
                   all(lo[i] - 0.3 <= v[i] <= hi[i] + 0.3 for i in others)]
            n = Vector((0, 0, 0))
            n[ax] = sg
            for a_ in others:                                       # seams at each distinct coordinate along a_
                b_ = [i for i in others if i != a_][0]               # swept along b_
                vals = sorted({round(v[a_], 4) for v in sel if lo[a_] < v[a_] < hi[a_]})
                sl = Vector((0, 0, 0))
                sl[b_] = 0.5
                ds = (n, (n + sl).normalized(), (n - sl).normalized())
                for val in vals:
                    for dv in offs:
                        t = lo[b_] + 0.02
                        while t < hi[b_]:
                            p = Vector((0, 0, 0))
                            p[ax] = c - sg * (0.05 if ax == 2 else 0.30)
                            p[a_] = val + dv
                            p[b_] = t
                            if enclosed(p, 0.004):
                                nseam += 1
                                for d in ds:
                                    cast(p, d)
                            t += step
        out["seam_points"] = nseam
    leaks = {k: v for k, v in out["escapes"].items() if k not in allow}
    out["leaks"] = sum(leaks.values())
    out["leak_regions"] = leaks
    out["examples"] = {k: v for k, v in out["examples"].items() if k in leaks}
    if out["leaks"]:
        P.append(f"{X.o.name}: inside escape scan: {out['leaks']} rays out of the interior outside "
                 f"{sorted(allow)} {leaks}")
    return out


def _proxy_samples(boxes, fwd, side):
    out = []
    for hx, hy, z0, z1 in boxes:
        for i in range(9):
            for j in range(9):
                u, w = -1 + 2 * i / 8, -1 + 2 * j / 8
                z = Vector((0, 0, z0 + (z1 - z0) * j / 8))
                out += [side * (hx * u) - fwd * hy + z, side * (hx * u) + fwd * hy + z, -side * hx + fwd * (hy * u) + z,
                        side * hx + fwd * (hy * u) + z, side * (hx * u) + fwd * (hy * w) + Vector((0, 0, z1))]
    return out


def _proxy_mesh(boxes, fwd, side, base):
    cos, polys = [], []
    for hx, hy, z0, z1 in boxes:
        b = len(cos)
        for z in (z0, z1):
            for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                cos.append(base + side * (hx * sx) + fwd * (hy * sy) + Vector((0, 0, z)))
        polys += [[b + i for i in f] for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6),
                                                (3, 0, 4, 7))]
    return BVHTree.FromPolygons(cos, polys)


def _walk(X, opt, P):
    skip = tuple(opt.get("skip", ()))
    full = X.all_tree()
    ctree, cown = X.sub_tree(lambda k: not (skip and (X.labels[k][1].startswith(skip) or
                                                      X.labels[k][0].startswith(skip))))
    proxy = opt.get("proxy", "box")
    boxes = PROXY if proxy in ("box", None) else (proxy if not isinstance(proxy, str) else PROXY)
    capsule = proxy == "capsule"
    rad, height = opt.get("radius", 1.0), opt.get("height", 5.5)
    ride, feet_z = opt.get("ride", True), opt.get("feet_z", 0.0)
    lift = opt.get("lift", 0.10 if ride else 0.0)
    span = max(b[0] for b in boxes)
    top = height if capsule else max(b[3] for b in boxes)

    ground = X.L((0, 0, feet_z)).z
    max_rise = opt.get("max_rise", 1.0)

    def base_at(c, fwd, side, zprev):
        """The highest surface under the footprint that a step from zprev can reach (rays down from zprev +
        max_rise), or the ground."""
        if not ride:
            return ground
        z = ground
        for a in (-0.95, 0.0, 0.95):
            for b in (-0.45, 0.0, 0.45):
                q = c + side * (a * span) + fwd * b
                h = full.ray_cast(Vector((q.x, q.y, zprev + max_rise + 0.05)), Vector((0, 0, -1)), 200.0)
                if h[0] is not None:
                    z = max(z, h[0].z)
        return z

    def clear_at(c, zb, fwd, side):
        if ctree is None:
            return 9.0, None, 0
        if capsule:
            best = (9.0, None)
            z = zb + lift + rad
            while z <= zb + lift + height - rad + 1e-6:
                loc, nrm, fi, d = ctree.find_nearest(Vector((c.x, c.y, z)))
                if loc is not None and d - rad < best[0]:
                    best = (d - rad, cown[fi])
                z += 0.1
            return best[0], best[1], 0
        base = Vector((c.x, c.y, zb + lift))
        best = (9.0, None)
        for q in _proxy_samples(boxes, fwd, side):
            loc, nrm, fi, d = ctree.find_nearest(base + q)
            if loc is not None and d < best[0]:
                best = (d, cown[fi])
        hits = len(ctree.overlap(_proxy_mesh(boxes, fwd, side, base)))
        return best[0], best[1], hits
    res = {"frame": X.frame, "proxy": "capsule" if capsule else [list(b) for b in boxes], "paths": []}
    for path in opt["paths"]:
        pts = [X.L((p[0], p[1], 0.0)) for p in path]
        worst, at, who, inter, prof, head = 9.0, None, None, 0, [], (99.0, None)
        zb = ground
        for a, b in zip(pts, pts[1:]):
            d = b - a
            d.z = 0
            L = d.length
            fwd = d.normalized()
            side = Vector((fwd.y, -fwd.x, 0))
            for s in range(int(L / opt.get("step", 0.1)) + 1):
                c = a + fwd * min(L, s * opt.get("step", 0.1))
                zb = base_at(c, fwd, side, zb)
                if not prof or abs(prof[-1][1] - zb) > 1e-3:
                    prof.append((X.F(c)[:2], zb))
                cl, nm, hits = clear_at(c, zb, fwd, side)
                inter += hits > 0
                if cl < worst:
                    worst, at, who = cl, X.F(c)[:2], (X.name(nm) if nm is not None else None)
                for u in (-span, 0.0, span):
                    q = c + side * u
                    z_up = zb + lift + 0.05 + (0.0 if capsule else min(b[2] for b in boxes))
                    h = ctree.ray_cast(Vector((q.x, q.y, z_up)), Vector((0, 0, 1)), 200.0) if ctree else (None,)
                    if h[0] is not None and h[0].z - zb < head[0]:
                        head = (h[0].z - zb, X.F(q)[:2])
        rises = [_r(prof[i][1] - prof[i - 1][1]) for i in range(1, len(prof))]
        row = {"path": [list(p) for p in path], "min_clearance": _r(worst), "at": at, "nearest": who,
               "intersecting_steps": inter, "rises": rises, "surface": [[p, _r(z + X.off.z)] for p, z in prof][:20],
               "headroom": _r(head[0]) if head[0] < 99 else None, "headroom_at": head[1]}
        res["paths"].append(row)
        tag = f"{X.o.name}: walk {row['path'][0]} -> {row['path'][-1]}"
        if worst < opt.get("clear", 0.10) or inter:
            P.append(f"{tag}: clearance {row['min_clearance']} at {at} ({who}), {inter} intersecting steps")
        if any(abs(r) > opt.get("max_rise", 1.0) for r in rises):
            P.append(f"{tag}: rises {rises} over {opt.get('max_rise', 1.0)}")
        if row["headroom"] is not None and row["headroom"] < top + lift:
            P.append(f"{tag}: headroom {row['headroom']} at {row['headroom_at']} under {top + lift:.2f}")
    turns = []
    for t in opt.get("turn", ()):
        c = X.L((t[0], t[1], 0.0))
        best, inter = (9.0, None, None), 0
        z0 = X.L((0, 0, t[2])).z if len(t) > 2 else None      # (x, y, z): the floor height to stand on
        for yaw in range(0, 181, 15):
            fwd = Vector((math.sin(math.radians(yaw)), math.cos(math.radians(yaw)), 0))
            side = Vector((fwd.y, -fwd.x, 0))
            zb = base_at(c, fwd, side, z0 if z0 is not None else ground)
            cl, nm, hits = clear_at(c, zb, fwd, side)
            inter += hits > 0
            if cl < best[0]:
                best = (cl, yaw, X.name(nm) if nm is not None else None)
        turns.append({"at": list(t), "min_clearance": _r(best[0]), "yaw": best[1], "nearest": best[2],
                      "intersecting_yaws": inter})
        if best[0] < opt.get("clear", 0.10) or inter:
            P.append(f"{X.o.name}: turning at {list(t)}: clearance {_r(best[0])} ({best[2]}), {inter} "
                     f"intersecting yaws")
    res["turn"] = turns
    return res


def _tri_arrays(X):
    cos = [v.co + X.off for v in X.bm.verts]
    polys = [[v.index for v in f.verts] for f in X.bm.faces]
    return cos, polys


def _seams(XA, XB, opt, P):
    pitch = Vector(opt.get("pitch", (16.0, 0.0, 0.0)))
    ax = max(range(3), key=lambda i: abs(pitch[i]))
    if pitch[ax] < 0:
        pitch = -pitch
    tol = opt.get("tol", 0.001)
    half = pitch[ax] / 2
    out = {"frame": XA.frame, "pitch": _v(pitch), "pairs": {}}

    s_ax = 2 if ax != 2 else 1                      # slice the end faces across this axis (height)
    q_ax = 3 - ax - s_ax

    def section(X, hi_end):
        """The end plane's coordinate, the faces lying in it (as coordinate lists) and their range along s_ax."""
        cos, polys = _tri_arrays(X)
        e = max(c[ax] for c in cos) if hi_end else min(c[ax] for c in cos)
        fs = [[cos[i] for i in p] for p in polys if all(abs(cos[i][ax] - e) <= tol for i in p)]
        ss = [c[s_ax] for f in fs for c in f]
        return e, fs, ((min(ss), max(ss)) if ss else None)

    def width(fs, s):
        """(min, max) along q_ax of the end faces' cut at s."""
        qs = []
        for f in fs:
            for i in range(len(f)):
                a, b = f[i - 1], f[i]
                if (a[s_ax] - s) * (b[s_ax] - s) <= 0 and abs(b[s_ax] - a[s_ax]) > 1e-9:
                    t = (s - a[s_ax]) / (b[s_ax] - a[s_ax])
                    qs.append(a[q_ax] + (b[q_ax] - a[q_ax]) * t)
        return (min(qs), max(qs)) if qs else None
    objs = {XA.o.name: XA}
    if XB is not None:
        objs[XB.o.name] = XB
    for nm, X in objs.items():
        cos, _ = _tri_arrays(X)
        vals = [c[ax] for c in cos]
        past = sum(1 for v in vals if abs(v) > half + 0.001)
        out[nm] = {"extent": [_r(min(vals), 4), _r(max(vals), 4)], "past_seam": past}
        if past:
            P.append(f"{nm}: {past} verts past the seam planes +-{half}")
    pairs = [(XA, XA)] + ([(XA, XB), (XB, XA), (XB, XB)] if XB is not None else [])
    for A, B in pairs:
        ca, pa = _tri_arrays(A)
        cb, pb = _tri_arrays(B)
        ta = BVHTree.FromPolygons(ca, pa)
        tb = BVHTree.FromPolygons([c + pitch for c in cb], pb)
        crossing = len(ta.overlap(tb))
        close = min(min(tb.find_nearest(c)[3] for c in ca), min(ta.find_nearest(c + pitch)[3] for c in cb))
        ea, fa, ra = section(A, True)
        eb, fb, rb = section(B, False)
        worst, common = None, None
        if ra and rb:
            lo_, hi_ = max(ra[0], rb[0]), min(ra[1], rb[1])
            common = [_r(lo_), _r(hi_)]
            worst = 0.0
            for i in range(41):
                s = lo_ + (hi_ - lo_) * (0.002 + 0.996 * i / 40)
                wa, wb = width(fa, s), width(fb, s)
                if wa is None or wb is None:
                    worst = 9.0
                    break
                worst = max(worst, abs(wa[0] - wb[0]), abs(wa[1] - wb[1]))
        same = worst is not None and worst <= 0.002
        key = f"{A.o.name}|{B.o.name}"
        out["pairs"][key] = {"crossing_tri_pairs": crossing, "closest": _r(close, 4),
                             "gap_at_seam": _r(eb + pitch[ax] - ea, 4), "end_faces": [len(fa), len(fb)],
                             "end_ranges": [[_r(x) for x in ra] if ra else None, [_r(x) for x in rb] if rb else None],
                             "common_range": common, "section_mismatch": _r(worst, 4) if worst is not None else None,
                             "same_section": same}
        if crossing:
            P.append(f"{key}: {crossing} triangle pairs cross when tiled at {_v(pitch)}")
        if opt.get("same_section", True) and not same:
            P.append(f"{key}: end sections differ over their common range (mismatch {worst}; flat end faces "
                     f"{len(fa)} / {len(fb)})")
    return out


# ---- entry point ----------------------------------------------------------------------------------------------------
def run(objs, cls="asset", **opts):
    """Every technical check on objs in one call. Returns {"objects": {name: {...}}, optional sections
    ("foliage", "escape", "walk", "seams"), "problems": [...], "secs": {check: seconds}, "total_s"}."""
    t_all = time.time()
    objs = [bpy.data.objects[o] if isinstance(o, str) else o for o in
            (objs if isinstance(objs, (list, tuple)) else [objs])]
    bpy.context.view_layer.update()
    hero = next((o for o in objs if o.get("kit_role") == "hero"), objs[0])
    P, secs, res = [], {}, {"objects": {}}
    frame = opts.get("frame", "build")
    preps = {}

    def timed(key, fn, *a):
        t0 = time.time()
        try:
            return fn(*a)
        finally:
            secs[key] = _r(secs.get(key, 0.0) + time.time() - t0, 2)

    def prep(o):
        if o.name not in preps:
            preps[o.name] = timed("prepare", _Obj, o, frame)
        return preps[o.name]
    try:
        for o in objs:
            X = prep(o)
            role = o.get("kit_role")
            c = (opts.get("classes") or {}).get(o.name) or (cls if o is hero or role in ("hero", "variant") else "part")
            budget = (opts.get("budgets") or {}).get(o.name) or CLASSES[c]
            size = _per(opts.get("size"), o.name, hero.name)
            r = {"class": c, "role": role, "frame": X.frame, "offset": _v(X.off) if X.frame == "build" else None,
                 "labels_from": "register" if X.registry else "material"}
            r.update(timed("basic", _basic, X, budget, size, opts.get("size_tol", 0.05),
                           opts.get("origin_tol", 0.01), P))
            r["shell_checks"] = timed("shells", _shells, X, P)
            r["contact"] = timed("contact", _contact, X, opts.get("contact", CONTACT), opts.get("chain", CHAIN),
                                 opts.get("ground_z", 0.0), P)
            r["bury"] = timed("bury", _bury, X, opts.get("bury", BURY), opts.get("bury_pairs", BURY_PAIRS),
                              opts.get("bury_edges", True), P)
            r["pierce"] = timed("pierce", _pierce, X, opts.get("thin", THIN_KEYS), P)
            floor = opts.get("thin_floor", THIN_FLOOR)
            mc = r["shell_checks"]["min_corner_deg"]
            if mc is not None and mc < floor:
                P.append(f"{o.name}: a face corner of {mc} deg (floor {floor})")
            r["uv"] = timed("uv", _uv, o, opts.get("uv_gap", 0.0159), opts.get("uv_border", 0.0079), P)
            r["colour"] = timed("colour", _colour, X, opts.get("colour_limit", 0.3), P)
            r.update(timed("sockets", _sockets_stored, X, _per(opts.get("sockets"), o.name, hero.name),
                           _per(opts.get("stored"), o.name, hero.name), P))
            if opts.get("kit_check", True):
                r["kit_check"] = timed("kit_check", K.check, [o])
                P.extend(r["kit_check"])
            res["objects"][o.name] = r

        def target(opt):
            nm = opt.get("obj") if isinstance(opt, dict) else None
            return prep(bpy.data.objects[nm] if nm else hero)
        if opts.get("foliage"):
            fo = opts["foliage"] if isinstance(opts["foliage"], dict) else {}
            names = fo.get("objs") or [o.name for o in objs]
            res["foliage"] = {}
            for nm in names:
                X = prep(bpy.data.objects[nm])
                r = timed("foliage", _foliage, X, fo, P)
                if r.get("leaves"):
                    res["foliage"][nm] = r
        if opts.get("escape"):
            res["escape"] = timed("escape", _escape, target(opts["escape"]), opts["escape"], P)
        if opts.get("walk"):
            res["walk"] = timed("walk", _walk, target(opts["walk"]), opts["walk"], P)
        if opts.get("seams"):
            so = opts["seams"] if isinstance(opts["seams"], dict) else {}
            XB = prep(bpy.data.objects[so["with"]]) if so.get("with") else None
            res["seams"] = timed("seams", _seams, target(so), XB, so, P)
    finally:
        for X in preps.values():
            X.free()
    res["problems"] = P
    res["secs"] = secs
    res["total_s"] = _r(time.time() - t_all, 1)
    return res


def summary(res):
    """One line per object (tris / budget, shells, floating, buried, min corner) plus the problem count."""
    rows = []
    for nm, r in res["objects"].items():
        rows.append(f"{nm}: {r['tris']}/{r['budget']} tris, {r['shells']} shells, size {r['size']}, floating "
                    f"{r['contact']['floating']}/{r['contact']['unchained']}, buried {r['bury']['buried']}, deepest "
                    f"{r['bury']['deepest']}, min corner {r['shell_checks']['min_corner_deg']} deg")
    rows.append(f"{len(res['problems'])} problems in {res['total_s']} s")
    return rows
