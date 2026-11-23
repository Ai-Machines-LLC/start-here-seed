#!/usr/bin/env python3
"""check_corrections.py (v0.8.0) - list Designer corrections that no bot saved as a file (CONTROLLER CT-10).

Usage: python3 check_corrections.py --folder <CORRECTIONS_DIR> --seen <seen.csv> [--window 30]
  --folder  the corrections folder; each file is <YYYY-MM-DD_HHMM>_<bot name>_CORRECTION.txt
            (optional _2, _3 suffix), one CORRECTION line. _FEEDBACK files are skipped.
  --seen    CSV with header "bot,time" (time "YYYY-MM-DD HH:MM"), one row per correction the Controller
            found in a bot's chats this pass.
  --window  minutes a file's stamp may differ from the chat time (default 30).
Feedback-cycle answers (*_FEEDBACK.txt) are skipped. Prints one MISSING line per unmatched
correction and one BADNAME line per misnamed file, then
"PASS <n> saved" or "FAIL <m> missing". Exit code 0 on PASS, 1 on FAIL.
Other exits (scripts/ERROR_CODES.txt): 2 usage, 21 --folder missing, 20 --seen missing, 30 --seen lacks the bot,time header,
31 a --seen time is not "YYYY-MM-DD HH:MM". v0.8.0: startup path checks; each failure names the path.
Why: each correction is its own file (no shared-file writers), so a missed save shows up as a gap here.
"""
import argparse, csv, os, re, sys
from datetime import datetime

def fail(code, name, path, what):
    # One line on standard error, then the ERROR_CODES.txt exit code (path = what the caller gave, never a secret).
    print(f"ERROR {code} {name} | {path} | {what}", file=sys.stderr); sys.exit(code)

NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})_(\d{4})_(.+?)_(CORRECTION|FEEDBACK)(?:_\d+)?\.txt$")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True)
    ap.add_argument("--seen", required=True)
    ap.add_argument("--window", type=int, default=30)
    a = ap.parse_args()
    if not os.path.isdir(a.folder): fail(21, "FOLDER_MISSING", a.folder, "pass the corrections folder with --folder")
    if not os.path.isfile(a.seen): fail(20, "FILE_MISSING", a.seen, "pass the seen CSV (header bot,time) with --seen")
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
        rd = csv.DictReader(fh)
        if not rd.fieldnames or not {"bot", "time"} <= {x.strip() for x in rd.fieldnames}:
            fail(30, "BAD_FORMAT", a.seen, "first line must be the header bot,time")
        for row in rd:
            total += 1
            bot = (row.get("bot") or "").strip().lower()
            try: t = datetime.strptime((row.get("time") or "").strip(), "%Y-%m-%d %H:%M")
            except ValueError: fail(31, "BAD_VALUE", a.seen, f"row {total}: time {row.get('time')!r} is not YYYY-MM-DD HH:MM")
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
