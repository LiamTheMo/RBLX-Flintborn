"""Ask a live place whether it can load the uploaded UI images.

Runs one read-only Open Cloud Luau task in the place (nothing is saved): it
reports the experience's owner and, for a sample of sprites from
src/shared/UI/UiAssetIds.json (or the names given), whether the engine can load
each image there (AssetService:CreateEditableImageAsync answers with the same
permission and moderation checks a client's ImageLabel meets). Used by
.github/workflows/probe-ui-assets.yml on main.

    ROBLOX_API_KEY=... ROBLOX_UNIVERSE_ID=... ROBLOX_PLACE_ID=... \\
        python3 scripts/roblox_probe_ui_assets.py [--names a,b,c]
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from roblox_live_publish import Cloud  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
IDS = ROOT / "src" / "shared" / "UI" / "UiAssetIds.json"
DECALS = ROOT / "art" / "ui" / "uploaded_decals.json"
# A spread of old and new sprites: the first HUD upload, the lobby, a menu
# window, the in-world HUD and the one uploaded as an Image.
SAMPLE = ["button_add_friend", "frame_slot", "pm_panel", "pm_lobby_enter", "pm_frame_window",
          "pm_hud_slot", "pm_map_pin"]

PROBE = """
local AssetService = game:GetService("AssetService")
local lines = { ("place %d universe %d creator %s %d"):format(game.PlaceId, game.GameId,
	tostring(game.CreatorType), game.CreatorId) }
for _, entry in ENTRIES do
	local ok, result = pcall(function()
		local image = AssetService:CreateEditableImageAsync(Content.fromAssetId(entry[2]))
		local size = image.Size
		image:Destroy()
		return ("%dx%d"):format(size.X, size.Y)
	end)
	-- What Roblox says the asset is, from inside the experience.
	local infoOk, info = pcall(function()
		return game:GetService("MarketplaceService"):GetProductInfo(entry[2], Enum.InfoType.Asset)
	end)
	local about = if infoOk and type(info) == "table"
		then ("type %s creator %s %s"):format(
			tostring(info.AssetTypeId),
			tostring(info.Creator and info.Creator.CreatorType),
			tostring(info.Creator and info.Creator.CreatorTargetId)
		)
		else "info unavailable: " .. tostring(info)
	table.insert(lines, ("%s %d %s %s (%s)"):format(entry[1], entry[2], if ok then "LOADS" else "FAILS", tostring(result), about))
end
return table.concat(lines, "\\n")
"""


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--names", default="", help="comma-separated sprite names (default: a sample)")
    args = parser.parse_args(argv)
    ids = json.loads(IDS.read_text(encoding="utf-8"))
    decals = json.loads(DECALS.read_text(encoding="utf-8"))
    names = [n.strip() for n in args.names.split(",") if n.strip()] or SAMPLE
    entries = []
    for name in names:
        if name in ids:
            entries.append((name, int(ids[name])))
    # A decal id is not an image: it should fail, which shows the probe can tell.
    if "pm_panel" in decals:
        entries.append(("pm_panel(decal)", int(decals["pm_panel"])))
    table = "{" + ", ".join('{"%s", %d}' % (name, asset) for name, asset in entries) + "}"
    result = Cloud().task(PROBE.replace("ENTRIES", table, 1))
    for value in (result.get("output") or {}).get("results", []):
        print(value)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, OSError, KeyError) as error:
        print("SAFE STOP: " + str(error), file=sys.stderr)
        sys.exit(1)
