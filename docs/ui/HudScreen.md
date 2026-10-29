# In-world HUD (parchment) spec

Reference: `art/reference/ui/parchment/12_hud_master.png` at its own 1672 × 941
px, which is the layout's reference size (`src/shared/UI/HudLayout.json`; the
HUD's UIScale fits it to the screen). Status: Built. Hotbar: six slots (GDD §56).

| Element | Place (anchor, offset) | Art |
|---|---|---|
| Compass | top centre, y 34, 481 × 40 | `pm_hud_compass` (the strip with its marks erased); ink letters and ticks scroll over it, waypoint icons below |
| Vitals | top right, 30 in, y 34; rows every 63 px | `pm_hud_health` / `pm_hud_stamina` / `pm_hud_food`: icon plate and empty bar in one piece; the coloured fill (x 70, 247 × 19) and the number are drawn over it |
| Status | top right, y 222, 334 × 32 | `pm_stat_chip`: medicine lock, food healing, hunger slow |
| Objective | top right, y 262, 334 × 112 | `pm_hud_card` (its placeholder rows erased), leather diamond and runner, two task rows |
| World event | top right, y 384, 334 × 98 | `pm_hud_card` |
| Party | top left, rows every 76 px, 276 × 70 | `pm_hud_card`, headshot, ink name, health bar |
| Backpack | left, (43, 308), 134 × 131 | `pm_tile_inventory`; opens the run backpack |
| Menu | left, (43, 452), 134 × 58 | `pm_button_paper` MENU; opens a row of CRAFT, BUILD, TRIBE, MAP, PROGRESS (150 × 58, every 160 px) in place of the old navigation bar |
| Level and XP | bottom centre, 37 up | `pm_stat_chip` "LV. n"; `pm_hud_xp` (star plate and empty track; fill x 42, 466 × 14) |
| Hotbar | under the XP bar, 123 × 120 every 140 px | `pm_hud_slot`, chosen `pm_hud_slot_selected`; key number, ink item name, count, rarity stripe |

Item icons: slots show the item's name until item icons exist.

Verification: `capture.py hud` (the HUD modules with the layout's preview values).
