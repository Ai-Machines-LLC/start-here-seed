#!/usr/bin/env python3
"""move_lock.py (v0.1.1) - the shared move/edit lock log (H12), as one file per writer bot.
Why: one shared MOVE_LOCK file lost lines whenever two bots rewrote it close together (each upload replaces the whole
file). Here each bot appends only to its OWN file <lockdir>/<bot>.txt, so no bot can overwrite another bot's lines.
The folder as a whole is the lock log; "view" merges it and "open" tells whether a path is free.
Line format (one per event, " | " between fields; other lines, such as a first header line, are ignored):
  HELD | <YYYY-MM-DD HH:MM +HHMM> | <bot> | <path> | <what you will do>
  RELEASED | <YYYY-MM-DD HH:MM +HHMM> | <bot> | <path> | <what was done, versions, read-back result>
Paths compare case-insensitively with / and \\ treated the same, "." segments dropped; a folder conflicts with
everything under it. An empty path (such as "/" or "\\") or one with a ".." segment is refused (2; 30 inside a file).
Commands (every path comes from the command line; nothing is fixed):
  add    --dir D --bot B --kind HELD|RELEASED --path P --what W [--time T]   append one line to D/B.txt
         HELD is refused (32) while another bot holds P; RELEASED is refused (33) without your own open HELD on P.
  open   --dir D [--path P [--bot B]]   list open holds. With --path: 0 free, 32 held by another bot. With --bot too:
         0 only when B has an open HELD on P and NO other bot has an open HELD overlapping P (B won); 32 when any
         other bot does (B lost the race, whatever the times say).
  view   --dir D                         every line of every bot's file, oldest first
  verify --before OLD --after NEW        after an upload and read-back: every line of OLD is still in NEW, in order (34 if not)
Bot steps for one held edit: download all of D; open --path P (must be 0); download your own file again, copy it as OLD;
add HELD; upload your file; read it back; verify --before OLD --after <read-back>; download all of D again;
open --path P --bot B (must be 0; 32 = lost race, see RACE); do the edit; then add RELEASED the same way (download, copy, add, upload, read back, verify).
RACE: two bots can each write HELD from a view that did not yet show the other's. Times never decide the race, since
a line stamped earlier can be uploaded later. A bot wins only by seeing no other open overlapping HELD after its own
HELD is uploaded and read back. On 32 (LOST RACE): add RELEASED with "lost race", wait a random 1-5 minutes, then
start again from the first step. Both bots may lose and both retry; at most one can ever win. A winner does not
recheck: anyone who uploads a HELD after the winner's will see the winner's line and lose.
Exit codes (ERROR_CODES.txt): 0 OK, 2 usage, 20 file missing, 21 folder missing, 30 bad line or a line in another
bot's file, 32 LOCK_HELD, 33 NOT_HELD, 34 LINES_LOST.
"""
import argparse, datetime, glob, os, re, sys

BAD_NAME = re.compile(r'[\\/:*?"<>|]')

def fail(code, name, where, what):
    print(f"ERROR {code} {name} | {where} | {what}", file=sys.stderr); sys.exit(code)

def norm(p):
    """'Shared\\./X' -> 'shared/x'. Returns None for an empty path or one with a '..' segment."""
    segs = [x for x in re.split(r"[\\/]+", p.strip()) if x.strip() not in ("", ".")]
    if not segs or any(x.strip() == ".." for x in segs):
        return None
    return "/".join(x.strip() for x in segs).casefold()

def overlaps(a, b):
    a, b = norm(a), norm(b)
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")

def when(t):
    try:
        return datetime.datetime.strptime(t.strip(), "%Y-%m-%d %H:%M %z")
    except ValueError:
        return None

def read_dir(d):
    """Every HELD/RELEASED line in d/*.txt as dicts; a bad line or a line naming another bot stops with 30."""
    rows = []
    for f in sorted(glob.glob(os.path.join(d, "*.txt"))):
        if os.path.basename(f).casefold() == "readme.txt":
            continue   # the folder's README explains the format; it is not a bot's file
        owner = os.path.splitext(os.path.basename(f))[0]
        with open(f, encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):
                line = line.rstrip("\r\n")
                kind = line.split("|", 1)[0].strip()
                if kind not in ("HELD", "RELEASED"):
                    continue
                parts = [x.strip() for x in line.split("|", 4)]
                if len(parts) != 5 or norm(parts[3]) is None or when(parts[1]) is None:
                    fail(30, "BAD_FORMAT", f"{f}:{n}", "expected 'HELD|RELEASED | YYYY-MM-DD HH:MM +HHMM | bot | path | what'")
                if parts[2] != owner:
                    fail(30, "BAD_FORMAT", f"{f}:{n}", f"line names bot '{parts[2]}' but this is {owner}'s file; each bot writes only its own file")
                rows.append({"kind": kind, "t": when(parts[1]), "bot": owner, "path": parts[3], "line": line, "file": f, "n": n})
    rows.sort(key=lambda r: (r["t"], r["bot"], r["n"]))
    return rows

def open_holds(rows):
    held = []
    for r in rows:
        if r["kind"] == "HELD":
            held.append(r)
        else:
            for h in held:
                if h["bot"] == r["bot"] and norm(h["path"]) == norm(r["path"]):
                    held.remove(h); break
    return held

def main():
    ap = argparse.ArgumentParser(description="per-bot move/edit lock log (H12)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a1 = sub.add_parser("add"); a1.add_argument("--dir", required=True); a1.add_argument("--bot", required=True)
    a1.add_argument("--kind", required=True, choices=["HELD", "RELEASED"]); a1.add_argument("--path", required=True)
    a1.add_argument("--what", required=True); a1.add_argument("--time")
    a2 = sub.add_parser("open"); a2.add_argument("--dir", required=True); a2.add_argument("--path"); a2.add_argument("--bot")
    a3 = sub.add_parser("view"); a3.add_argument("--dir", required=True)
    a4 = sub.add_parser("verify"); a4.add_argument("--before", required=True); a4.add_argument("--after", required=True)
    a = ap.parse_args()
    if getattr(a, "path", None) is not None and norm(a.path) is None:
        fail(2, "USAGE", "--path", "path is empty (such as '/' or '\\') or has a '..' segment; name the real file or folder")

    if a.cmd == "verify":
        for f in (a.before, a.after):
            if not os.path.isfile(f): fail(20, "FILE_MISSING", f, "download the file again and retry")
        before = [l.rstrip("\r\n") for l in open(a.before, encoding="utf-8")]
        after = [l.rstrip("\r\n") for l in open(a.after, encoding="utf-8")]
        if after[:len(before)] != before:
            lost = [l for l in before if l not in after]
            for l in lost: print(f"LOST: {l}")
            fail(34, "LINES_LOST", a.after, f"{len(lost) or 'some'} earlier line(s) missing or reordered; put them back from OLD before anything else")
        print(f"OK {len(after) - len(before)} line(s) added, {len(before)} kept"); return

    if not os.path.isdir(a.dir): fail(21, "FOLDER_MISSING", a.dir, "the lock folder is missing (it is never created by a script, H24)")
    rows = read_dir(a.dir)

    if a.cmd == "view":
        for r in rows: print(r["line"])
        return

    if a.cmd == "open":
        if a.bot and not a.path: fail(2, "USAGE", "--bot", "--bot needs --path")
        held = open_holds(rows)
        if not a.path:
            for h in held: print(f"OPEN {h['line']}")
            print(f"{len(held)} open hold(s)"); return
        on = [h for h in held if overlaps(h["path"], a.path)]
        if a.bot:
            mine = [h for h in on if h["bot"] == a.bot]
            if not mine: fail(33, "NOT_HELD", a.path, f"{a.bot} has no open HELD on this path")
            rivals = [h for h in on if h["bot"] != a.bot]
            if rivals:
                for h in rivals: print(f"LOST RACE: {h['bot']} also holds it: {h['line']}")
                fail(32, "LOCK_HELD", a.path, "another bot also holds it; add RELEASED 'lost race', wait a random 1-5 minutes, start again")
            print(f"WON {a.path}: {a.bot} holds it alone; do the edit (no recheck needed)"); return
        others = on
        if others:
            for h in others: print(f"HELD BY {h['bot']}: {h['line']}")
            fail(32, "LOCK_HELD", a.path, f"held by {', '.join(sorted({h['bot'] for h in others}))}; wait for their RELEASED")
        print(f"FREE {a.path}"); return

    # add
    if BAD_NAME.search(a.bot) or not a.bot.strip() or a.bot.casefold() == "readme": fail(2, "USAGE", "--bot", "bot name cannot be empty, README, or hold \\ / : * ? \" < > |")
    if "|" in a.path or "|" in a.what or "\n" in a.what: fail(2, "USAGE", "--path/--what", "no '|' or line breaks in path or what")
    t = a.time or datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %z")
    if when(t) is None: fail(2, "USAGE", "--time", "use 'YYYY-MM-DD HH:MM +HHMM'")
    held = open_holds(rows)
    on = [h for h in held if overlaps(h["path"], a.path)]
    if a.kind == "HELD":
        if on:
            for h in on: print(f"HELD BY {h['bot']}: {h['line']}")
            fail(32, "LOCK_HELD", a.path, "already held (by another bot, or by you without a RELEASED); nothing written")
    elif not [h for h in on if h["bot"] == a.bot and norm(h["path"]) == norm(a.path)]:
        fail(33, "NOT_HELD", a.path, f"{a.bot} has no open HELD on exactly this path; nothing written")
    f = os.path.join(a.dir, a.bot + ".txt")
    line = f"{a.kind} | {t} | {a.bot} | {a.path} | {a.what}"
    lead = ""
    if os.path.isfile(f) and os.path.getsize(f):
        with open(f, "rb") as fh:
            fh.seek(-1, 2); lead = "" if fh.read(1) == b"\n" else "\n"
    with open(f, "a", encoding="utf-8", newline="\n") as fh: fh.write(lead + line + "\n")
    print(line)

if __name__ == "__main__":
    main()
