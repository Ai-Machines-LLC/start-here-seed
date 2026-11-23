#!/usr/bin/env python3
"""toggle.py (v0.6.0 draft) - turns a leader or a recurring cycle ON/OFF, or checks it (H30, L-17, L-18).
Why: a pause must be a file anyone can read, never a deleted scheduled job. A missing entry counts as ON.
Why --file: LEADER_STATUS.txt / CYCLE_STATUS.txt live in the shared store's 01 Roles folder; a bot downloads the file,
runs this, and (after --set only) writes it back and reads it back. No machine path or environment variable.
Why a missing file still counts as ON, with exit 50: an unknown status must never block work, but the caller must be able to
see the file is gone (H24: flagged, not recreated). The Designer chose this 2026-11-22 8:54 PM ET ("just fix it", option B).
Usage: toggle.py --file <LEADER_STATUS.txt|CYCLE_STATUS.txt> --name "<leader or group/cycle>" [--set ON|OFF] [--check]
Exit codes (scripts/ERROR_CODES.txt): 0 ON or changed, 2 usage, 3 OFF with --check, 50 WARN_ASSUMED_ON (status file missing,
treated as ON; nothing written, also with --set), 30 a status line has a state other than ON or OFF.
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
        print(f"{a.name} is ON (assumed)")
        print(f"WARN 50 WARN_ASSUMED_ON | {a.file} | status file missing (H24: not recreated); treating {a.name} as ON", file=sys.stderr)
        sys.exit(50)
    with open(a.file, encoding="utf-8") as f:
        lines = [l.rstrip("\r\n") for l in f if l.strip()]
    key = lambda l: l.split("|")[0].strip()
    hits = [l for l in lines if key(l) == a.name]
    state = hits[-1].split("|")[1].strip() if hits and "|" in hits[-1] else "ON"
    if state not in ("ON", "OFF"):
        print(f"ERROR 30 BAD_FORMAT | {a.file} | {a.name} has state {state[:20]!r}, not ON or OFF", file=sys.stderr); sys.exit(30)
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
