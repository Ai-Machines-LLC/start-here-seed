#!/usr/bin/env python3
"""toggle.py (v0.5.0 draft) - turns a leader or a recurring cycle ON/OFF, or checks it (H30, L-17, L-18).
Why: a pause must be a file anyone can read, never a deleted scheduled job. A missing entry counts as ON.
Why --file: LEADER_STATUS.txt / CYCLE_STATUS.txt live in the shared store's 01 Roles folder; a bot downloads the file,
runs this, and (after --set only) writes it back and reads it back. No machine path or environment variable.
Why exit 0 when the file is missing: an unknown status must never block work (H24: the file is flagged, not recreated).
Usage: toggle.py --file <LEADER_STATUS.txt|CYCLE_STATUS.txt> --name "<leader or group/cycle>" [--set ON|OFF] [--check]
Exit codes: 0 ON or changed, 3 OFF with --check.
"""
import argparse, datetime, os, sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--set", choices=["ON", "OFF"])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if not os.path.isfile(a.file):
        print(f"{a.file} missing (H24: not recreated); treating {a.name} as ON"); sys.exit(0)
    with open(a.file, encoding="utf-8") as f:
        lines = [l.rstrip("\r\n") for l in f if l.strip()]
    key = lambda l: l.split("|")[0].strip()
    hits = [l for l in lines if key(l) == a.name]
    state = hits[-1].split("|")[1].strip() if hits and "|" in hits[-1] else "ON"
    if a.set:
        kept = [l for l in lines if key(l) != a.name]
        kept.append(f"{a.name} | {a.set} | {datetime.datetime.now():%Y-%m-%d %H:%M}")
        with open(a.file, "w", encoding="utf-8", newline="\r\n") as f:
            f.write("\n".join(kept) + "\n")
        print(f"{a.name} set {a.set} (was {state})"); sys.exit(0)
    print(f"{a.name} is {state}")
    if a.check and state == "OFF": sys.exit(3)

if __name__ == "__main__":
    main()
