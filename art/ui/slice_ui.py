"""Slice the Flintborn UI reference sheets into alpha-clean sprites + manifest.

Run headless with Blender's Python (no system Python needed):

    "D:/Steam/steamapps/common/Blender/blender.exe" --background --factory-startup \
        --python-exit-code 1 --python art/ui/slice_ui.py < /dev/null

Inputs : art/reference/ui/sheet_hud_widgets.png, sheet_icons.png, sheet_frames.png
Outputs: art/ui/sprites/<name>.png, manifest.json, _contact_dark.png,
         _contact_light.png, _slice_test.png

The sheets already carry an alpha channel, but the edge pixels were badly
keyed: near-zero-alpha pixels hold saturated red/olive garbage colour, a
1/255 alpha haze covers the background, and the RGB under transparent pixels
is black/red (which bleeds into edges when Roblox filters the texture).
Clean-up per sheet:
  1. alpha floor: alpha <= 6/255 -> 0 (removes the haze, never touches opaque
     panel interiors).
  2. connectivity: the "outside" is every large low-alpha region (the region
     connected to the sheet border plus the hollow holes of open frames).
     Only pixels in / next to that region are keyed, so opaque dark panel
     interiors can never be punched through.
  3. red fringe: saturated-red pixels next to the outside whose nearest solid
     neighbour is not red are removed (alpha < 0.3) or recoloured.
  4. colour de-fringe: semi-transparent edge pixels are blended toward the
     colour of the nearest solid pixel; cyan glows are left alone.
  5. 1px feather on hard silhouette pixels, then RGB bleed into fully
     transparent pixels so bilinear filtering cannot pull in black/red.
Deterministic: no randomness, fixed iteration order.
"""
import bpy
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
REF = os.path.join(ROOT, "art", "reference", "ui")
OUT = os.path.join(HERE, "sprites")

PAD = 2
FILL = (0.135, 0.135, 0.132)  # HUD dark-panel interior colour (sampled)

# ----------------------------------------------------------------------------
# image io
# ----------------------------------------------------------------------------


def load(path):
    im = bpy.data.images.load(path)
    w, h = im.size
    a = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)[::-1].copy()
    bpy.data.images.remove(im)
    return a


def save(a, path):
    a = np.clip(a, 0.0, 1.0).astype(np.float32)
    h, w = a.shape[:2]
    if a.shape[2] == 3:
        a = np.concatenate([a, np.ones((h, w, 1), np.float32)], 2)
    # quantise ourselves so the byte buffer is exactly what we expect
    a = np.round(a * 255.0) / 255.0
    im = bpy.data.images.new("tmp_out", w, h, alpha=True)
    im.pixels.foreach_set(np.ascontiguousarray(a[::-1]).ravel())
    im.filepath_raw = path
    im.file_format = "PNG"
    im.save()
    bpy.data.images.remove(im)


# ----------------------------------------------------------------------------
# numpy morphology helpers (no scipy in Blender's Python)
# ----------------------------------------------------------------------------

N4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
N8 = N4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]


def shift(m, dy, dx, fill=0):
    """out[y, x] = m[y - dy, x - dx]"""
    out = np.full_like(m, fill)
    H, W = m.shape[:2]
    ys = slice(max(dy, 0), H + min(dy, 0))
    yd = slice(max(-dy, 0), H + min(-dy, 0))
    xs = slice(max(dx, 0), W + min(dx, 0))
    xd = slice(max(-dx, 0), W + min(-dx, 0))
    out[ys, xs] = m[yd, xd]
    return out


def dilate(m, r=1, nb=N8):
    m = m.copy()
    for _ in range(r):
        o = m.copy()
        for dy, dx in nb:
            o |= shift(m, dy, dx, False)
        m = o
    return m


def box3(x):
    s = x.copy()
    for dy, dx in N8:
        s = s + shift(x, dy, dx, 0)
    return s / 9.0


def label(mask):
    """4-connected component labels (label = min flat index), BIG for bg."""
    H, W = mask.shape
    BIG = H * W
    lab = np.where(mask, np.arange(H * W).reshape(H, W), BIG)
    while True:
        old = lab
        for _ in range(4):
            n = lab.copy()
            n[1:] = np.minimum(n[1:], lab[:-1])
            n[:-1] = np.minimum(n[:-1], lab[1:])
            n[:, 1:] = np.minimum(n[:, 1:], lab[:, :-1])
            n[:, :-1] = np.minimum(n[:, :-1], lab[:, 1:])
            lab = np.where(mask, n, BIG)
        f = lab.ravel().copy()
        m = mask.ravel()
        for _ in range(8):
            f[m] = f[f[m]]
        lab = f.reshape(H, W)
        if np.array_equal(lab, old):
            return lab


def bleed(rgb, known, iters):
    """Fill unknown pixels with the average colour of known neighbours,
    growing outward `iters` pixels. Returns (colour, known_mask)."""
    col = rgb * known[..., None]
    kn = known.copy()
    for _ in range(iters):
        s = np.zeros_like(col)
        c = np.zeros(kn.shape, np.float32)
        ck = col * kn[..., None]
        kf = kn.astype(np.float32)
        for dy, dx in N8:
            s += shift(ck, dy, dx, 0)
            c += shift(kf, dy, dx, 0)
        new = (~kn) & (c > 0)
        if not new.any():
            break
        col[new] = s[new] / c[new][:, None]
        kn = kn | new
    return col, kn


# ----------------------------------------------------------------------------
# sheet clean-up
# ----------------------------------------------------------------------------


def is_glow(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (b > 0.45) & (g > 0.35) & (b > r + 0.25)


def clean_sheet(a):
    a = a.copy()
    rgb = a[..., :3]
    al = a[..., 3]
    al[al <= 6.0 / 255.0] = 0.0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    glow = is_glow(rgb)

    # "outside" = large low-alpha regions (border-connected background and
    # the transparent holes of open frames). Opaque panels are never in it.
    low = al < 0.5
    lab = label(low)
    ids, cnt = np.unique(lab[low], return_counts=True)
    outside = np.isin(lab, ids[cnt >= 300]) & low
    near = dilate(outside, 2)

    redf = (r > 0.3) & (r > 2.5 * g) & (r > 2.5 * b)
    solid = (al >= 0.6) & ~redf
    ncol, nkn = bleed(rgb, solid, 10)
    nred = (ncol[..., 0] > 0.3) & (ncol[..., 0] > 2.0 * ncol[..., 1]) & (
        ncol[..., 0] > 2.0 * ncol[..., 2])

    fringe = near & redf & ~nred & ~glow & nkn
    # haze: faint pixels that are not part of a 1-2px anti-alias ramp
    haze = outside & (al < 0.3) & ~dilate(al >= 0.5, 2) & ~glow
    kill = (outside & (al < 0.14) & ~glow) | (fringe & (al < 0.3)) | haze
    al[kill] = 0.0
    rec = fringe & (al >= 0.3)
    rgb[rec] = ncol[rec]

    t = np.clip((al - 0.1) / 0.5, 0.0, 1.0)
    dm = near & (al > 0) & (al < 0.6) & ~glow & ~rec & nkn
    rgb[dm] = ncol[dm] * (1.0 - t[dm][:, None]) + rgb[dm] * t[dm][:, None]

    # 1px feather on hard silhouette pixels
    zero = al == 0
    edge = dilate(zero, 1, N4) & ~zero & near & (al > 0.5)
    m3 = box3(al)
    al[edge] = 0.5 * al[edge] + 0.5 * m3[edge]

    # bleed colour into transparent pixels (texture filtering safety)
    col2, kn2 = bleed(rgb, al > 0, 4)
    z = al == 0
    rgb[z] = np.where(kn2[z][:, None], col2[z], 0.0)
    return a


# ----------------------------------------------------------------------------
# per-sprite operations
# ----------------------------------------------------------------------------


def op_cols(a, x0, x1, y0, y1, src):
    """Replace columns x0..x1 (rows y0..y1) with a copy of column `src`."""
    a[y0:y1, x0:x1] = a[y0:y1, src][:, None]


def fill_holes(s):
    """Make the transparent hole inside a closed frame opaque dark panel."""
    s = s.copy()
    al = s[..., 3]
    low = al < 0.5
    lab = label(low)
    border = np.unique(np.concatenate(
        [lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    outside = np.isin(lab, border) & low
    F = ~dilate(outside, 2)
    s[..., :3][F] = s[..., :3][F] * al[F][:, None] + \
        np.array(FILL, np.float32) * (1.0 - al[F][:, None])
    al[F] = 1.0
    return s


def trim(s):
    ys, xs = np.nonzero(s[..., 3] > 0)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    s = s[y0:y1, x0:x1]
    out = np.zeros((s.shape[0] + 2 * PAD, s.shape[1] + 2 * PAD, 4), np.float32)
    out[PAD:-PAD, PAD:-PAD] = s
    # bleed edge colour into the padding too
    col, kn = bleed(out[..., :3], out[..., 3] > 0, PAD + 1)
    z = out[..., 3] == 0
    out[..., :3][z] = np.where(kn[z][:, None], col[z], 0.0)
    return out


class Sheet:
    def __init__(self, a):
        self.a = a
        self.relabel()

    def relabel(self):
        m = self.a[..., 3] > 0.1
        self.lab = label(m)
        H, W = m.shape
        flat = self.lab.ravel()
        ok = flat < H * W
        ids, inv, cnt = np.unique(flat[ok], return_inverse=True,
                                  return_counts=True)
        yy, xx = np.divmod(np.arange(H * W)[ok], W)
        self.ids = ids
        self.cnt = cnt
        self.cy = np.bincount(inv, yy) / cnt
        self.cx = np.bincount(inv, xx) / cnt
        mnx = np.full(len(ids), W)
        mny = np.full(len(ids), H)
        mxx = np.zeros(len(ids), int)
        mxy = np.zeros(len(ids), int)
        np.minimum.at(mnx, inv, xx)
        np.minimum.at(mny, inv, yy)
        np.maximum.at(mxx, inv, xx)
        np.maximum.at(mxy, inv, yy)
        self.bbox = np.stack([mnx, mny, mxx, mxy], 1)

    def comps_in(self, rect, min_area=30):
        x0, y0, x1, y1 = rect
        sel = (self.cx >= x0) & (self.cx <= x1) & (self.cy >= y0) & (
            self.cy <= y1) & (self.cnt >= min_area)
        return np.nonzero(sel)[0]

    def extract(self, idx):
        """Cut the components with indices idx (into self.ids)."""
        bb = self.bbox[idx]
        M = 16
        H, W = self.lab.shape
        x0 = max(bb[:, 0].min() - M, 0)
        y0 = max(bb[:, 1].min() - M, 0)
        x1 = min(bb[:, 2].max() + M + 1, W)
        y1 = min(bb[:, 3].max() + M + 1, H)
        lab = self.lab[y0:y1, x0:x1]
        crop = self.a[y0:y1, x0:x1].copy()
        sel = np.isin(lab, self.ids[idx])
        other = (lab < H * W) & ~sel
        glow = is_glow(crop[..., :3])
        own = (dilate(sel, 3) & ~other) | (
            dilate(sel, 14) & glow & ~dilate(other, 3))
        crop[..., 3] *= own
        return trim(crop)


def unmix(a, rect, bg_rect, circle=None, use_ink=True):
    """Lift an overlay graphic off a flat dark slot interior."""
    x0, y0, x1, y1 = rect
    crop = a[y0:y1, x0:x1, :3]
    bx0, by0, bx1, by1 = bg_rect
    bg = np.median(a[by0:by1, bx0:bx1, :3].reshape(-1, 3), 0)
    d = np.abs(crop - bg).max(-1)
    lighter = (crop - bg).mean(-1) > 0
    core = (d > 0.12) & lighter
    if circle is not None:
        cx, cy, rad = circle
        yy, xx = np.mgrid[y0:y1, x0:x1]
        dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        inside = np.clip(rad - dist, 0.0, 1.0)
        core &= inside > 0
    else:
        inside = np.ones(d.shape, np.float32)
    # keep only sizeable core blobs (drop noise specks)
    lab = label(core)
    ids, cnt = np.unique(lab[core], return_counts=True)
    core = np.isin(lab, ids[cnt >= 20]) & core
    # lighter-than-panel edge pixels: two-colour unmix against the nearest
    # solid colour, C = a*F + (1-a)*bg, in a 1px ring around the core
    F, kn = bleed(crop, core, 4)
    fb = F - bg
    al = ((crop - bg) * fb).sum(-1) / np.maximum((fb * fb).sum(-1), 1e-4)
    al = np.clip(al, 0.0, 1.0) * (kn & dilate(core, 1) & lighter)
    rgb = F.copy()
    # darker-than-panel pixels (outline, keyhole) near or enclosed by the
    # core: unmix against near-black ink
    nc = ~core
    lab = label(nc)
    edge_ids = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0],
                                         lab[:, -1]]))
    holes = nc & ~np.isin(lab, edge_ids)
    ink = np.array([0.012, 0.012, 0.014], np.float32)
    dark = (dilate(core, 2) | holes) & ~core & ~lighter & use_ink
    da = np.clip((bg - crop).mean(-1) / np.maximum((bg - ink).mean(), 1e-3),
                 0.0, 1.0)
    al[dark] = da[dark]
    rgb[dark] = ink
    al[core] = 1.0
    rgb[core] = crop[core]
    al[al < 0.08] = 0.0
    al *= inside
    out = np.dstack([np.clip(rgb, 0, 1), al]).astype(np.float32)
    return trim(out)


def marker(a, rect):
    """Re-cut the white compass triangle with a clean synthetic outline."""
    x0, y0, x1, y1 = rect
    crop = a[y0:y1, x0:x1, :3]
    w = np.clip((crop.min(-1) - 0.45) / 0.35, 0.0, 1.0)
    lab = label(w > 0.5)
    ids, cnt = np.unique(lab[w > 0.5], return_counts=True)
    keep = dilate(lab == ids[np.argmax(cnt)], 1)
    w = w * keep
    def grow(x):
        n = x.copy()
        for dy, dx in N4:
            n = np.maximum(n, shift(x, dy, dx, 0))
        return n
    o1 = grow(w)
    o = np.maximum(np.maximum(o1, 0.5 * grow(o1)), w)  # ~1.5px outline
    k = np.where(o > 0, w / np.maximum(o, 1e-6), 0)[..., None]
    dark = np.array([0.07, 0.065, 0.06], np.float32)
    rgb = crop * k + dark * (1 - k)
    return trim(np.dstack([rgb, o]).astype(np.float32))


# ----------------------------------------------------------------------------
# 9-slice insets
# ----------------------------------------------------------------------------


def auto_slice(s, tol=0.04):
    pm = np.dstack([s[..., :3] * s[..., 3:4], s[..., 3:4]])

    def axis(lines):
        n = lines.shape[0]
        c = n // 2
        d = np.abs(lines - lines[c]).mean(axis=tuple(range(1, lines.ndim)))
        lo = c
        while lo - 1 >= 0 and d[lo - 1] < tol:
            lo -= 1
        hi = c
        while hi + 1 < n and d[hi + 1] < tol:
            hi += 1
        if hi - lo < 4:  # no uniform run: keep a 2px centre strip
            lo, hi = c - 2, c + 1
        return lo + 1, n - hi

    left, right = axis(np.transpose(pm, (1, 0, 2)))
    top, bottom = axis(pm)
    return [int(left), int(top), int(right), int(bottom)]


def nine_slice(img, ins, W, H):
    h, w = img.shape[:2]
    L, T, R, B = ins

    def mapping(n_out, n, lo, hi):
        o = np.arange(n_out)
        mid = (o - lo + 0.5) * (n - lo - hi) / max(n_out - lo - hi, 1) + lo
        src = np.where(o < lo, o, np.where(o >= n_out - hi, n - (n_out - o),
                                           np.floor(mid)))
        return np.clip(src, 0, n - 1).astype(int)

    return img[mapping(H, h, T, B)][:, mapping(W, w, L, R)]


# ----------------------------------------------------------------------------
# tiny 5x7 bitmap font for labels
# ----------------------------------------------------------------------------

GLYPHS = {
    "A": "01110 10001 10001 11111 10001 10001 10001",
    "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01110 10001 10000 10000 10000 10001 01110",
    "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111",
    "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01110 10001 10000 10111 10001 10001 01111",
    "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "01110 00100 00100 00100 00100 00100 01110",
    "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001",
    "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001",
    "N": "10001 10001 11001 10101 10011 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110",
    "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101",
    "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110",
    "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110",
    "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 10101 01010",
    "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100",
    "Z": "11111 00001 00010 00100 01000 10000 11111",
    "0": "01110 10001 10011 10101 11001 10001 01110",
    "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111",
    "3": "11111 00010 00100 00010 00001 10001 01110",
    "4": "00010 00110 01010 10010 11111 00010 00010",
    "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110",
    "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110",
    "9": "01110 10001 10001 01111 00001 00010 01100",
    "_": "00000 00000 00000 00000 00000 00000 11111",
    "-": "00000 00000 00000 11111 00000 00000 00000",
    ".": "00000 00000 00000 00000 00000 01100 01100",
    ",": "00000 00000 00000 00000 01100 00100 01000",
    "[": "01110 01000 01000 01000 01000 01000 01110",
    "]": "01110 00010 00010 00010 00010 00010 01110",
    " ": "00000 00000 00000 00000 00000 00000 00000",
}
GLYPHS = {k: np.array([[c == "1" for c in row] for row in v.split()])
          for k, v in GLYPHS.items()}


def text_size(t, sc):
    return len(t) * 6 * sc, 7 * sc


def draw_text(canvas, x, y, t, color, sc=2):
    for i, ch in enumerate(t.upper()):
        g = GLYPHS.get(ch, GLYPHS[" "])
        g = np.repeat(np.repeat(g, sc, 0), sc, 1)
        gx = x + i * 6 * sc
        sub = canvas[y:y + g.shape[0], gx:gx + g.shape[1]]
        if sub.shape[:2] != g.shape:
            continue
        sub[g] = color


def over(canvas, img, x, y):
    h, w = img.shape[:2]
    sub = canvas[y:y + h, x:x + w]
    a = img[..., 3:4]
    sub[...] = img[..., :3] * a + sub * (1 - a)


def pack(items, max_w, gap=14):
    """items: list of (w, h). Shelf pack; returns positions and canvas size."""
    pos, x, y, row_h, W = [], gap, gap, 0, 0
    for w, h in items:
        if x + w + gap > max_w and x > gap:
            x, y, row_h = gap, y + row_h + gap, 0
        pos.append((x, y))
        x += w + gap
        row_h = max(row_h, h)
        W = max(W, x)
    return pos, W, y + row_h + gap


def contact(sprites, bg, fg, path):
    sc = 2
    cells = []
    for name, s in sprites:
        lab = "%s %dx%d" % (name, s.shape[1], s.shape[0])
        tw, th = text_size(lab, sc)
        cells.append((max(s.shape[1], tw), s.shape[0] + th + 6))
    pos, W, H = pack(cells, 2400)
    canvas = np.empty((H, W, 3), np.float32)
    canvas[:] = bg
    for (name, s), (x, y) in zip(sprites, pos):
        over(canvas, s, x, y)
        draw_text(canvas, x, y + s.shape[0] + 4,
                  "%s %dx%d" % (name, s.shape[1], s.shape[0]), fg, sc)
    save(canvas, path)


def slice_test(sprites, manifest, path):
    sc = 2
    tiles = []
    for name, s in sprites:
        ins = manifest[name]["slice"]
        if ins is None:
            continue
        h, w = s.shape[:2]
        big = nine_slice(s, ins, 3 * w, 2 * h)
        tw = 3 * w * 2 + 3 * 8 + w
        tile = np.empty((2 * h + 7 * sc + 8, tw, 3), np.float32)
        tile[:] = (0.5, 0.5, 0.5)
        draw_text(tile, 2, 2, "%s slice %s" % (name, ins), (1, 1, 1), sc)
        y = 7 * sc + 6
        dark = np.empty((2 * h, 3 * w, 3), np.float32)
        dark[:] = (0.1, 0.1, 0.11)
        light = np.empty_like(dark)
        light[:] = (0.93, 0.93, 0.9)
        over(dark, big, 0, 0)
        over(light, big, 0, 0)
        tile[y:y + 2 * h, 0:3 * w] = dark
        tile[y:y + 2 * h, 3 * w + 8:6 * w + 8] = light
        over(tile, s, 6 * w + 16, y)
        tiles.append(tile)
    pos, W, H = pack([(t.shape[1], t.shape[0]) for t in tiles], 3000)
    canvas = np.empty((H, W, 3), np.float32)
    canvas[:] = (0.3, 0.3, 0.3)
    for t, (x, y) in zip(tiles, pos):
        canvas[y:y + t.shape[0], x:x + t.shape[1]] = t
    save(canvas, path)


# ----------------------------------------------------------------------------
# sprite specs (sheet pixel coordinates, origin top-left)
# ----------------------------------------------------------------------------

ICON_NAMES = """backpack hammer chest coin_bag scroll group star gear
map compass help swap add_friend trophy calendar gift
heart lightning meat star_gold coin gem shield crossed_swords
axe pickaxe stone_hammer bow spear sword campfire anvil
x plus minus check lock unlock search more
up down left right back refresh expand collapse
sound_on sound_off music bell warning info skull hourglass
exit waypoint eye hand run storm mountain tower""".split()
ICON_COL_BOUNDS = [225, 398, 575, 750, 927, 1110, 1295]
ICON_ROW_BOUNDS = [137, 271, 405, 538, 662, 779, 896]

BUTTON_NAMES = ["backpack", "tools", "chest", "gift", "scroll", "group",
                "star", "gear", "map", "help", "swap", "add_friend", "check",
                "x", "back", "sound_on"]
BUTTON_X = [(19, 198), (209, 384), (396, 574), (582, 761), (772, 951),
            (961, 1140), (1150, 1328), (1339, 1515)]
BUTTON_Y = [(499, 660), (671, 830)]

# Each entry: name, sheet, pick rect (components whose centroid falls inside),
# slice mode ("auto" | None | explicit list), post op.
W_SPECS = [
    ("frame_slot", (68, 508, 215, 648), "auto", None),
    ("frame_slot_selected", (253, 509, 400, 650), "auto", None),
    ("frame_panel_wide", (565, 663, 982, 767), "auto", None),
    ("frame_panel_medium", (465, 776, 817, 881), "auto", None),
    ("frame_badge", (1146, 542, 1332, 627), "auto", None),
    ("frame_compass", (38, 895, 763, 976), "auto", None),
    ("frame_prompt", (1191, 875, 1497, 988), "auto", None),
    ("stat_bar_empty", (74, 21, 499, 99), "auto", None),
    # centred artwork: scale uniformly, never 9-slice
    ("slot_lock_full", (437, 510, 585, 650), None, None),
    ("slot_cooldown_full", (617, 510, 767, 652), None, None),
    ("slot_broken", (799, 510, 949, 651), None, None),
]
F_SPECS = [
    ("frame_bar", (541, 71, 961, 177), "auto", "fill"),
    ("frame_panel_large", (975, 38, 1308, 211), "auto", "fill"),
    ("frame_round", (1322, 24, 1517, 220), None, "fill"),
    ("frame_square_hollow", (20, 58, 152, 188), "auto", None),
    ("frame_selected_hollow", (158, 53, 318, 196), "auto", None),
    ("frame_wide_hollow", (324, 61, 532, 187), "auto", None),
    ("frame_bar_hollow", (541, 71, 961, 177), "auto", None),
    ("frame_panel_large_hollow", (975, 38, 1308, 211), "auto", None),
    ("frame_round_hollow", (1322, 24, 1517, 220), None, None),
    ("nine_corner_tl", (41, 236, 144, 347), None, None),
    ("nine_corner_tr", (201, 237, 303, 347), None, None),
    ("nine_corner_bl", (357, 242, 465, 355), None, None),
    ("nine_corner_br", (529, 243, 639, 355), None, None),
    ("nine_edge_top", (715, 241, 1140, 292), None, None),
    ("nine_edge_bottom", (715, 305, 1140, 357), None, None),
    ("nine_edge_left", (1199, 225, 1248, 373), None, None),
    ("nine_edge_right", (1440, 225, 1490, 373), None, None),
    ("fill_red", (29, 420, 192, 456), "auto", None),
    ("fill_green", (210, 420, 373, 456), "auto", None),
    ("fill_yellow", (391, 420, 554, 457), "auto", None),
    # stripes have no uniform run; slice just inside the rounded caps
    ("fill_orange_striped", (572, 420, 743, 458), [21, 14, 21, 14], None),
    ("fill_blue", (759, 421, 922, 457), "auto", None),
    ("fill_track", (935, 420, 1142, 461), "auto", None),
    ("panel_dark", (1162, 395, 1380, 486), "auto", None),
    ("panel_dark_small", (1402, 394, 1503, 486), "auto", None),
    ("pill_dark", (1149, 867, 1340, 972), "auto", None),
    ("keycap", (911, 848, 1071, 991), "auto", None),
    ("icon_crown", (137, 857, 277, 979), None, None),
    ("icon_lock_silver", (345, 846, 453, 983), None, None),
    ("icon_red_dot", (544, 883, 620, 959), None, None),
    ("icon_spinner", (704, 850, 832, 986), None, None),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    print("[slice_ui] cleaning sheets")
    W = clean_sheet(load(os.path.join(REF, "sheet_hud_widgets.png")))
    I = clean_sheet(load(os.path.join(REF, "sheet_icons.png")))
    F = clean_sheet(load(os.path.join(REF, "sheet_frames.png")))

    sprites = {}
    slices = {}

    # --- overlays / synthetic pieces cut before any in-painting -----------
    sprites["compass_marker"] = marker(W, (378, 892, 424, 929))
    slices["compass_marker"] = None
    sprites["slot_lock"] = unmix(W, (478, 544, 547, 621), (458, 535, 475, 625))
    slices["slot_lock"] = None
    sprites["slot_cooldown"] = unmix(W, (636, 527, 747, 638),
                                     (636, 600, 652, 630), (691.5, 582.5, 52),
                                     use_ink=False)
    slices["slot_cooldown"] = None

    # --- in-paint text / icons / markers out of frames --------------------
    op_cols(W, 104, 691, 884, 986, 130)     # compass: ticks + marker -> plain
    op_cols(W, 103, 152, 37, 84, 153)       # stat bar: remove heart icon
    op_cols(W, 1190, 1285, 560, 611, 1288)  # badge: remove "LV. 12"
    op_cols(W, 1209, 1306, 890, 974, 1330)  # prompt: remove key socket
    Ws, Is, Fs = Sheet(W), Sheet(I), Sheet(F)

    order = ["compass_marker", "slot_lock", "slot_cooldown"]

    def add(name, sheet, rect, sl, post):
        idx = sheet.comps_in(rect)
        assert len(idx) > 0, name
        s = sheet.extract(idx)
        if post == "fill":
            s = fill_holes(s)
        sprites[name] = s
        slices[name] = auto_slice(s) if sl == "auto" else sl
        order.append(name)

    for name, rect, sl, post in W_SPECS:
        add(name, Ws, rect, sl, post)
    for name, rect, sl, post in F_SPECS:
        add(name, Fs, rect, sl, post)

    # icons: assign every component to a grid cell by centroid
    col = np.searchsorted(ICON_COL_BOUNDS, Is.cx)
    row = np.searchsorted(ICON_ROW_BOUNDS, Is.cy)
    for k, nm in enumerate(ICON_NAMES):
        r, c = divmod(k, 8)
        idx = np.nonzero((row == r) & (col == c) & (Is.cnt >= 30))[0]
        assert len(idx) > 0, nm
        name = "icon_" + nm
        sprites[name] = Is.extract(idx)
        slices[name] = None
        order.append(name)

    for k, nm in enumerate(BUTTON_NAMES):
        r, c = divmod(k, 8)
        (x0, x1), (y0, y1) = BUTTON_X[c], BUTTON_Y[r]
        add("button_" + nm, Fs, (x0, y0, x1, y1), None, None)

    # --- write -----------------------------------------------------------
    old_manifest = os.path.join(OUT, "manifest.json")
    stale = set()
    if os.path.exists(old_manifest):
        with open(old_manifest) as fh:
            stale = {v["file"] for v in json.load(fh).values()}
    manifest = {}
    for name in order:
        s = sprites[name]
        save(s, os.path.join(OUT, name + ".png"))
        manifest[name] = {"file": name + ".png", "w": int(s.shape[1]),
                          "h": int(s.shape[0]), "slice": slices[name]}
        stale.discard(name + ".png")
    for f in sorted(stale):  # files this script wrote on an earlier run only
        p = os.path.join(OUT, f)
        if os.path.exists(p):
            os.remove(p)
    with open(old_manifest, "w") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")

    lst = [(n, sprites[n]) for n in order]
    contact(lst, (0.11, 0.11, 0.12), (0.85, 0.85, 0.85),
            os.path.join(OUT, "_contact_dark.png"))
    contact(lst, (0.93, 0.93, 0.90), (0.1, 0.1, 0.1),
            os.path.join(OUT, "_contact_light.png"))
    slice_test(lst, manifest, os.path.join(OUT, "_slice_test.png"))
    print("[slice_ui] wrote %d sprites to %s" % (len(order), OUT))
    for n in order:
        if manifest[n]["slice"] is not None:
            print("  %-26s %4dx%-4d slice %s" % (
                n, manifest[n]["w"], manifest[n]["h"], manifest[n]["slice"]))


main()
