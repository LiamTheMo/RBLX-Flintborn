# Market, Trade, Progress and World Map windows

These screens have no mockup of their own. They are built only from the UI kit
(`src/client/Hud/Kit`, [KIT.md](KIT.md); ARCHITECTURE §4.8 and D15), so they
look like the lobby windows: Inventory, Forge, Journal and Party. Market, Trade
and Progress share one list window (`Hud/ListWindow`). The world map is a kit
window around `Hud/IslandMap`. Status: Built.

Style references: `art/ui/captures/inventory_backpack.png` (frame, banner header,
category column) and `journal.png` / `forge.png` (soft cards, bars, check rings).

## List window (`Hud/ListWindow`)

The design size is 1180 × 690 px. The window is a `Kit.Screen`, so it is fitted
to the screen, opens and closes with the kit's motion, and Escape or gamepad B
closes the dialog first and then the window (`Kit.Modal`).

| Element | Bounds (x, y, w, h) | Kit |
|---|---|---|
| Frame and header | 0, 0, 1180, 690 | `Kit.Window` banner: header icon (76 px), title in `windowTitle`, ink rule, close ✕, right clasps |
| Currency pills (Market) | 794, 26, 140, 46 and 946, 26, 128, 46 | `Kit.CurrencyPill` coins / gems (`SetCurrencies`) |
| Category column | 24, 114, 232, 54 per tab, 64 px pitch | `Kit.Tab` "category" (icon at 16, label at 73, as the Inventory) in a `Kit.TabGroup`, hairline rules between rows |
| Column rule | 272, 110, 2, 508 | `Kit.Divider` hairline |
| Page | 288, 108, 868, 512 (no tabs: 24, 108, 1132, 512) | `Kit.Scroll`; rows fill its width less the rail |
| Status | page x, 632, page w, 34 | `Kit.Text` bodySoft; tones good (`toggleOn`) / warn (`short`) |

Page items, added between `Begin()` and `Finish()`:

| Call | Draws |
|---|---|
| `Section(text, icon?)` | `Kit.SectionHeader` (capitals, optional icon, ink rule) |
| `Line(text, tone?, size?)` | wrapping `Kit.Text` body; tones ink / soft / good / warn / gold. Returns the label (Trade's countdown rewrites it) |
| `Row(spec)` | a soft card (`Kit.Panel` inset, the mockups' soft-card art), at least 84 px tall and growing with its wrapped detail: item art (`Kit.ItemIcon` from `icon` = catalog id) or a `glyph` icon, title, detail, an optional `bar` (`Kit.Bar` on its track: `{value, fill}`), a `value` with a `coin` / `gem` icon, `Kit.Button` "s" buttons (leather; `kind = "paper"` for parchment), and a `Kit.Checkbox` ring (`done = true` ticked, `false` with no buttons empty) |
| `Player(spec)` | `Kit.PlayerRow` (portrait, name, level, action button), as the Party window's invite list |
| `Buttons(specs)` | a right-aligned row of `Kit.Button` "s" buttons |
| `Input(label, placeholder, onSubmit, always?, submit?)` | label, a text field on the `field.value` plate (`Kit.Picture`) and an optional submit button |
| `Pair(left, right)` | two `Kit.Panel` inset offer panels with a section header, a lock `Kit.Badge` (Not locked / Locked / Confirmed), `Kit.Slot` items with their names under them, and a gems `Kit.CurrencyPill` |
| `Confirm(text, yes, delay, onYes, opts?)` | `Kit.ConfirmDialog` over the window. `delay` > 0 makes Confirm a press-and-hold of that many seconds. `opts.rows` gives labelled paragraphs, plus `opts.title` and `opts.size` |

Row heights come from design numbers (`ListWindow.Lines` wraps by measured word
widths), never from `AbsoluteSize`. After a redraw, `Finish` gives gamepad focus
back to the same button (row key and button key), else to the first enabled
button, else to the close button.

| Screen | Controller | Tabs (icons) | Contents |
|---|---|---|---|
| Market (lobby) | `WalletController` (`Open(tab)`, `Toggle()`) | Shop (market), Sell (coin), Offers (gem), Codes (gift) | Coins and Gems pills in the header. Stock by category with item art, price and Buy, which asks in a dialog first. Owned titles show a ticked ring. Backpack and vault sales: Sell, Sell 10, Sell All (never for a Forge reagent). Vault upgrade (asks first), perk respec (asks first) and Robux offers with their earnable route (MarketplaceService prompt unchanged). Code field with Enter or Redeem. |
| Progress | `ProgressionController` (`Toggle()`, `View()`, `Changed`, `MountPopups`) | Overview (trophy), Perks (star), Rebirth (totem), Titles (crown) | Level card with the XP bar. Mastery cards with green bars (track icons from `JournalModel.TRACK_ICONS`) and a ring when mastered. Perk cards with rank bars, a token price and Buy (asks first). Rebirth requirements with rings, then Review Rebirth: Reset / Kept / Gained in a dialog, confirmed by holding Rebirth for 1.5 s. Titles. Perks and Rebirth are lobby-only. |
| Trade (lobby) | `TradeController` (`Toggle()`) | — | Lobby players as player rows with Invite. During a trade the title names the partner, and You give / You get show as slot panels with their lock badges and gems. Below them: the countdown, Cancel / Lock Offer / Confirm (Confirm asks with both offers spelled out), the Gems field, backpack items (Add / Remove) and tradeable vault materials (Remove, All, +10, +1). An invite arrives as a `Kit.Toast` whose View opens Accept / Decline. |

The XP pop-ups are kit text (cream, gold for a level-up, ink outline) in the
host the HUD mounts. Where no HUD shows the level, the fallback is a `Kit.Bar`
XP track with the level text above it. Outside the new lobby HUD, the Market
keeps Coins and Gems pills at the top right.

## World map (`MapController`)

The map is a 1000 × 860 `Kit.Screen` with a `Kit.Window` banner (map icon, MAP,
close, right clasps). The painted island (`Hud/IslandMap`, as in the Journal's
map tab) sits in a `Kit.Panel` inset at 28, 104, 944, 680, with the map inside
it at 36, 112, 928, 664:

- **Zoom:** the kit's + / − buttons. Each one disables at its limit.
- **Compass:** at the map's top-left corner (north is up).
- **Pins:** safe camps and main landmarks. Press a pin for its name plate.
- **Live markers:** active portals (the `blue` token) and announced events (rarity colour), as tinted dots.
- **Your position:** the compass arrow, followed while zoomed in until you pan.
- **Legend:** under the panel (You, Camps and landmarks, Portals, Events).

An authored map hides the painting and the pins and keeps the live markers on
the bare panel. The safe-camp notice is still `Hud/NoticeCard` (W2's, now on the
kit). The legacy compass strip shows only without the new HUD.

## Captures

Run `python3 art/ui/capture/capture.py <scene>`. Each scene drives the real
controller with mocked remotes, prints its checks and ends with `FLOW OK`.

| Scene | Pages (`art/ui/captures/<scene>[_n].png`) |
|---|---|
| `market_flow` | 1 Shop, 2 Sell, 3 Offers, 4 Codes, 5 the Buy dialog, 6 forced states (hover, pressed, busy buttons; hovered tab), 7 phone 844 × 390 |
| `trade_flow` | 1 invite list, 2 invite toast, 3 running trade, 4 scrolled to your items, 5 both locked with the confirm dialog, 6 forced states, 7 phone |
| `progress_flow` | 1 Overview, 2 Perks, 3 Rebirth, 4 Titles, 5 the rebirth dialog, 6 forced states, 7 phone |
| `map_flow` | 1 the map, 2 zoomed with a pin chosen, 3 forced states, 4 phone |

Stock, offers and sale quotes in `market_flow` come from `ShopCatalog`,
`OfferCatalog` and `EconomyRules`.

These are checked in game, not in the captures, because time does not pass
there:

- the 1.5 s hold on Rebirth
- tween motion
- the background blur

## Kit requests

- A plain text field (`Kit.TextField`): the search box art has its magnifier
  baked in. The Codes and Gems fields use the `field.value` plate with a
  TextBox.
- `Kit.Toast` with two actions: the 430 px toast leaves the title about 90 px
  beside two buttons, so the trade invite uses one View action and a dialog.
- A partial ring (sheet 19): only the empty and full rings exist, so progress
  uses bars.
- A plain coloured map-marker dot: the tinted `dot.yellow` multiplies, so
  "blue" portals draw green.
- The trade payload names items but carries no catalog id for backpack items.
  The client resolves them by name; adding `catalogId` to
  `TradeService.describe` would make this exact (server owner).
