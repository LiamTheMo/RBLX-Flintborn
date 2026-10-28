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


_grain = None


def grain():
    """High-pass texture of a clean parchment plate (materials sheet, plain paper)."""
    global _grain
    if _grain is None:
        paper = sheet("06")[60:236, 62:362, :3]
        _grain = paper - box_blur(paper, 5)
    return _grain


def erase(a, mask, amount=0.8, feather=1):
    """Repaints `mask` from its surroundings plus parchment grain, blending over
    `feather` pixels at its edge. Alpha is kept."""
    a = a.copy()
    # Anti-aliased ink just outside the mask would tint the fill with a ghost of
    # the text, and far pixels (frame outlines) would darken it: fill only from a
    # clean ring of paper around the mask.
    mask = dilate(mask, 1)
    ring = dilate(mask, 8) & ~dilate(mask, 3) & (a[..., 3] > 0.9)
    base = push_pull(a[..., :3], ring)
    g = grain()
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
    keep = dilate(parchment_like(p) & corner & hole, 2) & corner & hole
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


def contact(sprites, path):
    items = [(n, a) for n, (a, _) in sorted(sprites.items())]
    width, x, y, row, gap = 1600, 10, 10, 0, 12
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
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.is_file() else {}
    for name in [n for n in manifest if n.startswith("pm_")]:
        del manifest[name]
    for name, (a, insets) in sorted(sprites.items()):
        a = clean(a)
        sprites[name] = (a, insets)
        save(a, OUT / f"{name}.png")
        h, w = a.shape[:2]
        manifest[name] = {"file": f"{name}.png", "w": int(w), "h": int(h), "slice": insets}
        print(f"{name:28s} {w:4d}x{h:<4d} slice={insets}")
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    contact(sprites, OUT / "_parchment_contact.png")
    print(f"{len(sprites)} parchment sprites -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
