"""Composite a preview of the lobby screen from the shared layout and sprites.

Reads the "lobby" section of src/shared/UI/HudLayout.json (what LobbyHud.luau
builds from) and draws it with the pm_* sprites in art/ui/sprites on the
1672x941 design canvas, mirroring src/client/Hud/LobbyHud.luau: same rects,
sprites, padding, texts and party rows. Writes art/ui/lobby_preview.png.

Plain Python with numpy and Pillow:

    python3 art/ui/preview_lobby.py [out.png] [--bg scene|none] [--compare out_compare.png]

--bg scene (default) draws over a plain green wash; --bg none
leaves the canvas transparent like the master sheet, for pixel comparison.
--compare also writes the master and the preview stacked on one background.

Text uses Merriweather Bold (Roblox's family for the "serif" face) from
LOBBY_FONT=<path to a .ttf/.woff>; without it a local serif bold stands in, so
letter widths are approximate.
"""
import argparse
import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LAYOUT = json.loads((ROOT / "src" / "shared" / "UI" / "HudLayout.json").read_text(encoding="utf-8"))
SPRITES = HERE / "sprites"
MASTER = ROOT / "art" / "reference" / "ui" / "parchment" / "13_lobby_master.png"
W, H = LAYOUT["reference"]["width"], LAYOUT["reference"]["height"]
LOBBY = LAYOUT["lobby"]
COLORS = LAYOUT["colors"]
PAD = 2  # transparent padding around every sprite (LobbyHud SPRITE_PAD)

FALLBACK_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "C:/Windows/Fonts/georgiab.ttf",
    "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
]


def color(key, alpha=255):
    value = COLORS.get(key, key).lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)


_fonts = {}


def font(size):
    if size not in _fonts:
        paths = [os.environ.get("LOBBY_FONT", "")] + FALLBACK_FONTS
        for path in paths:
            if path and Path(path).is_file():
                _fonts[size] = ImageFont.truetype(path, size)
                break
        else:
            _fonts[size] = ImageFont.load_default()
    return _fonts[size]


class Canvas:
    def __init__(self, image):
        self.image = image

    def sprite(self, name, x, y, w, h):
        """A sprite whose art lands on (x, y, w, h); its padding spills over."""
        path = SPRITES / f"{name}.png"
        if not path.is_file():
            ImageDraw.Draw(self.image).rounded_rectangle([x, y, x + w, y + h], 8, color("paper"),
                                                         color("paperEdge"), 2)
            return
        art = Image.open(path).convert("RGBA").resize((w + PAD * 2, h + PAD * 2), Image.LANCZOS)
        self.image.alpha_composite(art, (x - PAD, y - PAD))

    def fit(self, name, x, y, w, h):
        """A sprite scaled to fit (x, y, w, h), centred (ScaleType.Fit)."""
        art = Image.open(SPRITES / f"{name}.png").convert("RGBA")
        scale = min(w / art.width, h / art.height)
        art = art.resize((max(1, round(art.width * scale)), max(1, round(art.height * scale))), Image.LANCZOS)
        self.image.alpha_composite(art, (x + (w - art.width) // 2, y + (h - art.height) // 2))

    def sliced(self, name, x, y, w, h, insets):
        """9-slice at natural corner size (SliceScale 1)."""
        art = Image.open(SPRITES / f"{name}.png").convert("RGBA")
        left, top, right, bottom = insets
        sw, sh = art.size
        cols = [(0, left, 0, left), (left, sw - right, left, w - right), (sw - right, sw, w - right, w)]
        rows = [(0, top, 0, top), (top, sh - bottom, top, h - bottom), (sh - bottom, sh, h - bottom, h)]
        for sx0, sx1, dx0, dx1 in cols:
            for sy0, sy1, dy0, dy1 in rows:
                if dx1 > dx0 and dy1 > dy0 and sx1 > sx0 and sy1 > sy0:
                    piece = art.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0), Image.LANCZOS)
                    self.image.alpha_composite(piece, (x + dx0, y + dy0))

    def text(self, entry, value, x, y, w, h, align="left", size=None):
        """Roblox-style text: the line box centred vertically in its rect, shrunk
        to fit its width down to 12 px (TextScaled with a size constraint)."""
        size = size or entry["textSize"]
        f = font(size)
        while f.getlength(value) > w and size > 12:
            size -= 1
            f = font(size)
        ascent, descent = f.getmetrics()
        width = f.getlength(value)
        tx = x + (w - width) / 2 if align == "center" else x
        ty = y + (h - (ascent + descent)) / 2
        ImageDraw.Draw(self.image).text((tx, ty), value, font=f, fill=color(entry["color"]))

    def rect(self, x, y, w, h, key, radius=0):
        ImageDraw.Draw(self.image).rounded_rectangle([x, y, x + w - 1, y + h - 1], radius, color(key))


def place(entry, size=None):
    """Top-left of a top-level widget {anchor, pos, size} on the design canvas."""
    w, h = size or entry["size"]
    ax, ay = entry["anchor"]
    sx, ox, sy, oy = entry["pos"]
    return round(sx * W + ox - ax * w), round(sy * H + oy - ay * h), w, h


def at(entry, x, y):
    rx, ry, rw, rh = entry["rect"]
    return x + rx, y + ry, rw, rh


def draw(c, preview):
    manifest = json.loads((SPRITES / "manifest.json").read_text(encoding="utf-8"))

    cfg = LOBBY["profile"]
    x, y, w, h = place(cfg)
    ax, ay, aw, ah = at(cfg["avatar"], x, y)
    c.rect(ax, ay, aw, ah, "photo")
    c.sprite(cfg["sprite"], x, y, w, h)
    c.text(cfg["name"], preview["name"], *at(cfg["name"], x, y))
    c.text(cfg["level"], "LV. %d" % preview["level"], *at(cfg["level"], x, y))
    bx, by, bw, bh = at(cfg["xp"], x, y)
    fill = round(bw * preview["xp"])
    if fill >= 1:
        c.sliced(cfg["xp"]["fill"], bx, by, fill, bh, manifest[cfg["xp"]["fill"]]["slice"])

    for key, value in (("coins", preview["coins"]), ("gems", preview["gems"])):
        cfg = LOBBY[key]
        x, y, w, h = place(cfg)
        c.sprite(cfg["sprite"], x, y, w, h)
        c.text(cfg["value"], value, *at(cfg["value"], x, y))
    cfg = LOBBY["settings"]
    c.sprite(cfg["sprite"], *place(cfg))

    nav = LOBBY["nav"]
    nx, ny, _, _ = place(dict(nav, size=[0, 0]))
    for index, button in enumerate(nav["buttons"]):
        col, row = index % nav["columns"], index // nav["columns"]
        c.sprite(button["sprite"], nx + col * nav["pitch"][0], ny + row * nav["pitch"][1], *nav["tile"])

    cfg = LOBBY["party"]
    x, y, w, h = place(cfg)
    c.sprite(cfg["sprite"], x, y, w, h)
    c.text(cfg["title"], cfg["title"]["text"], *at(cfg["title"], x, y))
    c.text(cfg["count"], "%d/%d" % (len(preview["party"]), preview["partyMax"]), *at(cfg["count"], x, y))
    c.rect(*at(cfg["divider"], x, y), "line")
    lx, ly, lw, lh = at(cfg["list"], x, y)
    rows = [("member", m) for m in preview["party"]] + [("empty", None)] * (preview["partyMax"] - len(preview["party"]))
    total = sum(cfg[kind]["height"] for kind, _ in rows)
    bar = cfg["list"]["scrollBar"] if total > lh else 0
    if bar:
        c.rect(lx + lw - bar, ly, bar, lh, "scrollTrack", bar // 2)
        c.rect(lx + lw - bar, ly, bar, round(lh * lh / total), "thumb", bar // 2)
    region = Image.new("RGBA", (lw - bar, lh), (0, 0, 0, 0))
    sub = Canvas(region)
    ry = 0
    for kind, member in rows:
        entry = cfg[kind]
        sub.rect(*at(entry["rule"], 0, ry), "rule")
        if kind == "member":
            hx, hy, hw, hh = at(entry["headshot"], 0, ry)
            sub.rect(hx, hy, hw, hh, "photo", 6)
            ImageDraw.Draw(region).rounded_rectangle([hx, hy, hx + hw - 1, hy + hh - 1], 6, None, color("photoEdge"), 2)
            sub.text(entry["name"], member["name"], *at(entry["name"], 0, ry))
            if member.get("leader"):
                sub.fit(entry["crown"]["sprite"], *at(entry["crown"], 0, ry))
                sub.fit(entry["invite"]["sprite"], *at(entry["invite"], 0, ry))
        else:
            dx, dy, dw, dh = at(entry["dot"], 0, ry)
            ImageDraw.Draw(region).ellipse([dx, dy, dx + dw - 1, dy + dh - 1], color("dot"))
        ry += entry["height"]
        if ry >= lh:
            break
    c.image.alpha_composite(region, (lx, ly))

    cfg = LOBBY["enter"]
    c.sprite(cfg["sprite"], *place(cfg))
    cfg = LOBBY["server"]
    x, y, w, h = place(cfg)
    c.sprite(cfg["sprite"], x, y, w, h)
    c.text(cfg["label"], cfg["label"]["text"], *at(cfg["label"], x, y))


def background(kind):
    if kind == "none":
        return Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # A soft green-to-dusk wash standing in for the lobby world behind the UI.
    top, bottom = (78, 112, 92), (36, 48, 40)
    column = Image.new("RGBA", (1, H))
    for y in range(H):
        t = y / (H - 1)
        column.putpixel((0, y), tuple(round(a + (b - a) * t) for a, b in zip(top, bottom)) + (255,))
    return column.resize((W, H))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", nargs="?", default=str(HERE / "lobby_preview.png"))
    parser.add_argument("--bg", choices=["scene", "none"], default="scene")
    parser.add_argument("--compare", default="")
    args = parser.parse_args()
    canvas = Canvas(background(args.bg))
    draw(canvas, LOBBY["preview"])
    canvas.image.save(args.output)
    print("wrote", args.output)
    if args.compare:
        master = Image.open(MASTER).convert("RGBA")
        stack = Image.new("RGBA", (W, H * 2 + 10), (60, 70, 60, 255))
        stack.alpha_composite(master, (0, 0))
        clean = Canvas(Image.new("RGBA", (W, H), (0, 0, 0, 0)))
        draw(clean, LOBBY["preview"])
        stack.alpha_composite(clean.image, (0, H + 10))
        stack.save(args.compare)
        print("wrote", args.compare)


if __name__ == "__main__":
    main()
