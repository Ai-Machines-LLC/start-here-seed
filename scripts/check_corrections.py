#!/usr/bin/env python3
"""check_corrections.py (v0.7.0) - list Designer corrections that no bot saved as a file (CONTROLLER CT-10).

Usage: python3 check_corrections.py --folder <CORRECTIONS_DIR> --seen <seen.csv> [--window 30]
  --folder  the corrections folder; each file is <YYYY-MM-DD_HHMM>_<bot name>_CORRECTION.txt
            (optional _2, _3 suffix), one CORRECTION line. _FEEDBACK files are skipped.
  --seen    CSV with header "bot,time" (time "YYYY-MM-DD HH:MM"), one row per correction the Controller
            found in a bot's chats this pass.
  --window  minutes a file's stamp may differ from the chat time (default 30).
Feedback-cycle answers (*_FEEDBACK.txt) are skipped. Prints one MISSING line per unmatched
correction and one BADNAME line per misnamed file, then
"PASS <n> saved" or "FAIL <m> missing". Exit code 0 on PASS, 1 on FAIL.
Why: each correction is its own file (no shared-file writers), so a missed save shows up as a gap here.
"""
import argparse, csv, os, re, sys
from datetime import datetime

NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})_(\d{4})_(.+?)_(CORRECTION|FEEDBACK)(?:_\d+)?\.txt$")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True)
    ap.add_argument("--seen", required=True)
    ap.add_argument("--window", type=int, default=30)
    a = ap.parse_args()
    files, bad = [], 0
    for f in sorted(os.listdir(a.folder)):
        p = os.path.join(a.folder, f)
        if not os.path.isfile(p):
            continue
        m = NAME.match(f)
        if not m:
            print(f"BADNAME {f}")
            bad += 1
            continue
        if m.group(4) != "CORRECTION":
            continue
        t = datetime.strptime(m.group(1) + m.group(2), "%Y-%m-%d%H%M")
        files.append([m.group(3).strip().lower(), t, False])
    missing = total = 0
    with open(a.seen, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            total += 1
            bot = row["bot"].strip().lower()
            t = datetime.strptime(row["time"].strip(), "%Y-%m-%d %H:%M")
            best = None
            for rec in files:  # nearest unused file from the same bot inside the window
                d = abs((rec[1] - t).total_seconds()) / 60
                if rec[0] == bot and not rec[2] and d <= a.window and (best is None or d < best[0]):
                    best = (d, rec)
            if best:
                best[1][2] = True
            else:
                missing += 1
                print(f"MISSING {row['bot'].strip()} {row['time'].strip()}")
    if missing:
        print(f"FAIL {missing} missing of {total}")
        return 1
    print(f"PASS {total} saved" + (f" ({bad} misnamed files)" if bad else ""))
    return 0

if __name__ == "__main__":
    sys.exit(main())
