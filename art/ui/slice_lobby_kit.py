"""Slice the lobby kit sheets into clean lk_* sprites + manifest entries.

Inputs : art/reference/ui/lobby/kit/NN_*.png (the owner's kit sheets, RGBA on
         transparent backgrounds). The screen mockups next to them
         (art/reference/ui/lobby/0N_*.png, 1672x941) set each part's size.
Outputs: art/ui/sprites/lk_<name>.png
         the lk_* entries of art/ui/sprites/manifest.json (other entries are kept
         exactly as they are)
         art/ui/kit/contact_dark.png, contact_light.png, slice_test.png

Plain Python with numpy and Pillow:

    python3 art/ui/slice_lobby_kit.py
    uv run --with numpy --with pillow art/ui/slice_lobby_kit.py      # Windows

Every part is a hard-coded box in PARTS (found once with alpha connected
components), so the output is stable and the script is deterministic: running
it twice writes identical files.

Clean-up of every part (the sheets came out of background removal):
  * the faint red/yellow keying fringe (alpha below ~64) and loose specks
    (connected components below a size floor, or whose centre lies outside the
    part's box) are dropped;
  * small pin-holes inside a part are filled, interiors become fully opaque
    (the sheets hold fills at alpha 250-254);
  * alpha is re-ramped so the silhouette keeps a 1-2 px anti-aliased edge;
  * edge pixels take the colour of the nearest solid pixel (no red/yellow tint)
    and colour is bled into fully transparent pixels so bilinear filtering in
    Roblox never pulls in black or red;
  * parts are downscaled with premultiplied Lanczos to their on-screen size.

Text, numbers and placeholder icons baked into a few parts are painted out
(push-pull fill from the surrounding paper or leather plus that material's
grain), so text can be drawn natively. Icons that only exist on a tile are
lifted off it (flood fill of the paper up to the icon's dark outline).
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KIT = ROOT / "art" / "reference" / "ui" / "lobby" / "kit"
OUT = HERE / "sprites"
DOCS = HERE / "kit"
MANIFEST = OUT / "manifest.json"
PREFIX = "lk_"
GLYPH_PREFIXES = ("lk_glyph_ink_", "lk_glyph_white_")
PAD = 8          # source pixels read around each box
EDGE_PAD = 2     # transparent pixels kept around each sprite
MAX_SIDE = 1024

N4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
N8 = N4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]

_sheets = {}


def sheet(sid):
    """RGBA float array (0..1) of kit sheet `sid` ("01".."20")."""
    if sid not in _sheets:
        path = next(KIT.glob(f"{sid}_*.png"))
        _sheets[sid] = np.asarray(Image.open(path).convert("RGBA"), np.float32) / 255.0
    return _sheets[sid]


# ---------------------------------------------------------------------------
# numpy helpers (no scipy)
# ---------------------------------------------------------------------------


def shift(m, dy, dx, fill=0):
    """out[y, x] = m[y - dy, x - dx]"""
    out = np.full_like(m, fill)
    h, w = m.shape[:2]
    out[max(dy, 0):h + min(dy, 0), max(dx, 0):w + min(dx, 0)] = m[max(-dy, 0):h + min(-dy, 0),
                                                                  max(-dx, 0):w + min(-dx, 0)]
    return out


def dilate(m, r=1):
    m = m.copy()
    for _ in range(r):
        o = m.copy()
        for dy, dx in N8:
            o |= shift(m, dy, dx, False)
        m = o
    return m


def erode(m, r=1):
    return ~dilate(~m, r)


def box_blur(x, r):
    """Separable box blur with edge clamping; x is HxW or HxWxC."""
    if r <= 0:
        return x
    k = 2 * r + 1
    for axis in (0, 1):
        pad = [(0, 0)] * x.ndim
        pad[axis] = (r + 1, r)
        c = np.cumsum(np.pad(x, pad, mode="edge"), axis=axis)
        hi = np.take(c, range(k, c.shape[axis]), axis=axis)
        lo = np.take(c, range(0, c.shape[axis] - k), axis=axis)
        x = (hi - lo) / k
    return x


def label(mask, conn8=True):
    """Connected components of a bool mask via row runs + union-find.
    Returns (labels int32 with 0 = background, count)."""
    h, w = mask.shape
    m = np.zeros((h, w + 2), np.int8)
    m[:, 1:-1] = mask
    d = np.diff(m, axis=1)
    rows, starts = np.nonzero(d == 1)
    _, ends = np.nonzero(d == -1)
    n = len(rows)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    first = np.searchsorted(rows, np.arange(h + 1)).tolist()
    cs, ce = starts.tolist(), ends.tolist()
    ext = 1 if conn8 else 0
    for y in range(1, h):
        i, a1 = first[y - 1], first[y]
        j, b1 = first[y], first[y + 1]
        while i < a1 and j < b1:
            if cs[i] < ce[j] + ext and cs[j] < ce[i] + ext:
                ri, rj = find(i), find(j)
                if ri != rj:
                    parent[max(ri, rj)] = min(ri, rj)
            if ce[i] < ce[j]:
                i += 1
            else:
                j += 1
    roots = [find(i) for i in range(n)]
    ids = {}
    out = np.zeros((h, w), np.int32)
    for k in range(n):
        lab = ids.setdefault(roots[k], len(ids) + 1)
        out[rows[k], cs[k]:ce[k]] = lab
    return out, len(ids)


def flood(passable, seeds):
    """Pixels of `passable` 4-connected to any seed pixel."""
    lab, _ = label(passable, conn8=False)
    hit = np.unique(lab[seeds & passable])
    hit = hit[hit > 0]
    return np.isin(lab, hit)


def lum(a):
    return a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11


def bleed_into(rgb, known, iters):
    """Fill unknown pixels with the mean of known neighbours, ring by ring."""
    rgb = rgb.copy()
    known = known.copy()
    for _ in range(iters):
        if known.all():
            break
        acc = np.zeros_like(rgb)
        cnt = np.zeros(known.shape, np.float32)
        for dy, dx in N8:
            k = shift(known, dy, dx, False)
            acc += shift(rgb, dy, dx, 0) * k[..., None]
            cnt += k
        grow = (~known) & (cnt > 0)
        rgb[grow] = acc[grow] / cnt[grow][:, None]
        known = known | grow
    return rgb, known


def _down(x):
    h, w = x.shape[:2]
    x = x[: h - h % 2 or h, : w - w % 2 or w]
    if x.shape[0] < 2 or x.shape[1] < 2:
        return x
    return (x[0::2, 0::2] + x[1::2, 0::2] + x[0::2, 1::2] + x[1::2, 1::2]) / 4.0


def _up(x, shape):
    size = (shape[1], shape[0])
    return np.stack([np.asarray(Image.fromarray(np.ascontiguousarray(x[..., i])).resize(size, Image.BILINEAR))
                     for i in range(x.shape[2])], -1)


def push_pull(rgb, known):
    """Smoothly fills unknown pixels from the known ones (pyramid push-pull)."""
    w = known.astype(np.float32)
    c = rgb * w[..., None]
    levels = [(c, w)]
    while min(levels[-1][1].shape) > 2:
        c, w = levels[-1]
        levels.append((_down(c), _down(w)))
    c, w = levels[-1]
    mean = (rgb * known[..., None]).sum((0, 1)) / max(1, known.sum())
    est = np.where(w[..., None] > 0, c / np.maximum(w, 1e-6)[..., None], mean)
    for c, w in reversed(levels[:-1]):
        up = _up(est, w.shape)
        wc = np.clip(w, 0, 1)[..., None]
        est = np.where(wc > 0, c / np.maximum(wc, 1e-6), up) * wc + up * (1 - wc)
    return est


# ---------------------------------------------------------------------------
# painting out baked text / icons
# ---------------------------------------------------------------------------

# Clean texture patches (sheet, x0, y0, x1, y1): plain parchment inside a
# window, plain leather inside the normal leather button.
GRAIN_SOURCES = {"paper": ("04", (600, 150, 900, 350)), "leather": ("03", (100, 95, 330, 140))}
_grains = {}


def grain(kind):
    if kind not in _grains:
        sid, (x0, y0, x1, y1) = GRAIN_SOURCES[kind]
        patch = sheet(sid)[y0:y1, x0:x1, :3]
        _grains[kind] = patch - box_blur(patch, 5)
    return _grains[kind]


def material_like(a, kind):
    if kind == "paper":
        return (lum(a) > 0.62) & (a[..., 0] - a[..., 2] > 0.1) & (a[..., 3] > 0.9)
    if kind == "leather":
        r, g = a[..., 0], a[..., 1]
        return (r > g * 1.6) & (lum(a) > 0.16) & (lum(a) < 0.6) & (a[..., 3] > 0.9)
    if kind == "dark":  # the dark well of a bar frame
        return (lum(a) < 0.3) & (a[..., 3] > 0.9)
    raise ValueError(kind)


def erase(a, mask, kind="paper", amount=0.8, feather=1):
    """Repaints `mask` from the surrounding `kind` pixels (push-pull) plus that
    material's grain. Alpha is set opaque inside the mask."""
    a = a.copy()
    mask = dilate(mask, 1)
    ring = dilate(mask, 8) & ~dilate(mask, 2)
    good = ring & material_like(a, kind)
    ring = good if good.sum() > 30 else ring & (a[..., 3] > 0.9)
    base = push_pull(a[..., :3], ring)
    if kind in GRAIN_SOURCES:
        g = grain(kind)
        h, w = mask.shape
        reps = (h // g.shape[0] + 2, w // g.shape[1] + 2, 1)
        tex = np.tile(np.concatenate([g, g[:, ::-1]], 1), reps)[:h, :w]
        base = base + tex * amount
    soft = np.clip(box_blur(mask.astype(np.float32), feather) * 1.5, 0, 1)[..., None]
    a[..., :3] = a[..., :3] * (1 - soft) + base * soft
    a[..., 3] = np.where(mask, 1.0, a[..., 3])
    return a


def rect_mask(shape, rect):
    m = np.zeros(shape[:2], bool)
    x0, y0, x1, y1 = rect
    m[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = True
    return m


def lift(a, rect, dark=0.33, seeds=(), keep_seed=None):
    """Lifts an icon/glyph drawn on a plain backing (paper/leather) inside rect:
    the backing is flood-filled from the rect's border (and extra seed points)
    up to the icon's dark outline; whatever is left is the icon. Its 1-px rim
    gets a soft alpha from its colour distance to the local backing colour."""
    a = a.copy()
    r = rect_mask(a.shape, rect)
    barrier = lum(a) < dark
    border = r & ~erode(r, 1)
    seed = border.copy()
    for x, y in seeds:
        seed[y, x] = True
    bg = flood(r & ~barrier, seed)
    icon = r & ~bg
    # Drop tiny bits (paper texture specks the flood did not reach).
    lab, n = label(icon)
    if n:
        areas = np.bincount(lab.ravel())
        areas[0] = 0
        keep = areas >= max(12, 0.01 * areas.max())
        icon = keep[lab]
    # Local backing colour (normalised convolution of the backing pixels).
    w = box_blur(bg.astype(np.float32), 6)
    bgc = box_blur(a[..., :3] * bg[..., None], 6) / np.maximum(w, 1e-4)[..., None]
    edge_rgb, _ = bleed_into(a[..., :3], erode(icon, 1), 3)
    rim = dilate(icon, 1) & ~icon & r
    # Only darkening counts: the light glow some icons carry outside their
    # outline must not turn into an opaque light rim.
    l_bg = lum(bgc)
    soft = np.clip((l_bg - lum(a)) / np.maximum(l_bg - lum(edge_rgb), 0.08), 0, 1)
    alpha = np.where(icon, 1.0, np.where(rim, soft, 0.0)).astype(np.float32)
    a[..., :3] = np.where(rim[..., None], edge_rgb, a[..., :3])
    a[..., 3] = alpha
    return a


# ---------------------------------------------------------------------------
# clean-up and resampling
# ---------------------------------------------------------------------------

LO, HI = 0.25, 0.85   # alpha ramp: <= 64/255 -> 0 (fringe), >= 217/255 -> 1


def clean_alpha(a, box, keep="inside", min_area=40, fill="small", hole_max=150):
    """Drops fringe and specks, fills pin-holes, makes interiors opaque."""
    a = a.copy()
    alpha = a[..., 3]
    solid = alpha >= 0.5
    lab, n = label(solid)
    areas = np.bincount(lab.ravel(), minlength=n + 1)
    areas[0] = 0
    x0, y0, x1, y1 = box
    keep_ids = np.zeros(n + 1, bool)
    if n:
        if keep == "largest":
            keep_ids[int(np.argmax(areas))] = True
        else:
            floor = max(min_area, 0.004 * areas.max())
            ys, xs = np.nonzero(lab)
            ids = lab[ys, xs]
            sx = np.bincount(ids, weights=xs, minlength=n + 1)
            sy = np.bincount(ids, weights=ys, minlength=n + 1)
            for i in range(1, n + 1):
                if areas[i] < floor:
                    continue
                cx, cy = sx[i] / areas[i], sy[i] / areas[i]
                if x0 <= cx < x1 and y0 <= cy < y1:
                    keep_ids[i] = True
    kept = keep_ids[lab]
    holes = np.zeros_like(kept)
    if fill != "none":
        hl, hn = label(~kept, conn8=False)
        if hn:
            border = np.unique(np.concatenate([hl[0], hl[-1], hl[:, 0], hl[:, -1]]))
            hareas = np.bincount(hl.ravel(), minlength=hn + 1)
            small = np.ones(hn + 1, bool) if fill == "all" else hareas <= hole_max
            small[0] = False
            small[border] = False
            holes = small[hl]
    body = kept | holes
    ramp = np.clip((alpha - LO) / (HI - LO), 0, 1)
    new = np.where(erode(body, 1), 1.0, np.where(dilate(body, 2), ramp, 0.0))
    new = np.where(holes, 1.0, new).astype(np.float32)
    # Colour: filled holes and the semi-transparent rim take the colour of the
    # nearest solid pixel (no keying tint).
    solid_px = (new >= 0.999) & ~holes & (alpha >= HI)
    rgb, _ = bleed_into(a[..., :3], solid_px, 4)
    fix = holes | ((new > 0) & (new < 0.999))
    a[..., :3] = np.where(fix[..., None], rgb, a[..., :3])
    a[..., 3] = new
    return a


def resize(a, w, h):
    """Premultiplied Lanczos resize of a float RGBA array."""
    if (a.shape[1], a.shape[0]) == (w, h):
        return a.copy()
    pm = a[..., :3] * a[..., 3:4]
    chans = [pm[..., 0], pm[..., 1], pm[..., 2], a[..., 3]]
    out = [np.asarray(Image.fromarray(np.ascontiguousarray(c, np.float32), "F").resize((w, h), Image.LANCZOS))
           for c in chans]
    alpha = np.clip(out[3], 0, 1)
    rgb = np.stack(out[:3], -1) / np.maximum(alpha, 1e-4)[..., None]
    return np.concatenate([np.clip(rgb, 0, 1), alpha[..., None]], -1).astype(np.float32)


def finish(a):
    """Snap alpha, decontaminate faint rims, bleed colour outward, trim."""
    a = a.copy()
    alpha = a[..., 3]
    alpha[alpha < 3 / 255] = 0
    alpha[alpha > 0.96] = 1
    strong = alpha >= 0.5
    rgb, _ = bleed_into(a[..., :3], strong, 3)
    weak = (alpha > 0) & ~strong
    a[..., :3] = np.where(weak[..., None], rgb, a[..., :3])
    ys, xs = np.nonzero(alpha > 0)
    y0, y1 = max(0, ys.min() - EDGE_PAD), min(a.shape[0], ys.max() + 1 + EDGE_PAD)
    x0, x1 = max(0, xs.min() - EDGE_PAD), min(a.shape[1], xs.max() + 1 + EDGE_PAD)
    a = a[y0:y1, x0:x1]
    # Ensure the EDGE_PAD transparent margin exists even where the crop ended.
    a = np.pad(a, ((EDGE_PAD - (ys.min() - y0), EDGE_PAD - (y1 - 1 - ys.max())),
                   (EDGE_PAD - (xs.min() - x0), EDGE_PAD - (x1 - 1 - xs.max())), (0, 0)))
    known = a[..., 3] > 0
    rgb, known = bleed_into(a[..., :3], known, 24)
    if not known.all():
        rgb[~known] = rgb[known].mean(0)
    a[..., :3] = np.where((a[..., 3] > 0)[..., None], a[..., :3], rgb)
    return a


# ---------------------------------------------------------------------------
# the parts
# ---------------------------------------------------------------------------

PARTS = []


def part(name, sid, box, scale=None, size=None, slice_=None, role="", note="", ops=(),
         keep="inside", min_area=40, fill="small", hole_max=150):
    """box = (x0, y0, x1, y1) on sheet `sid`. Either `scale` (output / source)
    or `size` (output long side). `slice_` = [l, t, r, b] in output pixels."""
    PARTS.append(dict(name=PREFIX + name, sid=sid, box=box, scale=scale, size=size, slice=slice_, role=role,
                      note=note, ops=list(ops), keep=keep, min_area=min_area, fill=fill, hole_max=hole_max))


# ---- windows, panels, frames ----------------------------------------------
part("window_frame", "04", (1200, 542, 1580, 739), 0.75, slice_=[40, 38, 40, 38], keep="largest",
     role="Every window body (Inventory, Settings, Party, Play, Forge, Quest Journal)",
     note="Store size; 9-slice to the window size. Add lk_clasp_* on the edges when wanted.")
part("window_clasp_frame", "04", (1169, 43, 1629, 469), 0.6, keep="largest",
     role="Reference window with side clasps", note="Clasps sit mid-edge, so it is NOT 9-sliceable; "
     "prefer lk_window_frame + lk_clasp_left/right overlays.")
part("dialog_frame", "13", (866, 58, 1606, 462), 0.6, slice_=[46, 42, 46, 42], keep="largest",
     ops=[("mirror_x", (1470, 50, 1615, 186), 2471)],
     role="Confirm dialog / popups body", note="Baked close button removed (top-right corner rebuilt from the mirrored top-left); place lk_button_close_* on top.")
part("toast_frame", "13", (67, 488, 772, 621), 0.6, slice_=[36, 30, 36, 30], keep="largest",
     ops=[("erase", (102, 507, 748, 603), "paper")],
     role="Quest Complete / Item Received toasts", note="Icon, title and close mark painted out.")
part("panel", "12", (327, 774, 845, 985), 0.5, slice_=[30, 28, 30, 28], keep="largest",
     role="Inner panels (Party columns, Forge columns, Quest details)")
part("panel_inset", "01", (716, 378, 982, 516), 0.75, slice_=[14, 14, 14, 14], keep="largest",
     ops=[("crop_opaque",)],
     role="Inset card drawn on parchment (rows, sub-panels)",
     note="Opaque parchment around a thin rounded inset border; place it on parchment.")
part("card_detail", "10", (1116, 394, 1362, 752), 0.6, keep="largest",
     role="Item detail card (picture well + stat lines)", note="Fixed layout lines; not sliced.")
part("frame_hollow", "12", (46, 774, 302, 981), 0.5, slice_=[30, 28, 30, 28], keep="largest", fill="none",
     role="Hollow paper frame with leather corners (map / picture frame)")
part("frame_hollow_large", "02", (29, 33, 702, 383), 0.5, slice_=[32, 30, 32, 30], keep="largest", fill="none",
     role="Hollow window frame (map, viewport)")
part("frame_hollow_bar", "02", (129, 397, 998, 515), 0.5, slice_=[30, 26, 30, 26], keep="largest", fill="none",
     role="Hollow wide bar frame")
part("frame_hollow_speech", "02", (1084, 372, 1405, 517), 0.6, keep="largest", fill="none",
     role="Hollow speech frame (tail at bottom centre)", note="Tail in the bottom edge: not sliced.")
part("frame_hollow_small", "02", (1446, 383, 1571, 502), 0.7, slice_=[26, 26, 26, 26], keep="largest",
     fill="none", role="Small hollow square frame")
part("frame_hollow_capped", "15", (654, 746, 800, 887), 0.6, slice_=[24, 24, 24, 24], keep="largest",
     fill="none", role="Hollow square frame with leather caps (item preview)")
part("portrait_frame", "01", (154, 764, 249, 862), 1.0, slice_=[30, 30, 30, 30], keep="largest", fill="none",
     role="Player headshot frame (HUD player card, party rows)", note="Hollow; put the headshot behind it.")
part("portrait_plaque", "01", (521, 890, 929, 978), 0.7, keep="largest", fill="small",
     role="Portrait window + name plaque (party member row)", note="Hollow portrait window at left.")
part("frame_hollow_circle", "01", (279, 764, 375, 862), 0.8, keep="largest", fill="none",
     role="Square frame with round window")
part("frame_hollow_wide", "01", (404, 763, 501, 862), 0.8, keep="largest", fill="none",
     role="Square frame with wide window")
part("frame_rails", "01", (28, 884, 125, 981), 0.8, keep="largest", fill="none",
     role="Hollow square of rails")
part("frame_ring", "01", (142, 884, 245, 989), 0.8, keep="largest", fill="none", role="Round hollow ring")
part("frame_ring_leaves", "01", (254, 884, 372, 988), 0.8, keep="largest", fill="none",
     role="Round hollow ring with leaves")
part("frame_round_paper", "01", (385, 883, 489, 988), 0.8, keep="largest", role="Round paper disc")
part("frame_round", "03", (1342, 482, 1497, 639), 0.5, keep="largest", role="Round paper frame with straps")
part("frame_capped_hollow", "01", (1142, 738, 1505, 790), 0.6, slice_=[24, 14, 24, 14], keep="largest",
     fill="none", role="Hollow bar with leather end caps")

# ---- buttons ----------------------------------------------------------------
for i, st in enumerate(("normal", "hover", "pressed", "disabled")):
    x0, x1 = ((43, 390), (409, 753), (773, 1126), (1145, 1492))[i]
    part(f"button_leather_{st}", "03", (x0, 63, x1, 170), 0.6, slice_=[26, 24, 26, 24], keep="largest",
         role="Primary action (Equip, Claim, Forge, Apply, Invite, Close, Play)")
    x0, x1 = ((44, 389), (407, 753), (770, 1126), (1145, 1492))[i]
    part(f"button_paper_{st}", "03", (x0, 198, x1, 306), 0.6, slice_=[26, 24, 26, 24], keep="largest",
         role="Secondary action (Reset, Cancel), inactive tabs")
    x0, x1 = ((341, 483), (537, 679), (734, 877), (932, 1074))[i]
    part(f"button_close_{st}", "03", (x0, 328, x1, 466), 0.46, keep="largest",
         role="Window close button (top right)")
part("button_square_paper", "03", (37, 489, 177, 625), 0.4, keep="largest",
     ops=[("erase_mask", (58, 510, 157, 605), "dark", 0.5, 2, "paper")],
     role="Square paper button; put a lk_glyph_* on it", note="Glyph painted out.")
GLYPHS = ("plus", "minus", "check", "cross", "arrow_left", "arrow_right", "arrow_up", "arrow_down")
for i, g in enumerate(GLYPHS):
    x0 = (37, 191, 350, 505, 663, 816, 970, 1125)[i]
    part(f"glyph_{g}", "03", (x0 + 18, 508, x0 + 120, 607), 0.4, ops=[("lift", (x0 + 18, 508, x0 + 120, 607), 0.5)],
         fill="all", role="Dark glyph for lk_button_square_paper / steppers", note="Dark brown; tint with ImageColor3.")
part("button_square_leather", "01", (568, 672, 639, 734), 0.75, keep="largest", role="Small leather square button")
part("button_square_small", "01", (653, 673, 723, 735), 0.75, keep="largest", role="Small paper square button")
part("button_play_square", "02", (185, 629, 292, 722), 0.55, keep="largest", role="Square paper Play button")
part("button_hud", "02", (185, 629, 292, 722), 0.55, keep="largest",
     ops=[("erase_mask", (205, 645, 275, 707), "dark", 0.62, 2, "paper")],
     role="Blank square HUD button; put an icon on it", note="Play triangle painted out.")
part("button_settings", "07", (1458, 82, 1576, 190), 0.5, keep="largest", role="HUD settings (gear) button")
part("button_invite", "15", (955, 764, 1079, 864), 0.45, keep="largest", role="Invite / add-friend button")
part("button_invite_card", "06", (1287, 413, 1625, 722), 0.35, keep="largest", role="Large invite-player card")
for i, st in enumerate(("hover", "normal", "disabled")):
    x0, x1 = ((804, 1026), (1041, 1262), (1279, 1498))[i]
    part(f"button_paper_small_{st}", "03", (x0, 816, x1, 930), 0.45, slice_=[18, 18, 18, 18], keep="largest",
         role="Small paper button / value box (key binds, slider values)")
for i, st in enumerate(("leather", "paper", "disabled")):
    x0, x1 = ((26, 410), (418, 865), (873, 1297))[i]
    part(f"button_flat_{st}", "09", (x0, 194, x1, 289), 0.5, slice_=[20, 18, 20, 18], keep="largest",
         role="Flat plaque button (selected / normal / disabled)")
for i, st in enumerate(("leather", "paper", "disabled")):
    x0, x1 = ((63, 507), (541, 983), (1018, 1461))[i]
    part(f"plaque_notched_{st}", "03", (x0, 652, x1, 775), 0.5, slice_=[28, 24, 28, 24], keep="largest",
         role="Notched-corner plaque button (Close in Party)")
part("glyph_play", "03", (100, 832, 190, 915), 0.45, ops=[("lift", (100, 832, 190, 915), 0.2)], fill="all",
     role="White play triangle for the PLAY button", note="From the PLAY button (text not taken).")
part("glyph_check_white", "03", (462, 834, 556, 912), 0.45, ops=[("lift", (462, 834, 556, 912), 0.2)], fill="all",
     role="White check for CONFIRM buttons", note="From the CONFIRM button (text not taken).")

# ---- slots, tiles, badges -----------------------------------------------------
for i, st in enumerate(("normal", "selected", "hover", "disabled", "locked")):
    x0, x1 = ((64, 335), (375, 658), (706, 977), (1027, 1298), (1344, 1608))[i]
    part(f"slot_{st}", "05", (x0, 44, x1, 307), 0.4, slice_=[24, 24, 24, 24] if st != "locked" else None,
         keep="largest", role="Hotbar / equipment slot states")
part("slot_hotbar", "05", (77, 499, 314, 733), 0.4, keep="largest",
     ops=[("erase_mask", (90, 510, 145, 565), "light", 0.55, 2, "leather")],
     role="Hotbar slot with blank number badge (HUD, Play equipment)", note="Digit painted out; draw it as text.")
part("slot_item_normal", "10", (787, 74, 947, 229), 0.62, slice_=[20, 20, 20, 20], keep="largest",
     role="Inventory grid slot")
part("slot_item_selected", "10", (981, 72, 1150, 236), 0.62, slice_=[24, 24, 24, 24], keep="largest",
     role="Inventory grid slot, selected (gold glow)", note="About 6 px bigger than slot_item_normal per side.")
part("tile_frame", "07", (771, 239, 974, 435), 0.5, slice_=[22, 22, 22, 22], keep="largest",
     ops=[("erase", (798, 262, 946, 418), "paper")],
     role="HUD menu tile (3x2 grid)", note="Icon painted out; put a lk_icon_* on it.")
part("tile_paper", "01", (28, 764, 124, 862), 0.8, slice_=[22, 22, 22, 22], keep="largest",
     role="Paper tile with leather corners")
part("tile_header", "01", (655, 763, 753, 862), 0.8, keep="largest", role="Paper tile with leather header band")
part("tile_rail", "01", (782, 763, 880, 862), 0.8, keep="largest", role="Paper tile with a rail on top")
part("tile_tab", "01", (909, 758, 1007, 862), 0.8, keep="largest", role="Paper tile with a leather tab on top")
part("tile_blank", "12", (890, 649, 993, 751), 0.6, slice_=[16, 16, 16, 16], keep="largest",
     role="Plain square tile (requirements, rewards)")
part("tile_small", "08", (1303, 577, 1402, 653), 0.6, slice_=[16, 16, 16, 16], keep="largest",
     role="Small tile (stat icon tiles)")
part("tile_check_on", "12", (1153, 901, 1221, 971), 0.7, keep="largest", role="Check tile (ticked)")
part("tile_check_off", "12", (1242, 901, 1312, 973), 0.7, keep="largest", role="Check tile (empty)")
part("badge_number", "05", (87, 363, 187, 461), 0.36, keep="largest",
     ops=[("erase_mask", (102, 378, 172, 446), "light", 0.55, 2, "leather")],
     role="Hotbar number badge (blank leather)", note="Digit painted out; draw the number as text.")
part("badge_count", "05", (1238, 366, 1347, 466), 0.4, keep="largest",
     ops=[("erase_mask", (1255, 382, 1330, 450), "dark", 0.45, 2, "paper")],
     role="Stack count badge (blank)", note="Digits painted out.")
part("badge_count_wide", "05", (1389, 355, 1593, 449), 0.4, slice_=[12, 12, 12, 12], keep="largest",
     ops=[("erase_mask", (1410, 370, 1575, 435), "dark", 0.45, 2, "paper")],
     role="Wide count badge (blank)", note="Digits painted out.")
part("pill_value", "08", (1090, 576, 1252, 633), 0.6, slice_=[14, 12, 14, 12], keep="largest",
     ops=[("erase_mask", (1104, 586, 1238, 623), "dark", 0.5, 2, "paper")],
     role="Value pill (\"450/750 XP\", \"LV. 12\")", note="Text painted out.")
part("currency_pill", "07", (915, 85, 1160, 190), 0.5, slice_=[18, 18, 18, 18], keep="largest",
     ops=[("erase", (934, 102, 1141, 173), "paper")],
     role="HUD currency pill (coins, gems)", note="Coin and amount painted out; add lk_icon_coin/gem + text.")
part("player_card", "07", (95, 33, 866, 211), 0.46, keep="largest",
     ops=[("erase", (300, 60, 781, 182), "paper"), ("clear", (121, 58, 258, 186))],
     role="HUD player card (portrait, name, level bar, leaf)",
     note="Name, level, XP bar and headshot painted out: overlay the headshot, text and lk_bar_track/fill.")

# ---- tabs, plaques, banners ---------------------------------------------------
part("tab_category", "02", (653, 546, 931, 614), 0.8, slice_=[20, 16, 34, 16], keep="largest",
     role="Selected category tab with arrow (Inventory categories)")
part("tab_arrow_paper", "14", (698, 848, 950, 947), 0.6, slice_=[30, 20, 40, 20], keep="largest",
     role="Paper arrow tab with leather strap")
part("tab_arrow_leather", "14", (965, 848, 1231, 946), 0.6, slice_=[30, 20, 40, 20], keep="largest",
     role="Leather arrow tab")
part("plaque_paper", "14", (68, 852, 358, 954), 0.6, slice_=[30, 26, 30, 26], keep="largest",
     role="Paper title plaque with leather corners (PLAY title, region name)")
part("plaque_leather", "14", (379, 848, 667, 950), 0.6, slice_=[30, 26, 30, 26], keep="largest",
     role="Stitched leather plaque")
part("plaque_small", "05", (1130, 783, 1455, 902), 0.5, slice_=[20, 20, 20, 20], keep="largest",
     role="Small paper plaque")
part("plaque_leather_bar", "01", (33, 671, 299, 734), 0.7, slice_=[18, 16, 18, 16], keep="largest",
     role="Leather bar plaque")
part("plaque_paper_bar", "01", (310, 671, 553, 735), 0.7, slice_=[18, 16, 18, 16], keep="largest",
     role="Paper bar plaque")
part("plaque_rivet_leather", "02", (48, 544, 347, 613), 0.7, slice_=[18, 18, 18, 18], keep="largest",
     role="Leather plaque with rivets")
part("plaque_rivet_paper", "02", (371, 544, 626, 614), 0.7, slice_=[18, 18, 18, 18], keep="largest",
     role="Paper plaque with rivets")
part("plaque_capped", "01", (1141, 676, 1507, 730), 0.6, slice_=[24, 14, 24, 14], keep="largest",
     role="Paper plaque with leather end caps")
part("strap_leather", "14", (60, 377, 581, 449), 0.6, slice_=[24, 18, 24, 18], keep="largest",
     role="Stitched leather strap with rivets")
part("strap_leather_short", "14", (623, 392, 858, 451), 0.6, slice_=[22, 16, 22, 16], keep="largest",
     role="Short stitched leather strap")
part("banner_paper", "14", (67, 593, 1204, 715), 0.5, slice_=[36, 28, 36, 28], keep="largest",
     role="Long torn-paper banner with leather corners")
part("banner_leather", "14", (65, 726, 1203, 830), 0.5, slice_=[26, 22, 26, 22], keep="largest",
     role="Long stitched leather banner")

# ---- bars ---------------------------------------------------------------------------
part("bar_track", "05", (198, 845, 1089, 904), 0.4, slice_=[12, 10, 12, 10], keep="largest",
     role="XP / progress bar track (HUD XP bar, Quest progress)")
for col, (sid, box) in {"red": ("18", (963, 640, 1407, 688)), "green": ("18", (963, 696, 1407, 745)),
                        "orange": ("18", (963, 752, 1407, 801)), "yellow": ("18", (963, 811, 1407, 862)),
                        "blue": ("19", (460, 572, 834, 627))}.items():
    part(f"bar_fill_{col}", sid, box, 0.5 if sid == "18" else 0.44, slice_=[12, 10, 12, 10], keep="largest",
         role="Bar fill (health red, stamina green, food orange, XP yellow, timer blue)",
         note="Scale X with the value; keep at least l+r px wide.")
part("bar_frame", "18", (270, 643, 867, 745), 0.5, slice_=[24, 20, 24, 20], keep="largest",
     role="Paper bar frame with dark well")
part("bar_frame_plain", "18", (270, 764, 866, 871), 0.5, slice_=[24, 20, 24, 20], keep="largest",
     role="Plain paper bar frame")
part("bar_frame_thin", "12", (45, 567, 341, 614), 0.6, slice_=[16, 12, 16, 12], keep="largest",
     role="Thin paper bar frame with dark well (quest rows)")
part("statbar_frame", "18", (42, 114, 561, 214), 0.6, slice_=[66, 20, 84, 20], keep="largest",
     ops=[("erase_mask", (62, 131, 141, 203), "nonpaper", 0, 2, "paper"), ("erase", (64, 133, 140, 201), "paper"),
          ("erase", (440, 132, 541, 197), "paper")],
     role="Stat bar frame: icon box + bar well + value box",
     note="Icon and value painted out; slice centre is the bar well. Add a stat icon, a fill and text.")
for i, st in enumerate(("track", "half", "full")):
    x0, x1 = ((859, 1062), (1075, 1279), (1288, 1492))[i]
    cx = (x0 + x1) // 2
    part(f"ring_{st}", "19", (x0, 529, x1, 737), 0.5, keep="largest",
         ops=[("erase", (cx - 52, 600, cx + 52, 668), "paper")],
         role="Round progress ring (0 / 50 / 100 %)", note="Percent text painted out.")

# ---- controls -------------------------------------------------------------------------
part("search", "09", (25, 52, 515, 166), 0.42, slice_=[44, 18, 18, 18], keep="largest",
     role="Search box (Inventory, Party invite)", note="Magnifier baked in the left inset; type text natively.")
part("dropdown", "09", (538, 52, 1027, 166), 0.42, slice_=[18, 18, 44, 18], keep="largest",
     role="Dropdown (Language)", note="Arrow baked in the right inset.")
part("dropdown_button", "09", (1049, 59, 1158, 163), 0.42, keep="largest", role="Small dropdown arrow button")
for i, st in enumerate(("normal", "hover", "disabled")):
    x0, x1 = ((26, 515), (544, 1037), (1064, 1561))[i]
    dot_x = (x0 + 52, x0 + 52, x0 + 52)[i]
    part(f"row_{st}", "09", (x0, 316, x1, 435), 0.65, slice_=[24, 22, 24, 22], keep="largest",
         ops=[("erase", (x0 + 28, 352, x0 + 78, 400), "paper"), ("erase", (x1 - 72, 350, x1 - 30, 402), "paper")],
         role="List row states (recipes, quests, materials)",
         note="Bullet and chevron painted out; add lk_glyph_chevron_right / icon.")
part("glyph_chevron_right", "09", (440, 350, 490, 402), 0.65, ops=[("lift", (440, 350, 490, 402), 0.45)],
     fill="all", role="Row chevron")
part("checkbox_off", "09", (27, 469, 131, 571), 0.4, keep="largest", role="Checkbox (Settings)")
part("checkbox_on", "09", (153, 469, 259, 571), 0.4, keep="largest", role="Checkbox ticked")
part("glyph_checkmark", "09", (305, 477, 391, 551), 0.45, role="Loose dark check mark")
part("toggle_off", "09", (470, 471, 657, 570), 0.45, keep="largest", role="Toggle off")
part("toggle_on", "09", (706, 471, 884, 570), 0.45, keep="largest", role="Toggle on")
part("slider_track", "09", (940, 500, 1341, 537), 0.45, slice_=[9, 7, 9, 7], keep="largest",
     role="Slider track (Settings)", note="Fill it with lk_bar_fill_yellow scaled to the value.")
part("slider_knob", "09", (1389, 484, 1459, 556), 0.5, keep="largest", role="Slider knob")
part("scroll_track", "09", (1520, 461, 1567, 727), 0.4, slice_=[8, 10, 8, 10], keep="largest",
     role="Scrollbar track (party list)")
part("scroll_thumb", "09", (1601, 477, 1648, 621), 0.4, slice_=[8, 10, 8, 10], keep="largest",
     role="Scrollbar thumb")
part("button_stepper_plus", "09", (32, 610, 140, 714), 0.42, keep="largest", role="Quantity +")
part("button_stepper_minus", "09", (164, 610, 272, 714), 0.42, keep="largest", role="Quantity -")
part("stepper_box", "09", (307, 606, 661, 719), 0.42, slice_=[14, 14, 30, 14], keep="largest",
     role="Number stepper field (quantity)", note="Up/down arrows baked in the right inset.")
part("keycap", "09", (736, 605, 855, 721), 0.45, slice_=[16, 14, 16, 20], keep="largest",
     ops=[("erase_mask", (770, 630, 822, 690), "dark", 0.5, 2, "paper")],
     role="Key cap (key prompts)", note="Letter painted out.")
part("keycap_wide", "09", (1039, 604, 1270, 721), 0.45, slice_=[16, 14, 16, 20], keep="largest",
     ops=[("erase_mask", (1070, 630, 1240, 690), "dark", 0.5, 2, "paper")],
     role="Wide key cap (SHIFT, TAB)", note="Label painted out.")
part("tooltip", "09", (60, 750, 474, 901), 0.6, slice_=[22, 22, 22, 22], keep="largest", role="Tooltip box")
part("tooltip_tail", "09", (640, 862, 730, 899), 0.6, ops=[("clear", (0, 0, 2000, 870))], role="Tooltip tail (down)",
     note="Overlay on the bottom edge of lk_tooltip; its top rows are paper and cover the border.")
part("divider_diamond", "09", (935, 815, 1628, 844), 0.6, slice_=[16, 4, 16, 4], role="Divider with diamond ends")
part("divider_line", "14", (60, 476, 847, 495), 0.6, slice_=[14, 4, 14, 4], role="Thin divider with diamond ends")
part("divider_ornament", "14", (60, 508, 852, 548), 0.6, min_area=8,
     role="Divider with centre diamond (dialog title)", note="Centre ornament: stretch with care (not sliced).")
part("divider_vertical", "14", (960, 308, 983, 570), 0.6, slice_=[4, 16, 4, 16], role="Vertical divider")
part("row_bullet", "14", (1039, 316, 1481, 345), 0.6, slice_=[24, 8, 12, 8], keep="largest",
     role="Light list row with bullet (party empty slots)")
part("row_check_off", "12", (48, 655, 442, 737), 0.6, slice_=[44, 16, 16, 16], keep="largest",
     role="Checklist row (empty box)")
part("row_check_on", "12", (464, 655, 854, 737), 0.6, slice_=[44, 16, 16, 16], keep="largest",
     role="Checklist row (ticked)")

# ---- ornaments ---------------------------------------------------------------------
for nm, box in {"tl": (1473, 539, 1528, 595), "tr": (1582, 539, 1637, 595),
                "bl": (1473, 630, 1528, 685), "br": (1582, 630, 1637, 685)}.items():
    part(f"corner_{nm}", "02", box, 0.75, keep="largest", role="Leather corner piece")
for nm, box in {"tl": (95, 49, 196, 141), "tr": (226, 49, 327, 141),
                "bl": (95, 159, 196, 249), "br": (226, 159, 326, 249)}.items():
    part(f"corner_ornate_{nm}", "14", box, 0.45, keep="largest", role="Ornate leather corner with torn paper")
part("clasp_left", "14", (395, 66, 439, 185), 0.4, keep="largest", role="Leather clasp on a window edge")
part("clasp_right", "14", (488, 66, 532, 185), 0.4, keep="largest", role="Leather clasp on a window edge")
part("corner_fold", "14", (693, 67, 870, 274), 0.5, keep="largest", role="Folded paper corner")
part("medallion_square", "14", (938, 101, 1094, 260), 0.5, keep="largest", role="Square paper medallion")
part("medallion_round", "14", (1123, 87, 1312, 275), 0.5, keep="largest", role="Round paper medallion")
part("medallion_octagon", "14", (1335, 83, 1494, 275), 0.5, keep="largest", role="Octagonal paper medallion")
part("rivet", "14", (69, 295, 115, 340), 0.5, keep="largest", role="Brass rivet")
part("spike", "14", (263, 296, 299, 330), 0.6, keep="largest", role="Brass spike")
part("nail", "14", (314, 295, 351, 343), 0.6, keep="largest", role="Brass nail")
part("rope_knot", "14", (391, 250, 484, 356), 0.5, keep="largest", role="Rope knot")
part("rope_ring", "14", (511, 249, 623, 355), 0.5, keep="largest", fill="small", hole_max=60, role="Rope ring")
part("rope_cross", "14", (647, 241, 781, 368), 0.5, keep="largest", role="Rope lashing")
part("rail_h", "02", (1063, 553, 1365, 585), 0.6, slice_=[12, 6, 12, 6], keep="largest", role="Horizontal rail")
part("rail_v", "02", (1407, 546, 1430, 709), 0.6, slice_=[6, 12, 6, 12], keep="largest", role="Vertical rail")
part("emblem_leaf", "14", (1252, 580, 1342, 865), 0.45, min_area=6, role="Leaf emblem (player card)")
part("emblem_rune", "14", (1378, 598, 1494, 898), 0.45, min_area=6, role="Rune emblem")
for col, box in {"brown": (904, 687, 943, 726), "yellow": (961, 687, 1000, 726),
                 "green": (1020, 687, 1058, 726), "red": (1076, 687, 1115, 726)}.items():
    part(f"dot_{col}", "01", box, 0.6, keep="largest", role="Status dot (ready, away, busy, offline)")
part("map_parchment", "15", (1157, 663, 1493, 987), 0.8, keep="largest", role="Plain parchment map")

# ---- icons -----------------------------------------------------------------------------
ICON = 112
for nm, box in {"backpack": (47, 41, 386, 383), "portal": (438, 48, 843, 372), "scroll": (872, 70, 1205, 365),
                "market": (1276, 59, 1621, 363), "anvil": (62, 399, 402, 695), "trade": (487, 409, 857, 673),
                "gear": (907, 411, 1193, 691), "coin": (171, 706, 375, 906), "gem": (605, 700, 764, 915),
                "crown": (945, 721, 1138, 881)}.items():
    part(f"icon_{nm}", "06", box, size=ICON, fill="small", role="Menu / currency icon")
for nm, box in {"backpack_alt": (45, 63, 265, 297), "portal_alt": (281, 57, 562, 297),
                "scroll_alt": (584, 67, 811, 292), "market_alt": (837, 72, 1100, 297),
                "anvil_alt": (1127, 91, 1364, 301), "trade_alt": (29, 339, 283, 544),
                "gear_alt": (327, 334, 550, 560), "party": (572, 354, 839, 557), "map": (850, 334, 1103, 561),
                "trophy": (1125, 341, 1374, 560), "mail": (50, 625, 273, 784), "chest": (307, 607, 567, 808),
                "hammer": (605, 591, 832, 816), "torch": (883, 578, 1058, 828), "compass": (1143, 580, 1347, 816),
                "house": (42, 835, 301, 1067), "runestone": (325, 833, 549, 1068), "exit": (577, 833, 833, 1066),
                "journal": (881, 831, 1101, 1076), "magnifier": (1144, 837, 1359, 1064)}.items():
    part(f"icon_{nm}", "11", box, size=ICON, fill="small", role="Menu / side-tab icon")
for nm, box in {"heart": (32, 83, 254, 278), "lightning": (343, 73, 503, 293), "drumstick": (575, 78, 808, 284),
                "star": (881, 74, 1092, 280), "crown_gem": (1156, 81, 1373, 273), "exclamation": (85, 336, 189, 562),
                "warning": (285, 342, 532, 555), "check": (597, 365, 837, 557), "cross": (886, 352, 1105, 563),
                "hourglass": (1184, 336, 1342, 560), "clock": (28, 604, 257, 838), "scroll_small": (305, 604, 540, 827),
                "gift": (601, 607, 815, 832), "backpack_small": (878, 605, 1106, 833),
                "log": (30, 883, 275, 1083), "stone": (309, 869, 553, 1083), "plant_fiber": (594, 862, 831, 1090),
                "arrow_up": (897, 875, 1085, 1076), "speech": (1144, 882, 1375, 1081)}.items():
    part(f"icon_{nm}", "16", box, size=ICON, fill="small", role="Status / stat / item icon")
part("icon_stone_axe", "16", (1177, 593, 1373, 842), size=192, fill="small",
     role="Stone axe (hotbar, inventory detail art ~170 px)")
WORLD = 96
for nm, box in {"mountain": (42, 87, 294, 292), "tree": (312, 58, 531, 296), "cave": (557, 101, 825, 296),
                "campfire": (852, 70, 1071, 303), "ruin": (1103, 79, 1357, 296), "rocks": (42, 339, 291, 542),
                "crystals": (325, 327, 532, 547), "magma_ore": (575, 346, 810, 549), "berry_bush": (849, 330, 1082, 546),
                "anvil_hammer": (1105, 323, 1363, 552), "totem": (61, 575, 278, 817),
                "runestone_world": (308, 581, 541, 816), "treasure": (562, 608, 844, 802), "paw": (881, 593, 1088, 808),
                "tusk": (1151, 577, 1344, 820), "map_pin": (69, 841, 271, 1070), "compass_arrow": (315, 845, 540, 1069),
                "bridge": (559, 879, 852, 1059), "wave": (862, 876, 1108, 1060), "hut": (1130, 834, 1370, 1065)}.items():
    part(f"icon_{nm}", "17", box, size=WORLD, fill="small", min_area=20, role="World / map icon")
for nm, box in {"logs": (763, 830, 868, 921), "stones": (903, 829, 1001, 917), "plank": (1040, 826, 1141, 924)}.items():
    part(f"icon_{nm}", "10", box, 1.0, fill="small", role="Material icon (inventory, forge, rewards)")
part("icon_hatchet", "12", (1021, 644, 1149, 766), 1.0, fill="small", role="Tool icon (forge recipes)")
part("icon_pickaxe", "12", (1170, 648, 1300, 768), 1.0, fill="small", role="Tool icon (forge recipes / detail)")
for nm, (box, seeds) in {"spear": ((992, 735, 1109, 817), ()), "rope": ((855, 824, 983, 914), ((918, 862),)),
                         "berries": ((1117, 824, 1242, 914), ()), "mushroom": ((1250, 824, 1378, 914), ()),
                         "hide": ((1387, 824, 1514, 914), ()), "bone": ((1522, 824, 1646, 914), ())}.items():
    x0, y0, x1, y1 = box
    inner = (x0 + 6, y0 + 5, x1 - 6, y1 - 5)
    part(f"icon_{nm}", "02", box, 1.0, ops=[("lift", inner, 0.33, seeds)], fill="all" if nm != "rope" else "small",
         hole_max=40, role="Item icon (inventory grid)", note="Lifted off its item tile.")
for nm, box in {"flag": (773, 767, 970, 949), "build": (1019, 767, 1218, 949)}.items():
    x0, y0, x1, y1 = box
    part(f"icon_{nm}", "19", box, 0.75, ops=[("lift", (x0 + 30, y0 + 30, x1 - 30, y1 - 28), 0.33)], fill="all",
         role="Status icon", note="Lifted off its framed tile.")
part("icon_lock", "13", (1136, 805, 1200, 888), 1.0, keep="largest", role="Locked status")
part("icon_cursor", "13", (1543, 802, 1608, 893), 1.0, keep="largest", role="Pointer cursor")
part("icon_backpack_white", "10", (1209, 55, 1512, 145), 0.8, ops=[("lift", (1236, 64, 1308, 136), 0.2)],
     fill="all", role="White backpack for the active Backpack tab", note="Lifted off the active tab.")
part("glyph_invite", "06", (1340, 462, 1585, 688), 0.2, ops=[("lift", (1340, 462, 1585, 688), 0.45)], fill="all",
     min_area=400,
     role="Person+ glyph (invite)", note="Dark; tint with ImageColor3.")


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------


def build_part(p):
    src = sheet(p["sid"])
    H, W = src.shape[:2]
    x0, y0, x1, y1 = p["box"]
    cx0, cy0 = max(0, x0 - PAD), max(0, y0 - PAD)
    cx1, cy1 = min(W, x1 + PAD), min(H, y1 + PAD)
    a = src[cy0:cy1, cx0:cx1].copy()

    def local(r):
        return (r[0] - cx0, r[1] - cy0, r[2] - cx0, r[3] - cy0)

    lifted = False
    for op in p["ops"]:
        kind = op[0]
        if kind == "clear":
            a[..., 3] = np.where(rect_mask(a.shape, local(op[1])), 0.0, a[..., 3])
        elif kind == "erase":
            a = erase(a, rect_mask(a.shape, local(op[1])), op[2])
        elif kind == "erase_mask":
            _, rect, which, thr, grow, mat = op
            r = rect_mask(a.shape, local(rect))
            if which == "nonpaper":
                m = r & ~material_like(a, "paper") & (a[..., 3] > 0.5)
            else:
                m = r & ((lum(a) < thr) if which == "dark" else (lum(a) > thr)) & (a[..., 3] > 0.5)
            a = erase(a, dilate(m, grow) & r, mat)
        elif kind == "lift":
            seeds = [(sx - cx0, sy - cy0) for sx, sy in (op[3] if len(op) > 3 else ())]
            a = lift(a, local(op[1]), op[2], seeds)
            lifted = True
        elif kind == "copy":
            # Paint a rect with the pixels at an offset (same band of plain
            # parchment), feathered over 3 px.
            _, rect, (dx, dy) = op
            m = rect_mask(a.shape, local(rect))
            src_full = sheet(p["sid"])
            moved = a.copy()
            ys, xs = np.nonzero(m)
            moved[ys, xs] = src_full[ys + cy0 + dy, xs + cx0 + dx]
            soft = np.clip(box_blur(m.astype(np.float32), 3) * 1.5, 0, 1)[..., None]
            a = a * (1 - soft) + moved * soft
        elif kind == "mirror_x":
            # Paint a rect with its mirror image across the part's vertical
            # axis (src x = axis - x), feathered over 3 px.
            _, rect, axis = op
            m = rect_mask(a.shape, local(rect))
            src_full = sheet(p["sid"])
            moved = a.copy()
            ys, xs = np.nonzero(m)
            moved[ys, xs] = src_full[ys + cy0, axis - (xs + cx0)]
            soft = np.clip(box_blur(m.astype(np.float32), 3) * 1.5, 0, 1)[..., None]
            a = a * (1 - soft) + moved * soft
        elif kind == "crop_opaque":
            # Keep the whole crop opaque (a piece cut out of a parchment panel).
            r = rect_mask(a.shape, local(p["box"]))
            a[..., 3] = np.where(r, 1.0, 0.0)
        else:
            raise ValueError(kind)
    a = clean_alpha(a, local(p["box"]), keep="largest" if lifted and p["keep"] == "largest" else p["keep"],
                    min_area=p["min_area"], fill=p["fill"], hole_max=p["hole_max"])
    ys, xs = np.nonzero(a[..., 3] > 0)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = a.shape[:2]
    scale = p["scale"] if p["scale"] is not None else p["size"] / max(w, h)
    ow, oh = max(1, round(w * scale)), max(1, round(h * scale))
    a = finish(resize(a, ow, oh))
    if max(a.shape[:2]) > MAX_SIDE:
        raise ValueError(f"{p['name']} is larger than {MAX_SIDE} px")
    return a, scale


def to_u8(a):
    return np.clip(np.round(a * 255.0), 0, 255).astype(np.uint8)


def save(a, path):
    Image.fromarray(to_u8(a), "RGBA").save(path, optimize=True)


def font(size):
    for name in ("DejaVuSans.ttf", "arial.ttf", "Arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def over(canvas, img, x, y):
    canvas.alpha_composite(img, (int(x), int(y)))


def straight_half(img):
    """0.5x with straight (non-premultiplied) bilinear filtering per channel, the
    way a GPU samples a straight-alpha texture: shows any colour halo."""
    w, h = max(1, img.width // 2), max(1, img.height // 2)
    return Image.merge("RGBA", [c.resize((w, h), Image.BILINEAR) for c in img.split()])


def contact(sprites, path, bg):
    f = font(12)
    cells = []
    for name, a in sprites:
        img = Image.fromarray(to_u8(a), "RGBA")
        half = straight_half(img)
        label_w = int(f.getlength(name[len(PREFIX):])) + 4
        cw = max(img.width + 6 + half.width, label_w)
        ch = max(img.height, half.height) + 18
        cells.append((name, img, half, cw, ch))
    width = 1800
    x = y = 10
    row = 0
    placed = []
    for c in cells:
        if x + c[3] > width - 10 and x > 10:
            x, y, row = 10, y + row + 14, 0
        placed.append((x, y, c))
        x += c[3] + 18
        row = max(row, c[4])
    canvas = Image.new("RGBA", (width, y + row + 10), bg + (255,))
    d = ImageDraw.Draw(canvas)
    ink = (235, 235, 235, 255) if sum(bg) < 300 else (30, 30, 30, 255)
    for x, y, (name, img, half, cw, ch) in placed:
        over(canvas, img, x, y)
        over(canvas, half, x + img.width + 6, y)
        d.text((x, y + max(img.height, half.height) + 3), name[len(PREFIX):], fill=ink, font=f)
    canvas.convert("RGB").save(path, optimize=True)


def nine_slice(img, insets, w, h):
    l, t, r, b = insets
    sw, sh = img.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    xs_src = [0, l, sw - r, sw]
    ys_src = [0, t, sh - b, sh]
    xs_dst = [0, l, w - r, w]
    ys_dst = [0, t, h - b, h]
    for i in range(3):
        for j in range(3):
            sx0, sx1, sy0, sy1 = xs_src[i], xs_src[i + 1], ys_src[j], ys_src[j + 1]
            dx0, dx1, dy0, dy1 = xs_dst[i], xs_dst[i + 1], ys_dst[j], ys_dst[j + 1]
            if sx1 <= sx0 or sy1 <= sy0 or dx1 <= dx0 or dy1 <= dy0:
                continue
            piece = img.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0), Image.BILINEAR)
            out.alpha_composite(piece, (dx0, dy0))
    return out


def slice_test(sprites, insets, path):
    f = font(12)
    rows = []
    for name, a in sprites:
        ins = insets.get(name)
        if not ins:
            continue
        img = Image.fromarray(to_u8(a), "RGBA")
        w, h = img.size
        l, t, r, b = ins
        sizes = [(max(l + r + 8, int(w * 0.75)), h), (int(w * 1.9), h), (int(w * 1.35), int(h * 1.8))]
        rendered = [img] + [nine_slice(img, ins, sw, sh) for sw, sh in sizes]
        rows.append((name, ins, rendered))
    width = max([2000] + [sum(r.width for r in rd) + 14 * len(rd) + 20 for _, _, rd in rows])
    x = y = 10
    rowh = 0
    placed = []
    for name, ins, rendered in rows:
        rw = sum(r.width for r in rendered) + 14 * len(rendered)
        rh = max(r.height for r in rendered) + 18
        if x + rw > width - 10 and x > 10:
            x, y = 10, y + rowh + 12
        if x == 10:
            rowh = 0
        placed.append((x, y, name, ins, rendered))
        x += rw + 30
        rowh = max(rowh, rh)
    canvas = Image.new("RGBA", (width, y + rowh + 10), (58, 70, 58, 255))
    d = ImageDraw.Draw(canvas)
    for x, y, name, ins, rendered in placed:
        cx = x
        for k, r in enumerate(rendered):
            over(canvas, r, cx, y)
            if k == 0:
                l, t, rr, b = ins
                d.rectangle([cx + l, y + t, cx + r.width - rr - 1, y + r.height - b - 1], outline=(0, 255, 255, 255))
            cx += r.width + 14
        d.text((x, y + max(r.height for r in rendered) + 3), f"{name[len(PREFIX):]} {ins}", fill=(240, 240, 240, 255),
               font=f)
    canvas.convert("RGB").save(path, optimize=True)


def alpha_report(sprites):
    """Share of semi-transparent pixels and how many lie > 2 px from the edge."""
    total = partial = deep = 0
    worst = []
    for name, a in sprites:
        alpha = np.round(a[..., 3] * 255).astype(np.int32)
        clear = alpha == 0
        band = dilate(clear, 2)
        p = (alpha > 0) & (alpha < 255)
        total += int((alpha > 0).sum())
        partial += int(p.sum())
        dp = int((p & ~band).sum())
        deep += dp
        if dp:
            worst.append((dp, name))
    return total, partial, deep, sorted(worst, reverse=True)[:10]


# Parts whose 9-slice should only be stretched along one axis: a glyph or an
# arrow sits in the middle of the other axis' edge.
ONE_AXIS = {
    "search": "X", "dropdown": "X", "stepper_box": "X", "tab_category": "X", "tab_arrow_paper": "X",
    "tab_arrow_leather": "X", "row_check_off": "X", "row_check_on": "X", "row_bullet": "X", "divider_diamond": "X",
    "divider_line": "X", "divider_vertical": "Y", "bar_track": "X", "slider_track": "X", "rail_h": "X", "rail_v": "Y",
    "scroll_track": "Y", "scroll_thumb": "Y", "strap_leather": "X", "strap_leather_short": "X",
    **{f"bar_fill_{c}": "X" for c in ("red", "green", "orange", "yellow", "blue")},
}

# Things on the sheets that were deliberately not exported.
SKIPPED = [
    ("01 panels with list / column / checklist guides", "Same frame as lk_window_frame / lk_panel with drawn guide "
     "lines; draw dividers natively or with lk_divider_*."),
    ("01 six-slot row, 05/07/15 numbered hotbars, 02 numbered hotbar", "Baked digits; compose lk_slot_hotbar or "
     "lk_slot_normal + lk_badge_number + text."),
    ("02 hollow frames 2-4 (other sizes)", "Same art as lk_frame_hollow_large, which 9-slices to any size."),
    ("02 coin / gem / gear / backpack / chest HUD buttons", "Icon on a paper square: lk_button_hud + lk_icon_*."),
    ("02 item tiles (axe, torch, logs, stones, plank, flowers)", "Cleaner stand-alone icons exist (16, 10, 11); the "
     "spear, rope, berries, mushroom, hide and bone icons were lifted off their tiles."),
    ("03 PLAY and CONFIRM buttons", "Baked text. Use lk_button_leather_* + lk_glyph_play / lk_glyph_check_white + "
     "native text."),
    ("04 window frames in other sizes", "lk_window_frame 9-slices to all of them."),
    ("05 number badges 2-6, count badges \"12\" / \"99\"", "Digits; the blank lk_badge_number / lk_badge_count(_wide) "
     "replace them."),
    ("07 player card text, LV plaques, party panel, XP bar, menu tiles with icons", "Text / composites. lk_player_card "
     "is the card with its text and headshot removed; lk_tile_frame is a tile with the icon removed."),
    ("08 / 18 / 19 / 20 composed stat and progress bars, value plaques with numbers", "Composites with numbers: "
     "lk_statbar_frame + lk_icon_heart/... + lk_bar_fill_* + text. lk_pill_value is the blank value plaque."),
    ("08 / 20 framed stat icon tiles, 19 framed status tiles", "lk_tile_small / lk_tile_blank + icon. The flag and "
     "build icons only existed framed and were lifted off."),
    ("09 key caps TAB / ESC", "Same art as lk_keycap / lk_keycap_wide with text."),
    ("10 inventory window, Backpack / Vault tabs, \"Search items...\" box, detail cards with icons, count tag",
     "Baked text or broken (the count tag has a transparent hole). Tabs: lk_button_leather_normal (active) / "
     "lk_button_paper_normal (inactive) + lk_icon_backpack_white / lk_icon_chest + text; search: lk_search."),
    ("10 category tab with grid icon", "lk_tab_category is the blank tab (sheet 02)."),
    ("12 quest objective panel, forge recipe card, CLAIM / FORGE buttons, checklist panel", "Composites / baked text."),
    ("13 confirm dialog with text, count-badged frames, glossy status dots, warning/check/cross duplicates",
     "Text / composites; lk_dialog_frame, lk_frame_hollow_small + lk_badge_count, lk_dot_* and the larger "
     "sheet-16 icons cover them."),
    ("13 tooltips with tails (ragged style)", "lk_tooltip + lk_tooltip_tail cover the role."),
    ("14 duplicate rivets, list rows 2-4, extra thin dividers", "Duplicates of exported parts."),
    ("15 Play / Party windows, island map painting", "Composites; the painted map sits on the window paper with no "
     "clean edge (the older pm_map_island sprite remains)."),
    ("15 search box and player row", "Their text was keyed out of the sheet, leaving transparent holes."),
    ("15 portal, backpack button, crown, invite card duplicates", "Same art as exported icons/buttons."),
]


def write_catalog(info, insets, stats):
    by_name = {p["name"]: p for p in PARTS}
    sheets = {p.stem[:2]: p.name for p in KIT.glob("*.png")}
    families = {}
    for name in info:
        short = name[len(PREFIX):]
        fam = "icon" if short.startswith("icon_") else short.split("_")[0]
        families[fam] = families.get(fam, 0) + 1
    area = sum(w * h for w, h, _ in info.values())
    total, partial, deep, _ = stats
    lines = [
        "# Lobby kit sprites (`lk_*`)",
        "",
        "Generated by `art/ui/slice_lobby_kit.py` from the kit sheets in `art/reference/ui/lobby/kit/`; "
        "re-run the script instead of editing this file. Sprites are in `art/ui/sprites/lk_*.png` and in "
        "`art/ui/sprites/manifest.json` (`w`, `h`, `slice` = 9-slice insets `[left, top, right, bottom]` in pixels).",
        "",
        "Contact sheets: `contact_dark.png` (on #202020) and `contact_light.png` (on #F0E6D2) show every sprite at 1x "
        "with a 0.5x copy (straight-alpha bilinear, the way the GPU samples it). `slice_test.png` shows each sliced "
        "sprite at its stored size (cyan box = slice centre) and stretched to three other sizes.",
        "",
        "## Using them",
        "",
        "- Sizes are design pixels of the 1672x941 mockups: show a sprite at its stored size for the mockup look. "
        "Small icons are stored up to about 1.5x their largest on-screen size.",
        "- 9-slice: `ScaleType = Slice`, `SliceCenter = Rect(l, t, w - r, h - b)`, `SliceScale = 1` at design "
        "resolution (scale it with the UI scale). Corners, rivets and ornaments lie inside the insets.",
        "- \"Stretch\" = the axis a sliced sprite may grow along; X-only parts carry a glyph or arrow centred "
        "vertically in their side insets, so set their height to the stored height.",
        "- Text, numbers and placeholder icons were painted out of the parts that had them; draw them natively.",
        "- Glyphs (`lk_glyph_*`) are dark brown (white for `glyph_play` / `glyph_check_white`); tint with "
        "`ImageColor3` if needed.",
        "- No atlas groups are assigned yet (`pack_atlas.py` GROUPS is untouched).",
        "",
        "### Button and state families",
        "",
        "| Family | States |",
        "|---|---|",
        "| `lk_button_leather_*` (primary) | normal, hover, pressed, disabled |",
        "| `lk_button_paper_*` (secondary / inactive tab) | normal, hover, pressed, disabled |",
        "| `lk_button_close_*` | normal, hover, pressed, disabled |",
        "| `lk_button_paper_small_*` | normal, hover, disabled (no pressed: scale it down) |",
        "| `lk_button_flat_*` | leather (selected), paper (normal), disabled |",
        "| `lk_plaque_notched_*` | leather, paper, disabled |",
        "| `lk_slot_*` (hotbar style) | normal, selected, hover, disabled, locked |",
        "| `lk_slot_item_*` (inventory grid) | normal, selected |",
        "| `lk_row_*` | normal, hover, disabled |",
        "| `lk_checkbox_*`, `lk_toggle_*`, `lk_tile_check_*`, `lk_row_check_*` | off, on |",
        "| `lk_ring_*` | track (0 %), half (50 %), full (100 %) |",
        "",
        f"## Totals",
        "",
        f"{len(info)} sprites, {area:,} px in all ({area / 1024 ** 2:.2f} x 1024x1024 before packing gaps; "
        "about 3-4 atlases once packed).",
        "",
        "| Family | Count |",
        "|---|---|",
    ]
    lines += [f"| {fam} | {n} |" for fam, n in sorted(families.items())]
    lines += [
        "",
        f"Alpha after clean-up: {total:,} visible px, {partial:,} semi-transparent "
        f"({100 * partial / max(1, total):.1f} %), {deep} of them more than 2 px inside a silhouette (icon glows "
        "and thin glyphs). Interiors are 255; nothing below the keying fringe survives.",
        "",
        "## Sprites",
        "",
        "| Name | Source sheet + box (x0, y0, x1, y1) | Size | 9-slice [l, t, r, b] | Stretch | Role / where used "
        "| Notes |",
        "|---|---|---|---|---|---|---|",
    ]
    for name in sorted(info):
        p = by_name[name]
        w, h, scale = info[name]
        short = name[len(PREFIX):]
        ins = insets[name]
        stretch = ONE_AXIS.get(short, "X, Y") if ins else ""
        src = f"{sheets.get(p['sid'], p['sid'])} {tuple(p['box'])}"
        lines.append(f"| `{name}` | {src} | {w}x{h} | {ins if ins else ''} | {stretch} | {p['role']} | "
                     f"{p['note']} |".replace("[", "[").replace("  ", " "))
    lines += ["", "## Not exported", "", "| On the sheets | Why / use instead |", "|---|---|"]
    lines += [f"| {a} | {b} |" for a, b in SKIPPED]
    (DOCS / "CATALOG.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    only = set(sys.argv[1:])
    OUT.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    names = [p["name"] for p in PARTS]
    dupes = {n for n in names if names.count(n) > 1}
    if dupes:
        raise ValueError(f"duplicate part names: {sorted(dupes)}")
    sprites, insets, info = [], {}, {}
    for p in PARTS:
        if only and p["name"] not in only and p["name"][len(PREFIX):] not in only:
            continue
        a, scale = build_part(p)
        h, w = a.shape[:2]
        ins = p["slice"]
        if ins is not None:
            l, t, r, b = ins
            if l + r >= w or t + b >= h:
                raise ValueError(f"{p['name']}: insets {ins} do not fit {w}x{h}")
        save(a, OUT / f"{p['name']}.png")
        sprites.append((p["name"], a))
        insets[p["name"]] = ins
        info[p["name"]] = (w, h, scale)
        print(f"{p['name']:34s} {w:4d}x{h:<4d} scale={scale:.3f} slice={ins}")
    if only:
        return
    # Manifest: every non-lk entry is kept as it is (same order, same values).
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.is_file() else {}
    # The flat ink and white glyphs are built from these sprites by
    # art/ui/capture/glyphs.py, which owns their files and entries.
    owned = lambda n: n.startswith(PREFIX) and not n.startswith(GLYPH_PREFIXES)  # noqa: E731
    previous = {n: e for n, e in manifest.items() if owned(n)}
    manifest = {n: e for n, e in manifest.items() if not owned(n)}
    for old in OUT.glob(f"{PREFIX}*.png"):
        if old.stem not in info and owned(old.stem):
            old.unlink()
    for name in sorted(info):
        w, h, _ = info[name]
        entry = {"file": f"{name}.png", "w": int(w), "h": int(h), "slice": insets[name]}
        prev = previous.get(name, {})
        if prev.get("atlas") and prev.get("w") == w and prev.get("h") == h:
            # Keep an atlas placement pack_atlas.py made for this sprite.
            entry["atlas"], entry["rect"] = prev["atlas"], prev["rect"]
        manifest[name] = entry
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    contact(sprites, DOCS / "contact_dark.png", (0x20, 0x20, 0x20))
    contact(sprites, DOCS / "contact_light.png", (0xF0, 0xE6, 0xD2))
    slice_test(sprites, insets, DOCS / "slice_test.png")
    area = sum(w * h for w, h, _ in info.values())
    total, partial, deep, worst = alpha_report(sprites)
    write_catalog(info, insets, (total, partial, deep, worst))
    print(f"{len(info)} sprites, {area} px total ({area / 1024 ** 2:.2f} atlases of 1024x1024 before packing gaps)")
    print(f"alpha: {total} visible px, {partial} semi-transparent ({100 * partial / max(1, total):.2f} %), "
          f"{deep} of them more than 2 px inside the silhouette")
    if worst:
        print("  most interior semi-transparent px:", ", ".join(f"{n} {c}" for c, n in worst))


if __name__ == "__main__":
    main()
