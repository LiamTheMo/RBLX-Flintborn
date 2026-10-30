# Lobby UI references

The source of truth for the lobby UI rebuild. Every screen is a full-screen
mockup at the design resolution of 1672 × 941. These replace the earlier
parchment reference sheets, which have been removed.

| File | Screen |
|---|---|
| `01_hud.png` | Lobby HUD: player card, currencies, settings button, menu grid, party panel, XP bar, six-slot hotbar |
| `02_inventory.png` | Inventory (Backpack / Vault tabs, category list, item grid, item details, Equip) |
| `03_settings.png` | Settings (Gameplay / Audio / Graphics / Controls tabs, sliders, toggles, language, key binds, Reset / Apply) |
| `04_party.png` | Party (your party, invite players, party details, readied status) |
| `05_play.png` | Play (island map, region details, your party, your equipment, Play) |
| `06_forge.png` | Ancestral Forge (recipes, selected recipe, requirements, quantity, your materials, Forge) |
| `07_quest_journal.png` | Quest Journal (side tabs, quest list, quest details, objectives, rewards, Claim, quest progress) |

## Kit sheets (`kit/`)

The parts the screens are built from, on transparent backgrounds. Slice
assets from these. Use the screen mockups above for layout and size.

| File | Contents |
|---|---|
| `01_panel_layouts.png` | Panels with list, two-column, three-column, header, list + cards and checklist layouts; small buttons, status dots, plaques, slot frames, round frames, a portrait plaque, a six-slot row |
| `02_hollow_frames_hud_buttons.png` | Hollow window frames, a speech frame, plaques and an arrow tab, square HUD buttons (close, play, backpack, chest, coin, gem, gear), a numbered hotbar, item tiles, corner pieces, horizontal and vertical rails |
| `03_buttons_states.png` | Wide leather and parchment buttons and the close button, each in normal, hover, pressed and disabled states; square glyph buttons (+ − ✓ ✕ arrows); round frame; notched plaques; Play and Confirm buttons; small parchment buttons in three states |
| `04_window_frames.png` | Solid parchment windows in six sizes, some with side clasps |
| `05_slots_badges_bars.png` | Item slot in normal, selected, hover, disabled and locked states; number badges 1–6; count badges; numbered hotbar slots; XP bar fill and track; a small plaque |
| `06_menu_icons.png` | Menu icons (backpack, portal, scroll, market, anvil, trade, gear), invite-player card, coin, gem, crown |
| `07_hud_parts.png` | Lobby HUD parts on their own: player card, currencies, settings button, party panel, 3 × 2 menu grid, XP bar, hotbar |
| `08_stat_bars.png` | Health, stamina, food and XP icons, plaques, fills and composed bars; small bars; value plaques; small tiles; warning icon |
| `09_controls.png` | Search box, dropdowns, button plaques in three states, list rows in three states, checkboxes, toggles, slider track and knob, scrollbar, number steppers, key caps, tooltip boxes, divider |
| `10_inventory_parts.png` | Inventory window, slot normal and selected, Backpack and Vault tabs in both states, search box, category tab, item detail cards, scrollbar, count tag, material icons, leather button |
| `11_icons_extra.png` | 20 icons: backpack, portal, scroll, market, anvil, trade, gear, party, map, trophy, mail, chest, hammer, torch, compass, house, rune stone, exit door, journal book, magnifier |
| `12_quest_forge_parts.png` | Quest objective rows with Claim, forge recipe card with requirement checks, bars, Claim and Forge buttons, check rows, frames, tool icons, material tiles, check tiles |
| `13_popups_notices.png` | Confirm dialog, empty dialog, Quest Complete and Item Received toasts, tooltip boxes with tails, count-badged frames, status dots, lock, warning, check, cross, cursor |
| `14_ornaments.png` | Corner pieces, clasps, folded corner, round and octagonal frames, rivets and spikes, rope knots, leather and parchment strips, dividers, list rows, leaf and rune emblems, plaques and arrow tabs |
| `15_play_party_parts.png` | Play window with map, party list and hotbar; party window; portal; backpack button; frame; crown; invite button; search and player rows; plain map |
| `16_icons_status_items.png` | 20 icons: heart, lightning, drumstick, star, crown, exclamation, warning, check, cross, hourglass, clock, scroll, gift, backpack, stone axe, log, stone, plant fiber, up arrow, speech bubble |
| `17_icons_world.png` | 20 world icons: mountain, tree, cave, campfire, ruin arch, rocks, crystals, magma ore, berry bush, anvil, totem, rune stone, treasure chest, paw, tusk, map pin, compass arrow, rope bridge, wave, hut |
| `18_stat_bars_states.png` | Health, stamina, food and XP bars at 0, 50 and 100 %; empty and plain bar frames; the four fills |
| `19_progress_bars_badges.png` | Progress bars (XP, plant, wood timer, trade), empty bar, five fill colours, ring progress at 0/50/100 %, framed status tiles (check, hourglass, clock, flag, build, search) |
| `20_stat_bars_widths.png` | Health, stamina, food and XP bars at three widths; framed stat icon tiles |

These sheets came from background removal. Two consequences for slicing:
- Fills sit at alpha 250–254 rather than 255.
- Most parts carry a faint red or yellow fringe at low alpha (about 1–63).

Clean both up when slicing so the parts don't draw see-through or with halos.

More references are coming. Add each one here with the next number.
