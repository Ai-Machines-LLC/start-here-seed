#!/usr/bin/env python3
"""START HERE scorecard (one row per live START HERE rev). Writer: the feedback role only.
Usage: feedback_scorecard.py LISTING.json REVS.csv TRACKER.csv OUT.csv [CONTROLLER.csv]
 LISTING.json   folder listing of the corrections drop folder (Graph JSON: value[].name, optional value[].text)
 REVS.csv       rev,live_from  (YYYY-MM-DD HH:MM ET, oldest first; a rev ends when the next starts)
 TRACKER.csv    feedback_tracker.csv (source=correction rows; rule_ref used for repeats; date = YYYY-MM-DD HH:MM)
 CONTROLLER.csv optional: rev,found  (corrections the Controller's check found in bot chats)
Files: <YYYY-MM-DD_HHMM>_<bot>_CORRECTION.txt = correction; <YYYY-MM-DD_HHMM>_<bot>_FEEDBACK.txt = cycle answer (the agreed names, Lead 2:09 PM); optional _2/_3 before .txt; for safety the time may also be HHMMSS or absent (no time = 23:59 that day).
Q2/Q4 counts come from FEEDBACK files whose text was saved next to the listing as <name> (non-'none' answer = 1)."""
import csv, json, re, sys, os
from datetime import datetime
F = "%Y-%m-%d %H:%M"
def t(s): return datetime.strptime(s.strip(), F)
lst, revs_p, trk_p, out_p = sys.argv[1:5]
ctl = {}
if len(sys.argv) > 5:
    ctl = {r["rev"]: int(r["found"]) for r in csv.DictReader(open(sys.argv[5]))}
revs = [(r["rev"], t(r["live_from"])) for r in csv.DictReader(open(revs_p))]
now = datetime.now()
def rev_of(ts):
    cur = None
    for name, start in revs:
        if ts >= start: cur = name
    return cur
pat = re.compile(r"^(\d{4}-\d{2}-\d{2})_(?:(\d{2})(\d{2})(?:\d{2})?_)?(.+?)_(CORRECTION|FEEDBACK)(?:_\d+)?\.txt$")
stat = {n: dict(files=0, q2=0, q4=0) for n, _ in revs}
base = os.path.dirname(os.path.abspath(lst))
for it in json.load(open(lst)).get("value", []):
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
