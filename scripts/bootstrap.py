#!/usr/bin/env python3
"""bootstrap.py (v0.5.3 draft) - builds the generic bot-system folder tree and empty control files.
Why: one script makes the layout identical on every new system and never overwrites existing work.
Why Python and a staging folder: no bot depends on one machine. A bot with only file access to the store runs this on
its own computer into an empty staging folder, then uploads every "created" path to WORKING_ROOT in the shared
store, skipping any path that already exists there (never overwrite, H24). On a synced folder, --root is the folder.
Usage: bootstrap.py --root <folder> --companies "A,B" [--tz UTC] [--encoding UTF8|1252]
--encoding: answer to FIRST_BOT_QUESTIONS Q6; control files are written in it (H27). Standard library only.
Exit codes (scripts/ERROR_CODES.txt): 0 done, 2 usage, 12 root missing, 24 log_event.py, toggle.py or move_lock.py not beside this script.
v0.5.0: startup path checks with ERROR_CODES codes; every check runs before anything is created.
v0.5.1: the move/edit lock log is a folder, Bots/MOVE_LOCK/, one file per writer bot (written with move_lock.py), not one
shared MOVE_LOCK.txt that bots overwrite; bootstrap creates the folder and its README and copies move_lock.py.
v0.5.2: CHANGE_LOG.csv header column is "version" (H35 word; score_rebuild S6 expects it), not "revision".
v0.5.3: How-Tos INDEX.txt header follows the live system layout, one line per how-to "folder | open it when" (not "file | what it covers | owner").
"""
import argparse, os, shutil, sys

def fail(code, name, path, what):
    # One line on standard error, then the ERROR_CODES.txt exit code (path = what the caller gave, never a secret).
    print(f"ERROR {code} {name} | {path} | {what}", file=sys.stderr); sys.exit(code)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--companies", required=True)
    ap.add_argument("--tz", default="UTC")
    ap.add_argument("--encoding", choices=["UTF8", "1252"], default="UTF8")
    a = ap.parse_args()
    if not os.path.isdir(a.root):
        fail(12, "ROOT_MISSING", a.root, "create the root folder yourself, then rerun (H24: never recreate a missing target)")
    here = os.path.dirname(os.path.abspath(__file__))   # the scripts folder this copy runs from (no fixed path)
    for s in ["log_event.py", "toggle.py", "move_lock.py"]:
        if not os.path.isfile(os.path.join(here, s)):
            fail(24, "SCRIPT_MISSING", os.path.join(here, s), "run bootstrap.py from the seed's scripts folder")
    enc = "cp1252" if a.encoding == "1252" else "utf-8"

    def new_dir(p):
        if os.path.isdir(p): print(f"exists   {p}")
        else: os.makedirs(p); print(f"created  {p}")

    def new_file(p, body):
        if os.path.exists(p): print(f"exists   {p} (left as is)"); return
        with open(p, "w", encoding=enc, newline="\r\n") as f: f.write(body + "\n")
        print(f"created  {p}")

    bots = os.path.join(a.root, "Bots")
    new_dir(bots)
    for d in ["00 archive", "01 How-Tos", "Libraries", "03 tools", "04 Scripts", "05 Logs", "06 Lessons"]:
        new_dir(os.path.join(bots, d))
    J = lambda *p: os.path.join(bots, *p)
    new_dir(J("Libraries", "_suggested"))
    new_file(J("Libraries", "LIBRARY_CHANGES.txt"), "LIBRARY_CHANGES (owner: the librarian, or the Controller when there is none). Only LIVE entries: non-author review PASS, X.Y.0, sha. Never STAGED, PENDING or LINK-TBD. Leaders work from this list.\n"
             f"FORMAT: library | version | sha256 | Reviewer PASS | category | placed {a.tz} | what changed")
    new_file(J("01 How-Tos", "INDEX.txt"), "HOW-TOS INDEX (the ONE how-to library; owner of structure: the Controller)\n"
             "One line per how-to: folder | open it when. Open only the line that matches your work. Each folder has its own short INDEX.txt.\n"
             "Bots\\Libraries\\ holds code and config only. Project-specific notes live in that project's 02 Docs Master doc, not here.")
    new_file(J("DECISIONS.txt"), f"DECISIONS (newest first). date time {a.tz} | Designer's exact words | what it decides")
    new_file(J("OWNERS.txt"), "OWNERS. route | owner bot | reviewer bot | leader")
    new_file(J("_BOT_IDS.txt"), "_BOT_IDS. bot name (<CODE>-<Project>-<Role>, bootstrap/NAMING.txt) | bot id | counter name | company")
    new_dir(J("MOVE_LOCK"))
    new_file(J("MOVE_LOCK", "README.txt"), "MOVE_LOCK (H12): one file per writer bot, <bot>.txt; a bot appends only to its own file, never another's.\n"
             "LINE: HELD or RELEASED | YYYY-MM-DD HH:MM +HHMM | bot | path | what. Write lines with 04 Scripts/move_lock.py (add, open, view, verify).")
    new_file(J("CORRECTIONS_LOG.csv"), "date,bot,mistake,cause,fix,check_added")
    new_file(J("CHANGE_LOG.csv"), "date,bot,path,version,sha256,what,reviewer")
    new_file(J("05 Logs", "EVENTS.csv"), "time,bot,event,detail")
    new_file(J("05 Logs", "METRICS.txt"), "METRICS (one line per bot, written by bot_metrics; empty until it exists)")
    new_file(J("05 Logs", "WATCHDOG_MISSES.csv"), "date,time,bot,rule,miss")
    for s in ["log_event.py", "toggle.py", "move_lock.py"]:
        dst = J("04 Scripts", s)
        if os.path.exists(dst): print(f"exists   {dst} (left as is)")
        else: shutil.copyfile(os.path.join(here, s), dst); print(f"created  {dst}")
    i = 10
    for c in a.companies.split(","):
        name = c.strip()
        if not name: continue
        cdir = os.path.join(a.root, f"{i:02d} {name}"); i += 10
        new_dir(cdir); new_dir(os.path.join(cdir, "00 archive")); new_dir(os.path.join(cdir, "01 Projects"))

if __name__ == "__main__":
    main()
