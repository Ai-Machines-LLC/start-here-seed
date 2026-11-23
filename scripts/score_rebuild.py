#!/usr/bin/env python3
"""score_rebuild.py 0.2.1 (review build) - scripted checks for a START HERE rebuild test (stdlib only).
Usage: python3 score_rebuild.py --root <rebuilt working root> --seed <seed repo checkout> [--log <bot log>] [--pin <sha>] [--proof <CLONE_PROOF.txt>]
                              [--direct-msg <regex>]
Prints one line per item: ITEM | SCORE(2/1/0 or MANUAL) | evidence. Exit 0 if every scripted item is 2, else 1.
Items that need judgment (S8 creation, S10 drills, S11 isolation, S13 cost) print MANUAL with the evidence found.
0.1.2: scrub-clean (passes scrub_check and leak_check inside a seed); S18 runs the seed's check_scripts.py against the SCRIPTS
manifest when both exist; S20 reads the librarian's CLONE_PROOF.txt when --proof is given.
0.1.3 (Reviewer #189): S20 needs a full 40-hex proof commit that equals --pin (or starts with a --pin of 7+ hex), and a
clone_finished that parses, is not before clone_started and is not in the future; S18 never counts this script's own text.
0.2.0 startup path checks (scripts/ERROR_CODES.txt): 12 --root or --seed folder missing; 20 --log or --proof given but missing.
Before 0.2.0 a missing folder scored zeros silently.
0.2.1: MOVE_LOCK is a folder (Bots/MOVE_LOCK/, one file per writer bot): S6 needs its README.txt, S10 counts the lines of
every file in it (plus a legacy Bots/MOVE_LOCK.txt when one exists)."""
import argparse, datetime, os, re, sys, glob, subprocess
ap = argparse.ArgumentParser()
ap.add_argument("--root", required=True); ap.add_argument("--seed", required=True); ap.add_argument("--log", default=None); ap.add_argument("--pin", default=None, help="seed commit sha the live START HERE pins")
ap.add_argument("--proof", default=None, help="CLONE_PROOF.txt the librarian wrote for a test-mode clone (kept outside the clone)")
ap.add_argument("--direct-msg", default=r"direct bot message|messag(e|ed) [A-Z]{2,}-", help="regex for log lines where a bot messaged another bot directly; add the platform's own tool name from PLATFORMS.txt")
a = ap.parse_args()
def fail(code, name, path, what):
    print(f"ERROR {code} {name} | {path} | {what}", file=sys.stderr); sys.exit(code)
for k in ("root", "seed"):
    if not os.path.isdir(getattr(a, k)): fail(12, "ROOT_MISSING", getattr(a, k), f"--{k} folder not found")
for k in ("log", "proof"):
    if getattr(a, k) and not os.path.isfile(getattr(a, k)): fail(20, "FILE_MISSING", getattr(a, k), f"--{k} file not found")
R, S = os.path.abspath(a.root), os.path.abspath(a.seed)
SELF = os.path.abspath(__file__)
def p(*x): return os.path.join(R, *x)
def rd(f):
    try: return open(f, encoding="utf-8", errors="replace").read()
    except OSError: return ""
def nonempty(f): return os.path.isfile(f) and os.path.getsize(f) > 0
LOG = rd(a.log or p("T5_LOG.txt"))
SENSITIVE = re.compile(r"(password|passcode|api[_ -]?key|token|secret|card number|cvv|ssn)\b", re.I)
res = []
def out(item, score, ev): res.append((item, score, ev)); print(f"{item} | {score} | {ev}")
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
cnt = glob.glob(p("02 Read_Counts", "*.txt")); bad = [c for c in cnt if not re.fullmatch(r"\s*\d+\s*", rd(c))]
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
dec = glob.glob(p("01 Roles", "declarations", "*")); badges = glob.glob(p("05 Badges", "*.txt"))
out("S8 bot creation", "MANUAL", f"{len(dec)} role declarations, {len(ids)} _BOT_IDS rows, {sum('NOT-CREATED' in l for l in ids)} NOT-CREATED; {len(badges)} badge txt (optional)")
# S9 projects
projs = [d for d in glob.glob(p("[0-9][0-9] *", "01 Projects", "*")) if os.path.isdir(d)]
okp = [d for d in projs if all(glob.glob(os.path.join(d, f"{k:02d} *")) for k in range(5)) and glob.glob(os.path.join(d, "02 Docs", "*Master*"))]
out("S9 projects", 2 if projs and len(okp) == len(projs) else 1 if projs else 0, f"{len(projs)} project folders; {len(okp)} with 00-04 + Master")
# S10/S11/S13 manual evidence
out("S10 drills", "MANUAL", f"CORRECTIONS_LOG rows {max(0, len(rd(p('Bots','CORRECTIONS_LOG.csv')).splitlines())-1)}; MOVE_LOCK lines {sum(len(rd(f).splitlines()) for f in glob.glob(p('Bots','MOVE_LOCK','*.txt')) + glob.glob(p('Bots','MOVE_LOCK.txt')) if not f.endswith('README.txt'))}; archive files {len(glob.glob(p('**','00 archive','*'), recursive=True))}")
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
out("S14 bootstrap.py", 2 if "bootstrap.py: exists" in LOG and re.search(r"refus|no such root|missing root", LOG, re.I) else 1 if "bootstrap.py: created" in LOG else 0,
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
    out("S18 referenced scripts ship", 0 if r.returncode else 1 if named else 2, f"check_scripts: {last}; missing {bad18 or 'none'}; named by the seed but only planned {named or 'none'}")
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
print(f"TOTAL scripted {sum(scripted)}/{2*len(scripted)}; manual items {sum(1 for _, s, _ in res if s == 'MANUAL')}")
sys.exit(0 if all(s == 2 for s in scripted) else 1)
