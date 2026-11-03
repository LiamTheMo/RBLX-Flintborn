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
# A spread of what the game draws: the lobby and window kit, the icons, the
# island map, both item icon atlases and one item's hero picture.
SAMPLE = ["atlas_lk_lobby", "atlas_lk_window", "atlas_lk_icons", "atlas_island", "atlas_lk_items2_1",
          "atlas_lk_items2_2", "lk_item_Wood__hi"]

PROBE = """
local AssetService = game:GetService("AssetService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local lines = { ("place %d universe %d creator %s %d"):format(game.PlaceId, game.GameId,
	tostring(game.CreatorType), game.CreatorId) }
-- What the game's own code will see here: the place role, the asset ids and
-- sprite data it loads, and the client modules that draw the UI.
local function try(label, fn)
	local ok, result = pcall(fn)
	table.insert(lines, label .. ": " .. (if ok then tostring(result) else "ERROR " .. tostring(result)))
end
local Shared = ReplicatedStorage:FindFirstChild("Shared")
try("place role", function()
	return require(Shared.Config.PlaceConfig).Role()
end)
try("generated place ids", function()
	local ids = require(Shared.Generated.PlaceIds)
	return ("lobby %s world %s"):format(tostring(ids.lobby), tostring(ids.world))
end)
try("ui assets", function()
	local UiAssets = require(Shared.UI.UiAssets)
	local count = 0
	for _ in UiAssets.Ids do
		count += 1
	end
	local wood = UiAssets.sprite("lk_item_Wood")
	return ("%d ids; atlas_lk_lobby %s; lk_item_Wood in %s %s; its hero %s"):format(count,
		tostring(UiAssets.image("atlas_lk_lobby")), tostring(wood and wood.atlas),
		tostring(wood and UiAssets.image(wood.atlas)), tostring(UiAssets.image("lk_item_Wood__hi")))
end)
try("kit tokens", function()
	local tokens = require(Shared.UI.KitTokens)
	local colors = 0
	for _ in tokens.colors or {} do
		colors += 1
	end
	return ("%d colors; reference %s x %s"):format(colors, tostring(tokens.reference and tokens.reference.width),
		tostring(tokens.reference and tokens.reference.height))
end)
try("client modules", function()
	local client = game:GetService("StarterPlayer").StarterPlayerScripts:FindFirstChild("Client")
	local found = {}
	for _, path in { "Hud/Kit", "Hud/Kit/Art", "Hud/Kit/Tokens", "Hud/Kit/Screen", "Hud/Kit/Window",
		"Hud/Screens/LobbyHud", "Hud/Screens/InventoryWindow", "Hud/Screens/SettingsWindow",
		"Hud/Screens/PartyWindow", "Hud/Screens/PlayWindow", "Hud/Screens/RecipeWindow",
		"Hud/Screens/JournalWindow", "Hud/Widgets", "Hud/SpriteLoader", "Hud/ListWindow",
		"Controllers/LobbyHudController", "Controllers/HudController" } do
		local node = client
		for part in string.gmatch(path, "[^/]+") do
			node = node and node:FindFirstChild(part)
		end
		table.insert(found, path .. "=" .. (if node then tostring(#node.Source) else "MISSING"))
	end
	return table.concat(found, " ")
end)
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


# The latest device reports UiDiagnosticsService kept (how HUD images loaded on
# real clients).
REPORTS = """
local store = game:GetService("DataStoreService"):GetDataStore("FlintbornDiagnostics")
local list = store:GetAsync("uiimages:latest")
if type(list) ~= "table" or #list == 0 then
	return "no device reports yet"
end
local lines = {}
for _, entry in list do
	table.insert(lines, ("%s user %s server %s: %s"):format(os.date("!%Y-%m-%d %H:%M:%S", entry.at),
		tostring(entry.user), string.sub(tostring(entry.server), 1, 8), entry.summary))
	for _, line in entry.lines or {} do
		table.insert(lines, "    " .. line)
	end
end
return table.concat(lines, string.char(10))
"""


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--names", default="", help="comma-separated sprite names (default: a sample)")
    parser.add_argument("--reports", action="store_true", help="print the latest device image reports instead")
    args = parser.parse_args(argv)
    if args.reports:
        result = Cloud().task(REPORTS)
        for value in (result.get("output") or {}).get("results", []):
            print(value)
        return 0
    ids = json.loads(IDS.read_text(encoding="utf-8"))
    decals = json.loads(DECALS.read_text(encoding="utf-8"))
    names = [n.strip() for n in args.names.split(",") if n.strip()] or SAMPLE
    entries = []
    for name in names:
        # An empty id is a placeholder for an atlas not uploaded yet.
        if str(ids.get(name) or "").isdigit():
            entries.append((name, int(ids[name])))
    # A decal id is not an image: it should fail, which shows the probe can tell.
    if "atlas_lk_lobby" in decals:
        entries.append(("atlas_lk_lobby(decal)", int(decals["atlas_lk_lobby"])))
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
