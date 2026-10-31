Code review (independent): PASS, no High.
M1 PartyController.luau:92 + LobbyController.luau:145-155 status + LobbyHudController.luau:90-96 => double toast on failed party action. Fix: quiet path in typed wrappers when new HUD active.
M2 Ready/invite answer state in 3 places (PartyController:133 pending+timeout, PlayController:295 toggles stale view, LobbyHudController:132 accept/decline no busy) -> centralise pending state in LobbyController.
M3 PartyService.luau:74-79,208 broadcasts every action to all players incl no-ops; PartyWindow.luau:578 full rebuild on every change/Level change/search keystroke. Fix: skip unchanged ready, send ready changes to party members only; update rows in place.
M4 x20 open/close leak checks missing for inventory, forge, crafting, settings, trade, map, progress, market; only instance counts not connections.
L1 scripts/roblox_live_publish.py:28 retired list lacks removed modules (Parchment, LobbyHud, LobbyPopups, CraftingPanel, InventoryPanel, ItemSlot, JournalPanel, SettingsPanel) -> dead scripts stay in places.
L2 ~200 dead lines in Hud/Widgets.luau (Panel, Text, Bar, SelectionRing, Pin, SetBar, Fill/Frame).
L3 stale mentions: Hud/Layout.luau:6, docs/ui/*Screen.md; ForgeScreen.md:214 says no server qty support.
L4 Kit Ring/Toggle/TextField/Debug used only by gallery.
L5 Reasons lacks TooFast, PlayerNotHere, Rejected.
L6 ForgeRules.MaxCount ignores backpack room -> stepper offers batches that fail BackpackFull.
L7 forge batch counts as one action for analytics/tutorial/quests.
L8 ForgeController.luau:68-92 error after request leaves window busy forever (suspected).
L9 LobbyHudController.start partial failure leaves signals bound to destroyed HUD.
L10 inconsistent cleanup (only JournalWindow uses Maid; PlayWindow:SetParty destroys raw instances).
L12 selene not installed/in CI.
L13 (pre-existing) Take buttons for corpse/chest lack in-flight guard; index-based take may take next item on double press.
I1 51 pre-existing tracked files mention the assistant/vendor (CLAUDE.md, .claude/skills/, WorldModeling.md, art/blender/kit/*) - outside diff.
