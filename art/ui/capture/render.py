"""Lay out and draw a GUI instance tree dumped by gui_env.luau.

Follows Roblox's rules closely enough to judge a screen against its reference:
UDim2 positions and sizes with AnchorPoint, UIScale (about the anchor point),
UIPadding, UIListLayout and UIGridLayout, AutomaticSize, UISizeConstraint,
UIAspectRatioConstraint, ScrollingFrame canvases and scroll bars,
ClipsDescendants, sibling ZIndex order, Frame fills with UICorner, UIStroke and
UIGradient, ImageLabel sprites (Stretch, Fit, Crop, Slice) with ImageColor3,
and TextLabel text (FontFace with Merriweather Regular / Bold / Black and Patrick
Hand, TextScaled with UITextSizeConstraint, wrapping, truncation, alignment,
stroke, RichText <font size> and <font color> runs on one line). Images resolve through
src/shared/UI/UiAssetIds.json to art/ui/sprites; avatar thumbnails draw as a
grey head placeholder.
"""
import json
import math
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
SPRITES = ROOT / "art" / "ui" / "sprites"
FONTS = ROOT / "art" / "ui" / "fonts"
IDS = json.loads((ROOT / "src" / "shared" / "UI" / "UiAssetIds.json").read_text(encoding="utf-8"))
BY_ID = {str(v): k for k, v in IDS.items()}
SS = 2  # supersampling for anti-aliased shapes

# Font files per (family, weight class). Roblox draws Merriweather Heavy
# (900) from the family's Black face; Bold stands in where a heavier face is
# missing. Patrick Hand has one weight.
FONT_FILES = {
    ("merriweather", "black"): ["Merriweather-Black.ttf", "Merriweather-Bold.woff", "Merriweather-Bold.ttf"],
    ("merriweather", "bold"): ["Merriweather-Bold.woff", "Merriweather-Bold.ttf"],
    ("merriweather", "regular"): ["Merriweather-Regular.woff", "Merriweather-Regular.ttf"],
    ("patrickhand", "regular"): ["PatrickHand-Regular.ttf"],
    ("patrickhand", "bold"): ["PatrickHand-Regular.ttf"],
    ("patrickhand", "black"): ["PatrickHand-Regular.ttf"],
}
FALLBACK = {
    True: ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"],
    False: ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf"],
}
SERIF_FALLBACK = {
    True: ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", "C:/Windows/Fonts/georgiab.ttf"],
    False: ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", "C:/Windows/Fonts/georgia.ttf"],
}
BOLD_WEIGHTS = ("SemiBold", "Bold", "ExtraBold", "Heavy")
BLACK_WEIGHTS = ("ExtraBold", "Heavy")
BOLD_ENUMS = ("Bold", "Black", "Heavy", "FredokaOne", "LuckiestGuy", "Bangers")

# --------------------------------------------------------------------------- utils


def enum(value):
    return str(value).split(".")[-1] if value is not None else ""


def c3(value, alpha=255):
    if not isinstance(value, dict):
        return (255, 255, 255, alpha)
    return (round(value["R"] * 255), round(value["G"] * 255), round(value["B"] * 255), alpha)


def ud(value, size):
    return value["Scale"] * size + value["Offset"]


_font_cache = {}


def font_for(props, size, weight_override=None):
    face = props.get("FontFace") or {}
    family = str(face.get("Family", "")).lower()
    weight = weight_override or enum(face.get("Weight", ""))
    legacy = enum(props.get("Font", ""))
    if "legacyarial" in family or not family:
        family = legacy.lower()
    bold = weight in BOLD_WEIGHTS or any(b.lower() in family for b in BOLD_ENUMS) or "bold" in legacy.lower()
    klass = "black" if weight in BLACK_WEIGHTS else ("bold" if bold else "regular")
    serif = "merriweather" in family
    hand = "patrickhand" in family
    key = (family, klass, size)
    if key not in _font_cache:
        paths = []
        if serif or hand:
            name = "merriweather" if serif else "patrickhand"
            paths = [FONTS / n for n in FONT_FILES[(name, klass)]]
        if serif or hand:
            paths += [Path(p) for p in SERIF_FALLBACK[bold]]
        paths += [Path(p) for p in FALLBACK[bold]]
        font = None
        for path in paths:
            if path.is_file():
                font = ImageFont.truetype(str(path), max(1, int(round(size))))
                break
        _font_cache[key] = font or ImageFont.load_default()
    return _font_cache[key]


def text_widths():
    """Advance widths (per 1 px of TextSize) of printable ASCII in the fonts
    the env's TextService:GetTextSize measures: {"Font.Merriweather": {...}}."""
    out = {}
    for enum_name, file in (("Font.Merriweather", "Merriweather-Regular.woff"),
                            ("Font.PatrickHand", "PatrickHand-Regular.ttf")):
        path = FONTS / file
        if path.is_file():
            font = ImageFont.truetype(str(path), 100)
            out[enum_name] = {chr(c): round(font.getlength(chr(c)) / 100, 4) for c in range(32, 127)}
    return out


_sprite_cache = {}


def sprite_for(image):
    if not image:
        return None
    match = re.search(r"(\d+)\s*$", str(image))
    name = BY_ID.get(match.group(1)) if match and str(image).startswith("rbxassetid") else None
    if str(image).startswith("rbxthumb"):
        name = "__thumb"
    if name is None:
        return None
    if name not in _sprite_cache:
        if name == "__thumb":
            _sprite_cache[name] = placeholder_head()
        else:
            path = SPRITES / f"{name}.png"
            _sprite_cache[name] = Image.open(path).convert("RGBA") if path.is_file() else None
    return _sprite_cache[name]


def placeholder_head():
    im = Image.new("RGBA", (150, 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([40, 30, 110, 110], fill=(245, 205, 150, 255))
    d.rectangle([34, 22, 116, 50], fill=(110, 70, 40, 255))
    d.rectangle([20, 112, 130, 150], fill=(90, 55, 35, 255))
    d.ellipse([58, 62, 66, 74], fill=(20, 20, 20, 255))
    d.ellipse([84, 62, 92, 74], fill=(20, 20, 20, 255))
    d.arc([60, 76, 90, 96], 20, 160, fill=(20, 20, 20, 255), width=3)
    return im


# --------------------------------------------------------------------------- layout


class Node:
    def __init__(self, data, parent=None):
        self.props = data["props"]
        self.cls = self.props.get("ClassName")
        self.parent = parent
        self.children = [Node(c, self) for c in data["children"]]
        self.rect = (0.0, 0.0, 0.0, 0.0)  # in parent-local unscaled px
        self.scale = 1.0

    def child_of(self, cls):
        return [c for c in self.children if c.cls == cls]

    def first(self, cls):
        found = self.child_of(cls)
        return found[0] if found else None

    @property
    def gui(self):
        return self.cls in ("Frame", "ScrollingFrame", "CanvasGroup", "TextLabel", "TextButton", "TextBox",
                            "ImageLabel", "ImageButton", "ViewportFrame", "ScreenGui")

    @property
    def visible(self):
        if self.cls == "ScreenGui":
            return self.props.get("Enabled", True) is not False
        return self.props.get("Visible", True) is not False


def text_bounds(node, width_limit=None):
    p = node.props
    text = strip_rich(str(p.get("Text", "")))
    size = p.get("TextSize", 14)
    font = font_for(p, size)
    lines = wrap(text, font, width_limit) if (p.get("TextWrapped") and width_limit) else text.split("\n")
    w = max((font.getlength(line) for line in lines), default=0)
    ascent, descent = font.getmetrics()
    return w, len(lines) * (ascent + descent) * p.get("LineHeight", 1)


def strip_rich(text):
    return re.sub(r"<[^>]+>", "", text)


RICH_TAG = re.compile(r"<font\s+([^>]*)>(.*?)</font>", re.S)


def rich_runs(text, size, color):
    """RichText as runs [(text, size, colour)]: honours <font size="n"> and
    <font color="#rrggbb">; other tags are dropped."""
    runs, pos = [], 0
    for m in RICH_TAG.finditer(text):
        if m.start() > pos:
            runs.append((strip_rich(text[pos:m.start()]), size, color))
        attrs = dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"', m.group(1)))
        run_size = float(attrs["size"]) if "size" in attrs else size
        run_color = color
        if attrs.get("color", "").startswith("#") and len(attrs["color"]) == 7:
            h = attrs["color"]
            run_color = (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), color[3])
        runs.append((strip_rich(m.group(2)), run_size, run_color))
        pos = m.end()
    if pos < len(text):
        runs.append((strip_rich(text[pos:]), size, color))
    return [r for r in runs if r[0]]


def draw_rich(painter, node, box, clip, runs, k):
    """One line of mixed-size runs on a shared baseline."""
    p = node.props
    x, y, w, h = box
    fonts = [font_for(p, size * k) for _, size, _ in runs]
    widths = [f.getlength(t) for f, (t, _, _) in zip(fonts, runs)]
    ascent = max(f.getmetrics()[0] for f in fonts)
    descent = max(f.getmetrics()[1] for f in fonts)
    total_w = sum(widths)
    xa, ya = enum(p.get("TextXAlignment")), enum(p.get("TextYAlignment"))
    lx = {"Left": 0, "Right": w - total_w}.get(xa, (w - total_w) / 2)
    line_h = ascent + descent
    ty = {"Top": 0, "Bottom": h - line_h}.get(ya, (h - line_h) / 2)
    pad = int(max(s for _, s, _ in runs) * k) + 8
    layer = Image.new("RGBA", (int(w) + pad * 2, int(line_h) + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx = pad + lx
    for font, width, (text, _, color) in zip(fonts, widths, runs):
        d.text((cx, pad + ascent - font.getmetrics()[0]), text, font=font, fill=color)
        cx += width
    painter.composite(layer, clip, (x - pad, y + ty - pad))


def wrap(text, font, width):
    out = []
    for para in text.split("\n"):
        words, line = para.split(" "), ""
        for word in words:
            trial = (line + " " + word).strip()
            if font.getlength(trial) <= width or not line:
                line = trial
            else:
                out.append(line)
                line = word
        out.append(line)
    return out


def layout(node, pw, ph):
    """Sizes and positions `node`'s children inside a pw × ph content box."""
    pad = node.first("UIPadding")
    left = top = 0.0
    if pad:
        left = ud(pad.props["PaddingLeft"], pw)
        right = ud(pad.props["PaddingRight"], pw)
        top = ud(pad.props["PaddingTop"], ph)
        bottom = ud(pad.props["PaddingBottom"], ph)
        pw, ph = max(0, pw - left - right), max(0, ph - top - bottom)
    kids = [c for c in node.children if c.gui and c.visible]
    for child in kids:
        size_child(child, pw, ph)
    lst, grid = node.first("UIListLayout"), node.first("UIGridLayout")
    if lst or grid:
        # A layout stacks auto-sized containers at their grown size, so grow
        # them first (the engine does the same).
        for child in kids:
            if enum(child.props.get("AutomaticSize")) != "None" and child.cls not in (
                    "TextLabel", "TextButton", "TextBox", "ScrollingFrame"):
                child.rect = (0, 0) + tuple(child.size)
                layout(child, *child.size)
                auto_size_after(child)
                child.size = (child.rect[2], child.rect[3])
    if lst:
        list_layout(lst, kids, pw, ph, left, top)
    elif grid:
        grid_layout(grid, kids, pw, ph, left, top)
    else:
        for child in kids:
            w, h = child.size
            if child.cls == "ScreenGui":
                child.rect = (0, 0, w, h)
                continue
            pos, anchor = child.props["Position"], child.props["AnchorPoint"]
            x = ud(pos["X"], pw) - anchor["X"] * w + left
            y = ud(pos["Y"], ph) - anchor["Y"] * h + top
            child.rect = (x, y, w, h)
    for child in kids:
        w, h = child.rect[2], child.rect[3]
        if child.cls == "ScrollingFrame":
            canvas_layout(child, w, h)
        else:
            layout(child, w, h)
            before = child.rect
            auto_size_after(child)
            if child.rect != before:
                # Children sized by scale follow the grown box, as in the engine.
                layout(child, child.rect[2], child.rect[3])


def size_child(child, pw, ph):
    if child.cls == "ScreenGui":
        # A nested ScreenGui (several guis dumped from PlayerGui) covers the screen.
        child.size = (pw, ph)
        return
    size = child.props["Size"]
    w, h = ud(size["X"], pw), ud(size["Y"], ph)
    ratio = child.first("UIAspectRatioConstraint")
    if ratio:
        r = ratio.props.get("AspectRatio", 1)
        if enum(ratio.props.get("DominantAxis")) == "Height":
            w = h * r
        else:
            h = w / r
    cons = child.first("UISizeConstraint")
    if cons:
        mn, mx = cons.props["MinSize"], cons.props["MaxSize"]
        w = min(max(w, mn["X"]), mx["X"])
        h = min(max(h, mn["Y"]), mx["Y"])
    auto = enum(child.props.get("AutomaticSize"))
    if auto != "None" and child.cls in ("TextLabel", "TextButton", "TextBox"):
        tw, th = text_bounds(child, w if auto == "Y" else None)
        if auto in ("X", "XY"):
            w = max(w, tw)
        if auto in ("Y", "XY"):
            h = max(h, th)
    child.size = (w, h)


def auto_size_after(child):
    """AutomaticSize for containers: grow to their laid-out children."""
    auto = enum(child.props.get("AutomaticSize"))
    if auto == "None" or child.cls in ("TextLabel", "TextButton", "TextBox"):
        return
    kids = [c for c in child.children if c.gui and c.visible]
    if not kids:
        return
    x0, y0, w, h = child.rect
    pad = child.first("UIPadding")
    extra_w = extra_h = 0
    if pad:
        extra_w = pad.props["PaddingRight"]["Offset"]
        extra_h = pad.props["PaddingBottom"]["Offset"]
    right = max(c.rect[0] + c.rect[2] for c in kids) + extra_w
    bottom = max(c.rect[1] + c.rect[3] for c in kids) + extra_h
    if auto in ("X", "XY"):
        w = max(w, right)
    if auto in ("Y", "XY"):
        h = max(h, bottom)
    child.rect = (x0, y0, w, h)


def sorted_kids(kids):
    return sorted(kids, key=lambda c: (c.props.get("LayoutOrder", 0)))


def list_layout(lst, kids, pw, ph, left, top):
    p = lst.props
    vertical = enum(p.get("FillDirection")) != "Horizontal"
    gap = ud(p["Padding"], ph if vertical else pw)
    kids = sorted_kids(kids) if enum(p.get("SortOrder")) == "LayoutOrder" else kids
    total = sum((k.size[1] if vertical else k.size[0]) for k in kids) + gap * max(0, len(kids) - 1)
    ha, va = enum(p.get("HorizontalAlignment")), enum(p.get("VerticalAlignment"))
    cursor = 0.0
    if vertical:
        cursor = {"Center": (ph - total) / 2, "Bottom": ph - total}.get(va, 0)
    else:
        cursor = {"Center": (pw - total) / 2, "Right": pw - total}.get(ha, 0)
    for k in kids:
        w, h = k.size
        if vertical:
            x = {"Center": (pw - w) / 2, "Right": pw - w}.get(ha, 0)
            k.rect = (x + left, cursor + top, w, h)
            cursor += h + gap
        else:
            y = {"Center": (ph - h) / 2, "Bottom": ph - h}.get(va, 0)
            k.rect = (cursor + left, y + top, w, h)
            cursor += w + gap
    lst.content = total


def grid_layout(grid, kids, pw, ph, left, top):
    p = grid.props
    cw, chh = ud(p["CellSize"]["X"], pw), ud(p["CellSize"]["Y"], ph)
    gx, gy = ud(p["CellPadding"]["X"], pw), ud(p["CellPadding"]["Y"], ph)
    horizontal = enum(p.get("FillDirection")) != "Vertical"
    per = int(p.get("FillDirectionMaxCells") or 0)
    if per <= 0:
        per = max(1, int((pw + gx) // (cw + gx))) if horizontal else max(1, int((ph + gy) // (chh + gy)))
    kids = sorted_kids(kids) if enum(p.get("SortOrder")) == "LayoutOrder" else kids
    cols = min(per, len(kids)) if horizontal else math.ceil(len(kids) / per)
    span = cols * cw + gx * max(0, cols - 1)
    ha = enum(p.get("HorizontalAlignment"))
    x0 = {"Center": (pw - span) / 2, "Right": pw - span}.get(ha, 0)
    for i, k in enumerate(kids):
        col, row = (i % per, i // per) if horizontal else (i // per, i % per)
        k.size = (cw, chh)
        k.rect = (x0 + left + col * (cw + gx), top + row * (chh + gy), cw, chh)
    rows = math.ceil(len(kids) / per) if horizontal else per
    grid.content = rows * chh + gy * max(0, rows - 1)


def canvas_layout(frame, w, h):
    p = frame.props
    bar = p.get("ScrollBarThickness", 12)
    inset = enum(p.get("VerticalScrollBarInset")) == "ScrollBar"
    canvas = p.get("CanvasSize")
    cw, chh = ud(canvas["X"], w), ud(canvas["Y"], h)
    auto = enum(p.get("AutomaticCanvasSize"))
    inner_w = w - (bar if inset else 0)
    layout(frame, inner_w, max(chh, h))
    kids = [c for c in frame.children if c.gui and c.visible]
    content = max((k.rect[1] + k.rect[3] for k in kids), default=0)
    lst = frame.first("UIListLayout") or frame.first("UIGridLayout")
    if lst is not None and hasattr(lst, "content"):
        content = max(content, lst.content)
    if auto in ("Y", "XY"):
        chh = content
    frame.canvas = (cw, max(chh, 0))
    frame.window = (w, h)


# --------------------------------------------------------------------------- draw


class Painter:
    def __init__(self, width, height, background):
        self.img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        if background is not None:
            self.img.paste(background, (0, 0))

    def composite(self, layer, clip, xy=(0, 0)):
        """Alpha-composites `layer` at xy, restricted to the clip rect."""
        x, y = int(round(xy[0])), int(round(xy[1]))
        cx0, cy0, cx1, cy1 = [int(round(v)) for v in clip]
        lx0, ly0 = max(x, cx0, 0), max(y, cy0, 0)
        lx1 = min(x + layer.width, cx1, self.img.width)
        ly1 = min(y + layer.height, cy1, self.img.height)
        if lx1 <= lx0 or ly1 <= ly0:
            return
        piece = layer.crop((lx0 - x, ly0 - y, lx1 - x, ly1 - y))
        self.img.alpha_composite(piece, (lx0, ly0))


def rounded_mask(w, h, radius):
    w, h = max(1, int(round(w))), max(1, int(round(h)))
    m = Image.new("L", (w * SS, h * SS), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w * SS - 1, h * SS - 1], radius=max(0, radius) * SS, fill=255)
    return m.resize((w, h), Image.LANCZOS)


def corner_radius(node, w, h):
    corner = node.first("UICorner")
    if not corner:
        return 0
    r = corner.props["CornerRadius"]
    return min(ud(r, min(w, h)), min(w, h) / 2)


def gradient_layer(node, w, h, rgb):
    """Fill colour with a UIGradient applied (colour multiply and transparency)."""
    grad = node.first("UIGradient")
    base = np.zeros((h, w, 4), np.float32)
    base[..., :3] = np.array(rgb[:3], np.float32)
    base[..., 3] = rgb[3]
    if not grad or grad.props.get("Enabled") is False:
        return base
    rot = math.radians(grad.props.get("Rotation", 0))
    ys, xs = np.mgrid[0:h, 0:w]
    u = ((xs + 0.5) / max(w, 1) - 0.5) * math.cos(rot) + ((ys + 0.5) / max(h, 1) - 0.5) * math.sin(rot) + 0.5
    u = np.clip(u, 0, 1)
    keys = grad.props["Color"]["Keypoints"]
    times = [k["Time"] for k in keys]
    for ch, comp in enumerate("RGB"):
        vals = [k["Value"][comp] for k in keys]
        base[..., ch] *= np.interp(u, times, vals)
    tkeys = grad.props["Transparency"]["Keypoints"]
    base[..., 3] *= 1 - np.interp(u, [k["Time"] for k in tkeys], [k["Value"] for k in tkeys])
    return base


def draw_frame(painter, node, box, clip):
    x, y, w, h = box
    iw, ih = max(1, int(round(w))), max(1, int(round(h)))
    radius = corner_radius(node, w, h)
    tr = node.props.get("BackgroundTransparency", 0)
    if tr < 1 and w >= 1 and h >= 1:
        rgb = c3(node.props.get("BackgroundColor3"), round(255 * (1 - tr)))
        fill = gradient_layer(node, iw, ih, rgb)
        mask = np.asarray(rounded_mask(iw, ih, radius), np.float32) / 255 if radius else np.ones((ih, iw), np.float32)
        fill[..., 3] *= mask
        painter.composite(Image.fromarray(np.clip(fill, 0, 255).astype(np.uint8), "RGBA"), clip, (x, y))
    stroke = next((s for s in node.child_of("UIStroke") if s.props.get("Enabled", True) is not False), None)
    is_text = node.cls in ("TextLabel", "TextButton", "TextBox")
    if stroke and not (is_text and enum(stroke.props.get("ApplyStrokeMode")) != "Border") and w >= 1 and h >= 1:
        t = stroke.props.get("Thickness", 1) * node.scale_total
        col = c3(stroke.props.get("Color"), round(255 * (1 - stroke.props.get("Transparency", 0))))
        pad = int(math.ceil(t)) + 2
        lw, lh = iw + pad * 2, ih + pad * 2
        layer = Image.new("RGBA", (lw * SS, lh * SS), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        half = t / 2
        d.rounded_rectangle([(pad - half) * SS, (pad - half) * SS, (pad + w + half) * SS, (pad + h + half) * SS],
                            radius=(radius + half) * SS, outline=col, width=max(1, int(round(t * SS))))
        painter.composite(layer.resize((lw, lh), Image.LANCZOS), clip, (x - pad, y - pad))


def nine_slice(img, center, scale, w, h):
    sw, sh = img.size
    l, t = center["Min"]["X"], center["Min"]["Y"]
    r, b = sw - center["Max"]["X"], sh - center["Max"]["Y"]
    dl, dt, dr, db = l * scale, t * scale, r * scale, b * scale
    if dl + dr > w:
        k = w / max(dl + dr, 1e-6)
        dl, dr = dl * k, dr * k
    if dt + db > h:
        k = h / max(dt + db, 1e-6)
        dt, db = dt * k, db * k
    out = Image.new("RGBA", (max(1, int(round(w))), max(1, int(round(h)))), (0, 0, 0, 0))
    xs_s = [0, l, sw - r, sw]
    ys_s = [0, t, sh - b, sh]
    xs_d = [0, dl, w - dr, w]
    ys_d = [0, dt, h - db, h]
    for i in range(3):
        for j in range(3):
            sx0, sx1, sy0, sy1 = xs_s[i], xs_s[i + 1], ys_s[j], ys_s[j + 1]
            dx0, dx1, dy0, dy1 = [int(round(v)) for v in (xs_d[i], xs_d[i + 1], ys_d[j], ys_d[j + 1])]
            if sx1 - sx0 < 1 or sy1 - sy0 < 1 or dx1 - dx0 < 1 or dy1 - dy0 < 1:
                continue
            piece = img.crop((int(sx0), int(sy0), int(sx1), int(sy1))).resize((dx1 - dx0, dy1 - dy0), Image.LANCZOS)
            out.alpha_composite(piece, (dx0, dy0))
    return out


def tint(img, color, transparency):
    if img is None:
        return None
    arr = np.asarray(img, np.float32).copy()
    if isinstance(color, dict):
        arr[..., 0] *= color["R"]
        arr[..., 1] *= color["G"]
        arr[..., 2] *= color["B"]
    arr[..., 3] *= 1 - transparency
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")


def draw_image(painter, node, box, clip):
    p = node.props
    img = sprite_for(p.get("Image"))
    if img is None or p.get("ImageTransparency", 0) >= 1:
        return
    x, y, w, h = box
    if w < 1 or h < 1:
        return
    rect_size = p.get("ImageRectSize") or {"X": 0, "Y": 0}
    if rect_size["X"] > 0 and rect_size["Y"] > 0:
        off = p.get("ImageRectOffset")
        img = img.crop((off["X"], off["Y"], off["X"] + rect_size["X"], off["Y"] + rect_size["Y"]))
    mode = enum(p.get("ScaleType"))
    if mode == "Slice":
        out = nine_slice(img, p["SliceCenter"], p.get("SliceScale", 1) * node.scale_total, w, h)
        ox, oy = x, y
    elif mode in ("Fit", "Crop"):
        k = (min if mode == "Fit" else max)(w / img.width, h / img.height)
        nw, nh = max(1, int(round(img.width * k))), max(1, int(round(img.height * k)))
        out = img.resize((nw, nh), Image.LANCZOS)
        ox, oy = x + (w - nw) / 2, y + (h - nh) / 2
        if mode == "Crop":
            clip = intersect(clip, (x, y, x + w, y + h))
    else:
        out = img.resize((max(1, int(round(w))), max(1, int(round(h)))), Image.LANCZOS)
        ox, oy = x, y
    radius = corner_radius(node, w, h)
    if radius:
        mask = rounded_mask(out.width, out.height, radius)
        a = np.asarray(out, np.float32).copy()
        a[..., 3] *= np.asarray(mask, np.float32) / 255
        out = Image.fromarray(a.astype(np.uint8), "RGBA")
    out = tint(out, p.get("ImageColor3"), p.get("ImageTransparency", 0))
    grad = node.first("UIGradient")
    if grad and grad.props.get("Enabled") is not False:
        # The gradient's transparency over the image (a ring's wipe).
        layer = gradient_layer(node, out.width, out.height, (255, 255, 255, 255))
        a = np.asarray(out, np.float32).copy()
        a[..., 3] *= layer[..., 3] / 255
        out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    painter.composite(out, clip, (ox, oy))


def fit_text_size(node, w, h):
    p = node.props
    size = p.get("TextSize", 14)
    if not p.get("TextScaled"):
        return size
    cons = node.first("UITextSizeConstraint")
    mx = cons.props.get("MaxTextSize", 100) if cons else 100
    mn = cons.props.get("MinTextSize", 1) if cons else 1
    text = strip_rich(str(p.get("Text", "")))
    lo = int(mn)
    for s in range(int(min(mx, max(h, 1) * 2)), int(mn) - 1, -1):
        f = font_for(p, s)
        ascent, descent = f.getmetrics()
        lines = wrap(text, f, w) if p.get("TextWrapped") else text.split("\n")
        tw = max((f.getlength(line) for line in lines), default=0)
        th = len(lines) * (ascent + descent)
        if tw <= w + 0.5 and th <= h * 1.08 + 0.5:
            return s
    return lo


def draw_text(painter, node, box, clip):
    p = node.props
    raw = str(p.get("Text", ""))
    text = strip_rich(raw)
    color_key = "TextColor3"
    if not text and node.cls == "TextBox":
        text = str(p.get("PlaceholderText", ""))
        if p.get("PlaceholderColor3"):
            color_key = "PlaceholderColor3"
    if not text or p.get("TextTransparency", 0) >= 1:
        return
    x, y, w, h = box
    k = node.scale_total
    if p.get("RichText") and "<font" in raw and not p.get("TextScaled"):
        color = c3(p.get(color_key), round(255 * (1 - p.get("TextTransparency", 0))))
        draw_rich(painter, node, box, clip, rich_runs(raw, p.get("TextSize", 14), color), k)
        return
    size = fit_text_size(node, w / k, h / k) * k
    font = font_for(p, size)
    ascent, descent = font.getmetrics()
    line_h = (ascent + descent) * p.get("LineHeight", 1)
    lines = wrap(text, font, w) if p.get("TextWrapped") else text.split("\n")
    if enum(p.get("TextTruncate")) == "AtEnd":
        fixed = []
        for line in lines:
            while font.getlength(line) > w and len(line) > 1:
                line = line[:-2] + "…"
            fixed.append(line)
        lines = fixed
    total = line_h * len(lines)
    ya = enum(p.get("TextYAlignment"))
    ty = y + {"Top": 0, "Bottom": h - total}.get(ya, (h - total) / 2)
    xa = enum(p.get("TextXAlignment"))
    color = c3(p.get(color_key), round(255 * (1 - p.get("TextTransparency", 0))))
    pad = int(size) + 8
    layer = Image.new("RGBA", (int(w) + pad * 2, int(total) + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    stroke = next((s for s in node.child_of("UIStroke")
                   if enum(s.props.get("ApplyStrokeMode")) != "Border" and s.props.get("Enabled", True) is not False), None)
    stroke_w, stroke_fill = 0, None
    if stroke:
        stroke_w = max(1, int(round(stroke.props.get("Thickness", 1) * k)))
        stroke_fill = c3(stroke.props.get("Color"), round(255 * (1 - stroke.props.get("Transparency", 0))))
    elif p.get("TextStrokeTransparency", 1) < 1:
        stroke_w = max(1, int(round(k)))
        stroke_fill = c3(p.get("TextStrokeColor3"), round(255 * (1 - p.get("TextStrokeTransparency", 1))))
    for i, line in enumerate(lines):
        lw = font.getlength(line)
        lx = {"Left": 0, "Right": w - lw}.get(xa, (w - lw) / 2)
        d.text((pad + lx, pad + i * line_h + (line_h - ascent - descent) / 2), line, font=font, fill=color,
               stroke_width=stroke_w, stroke_fill=stroke_fill)
    painter.composite(layer, clip, (x - pad, ty - pad))


def intersect(a, b):
    return (max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]))


def paint(painter, node, origin, scale, clip):
    """Draws `node` (laid out at node.rect inside its parent's local space)."""
    ox, oy = origin
    x, y, w, h = node.rect
    ui = node.first("UIScale")
    own = ui.props.get("Scale", 1) if ui else 1
    # UIScale keeps the anchor point in place.
    anchor = node.props.get("AnchorPoint", {"X": 0, "Y": 0})
    ax, ay = x + anchor["X"] * w, y + anchor["Y"] * h
    sx = ox + (ax - anchor["X"] * w * own) * scale
    sy = oy + (ay - anchor["Y"] * h * own) * scale
    k = scale * own
    node.scale_total = k
    box = (sx, sy, w * k, h * k)
    if node.cls in ("Frame", "ScrollingFrame", "TextLabel", "TextButton", "TextBox", "ImageLabel",
                    "ImageButton", "CanvasGroup", "ViewportFrame"):
        draw_frame(painter, node, box, clip)
    if node.cls in ("ImageLabel", "ImageButton"):
        draw_image(painter, node, box, clip)
    if node.cls in ("TextLabel", "TextButton", "TextBox"):
        draw_text(painter, node, box, clip)
    child_clip = clip
    if node.props.get("ClipsDescendants") or node.cls == "ScrollingFrame":
        child_clip = intersect(clip, (box[0], box[1], box[0] + box[2], box[1] + box[3]))
    pad = node.first("UIPadding")
    kids = [c for c in node.children if c.gui and c.visible]
    kids.sort(key=lambda c: c.props.get("DisplayOrder", 0) if c.cls == "ScreenGui" else c.props.get("ZIndex", 1))
    origin = (box[0], box[1])
    if node.cls == "ScrollingFrame":
        # The canvas scrolls by CanvasPosition (canvas px, scaled like the frame).
        cpos = node.props.get("CanvasPosition") or {"X": 0, "Y": 0}
        origin = (box[0] - cpos["X"] * k, box[1] - cpos["Y"] * k)
    for child in kids:
        paint(painter, child, origin, k, child_clip)
    if node.cls == "ScrollingFrame":
        draw_scrollbar(painter, node, box, k, clip)


def draw_scrollbar(painter, node, box, k, clip):
    cw, chh = getattr(node, "canvas", (0, 0))
    ww, wh = getattr(node, "window", (1, 1))
    if chh <= wh + 0.5 or enum(node.props.get("ScrollingDirection")) == "X":
        return
    t = node.props.get("ScrollBarThickness", 12) * k
    if t <= 0:
        return
    x, y, w, h = box
    length = h * wh / chh
    color = c3(node.props.get("ScrollBarImageColor3"), round(255 * (1 - node.props.get("ScrollBarImageTransparency", 0))))
    layer = Image.new("RGBA", (max(1, int(t)), max(1, int(length))), (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle([0, 0, layer.width - 1, layer.height - 1], radius=t / 2, fill=color)
    painter.composite(layer, clip, (x + w - t, y))


def render(tree, out_path, background="scene"):
    width, height = int(tree["width"]), int(tree["height"])
    root = Node(tree["root"])
    root.rect = (0, 0, width, height)
    root.size = (width, height)
    layout(root, width, height)
    bg = None
    if tree.get("background"):
        bg = Image.open(ROOT / tree["background"]).convert("RGBA").resize((width, height), Image.LANCZOS)
    elif background == "scene":
        top, bottom = (78, 112, 92), (36, 48, 40)
        col = np.linspace(0, 1, height)[:, None]
        arr = np.zeros((height, width, 4), np.uint8)
        for ch in range(3):
            arr[..., ch] = (top[ch] + (bottom[ch] - top[ch]) * col).astype(np.uint8)
        arr[..., 3] = 255
        bg = Image.fromarray(arr, "RGBA")
    painter = Painter(width, height, bg)
    paint(painter, root, (0, 0), 1, (0, 0, width, height))
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    painter.img.save(out_path)
    return painter.img
