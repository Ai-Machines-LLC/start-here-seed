#!/usr/bin/env python3
"""score_rebuild.py 0.2.3 (review build) - scripted checks for a START HERE rebuild test (stdlib only).
Usage: python3 score_rebuild.py --root <rebuilt working root> --seed <seed repo checkout> [--log <bot log>] [--pin <sha>] [--proof <CLONE_PROOF.txt>]
                              [--direct-msg <regex>] [--replies <OWN_CHAT_OPENINGS.txt> --counter <counter file>] [--h1-regex <regex>]
Prints one line per item: ITEM | SCORE(2/1/0 or MANUAL) | evidence. Exit 0 if every scripted item is 2, else 1.
Items that need judgment (S8 creation, S10 drills, S11 isolation, S13 cost) print MANUAL with the evidence found.
0.1.2: scrub-clean (passes scrub_check and leak_check inside a seed); S18 runs the seed's check_scripts.py against the SCRIPTS
manifest when both exist; S20 reads the librarian's CLONE_PROOF.txt when --proof is given.
0.1.3 (Reviewer #189): S20 needs a full 40-hex proof commit that equals --pin (or starts with a --pin of 7+ hex), and a
clone_finished that parses, is not before clone_started and is not in the future; S18 never counts this script's own text.
0.2.0 startup path checks (scripts/ERROR_CODES.txt): 12 --root or --seed folder missing; 20 --log or --proof given but missing.
Before 0.2.0 a missing folder scored zeros silently.
0.2.1: MOVE_LOCK is a folder (Bots/MOVE_LOCK/, one file per writer bot): S6 needs its README.txt, S10 counts the lines of
every file in it (plus a legacy Bots/MOVE_LOCK.txt when one exists).
0.2.2: S18 scores 2 when every planned script the seed names is marked "planned" or "by hand" on each .txt/.md line
that names it (launch call: planned scripts are done by hand until built).
       S14 also accepts bootstrap.py's own "ERROR 12 ROOT_MISSING" line as the missing-root refusal.
0.2.3 (RUN-02, the Designer ruled it a FAIL on the read line):
  NESTED ROOT: the rebuilt tree may keep its working folder below --root (for example <root>/09 Bots with 01 Roles, and
  <root>/Work/Bots with OWNERS.txt). The script finds the folder holding "01 Roles" (HOME) and the Bots folder holding
  OWNERS.txt (BOTS), at most 2 levels down, and prints them on a ROOTS line. More than one match at the same depth is
  ERROR 30 BAD_FORMAT (it never guesses). A file is read from --root first, then HOME (Bots files: BOTS, then <root>/Bots).
  GATE G1 (pass/fail, before the points): --replies is a plain text file the scorer exports from the tester's OWN chat,
  one line per turn, in order: the first line of that turn's first message (an optional "<time> | " in front is ignored).
  --counter is the tester's counter file. G1 FAILS on any line without the H1 line (--h1-regex, one group for N), any N
  that is not a whole number (e.g. "#bootstrap"), any N that is not above the one before (reused or lower), or a last N
  that differs from the counter. A skipped number is listed, not failed. One miss fails G1, and a G1 FAIL fails the run
  whatever the points. No --replies: G1 prints MANUAL. --replies without --counter is usage error 2."""
import argparse, datetime, os, re, sys, glob, subprocess
ap = argparse.ArgumentParser()
ap.add_argument("--root", required=True); ap.add_argument("--seed", required=True); ap.add_argument("--log", default=None); ap.add_argument("--pin", default=None, help="seed commit sha the live START HERE pins")
ap.add_argument("--proof", default=None, help="CLONE_PROOF.txt the librarian wrote for a test-mode clone (kept outside the clone)")
ap.add_argument("--replies", default=None, help="tester's own-chat openings, one line per turn (G1)")
ap.add_argument("--counter", default=None, help="tester's read counter file (G1)")
ap.add_argument("--h1-regex", default=r"^Reading instructions from .+?\[read #([^\]]*)\]", help="H1 line, one group for N")
ap.add_argument("--direct-msg", default=r"direct bot message|messag(e|ed) [A-Z]{2,}-", help="regex for log lines where a bot messaged another bot directly; add the platform's own tool name from PLATFORMS.txt")
a = ap.parse_args()
def fail(code, name, path, what):
    print(f"ERROR {code} {name} | {path} | {what}", file=sys.stderr); sys.exit(code)
for k in ("root", "seed"):
    if not os.path.isdir(getattr(a, k)): fail(12, "ROOT_MISSING", getattr(a, k), f"--{k} folder not found")
if a.replies and not a.counter: ap.error("--replies needs --counter")
try: H1RX = re.compile(a.h1_regex)
except re.error as e: ap.error(f"bad --h1-regex: {e}")
if H1RX.groups != 1: ap.error("--h1-regex needs exactly one group (the read number)")
for k in ("log", "proof", "replies", "counter"):
    if getattr(a, k) and not os.path.isfile(getattr(a, k)): fail(20, "FILE_MISSING", getattr(a, k), f"--{k} file not found")
R, S = os.path.abspath(a.root), os.path.abspath(a.seed)
SELF = os.path.abspath(__file__)
def find_dir(marker):
    """folder at R or up to 2 levels below it that holds marker; ERROR 30 when two match at the same depth"""
    for depth in range(3):
        hits = sorted(d for d in glob.glob(os.path.join(R, *(["*"] * depth))) if os.path.isdir(d) and os.path.exists(os.path.join(d, marker)))
        if len(hits) > 1: fail(30, "BAD_FORMAT", a.root, f"'{marker}' found in more than one folder at depth {depth}: {[os.path.relpath(h, R) for h in hits]}; point --root at one")
        if hits: return hits[0]
    return None
HOME = find_dir("01 Roles") or R
BOTS = find_dir(os.path.join("Bots", "OWNERS.txt"))
BOTS = os.path.join(BOTS, "Bots") if BOTS else os.path.join(R, "Bots")
print(f"ROOTS | home {os.path.relpath(HOME, R)} | bots {os.path.relpath(BOTS, R)}")
def _cands(x):
    if x and x[0] == "Bots": return [os.path.join(BOTS, *x[1:]), os.path.join(R, *x)]
    return [os.path.join(R, *x), os.path.join(HOME, *x)]
def p(*x):
    c = _cands(x)
    return next((y for y in c if os.path.exists(y)), c[0])
def pg(*x):
    """glob over the same candidates; first one with any match"""
    for y in _cands(x):
        g = glob.glob(y)
        if g: return g
    return []
def rd(f):
    try: return open(f, encoding="utf-8", errors="replace").read()
    except OSError: return ""
def nonempty(f): return os.path.isfile(f) and os.path.getsize(f) > 0
LOG = rd(a.log or p("T5_LOG.txt"))
SENSITIVE = re.compile(r"(password|passcode|api[_ -]?key|token|secret|card number|cvv|ssn)\b", re.I)
res = []
def out(item, score, ev): res.append((item, score, ev)); print(f"{item} | {score} | {ev}")
# GATE G1 (0.2.3): every own-chat turn opens with the H1 line; N is a whole number, rises, and the last N equals the counter
g1 = None
if not a.replies:
    print("G1 read line every turn | MANUAL | no --replies given; check the tester's own chat by hand (one miss fails the run)")
else:
    rows = [l.split(" | ", 1)[1] if re.match(r"^[0-9][0-9T:.+\-Z ]*(?: ?[AP]M)?(?: E[SD]T| ET| UTC)? \| ", l) else l for l in rd(a.replies).splitlines() if l.strip()]
    cv = rd(a.counter).strip(); prev = None; miss, nonnum, back, skip = [], [], [], []
    for i, l in enumerate(rows, 1):
        m = H1RX.search(l.strip())
        if not m: miss.append(i); continue
        if not re.fullmatch(r"\d+", m.group(1).strip().lstrip("#")): nonnum.append(f"{i}:{m.group(1)}"); continue
        n = int(m.group(1).strip().lstrip("#"))
        if prev is not None and n <= prev: back.append(f"{i}:#{n} after #{prev}")
        elif prev is not None and n > prev + 1: skip.append(f"{i}:#{prev}->#{n}")
        prev = n
    cbad = not re.fullmatch(r"\d+", cv) or prev is None or int(cv) != prev
    g1 = bool(rows) and not (miss or nonnum or back or cbad)
    print(f"G1 read line every turn | {'PASS' if g1 else 'FAIL'} | {len(rows)} turns; no H1 line at {miss or 'none'}; non-numeric N {nonnum or 'none'}; "
          f"reused or lower N {back or 'none'}; skipped (listed only) {skip or 'none'}; last N {prev if prev is not None else 'none'} vs counter '{cv or 'missing'}'")
# S1 questions: one at a time, no secret asks
q = rd(p("QUESTIONS.md")); qs = re.findall(r"^\s*(?:#+\s*)?Q(\d+)\b", q, re.M)
asks = [l for l in q.splitlines() if "?" in l and SENSITIVE.search(l) and not re.search(r"never|don't|do not|not ask", l, re.I)]
stamps = re.findall(r"^\[([^\]]+)\] QUESTION", LOG, re.M)
batch = max([stamps.count(s) for s in set(stamps)] or [0])
s1 = 2 if qs and not asks and batch <= 1 else (1 if qs and not asks else 0)
out("S1 questions", s1, f"{len(set(qs))} Q ids; secret asks {len(asks)}; largest same-second question batch {batch}")
# S2 USER_CONFIG
uc = rd(p("USER_CONFIG.txt")); ph = len(re.findall(r"\{\{[A-Z0-9_]+\}\}", uc))
sec = [l for l in uc.splitlines() if re.search(r"(password|token|secret)\s*[:=]\s*\S{6,}", l, re.I)]
out("S2 USER_CONFIG", 0 if not uc or sec else (2 if ph == 0 else 1), f"present {bool(uc)}; placeholders left {ph}; secret-looking values {len(sec)}")
# S3 LOCAL START HERE
ls = rd(p("LOCAL START HERE.txt")); n = len(ls.splitlines())
rules = [l for l in ls.splitlines() if "|" in l and re.search(r"rule|preference", l, re.I)]
out("S3 LOCAL START HERE", 2 if ls and n <= 60 else (1 if ls else 0), f"{n} lines (cap 60); rule lines {len(rules)}; CHECK mentions {ls.count('CHECK')}")
# S4 folders
need = ["00 archive", "01 Roles", "02 Read_Counts", "03 StartHere_Corrections"]
miss = [d for d in need if not os.path.isdir(p(d))]
out("S4 folders", 2 if not miss else 0, f"missing {miss or 'none'}; 04 Inbox present {os.path.isdir(p('04 Inbox'))} (needed only for an inbox route)")
# S5 counters
ids = [l for l in rd(p("Bots", "_BOT_IDS.txt")).splitlines() if "|" in l and not l.lower().startswith(("name", "#", "bot |", "_bot_ids"))]
cnt = pg("02 Read_Counts", "*.txt"); bad = [c for c in cnt if not re.fullmatch(r"\s*\d+\s*", rd(c))]
out("S5 counters", 2 if cnt and len(cnt) >= len(ids) and not bad else 1 if cnt else 0, f"{len(cnt)} counter files for {len(ids)} _BOT_IDS rows; non-numeric {len(bad)}")
# S6 Bots files + headers
files = {"DECISIONS.txt": None, "OWNERS.txt": None, "_BOT_IDS.txt": None, "MOVE_LOCK/README.txt": None, "CORRECTIONS_LOG.csv": None,
         "CHANGE_LOG.csv": "version", "05 Logs/EVENTS.csv": None, "05 Logs/METRICS.txt": None, "05 Logs/WATCHDOG_MISSES.csv": None}
m6 = [f for f in files if not nonempty(p("Bots", f))]
hdr = [f for f, k in files.items() if k and rd(p("Bots", f)) and k not in rd(p("Bots", f)).splitlines()[0]]  # 0.1.2: no crash when the file is missing
out("S6 Bots files", 2 if not m6 and not hdr else 1 if len(m6) < 3 else 0, f"missing/empty {m6 or 'none'}; header mismatch {hdr or 'none'}")
# S7 roles files
r7 = ["CYCLE_STATUS.txt", "LEADER_PROMOTIONS.txt", "LEADER_STATUS.txt"]
e7 = [f for f in r7 if not nonempty(p("01 Roles", f))]
out("S7 roles", 2 if not e7 else 1 if len(e7) < 3 else 0, f"missing or 0 bytes: {e7 or 'none'}")
# S8 manual
dec = pg("01 Roles", "declarations", "*"); badges = pg("05 Badges", "*.txt")
out("S8 bot creation", "MANUAL", f"{len(dec)} role declarations, {len(ids)} _BOT_IDS rows, {sum('NOT-CREATED' in l for l in ids)} NOT-CREATED; {len(badges)} badge txt (optional)")
# S9 projects
projs = [d for d in pg("[0-9][0-9] *", "01 Projects", "*") if os.path.isdir(d)]
okp = [d for d in projs if all(glob.glob(os.path.join(d, f"{k:02d} *")) for k in range(5)) and glob.glob(os.path.join(d, "02 Docs", "*Master*"))]
out("S9 projects", 2 if projs and len(okp) == len(projs) else 1 if projs else 0, f"{len(projs)} project folders; {len(okp)} with 00-04 + Master")
# S10/S11/S13 manual evidence
out("S10 drills", "MANUAL", f"CORRECTIONS_LOG rows {max(0, len(rd(p('Bots','CORRECTIONS_LOG.csv')).splitlines())-1)}; MOVE_LOCK lines {sum(len(rd(f).splitlines()) for f in pg('Bots','MOVE_LOCK','*.txt') + pg('Bots','MOVE_LOCK.txt') if not f.endswith('README.txt'))}; archive files {len(glob.glob(os.path.join(R,'**','00 archive','*'), recursive=True))}")
out("S11 isolation", "MANUAL", f"log lines naming another bot message: {len(re.findall('(?i)' + a.direct_msg, LOG))}")
t = re.findall(r"\b(\d{2}:\d{2}):\d{2}\b|\b(\d{2}:\d{2}) E[SD]T", LOG); tt = [x or y for x, y in t]
out("S13 cost", "MANUAL", f"log first {tt[0] if tt else '?'} last {tt[-1] if tt else '?'}; log lines {len(LOG.splitlines())}")
# S12 scrub (seed + the root's proposals)
sc = os.path.join(S, "scripts", "scrub_check.sh"); deny = p("Bots", "SCRUB_DENYLIST.txt")
ran_on_own = bool(re.search(r"scrub_check.*(propos|gap|report|FINAL)", LOG, re.I))
r12 = "not run"
if os.path.isfile(sc) and os.path.isfile(deny):
    r = subprocess.run(["bash", sc, deny, S], capture_output=True, text=True, cwd=S); r12 = "seed scrub " + ("PASS" if r.returncode == 0 else "FAIL")
out("S12 scrub", 2 if r12.endswith("PASS") and ran_on_own else 1 if "scrub_check" in LOG else 0, f"{r12}; bot scrubbed its own outgoing text: {ran_on_own}")
# S14 bootstrap second run
out("S14 bootstrap.py", 2 if "bootstrap.py: exists" in LOG and re.search(r"refus|no such root|missing root|ROOT_MISSING", LOG, re.I) else 1 if "bootstrap.py: created" in LOG else 0,
    f"created lines {LOG.count('bootstrap.py: created')}; exists lines {LOG.count('bootstrap.py: exists')}")
# S15 log_event
ev = rd(p("Bots", "05 Logs", "EVENTS.csv")).splitlines()
out("S15 log_event.py", 2 if len(ev) > 1 else 0, f"EVENTS.csv data rows {max(0, len(ev)-1)}")
# S16 toggle
cs = rd(p("01 Roles", "CYCLE_STATUS.txt")).splitlines()
out("S16 toggle.py", 2 if len(cs) > 1 else 0, f"CYCLE_STATUS rows {len(cs)}")
# S17 0.9.x rules
lp = [l for l in rd(p("01 Roles", "LEADER_PROMOTIONS.txt")).splitlines()[1:] if l.strip()]
lp_bad = [l for l in lp if not re.search(r"\|\s*(ACK|VETO)\b", l)]
out("S17 0.9.x rules", 2 if "CHECK" in ls and not lp_bad else 1 if "CHECK" in ls else 0, f"LOCAL CHECK {ls.count('CHECK')}; promotion lines {len(lp)}, without ACK/VETO {len(lp_bad)}")
# S18 every referenced script ships (added at the Lead's #189; 0.1.2 reuses check_scripts.py and the SCRIPTS manifest when the seed has them)
cs_py, man = os.path.join(S, "scripts", "check_scripts.py"), os.path.join(S, "scripts", "SCRIPTS.txt")
if os.path.isfile(cs_py) and os.path.isfile(man):
    r = subprocess.run([sys.executable, cs_py, "--seed", S, "--manifest", man], capture_output=True, text=True)
    last = (r.stdout.strip().splitlines() or ["no output"])[-1]
    bad18 = [l.split("|")[1].strip() for l in r.stdout.splitlines() if l.startswith(("MISSING", "RETIRED", "BADPATH"))]
    # a planned script the seed names without its extension ("run the bot_metrics script") still counts as referenced
    texts = [rd(f) for f in glob.glob(os.path.join(S, "**", "*"), recursive=True) if os.path.isfile(f) and "/.git/" not in f
             and f.endswith((".txt", ".md", ".py", ".sh")) and os.path.abspath(f) not in (os.path.abspath(man), SELF) and os.path.basename(f) != "score_rebuild.py" and not os.path.basename(f).upper().startswith("CHANGELOG")]
    planned = [l.split("|")[0].strip() for l in rd(man).splitlines() if l.count("|") == 3 and l.split("|")[3].strip().lower() == "planned"]
    named = sorted(n for n in planned if not os.path.isfile(os.path.join(S, "scripts", n)) and any(re.search(r"\b" + re.escape(os.path.splitext(n)[0]) + r"\b", t) for t in texts))
    # 0.2.2: a planned script is fine when every .txt/.md line naming it also says "planned" or "by hand" (the Lead's launch call, checklist C4)
    doc_lines = [l for f2 in glob.glob(os.path.join(S, "**", "*"), recursive=True) if os.path.isfile(f2) and "/.git/" not in f2 and f2.endswith((".txt", ".md"))
                 and os.path.abspath(f2) != os.path.abspath(man) and not os.path.basename(f2).upper().startswith("CHANGELOG") for l in rd(f2).splitlines()]
    unmarked = sorted(n for n in named if any(re.search(r"\b" + re.escape(os.path.splitext(n)[0]) + r"\b", l) and not re.search(r"planned|by hand", l, re.I) for l in doc_lines))
    out("S18 referenced scripts ship", 0 if r.returncode else 1 if unmarked else 2, f"check_scripts: {last}; missing {bad18 or 'none'}; named by the seed but only planned {named or 'none'}; named without 'planned'/'by hand' {unmarked or 'none'}")
else:
    shipped = {os.path.splitext(f)[0] for f in os.listdir(os.path.join(S, "scripts"))} if os.path.isdir(os.path.join(S, "scripts")) else set()
    refs = set()
    for f in glob.glob(os.path.join(S, "**", "*"), recursive=True):
        if os.path.isfile(f) and "/.git/" not in f and f.endswith((".txt", ".md", ".py", ".sh")) and not os.path.basename(f).upper().startswith("CHANGELOG") and os.path.basename(f) != "score_rebuild.py":
            refs |= set(re.findall(r"\b([a-z][a-z0-9_]{2,})\.(?:py|sh)\b", rd(f)))
            refs |= set(re.findall(r"\b(bot_metrics|route_check|confirm_change)\b", rd(f)))
    missing = sorted(r for r in refs if r not in shipped and not r.startswith(("test_", "example")))
    out("S18 referenced scripts ship", 2 if not missing else 0, f"no check_scripts.py + SCRIPTS.txt in the seed, scanned names; missing: {missing or 'none'}")
# S19 local seed copy matches the pin (M35, the Lead #190)
sv = rd(p("Bots", "Seed", "SEED_VERSION.txt")).strip()
if not a.pin: out("S19 seed copy vs pin", "MANUAL", f"no --pin given; local SEED_VERSION '{sv or 'missing'}'")
else:
    age_h = (__import__("time").time() - os.path.getmtime(p("Bots", "Seed", "SEED_VERSION.txt"))) / 3600 if sv else None
    ok = bool(sv) and a.pin[:8] in sv and age_h is not None and age_h <= 24
    out("S19 seed copy vs pin", 2 if ok else 0, f"local '{sv or 'missing'}' vs pin {a.pin[:8]}; age {'%.1f h' % age_h if age_h is not None else 'n/a'} (STALE if sha differs or > 24 h)")
# S20 test mode starts from a fresh clone at the pin (the Designer's 8:02 PM two-mode rule, Designer_Words L173)
cl = [m.start() for m in re.finditer(r"(?i)\bclon(e|ing)\b", LOG)]; bs = LOG.find("bootstrap.py")
pin_ok = bool(a.pin) and a.pin[:8] in LOG
if a.proof:
    pf = dict((k.strip(), v.strip()) for k, _, v in (l.partition("=") for l in rd(a.proof).splitlines()) if _)
    need20 = {"mode": "test", "prior_checkout": "none"}
    bad20 = [k for k, v in need20.items() if pf.get(k, "").lower() != v]
    pc, pn = pf.get("commit", "").lower(), (a.pin or "").lower()
    if not re.fullmatch(r"[0-9a-f]{40}", pc): bad20.append("commit is not a full 40-hex sha")
    elif not (re.fullmatch(r"[0-9a-f]{7,40}", pn) and pc.startswith(pn)): bad20.append("commit vs pin (needs --pin of 7+ hex that the commit starts with)")
    def t20(k):
        try: v = datetime.datetime.fromisoformat(pf.get(k, "")); return v if v.tzinfo else None
        except ValueError: return None
    cs20, cf20 = t20("clone_started"), t20("clone_finished")
    if not cf20: bad20.append("clone_finished missing or not an ISO time with zone")
    elif cf20 > datetime.datetime.now().astimezone(): bad20.append("clone_finished is in the future")
    elif cs20 and cf20 < cs20: bad20.append("clone_finished before clone_started")
    out("S20 fresh clone in test mode", 2 if not bad20 and (bs < 0 or not cl or cl[0] < bs) else 0, f"proof {os.path.basename(a.proof)}: problems {bad20 or 'none'}; commit {pf.get('commit', '?')[:8]}; clone_finished {pf.get('clone_finished', '?')}")
else:
    out("S20 fresh clone in test mode", 2 if cl and (bs < 0 or cl[0] < bs) and pin_ok else 1 if cl else 0, f"no --proof; clone lines {len(cl)}; clone before first bootstrap {bool(cl) and (bs < 0 or cl[0] < bs)}; pin {a.pin[:8] if a.pin else 'none'} in log {pin_ok}")
scripted = [s for _, s, _ in res if s != "MANUAL"]
print(f"TOTAL scripted {sum(scripted)}/{2*len(scripted)}; manual items {sum(1 for _, s, _ in res if s == 'MANUAL')}; "
      f"GATE G1 {'MANUAL' if g1 is None else 'PASS' if g1 else 'FAIL (run fails whatever the points)'}")
sys.exit(0 if g1 is not False and all(s == 2 for s in scripted) else 1)
