"""Watch the kit workflow journals; print one line per finished agent and keep
art/reference/kit/CHECKLIST.md current.

  python kit_watch.py            # watch forever (Monitor)
  python kit_watch.py --once     # just rewrite the checklist
  python kit_watch.py --next 4   # print Workflow args for the next batch of sheets (JSON)
  python kit_watch.py --active   # print "running <runId>" or "idle"
"""
import glob
import json
import os
import re
import sys
import time

REPO = "D:/Projects/Roblox/RBLX-Flintborn"
# workflow journals from every orchestrator session of this project (history carries across sessions)
WF = "C:/Users/Orang/.claude/projects/D--Projects-Roblox-RBLX-Flintborn/*/subagents/workflows"
REF = f"{REPO}/art/reference/kit"
OUT = f"{REF}/CHECKLIST.md"
ACTIVE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kit_active.json")
WAVES = ["W01", "R01", "W02", "W03", "W04", "W05", "W06", "W07", "W08", "W09", "W10", "W11", "W12", "W13",
         "W14", "W15", "W16", "R02", "R03", "R04", "R05", "R06", "R07", "R08", "V01", "V02", "V03", "V04",
         "V05", "V06", "V07", "V08", "V09", "V10"]
# passed before a check that now rejects them (painted-in shading, 2026-10-25 22:20)
REVERIFY = set()  # W01/pebble_scatter re-passed under the colour rules on 2026-10-26
VFX_MESH = re.compile(r"(Curtain|Foam|Flow(?!er)|Splash|Mist|Smoke|Steam|Vapour|Spray)")  # not Flower

labels = {}   # agentId -> label
STOPS = []    # agents that failed since the last scan
RUN = {"id": ""}  # journal being scanned
# runs launched before the one-fix-round rule: their last check is reverify2
TWO_FIX_RUNS = {"wf_09e96fc7-7ef", "wf_b4845084-d68", "wf_f0f71fac-88d", "wf_5226fe6c-13d", "wf_f4f3bde9-cfd", "wf_4ba56d33-86b"}
state = {}    # "W01/boulder" -> dict(status, resemblance)
planned = {}  # sheet -> [modules]
offsets = {}
last_write = {}


def handle(rec, live):
    t = rec.get("type")
    if t == "started":
        lab = rec.get("label", "")
        labels[rec["agentId"]] = lab
        kind, _, tgt = lab.partition(":")
        if "/" in tgt:
            s = state.setdefault(tgt, {})
            s["status"] = "building" if kind in ("build", "rework") or kind.startswith("fix") else "verifying"
            s.pop("passed_ok", None)
        elif kind == "plan":
            state.setdefault(f"{tgt}/*", {})["status"] = "planning"
        return None
    lab = labels.get(rec.get("agentId"), "")
    kind, _, tgt = lab.partition(":")
    if t == "failed":
        if "/" in tgt:
            s = state.setdefault(tgt, {})
            s["status"] = "stopped-building" if s.get("status") == "building" else "stopped-verifying"
            if live:
                STOPS.append(tgt)  # summarised once per scan, not one line per agent
            return None
        if kind == "plan":
            state.setdefault(f"{tgt}/*", {})["status"] = "stopped"
        return None
    if t != "result":
        return None
    r = rec.get("result") or {}
    if kind == "plan" and isinstance(r, dict):
        planned[tgt] = [m.get("module") for m in r.get("models", [])]
        state.setdefault(f"{tgt}/*", {})["status"] = "planned"
        return None  # token budget: no photo/event for plans
    if "/" not in tgt or not isinstance(r, dict):
        return None
    s = state.setdefault(tgt, {})
    sheet, module = tgt.split("/")
    compare = f"{REPO}/art/blender/renders/kit/{sheet}/{module}_compare.png"
    if kind.startswith(("verify", "reverify")):
        s["resemblance"] = r.get("resemblance")
        goals = r.get("own_goals", [])
        s["must_unmet"] = sum(1 for g in goals if not g.get("met") and g.get("priority") == "must")
        if r.get("verdict") == "pass":
            s["status"] = "passed"
        else:
            last = "reverify2" if RUN["id"] in TWO_FIX_RUNS else "reverify1"
            s["status"] = "failed-final" if kind == last else "verify-failed"
        final = r.get("verdict") == "pass" or s["status"] == "failed-final"
        msg = (f"FINAL {tgt} {r.get('verdict')} {r.get('resemblance')}/10, "
               f"{s['must_unmet']} must-goals unmet | {compare}") if final else None
    else:
        unmet = sum(1 for g in r.get("goals", []) if not g.get("met"))
        s["status"] = "built"
        s["was_built"] = True
        msg = None  # token budget: builds are not reported, only final verdicts
    return msg if live else None


def journals():
    return sorted(glob.glob(f"{WF}/*/journal.jsonl"), key=os.path.getctime)  # oldest run first


def scan(live):
    events = []
    for j in journals():
        RUN["id"] = os.path.basename(os.path.dirname(j))
        pos = offsets.get(j, 0)
        with open(j, encoding="utf-8") as fh:
            fh.seek(pos)
            for line in fh:
                if not line.endswith("\n"):
                    break
                pos += len(line.encode("utf-8"))
                try:
                    m = handle(json.loads(line), live)
                except ValueError:
                    continue
                if m:
                    events.append(m)
        offsets[j] = pos
        last_write[j] = os.path.getmtime(j)
    return events


def subject_of(path):
    try:
        txt = open(path, encoding="utf-8").read()
    except OSError:
        return None
    m = re.search(r'^SUBJECT\s*=\s*"([^"]+)"', txt, re.M)
    return m.group(1) if m else None


ICON = {"passed": "✅", "failed-final": "⚠️", "verify-failed": "🔁", "verifying": "🔍", "built": "🔍",
        "building": "🔨", "rework": "🎨", "stopped-building": "⏸️", "stopped-verifying": "⏸️", "planning": "🗺️",
        "planned": "🗺️", "stopped": "⏸️"}


def sheet_ref(sid):
    return os.path.relpath(glob.glob(f"{REF}/{sid}_*.png")[0], REPO).replace("\\", "/")


def modules_of(sid):
    mods = glob.glob(f"{REPO}/art/blender/scripts/kit/{sid}/*.py")
    names = {os.path.splitext(os.path.basename(m))[0]: m for m in mods if not os.path.basename(m).startswith("_")}
    for mname in planned.get(sid, []):
        names.setdefault(mname, None)
    return names


def needs_rework(sid, mname):
    """True when the model's last build predates the one-colour-per-material check
    or still splits a material into lit/shadow shades or paints shading in."""
    p = f"{REPO}/art/blender/assets/kit/wip/{sid}_{mname}_stats.json"
    if not os.path.exists(p):
        return False  # never built: it gets a normal build
    try:
        d = json.load(open(p, encoding="utf-8"))
    except ValueError:
        return False
    mats = {m for a in d.get("assets", []) for m in (a.get("materials") or [])}
    if any("water" in m for m in mats) and not any("riverbed" in m for m in mats):
        return True  # water over a light bed reads pale: the bed under it needs the deep riverbed colour
    for a in d.get("assets", []):
        if VFX_MESH.search(a.get("name", "")):
            return True  # a mesh standing in for an effect: waterfalls, foam, mist, smoke are VFX now
        if "shade_pairs" not in a:
            return True
        if a["shade_pairs"] and not a.get("two_tone_ok"):
            return True
    return any("shades of one material" in x or "painted into the colours" in x or "Tint varies" in x
               for x in d.get("problems", []))


FOLIAGE_SHEETS = {"W04", "W05", "W06"} | {f"V{i:02d}" for i in range(1, 11)}


def needs_foliage_rework(sid, mname):
    """A failed foliage model that still builds crowns from plain blobs."""
    if sid not in FOLIAGE_SHEETS:
        return False
    try:
        src = open(f"{REPO}/art/blender/scripts/kit/{sid}/{mname}.py", encoding="utf-8").read()
    except OSError:
        return False
    return "canopy(" not in src and "leaf_cluster(" not in src and "leaf" in src


def status_of(sid, mname):
    st = state.get(f"{sid}/{mname}", {}).get("status")
    if st not in ("building", "verifying") and needs_rework(sid, mname):
        return "rework"
    if st == "failed-final" and needs_foliage_rework(sid, mname):
        return "rework"  # failed before the shared foliage helpers existed: one more try with them
    if st == "passed" and f"{sid}/{mname}" in REVERIFY:
        return "built"
    if st in ("stopped-verifying", "verifying") and not state.get(f"{sid}/{mname}", {}).get("was_built"):
        return "stopped-building"  # its builder never finished; the verifier had nothing to check
    return st


def checklist():
    rows, done_sheets, done_models = [], 0, 0
    for sid in WAVES:
        base = os.path.splitext(os.path.basename(sheet_ref(sid)))[0]
        title = base.split("_", 1)[1]
        names = modules_of(sid)
        cells, passed = [], 0
        for mname in sorted(names):
            s = state.get(f"{sid}/{mname}", {})
            st = status_of(sid, mname) or ("built" if names[mname] else "planned")
            if st == "passed":
                passed += 1
            subj = subject_of(names[mname]) if names[mname] else mname
            extra = f" {s['resemblance']}/10" if s.get("resemblance") is not None else ""
            cells.append(f"{ICON.get(st, '🔨')} {subj or mname}{extra}")
        sheet_state = state.get(f"{sid}/*", {}).get("status")
        box = "x" if names and passed == len(names) == 4 else " "
        done_sheets += box == "x"
        done_models += passed
        status = " · ".join(cells) if cells else (ICON.get(sheet_state, "⬜") + " " + (sheet_state or "queued"))
        rows.append(f"- [{box}] **{sid}** {title.replace('_', ' ').title()} — {status}")
    head = [
        "# World kit checklist",
        "",
        f"{done_sheets}/34 sheets done · {done_models}/136 models passed verification.",
        "",
        "✅ passed · 🔍 built, awaiting verification · 🔁 failed a check, fix pending · ⚠️ still failing after "
        "2 fixes, set aside for review (runs move on to new sheets) · 🎨 needs rework (one colour per material; water, mist and smoke as VFX) · 🔨 building · ⏸️ stopped (usage limit), resumes automatically · 🗺️ planned · ⬜ queued. "
        "The score is the latest verifier's resemblance out of 10.",
        "",
        "Order: pilot W01 R01, then 4 sheets per run: W02–W05 · W06–W09 · W10–W13 · W14–W16 R02 · R03–R06 · "
        "R07 R08 V01 V02 · V03–V06 · V07–V10.",
        "",
    ]
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(head + rows) + "\n")


def next_batch(n):
    """Args for the next run: the first n unfinished sheets in wave order. Passed
    models are skipped; built or checked ones start at verification; the rest
    build (continuing from any partial module on disk)."""
    out = []
    for sid in WAVES:
        names = modules_of(sid)
        sts = {m: status_of(sid, m) for m in names}
        # failed-final = used both fix rounds: set aside for the user's review
        # instead of looping on it, so the run moves on to new sheets
        if len(names) == 4 and all(v in ("passed", "failed-final") for v in sts.values()):
            continue
        sheet = {"id": sid, "ref": sheet_ref(sid)}
        skip = sorted(m for m, v in sts.items() if v in ("passed", "failed-final"))
        rework = sorted(m for m, v in sts.items() if v == "rework")
        verify = sorted(m for m, v in sts.items()
                        if v in ("built", "verifying", "verify-failed", "stopped-verifying"))
        if skip:
            sheet["skip"] = skip
        if verify:
            sheet["verifyFirst"] = verify
        if rework:
            sheet["rework"] = rework
        out.append(sheet)
        if len(out) == n:
            break
    return {"sheets": out}


def active():
    hold = os.path.join(os.path.dirname(ACTIVE), "kit_hold.txt")
    if os.path.exists(hold):  # shared-library work in progress: don't launch a run on half-done tools
        return "running hold: " + open(hold, encoding="utf-8").read().strip()
    try:
        a = json.load(open(ACTIVE, encoding="utf-8"))
    except (OSError, ValueError):
        return "idle"
    hits = glob.glob(f"{WF}/{a['runId']}/journal.jsonl")  # WF is a glob over every session
    j = hits[0] if hits else ""
    if a.get("done"):
        return "idle"
    if j and time.time() - os.path.getmtime(j) < 45 * 60:
        return f"running {a['runId']}"
    return f"stale {a['runId']}"


def main():
    scan(live=False)  # catch up silently
    checklist()
    if "--once" in sys.argv:
        return
    if "--next" in sys.argv:
        print(json.dumps(next_batch(int(sys.argv[sys.argv.index("--next") + 1]))))
        return
    if "--active" in sys.argv:
        print(active())
        return
    while True:
        ev = scan(live=True)
        if STOPS:
            ev.append(f"STOPPED {len(STOPS)} agents (usage limit or error): {', '.join(sorted(set(STOPS)))[:300]}")
            STOPS.clear()
        if ev:
            checklist()
            for e in ev:
                print(e, flush=True)
        time.sleep(3)


main()
