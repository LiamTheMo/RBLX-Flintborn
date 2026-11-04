"""Sheet against render, view by view: crop each named cell from the model's reference sheet
(art/blender/assets/references/NNN.png), render the model at the matching camera, and set the two side by side, so
a verifier can judge every view from one image.

    import sys; sys.path.insert(0, "<repo>/art/blender/kit/mcp")
    import kit_mcp; kit_mcp.install()
    import importlib, compare; importlib.reload(compare)
    r = compare.compare(68, {
        "f34": {"box": (16, 104, 508, 466), "view": (-40, 15)},
        "side": {"box": (276, 532, 510, 738), "view": (90, 3), "mirror": True},
        "top": {"box": (765, 532, 1010, 738), "view": (0, 89.9)},
    })
    r["sheet"]          # <out_dir>/M068_compare.png: one row per two cells, sheet crop left, render right

Per cell: box = sheet pixels (x0, y0, x1, y1), origin top left; view = (azimuth, elevation) as the kit cameras use
them (azimuth 0 looks from the front, -Y; 90 from +X); optional lens (focal multiplier of the studio camera, default
3.0: the near-orthographic sheet look the builders' *_sheet shots use), mirror (render with the objects mirrored
front-to-back, scale y -1, for cells drawn mirrored), rot90 (turn the render by that many quarter turns
counter-clockwise, for a top cell drawn turned), objs (names or objects; default the model's hero), floor (show the
studio floor; default hidden), vfx. The render gets the cell's aspect at `height` px; the crop is scaled to the same
size.
Each pair is labelled with the cell name, the camera and the content W : H of both (bounding box of everything that
is not background).

Writes <out_dir>/<cell>_render.png, <cell>_pair.png and M<NNN>_compare.png; out_dir defaults to the system temp folder
(<temp>/RBLX-Flintborn/compare/MNNN/), so a read-only verifier never writes into the repo. Nothing in the scene is
left changed.
"""
import math
import os

import bpy
import numpy as np

import kit_mcp as K
import kit_models as M

PAPER = (0.988, 0.980, 0.965)
INK = (0.12, 0.10, 0.10)

# 5 x 7 bitmap font (rows top to bottom, 5 bits each, as hex pairs) for the labels
_FONT = {
    "A": "0E11111F111111", "B": "1E11111E11111E", "C": "0E11101010110E", "D": "1E11111111111E",
    "E": "1F10101E10101F", "F": "1F10101E101010", "G": "0E11101711110F",
    "H": "1111111F111111", "I": "0E04040404040E", "J": "0702020202120C", "K": "11121418141211",
    "L": "1010101010101F", "M": "111B1515111111", "N": "11111915131111", "O": "0E11111111110E",
    "P": "1E11111E101010", "Q": "0E11111115120D", "R": "1E11111E141211", "S": "0F10100E01011E",
    "T": "1F040404040404", "U": "1111111111110E", "V": "11111111110A04",
    "W": "1111111515150A", "X": "11110A040A1111", "Y": "1111110A040404", "Z": "1F01020408101F",
    "0": "0E11131519110E", "1": "040C040404040E", "2": "0E11010204081F",
    "3": "1F02040201110E", "4": "02060A121F0202", "5": "1F101E0101110E", "6": "0608101E11110E",
    "7": "1F010204080808", "8": "0E11110E11110E", "9": "0E11110F01020C", " ": "00000000000000",
    ".": "00000000000C0C", ":": "000C0C000C0C00", "-": "0000001F000000", "_": "0000000000001F",
    "(": "02040808080402", ")": "08040202020408", "/": "00010204081000", ",": "000000000C0408",
    "=": "00001F001F0000", "+": "0004041F040400",
}


def _glyph(ch):
    h = _FONT.get(ch.upper(), _FONT[" "])
    rows = [int(h[i:i + 2], 16) for i in range(0, 14, 2)]
    return np.array([[(r >> (4 - b)) & 1 for b in range(5)] for r in rows], bool)


def _label(img, text, x, y, scale=2, colour=INK):
    """Draw text into a top-down RGBA float image at (x, y) (top left of the first glyph)."""
    for i, ch in enumerate(text):
        g = np.repeat(np.repeat(_glyph(ch), scale, axis=0), scale, axis=1)
        x0 = x + i * 6 * scale
        if x0 + g.shape[1] > img.shape[1] or y + g.shape[0] > img.shape[0]:
            break
        sub = img[y:y + g.shape[0], x0:x0 + g.shape[1], :3]
        sub[g] = colour


def _load(path):
    """Top-down RGBA float array of a PNG."""
    return np.flipud(K.NS["KIT"]["load_px"](path)).copy()


def _save(img, path):
    K.NS["KIT"]["save_px"](np.flipud(img).copy(), path)
    return path


def _resize(img, h, w):
    """Bilinear resize of a top-down image to (h, w)."""
    H, W = img.shape[:2]
    ys = np.clip((np.arange(h) + 0.5) * H / h - 0.5, 0, H - 1)
    xs = np.clip((np.arange(w) + 0.5) * W / w - 0.5, 0, W - 1)
    y0, x0 = np.floor(ys).astype(int), np.floor(xs).astype(int)
    y1, x1 = np.minimum(y0 + 1, H - 1), np.minimum(x0 + 1, W - 1)
    fy, fx = (ys - y0)[:, None, None], (xs - x0)[None, :, None]
    top = img[y0][:, x0] * (1 - fx) + img[y0][:, x1] * fx
    bot = img[y1][:, x0] * (1 - fx) + img[y1][:, x1] * fx
    return (top * (1 - fy) + bot * fy).astype(np.float32)


def content_wh(img, tol=0.07):
    """W : H of the bounding box of everything that differs from the background (the median of the border
    pixels) by more than tol in any channel; rows / columns with under 0.5 % of their pixels set don't count."""
    rgb = img[..., :3]
    border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    bg = np.median(border, axis=0)
    m = np.abs(rgb - bg).max(axis=2) > tol
    rows = np.where(m.sum(axis=1) > 0.005 * m.shape[1])[0]
    cols = np.where(m.sum(axis=0) > 0.005 * m.shape[0])[0]
    if not len(rows) or not len(cols):
        return None
    return round((cols[-1] - cols[0] + 1) / (rows[-1] - rows[0] + 1), 3)


def _render(objs, path, az, el, size, lens, mirror, floor, vfx):
    kit = K.NS["KIT"]
    cam = bpy.data.objects["FB_Cam"].data
    ground = bpy.data.objects.get("FB_Ground")
    old_cell, old_lens = kit["CELL"], cam.lens
    gh = ground.hide_render if ground else None
    gloc = ground.location.copy() if ground else None
    scales = [(o, o.scale.y) for o in objs]
    sc = bpy.context.scene
    kit["CELL"] = size
    try:
        if mirror:
            for o, s in scales:
                o.scale.y = -s
            bpy.context.view_layer.update()
        cam.lens = old_lens * lens
        if ground:
            ground.hide_render = not floor
        if vfx:
            kit["vfx"].clear(sc)
            kit["vfx"].realize(sc, objs)
        return kit["render_group"](objs, path, az, el)
    finally:
        kit["CELL"] = old_cell
        cam.lens = old_lens
        if ground:
            ground.hide_render = gh
            ground.location = gloc
        for o, s in scales:
            o.scale.y = s
        bpy.context.view_layer.update()
        if vfx:
            kit["vfx"].clear(sc)


def _hero(num):
    code = M.code(num)
    objs = [o for o in bpy.data.objects if o.get("kit_sheet") == code and o.get("kit_role") == "hero"]
    if not objs:
        raise ValueError(f"no hero tagged kit_sheet {code}; pass objs")
    return objs[:1]


def compare(num, cells, objs=None, ref=None, out_dir=None, height=360, lens=3.0, vfx=False, per_row=2, gap=12):
    """Render every cell and set it beside its sheet crop. Returns {"sheet": path, "cells": {name: {"pair", "render",
    "view", "wh_sheet", "wh_ours"}}}."""
    code = M.code(num)
    ref = ref or M.ref(num)
    out_dir = (out_dir or os.path.join(K.TEMP_ROOT, "compare", code)).replace("\\", "/")
    os.makedirs(out_dir, exist_ok=True)
    base_objs = [bpy.data.objects[o] if isinstance(o, str) else o for o in (objs or _hero(num))]
    sheet = _load(ref)
    bar = 9 * 2 + 10
    res, pairs = {}, []
    for name, c in cells.items():
        x0, y0, x1, y1 = c["box"]
        crop = sheet[y0:y1, x0:x1]
        w = max(8, int(round(height * (x1 - x0) / (y1 - y0))))
        group = [bpy.data.objects[o] if isinstance(o, str) else o for o in c.get("objs", base_objs)]
        az, el = c["view"]
        k = c.get("rot90", 0) % 4
        rpath = _render(group, f"{out_dir}/{name}_render.png", az, el, (height, w) if k % 2 else (w, height),
                        c.get("lens", lens), c.get("mirror", False), c.get("floor", False), c.get("vfx", vfx))
        ours = np.ascontiguousarray(np.rot90(_load(rpath)[:, :, :4], k))
        if ours.shape[:2] != (height, w):
            ours = _resize(ours, height, w)
        crop = _resize(crop, height, w)
        wh_s, wh_o = content_wh(crop), content_wh(ours)
        pair = np.ones((height + bar, 2 * w + gap, 4), np.float32)
        pair[..., :3] = PAPER
        pair[bar:, :w] = crop
        pair[bar:, w + gap:] = ours
        pair[bar:, w:w + gap, :3] = 1.0
        mir = (" MIRROR" if c.get("mirror") else "") + (f" ROT {90 * k}" if k else "")
        _label(pair, f"{name} AZ {az} EL {el}{mir}", 4, 4)
        _label(pair, f"SHEET W:H {wh_s}  OURS {wh_o}", w + gap + 4, 4)
        ppath = _save(pair, f"{out_dir}/{name}_pair.png")
        pairs.append(pair)
        res[name] = {"pair": ppath, "render": rpath, "view": [az, el], "mirror": bool(c.get("mirror")), "rot90": k,
                     "wh_sheet": wh_s, "wh_ours": wh_o}
    rows = []
    for i in range(0, len(pairs), per_row):
        row = pairs[i:i + per_row]
        h = max(p.shape[0] for p in row)
        wsum = sum(p.shape[1] for p in row) + gap * 2 * (len(row) - 1)
        canvas = np.ones((h, wsum, 4), np.float32)
        canvas[..., :3] = 1.0
        x = 0
        for p in row:
            canvas[:p.shape[0], x:x + p.shape[1]] = p
            x += p.shape[1] + gap * 2
        rows.append(canvas)
    W = max(r.shape[1] for r in rows)
    total = np.ones((sum(r.shape[0] for r in rows) + gap * 2 * (len(rows) - 1), W, 4), np.float32)
    y = 0
    for r in rows:
        total[y:y + r.shape[0], :r.shape[1]] = r
        y += r.shape[0] + gap * 2
    path = _save(total, f"{out_dir}/{code}_compare.png")
    return {"sheet": path, "out_dir": out_dir, "cells": res}
