"""W12 row 4: Barricade (rough log fence) - hero, parts and three variations."""
import math

SUBJECT = "Barricade"
ROW = 4
HERO_AZIMUTH = -22
SIDE_AZIMUTH = 135

PALETTE = {
    "w12_wood": ("#8F5A2C", 0.9, 0, 0),
    "w12_tan": ("#C9985A", 0.9, 0, 0),
    "w12_stone": ("#7E7F8C", 0.95, 0, 0),
    "w12_leaf": ("#3F9A2E", 0.9, 0, 0),
}

W, T, S, L = "w12_wood", "w12_tan", "w12_stone", "w12_leaf"
PI = math.pi


# -- helpers -----------------------------------------------------------------

def _post(a, x, y, h, r=0.55, lean=(0.0, 0.0)):
    v = a.post(r, h, loc=(0, 0, 0), sides=6, mat=W, top_mat=W, chamfer=0.4)
    a.transform(v, (x, y, 0), (lean[0], lean[1], 0))
    return v


def _rail(a, p1, p2, r=0.5):
    return a.beam(p1, p2, r, sides=7, mat=W, end_mat=W, overhang=0.0)


def _wrap_post(a, x, y, z, r=0.55, n=2, th=0.16):
    """Fat rope rings around a vertical post at height z."""
    for i in range(n):
        a.torus(r + th * 0.7, th, loc=(x, y, z + i * th * 1.8), mat=T, seg=8, rseg=4)


def _wrap_rail(a, x, y, z, r=0.5, n=2, th=0.16, dx=1.0):
    """Fat rope rings around a horizontal rail running along X."""
    for i in range(n):
        a.torus(r + th * 0.7, th, loc=(x + (i - (n - 1) / 2) * th * 1.9 * dx, y, z),
                rot=(0, PI / 2, 0), mat=T, seg=8, rseg=4)


def _wrap_rail_y(a, x, y, z, r=0.5, n=2, th=0.16):
    for i in range(n):
        a.torus(r + th * 0.7, th, loc=(x, y + (i - (n - 1) / 2) * th * 1.9, z),
                rot=(PI / 2, 0, 0), mat=T, seg=8, rseg=4)


def _junction(a, x, yp, z, yr=-0.75, th=0.16):
    """Fat X lashing binding a front rail to a post, plus a ring above it."""
    a.lashing((x, (yp + yr) / 2, z), size=0.78, thickness=th, mat=T)
    a.torus(0.55 + th * 0.7, th, loc=(x, yp, z + 0.75), mat=T, seg=8, rseg=4)


def _stone(a, loc, size, rz=0.0):
    size = tuple(c * 1.15 for c in size)
    a.rock(size, loc=loc, rot=(0, 0, rz), mat=S, subdiv=1, rough=0.14, facets=14, sink=0.15)


def _tuft(a, loc, r=0.5):
    r *= 1.35
    a.leaf_cluster(r, loc=loc, mat=L, lobes=7, squash=0.7, facets=1, floor=0.0)


def _floor(a):
    for v in a.bm.verts:
        if v.co.z < 0:
            v.co.z = 0.0


def _angled_beam(a, p1, p2, r, zlo, zhi):
    """Log with horizontal (angled-to-the-log) cut ends: clamp end rings to planes."""
    v = _rail(a, p1, p2, r)
    for vv in v:
        vv.co.z = min(max(vv.co.z, zlo), zhi)
    return v


# -- hero --------------------------------------------------------------------

def _fence(a, length, posts, heights, braces, xbrace=None, stones=(), tufts=(),
           back=True):
    half = length / 2
    yf, yb = -0.75, 0.75
    for x, h, dy in zip(posts, heights, [(-1) ** i * 0.12 for i in range(len(posts))]):
        _post(a, x, dy, h)
    # front rails (in front of the posts)
    _rail(a, (-half, yf, 1.6), (half, yf, 1.7))
    _rail(a, (-half + 0.2, yf, 3.6), (half - 0.1, yf, 3.5))
    # back rails behind the inner post pair
    if back:
        bx = posts[1] - 1.2, posts[-2] + 1.2
        _rail(a, (bx[0], yb, 1.9), (bx[1], yb, 1.8), 0.45)
        _rail(a, (bx[0], yb, 3.3), (bx[1], yb, 3.4), 0.45)
    # front braces
    for (x0, x1) in braces:
        _rail(a, (x0, -1.3, 0.35), (x1, -1.3, 3.6), 0.4)
    if xbrace:
        x0, x1 = xbrace
        _rail(a, (x0, -1.3, 0.35), (x1, -1.3, 3.5), 0.4)
        _rail(a, (x1, -1.3, 0.35), (x0, -1.3, 3.5), 0.4)
    for loc, size, rz in stones:
        _stone(a, loc, size, rz)
    for loc, r in tufts:
        _tuft(a, loc, r)


def _hero(kit):
    fk = kit.flintkit
    a = fk.Asset("Barricade", "W12 Barricade", seed=1204)
    posts = [-4.5, -1.5, 1.5, 4.5]
    stones = [((-3.6, -1.7, 0), (1.5, 1.3, 1.2), 0.3),
              ((-0.4, -1.8, 0), (1.3, 1.1, 1.0), 1.1),
              ((2.8, -1.7, 0), (1.9, 1.5, 1.6), 0.7),
              ((4.3, 1.2, 0), (1.4, 1.2, 1.1), 2.0)]
    tufts = [((-4.9, -1.6, 0), 0.55), ((-2.6, -1.9, 0), 0.5), ((-1.2, -1.0, 0), 0.45),
             ((0.9, -1.9, 0), 0.55), ((1.8, -1.1, 0), 0.45), ((4.4, -1.6, 0), 0.6),
             ((-3.0, 1.0, 0), 0.5), ((0.4, 1.2, 0), 0.5), ((3.0, 1.1, 0), 0.45),
             ((-5.3, -0.6, 0), 0.5), ((-2.0, -1.4, 0), 0.4), ((0.0, -1.5, 0), 0.4),
             ((2.2, -2.0, 0), 0.4), ((5.2, -0.5, 0), 0.45)]
    _fence(a, 10.6, posts, [4.6, 5.5, 5.0, 5.3],
           braces=[(-1.2, -4.2), (1.2, 4.2)], stones=stones, tufts=tufts)
    # rope wraps at junctions
    _junction(a, -4.5, -0.12, 3.6)
    _junction(a, -1.5, 0.12, 3.58)
    _junction(a, 1.5, -0.12, 3.54)
    _junction(a, 4.5, 0.12, 3.5)
    _junction(a, -4.5, -0.12, 1.6)
    _wrap_rail(a, -3.6, -0.75, 3.6, n=2, th=0.19)
    _wrap_rail(a, 3.6, -0.75, 3.5, n=2, th=0.19)
    _floor(a)
    o = a.finish()
    return kit.tag(o, "hero", collision="box", budget=4000,
                   notes="Straight log barricade segment, front -Y. No VFX.")


# -- parts -------------------------------------------------------------------

def _parts(kit):
    fk = kit.flintkit
    out = []

    a = fk.Asset("BarricadeRailLog", "W12 Barricade part", seed=1211)
    _rail(a, (-4, 0, 0.5), (4, 0, 0.5), 0.5)
    _floor(a)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Horizontal rail log with cut ends."))

    a = fk.Asset("BarricadeUprightPost", "W12 Barricade part", seed=1212)
    _post(a, 0, 0, 5.5)
    _wrap_post(a, 0, 0, 3.4, n=3)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Upright post, chamfered flat top, rope wrap."))

    a = fk.Asset("BarricadeDiagonalBrace", "W12 Barricade part", seed=1213)
    d = 5.0 / math.sqrt(2) / 2 + 0.3
    _angled_beam(a, (-d, 0, 2.0 - d), (d, 0, 2.0 + d), 0.4, 0.0, 3.6)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="45 deg brace log with angled flat-cut ends."))

    a = fk.Asset("BarricadeFootCollar", "W12 Barricade part", seed=1214)
    for i, (sz, rz) in enumerate([((1.6, 1.3, 1.3), 0.2), ((1.4, 1.2, 1.0), 1.4),
                                  ((1.5, 1.2, 1.1), 2.6), ((1.3, 1.1, 0.9), 3.9)]):
        ang = i * 2 * PI / 4 + 0.3
        _stone(a, (1.3 * math.cos(ang), 1.3 * math.sin(ang), 0), sz, rz)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500,
                       notes="Ring of foot stones around a 1.4 wide post hole."))

    a = fk.Asset("BarricadeStake", "W12 Barricade part", seed=1215)
    a.stake(0.4, 5.0, tip=1.1, loc=(0, 0, 0), sides=7, mat=W, tip_mat=T)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Sharpened ground stake, pale tan tip up."))
    return out


# -- variants ----------------------------------------------------------------

def _straight(kit):
    fk = kit.flintkit
    a = fk.Asset("BarricadeStraight", "W12 Barricade variant", seed=1221)
    posts = [-4.0, 0.0, 4.0]
    half = 4.6
    for x, h in zip(posts, [5.0, 5.4, 4.7]):
        _post(a, x, 0, h)
    _rail(a, (-half, -0.75, 1.6), (half, -0.75, 1.7))
    _rail(a, (-half, -0.75, 3.6), (half, -0.75, 3.5))
    _rail(a, (-3.6, -1.3, 0.35), (-0.4, -1.3, 3.5), 0.4)
    _rail(a, (-0.4, -1.3, 0.35), (-3.6, -1.3, 3.5), 0.4)
    _junction(a, -4.0, 0, 3.6)
    _junction(a, 0.0, 0, 3.58)
    _junction(a, 4.0, 0, 3.5)
    _wrap_rail(a, -2.0, -0.95, 2.0, r=0.4, n=1)
    _stone(a, (-2.4, -1.7, 0), (1.4, 1.2, 1.1), 0.4)
    _stone(a, (2.6, -1.6, 0), (1.6, 1.3, 1.3), 1.3)
    for loc, r in [((-4.4, -1.5, 0), 0.5), ((-0.8, -1.8, 0), 0.5), ((1.2, -1.5, 0), 0.45),
                   ((4.1, -1.5, 0), 0.55), ((-1.5, 1.0, 0), 0.45), ((2.0, 1.0, 0), 0.45)]:
        _tuft(a, loc, r)
    _floor(a)
    return kit.tag(a.finish(), "variant", collision="box", budget=3500,
                   notes="Straight standard barricade, 3 posts, X brace. No VFX.")


def _corner(kit):
    fk = kit.flintkit
    a = fk.Asset("BarricadeCorner", "W12 Barricade variant", seed=1222)
    # corner post at (0,0); arm A along -X, arm B along +Y
    _post(a, 0, 0, 5.6, r=0.6)
    _post(a, -3.0, 0, 4.8)
    _post(a, -6.0, 0, 5.1)
    _post(a, 0, -3.0, 5.0)
    _post(a, 0, -6.0, 4.6)
    for z in (1.6, 3.6):
        _rail(a, (-6.4, -0.7, z), (0.9, -0.7, z + 0.05))          # arm A, front
        _rail(a, (-0.7, 0.9, z + 0.4), (-0.7, -6.4, z + 0.35))   # arm B, crosses at corner
    # braces in a V toward the corner (outer faces)
    _rail(a, (-4.5, -1.25, 0.35), (-1.6, -1.25, 3.6), 0.4)
    _rail(a, (-1.3, -4.5, 0.35), (-1.3, -1.6, 3.9), 0.4)
    # rope bundle at the corner and wraps
    _wrap_post(a, 0, 0, 1.4, r=0.6, n=2)
    _wrap_post(a, 0, 0, 3.3, r=0.6, n=3)
    _wrap_post(a, -3.0, 0, 3.3)
    _wrap_post(a, 0, -3.0, 3.6)
    _wrap_post(a, 0, -6.0, 3.6)
    _wrap_post(a, -6.0, 0, 3.3)
    _stone(a, (-2.0, -1.8, 0), (1.5, 1.2, 1.2), 0.5)
    _stone(a, (-1.9, -4.6, 0), (1.3, 1.2, 1.0), 1.9)
    _stone(a, (-1.8, -1.8, 0), (1.2, 1.0, 0.9), 0.9)
    for loc, r in [((-5.4, -1.5, 0), 0.5), ((-3.4, -1.6, 0), 0.45), ((-0.6, -1.6, 0), 0.5),
                   ((-1.7, -3.2, 0), 0.5), ((-1.5, -6.2, 0), 0.45), ((-2.9, -2.6, 0), 0.45),
                   ((0.9, 0.9, 0), 0.4), ((-4.8, -2.4, 0), 0.4)]:
        _tuft(a, loc, r)
    _floor(a)
    return kit.tag(a.finish(), "variant", collision="box", budget=3500,
                   notes="90 deg corner barricade, two 6-stud arms. No VFX.")


def _damaged(kit):
    fk = kit.flintkit
    a = fk.Asset("BarricadeDamaged", "W12 Barricade variant", seed=1223)
    # standing / leaning / snapped posts
    _post(a, -4.3, 0, 5.0)
    _post(a, -1.4, 0, 4.4, lean=(0.0, 0.42))
    _post(a, 1.6, 0, 1.9)
    a.cyl(0.5, 0.12, 0.7, 6, loc=(1.7, 0.1, 1.85), rot=(0.25, 0.15, 0), mat=W)  # splintered top
    _post(a, 4.4, 0, 3.8, lean=(-0.3, -0.25))
    # rails: one still up, one fallen diagonally, one on the ground
    _rail(a, (-4.9, -0.75, 3.5), (-0.4, -0.75, 3.3))
    _rail(a, (-4.8, -0.75, 1.6), (2.6, -0.75, 0.45))
    _rail(a, (-0.5, -1.9, 0.5), (4.8, -1.4, 0.5))
    # shattered brace: a stub and a piece on the ground
    _rail(a, (2.4, -1.25, 0.3), (3.4, -1.25, 1.5), 0.4)
    _rail(a, (2.0, 1.1, 0.4), (4.4, 1.6, 0.4), 0.4)
    # splinters / loose logs
    _rail(a, (-3.0, -2.2, 0.15), (-1.6, -2.5, 0.15), 0.15)
    _rail(a, (0.2, 1.3, 0.14), (1.3, 1.9, 0.14), 0.14)
    _rail(a, (3.4, -2.4, 0.13), (4.3, -2.0, 0.13), 0.13)
    # leaning stakes
    v = a.stake(0.35, 3.4, tip=0.8, loc=(0, 0, 0), mat=W, tip_mat=T)
    a.transform(v, (-2.8, 1.1, 0), (-0.35, 0.2, 0))
    v = a.stake(0.32, 3.0, tip=0.7, loc=(0, 0, 0), mat=W, tip_mat=T)
    a.transform(v, (3.2, 0.8, 0), (-0.3, -0.35, 0))
    # rope wraps and a hanging rope
    _wrap_post(a, -4.3, 0, 3.2)
    _wrap_post(a, -4.3, 0, 1.3)
    a.tube_loop([(-1.4 + 0.55, -0.3, 3.0), (-0.6, -0.55, 2.4), (-0.5, -0.7, 1.6),
                 (-0.6, -0.65, 1.0)], 0.13, mat=T, rseg=4, closed=False)
    _stone(a, (-3.4, -1.8, 0), (1.5, 1.2, 1.2), 0.3)
    _stone(a, (0.9, -1.4, 0), (1.3, 1.1, 1.0), 1.5)
    _stone(a, (4.6, 1.2, 0), (1.2, 1.0, 0.9), 2.2)
    for loc, r in [((-4.9, -1.5, 0), 0.5), ((-1.8, -1.7, 0), 0.5), ((2.1, -2.2, 0), 0.45),
                   ((-0.4, 1.3, 0), 0.45), ((4.8, -0.6, 0), 0.5)]:
        _tuft(a, loc, r)
    _floor(a)
    return kit.tag(a.finish(), "variant", collision="box", budget=3500,
                   notes="Collapsed barricade segment with fallen rails, stakes. No VFX.")


def build(kit):
    out = [_hero(kit)]
    out += _parts(kit)
    out += [_straight(kit), _corner(kit), _damaged(kit)]
    return out
