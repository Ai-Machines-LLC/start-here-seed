#!/usr/bin/env python3
"""read_check.py v0.3.0 - checks each bot's own H1 record: the openings line it appends when it writes its counter
holds the read line, and its read counter goes up by exactly 1 per read, never repeating or skipping. It reads the bot's own
record, not its actual replies; the Watchdog spot-checks replies against it (W-1a). Lists flagged bots and logs every run.
Why: the read check must run on whatever machine hosts the bots, with no personal PC; paths come from config, never code.
Usage:
  read_check.py [--config <file>] [--bots <_BOT_IDS.txt>] [--counters <COUNTER_FOLDER>] [--openings <folder>]
                [--state <read_check_state.json>] [--log <read_check_log.txt>] [--out <results folder>]
                [--opening-regex <regex: group 1 = N, optional group 2 = READ CODE letter>] [--max-idle-h <hours>]
                [--letter-log <READ_CODE_LOG.txt>] [--letter-from <ISO time>] [--letter-grace-min <minutes>] [--dry-run] | --self-test
  Each option may instead come from --config, a "KEY = value" file using READ_CHECK_BOTS, READ_CHECK_COUNTERS,
  READ_CHECK_OPENINGS, READ_CHECK_STATE, READ_CHECK_LOG, READ_CHECK_OUT, READ_CHECK_LETTER_LOG. Order: command line, then config. No environment
  variables are read (MANIFEST step 8). --bots and --counters are required; the rest are optional.
INPUTS (all plain text; no secrets are read or needed):
  --bots      the bot roster: Bots\\_BOT_IDS.txt (header line, then "bot name | bot id | counter name | company").
  --counters  COUNTER_FOLDER: one "<counter name>.txt" per bot holding a whole number.
  --openings  folder of per-bot openings files, default = the counter folder. Each bot, when it writes its counter (H1),
              appends one line to "<counter name>.openings.txt" beside it: "<ISO time with zone> | <N> | <its opening line>".
              One file per bot: no shared-file races, no host hook, no secrets (v0.1.1, the Lead). A bot with no openings
              file yet gets a SKIP note for the opening and sequence checks (a note, not a pass), and the run log says so.
  --state     this script's own memory between runs (JSON: last counter value and last read number per bot, last
              openings line handled). Missing state = first run: values are recorded, nothing is flagged as SKIP/REPEAT.
CHECKS per bot (each flag names the bot and the reason):
  NO_COUNTER     no counter file;  BAD_COUNTER  counter is not a whole number;  COUNTER_BACK  counter went down.
  NO_READ_LINE   a new openings line does not hold the read line (--opening-regex; default below).
  NUMBER_MISMATCH the N column differs from the [read #N] or [read #N-X] in the opening line.
  READ CODE (v0.3.0, shared page H1): with --letter-log (the Controller's letter log, Bots\\05 Logs\\READ_CODE_LOG.txt, one line per
  letter write: "<ISO time with zone> | <old letter> | <new letter> | <page sha before> | <page sha after>"), the letter X of each
  new opening is checked against the letter live at that line's time, or any letter written in the --letter-grace-min minutes
  before it (default 10: the turn may have read the page just before a change).
  LETTER_MISMATCH the opening's letter was not live then.  NO_LETTER the opening ends [read #N] with no letter and its time is
  at or after --letter-from (TRANSITION: default = the log's first line, the version that added the letter; earlier no-letter
  openers are not flagged). Without --letter-log the letter is not checked and the run notes that once.
  (A trimmed or archived openings file resumes after the last line handled; if that line is gone, it is read from the top and
  lines with N at or below the last N handled are skipped.)
  REPEAT / SKIP  read numbers in new replies must each be the previous + 1 (previous = last N seen, else the state value).
  COUNTER_AHEAD  the counter rose more than the replies seen account for (a read with no reply line, or a skipped number).
  COUNTER_BEHIND the counter is below the newest read number a reply showed (the number was faked or the write failed).
  IDLE           with --max-idle-h: no new reply line for that many hours (a note, not a failure).
OUTPUT: prints one line per flag, then "READ_CHECK PASS|FAIL | bots=N flagged=N notes=N". Appends one summary line to --log
  and, with --out, writes <out>/READ_CHECK_<YYYY-MM-DD_HHMM>.txt (never overwritten). Saves --state unless --dry-run.
  Exit (scripts/ERROR_CODES.txt): 0 no failures, 1 a bot is flagged, 2 usage (bad --opening-regex), 10 --config missing,
  11 --bots or --counters in neither the command line nor the config, 20 roster missing, 21 counter or openings folder
  missing, 22 --out, --log or --state folder missing (no longer created), 30 roster lists no counter names or state is not JSON.
  Standard library only. --self-test runs the built-in READ CODE cases on temporary files and exits 0 if all pass, else 1.
v0.3.0: READ CODE letter check (LETTER_MISMATCH, NO_LETTER), optional letter group in the default regex, --self-test.
v0.2.0: startup path checks with ERROR_CODES codes on standard error. Resume point (Reviewer #194a): the state keeps the text of
  the last openings line handled; the next run resumes right after that line wherever it now sits, so a file that was
  archived and then grew past the old line count is still read from the right place. Only when that line is gone is the file
  read again from the top, skipping lines whose N is at or below the last N handled.
"""
import argparse, datetime, json, os, re, sys

def fail(code, name, path, what):
    print(f"ERROR {code} {name} | {path} | {what}", file=sys.stderr); sys.exit(code)
DEFAULT_RX = r"^Reading instructions from .+\[read #(\d+)(?:-([A-Z]))?\]"
KEYS = ["bots", "counters", "openings", "state", "log", "out", "letter_log"]

def now(): return datetime.datetime.now().astimezone()
def when(s):
    try: return datetime.datetime.fromisoformat(s.strip())
    except ValueError: return None

def settings(a):
    cfg = {}
    if a.config:
        if not os.path.isfile(a.config): fail(10, "CONFIG_MISSING", a.config, "config file not found")
        for ln in open(a.config, encoding="utf-8-sig"):
            if "=" in ln and not ln.lstrip().startswith("#"):
                k, v = ln.split("=", 1); cfg[k.strip().upper()] = v.strip()
    for k in KEYS:
        if getattr(a, k) is None: setattr(a, k, cfg.get("READ_CHECK_" + k.upper()))
    return a

def letters(path):
    """Letter log -> sorted [(time, new letter)]; bad lines are returned as a list too."""
    out, bad = [], []
    for ln in open(path, encoding="utf-8-sig"):
        p = [x.strip() for x in ln.split("|")]
        if not ln.strip() or ln.lstrip().startswith("#"): continue
        t = when(p[0]) if len(p) >= 3 else None
        if t is None or t.tzinfo is None or not re.fullmatch(r"[A-Z]", p[2]): bad.append(ln.strip()[:80]); continue
        out.append((t, p[2]))
    return sorted(out, key=lambda x: x[0]), bad

def live_letters(log, tm, grace_min):
    """Letters that were on the READ CODE line at time tm or within grace_min minutes before it."""
    ok, cur = set(), None
    lo = tm - datetime.timedelta(minutes=grace_min)
    for t, x in log:
        if t <= lo: cur = x
        elif t <= tm: ok.add(x)
    if cur is not None: ok.add(cur)
    return ok

def roster(path):
    names = []
    for i, ln in enumerate(open(path, encoding="utf-8-sig")):
        p = [x.strip() for x in ln.split("|")]
        if i == 0 or len(p) < 3 or not p[2] or p[2].lower() == "counter name": continue
        names.append(p[2])
    return names

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config")
    for k in KEYS: ap.add_argument("--" + k.replace("_", "-"), dest=k)
    ap.add_argument("--letter-from"); ap.add_argument("--letter-grace-min", type=float, default=10.0); ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--opening-regex", default=DEFAULT_RX); ap.add_argument("--max-idle-h", type=float); ap.add_argument("--dry-run", action="store_true")
    a = settings(ap.parse_args())
    if a.self_test: return self_test()
    for k in ("bots", "counters"):
        if not getattr(a, k): fail(11, "CONFIG_KEY_MISSING", f"READ_CHECK_{k.upper()}", f"give --{k} or READ_CHECK_{k.upper()} in --config")
    if not os.path.isfile(a.bots): fail(20, "FILE_MISSING", a.bots, "roster not found")
    if not os.path.isdir(a.counters): fail(21, "FOLDER_MISSING", a.counters, "counter folder not found")
    od = a.openings or a.counters
    if not os.path.isdir(od): fail(21, "FOLDER_MISSING", od, "openings folder not found")
    for k in ("out", "log", "state"):
        v = getattr(a, k); d = v if k == "out" else (os.path.dirname(os.path.abspath(v)) if v else None)
        if v and not os.path.isdir(d): fail(22, "OUTPUT_PARENT_MISSING", v, f"create the folder for --{k} first")
    try: rx = re.compile(a.opening_regex)
    except re.error as e: print(f"READ_CHECK FAIL | bad --opening-regex: {e}"); return 2
    if rx.groups not in (1, 2): print("READ_CHECK FAIL | --opening-regex needs one group (the read number) and may have a second (the letter)"); return 2
    if a.letter_log and not os.path.isfile(a.letter_log): fail(20, "FILE_MISSING", a.letter_log, "letter log not found")
    llog, lbad = letters(a.letter_log) if a.letter_log else ([], [])
    lfrom = when(a.letter_from) if a.letter_from else (llog[0][0] if llog else None)
    if a.letter_from and (lfrom is None or lfrom.tzinfo is None): print("READ_CHECK FAIL | --letter-from needs an ISO time with zone"); return 2
    t0 = now(); bots = roster(a.bots)
    if not bots: fail(30, "BAD_FORMAT", a.bots, "roster lists no counter names (third column)")
    try: st = json.load(open(a.state, encoding="utf-8")) if a.state and os.path.isfile(a.state) else {}
    except ValueError: fail(30, "BAD_FORMAT", a.state, "state file is not JSON; move it aside to start a new baseline")
    first = not st; sb = st.setdefault("bots", {})
    new, have, reread, flags, notes = {}, {}, {}, [], []
    for b in bots:
        of = os.path.join(od, b + ".openings.txt"); new[b] = []; have[b] = os.path.isfile(of)
        if not have[b]: continue
        lines = open(of, encoding="utf-8-sig").read().splitlines(); rec0 = sb.setdefault(b, {})
        done, last = int(rec0.get("openings_lines", 0)), rec0.get("openings_last")
        reread[b] = False
        if last is not None:   # v0.2.0 (#194a): resume right after the last line handled, wherever it now sits
            if not (0 < done <= len(lines) and lines[done - 1] == last):
                at = max((i for i, x in enumerate(lines) if x == last), default=None)
                if at is None: done, reread[b] = 0, True   # that line is gone (trimmed or archived): reread, skip handled N
                else: done = at + 1
        elif len(lines) < done: done, reread[b] = 0, True   # state from 0.1.x without the line text
        for ln in lines[done:]:
            p = [x.strip() for x in ln.split("|", 2)]
            if len(p) == 3: new[b].append((p[0], p[1], p[2]))
            elif ln.strip(): flags.append(f"BAD_OPENINGS_LINE | {b} | {ln[:80]!r}")
        sb[b]["openings_lines"] = len(lines)
        last_text = next((x for x in reversed(lines) if x.strip()), None)
        if last_text is not None: sb[b]["openings_last"] = last_text
    unknown = sorted(f[:-len(".openings.txt")] for f in os.listdir(od) if f.endswith(".openings.txt") and f[:-len(".openings.txt")] not in new)
    flag = lambda b, k, why: flags.append(f"{k} | {b} | {why}")
    for b in bots:
        rec = sb.setdefault(b, {}); cf = os.path.join(a.counters, b + ".txt")
        if not os.path.isfile(cf): flag(b, "NO_COUNTER", f"no {b}.txt in the counter folder"); cnt = None
        else:
            raw = open(cf, encoding="utf-8-sig").read().strip()
            cnt = int(raw) if raw.isdigit() else None
            if cnt is None: flag(b, "BAD_COUNTER", f"counter holds {raw[:20]!r}, not a whole number")
        last_c, last_n = rec.get("counter"), rec.get("last_n")
        if cnt is not None and last_c is not None and cnt < last_c: flag(b, "COUNTER_BACK", f"counter {cnt} is below last run's {last_c}")
        prev = last_n if last_n is not None else last_c
        ns = []
        if not have[b]: notes.append(f"SKIP | {b} | no {b}.openings.txt yet: opening and sequence checks did not run")
        else:
            for tm, col_n, first_line in new[b]:
                if reread.get(b) and last_n is not None and col_n.isdigit() and int(col_n) <= last_n: continue
                m = rx.search(first_line)
                if not m: flag(b, "NO_READ_LINE", f"reply at {tm} opens: {first_line[:80]!r}"); continue
                n = int(m.group(1)); ns.append(n)
                if col_n != str(n): flag(b, "NUMBER_MISMATCH", f"line at {tm} has N {col_n!r} but the opening says #{n}")
                if a.letter_log:
                    x = m.group(2) if rx.groups == 2 else None; t = when(tm)
                    if t is None or t.tzinfo is None: flag(b, "BAD_OPENINGS_LINE", f"time {tm!r} has no zone; letter not checked")
                    elif x is None:
                        if lfrom is not None and t >= lfrom: flag(b, "NO_LETTER", f"read #{n} at {tm} has no READ CODE letter")
                    else:
                        ok = live_letters(llog, t, a.letter_grace_min)
                        if x not in ok: flag(b, "LETTER_MISMATCH", f"read #{n}-{x} at {tm}; live letter then: {'/'.join(sorted(ok)) or 'none logged'}")
                if prev is not None and n == prev: flag(b, "REPEAT", f"read #{n} at {tm} repeats the previous number")
                elif prev is not None and n != prev + 1: flag(b, "SKIP", f"read #{n} at {tm}; expected #{prev + 1}")
                prev = n; rec["last_seen"] = tm
            if cnt is not None and ns:
                if cnt < ns[-1]: flag(b, "COUNTER_BEHIND", f"counter {cnt} is below the newest reply's read #{ns[-1]}")
                elif cnt > ns[-1]: flag(b, "COUNTER_AHEAD", f"counter {cnt} is above the newest reply's read #{ns[-1]} (a read with no reply line, or a skipped number)")
            elif cnt is not None and not ns and last_c is not None and cnt > last_c and not first:
                flag(b, "COUNTER_AHEAD", f"counter rose {last_c} -> {cnt} with no reply line seen")
            if ns: rec["last_n"] = ns[-1]
            if a.max_idle_h and rec.get("last_seen"):
                ls = when(rec["last_seen"])
                if ls and ls.tzinfo and (t0 - ls).total_seconds() > a.max_idle_h * 3600: notes.append(f"IDLE | {b} | no reply line since {rec['last_seen']}")
        if cnt is not None: rec["counter"] = cnt
    if not a.letter_log: notes.append("NO_LETTER_CHECK | - | no --letter-log: READ CODE letters were not checked")
    for x in lbad: notes.append(f"BAD_LETTER_LOG_LINE | - | {x!r}")
    for u in unknown: notes.append(f"UNLISTED | {u} | openings file for a name not in the roster")
    if first: notes.append("FIRST_RUN | - | no state yet: counter values recorded as the baseline")
    flagged = sorted({f.split(" | ")[1] for f in flags})
    verdict = "FAIL" if flags else "PASS"
    skipped = sorted(b for b in bots if not have[b])
    summary = f"READ_CHECK {verdict} | bots={len(bots)} flagged={len(flagged)} notes={len(notes)} openings_skipped={len(skipped)}"
    for x in flags + notes: print(x)
    print(summary + (f" | flagged: {', '.join(flagged)}" if flagged else ""))
    stamp = t0.isoformat(timespec="seconds")
    if a.log:
        with open(a.log, "a", encoding="utf-8", newline="\n") as o: o.write(f"{stamp} | {summary}" + (f" | flagged: {', '.join(flagged)}" if flagged else "") + (f" | openings SKIP: {', '.join(skipped)}" if skipped else "") + "\n")
    if a.out:
        base = os.path.join(a.out, f"READ_CHECK_{t0:%Y-%m-%d_%H%M}"); f, k = base + ".txt", 2
        while os.path.exists(f): f, k = f"{base}_{k}.txt", k + 1
        with open(f, "w", encoding="utf-8", newline="\n") as o: o.write(f"READ_CHECK {stamp}\n" + "".join(x + "\n" for x in flags + notes) + summary + "\n")
    if a.state and not a.dry_run:
        st["last_run"] = stamp; tmp = a.state + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="\n") as o: json.dump(st, o, indent=1, sort_keys=True)
        os.replace(tmp, a.state)
    return 1 if flags else 0

def self_test():
    """READ CODE cases on temporary files; prints one line per case."""
    import subprocess, tempfile
    cases = [  # (name, openings lines, expected flag or None)
        ("letter live", ["2026-01-02T10:05:00-05:00 | 1 | Reading instructions from X [read #1-B]"], None),
        ("old letter after grace", ["2026-01-02T10:30:00-05:00 | 1 | Reading instructions from X [read #1-A]"], "LETTER_MISMATCH"),
        ("old letter within grace", ["2026-01-02T10:04:00-05:00 | 1 | Reading instructions from X [read #1-A]"], None),
        ("no letter after change", ["2026-01-02T10:05:00-05:00 | 1 | Reading instructions from X [read #1]"], "NO_LETTER"),
        ("no letter before version (TRANSITION)", ["2026-01-02T08:00:00-05:00 | 1 | Reading instructions from X [read #1]"], None),
        ("wrong letter", ["2026-01-02T10:05:00-05:00 | 1 | Reading instructions from X [read #1-Q]"], "LETTER_MISMATCH"),
    ]
    log = "2026-01-02T09:00:00-05:00 | - | A | s0 | s1\n2026-01-02T10:00:00-05:00 | A | B | s1 | s2\n"
    bad = 0
    for name, lines, want in cases:
        with tempfile.TemporaryDirectory() as d:
            for f, txt in (("bots.txt", "bot name | bot id | counter name | company\nb | 1 | b | C\n"), ("b.txt", "1"),
                           ("b.openings.txt", "\n".join(lines) + "\n"), ("letters.txt", log)):
                open(os.path.join(d, f), "w", encoding="utf-8", newline="\n").write(txt)
            r = subprocess.run([sys.executable, os.path.abspath(__file__), "--bots", os.path.join(d, "bots.txt"), "--counters", d,
                                "--letter-log", os.path.join(d, "letters.txt"), "--dry-run"], capture_output=True, text=True)
            got = [ln.split(" | ")[0] for ln in r.stdout.splitlines() if ln.startswith(("LETTER_MISMATCH", "NO_LETTER |"))]
            ok = (got == [want]) if want else (not got and r.returncode == 0)
            bad += not ok
            print(f"SELF_TEST {'OK' if ok else 'FAIL'} | {name} | expected {want or 'no flag'} got {', '.join(got) or 'no flag'}")
    print(f"SELF_TEST {'PASS' if not bad else 'FAIL'} | cases={len(cases)} failed={bad}")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
