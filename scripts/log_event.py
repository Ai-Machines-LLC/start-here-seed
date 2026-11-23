#!/usr/bin/env python3
"""log_event.py (v0.5.0 draft) - appends one work event to EVENTS.csv (H30).
Why: metrics come from a log, never from a bot's memory. Why --file: the log lives in the shared store, so a bot
downloads Bots/05 Logs/EVENTS.csv to its own computer, runs this, writes the file back and reads it back. No machine path.
Events: task_start, task_done, handoff_sent, handoff_received, report, waiting.
Usage: log_event.py --file EVENTS.csv --bot "<name>" --event task_done [--detail "<path rev>"] [--time "YYYY-MM-DD HH:MM"]
Exit codes (scripts/ERROR_CODES.txt): 0 logged, 2 usage, 20 EVENTS.csv missing, 30 its first line is not time,bot,event,detail.
v0.5.0: missing file exits 20 (was 1) on standard error; header checked before appending.
"""
import argparse, csv, datetime, os, sys

def fail(code, name, path, what):
    # One line on standard error, then the ERROR_CODES.txt exit code (path = what the caller gave, never a secret).
    print(f"ERROR {code} {name} | {path} | {what}", file=sys.stderr); sys.exit(code)

EVENTS = ["task_start", "task_done", "handoff_sent", "handoff_received", "report", "waiting"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--bot", required=True)
    ap.add_argument("--event", required=True, choices=EVENTS)
    ap.add_argument("--detail", default="")
    ap.add_argument("--time", default=None, help="local time of the event; default: now on this computer")
    a = ap.parse_args()
    if not os.path.isfile(a.file):
        fail(20, "FILE_MISSING", a.file, "EVENTS.csv not found (H24: not recreated; MANIFEST step 5 creates it)")
    with open(a.file, encoding="utf-8-sig") as f:
        head = f.readline().strip()
    if head.replace(" ", "") != "time,bot,event,detail":
        fail(30, "BAD_FORMAT", a.file, "first line must be time,bot,event,detail")
    t = a.time or datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(a.file, "a", encoding="utf-8", newline="") as f:
        csv.writer(f, lineterminator="\r\n").writerow([t, a.bot, a.event, a.detail])
    print(f"logged {a.event} for {a.bot}")

if __name__ == "__main__":
    main()
