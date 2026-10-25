"""Composite a preview of the lobby screen from the shared layout and sprites.

Reads the "lobby" section of src/shared/UI/HudLayout.json (what
LobbyHudController builds from) and draws it with the sliced sprites over the
lobby master (art/reference/ui/lobby_master.png, blurred and darkened), using
the helpers of preview_hud.py. Writes art/ui/lobby_preview.png. It mirrors
src/client/Hud/LobbyHud.luau: same rects, sprites and texts.

Run through the Blender wrapper:

    art/blender/run.sh art/ui/preview_lobby.py art/ui/lobby_preview.png

Environment: HUD_COMPARE=<png> also writes the master and the preview stacked.
"""
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import preview_hud as P  # noqa: E402

P.MASTER = P.ROOT / "art" / "reference" / "ui" / "lobby_master.png"
OUTPUT = HERE / "lobby_preview.png"
LOBBY = P.layout["lobby"]
COLORS = LOBBY["colors"]


def lc(key):
    value = COLORS[key].lstrip("#")
    return tuple(int(value[i:i + 2], 16) / 255 for i in (0, 2, 4))


def at(entry, x, y):
    rx, ry, rw, rh = entry["rect"]
    return x + rx, y + ry, rw, rh


def draw_profile(preview):
    cfg = LOBBY["profile"]
    x, y, w, h = P.place(cfg)
    P.panel(cfg, x, y, w, h)
    ax, ay, aw, ah = at(cfg["avatar"], x, y)
    P.rrect(ax, ay, aw, ah, 8, lc("row"), 1)
    P.draw_headshot(ax + 6, ay + 4, aw - 12, ah - 4, 0)
    P.stroke_rrect(ax, ay, aw, ah, 8, 2, lc("rowStroke"), 1)
    P.text(cfg["name"], preview["name"], *at(cfg["name"], x, y))
    P.text(cfg["level"], "LV. %d" % preview["level"], *at(cfg["level"], x, y))
    xp = cfg["xp"]
    P.bar({"rect": xp["rect"], "inset": xp["inset"], "track": xp["track"], "fillColor": xp["fillColor"]},
          x, y, preview["xp"])


def draw_nav():
    cfg = LOBBY["nav"]
    count = len(cfg["buttons"])
    x, y, _, _ = P.place(cfg, (cfg["button"][0], cfg["pitch"] * (count - 1) + cfg["button"][1]))
    bw, bh = cfg["button"]
    for index, entry in enumerate(cfg["buttons"]):
        by = y + index * cfg["pitch"]
        P.draw_frame(cfg["frame"], x, by, bw, bh, cfg["sliceScale"], [0, 0, 0, 0])
        P.draw_sprite(entry["icon"], *at(cfg["icon"], x, by))
        P.text(cfg["label"], entry["label"], *at(cfg["label"], x, by), align="center")


def draw_currency(preview):
    cfg = LOBBY["currency"]
    x, y, w, h = P.place(cfg)
    P.panel(cfg, x, y, w, h)
    P.draw_sprite(cfg["coinIcon"]["icon"], *at(cfg["coinIcon"], x, y))
    P.text(cfg["coins"], preview["coins"], *at(cfg["coins"], x, y))
    P.draw_sprite(cfg["gemIcon"]["icon"], *at(cfg["gemIcon"], x, y))
    P.text(cfg["gems"], preview["gems"], *at(cfg["gems"], x, y))


def row_box(cfg, x, y):
    w, h = cfg["row"]["width"], cfg["list"]["rowHeight"]
    P.rrect(x, y, w, h, cfg["row"]["radius"], lc("row"), 1)
    P.stroke_rrect(x, y, w, h, cfg["row"]["radius"], 1.5, lc("rowStroke"), 1 - cfg["row"]["strokeTransparency"])


def draw_party(preview):
    cfg = LOBBY["party"]
    x, y, w, h = P.place(cfg)
    P.panel(cfg, x, y, w, h)
    P.draw_sprite(cfg["icon"]["icon"], *at(cfg["icon"], x, y), tint=cfg["icon"].get("tint"))
    members = preview["party"]
    P.text(cfg["title"], "PARTY  %d/%d" % (len(members), preview["partyMax"]), *at(cfg["title"], x, y))
    dx, dy, dw, dh = at(cfg["divider"], x, y)
    P.rrect(dx, dy, dw, dh, 0, (1, 1, 1), 1 - cfg["divider"]["transparency"])
    lx, ly, lw, lh = at(cfg["list"], x, y)
    step = cfg["list"]["rowHeight"] + cfg["list"]["rowGap"]
    for index, member in enumerate(members):
        ry = ly + index * step
        row_box(cfg, lx, ry)
        hx, hy, hw, hh = at(cfg["headshot"], lx, ry)
        P.draw_headshot(hx, hy, hw, hh, 0)
        s = cfg["dot"]["size"]
        cx, cy = lx + cfg["dot"]["centre"][0], ry + cfg["dot"]["centre"][1]
        P.rrect(cx - s / 2, cy - s / 2, s, s, s / 2, lc("online"), 1)
        P.text(cfg["memberName"], member["name"], *at(cfg["memberName"], lx, ry))
        if member.get("leader"):
            P.draw_sprite(cfg["crown"]["icon"], *at(cfg["crown"], lx, ry))
    ry = ly + len(members) * step
    row_box(cfg, lx, ry)
    P.draw_sprite(cfg["inviteIcon"]["icon"], *at(cfg["inviteIcon"], lx, ry))
    P.text(cfg["invite"], cfg["invite"]["text"], *at(cfg["invite"], lx, ry))
    # Scroll bar, as Roblox draws it for the list.
    P.rrect(lx + lw - cfg["list"]["scrollBar"], ly, cfg["list"]["scrollBar"], lh, 3, lc("scroll"), 0.9)


def draw_enter():
    cfg = LOBBY["enter"]
    x, y, w, h = P.place(cfg)
    P.panel(cfg, x, y, w, h)
    P.draw_sprite(cfg["icon"]["icon"], *at(cfg["icon"], x, y))
    for key in ("title", "subtitle"):
        P.text(cfg[key], cfg[key]["text"], *at(cfg[key], x, y), align="center", color="#FFD24A")
    sx, sy, sw, sh = at(cfg["server"], x, y)
    label = cfg["server"]["text"]
    P.text(cfg["server"], label, sx - 12, sy, sw, sh, align="center")
    size = cfg["chevron"]["size"]
    # About half the label's width right of centre, like the centred list layout.
    P.draw_sprite(cfg["chevron"]["icon"], sx + sw / 2 + 52, sy + (sh - size) / 2, size, size)


def draw_settings():
    cfg = LOBBY["settings"]
    x, y, w, h = P.place(cfg)
    P.draw_frame(cfg["frame"], x, y, w, h, cfg["sliceScale"], [0, 0, 0, 0])
    P.draw_sprite(cfg["icon"]["icon"], *at(cfg["icon"], x, y))


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    output = Path(argv[0]) if argv else OUTPUT
    P.canvas = P.background()
    preview = LOBBY["preview"]
    draw_profile(preview)
    draw_nav()
    draw_currency(preview)
    draw_party(preview)
    draw_enter()
    draw_settings()
    temp = output.with_name(output.stem + "_base.png")
    P.save_png(temp, np.clip(P.canvas, 0, 1))
    P.draw_texts(temp, output)
    temp.unlink()
    print(f"Lobby preview written: {output}")
    compare = os.environ.get("HUD_COMPARE")
    if compare:
        master = P.load_png(P.MASTER)
        master = P.resize(master, P.W, P.H) if master.shape[:2] != (P.H, P.W) else master
        result = P.load_png(output)
        P.save_png(compare, np.concatenate([master, result], axis=1))
        print(f"Comparison written: {compare}")


main()
