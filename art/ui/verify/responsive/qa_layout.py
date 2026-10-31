#!/usr/bin/env python3
"""Responsive & platform QA harness (independent verifier, read-only on source).

Runs the scene bodies in art/ui/verify/responsive/scenes/*.luau through the same
headless runtime as art/ui/capture/capture.py (gui_env.luau + the real game
modules), once per device profile, with a header that sets the viewport and the
input type BEFORE any game module is required (so Kit text boosts, phone
placements and touch hit pads see the device). It then lays the dumped tree out
with render.py and checks it:

  - text effective size in screen px (TextSize x every UIScale above it)
  - text overflow / truncation at its design size
  - elements off-screen and under the Roblox top-bar band
  - touch hit targets (Kit "Hit" pads simulated the way Interact.fitTouch grows
    them in game, since the harness has no AbsoluteSize), and pads that cover a
    neighbour's art
  - gamepad: Selectable / NextSelection / default selection (reported by the
    scene through @@QA@@ lines)

    python3 art/ui/verify/responsive/qa_layout.py                 # every scene x profile
    python3 art/ui/verify/responsive/qa_layout.py lobby_hud       # one scene
    python3 art/ui/verify/responsive/qa_layout.py lobby_hud --profiles phone844

Outputs: captures/<scene>/<profile>[_pN].png (+ _qa.png with the top-bar band,
hit pads and flagged boxes drawn), data/<scene>__<profile>.json, data/summary.json.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CAPTURE = ROOT / "art" / "ui" / "capture"
sys.path.insert(0, str(CAPTURE))
import capture  # noqa: E402
import render  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

OUT_CAP = HERE / "captures"
OUT_DATA = HERE / "data"
TOP_BAR = 58          # Roblox top bar height (GuiService.TopbarInset.Max.Y) assumed on every device
UNIBAR_W = 200        # approx. width of Roblox's top-left unibar (menu, chat, ...) on phones/tablets
TOUCH_MIN = 44
PHONE_MIN_TEXT = 9

# name: (W, H, input, label)
PROFILES = {
    "desk1080": (1920, 1080, "kbm", "1920x1080 mouse/keyboard"),
    "desk768": (1366, 768, "kbm", "1366x768 mouse/keyboard"),
    "ultra2560": (2560, 1080, "kbm", "2560x1080 ultrawide"),
    "tab1280": (1280, 800, "touch", "1280x800 tablet (touch)"),
    "tab1024": (1024, 768, "touch", "1024x768 4:3 tablet (touch)"),
    "phone2532": (2532, 1170, "touch", "2532x1170 phone px, literal (touch)"),
    "phone1334": (1334, 750, "touch", "1334x750 phone px, literal (touch)"),
    "phone844": (844, 390, "touch", "844x390 phone (iPhone 12-15 in points, touch)"),
    "phone667": (667, 375, "touch", "667x375 phone (iPhone 8/SE in points, touch) [edge]"),
    "console1080": (1920, 1080, "gamepad", "1920x1080 console (gamepad)"),
    "superwide": (5120, 1440, "kbm", "5120x1440 32:9 [edge]"),
}
DEFAULT_PROFILES = list(PROFILES)


def header(name, W, H, kind):
    touch = kind == "touch"
    pad = kind == "gamepad"
    kbm = kind == "kbm"
    last = {"touch": "Touch", "gamepad": "Gamepad1", "kbm": "MouseMovement"}[kind]
    return f"""
for key, widths in table.clone(__textWidths or {{}}) do
	__textWidths["Enum." .. key] = __textWidths["Enum." .. key] or widths
end
QA = {{ W = {W}, H = {H}, touch = {str(touch).lower()}, gamepad = {str(pad).lower()}, kbm = {str(kbm).lower()},
	top = {TOP_BAR}, profile = "{name}", kind = "{kind}" }}
do
	local UIS = game:GetService("UserInputService")
	workspace.CurrentCamera.ViewportSize = Vector2.new(QA.W, QA.H)
	UIS.TouchEnabled = QA.touch
	UIS.KeyboardEnabled = QA.kbm
	UIS.MouseEnabled = QA.kbm
	UIS.GamepadEnabled = QA.gamepad
	UIS.GetLastInputType = function()
		return __enum("UserInputType.{last}")
	end
end
local function qaPath(object)
	local parts = {{}}
	local node = object
	while node and node.Parent and not node:IsA("PlayerGui") do
		table.insert(parts, 1, node.Name)
		node = node.Parent
	end
	return table.concat(parts, "/")
end
local function qaShown(object)
	local node = object
	while node do
		if node:IsA("ScreenGui") then
			return node.Enabled ~= false
		end
		if node:IsA("GuiObject") and node.Visible == false then
			return false
		end
		node = node.Parent
	end
	return true
end
-- Marks a node in the dump (props are dumped as-is).
function QA.mark(object, key, value)
	if object then
		rawget(object, "__props")["QA_" .. key] = if value == nil then true else value
	end
end
-- Gamepad facts for every shown GuiButton/TextBox under `root`, printed as one @@QA@@ line.
function QA.report(root, extra)
	local GuiService = game:GetService("GuiService")
	local rows = {{}}
	for _, object in root:GetDescendants() do
		if (object:IsA("GuiButton") or object:IsA("TextBox")) and qaShown(object) then
			table.insert(rows, {{
				path = qaPath(object),
				selectable = object.Selectable == true,
				interactable = object.Interactable ~= false,
				nav = (object.NextSelectionUp ~= nil and 1 or 0) + (object.NextSelectionDown ~= nil and 1 or 0)
					+ (object.NextSelectionLeft ~= nil and 1 or 0) + (object.NextSelectionRight ~= nil and 1 or 0),
			}})
		end
	end
	local selected = GuiService.SelectedObject
	local out = {{ buttons = rows, selected = selected and qaPath(selected) or nil, extra = extra }}
	print("@@QA@@" .. __json(out) .. "@@END@@")
end
"""


# ----------------------------------------------------------------------- running

def run(scene_path: Path, profile: str):
    W, H, kind, _ = PROFILES[profile]
    extra_ids = capture.preview_ids()
    render.BY_ID.update({str(v): k for k, v in extra_ids.items()})
    body = scene_path.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        scene = Path(tmp) / f"qa_{scene_path.stem}.luau"
        scene.write_text(header(profile, W, H, kind) + "\n" + body, encoding="utf-8")
        bundle = Path(tmp) / "bundle.luau"
        bundle.write_text(capture.bundle(scene, extra_ids), encoding="utf-8")
        res = subprocess.run([shutil.which("luau"), str(bundle)], capture_output=True, text=True)
    out = res.stdout
    logs = [l for l in out.splitlines() if not l.startswith("@@GUI@@") and not l.startswith("@@QA@@")]
    if res.returncode != 0:
        return None, None, logs + res.stderr.splitlines()
    dumps = [json.loads(c.split("@@END@@")[0]) for c in out.split("@@GUI@@")[1:]]
    qas = [json.loads(c.split("@@END@@")[0]) for c in out.split("@@QA@@")[1:]]
    return dumps, qas, logs


# ----------------------------------------------------------------------- geometry

class Box:
    __slots__ = ("node", "x", "y", "w", "h", "k", "clip", "path", "parent")


def walk(node, origin, scale, clip, path, parent_box, out):
    ox, oy = origin
    x, y, w, h = node.rect
    ui = node.first("UIScale")
    own = ui.props.get("Scale", 1) if ui else 1
    anchor = node.props.get("AnchorPoint", {"X": 0, "Y": 0})
    ax, ay = x + anchor["X"] * w, y + anchor["Y"] * h
    sx = ox + (ax - anchor["X"] * w * own) * scale
    sy = oy + (ay - anchor["Y"] * h * own) * scale
    k = scale * own
    b = Box()
    b.node, b.x, b.y, b.w, b.h, b.k, b.clip, b.path = node, sx, sy, w * k, h * k, k, clip, path
    b.parent = parent_box
    node.box = b
    out.append(b)
    child_clip = clip
    if node.props.get("ClipsDescendants") or node.cls == "ScrollingFrame":
        child_clip = render.intersect(clip, (sx, sy, sx + w * k, sy + h * k))
    o = (sx, sy)
    if node.cls == "ScrollingFrame":
        cpos = node.props.get("CanvasPosition") or {"X": 0, "Y": 0}
        o = (sx - cpos["X"] * k, sy - cpos["Y"] * k)
    for child in node.children:
        if child.gui and child.visible:
            walk(child, o, k, child_clip, path + "/" + str(child.props.get("Name", child.cls)), b, out)


def clipped(b):
    x0, y0 = max(b.x, b.clip[0]), max(b.y, b.clip[1])
    x1, y1 = min(b.x + b.w, b.clip[2]), min(b.y + b.h, b.clip[3])
    return (x0, y0, x1, y1) if x1 > x0 and y1 > y0 else None


def has_content(b):
    p = b.node.props
    if b.node.cls in ("TextLabel", "TextButton", "TextBox") and str(p.get("Text", "")).strip():
        return p.get("TextTransparency", 0) < 1
    if b.node.cls in ("ImageLabel", "ImageButton") and p.get("Image") and p.get("ImageTransparency", 0) < 1:
        return True
    if b.node.cls in ("Frame", "ScrollingFrame", "TextLabel", "ImageLabel", "CanvasGroup") and p.get("BackgroundTransparency", 0) < 0.95:
        return True
    return False


def text_metrics(b):
    """(effective screen px, status) for a text node."""
    node, p = b.node, b.node.props
    raw = str(p.get("Text", ""))
    text = render.strip_rich(raw)
    size = p.get("TextSize", 14)
    wd, hd = b.w / b.k if b.k else 0, b.h / b.k if b.k else 0
    if p.get("RichText") and "<font" in raw:
        runs = render.rich_runs(raw, size, (0, 0, 0, 255))
        size = min([r[1] for r in runs] or [size])
    if p.get("TextScaled"):
        # In game Widgets.TextCap re-caps the constraint in SCREEN px:
        # Max = round(maxSize * k), Min = min(minSize, Max). The harness leaves
        # the design-px values, so model the game here.
        cons = node.first("UITextSizeConstraint")
        mx = cons.props.get("MaxTextSize", 100) if cons else 100
        mn = cons.props.get("MinTextSize", 1) if cons else 1
        cap = max(1, round(mx * b.k)) if cons else 1e9
        floor = min(mn, cap) if cons else 1
        fit = 1
        for s in range(int(min(mx, max(hd, 1) * 2)), 0, -1):
            f = render.font_for(p, s)
            asc, desc = f.getmetrics()
            lines = render.wrap(text, f, wd) if p.get("TextWrapped") else text.split("\n")
            if max((f.getlength(l) for l in lines), default=0) <= wd + 0.5 and len(lines) * (asc + desc) <= hd * 1.08 + 0.5:
                fit = s
                break
        fit_screen = fit * b.k
        eff = min(max(fit_screen, floor), cap)
        status = "scaled-nofit" if fit_screen < floor - 0.25 else "ok"
        return eff, status, text
    eff = size * b.k
    status = "ok"
    font = render.font_for(p, size)
    if p.get("TextWrapped"):
        lines = render.wrap(text, font, wd)
        asc, desc = font.getmetrics()
        th = len(lines) * (asc + desc) * p.get("LineHeight", 1)
        if th > hd * 1.15 + 2 and not p.get("TextScaled"):
            status = "overflow-v"
        # a single word longer than the box
        if any(font.getlength(l) > wd + 2 for l in lines):
            status = "overflow-h"
    else:
        tw = max((font.getlength(l) for l in text.split("\n")), default=0)
        if tw > wd + 2:
            status = "truncated" if render.enum(p.get("TextTruncate")) == "AtEnd" else "overflow-h"
    return eff, status, text


def analyse(tree, qa, profile):
    W, H, kind, _ = PROFILES[profile]
    root = render.Node(tree["root"])
    root.rect = (0, 0, tree["width"], tree["height"])
    root.size = (tree["width"], tree["height"])
    render.layout(root, tree["width"], tree["height"])
    boxes = []
    walk(root, (0, 0), 1, (0, 0, W, H), "", None, boxes)
    res = {"texts": [], "offscreen": [], "topbar": [], "touch": [], "pads": [], "flags": []}
    screen = (0, 0, W, H)
    reported_off = set()
    for b in boxes:
        n = b.node
        if n.cls in ("ScreenGui", "PlayerGui", "Folder") or b.node.props.get("Name") in ("Veil",):
            continue
        vis = clipped(b)
        is_text = n.cls in ("TextLabel", "TextButton", "TextBox") and str(n.props.get("Text", "")).strip() \
            and n.props.get("TextTransparency", 0) < 1
        if is_text and vis:
            eff, status, text = text_metrics(b)
            res["texts"].append({"path": b.path, "text": text[:60], "px": round(eff, 2), "status": status,
                                 "box": [round(v) for v in (b.x, b.y, b.w, b.h)]})
        # off-screen: visible content outside the screen (after clipping by ancestors)
        if vis and has_content(b) and b.w < W * 0.98 and b.h < H * 0.98:
            x0, y0, x1, y1 = vis
            out = max(0 - x0, 0 - y0, x1 - W, y1 - H)
            if out > 2 and not any(b.path.startswith(r + "/") for r in reported_off):
                res["offscreen"].append({"path": b.path, "by": round(out), "box": [round(v) for v in vis]})
                reported_off.add(b.path)
        # top-bar band
        if vis and (is_text or n.cls in ("TextButton", "ImageButton", "TextBox")) and n.props.get("Name") != "Hit":
            x0, y0, x1, y1 = vis
            if y0 < TOP_BAR - 2 and y1 > 2:
                res["topbar"].append({"path": b.path, "box": [round(v) for v in vis],
                                      "unibar": x0 < UNIBAR_W, "text": str(n.props.get("Text", ""))[:30]})
        # touch targets
        if n.cls in ("TextButton", "ImageButton", "TextBox") and vis and n.props.get("Interactable", True) is not False:
            if n.props.get("Name") == "Hit" and b.parent is not None:
                pb = b.parent
                bw, bh = pb.w / pb.k, pb.h / pb.k  # base design size of the kit component
                cur = -n.props["Position"]["X"]["Offset"]
                need = cur
                if kind == "touch" and pb.k > 0:
                    need = max(cur, (TOUCH_MIN / pb.k - min(bw, bh)) / 2, 0)
                hx, hy = pb.x - need * pb.k, pb.y - need * pb.k
                hw, hh = (bw + 2 * need) * pb.k, (bh + 2 * need) * pb.k
                art = (pb.x, pb.y, pb.x + pb.w, pb.y + pb.h)
                target = min(hw, hh)
                kitpad = True
            else:
                hx, hy, hw, hh = b.x, b.y, b.w, b.h
                art = (b.x, b.y, b.x + b.w, b.y + b.h)
                target = min(hw, hh)
                kitpad = False
            res["touch"].append({"path": b.path, "hit": [round(v, 1) for v in (hx, hy, hw, hh)],
                                 "art": [round(v, 1) for v in art], "min": round(target, 1), "kitpad": kitpad,
                                 "artmin": round(min(art[2] - art[0], art[3] - art[1]), 1),
                                 "z": n.props.get("ZIndex", 1)})
    # pad conflicts: a hit area that covers more than 25 % of a neighbour's art
    if kind == "touch":
        T = res["touch"]
        for a in T:
            ax0, ay0, aw, ah = a["hit"]
            for c in T:
                if a is c or c["path"].startswith(a["path"].rsplit("/", 1)[0] + "/Hit") and a["path"] == c["path"]:
                    continue
                pa, pc = a["path"].rsplit("/", 1)[0], c["path"].rsplit("/", 1)[0]
                if pa == pc or pa.startswith(pc + "/") or pc.startswith(pa + "/"):
                    continue
                cx0, cy0, cx1, cy1 = c["art"]
                ix = max(0, min(ax0 + aw, cx1) - max(ax0, cx0))
                iy = max(0, min(ay0 + ah, cy1) - max(ay0, cy0))
                area = (cx1 - cx0) * (cy1 - cy0)
                if area > 0 and ix * iy / area > 0.25:
                    res["pads"].append({"pad": a["path"], "covers": c["path"], "share": round(ix * iy / area, 2)})
    res["qa"] = qa
    return res, boxes


def overlay(img_path, res, profile, out_path):
    W, H, kind, _ = PROFILES[profile]
    im = Image.open(img_path).convert("RGBA")
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rectangle([0, 0, W, TOP_BAR], fill=(255, 0, 0, 40))
    d.rectangle([0, 0, UNIBAR_W, TOP_BAR], outline=(255, 0, 0, 200), width=2)
    if kind == "touch":
        for t in res["touch"]:
            x, y, w, h = t["hit"]
            col = (0, 160, 255, 160) if t["min"] >= TOUCH_MIN - 0.5 else (255, 0, 255, 230)
            d.rectangle([x, y, x + w, y + h], outline=col, width=1)
    for t in res["texts"]:
        if t["status"] in ("overflow-h", "overflow-v", "scaled-nofit") or (kind == "touch" and t["px"] < PHONE_MIN_TEXT):
            x, y, w, h = t["box"]
            d.rectangle([x, y, x + w, y + h], outline=(255, 140, 0, 255), width=2)
    for o in res["offscreen"]:
        x0, y0, x1, y1 = o["box"]
        d.rectangle([x0, y0, x1, y1], outline=(255, 0, 0, 255), width=3)
    Image.alpha_composite(im, lay).save(out_path)


def summarise(res, profile):
    W, H, kind, _ = PROFILES[profile]
    texts = res["texts"]
    small = sorted([t for t in texts if t["px"] < PHONE_MIN_TEXT], key=lambda t: t["px"])
    bad_touch = [t for t in res["touch"] if t["min"] < TOUCH_MIN - 0.5] if kind == "touch" else []
    qa = res["qa"][-1] if res["qa"] else None
    gp = None
    if qa:
        btn = qa["buttons"]
        gp = {"buttons": len(btn), "unselectable": [b["path"] for b in btn if b["interactable"] and not b["selectable"]],
              "with_nav": sum(1 for b in btn if b["nav"]), "selected": qa.get("selected"), "extra": qa.get("extra")}
    return {
        "min_text_px": min((t["px"] for t in texts), default=None),
        "median_text_px": sorted(t["px"] for t in texts)[len(texts) // 2] if texts else None,
        "small_text": small[:40],
        "overflow": [t for t in texts if t["status"] in ("overflow-h", "overflow-v", "scaled-nofit")],
        "truncated": [t for t in texts if t["status"] == "truncated"],
        "offscreen": res["offscreen"],
        "topbar": res["topbar"],
        "touch_small": bad_touch,
        "pad_conflicts": res["pads"],
        "gamepad": gp,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scenes", nargs="*")
    ap.add_argument("--profiles", nargs="*", default=DEFAULT_PROFILES)
    args = ap.parse_args()
    scenes = [HERE / "scenes" / f"{s}.luau" for s in args.scenes] if args.scenes else sorted((HERE / "scenes").glob("*.luau"))
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    summary_path = OUT_DATA / "summary.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    for scene in scenes:
        for profile in args.profiles:
            dumps, qas, logs = run(scene, profile)
            key = f"{scene.stem}__{profile}"
            if dumps is None:
                print(f"[{key}] FAILED\n  " + "\n  ".join(logs[-15:]))
                summary[key] = {"error": logs[-15:]}
                continue
            pages = []
            for i, tree in enumerate(dumps):
                suffix = "" if i == 0 else f"_p{i + 1}"
                cap = OUT_CAP / scene.stem / f"{profile}{suffix}.png"
                cap.parent.mkdir(parents=True, exist_ok=True)
                render.render(tree, cap)
                qa_for_page = [qas[i]] if i < len(qas) else []
                res, _ = analyse(tree, qa_for_page, profile)
                overlay(cap, res, profile, cap.with_name(cap.stem + "_qa.png"))
                s = summarise(res, profile)
                s["capture"] = str(cap.relative_to(ROOT))
                pages.append(s)
                (OUT_DATA / f"{key}{suffix}.json").write_text(json.dumps(res, indent=1))
            summary[key] = {"pages": pages, "log": [l for l in logs if l.strip()][-12:]}
            p0 = pages[0]
            print(f"[{key}] min text {p0['min_text_px']} px, overflow {len(p0['overflow'])}, trunc {len(p0['truncated'])}, "
                  f"off {len(p0['offscreen'])}, topbar {len(p0['topbar'])}, touch<44 {len(p0['touch_small'])}, "
                  f"pads {len(p0['pad_conflicts'])}, pages {len(pages)}")
    summary_path.write_text(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
