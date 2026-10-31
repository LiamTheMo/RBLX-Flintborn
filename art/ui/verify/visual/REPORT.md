# Visual Verifier — all screens — round 1
Result: FAIL (2 High, 13 Medium, 12 Low). Viewport 1672×941 (phone 844×390, wide 2560×1080).
Positions: frames, tabs, grids, buttons and rules within ±2 px everywhere except the last inventory slot right edge (3 px) and the Play window bottom border (1–5 px).

| Screen | mean ΔE | SSIM | Verdict |
|---|---|---|---|
| 01 HUD | 1.66 | 0.938 | FAIL (#1, #11, #13) |
| 02 Inventory | 7.14 | 0.896 | PASS (Low notes) |
| 03 Settings | 5.83 | 0.933 | FAIL (#3, #15) |
| 04 Party | 6.12 | 0.943 | FAIL (#11, #15) |
| 05 Play | 9.24 | 0.881 | FAIL (#14) |
| 06 Forge | 6.85 | 0.901 | FAIL (#1, #2, #8, #11) |
| 07 Journal | 7.20 | 0.899 | FAIL (#6) |
| No-mockup screens | – | – | FAIL (#1, #4, #5, #10, #12) |

| # | Finding | Sev | Owner |
|---|---|---|---|
| 1 | Items without art (bows) print their name inside slots (HUD/world hotbar, vault, forge list) | High | ItemInfo / missing art |
| 2 | Iron armour reads as hide, Iron Sword as a tusk (also the big forge picture) | High | ItemInfo / missing art |
| 3 | Settings Gameplay duplicates Music/Effects volume from Audio | Med | SettingsWindow |
| 4 | World menu shows raw reason code "(NotReady)" | Med | Ui/Reasons |
| 5 | World Event panel wraps "312 m" leaving a lone "m" touching the frame | Med | EventPanel |
| 6 | Journal reward count "x250" drawn over the coin icon (desktop + phone) | Med | JournalWindow |
| 7 | Journal phone: 3rd description line runs into the OBJECTIVES rule | Med | JournalWindow |
| 8 | Forge Permanent recipes clipped to "Permanent Woode"; subtitles "time(s), extra…" | Med | RecipeWindow |
| 9 | Party phone: "Invited" truncated to "Invit…" | Med | PartyWindow |
| 10 | Storage chest / body loot rows lack item icons (Carried rows have them) | Med | ListWindow / LootController |
| 11 | Flat fills off: HUD card ΔE 4.8–5.1, currency pill 7.4, empty XP track greyish (9.3), leather buttons too bright (5.5–10) | Med | Kit tokens / lk_ sprites |
| 12 | Toasts cover window titles while a window is open | Med | Kit Toast / TopStack |
| 13 | HUD party panel: leader name shrinks to ~11 px with 3 members | Med | LobbyHud / PlayerRow |
| 14 | Play map lacks a paper frame/margin; schematic look; rune glyph faint | Med | PlayWindow / IslandMap |
| 15 | Misleading stand-in icons: Audio=speech bubble, Gameplay=compass, Graphics=map, RESET=rune, Party Details "!" reads as warning | Med | SettingsWindow / PartyWindow |
| 16–27 | Low: Ready tag lacks green fill; colour campfire/trees vs ink sketches; inventory "All" chest icon, heavier tab/search outlines; "Max level · rebirth in the lobby" overruns the hotbar and card shows MAX; hover = selected look and gamepad focus = hover; "item(s)/tribe(s)/time(s)" wording; Play footnotes touch frame; scroll lists cut a row through its text; compass label clipped "SI"; old-style digits and →/★ boxes at small sizes; trade scene lacks catalogId; map labels hard to read | Low | various |

Not checked: blur and motion (harness), real font rendering and glyph fallback (Studio), real device safe areas and touch.
