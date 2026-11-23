#!/usr/bin/env python3
"""feedback_scorecard.py (v0.2.0) - START HERE scorecard (one row per live START HERE rev). Writer: the feedback role only.
Usage: feedback_scorecard.py LISTING.json REVS.csv TRACKER.csv OUT.csv [CONTROLLER.csv]
 LISTING.json   folder listing of the corrections drop folder (Graph JSON: value[].name, optional value[].text)
 REVS.csv       rev,live_from  (YYYY-MM-DD HH:MM ET, oldest first; a rev ends when the next starts)
 TRACKER.csv    feedback_tracker.csv (source=correction rows; rule_ref used for repeats; date = YYYY-MM-DD HH:MM)
 CONTROLLER.csv optional: rev,found  (corrections the Controller's check found in bot chats)
Files: <YYYY-MM-DD_HHMM>_<bot>_CORRECTION.txt = correction; <YYYY-MM-DD_HHMM>_<bot>_FEEDBACK.txt = cycle answer (the agreed names, Lead 2:09 PM); optional _2/_3 before .txt; for safety the time may also be HHMMSS or absent (no time = 23:59 that day).
Q2/Q4 counts come from FEEDBACK files whose text was saved next to the listing as <name> (non-'none' answer = 1).
Exit codes (scripts/ERROR_CODES.txt): 0 written, 2 wrong number of arguments, 20 an input file missing, 22 OUT.csv's folder
missing, 30 an input lacks its columns or is not JSON, 31 a date is not YYYY-MM-DD HH:MM.
v0.2.0: startup path and header checks before anything is read; each failure names the path."""
import csv, json, re, sys, os
from datetime import datetime
F = "%Y-%m-%d %H:%M"
def t(s): return datetime.strptime(s.strip(), F)
def fail(code, name, path, what):
    print(f"ERROR {code} {name} | {path} | {what}", file=sys.stderr); sys.exit(code)
if len(sys.argv) not in (5, 6):
    print("usage: feedback_scorecard.py LISTING.json REVS.csv TRACKER.csv OUT.csv [CONTROLLER.csv]", file=sys.stderr); sys.exit(2)
lst, revs_p, trk_p, out_p = sys.argv[1:5]
for p_ in sys.argv[1:4] + sys.argv[5:6]:
    if not os.path.isfile(p_): fail(20, "FILE_MISSING", p_, "input file not found (missing, renamed or moved)")
if not os.path.isdir(os.path.dirname(os.path.abspath(out_p))): fail(22, "OUTPUT_PARENT_MISSING", out_p, "create the output folder first")
def cols_of(p_, need):
    with open(p_, newline="") as fh: head = next(csv.reader(fh), [])
    if not set(need) <= {h.strip() for h in head}: fail(30, "BAD_FORMAT", p_, f"header must include {','.join(need)}")
cols_of(revs_p, ["rev", "live_from"]); cols_of(trk_p, ["source", "rule_ref", "date"])
ctl = {}
if len(sys.argv) > 5:
    cols_of(sys.argv[5], ["rev", "found"])
    try: ctl = {r["rev"]: int(r["found"]) for r in csv.DictReader(open(sys.argv[5]))}
    except ValueError: fail(31, "BAD_VALUE", sys.argv[5], "found must be a whole number")
try: revs = [(r["rev"], t(r["live_from"])) for r in csv.DictReader(open(revs_p))]
except ValueError: fail(31, "BAD_VALUE", revs_p, "live_from must be YYYY-MM-DD HH:MM")
try: listing = json.load(open(lst))
except ValueError: fail(30, "BAD_FORMAT", lst, "not a JSON folder listing")
now = datetime.now()
def rev_of(ts):
    cur = None
    for name, start in revs:
        if ts >= start: cur = name
    return cur
pat = re.compile(r"^(\d{4}-\d{2}-\d{2})_(?:(\d{2})(\d{2})(?:\d{2})?_)?(.+?)_(CORRECTION|FEEDBACK)(?:_\d+)?\.txt$")
stat = {n: dict(files=0, q2=0, q4=0) for n, _ in revs}
base = os.path.dirname(os.path.abspath(lst))
for it in listing.get("value", []):
    m = pat.match(it["name"])
    if not m: continue
    r = rev_of(datetime.strptime(f"{m.group(1)} {m.group(2) or '23'}:{m.group(3) or '59'}", F))
    if r is None: continue
    if m.group(5) == "CORRECTION":
        stat[r]["files"] += 1; continue
    p = os.path.join(base, it["name"])
    if os.path.exists(p):
        for line in open(p, errors="ignore"):
            q = re.match(r"\s*(Q2|Q4)\b[^:]*:\s*(.*)", line, re.I)
            if q and q.group(2).strip().lower() not in ("", "none", "no"):
                stat[r][q.group(1).lower()] += 1
seen, rep = set(), {n: 0 for n, _ in revs}
for row in csv.DictReader(open(trk_p)):
    if row.get("source") != "correction" or not row.get("rule_ref"): continue
    try: r = rev_of(t(row["date"]))
    except ValueError: continue
    if r is None: continue
    if row["rule_ref"] in seen: rep[r] += 1
    seen.add(row["rule_ref"])
cols = ["rev","live_from","live_to","days","corrections","per_day","repeats","saved_files","controller_found","saved_share","q2_read_two_ways","q4_cant_follow","d_per_day","d_repeats","d_saved_share","basis"]
rows, prev = [], None
for i, (n, start) in enumerate(revs):
    end = revs[i+1][1] if i+1 < len(revs) else now
    days = max((end - start).total_seconds() / 86400, 1/24)
    s = stat[n]; found = ctl.get(n)
    total = max(s["files"], found or 0)
    share = f"{s['files']/total:.2f}" if total else ""
    pd = total / days
    row = dict(rev=n, live_from=start.strftime(F), live_to=("live" if i+1 == len(revs) else end.strftime(F)),
               days=f"{days:.2f}", corrections=total, per_day=f"{pd:.2f}", repeats=rep[n], saved_files=s["files"],
               controller_found="" if found is None else found, saved_share=share,
               q2_read_two_ways=s["q2"], q4_cant_follow=s["q4"],
               basis="files" if s["files"] or found is not None else "pre-intake (no files)")
    if row["basis"].startswith("pre-intake"):
        row.update(corrections="", per_day="", saved_share="")
    if prev and row["per_day"] and prev["per_day"]:
        row["d_per_day"] = f"{pd - float(prev['per_day']):+.2f}"
        row["d_repeats"] = f"{rep[n] - int(prev['repeats']):+d}"
        row["d_saved_share"] = f"{float(share) - float(prev['saved_share']):+.2f}" if share and prev["saved_share"] else ""
    rows.append(row); prev = row
with open(out_p, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)
print(open(out_p).read())
