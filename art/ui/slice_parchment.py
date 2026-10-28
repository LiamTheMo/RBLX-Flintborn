"""Slice the parchment-and-leather UI sheets into lobby sprites + manifest.

Inputs : art/reference/ui/parchment/*.png (the 16 reference sheets; the lobby
         master is 13_lobby_master.png, drawn at the HUD's 1672x941 design size)
Outputs: art/ui/sprites/pm_<name>.png, their entries merged into
         art/ui/sprites/manifest.json, and art/ui/sprites/_parchment_contact.png

Plain Python with numpy and Pillow (no Blender needed):

    python3 art/ui/slice_parchment.py
    uv run --with numpy --with pillow art/ui/slice_parchment.py      # Windows

Most lobby sprites are cut from the lobby master itself, so each one lands at
exactly the size and place the master shows. Text and values the game fills in
at runtime (player name, level, Coins, Gems, the party list, the server line)
are erased from the plates: the ink is masked, the hole is filled smoothly from
its edges (push-pull) and re-textured with the grain of a clean parchment
patch. The profile portrait is cut out so the live headshot shows through, and
the XP fill is replaced by the empty track (the fill is its own sprite).

Clean-up of every sprite: alpha <= 24/255 becomes transparent (the sheets carry
a faint red/yellow keying halo), semi-transparent edge pixels take the colour of
the nearest solid pixel, and colour is bled into transparent pixels so Roblox's
bilinear filtering cannot pull in black or red. Deterministic.
"""
import json
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REF = ROOT / "art" / "reference" / "ui" / "parchment"
OUT = HERE / "sprites"
MANIFEST = OUT / "manifest.json"
PAD = 2
# Roblox's largest image side; bigger art is split into tiles of at most TILE px.
MAX_SIDE = 1024
TILE = 1000
TILE_OVERLAP = 2

N4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
N8 = N4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]

_sheets = {}


def sheet(name):
    """RGBA float array (0..1, top-down) of a reference sheet, by file stem prefix."""
    if name not in _sheets:
        path = next(REF.glob(f"{name}*.png"))
        _sheets[name] = np.asarray(Image.open(path).convert("RGBA"), np.float32) / 255.0
    return _sheets[name]


def save(a, path):
    a = np.clip(np.round(a * 255.0), 0, 255).astype(np.uint8)
    Image.fromarray(a, "RGBA").save(path, optimize=True)


# ---------------------------------------------------------------------------
# small numpy helpers (no scipy)
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


def box_blur(x, r):
    """Separable box blur with edge clamping; x is HxW or HxWxC."""
    k = 2 * r + 1
    for axis in (0, 1):
        pad = [(0, 0)] * x.ndim
        pad[axis] = (r + 1, r)
        c = np.cumsum(np.pad(x, pad, mode="edge"), axis=axis)
        hi = np.take(c, range(k, c.shape[axis]), axis=axis)
        lo = np.take(c, range(0, c.shape[axis] - k), axis=axis)
        x = (hi - lo) / k
    return x


def components(mask):
    """4-connected components: list of (ys, xs) index arrays."""
    h, w = mask.shape
    seen = np.zeros_like(mask, bool)
    out = []
    for y0, x0 in zip(*np.nonzero(mask)):
        if seen[y0, x0]:
            continue
        seen[y0, x0] = True
        queue, ys, xs = deque([(y0, x0)]), [], []
        while queue:
            y, x = queue.popleft()
            ys.append(y)
            xs.append(x)
            for dy, dx in N4:
                yy, xx = y + dy, x + dx
                if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    queue.append((yy, xx))
        out.append((np.array(ys), np.array(xs)))
    return out


def flood(passable, seeds):
    """Pixels of `passable` 4-connected to any seed pixel."""
    h, w = passable.shape
    hit = np.zeros_like(passable, bool)
    queue = deque()
    for y, x in zip(*np.nonzero(seeds & passable)):
        hit[y, x] = True
        queue.append((y, x))
    while queue:
        y, x = queue.popleft()
        for dy, dx in N4:
            yy, xx = y + dy, x + dx
            if 0 <= yy < h and 0 <= xx < w and passable[yy, xx] and not hit[yy, xx]:
                hit[yy, xx] = True
                queue.append((yy, xx))
    return hit


def lum(a):
    return a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11


def parchment_like(a):
    """Light paper: bright and warm (the portrait's grey backdrop is not warm)."""
    return (lum(a) > 0.66) & (a[..., 0] - a[..., 2] > 0.17) & (a[..., 3] > 0.9)


# ---------------------------------------------------------------------------
# clean-up
# ---------------------------------------------------------------------------


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
    return rgb


def clean(a):
    a = a.copy()
    alpha = a[..., 3]
    alpha[alpha <= 24 / 255] = 0.0
    solid = alpha >= 0.94
    # Semi-transparent edge pixels take the colour of the nearest solid pixel.
    edge = (alpha > 0) & ~solid
    rgb = bleed_into(a[..., :3], solid, 4)
    a[..., :3] = np.where(edge[..., None], rgb, a[..., :3])
    # Colour into transparent pixels (halo-free filtering).
    a[..., :3] = bleed_into(a[..., :3], alpha > 0, 12)
    return a


def isolate(a, keep_rect=None):
    """Drops alpha islands whose centre lies outside keep_rect (x0, y0, x1, y1),
    i.e. bits of neighbouring sprites that a padded crop picked up."""
    if keep_rect is None:
        return a
    x0, y0, x1, y1 = keep_rect
    a = a.copy()
    for ys, xs in components(a[..., 3] > 0.1):
        cy, cx = ys.mean(), xs.mean()
        if not (x0 <= cx < x1 and y0 <= cy < y1):
            a[ys, xs, 3] = 0.0
    return a


# ---------------------------------------------------------------------------
# erasing baked-in content
# ---------------------------------------------------------------------------


def _down(x):
    h, w = x.shape[:2]
    x = x[: h - h % 2 or h, : w - w % 2 or w]
    if x.shape[0] < 2 or x.shape[1] < 2:
        return x
    return (x[0::2, 0::2] + x[1::2, 0::2] + x[0::2, 1::2] + x[1::2, 1::2]) / 4.0


def _up(x, shape):
    """Bilinear upsample of an HxWxC array to shape (blocky nearest-neighbour
    upsampling would print the pyramid's cells into large fills)."""
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


_grains = {}
# Clean texture patches: plain paper (materials sheet) and blank leather (the
# buttons sheet's leather plate).
GRAIN_SOURCES = {"paper": ("06", (62, 60, 362, 236)), "leather": ("03", (70, 92, 370, 170)),
                 # Leather well inside the plate, clear of its rivets and stitching
                 # (the screens after the lobby use this one).
                 "hide": ("03", (100, 106, 330, 156))}


def grain(kind="paper"):
    """High-pass texture of a clean patch, to re-texture repainted areas."""
    if kind not in _grains:
        name, (x0, y0, x1, y1) = GRAIN_SOURCES[kind]
        patch = sheet(name)[y0:y1, x0:x1, :3]
        _grains[kind] = patch - box_blur(patch, 5)
    return _grains[kind]


def erase(a, mask, amount=0.8, feather=1, texture="paper"):
    """Repaints `mask` from its surroundings plus parchment grain, blending over
    `feather` pixels at its edge. Alpha is kept."""
    a = a.copy()
    # Anti-aliased ink just outside the mask would tint the fill with a ghost of
    # the text, and far pixels (frame outlines) would darken it: fill only from a
    # clean ring of paper around the mask.
    mask = dilate(mask, 1)
    ring = dilate(mask, 8) & ~dilate(mask, 3) & (a[..., 3] > 0.9)
    # Only paper feeds the fill: a leather corner or its shadow beside the mask
    # would smudge into it.
    paper = ring & (lum(a) > 0.78)
    ring = paper if paper.sum() > 50 else ring
    base = push_pull(a[..., :3], ring)
    g = grain(texture)
    h, w = mask.shape
    reps = (h // g.shape[0] + 2, w // g.shape[1] + 2, 1)
    tex = np.tile(np.concatenate([g, g[:, ::-1]], 1), reps)[:h, :w]
    soft = np.clip(box_blur(mask.astype(np.float32), feather) * 1.5, 0, 1)[..., None]
    filled = base + tex[:, : w] * amount
    a[..., :3] = a[..., :3] * (1 - soft) + filled * soft
    return a


def ink(a, rect, threshold=0.68, grow=2):
    """Dark text pixels inside rect (x0, y0, x1, y1), grown to cover anti-aliasing."""
    m = np.zeros(a.shape[:2], bool)
    x0, y0, x1, y1 = rect
    m[y0:y1, x0:x1] = lum(a[y0:y1, x0:x1]) < threshold
    m = dilate(m, grow)
    clip = np.zeros_like(m)
    clip[y0:y1, x0:x1] = True
    return m & clip


def box(shape, rect):
    m = np.zeros(shape[:2], bool)
    x0, y0, x1, y1 = rect
    m[y0:y1, x0:x1] = True
    return m


# ---------------------------------------------------------------------------
# sprites
# ---------------------------------------------------------------------------


def cut(a, rect, pad=PAD):
    """Crop rect (x, y, w, h) with `pad` transparent-safe pixels around it."""
    x, y, w, h = rect
    H, W = a.shape[:2]
    out = np.zeros((h + 2 * pad, w + 2 * pad, 4), np.float32)
    sx0, sy0 = max(0, x - pad), max(0, y - pad)
    sx1, sy1 = min(W, x + w + pad), min(H, y + h + pad)
    out[sy0 - (y - pad): sy1 - (y - pad), sx0 - (x - pad): sx1 - (x - pad)] = a[sy0:sy1, sx0:sx1]
    return out


def cut_clean(a, rect, pad=PAD):
    """Crop plus isolation of the piece itself (its islands centred in rect)."""
    x, y, w, h = rect
    piece = cut(a, rect, pad)
    return isolate(piece, (pad, pad, pad + w, pad + h))


def frame_cutout(a, rect, pad=PAD):
    """A framed button drawn on a panel: the panel paper around its outline is
    made transparent (flood from the crop border over light pixels)."""
    piece = cut(a, rect, pad)
    light = lum(piece) > 0.55
    border = np.zeros(light.shape, bool)
    border[0, :] = border[-1, :] = border[:, 0] = border[:, -1] = True
    outside = flood(light, border)
    piece[outside, 3] = 0.0
    return piece


def icon_mask(tile, inset, corner):
    """The icon on a parchment tile: everything inside the tile that the paper,
    flooded inward from an inset border, cannot reach; corner hardware dropped."""
    h, w = tile.shape[:2]
    paper = parchment_like(tile)
    inner = box(tile.shape, (inset, inset, w - inset, h - inset))
    ring = inner & ~box(tile.shape, (inset + 1, inset + 1, w - inset - 1, h - inset - 1))
    reach = flood(paper & inner, ring)
    rest = inner & ~reach
    keep = np.zeros_like(rest)
    for ys, xs in components(rest):
        cy, cx = ys.mean(), xs.mean()
        in_corner = (min(cy, h - cy) < corner) and (min(cx, w - cx) < corner)
        if len(ys) >= 40 and not in_corner:
            keep[ys, xs] = True
    # Close small gaps between outline pieces, then fill enclosed paper so the
    # icon's own light parts (blades, highlights) stay with it.
    keep = dilate(keep, 1)
    holes = ~flood(~keep, box(tile.shape, (0, 0, w, 1)) | box(tile.shape, (0, h - 1, w, h))
                   | box(tile.shape, (0, 0, 1, h)) | box(tile.shape, (w - 1, 0, w, h)))
    return keep | holes


def extract_icon(tile, inset, corner):
    m = icon_mask(tile, inset, corner)
    icon = tile.copy()
    icon[~m, 3] = 0.0
    ys, xs = np.nonzero(m)
    return icon[ys.min(): ys.max() + 1, xs.min(): xs.max() + 1]


def resize(a, w, h):
    """Premultiplied Lanczos resize of a float RGBA array."""
    pm = a.copy()
    pm[..., :3] *= pm[..., 3:4]
    chans = [np.asarray(Image.fromarray(pm[..., i]).resize((w, h), Image.LANCZOS)) for i in range(4)]
    out = np.clip(np.stack(chans, -1), 0, 1)
    out[..., :3] = np.where(out[..., 3:4] > 1e-4, out[..., :3] / np.maximum(out[..., 3:4], 1e-4), 0)
    return np.clip(out, 0, 1)


def over(dst, src, x, y):
    """Composites src onto dst at (x, y), straight alpha."""
    h, w = src.shape[:2]
    d = dst[y:y + h, x:x + w]
    sa = src[..., 3:4]
    da = d[..., 3:4]
    oa = sa + da * (1 - sa)
    rgb = (src[..., :3] * sa + d[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-6)
    dst[y:y + h, x:x + w] = np.concatenate([rgb, oa], -1)


# ---------------------------------------------------------------------------
# the lobby kit
# ---------------------------------------------------------------------------

# Lobby master element bounds (x, y, w, h) in design pixels, measured from the
# alpha components of 13_lobby_master.png. docs/ui/LobbyScreen.md mirrors these.
M = {
    "profile": (48, 85, 529, 135),
    "coins": (1253, 99, 162, 66),
    "gems": (1425, 99, 132, 66),
    "gear": (1569, 98, 69, 66),
    "party": (1211, 267, 433, 381),
    "tile_inventory": (35, 370, 142, 141),
    # Every tile is cut at one size so all six draw unscaled (the master's are
    # 139-141 px tall; the extra rows are transparent).
    "tile_vault": (182, 370, 142, 141),
    "tile_quests": (35, 517, 142, 141),
    "tile_shop": (182, 517, 142, 141),
    "enter": (525, 741, 622, 180),
    "server": (1150, 799, 251, 71),
}


def build():
    m = sheet("13")
    s = {}

    # Profile: name, level and XP erased, the portrait cut out, empty XP track.
    p = m.copy()
    p = erase(p, ink(p, (203, 114, 392, 150)) | ink(p, (203, 156, 280, 186)))
    # XP fill -> the track's own dark interior: each row repeats a stretch of the
    # empty track, so its grain carries on with no seam.
    for y in range(164, 180):
        p[y, 287:466, :3] = np.resize(p[y, 468:508, :3], (179, 3))
    # Portrait window. The paper photo corners that overlap it stay: paper pixels
    # near the window's own corners (a short diagonal), never the painted
    # portrait (its hands and face are paper-coloured too).
    x0, y0, x1, y1 = 69, 104, 171, 201
    hole = box(p.shape, (x0, y0, x1, y1))
    ys, xs = np.mgrid[0:p.shape[0], 0:p.shape[1]]
    corner = np.zeros_like(hole)
    for cx, cy in ((x0, y0), (x1 - 1, y0), (x0, y1 - 1), (x1 - 1, y1 - 1)):
        corner |= (np.abs(xs - cx) + np.abs(ys - cy)) < 18
    # Cream paper only: the painted hand is paper-bright too, but orange.
    cream = parchment_like(p) & (p[..., 1] > p[..., 0] * 0.78)
    keep = dilate(cream & corner & hole, 2) & corner & hole
    # The tapes' rivets are dark: islands the paper encloses stay too.
    open_window = ~corner & hole
    for ys, xs in components(corner & hole & ~keep):
        island = np.zeros_like(keep)
        island[ys, xs] = True
        if len(ys) < 60 and not (dilate(island, 1) & open_window).any():
            keep |= island
    hole &= ~keep
    # Soft 1 px edge: the cut is anti-aliased instead of stepped.
    cut_alpha = np.clip(1 - box_blur(hole.astype(np.float32), 1) * 1.5, 0, 1)
    p[..., 3] *= cut_alpha
    s["pm_lobby_profile"] = (cut_clean(p, M["profile"]), None)

    # Coins and Gems plates with their icons; the numbers are drawn live.
    c = erase(m, ink(m, (1318, 116, 1396, 148)))
    s["pm_lobby_coins"] = (cut_clean(c, M["coins"]), None)
    g = erase(m, ink(m, (1486, 116, 1536, 148)))
    s["pm_lobby_gems"] = (cut_clean(g, M["gems"]), None)
    s["pm_lobby_gear"] = (cut_clean(m, M["gear"]), None)

    # Party panel: every bit of content erased; rows are drawn live.
    # Only the content is repainted (ink, rules, dots, scrollbar and the member
    # row's pieces), so the paper between keeps its own colour and grain.
    area = (1250, 302, 1613, 603)
    content = box(m.shape, area) & (lum(m) < 0.84)
    # The frame's leather corners reach into the area: anything dark that runs
    # past the area's edge belongs to the frame and stays untouched.
    x0, y0, x1, y1 = area
    inner = box(m.shape, (x0 + 1, y0 + 1, x1 - 1, y1 - 1))
    dark = lum(m) < 0.84
    for ys, xs in components(dark & box(m.shape, (x0 - 40, y0 - 40, x1 + 40, y1 + 40))):
        if not inner[ys, xs].all() and box(m.shape, area)[ys, xs].any():
            frame = np.zeros_like(content)
            frame[ys, xs] = True
            content &= ~dilate(frame, 3)
    # The painted scrollbar joins the frame's edge shading, so it is named here.
    content |= box(m.shape, (1592, 432, 1609, 601))
    for rect in ((1256, 360, 1330, 432), (1486, 378, 1527, 412), (1533, 364, 1609, 424)):
        content |= box(m.shape, rect)
    party = erase(m, dilate(content, 2) & box(m.shape, area), amount=0.8, feather=2)
    s["pm_lobby_party"] = (cut_clean(party, M["party"]), None)
    s["pm_button_add_friend"] = (frame_cutout(m, (1537, 368, 68, 52), pad=0), None)

    # Enter keeps its painted lettering (fixed text); the server line is live.
    s["pm_lobby_enter"] = (cut_clean(m, M["enter"]), None)
    srv = erase(m, ink(m, (1220, 818, 1361, 848)))
    s["pm_lobby_server"] = (cut_clean(srv, M["server"]), None)

    # Navigation tiles: the four the master shows, plus Forge and Trade built on a
    # blank master tile with the icon sheet's hammer-and-axe and group icons.
    for key in ("inventory", "vault", "quests", "shop"):
        s["pm_tile_" + key] = (cut_clean(m, M["tile_" + key]), None)
    tile = cut_clean(m, M["tile_inventory"])
    blank = erase(tile, dilate(icon_mask(tile, 14, 30), 2), amount=0.7)
    icons = sheet("04")
    for key, rect in (("forge", (1024, 21, 217, 212)), ("trade", (1269, 21, 216, 212))):
        art = extract_icon(cut(icons, rect, 0), 20, 48)
        scale = 92.0 / max(art.shape[:2])
        art = resize(art, max(1, round(art.shape[1] * scale)), max(1, round(art.shape[0] * scale)))
        t = blank.copy()
        over(t, art, (t.shape[1] - art.shape[1]) // 2, (t.shape[0] - art.shape[0]) // 2 + 1)
        s["pm_tile_" + key] = (t, None)

    # The XP fill itself: a 9-slice strip with round caps.
    s["pm_fill_xp"] = (cut(m, (287, 165, 176, 14), 0), [7, 6, 7, 6])

    # Small icons from the icon sheet.
    s["pm_icon_crown"] = (cut_clean(icons, (58, 678, 164, 127)), None)
    s["pm_icon_add_friend"] = (cut_clean(icons, (308, 670, 175, 139)), None)

    # Popup card and buttons (9-sliced).
    frames = sheet("01")
    s["pm_panel"] = (cut_clean(frames, (26, 31, 525, 310)), [70, 62, 70, 62])
    buttons = sheet("03")
    for name, rect in (("leather", (20, 66, 397, 136)), ("leather_hover", (429, 65, 402, 137)),
                       ("leather_pressed", (842, 65, 400, 137)), ("leather_disabled", (1253, 65, 401, 137)),
                       ("parchment", (28, 233, 382, 155)), ("parchment_hover", (438, 233, 383, 155)),
                       ("parchment_pressed", (851, 233, 381, 155)), ("parchment_disabled", (1261, 233, 382, 155))):
        insets = [64, 44, 64, 44] if name.startswith("leather") else [56, 48, 56, 48]
        s["pm_button_" + name] = (cut_clean(buttons, rect), insets)
    s["pm_button_x"] = (cut_clean(buttons, (43, 581, 151, 146)), None)
    s["pm_button_check"] = (cut_clean(buttons, (244, 581, 151, 146)), None)
    return s


# ---------------------------------------------------------------------------
# menu kit helpers
# ---------------------------------------------------------------------------


def trim_alpha(a, pad=PAD):
    """Crops to the opaque bounding box with `pad` transparent pixels around."""
    ys, xs = np.nonzero(a[..., 3] > 0.02)
    a = a[ys.min(): ys.max() + 1, xs.min(): xs.max() + 1]
    out = np.zeros((a.shape[0] + 2 * pad, a.shape[1] + 2 * pad, 4), np.float32)
    out[pad:pad + a.shape[0], pad:pad + a.shape[1]] = a
    return out


def plate(a, rect):
    """A button or tab drawn on paper: cut out (paper around it made clear),
    reduced to its largest piece and trimmed."""
    piece = frame_cutout(a, rect, pad=0)
    parts = components(piece[..., 3] > 0.1)
    if parts:
        ys, xs = max(parts, key=lambda c: len(c[0]))
        keep = np.zeros(piece.shape[:2], bool)
        keep[ys, xs] = True
        piece[~dilate(keep, 1), 3] = 0.0
    return trim_alpha(piece)


def silhouette(a, rect, dark=True, lo=0.30, hi=0.75):
    """A glyph as a white silhouette (tinted in game with ImageColor3): alpha is how
    far each pixel is from the background toward the ink (dark ink on paper, or
    light ink on leather when dark=False)."""
    x, y, w, h = rect
    piece = a[y:y + h, x:x + w]
    L = lum(piece)
    alpha = (hi - L) / (hi - lo) if dark else (L - lo) / (hi - lo)
    # Transparent sheet pixels (an icon on the icon sheet) are never ink.
    alpha = np.clip(alpha, 0, 1) * piece[..., 3]
    # Keep the glyph's own islands, not stray texture.
    keep = np.zeros(alpha.shape, bool)
    for ys, xs in components(alpha > 0.5):
        if len(ys) >= 25:
            keep[ys, xs] = True
    alpha *= dilate(keep, 2)
    out = np.ones(piece.shape, np.float32)
    out[..., 3] = alpha
    return trim_alpha(out)


def disc(a, cx, cy, r):
    """A round piece (a slider knob) cut with an anti-aliased circular mask."""
    size = int(2 * r + 2 * PAD)
    x0, y0 = int(cx - r - PAD), int(cy - r - PAD)
    piece = a[y0:y0 + size, x0:x0 + size].copy()
    ys, xs = np.mgrid[0:size, 0:size]
    d = np.sqrt((xs + 0.5 - (cx - x0)) ** 2 + (ys + 0.5 - (cy - y0)) ** 2)
    piece[..., 3] *= np.clip(r - d + 0.5, 0, 1)
    return piece


def rounded_cut(a, rect, r):
    """A rounded-rectangle piece (x, y, w, h, corner radius r) cut out of busy art
    with an anti-aliased mask, where flooding the background would leak."""
    x, y, w, h = rect
    piece = cut(a, rect)
    ys, xs = np.mgrid[0:h + 2 * PAD, 0:w + 2 * PAD]
    px, py = xs + 0.5 - PAD, ys + 0.5 - PAD
    dx = np.maximum(np.maximum(r - px, px - (w - r)), 0)
    dy = np.maximum(np.maximum(r - py, py - (h - r)), 0)
    inside = np.where((dx > 0) & (dy > 0), r - np.sqrt(dx ** 2 + dy ** 2),
                      np.minimum(np.minimum(px, w - px), np.minimum(py, h - py)))
    piece[..., 3] *= np.clip(inside + 0.5, 0, 1)
    return piece


def pin_cut(a, cx, cy, r, tip):
    """A map pin: the round head (centre cx, cy, radius r) and its pointed foot down
    to y `tip`, cut out of whatever it is drawn over."""
    x0, y0 = int(cx - r - PAD), int(cy - r - PAD)
    w, h = int(2 * r + 2 * PAD), int(tip - y0 + PAD + 1)
    piece = a[y0:y0 + h, x0:x0 + w].copy()
    ys, xs = np.mgrid[0:h, 0:w]
    px, py = xs + 0.5 + x0, ys + 0.5 + y0
    head = np.clip(r - np.sqrt((px - cx) ** 2 + (py - cy) ** 2) + 0.5, 0, 1)
    # The foot: a triangle from the head's lower sides to the tip.
    top = cy + r * 0.66
    half = r * 0.78 * np.clip((tip - py) / (tip - top), 0, 1)
    foot = np.clip(half - np.abs(px - cx) + 0.5, 0, 1) * (py >= cy) * (py <= tip + 0.5)
    piece[..., 3] *= np.maximum(head, foot)
    return piece


def erase_ink(a, rect, dark=True, threshold=None, grow=2, amount=0.8, texture="paper"):
    """Erases text or a glyph inside rect: dark ink on paper, or light ink on leather."""
    x0, y0, x1, y1 = rect
    m = np.zeros(a.shape[:2], bool)
    L = lum(a[y0:y1, x0:x1])
    if dark:
        m[y0:y1, x0:x1] = L < (threshold or 0.62)
    else:
        m[y0:y1, x0:x1] = L > (threshold or 0.55)
    m = dilate(m, grow) & box(a.shape, rect)
    return erase(a, m, amount=amount, texture=texture)


def build_settings():
    """Settings window (10_settings): the shell with tabs and content erased, and
    the pieces its screen is built from."""
    g = sheet("10")
    s = {}
    # Tabs: the selected (leather) and normal (paper) plates, label and icon erased.
    sel = plate(g, (84, 190, 320, 104))
    # The leather face between its stitch lines is repainted whole (label and
    # icon), so no ghost of either stays.
    sel = erase(sel, box(sel.shape, (22, 24, 264, 82)), amount=1.0, feather=3, texture="hide")
    s["pm_tab_leather"] = (sel, [40, 30, 52, 30])
    tab = plate(g, (86, 294, 316, 100))
    tab = erase_ink(tab, (26, 10, 262, 92), dark=True)
    s["pm_tab_paper"] = (tab, [40, 30, 52, 30])
    # Tab icons as white silhouettes.
    s["pm_glyph_gear"] = (silhouette(g, (116, 212, 66, 66), dark=False, lo=0.35, hi=0.8), None)
    s["pm_glyph_sound"] = (silhouette(g, (116, 312, 66, 62)), None)
    s["pm_glyph_monitor"] = (silhouette(g, (112, 408, 72, 66)), None)
    s["pm_glyph_gamepad"] = (silhouette(g, (112, 510, 72, 62)), None)
    s["pm_glyph_person"] = (silhouette(g, (116, 606, 64, 74)), None)
    s["pm_glyph_diamond"] = (silhouette(g, (448, 222, 26, 28)), None)
    # Window shell: the tab column and the whole content panel repainted as paper.
    win = erase(g, box(g.shape, (84, 190, 404, 702)), amount=0.8, feather=4)
    # RESET and APPLY are repainted too (their own sprites draw over the spot and
    # dim cleanly); only the strip where APPLY meets the leather corner keeps its
    # pixels, under APPLY's own right end, so no hard edge cuts into the corner.
    content = box(g.shape, (424, 197, 1584, 724)) & ~box(g.shape, (1574, 618, 1592, 728))
    win = erase(win, content, amount=0.8, feather=4)
    s["pm_window_settings"] = (cut_clean(win, (23, 60, 1626, 702)), None)
    # Controls from the component strip.
    s["pm_check_off"] = (cut_clean(g, (50, 817, 54, 57)), None)
    s["pm_check_on"] = (cut_clean(g, (152, 812, 66, 67)), None)
    dd = erase_ink(g, (290, 820, 420, 870), dark=True)
    s["pm_dropdown"] = (cut_clean(dd, (267, 810, 235, 69)), [30, 26, 72, 26])
    s["pm_slider_knob"] = (disc(g, 746, 842, 27), None)
    for name, rect, text in (("pm_keycap", (1098, 814, 112, 67), (1110, 824, 1200, 868)),
                             ("pm_keycap_small", (1249, 814, 75, 67), (1258, 824, 1316, 868))):
        k = erase_ink(g, text, dark=True)
        s[name] = (cut_clean(k, rect), [22, 22, 22, 26] if name == "pm_keycap" else None)
    s["pm_button_reset"] = (plate(g, (1076, 634, 214, 76)), None)
    # The leather corner of the window touches APPLY's lower right: cut on the
    # button's own rounded outline instead.
    s["pm_button_apply"] = (rounded_cut(g, (1309, 629, 272, 85), 12), None)
    return s


def build_journal():
    """Journal window (07_journal): the shell with the quest list, the quest card's
    contents and the map erased, and the pieces the screen is built from. Reward
    and objective icons come from the icon sheet (04_icons)."""
    g = sheet("07")
    s = {}
    # Window: list column, quest card contents and the map repainted as paper
    # (the card's and map's own frames stay).
    win = erase(g, box(g.shape, (60, 142, 441, 760)), amount=0.8, feather=4)
    win = erase(win, box(g.shape, (468, 140, 932, 761)), amount=0.8, feather=3)
    win = erase(win, box(g.shape, (972, 140, 1613, 753)), amount=0.8, feather=4)
    # The strip's map pin overlaps the window's bottom edge: patch that stretch of
    # frame from the stretch beside it.
    win[738:792, 1246:1350] = win[738:792, 1126:1230]
    s["pm_window_journal"] = (cut_clean(win, (22, 20, 1628, 768)), None)
    # Category tabs: selected leather, normal paper, labels erased.
    tab = cut_clean(g, (63, 144, 122, 54))
    s["pm_jtab_leather"] = (erase_ink(tab, (14, 8, 112, 50), dark=False, texture="hide"), [20, 16, 20, 8])
    tab = plate(g, (189, 146, 125, 52))
    s["pm_jtab_paper"] = (erase_ink(tab, (16, 8, 110, 50), dark=True), [20, 16, 20, 8])
    # Quest rows (scroll icon and chevron kept; name and status dot erased).
    row = plate(g, (68, 204, 366, 92))
    row = erase_ink(row, (92, 14, 296, 80), dark=True)
    s["pm_quest_row_selected"] = (erase(row, box(row.shape, (290, 18, 332, 74)), amount=1.0, feather=2), [40, 30, 40, 30])
    # A plain row as the list draws it (cut on its rounded outline).
    row = rounded_cut(g, (72, 299, 358, 84), 8)
    row = erase_ink(row, (96, 12, 292, 76), dark=True)
    s["pm_quest_row"] = (erase(row, box(row.shape, (290, 24, 326, 60)), amount=1.0, feather=2), [40, 30, 40, 30])
    # Leather strip buttons with their labels erased (CLAIM, the active count).
    claim = plate(g, (506, 682, 388, 78))
    s["pm_button_claim"] = (erase_ink(claim, (90, 12, 300, 64), dark=False, texture="hide"), [70, 26, 70, 26])
    count = plate(g, (76, 675, 354, 76))
    s["pm_button_strip"] = (erase_ink(count, (70, 12, 290, 62), dark=False, texture="hide"), [64, 26, 64, 26])
    # Card pieces.
    # The mountain mark in the middle of the card's dividers (the lines are drawn
    # natively, so the mark never stretches).
    s["pm_glyph_mountain"] = (silhouette(g, (668, 522, 62, 32), lo=0.35, hi=0.8), None)
    s["pm_check_green"] = (rounded_cut(g, (487, 450, 28, 28), 4), None)
    # Map pieces: compass rose, zoom buttons, the red pin and its name plate.
    s["pm_compass_rose"] = (silhouette(g, (1500, 146, 106, 120), lo=0.3, hi=0.7), None)
    s["pm_button_zoom_in"] = (rounded_cut(g, (1548, 542, 58, 58), 9), None)
    s["pm_button_zoom_out"] = (rounded_cut(g, (1548, 608, 58, 59), 9), None)
    s["pm_map_pin"] = (pin_cut(g, 1297, 789, 40, 862), None)
    label = plate(g, (1262, 808, 296, 104))
    # The pin's foot covers the plate's left end: that end is the right end
    # mirrored (the plate is symmetric).
    half = label.shape[1] // 2
    label[:, :half] = label[:, ::-1][:, :half]
    s["pm_map_label"] = (erase_ink(label, (70, 20, label.shape[1] - 70, 68), dark=True), [40, 30, 40, 30])
    # The painted island (art/ui/map/render_island.py) for the map panels.
    island = np.asarray(Image.open(HERE / "map" / "island.png").convert("RGBA"), np.float32) / 255
    s["pm_map_island"] = (island, None)
    # Icons from the icon sheet (on transparency).
    i = sheet("04")
    s["pm_icon_scroll"] = (cut_clean(i, (552, 484, 178, 160)), None)
    s["pm_icon_coin"] = (cut_clean(i, (1058, 494, 172, 162)), None)
    s["pm_icon_gem"] = (cut_clean(i, (1318, 488, 124, 164)), None)
    s["pm_icon_bolt"] = (cut_clean(i, (838, 662, 126, 156)), None)
    return s


def build_inventory():
    """Inventory & Vault window (08_inventory_vault): the shell with both panes,
    the middle column and the detail strip repainted as paper and the title
    erased (the game writes "INVENTORY & VAULT" or "INVENTORY"), plus the slots,
    controls and category tabs the screen is built from."""
    g = sheet("08")
    s = {}
    win = erase_ink(g, (560, 30, 1112, 92), dark=False, texture="hide", threshold=0.6, grow=3, amount=1.0)
    # The ampersand is repainted whole (its anti-aliased edge survives the ink pass).
    win = erase(win, box(g.shape, (878, 36, 924, 90)), amount=1.0, feather=2, texture="hide")
    # Stitch dashes left over from the erased mark under the title.
    win = erase(win, box(g.shape, (824, 86, 868, 100)), amount=1.0, feather=2, texture="hide")
    for rect in ((206, 131, 830, 614), (843, 130, 941, 617), (955, 131, 1592, 614), (210, 627, 1586, 771)):
        win = erase(win, box(g.shape, rect), amount=0.8, feather=3)
    # The category tabs are drawn on their own: clear what of them overlaps the
    # window's left edge.
    win = win.copy()
    win[105:650, :163, 3] = 0.0
    s["pm_window_inventory"] = (cut_clean(win, (150, 8, 1490, 782)), None)
    # Category tabs down the left: backgrounds with the icon erased, and the icons.
    tabs = {"all": (48, 114, 122, 124), "tools": (44, 250, 120, 124), "materials": (44, 380, 120, 124),
            "food": (44, 510, 120, 124)}
    for key, rect in tabs.items():
        tab = cut_clean(g, rect)
        s["pm_cat_" + key] = (extract_icon(tab, 14, 26), None)
    # The whole tab column (wooden spine, ropes and four plain tiles, icons
    # erased): the first tile's glow is replaced by a copy of the second tile, so
    # the glowing tile can be laid on whichever tab is chosen.
    column = g.copy()
    column[110:244, 36:172] = g[246:380, 36:172]
    for y0, y1 in ((122, 236), (258, 370), (388, 500), (518, 636)):
        column = erase(column, box(g.shape, (64, y0, 150, y1)), amount=1.0, feather=4)
    s["pm_side_column"] = (cut_clean(column, (20, 95, 152, 565)), None)
    glow = rounded_cut(g, (50, 112, 118, 130), 16)
    s["pm_side_tab_selected"] = (erase(glow, box(glow.shape, (16, 12, 104, 120)), amount=1.0, feather=4), None)
    # Slots and controls.
    s["pm_item_slot"] = (rounded_cut(g, (216, 518, 93, 92), 9), [20, 20, 20, 20])
    search = rounded_cut(g, (497, 141, 226, 42), 9)
    s["pm_search_box"] = (erase_ink(search, (46, 6, 220, 40), dark=True, threshold=0.7), [40, 14, 14, 14])
    s["pm_sort_button"] = (rounded_cut(g, (737, 141, 77, 42), 9), None)
    s["pm_arrow_right"] = (rounded_cut(g, (851, 276, 82, 71), 13), None)
    s["pm_arrow_left"] = (rounded_cut(g, (851, 375, 82, 70), 13), None)
    store = rounded_cut(g, (836, 516, 112, 89), 10)
    s["pm_button_square"] = (erase_ink(store, (16, 14, 98, 78), dark=False, texture="hide"), [26, 26, 26, 26])
    chip = rounded_cut(g, (408, 698, 100, 43), 9)
    s["pm_stat_chip"] = (erase_ink(chip, (8, 5, 96, 40), dark=True, threshold=0.6), [16, 14, 16, 14])
    s["pm_glyph_sword"] = (silhouette(g, (414, 703, 32, 34)), None)
    s["pm_glyph_hammer"] = (silhouette(g, (533, 703, 32, 34)), None)
    s["pm_glyph_weight"] = (silhouette(g, (648, 703, 30, 34)), None)
    action = plate(g, (1102, 652, 226, 82))
    s["pm_button_action"] = (erase_ink(action, (34, 14, 196, 68), dark=False, texture="hide"), [40, 26, 40, 26])
    icons = sheet("04")
    s["pm_icon_chest"] = (cut_clean(icons, (290, 482, 210, 166)), None)
    return s


def build_crafting():
    """Crafting window (09_crafting): the shell with the recipe column, the
    detail card and the queue repainted as paper (title, close and panel frames
    stay), and the tabs, rows, chips, cards, stepper and buttons."""
    g = sheet("09")
    s = {}
    win = g
    for rect in ((76, 168, 484, 772), (518, 172, 1168, 772), (1194, 170, 1616, 772)):
        win = erase(win, box(g.shape, rect), amount=0.8, feather=3)
    s["pm_window_crafting"] = (cut_clean(win, (25, 60, 1625, 738)), None)
    # The same shell for the lobby's Forge, its title word erased (the game
    # writes it; the hammers stay).
    forge = erase_ink(win, (196, 96, 450, 152), dark=True, threshold=0.5, grow=3, amount=1.0)
    s["pm_window_forge"] = (cut_clean(forge, (25, 60, 1625, 738)), None)
    # Category tabs: selected (gold) and plain, glyph erased; the glyphs as
    # white silhouettes.
    tab = rounded_cut(g, (82, 235, 79, 60), 7)
    s["pm_ctab_selected"] = (erase(tab, box(tab.shape, (12, 8, 70, 56)), amount=1.0, feather=2), [16, 14, 16, 14])
    tab = rounded_cut(g, (163, 235, 78, 60), 7)
    s["pm_ctab"] = (erase(tab, box(tab.shape, (12, 8, 70, 56)), amount=1.0, feather=2), [16, 14, 16, 14])
    for key, rect in (("tools", (90, 242, 64, 48)), ("tent", (170, 242, 64, 48)), ("armor", (250, 242, 64, 48)),
                      ("bench", (328, 242, 64, 48)), ("bag", (406, 242, 62, 48))):
        s["pm_glyph_" + key] = (silhouette(g, rect, lo=0.3, hi=0.62), None)
    # Recipe rows (chevron kept; icon and name erased).
    for name, rect in (("pm_recipe_row_selected", (80, 307, 401, 72)), ("pm_recipe_row", (80, 385, 401, 70))):
        row = rounded_cut(g, rect, 7)
        s[name] = (erase(row, box(row.shape, (10, 6, 350, rect[3] - 2)), amount=1.0, feather=2), [30, 24, 60, 24])
    # Detail card pieces.
    chip = rounded_cut(g, (827, 295, 102, 68), 8)
    s["pm_stat_chip_tall"] = (erase(chip, box(chip.shape, (8, 8, 96, 62)), amount=1.0, feather=2), [18, 18, 18, 18])
    card = rounded_cut(g, (830, 447, 102, 152), 8)
    s["pm_req_card"] = (erase(card, box(card.shape, (8, 10, 96, 146)), amount=1.0, feather=2), [18, 18, 18, 18])
    s["pm_stepper_minus"] = (rounded_cut(g, (535, 670, 60, 61), 8), None)
    s["pm_stepper_plus"] = (rounded_cut(g, (667, 670, 60, 61), 8), None)
    field = rounded_cut(g, (595, 672, 73, 58), 3)
    s["pm_stepper_field"] = (erase(field, box(field.shape, (10, 6, 66, 56)), amount=1.0, feather=2), [10, 10, 10, 10])
    craft = plate(g, (754, 655, 280, 92))
    s["pm_button_craft"] = (erase_ink(craft, (70, 14, 210, 76), dark=False, texture="hide"), [70, 26, 70, 26])
    small = rounded_cut(g, (1041, 672, 125, 60), 9)
    s["pm_button_paper"] = (erase_ink(small, (12, 8, 114, 52), dark=True), [22, 18, 22, 18])
    # Queue.
    queue = rounded_cut(g, (1205, 230, 400, 94), 8)
    s["pm_queue_row"] = (erase(queue, box(queue.shape, (8, 8, 334, 88)), amount=1.0, feather=2), [24, 24, 60, 24])
    s["pm_queue_empty"] = (rounded_cut(g, (1205, 541, 400, 92), 10), None)
    s["pm_button_x_leather"] = (rounded_cut(g, (1547, 252, 51, 49), 6), None)
    # Food & potions tab: the icon sheet's heart as a silhouette.
    s["pm_glyph_heart"] = (silhouette(sheet("04"), (566, 662, 162, 150), lo=0.55, hi=0.9), None)
    return s


def contact(sprites, path):
    items = [(n, a) for n, (a, _) in sorted(sprites.items())]
    width = max(1600, max(a.shape[1] for _, a in items) + 20)
    x, y, row, gap = 10, 10, 0, 12
    placed = []
    for name, a in items:
        h, w = a.shape[:2]
        if x + w > width:
            x, y, row = 10, y + row + gap, 0
        placed.append((x, y, a))
        x += w + gap
        row = max(row, h)
    canvas = np.zeros((y + row + 10, width, 4), np.float32)
    canvas[..., :3] = (0.24, 0.33, 0.24)
    canvas[..., 3] = 1
    for x, y, a in placed:
        over(canvas, a, x, y)
    save(canvas, path)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sprites = build()
    sprites.update(build_settings())
    sprites.update(build_journal())
    sprites.update(build_inventory())
    sprites.update(build_crafting())
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.is_file() else {}
    for name in [n for n in manifest if n.startswith("pm_")]:
        del manifest[name]
    for old in OUT.glob("pm_*.png"):
        old.unlink()
    for name, (a, insets) in sorted(sprites.items()):
        a = clean(a)
        sprites[name] = (a, insets)
        h, w = a.shape[:2]
        if w <= MAX_SIDE and h <= MAX_SIDE:
            save(a, OUT / f"{name}.png")
            manifest[name] = {"file": f"{name}.png", "w": int(w), "h": int(h), "slice": insets}
        else:
            # Roblox shrinks uploads past 1024 px: big art goes up as tiles that
            # Widgets.Sprite lays back together (tiles overlap by TILE_OVERLAP so
            # filtering leaves no seam).
            tiles = []
            cols, rows = -(-w // TILE), -(-h // TILE)
            for row in range(rows):
                for col in range(cols):
                    x0, y0 = col * w // cols, row * h // rows
                    x1, y1 = (col + 1) * w // cols, (row + 1) * h // rows
                    ex0, ey0 = max(0, x0 - TILE_OVERLAP), max(0, y0 - TILE_OVERLAP)
                    ex1, ey1 = min(w, x1 + TILE_OVERLAP), min(h, y1 + TILE_OVERLAP)
                    tile = f"{name}__{row + 1}_{col + 1}"
                    save(a[ey0:ey1, ex0:ex1], OUT / f"{tile}.png")
                    manifest[tile] = {"file": f"{tile}.png", "w": int(ex1 - ex0), "h": int(ey1 - ey0), "slice": None}
                    tiles.append([tile, int(ex0), int(ey0), int(ex1 - ex0), int(ey1 - ey0)])
            manifest[name] = {"file": None, "w": int(w), "h": int(h), "slice": None, "tiles": tiles}
        print(f"{name:28s} {w:4d}x{h:<4d} slice={insets}" + (" (tiled)" if w > MAX_SIDE or h > MAX_SIDE else ""))
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    contact(sprites, OUT / "_parchment_contact.png")
    print(f"{len(sprites)} parchment sprites -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
