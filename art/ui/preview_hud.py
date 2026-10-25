"""Composite a preview of the in-world HUD from the shared layout and sprites.

Reads src/shared/UI/HudLayout.json (the same file HudController builds from) and
draws the sliced sprites in art/ui/sprites at their layout positions onto the
1672x941 reference canvas, over the master screenshot blurred and darkened 60%
(or a plain gradient), then writes art/ui/hud_preview.png. Text uses the fonts
Roblox ships (FredokaOne, Montserrat for Gotham) when a local Roblox install has
them, else Windows fonts. It mirrors HudController and the Hud/ widgets: same
rects, same 9-slice corner scale (HudModel.SliceScale), same compass projection.

Run through the Blender wrapper (needs Blender's numpy, bpy and blf):

    art/blender/run.sh art/ui/preview_hud.py art/ui/hud_preview.png

Environment: HUD_BACKGROUND=gradient for a plain background; HUD_COMPARE=<png>
also writes the master and the preview stacked for side-by-side review.
"""
import glob
import json
import math
import os
import sys
from pathlib import Path

import blf
import bpy
import imbuf
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LAYOUT = ROOT / "src" / "shared" / "UI" / "HudLayout.json"
SPRITES = HERE / "sprites"
MANIFEST = SPRITES / "manifest.json"
MASTER = ROOT / "art" / "reference" / "ui" / "hud_master.png"
OUTPUT = HERE / "hud_preview.png"

layout = json.loads(LAYOUT.read_text(encoding="utf-8"))
manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.is_file() else {}
W = layout["reference"]["width"]
H = layout["reference"]["height"]
COLORS = layout["colors"]
FONTS = layout["fonts"]


def hex_color(key, alpha=1.0):
    value = COLORS.get(key, key)
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (alpha,)


# Image IO -------------------------------------------------------------------

def load_png(path):
    image = bpy.data.images.load(str(path), check_existing=True)
    w, h = image.size
    pixels = np.empty(w * h * 4, np.float32)
    image.pixels.foreach_get(pixels)
    return pixels.reshape(h, w, 4)[::-1].copy()  # top-down rows


def save_png(path, rgba):
    h, w = rgba.shape[:2]
    image = bpy.data.images.new(Path(path).stem, w, h, alpha=True)
    image.pixels.foreach_set(np.ascontiguousarray(rgba[::-1], dtype=np.float32).ravel())
    image.filepath_raw = str(path)
    image.file_format = "PNG"
    image.save()
    bpy.data.images.remove(image)


_sprite_cache = {}


def sprite(name):
    """Premultiplied RGBA of a sprite, or None when it is not sliced yet."""
    if name not in _sprite_cache:
        path = SPRITES / f"{name}.png"
        if path.is_file():
            pixels = load_png(path)
            pixels[..., :3] *= pixels[..., 3:4]
            _sprite_cache[name] = pixels
        else:
            _sprite_cache[name] = None
    return _sprite_cache[name]


def resize(img, w, h):
    w, h = int(round(w)), int(round(h))
    if w <= 0 or h <= 0:
        return None
    # Box-halve large reductions first so small icons do not alias.
    while img.shape[0] >= 2 * h and img.shape[1] >= 2 * w and img.shape[0] >= 2 and img.shape[1] >= 2:
        hh, ww = img.shape[0] // 2 * 2, img.shape[1] // 2 * 2
        img = img[:hh, :ww].reshape(hh // 2, 2, ww // 2, 2, 4).mean(axis=(1, 3))
    sh, sw = img.shape[:2]
    ys = np.clip((np.arange(h) + 0.5) * sh / h - 0.5, 0, sh - 1)
    xs = np.clip((np.arange(w) + 0.5) * sw / w - 0.5, 0, sw - 1)
    y0, x0 = np.floor(ys).astype(int), np.floor(xs).astype(int)
    y1, x1 = np.minimum(y0 + 1, sh - 1), np.minimum(x0 + 1, sw - 1)
    fy, fx = (ys - y0)[:, None, None], (xs - x0)[None, :, None]
    top = img[y0][:, x0] * (1 - fx) + img[y0][:, x1] * fx
    bottom = img[y1][:, x0] * (1 - fx) + img[y1][:, x1] * fx
    return top * (1 - fy) + bottom * fy


# Canvas -----------------------------------------------------------------------

def blur(img, radius, passes=3):
    out = img
    for _ in range(passes):
        for axis in (0, 1):
            pad = [(0, 0)] * 3
            pad[axis] = (radius + 1, radius)
            padded = np.pad(out, pad, mode="edge")
            cumulative = np.cumsum(padded, axis=axis)
            size = out.shape[axis]
            hi = np.take(cumulative, np.arange(2 * radius + 1, 2 * radius + 1 + size), axis=axis)
            lo = np.take(cumulative, np.arange(0, size), axis=axis)
            out = (hi - lo) / (2 * radius + 1)
    return out


def background():
    if os.environ.get("HUD_BACKGROUND") != "gradient" and MASTER.is_file():
        master = load_png(MASTER)
        master = resize(master, W, H) if master.shape[:2] != (H, W) else master
        out = blur(master, 6) * 0.4
        out[..., 3] = 1
        return out
    t = np.linspace(0, 1, H)[:, None, None]
    out = np.zeros((H, W, 4), np.float32)
    out[..., :3] = (1 - t) * np.array([0.22, 0.34, 0.42]) + t * np.array([0.16, 0.2, 0.12])
    out[..., 3] = 1
    return out


canvas = None


def blit(img, x, y):
    """Composite premultiplied `img` with its top-left at (x, y)."""
    if img is None:
        return
    x, y = int(round(x)), int(round(y))
    h, w = img.shape[:2]
    cx0, cy0 = max(0, x), max(0, y)
    cx1, cy1 = min(W, x + w), min(H, y + h)
    if cx1 <= cx0 or cy1 <= cy0:
        return
    src = img[cy0 - y:cy1 - y, cx0 - x:cx1 - x]
    dst = canvas[cy0:cy1, cx0:cx1]
    dst[..., :3] = src[..., :3] + dst[..., :3] * (1 - src[..., 3:4])


def slice_scale(nw, nh, tw, th):
    # HudModel.SliceScale
    if nw <= 0 or nh <= 0:
        return 1
    return min(max(min(tw / nw, th / nh), 0.15), 1)


def fallback_rect(name, x, y, w, h):
    color = hex_color("fallbackFill", 0.9)
    patch = np.zeros((max(1, int(h)), max(1, int(w)), 4), np.float32)
    patch[...] = (color[0] * color[3], color[1] * color[3], color[2] * color[3], color[3])
    blit(patch, x, y)


def draw_sprite(name, x, y, w, h, fit=None, scale_override=None, tint=None):
    """Draws a sprite like Widgets.Sprite: 9-slice when the manifest slices it,
    stretched for fills, fitted (aspect kept, centred) for everything else.
    `tint` multiplies the colour like ImageColor3."""
    img = sprite(name)
    if img is None:
        fallback_rect(name, x, y, w, h)
        return
    if tint:
        img = img.copy()
        img[..., :3] *= np.array(hex_color(tint)[:3], np.float32)
    nh, nw = img.shape[:2]
    entry = manifest.get(name) or {}
    insets = entry.get("slice")
    if insets:
        s = scale_override or slice_scale(nw, nh, w, h)
        l, t, r, b = insets
        dl, dt, dr, db = l * s, t * s, r * s, b * s
        xs_src = [0, l, nw - r, nw]
        ys_src = [0, t, nh - b, nh]
        xs_dst = [0, dl, w - dr, w]
        ys_dst = [0, dt, h - db, h]
        for row in range(3):
            for col in range(3):
                piece = img[ys_src[row]:ys_src[row + 1], xs_src[col]:xs_src[col + 1]]
                pw = round(x + xs_dst[col + 1]) - round(x + xs_dst[col])
                ph = round(y + ys_dst[row + 1]) - round(y + ys_dst[row])
                if piece.size and pw > 0 and ph > 0:
                    blit(resize(piece, pw, ph), x + xs_dst[col], y + ys_dst[row])
        return
    if name.startswith("fill_") and not fit:
        blit(resize(img, w, h), x, y)
        return
    k = min(w / nw, h / nh)
    fw, fh = nw * k, nh * k
    blit(resize(img, fw, fh), x + (w - fw) / 2, y + (h - fh) / 2)


def draw_rect(x, y, w, h, color):
    patch = np.zeros((max(1, int(round(h))), max(1, int(round(w))), 4), np.float32)
    patch[...] = (color[0] * color[3], color[1] * color[3], color[2] * color[3], color[3])
    blit(patch, x, y)


def _rrect_sdf(w, h, radius, ox, oy):
    # Signed distance to a rounded box of size (w, h), sampled on a pixel grid
    # whose origin is offset by the sub-pixel position (ox, oy).
    gw, gh = int(math.ceil(w + ox)) + 2, int(math.ceil(h + oy)) + 2
    yy, xx = np.mgrid[0:gh, 0:gw] + 0.5
    px, py = xx - ox - w / 2, yy - oy - h / 2
    radius = min(radius, w / 2, h / 2)
    qx, qy = np.abs(px) - (w / 2 - radius), np.abs(py) - (h / 2 - radius)
    outside = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2)
    inside = np.minimum(np.maximum(qx, qy), 0)
    return outside + inside - radius, yy - oy


def _blit_mask(x, y, alpha, rgb):
    patch = np.zeros(alpha.shape + (4,), np.float32)
    patch[..., :3] = rgb * alpha[..., None]
    patch[..., 3] = alpha
    blit(patch, math.floor(x), math.floor(y))


def rrect(x, y, w, h, radius, rgb, alpha, gradient=None):
    """A filled rounded rectangle; gradient(t) gives an RGB row per t in 0..1."""
    if w <= 0 or h <= 0:
        return
    ox, oy = x - math.floor(x), y - math.floor(y)
    d, rows = _rrect_sdf(w, h, radius, ox, oy)
    mask = np.clip(0.5 - d, 0, 1) * alpha
    if gradient is not None:
        t = np.clip(rows[:, 0] / h, 0, 1)
        colors = np.broadcast_to(gradient(t)[:, None, :], mask.shape + (3,))
    else:
        colors = np.broadcast_to(np.asarray(rgb, np.float32), mask.shape + (3,))
    patch = np.zeros(mask.shape + (4,), np.float32)
    patch[..., :3] = colors * mask[..., None]
    patch[..., 3] = mask
    blit(patch, math.floor(x), math.floor(y))


def stroke_rrect(x, y, w, h, radius, thickness, rgb, alpha):
    """A rounded-rectangle outline centred on the edge (Roblox UIStroke)."""
    pad = thickness
    ox, oy = x - math.floor(x) + pad, y - math.floor(y) + pad
    d, _ = _rrect_sdf(w, h, radius, ox, oy)
    mask = np.clip(thickness / 2 - np.abs(d) + 0.5, 0, 1) * alpha
    _blit_mask(math.floor(x) - pad, math.floor(y) - pad, mask, np.asarray(rgb, np.float32))


def draw_triangle(cx, cy, w, h, rgb):
    """An upward triangle with a dark outline (the compass end markers)."""
    size_w, size_h = int(math.ceil(w)) + 4, int(math.ceil(h)) + 4
    yy, xx = np.mgrid[0:size_h, 0:size_w] + 0.5
    x0, y0 = size_w / 2, (size_h - h) / 2
    # Distance inside the triangle (positive inside): min over the three edges.
    def edge(ax, ay, bx, by):
        nx, ny = by - ay, ax - bx
        length = math.hypot(nx, ny)
        return ((xx - ax) * nx + (yy - ay) * ny) / length
    apex, left, right = (x0, y0), (x0 - w / 2, y0 + h), (x0 + w / 2, y0 + h)
    inside = np.minimum(np.minimum(edge(*apex, *left), edge(*left, *right)), edge(*right, *apex))
    inside = -inside if inside[int(y0 + h * 0.7), int(x0)] < 0 else inside
    outline = np.clip(inside + 1.0, 0, 1)
    fill = np.clip(inside - 0.6, 0, 1)
    patch = np.zeros((size_h, size_w, 4), np.float32)
    dark = np.array(hex_color("outline")[:3])
    color = dark[None, None, :] * (outline - fill)[..., None] + np.asarray(rgb)[None, None, :] * fill[..., None]
    patch[..., :3] = color
    patch[..., 3] = outline
    blit(patch, cx - size_w / 2, cy - size_h / 2)


def draw_diamond(cx, cy, size, thickness, rgb):
    """A square outline rotated 45 degrees (UIStroke on a Rotation=45 Frame)."""
    n = int(math.ceil(size)) + 4
    yy, xx = np.mgrid[0:n, 0:n] + 0.5
    d = (np.abs(xx - n / 2) + np.abs(yy - n / 2)) / math.sqrt(2) - size / (2 * math.sqrt(2))
    mask = np.clip(thickness / 2 - np.abs(d) + 0.5, 0, 1)
    patch = np.zeros((n, n, 4), np.float32)
    patch[..., :3] = np.asarray(rgb)[None, None, :] * mask[..., None]
    patch[..., 3] = mask
    blit(patch, cx - n / 2, cy - n / 2)


def draw_pin(x, y, w, h, rgb):
    """Widgets.Pin: a round head, a pointed foot and a dark centre dot."""
    head = w
    foot = w * 0.5
    # Foot: a square rotated 45 degrees below the head's centre.
    size = int(math.ceil(max(w, h))) + 2
    yy, xx = np.mgrid[0:size, 0:size] + 0.5
    fx, fy = w / 2, h * 0.58
    diamond = np.clip(foot * 0.72 - (np.abs(xx - fx) + np.abs(yy - fy)) + 0.5, 0, 1)
    circle = np.clip(head / 2 - np.sqrt((xx - w / 2) ** 2 + (yy - head / 2) ** 2) + 0.5, 0, 1)
    dot = np.clip(head * 0.18 - np.sqrt((xx - w / 2) ** 2 + (yy - head / 2) ** 2) + 0.5, 0, 1)
    alpha = np.maximum(diamond, circle)
    patch = np.zeros((size, size, 4), np.float32)
    dark = np.array(hex_color("outline")[:3])
    color = np.asarray(rgb)[None, None, :] * (1 - dot[..., None]) + dark[None, None, :] * dot[..., None]
    patch[..., :3] = color * alpha[..., None]
    patch[..., 3] = alpha
    blit(patch, x, y)


def draw_ring(cx, cy, diameter, thickness, color, filled=False):
    size = int(math.ceil(diameter)) + 2
    yy, xx = np.mgrid[0:size, 0:size] + 0.5
    d = np.sqrt((xx - size / 2) ** 2 + (yy - size / 2) ** 2)
    radius = diameter / 2
    if filled:
        alpha = np.clip(radius - d + 0.5, 0, 1)
    else:
        alpha = np.clip(thickness / 2 - np.abs(d - (radius - thickness / 2)) + 0.5, 0, 1)
    alpha *= color[3]
    patch = np.zeros((size, size, 4), np.float32)
    for i in range(3):
        patch[..., i] = color[i] * alpha
    patch[..., 3] = alpha
    blit(patch, cx - size / 2, cy - size / 2)


def draw_headshot(x, y, w, h, seed):
    # Stand-in for Players:GetUserThumbnailAsync headshots, clipped to its square.
    tones = [(0.86, 0.66, 0.5), (0.78, 0.55, 0.4), (0.55, 0.38, 0.27)]
    w, h = int(round(w)), int(round(h))
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    patch = np.zeros((h, w, 4), np.float32)
    patch[...] = (0.16, 0.2, 0.26, 1)
    layers = [
        ((0.25, 0.3, 0.36), (w / 2, h * 1.05, w * 0.48)),
        (tones[seed % len(tones)], (w / 2, h * 0.46, w * 0.28)),
    ]
    for color, (cx, cy, radius) in layers:
        alpha = np.clip(radius - np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) + 0.5, 0, 1)[..., None]
        patch[..., :3] = np.array(color) * alpha + patch[..., :3] * (1 - alpha)
    blit(patch, x, y)


# Text (drawn last with blf into an ImBuf) ----------------------------------------

texts = []


def text(entry, value, x, y, w, h, align="left", size=None, color=None):
    texts.append({
        "text": value, "x": x, "y": y, "w": w, "h": h, "align": align,
        "font": entry.get("font", "body"), "size": size or entry.get("textSize", 14),
        "color": color or entry.get("color", "text"),
    })


def font_file(roblox_font):
    roblox = os.path.expandvars(r"%LOCALAPPDATA%\Roblox\Versions\*\content\fonts")
    wanted = {
        "FredokaOne": ["FredokaOne-Regular.ttf"],
        "GothamBlack": ["Montserrat-Black.ttf"],
        "GothamBold": ["Montserrat-Bold.ttf"],
        "GothamMedium": ["Montserrat-Medium.ttf"],
        "Gotham": ["Montserrat-Regular.ttf"],
    }.get(roblox_font, ["Montserrat-Medium.ttf"])
    for name in wanted:
        found = sorted(glob.glob(os.path.join(roblox, name)))
        if found:
            return found[-1]
    windows = {
        "FredokaOne": "seguibl.ttf", "GothamBlack": "seguibl.ttf", "GothamBold": "segoeuib.ttf",
    }.get(roblox_font, "segoeui.ttf")
    return os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", windows)


_font_ids = {}


def font_id(key):
    path = font_file(FONTS.get(key, key))
    if path not in _font_ids:
        _font_ids[path] = blf.load(path)
    return _font_ids[path]


def draw_texts(png_in, png_out):
    buffer = imbuf.load(str(png_in))
    for item in texts:
        fid = font_id(item["font"])
        with blf.bind_imbuf(fid, buffer):
            blf.size(fid, item["size"])
            width, _ = blf.dimensions(fid, item["text"])
            if item["align"] == "right":
                tx = item["x"] + item["w"] - width
            elif item["align"] == "center":
                tx = item["x"] + (item["w"] - width) / 2
            else:
                tx = item["x"]
            # Roblox centres a line box vertically; cap height is ~0.7 em.
            baseline = item["y"] + item["h"] / 2 + item["size"] * 0.36
            by = H - baseline
            blf.color(fid, 0, 0, 0, 0.35)
            blf.position(fid, tx + 1, by - 1, 0)
            blf.draw_buffer(fid, item["text"])
            blf.color(fid, *hex_color(item["color"]))
            blf.position(fid, tx, by, 0)
            blf.draw_buffer(fid, item["text"])
    imbuf.write(buffer, filepath=str(png_out))


# Widgets (mirrors src/client/Hud) ---------------------------------------------

def place(entry, size=None):
    w, h = size or entry["size"]
    sx, ox, sy, oy = entry["pos"]
    ax, ay = entry["anchor"]
    return sx * W + ox - ax * w, sy * H + oy - ay * h, w, h


def draw_frame(name, x, y, w, h, scale_override=None, outset=None):
    # Widgets.Frame: the sprite is drawn larger so its rails land on the rect.
    l, t, r, b = outset or layout.get("frameOutset", [0, 0, 0, 0])
    draw_sprite(name, x - l, y - t, w + l + r, h + t + b, scale_override=scale_override)


def panel(cfg, x, y, w, h):
    # Widgets.Panel: translucent rounded fill under a rope frame on the rect.
    if cfg.get("fill"):
        inset = cfg.get("fillInset", 3)
        rrect(x + inset, y + inset, w - 2 * inset, h - 2 * inset, 8,
              hex_color(cfg["fill"])[:3], 1 - cfg.get("fillTransparency", 0))
    if cfg.get("frame"):
        draw_frame(cfg["frame"], x, y, w, h, cfg.get("sliceScale"), cfg.get("frameOutset"))


def fill_bar(color_key, x, y, w, h):
    # Widgets.Fill: rounded, with the same three-stop vertical gradient.
    if w < 1:
        return
    base = np.array(hex_color(color_key)[:3])
    top = base + (1 - base) * 0.25
    bottom = base * 0.88

    def gradient(t):
        upper = np.clip(t / 0.45, 0, 1)
        lower = np.clip((t - 0.45) / 0.55, 0, 1)
        first = top[None, :] * (1 - upper[:, None]) + base[None, :] * upper[:, None]
        return np.where((t < 0.45)[:, None], first, base[None, :] * (1 - lower[:, None]) + bottom[None, :] * lower[:, None])

    rrect(x, y, w, h, h / 2, base, 1, gradient=gradient)


def bar(cfg, bx, by, fraction):
    # Widgets.Bar
    rx, ry, rw, rh = cfg["rect"]
    x, y = bx + rx, by + ry
    inset = cfg.get("inset", 0)
    if cfg.get("track"):
        draw_sprite(cfg["track"], x, y, rw, rh)
    elif cfg.get("trackColor"):
        rrect(x, y, rw, rh, rh / 2, hex_color(cfg["trackColor"])[:3], 1)
    max_width = cfg.get("maxWidth", rw - 2 * inset)
    fill_bar(cfg["fillColor"], x + cfg.get("insetX", inset), y + inset, max_width * fraction, rh - 2 * inset)


def draw_party(preview):
    cfg = layout["party"]
    x0, y0, _, _ = place(cfg, (cfg["size"][0], cfg["pitch"] * (cfg["maxRows"] - 1) + cfg["size"][1]))
    w, h = cfg["size"]
    for index, member in enumerate(preview["party"][:cfg["maxRows"]]):
        x, y = x0, y0 + index * cfg["pitch"]
        panel(cfg, x, y, w, h)
        px, py, pw, ph = cfg["portrait"]["rect"]
        draw_headshot(x + px, y + py, pw, ph, index)
        stroke_rrect(x + px, y + py, pw, ph, 6, 2, hex_color("outline")[:3], 1)
        nx, ny, nw, nh = cfg["name"]["rect"]
        text(cfg["name"], member["name"], x + nx, y + ny, nw, nh)
        bar(cfg["bar"], x, y, member["health"])


HEADINGS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def angle_delta(a, b):
    d = (b - a) % 360
    return d - 360 if d > 180 else d


def draw_compass(preview):
    cfg = layout["compass"]
    x, y, w, h = place(cfg)
    panel(cfg, x, y, w, h)
    tri = cfg["triangles"]
    for cx, cy in tri["centres"]:
        draw_triangle(x + cx, y + cy, tri["size"][0], tri["size"][1], hex_color(tri["color"])[:3])
    tx, ty, tw, th = cfg["track"]
    centre = tw / 2
    ppd = centre / cfg["halfSpan"]
    heading = preview["heading"]
    for angle in range(0, 360, cfg["minorStep"]):
        offset = angle_delta(heading, angle)
        label = HEADINGS[angle // 45] if angle % 45 == 0 else None
        limit = cfg["halfSpan"] if label else min(cfg.get("minorLimit", cfg["halfSpan"]), cfg["halfSpan"])
        if abs(offset) > limit:
            continue
        mx = x + tx + centre + offset * ppd
        tick = cfg["majorTick"] if label else cfg["minorTick"]
        draw_rect(mx - 1, y + ty + tick["y"], 2, tick["h"], hex_color("body", 0.7))
        if label:
            edge = abs(offset) / cfg["halfSpan"]
            fade = min(max((edge - 0.8) / 0.2, 0), 1)
            letter = cfg["letter"]
            cardinal = label == "N"
            size = letter["cardinalTextSize"] if cardinal else letter["textSize"]
            raise_ = letter["cardinalRaise"] if cardinal else 0
            rgba = hex_color(letter["color"], 1 - fade * 0.8)
            shade = "#%02X%02X%02X" % tuple(int(c * 255 * rgba[3] + 40 * (1 - rgba[3])) for c in rgba[:3])
            texts.append({"text": label, "x": mx - 22, "y": y + ty + letter["y"] - raise_, "w": 44, "h": letter["h"],
                          "align": "center", "font": letter["font"], "size": size, "color": shade})
    mxr, myr, mw, mh = cfg["marker"]["rect"]
    draw_sprite(cfg["marker"]["sprite"], x + mxr, y + myr, mw, mh)
    way = cfg["waypoints"]
    for waypoint in preview["waypoints"]:
        offset = angle_delta(heading, waypoint["bearing"])
        if abs(offset) <= cfg["halfSpan"]:
            size = waypoint.get("size", way["size"])
            cx = x + tx + centre + offset * ppd
            bottom = y + way["y"] + way["size"]
            draw_sprite(waypoint["icon"], cx - size / 2, bottom - size, size, size, tint=way.get("tint"))


def draw_objective(preview):
    cfg = layout["objective"]
    x, y, w, h = place(cfg)
    panel(cfg, x, y, w, h)
    diamond = cfg["diamond"]
    dx, dy, dw, dh = diamond["rect"]
    draw_diamond(x + dx + dw / 2, y + dy + dh / 2, min(dw, dh), diamond["thickness"], hex_color(diamond["color"])[:3])
    fx, fy, fw, fh = cfg["figure"]["rect"]
    draw_sprite(cfg["figure"]["icon"], x + fx, y + fy, fw, fh, tint=cfg["figure"].get("tint"))
    tx, ty, tw, th = cfg["title"]["rect"]
    text(cfg["title"], "FIND EXTRACTION", x + tx, y + ty, tw, th)
    div = cfg["dividers"]
    for dy in div["y"]:
        draw_rect(x + div["x"], y + dy, div["w"], 1, hex_color(div["color"], 1 - div["transparency"]))
    row_h = cfg["rows"]["h"]
    for line, ry in zip(preview["objective"], cfg["rows"]["y"]):
        cy = y + ry + row_h / 2
        draw_ring(x + cfg["check"]["x"] + cfg["check"]["size"] / 2, cy, cfg["check"]["size"], 1.5, hex_color("text"))
        has_distance = "distance" in line
        text_w = cfg["text"]["w"] if has_distance else cfg["progress"]["right"] - cfg["progress"]["w"] - cfg["text"]["x"]
        text(cfg["text"], line["text"], x + cfg["text"]["x"], y + ry, text_w, row_h)
        if has_distance:
            pw, ph = cfg["pin"]["size"]
            draw_pin(x + cfg["pin"]["x"], cy - ph / 2, pw, ph, hex_color(cfg["pin"]["color"])[:3])
            text(cfg["distance"], line["distance"], x + cfg["distance"]["x"], y + ry, cfg["distance"]["w"], row_h)
        pw = cfg["progress"]["w"]
        text(cfg["progress"], line["progress"], x + cfg["progress"]["right"] - pw, y + ry, pw, row_h, align="right")


def draw_event(preview):
    cfg = layout["event"]
    x, y, w, h = place(cfg)
    panel(cfg, x, y, w, h)
    ix, iy, iw, ih = cfg["icon"]["rect"]
    draw_sprite(cfg["icon"]["icon"], x + ix, y + iy, iw, ih)
    event = preview["event"]
    for key, align in (("title", "left"), ("timer", "right"), ("name", "left"), ("description", "left")):
        rx, ry, rw, rh = cfg[key]["rect"]
        text(cfg[key], event[key], x + rx, y + ry, rw, rh, align=align)


def draw_vitals(preview):
    cfg = layout["vitals"]
    x, y, w, h = place(cfg)
    panel(cfg, x, y, w, h)
    for index, row in enumerate(cfg["rows"]):
        top = cfg["rowTop"] + index * cfg["rowPitch"]
        cy = top + cfg["rowHeight"] / 2
        s = cfg["icon"]["size"]
        draw_sprite(row["icon"], x + cfg["icon"]["x"], y + cy - s / 2, s, s)
        text(cfg["label"], row["label"], x + cfg["label"]["x"], y + top, cfg["label"]["w"], cfg["rowHeight"])
        track = cfg["track"]
        fraction, value = preview["vitals"][row["key"]]
        bar({"rect": [track["x"], cy - track["h"] / 2, track["w"], track["h"]], "inset": cfg["fillBar"]["inset"],
             "maxWidth": cfg["fillBar"]["w"], "track": track["sprite"], "fillColor": row["color"]}, x, y, fraction)
        vw = cfg["value"]["w"]
        text(cfg["value"], value, x + cfg["value"]["right"] - vw, y + top, vw, cfg["rowHeight"], align="right")


def draw_selection(cfg, sx, sy, sw, sh):
    # Widgets.SelectionRing: the glowing slot frame over the slot, untinted.
    l, t, r, b = cfg.get("frameOutset") or layout.get("frameOutset", [0, 0, 0, 0])
    draw_sprite(cfg["sprite"], sx - l, sy - t, sw + l + r, sh + t + b, scale_override=cfg.get("sliceScale"))


def draw_bottom(preview):
    cfg = layout["bottom"]
    x, y, w, h = place(cfg)
    badge = cfg["badge"]
    bx, by, bw, bh = badge["rect"]
    draw_sprite(badge["sprite"], x + bx, y + by, bw, bh)
    text(badge, "LV. %d" % preview["level"], x + bx, y + by, bw, bh, align="center")
    xp = cfg["xp"]
    rx, ry, rw, rh = xp["rect"]
    l, t, r, _ = xp["inset"]
    bar({"rect": xp["rect"], "inset": t, "insetX": l, "maxWidth": rw - l - r, "track": xp["track"],
         "fillColor": xp["fillColor"]}, x, y, preview["xp"])
    draw_frame(xp["frame"], x + rx, y + ry, rw, rh, outset=xp.get("frameOutset"))
    hot = cfg["hotbar"]
    sw, sh = hot["slot"]
    number = cfg["slotNumber"]
    for index in range(hot["count"]):
        sx = x + hot["x"] + index * hot["pitch"]
        sy = y + hot["y"]
        draw_frame(hot["frame"], sx, sy, sw, sh, hot.get("sliceScale"), hot.get("frameOutset"))
        if index + 1 == preview["selectedSlot"]:
            draw_selection(cfg["selected"], sx, sy, sw, sh)
        nx, ny, nw, nh = number["rect"]
        text(number, str(index + 1), sx + nx, sy + ny, nw, nh)


def draw_prompt(preview):
    cfg = layout["prompt"]
    x, y = cfg["previewPos"]
    w, h = cfg["size"]
    panel(cfg, x, y, w, h)
    plate = cfg["plate"]
    px, py, pw, ph = plate["rect"]
    rrect(x + px, y + py, pw, ph, 9, hex_color(plate["color"])[:3], 1 - plate["transparency"])
    kx, ky, kw, kh = cfg["keycap"]["rect"]
    top_c, bottom_c = np.array(hex_color("keycap")[:3]), np.array(hex_color("keycapShade")[:3])
    rrect(x + kx, y + ky, kw, kh, 7, top_c, 1,
          gradient=lambda t: top_c[None, :] * (1 - t[:, None]) + bottom_c[None, :] * t[:, None])
    prompt = preview["prompt"]
    text(cfg["keycap"], prompt["key"], x + kx, y + ky, kw, kh, align="center")
    for key in ("title", "subtitle"):
        rx, ry, rw, rh = cfg[key]["rect"]
        text(cfg[key], prompt[key], x + rx, y + ry, rw, rh)


def main():
    global canvas
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    output = Path(argv[0]) if argv else OUTPUT
    canvas = background()
    preview = layout["preview"]
    draw_party(preview)
    draw_compass(preview)
    draw_objective(preview)
    draw_event(preview)
    draw_vitals(preview)
    draw_bottom(preview)
    draw_prompt(preview)
    temp = output.with_name(output.stem + "_base.png")
    save_png(temp, np.clip(canvas, 0, 1))
    draw_texts(temp, output)
    temp.unlink()
    print(f"HUD preview written: {output}")
    compare = os.environ.get("HUD_COMPARE")
    if compare and MASTER.is_file():
        master = load_png(MASTER)
        master = resize(master, W, H) if master.shape[:2] != (H, W) else master
        result = load_png(output)
        save_png(compare, np.concatenate([master, result], axis=0))
        print(f"Comparison written: {compare}")


if __name__ == "__main__":  # art/ui/preview_lobby.py imports these helpers
    main()
