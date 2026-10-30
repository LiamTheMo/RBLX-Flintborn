#!/usr/bin/env bash
# Re-runs the measurements behind docs/ui/InventoryScreen.md and
# docs/ui/SettingsScreen.md and writes them to measurements.txt in
# art/ui/kit/analysis/inventory/ and art/ui/kit/analysis/settings/.
# Run from the repository root:  bash art/ui/kit/analysis/inventory/tools/measure_inventory_settings.sh
# Needs python3 with Pillow and numpy.
set -u
T=art/ui/kit/analysis/inventory/tools
L=art/reference/ui/lobby
INV=$L/02_inventory.png
SET=$L/03_settings.png
py() { python3 "$T/$1" "${@:2}" < /dev/null; }

{
echo "## Dim overlay (02/03 vs 01_hud): per-channel fit out = k*hud + c on background-only regions"
py dimch.py
echo; echo "## Dim factor map (80 px tiles)"; py dimmap.py
echo; echo "## Background blur test (best Gaussian sigma)"; py blur.py
} > art/ui/kit/analysis/inventory/dim_overlay.txt 2>&1

{
echo "## Window outline (outer dark run)"
py px.py $INV row 500 236 260; py px.py $INV row 500 1415 1432
py px.py $INV col 700 145 160; py px.py $INV col 700 790 806
echo; echo "## Header, tabs, underline, close"
py edges.py $INV row 270 240 1435 110; py edges.py $INV col 270 150 800 110; py edges.py $INV col 600 150 800 110
py edges.py $INV row 235 240 1430 120
py edges.py $INV row 172 1330 1420 90; py edges.py $INV col 1400 155 240 90
echo; echo "## Search box, All tab, category rules"
py edges.py $INV row 360 250 495 200; py edges.py $INV col 450 320 380 200
py edges.py $INV col 275 320 790 150
for y in 504 569 633 697; do py edges.py $INV row $y 250 490 208; done
echo; echo "## Item grid"
py edges.py $INV row 660 480 1100 120; py edges.py $INV col 1080 320 760 120
py px.py $INV row 380 484 502; py px.py $INV col 540 323 340
echo; echo "## Detail card, divider, stat rules, EQUIP"
py px.py $INV row 450 1090 1122; py px.py $INV row 450 1398 1430
py px.py $INV col 1200 250 272; py px.py $INV col 1200 768 798
py edges.py $INV col 1095 240 800 205; py edges.py $INV col 1320 555 705 210
py edges.py $INV row 718 1110 1410 90; py edges.py $INV col 1150 690 790 90
echo; echo "## Icons and labels (bbox vs parchment)"
py obj.py $INV 80 bigIcon:1125,268,270,205 iconAll:276,392,50,44 iconTools:276,450,50,50 iconMat:276,515,50,50 iconFood:276,578,50,50 iconPlants:276,642,50,50 iconMisc:276,705,50,52 statIc1:1135,580,40,30 statIc2:1135,620,40,30 statIc3:1135,658,40,32 searchIc:270,333,40,34
echo; echo "## Text ink rows (cap heights)"
py ink.py $INV 375,175,300,55 90; py ink.py $INV 383,180,16,45 90
py ink.py $INV 1120,470,285,100 110; py ink.py $INV 1128,512,260,46 170; py ink.py $INV 1120,575,280,115 110
py ink.py $INV 326,275,16,28 200 light; py ink.py $INV 519,275,16,28 90; py ink.py $INV 1223,725,16,30 200 light
py ink.py $INV 338,400,18,28 110; py ink.py $INV 338,458,14,30 110; py ink.py $INV 305,335,170,28 175
py ink.py $INV 650,398,30,28 80; py ink.py $INV 545,505,35,28 80
echo; echo "## Colours (flat medians)"
py col.py $INV parch:700,245,300,8 parch_mid:1100,300,8,150 tabBP_fill:310,262,110,8 tabV_fill:580,270,15,35 search_fill:410,340,60,20 all_fill:370,392,90,12 rule:330,504,140,1 slot_fill:1000,665,75,75 slot_out:592,360,1,40 det_fill:1150,700,20,5 statrule:1140,612,240,1 equip_fill:1160,715,200,10 divider:1095,300,2,400 underline:500,235,600,2
echo; echo "## Colours (glyph cores)"
py ink2.py $INV title:383,186,275,31 tabBP_lbl:328,279,82,20:light tabV_lbl:521,279,46,15 search_ph:310,343,100,12 cat_lbl:340,465,45,15 count:556,514,20,15 name:1132,481,131,21 desc:1131,516,236,17 statlbl:1180,587,100,15 statval:1355,587,30,15 equipTxt:1225,730,71,21:light closeX:1360,180,35,35:light statIcon:1143,583,23,23
} > art/ui/kit/analysis/inventory/measurements.txt 2>&1

{
echo "## Window outline"
py px.py $SET row 450 280 300; py px.py $SET row 450 1370 1392; py px.py $SET col 800 140 160; py px.py $SET col 800 790 812
echo; echo "## Header, close, underline"
py ink.py $SET 415,180,260,50 90; py ink.py $SET 325,160,90,80 90
py edges.py $SET row 237 290 1385 150; py edges.py $SET row 176 1290 1380 70; py edges.py $SET col 1310 160 235 70
echo; echo "## Tabs"
py edges.py $SET col 330 250 630 70; py edges.py $SET row 290 300 570 70; py edges.py $SET row 380 300 570 70
echo; echo "## Dividers and rules"
py edges.py $SET col 564 240 720 200; py edges.py $SET col 993 250 710 205; py edges.py $SET row 717 380 1360 160
py edges.py $SET row 298 580 1000 190; py edges.py $SET row 298 1010 1360 190; py edges.py $SET row 527 585 990 212
py edges.py $SET col 1150 300 680 212
echo; echo "## Section headers"
py ink.py $SET 585,260,150,30 90; py ink.py $SET 1015,260,150,30 90
echo; echo "## Sliders, value boxes"
for y in 357 426 494; do py edges.py $SET row $y 585 980 70; done
py edges.py $SET col 650 340 375 90; py edges.py $SET col 650 405 445 90; py edges.py $SET col 650 475 510 90
py edges.py $SET col 797 335 380 70; py edges.py $SET col 779 400 450 70; py edges.py $SET col 770 470 520 70
py edges.py $SET row 345 885 980 160; py edges.py $SET col 910 335 515 160
echo; echo "## Checkboxes, dropdown, key caps"
py edges.py $SET row 545 590 640 90; py edges.py $SET col 613 535 640 90; py edges.py $SET row 615 590 640 90
py edges.py $SET row 690 720 980 120; py edges.py $SET col 760 650 705 120
py edges.py $SET col 1242 300 680 150; py edges.py $SET row 325 1225 1345 130
echo; echo "## Buttons"
py edges.py $SET row 745 820 1360 70; py edges.py $SET col 880 720 800 70; py edges.py $SET col 1300 720 800 70
echo; echo "## Text ink rows"
py ink.py $SET 395,285,130,35 215 light; py ink.py $SET 400,378,90,35 90
py ink.py $SET 594,315,14,25 110; py ink.py $SET 649,538,14,22 110; py ink.py $SET 649,560,12,22 160
py ink.py $SET 1025,310,200,360 110; py ink.py $SET 1240,314,95,22 110; py ink.py $SET 900,345,65,25 110
py ink.py $SET 935,740,90,40 130; py ink.py $SET 1170,740,110,40 200 light
echo; echo "## Colours"
py col.py $SET parch:1100,690,200,15 parch_tabs:330,640,200,30 tabActive:470,268,60,10 tabInactive:480,365,50,20 track_fill:620,355,100,5 track_empty:830,355,40,5 knob:790,350,15,15 valbox_fill:905,350,15,15 valbox_out:897,350,2,15 chk_fill:603,547,8,6 dd_fill:860,665,60,25 dd_out:734,670,1,20 key_fill:1245,316,30,18 key_out:1237,316,1,20 divider:993,300,2,350 rule_left:600,527,350,1 bottom_rule:500,717,800,2 hdr_ul:600,298,240,1 keyrule:1120,415,80,1 reset_fill:960,737,60,8 apply_fill:1110,745,60,30
py ink2.py $SET title:420,188,234,34 gear:337,172,63,65 hdr:590,268,130,17 tabG:402,291,110,24:light tabA:408,384,65,18 lblCam:596,319,146,13 val:924,351,20,12 chkT:651,543,75,12 chkD:651,564,230,14 dd:753,669,59,19 chev:937,673,16,10 keyLbl:1031,318,105,13 keyTxt:1279,319,16,12 resetT:944,751,66,16 applyT:1179,750,75,17:light emblem:864,258,103,54 signpost:1222,247,127,57 plant:314,672,226,118 chkMark:600,544,28,28
} > art/ui/kit/analysis/settings/measurements.txt 2>&1

{
echo "## Kit part bounding boxes (alpha > 200, area >= 1500)"
for k in 02_hollow_frames_hud_buttons 03_buttons_states 04_window_frames 05_slots_badges_bars 09_controls 10_inventory_parts 14_ornaments; do
  echo "== $k"; py parts.py $L/kit/$k.png 1500
done
for k in 06_menu_icons 11_icons_extra 16_icons_status_items; do
  echo "== $k"; py parts.py $L/kit/$k.png 3000
done
} > art/ui/kit/analysis/inventory/kit_parts.txt 2>&1

echo "wrote inventory/measurements.txt, inventory/dim_overlay.txt, inventory/kit_parts.txt, settings/measurements.txt"
