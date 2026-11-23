#!/usr/bin/env python3
"""run_team_checks.py v0.2.1 (review build) - one runner for the START HERE team's own checks; writes one dated results file.
Why: testing and verification are script-driven wherever possible, not manual steps. Each check reports PASS, FAIL or SKIP
with its reason, so a reader sees at once what ran, what failed and what could not run.
Usage:
  run_team_checks.py --mode test|normal --seed <seed folder> --pin <commit sha> --out <results folder>
                     [--proof <CLONE_PROOF.txt>] [--max-proof-age-min 180] [--max-age-h 24]
                     [--deny <denylist kept outside the seed>] [--allow <leak allowlist>]
                     [--rebuild-root <rebuilt working root> [--log <bot log>]]
                     [--verify-tier platform|project [--project <name>] --counters <dir> --heartbeats <dir> [--config <USER_CONFIG>]]
                     [--hb <HEARTBEATS> --req <OPEN_REQUESTS> --bots <roster>]
                     [--manifest <SCRIPTS manifest>] [--scripts-dir <dir>] [--only name,name] [--require name,name]
MODES (the librarian's two modes):
  test    the run must start from a fresh clone at --pin made by the librarian in test mode (no cached or earlier local copy).
          FRESH_CLONE checks the librarian's proof file and the clone itself. Every script the runner uses must come from
          inside that clone: a check whose script is outside it FAILs (it is not skipped).
  normal  the local copy is checked against --pin: PIN_CHECK FAILs as STALE if HEAD is not the pin or the copy is older
          than --max-age-h hours (the librarian pulls once a day).
This runner never contacts the remote repo: it reads local git state only (rev-parse, status, log, reflog). The clone and the
daily pull are librarian actions; the runner only verifies the librarian's proof.
CLONE_PROOF.txt (written by the librarian, key = value lines):
  mode = test | commit = <full sha cloned> | clone_started = <ISO time> | clone_finished = <ISO time>
  target = <absolute clone folder> | prior_checkout = none | by = <librarian name>
  ('|' above only separates the keys here; in the file each key is on its own line)
FRESH_CLONE FAILs if: the proof is missing or not mode=test; prior_checkout is not 'none'; target is not --seed; commit is not
  --pin or not the clone's HEAD; the proof is older than --max-proof-age-min or dated after this run started; the clone's
  reflog has anything besides the single 'clone' entry; the clone has tracked changes or untracked files; any file is a
  link pointing outside the clone; or the clone's git folder is older than clone_started (a reused copy).
Checks, in order (each PASS, FAIL or SKIP with a reason):
  FRESH_CLONE (test) or PIN_CHECK (normal); BOOTSTRAP_VERIFY (bootstrap.py --verify; SKIP while bootstrap.py lacks an option it needs); SCRUB_CHECK (scrub_check.sh);
  LEAK_CHECK (leak_check.py --dir <seed>, plus --history inside a git clone; planned, SKIP until shipped); CHECK_HEARTBEATS (check_heartbeats.py; planned, SKIP until shipped);
  CHECK_SCRIPTS (check_scripts.py); SCORE_REBUILD (score_rebuild.py, the T5/T6 scorecard; its MANUAL items are listed, not scored).
v0.1.2 GATES (Reviewer #186): --pin is required. FRESH_CLONE (test) or PIN_CHECK (normal) always runs, whatever --only says.
  --only and --require take check names from the list above; an unknown name is a usage error (exit 2). A required check
  that is SKIPped or left out by --only becomes FAIL. SCRUB_CHECK and LEAK_CHECK are always required in test mode. In test
  mode the runner itself must sit inside the clone. A run with no PASS row is FAIL ('nothing was checked').
Scripts are found in --scripts-dir (normal mode only), else <seed>/scripts. Missing inputs give SKIP with the option needed.
Results: <out>/TEAM_CHECKS_<YYYY-MM-DD_HHMM>.txt (never overwritten: a second run in the same minute adds _2, _3).
Last line: TEAM_CHECKS PASS|FAIL | pass=N fail=N skip=N. Exit 0 when nothing FAILs, 1 if any FAIL, 2 on a usage error.
v0.2.1 (Lead #242): BOOTSTRAP_VERIFY never calls bootstrap.py with an option bootstrap.py does not define. It reads the
  add_argument("--...") names in bootstrap.py first; any missing one gives SKIP 'bootstrap verify not built yet' naming it
  (bootstrap.py 0.5.0 has no --verify mode, so this SKIPs until one is built).
v0.2.0 startup path checks (scripts/ERROR_CODES.txt), before any check runs: 12 --seed missing; 22 --out folder missing (it is
  no longer created); 20 a file option given but missing (--proof --deny --allow --log --config --bots --manifest; --hb and --req
  may be a file or a folder);
  21 a folder option given but missing (--rebuild-root --counters --heartbeats --scripts-dir). Leaving an option out still
  gives the check's SKIP (or, for a required check, FAIL) row as before.
Standard library only; needs git on the path for the git checks (a missing git is a FAIL in test mode, SKIP in normal)."""
import argparse, datetime, hashlib, os, re, shutil, subprocess, sys

def fail(code, name, path, what):
    print(f"ERROR {code} {name} | {path} | {what}", file=sys.stderr); sys.exit(code)

def now(): return datetime.datetime.now().astimezone()
def when(s):
    t = datetime.datetime.fromisoformat(s.strip().replace("Z", "+00:00"))
    return t.astimezone() if t.tzinfo is None else t
def sha8(f):
    try: return hashlib.sha256(open(f, "rb").read()).hexdigest()[:8]
    except OSError: return "--------"
def same(x, y):
    x, y = (x or "").lower(), (y or "").lower()
    return min(len(x), len(y)) >= 7 and (x.startswith(y) or y.startswith(x))
def inside(path, root):
    path, root = os.path.realpath(path), os.path.realpath(root)
    return path == root or path.startswith(root + os.sep)

CHECKS = ["FRESH_CLONE", "PIN_CHECK", "BOOTSTRAP_VERIFY", "SCRUB_CHECK", "LEAK_CHECK", "CHECK_HEARTBEATS", "CHECK_SCRIPTS", "SCORE_REBUILD"]
LOCAL_GIT = {"rev-parse", "status", "log", "reflog", "ls-files", "cat-file"}
def git(seed, *args):
    """Local, read-only git only: the runner never clones, fetches, pulls or pushes."""
    if args[0] not in LOCAL_GIT: raise SystemExit(f"REFUSED git {args[0]}: the runner reads local git state only")
    r = subprocess.run(["git", "-C", seed, *args], capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

def defined_opts(script):
    """Option names a script defines (its add_argument("--x") calls), read as text; nothing is run."""
    try: return set(re.findall(r"""add_argument\(\s*["'](--[A-Za-z0-9][A-Za-z0-9-]*)["']""", open(script, encoding="utf-8", errors="replace").read()))
    except OSError: return set()

class Run:
    def __init__(s): s.rows, s.detail = [], []
    def add(s, name, result, reason, out=""):
        s.rows.append((name, result, reason)); print(f"{name} | {result} | {reason}")
        if out: s.detail.append(f"--- {name} output (last 40 lines) ---\n" + "\n".join(out.splitlines()[-40:]))

def run_script(R, name, script, argv, seed, mode, timeout=600):
    if not script or not os.path.isfile(script): return R.add(name, "SKIP", f"script not found ({os.path.basename(script) if script else '?'})")
    if mode == "test" and not inside(script, seed): return R.add(name, "FAIL", f"{script} is outside the fresh clone (test mode uses only files from the clone)")
    cmd = (["bash"] if script.endswith(".sh") else [sys.executable]) + [script] + argv
    try: r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired: return R.add(name, "FAIL", f"timed out after {timeout} s")
    out = (r.stdout + ("\n" + r.stderr if r.stderr else "")).strip()
    last = (out.splitlines() or [""])[-1][:160]
    R.add(name, "PASS" if r.returncode == 0 else "FAIL", f"exit {r.returncode} | {os.path.basename(script)} {sha8(script)} | {last}", out)

def fresh_clone(R, a, seed, start):
    if not shutil.which("git"): return R.add("FRESH_CLONE", "FAIL", "git not found; cannot prove a fresh clone")
    if not a.proof or not os.path.isfile(a.proof): return R.add("FRESH_CLONE", "FAIL", "no clone proof (--proof CLONE_PROOF.txt from the librarian's test-mode clone)")
    kv = {}
    for line in open(a.proof, encoding="utf-8", errors="replace"):
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1); kv[k.strip().lower()] = v.strip()
    bad = []
    need = ["mode", "commit", "clone_started", "clone_finished", "target", "prior_checkout", "by"]
    miss = [k for k in need if not kv.get(k)]
    if miss: return R.add("FRESH_CLONE", "FAIL", f"proof missing {', '.join(miss)}")
    if kv["mode"].lower() != "test": bad.append(f"proof mode '{kv['mode']}' is not test")
    if kv["prior_checkout"].lower() != "none": bad.append(f"prior_checkout '{kv['prior_checkout']}' (must be none)")
    if os.path.realpath(kv["target"]) != os.path.realpath(seed): bad.append("proof target is not --seed")
    try: t0, t1 = when(kv["clone_started"]), when(kv["clone_finished"])
    except ValueError: return R.add("FRESH_CLONE", "FAIL", "proof times are not ISO times")
    if t1 < t0: bad.append("clone_finished before clone_started")
    if t1 > start: bad.append("proof dated after this run started")
    if (start - t1).total_seconds() > a.max_proof_age_min * 60: bad.append(f"proof older than {a.max_proof_age_min} min")
    rc, head, err = git(seed, "rev-parse", "HEAD")
    if rc: return R.add("FRESH_CLONE", "FAIL", f"--seed is not a git clone ({err[:80]})")
    if not same(head, a.pin): bad.append(f"HEAD {head[:8]} is not pin {(a.pin or '?')[:8]}")
    if not same(head, kv["commit"]): bad.append(f"proof commit {kv['commit'][:8]} is not HEAD {head[:8]}")
    rc, refl, _ = git(seed, "reflog", "--all", "--format=%gs")
    entries = [x for x in refl.splitlines() if x.strip()]
    if not entries or not all(e.startswith("clone:") for e in entries): bad.append(f"reflog has {len(entries)} entries beyond the clone (checkout, pull, reset or commit after cloning)")
    rc, st, _ = git(seed, "status", "--porcelain", "--untracked-files=all", "--ignored")
    if st: bad.append(f"{len(st.splitlines())} changed, untracked or ignored files (not from the clone)")
    for d, dirs, files in os.walk(seed):
        dirs[:] = [x for x in dirs if x != ".git"]
        for fn in files + dirs:
            fp = os.path.join(d, fn)
            if os.path.islink(fp) and not inside(fp, seed): bad.append(f"link leaves the clone: {os.path.relpath(fp, seed)}"); break
    gd = os.path.join(seed, ".git")
    try:
        born = datetime.datetime.fromtimestamp(os.stat(os.path.join(gd, "HEAD")).st_mtime).astimezone()
        if born < t0 - datetime.timedelta(seconds=5): bad.append("git folder is older than clone_started (a reused copy)")
    except OSError: bad.append("no .git/HEAD")
    if bad: return R.add("FRESH_CLONE", "FAIL", "; ".join(bad))
    R.add("FRESH_CLONE", "PASS", f"commit {head[:8]} = pin; cloned {kv['clone_finished']} by {kv['by']}; reflog clone only; no extra files")

def pin_check(R, a, seed):
    if not shutil.which("git"): return R.add("PIN_CHECK", "SKIP", "git not found")
    rc, head, err = git(seed, "rev-parse", "HEAD")
    if rc: return R.add("PIN_CHECK", "FAIL", f"--seed is not a git copy ({err[:80]})")
    if not a.pin: return R.add("PIN_CHECK", "SKIP", "no --pin given")
    probs = []
    if not same(head, a.pin): probs.append(f"HEAD {head[:8]} is not pin {a.pin[:8]}")
    stamps = [os.path.join(seed, ".git", f) for f in ("FETCH_HEAD", "HEAD")]
    newest = max((os.path.getmtime(f) for f in stamps if os.path.exists(f)), default=0)
    age_h = (now().timestamp() - newest) / 3600
    if age_h > a.max_age_h: probs.append(f"last pull {age_h:.1f} h ago (> {a.max_age_h} h)")
    rc, st, _ = git(seed, "status", "--porcelain")
    if st: probs.append(f"{len(st.splitlines())} local changes")
    R.add("PIN_CHECK", "FAIL" if probs else "PASS", ("STALE: " + "; ".join(probs)) if probs else f"HEAD {head[:8]} = pin; last pull {age_h:.1f} h ago")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["test", "normal"], required=True)
    ap.add_argument("--seed", required=True); ap.add_argument("--pin", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--proof"); ap.add_argument("--max-proof-age-min", type=int, default=180); ap.add_argument("--max-age-h", type=float, default=24)
    ap.add_argument("--deny"); ap.add_argument("--allow")
    ap.add_argument("--rebuild-root"); ap.add_argument("--log")
    ap.add_argument("--verify-tier", choices=["platform", "project"]); ap.add_argument("--project")
    ap.add_argument("--counters"); ap.add_argument("--heartbeats"); ap.add_argument("--config")
    ap.add_argument("--hb"); ap.add_argument("--req"); ap.add_argument("--bots")
    ap.add_argument("--manifest"); ap.add_argument("--scripts-dir"); ap.add_argument("--only"); ap.add_argument("--require")
    a = ap.parse_args()
    seed = os.path.abspath(a.seed)
    if not os.path.isdir(seed): fail(12, "ROOT_MISSING", a.seed, "pass the seed folder (the clone) with --seed")
    if not os.path.isdir(a.out): fail(22, "OUTPUT_PARENT_MISSING", a.out, "create the results folder first (H24)")
    for k in ("hb", "req"):   # a heartbeat or open-requests store may be one file or a folder
        v = getattr(a, k)
        if v and not os.path.exists(v): fail(20, "FILE_MISSING", v, f"--{k} file or folder not found (missing, renamed or moved)")
    for k in ("proof", "deny", "allow", "log", "config", "bots", "manifest"):
        v = getattr(a, k)
        if v and not os.path.isfile(v): fail(20, "FILE_MISSING", v, f"--{k} file not found (missing, renamed or moved)")
    for k in ("rebuild_root", "counters", "heartbeats", "scripts_dir"):
        v = getattr(a, k)
        if v and not os.path.isdir(v): fail(21, "FOLDER_MISSING", v, f"--{k.replace('_', '-')} folder not found")
    if a.mode == "test" and a.scripts_dir: print("TEAM_CHECKS FAIL | --scripts-dir is not allowed in test mode (scripts must come from the clone)"); return 2
    start = now()
    names = lambda v: {x.strip().upper() for x in v.split(",") if x.strip()} if v else set()
    only, req = (names(a.only) or None), names(a.require)
    unknown = sorted(((only or set()) | req) - set(CHECKS))
    if unknown: print(f"TEAM_CHECKS FAIL | unknown check name(s) {unknown}; known: {', '.join(CHECKS)}"); return 2
    if a.mode == "test": req |= {"SCRUB_CHECK", "LEAK_CHECK"}
    gate = "FRESH_CLONE" if a.mode == "test" else "PIN_CHECK"
    req.add(gate)
    want = lambda n: n == gate or only is None or n in only
    sd = os.path.abspath(a.scripts_dir) if a.scripts_dir else os.path.join(seed, "scripts")
    sc = lambda n: os.path.join(sd, n)
    R = Run()
    if a.mode == "test":
        fresh_clone(R, a, seed, start)
        if not inside(os.path.abspath(__file__), seed): R.add("RUNNER_IN_CLONE", "FAIL", f"the runner {os.path.abspath(__file__)} is outside the fresh clone")
    if a.mode == "normal" and want("PIN_CHECK"): pin_check(R, a, seed)
    if want("BOOTSTRAP_VERIFY"):
        bs = sc("bootstrap.py")
        opts = ["--verify", "--root", "--counters", "--heartbeats"] + (["--project"] if a.project else []) + (["--config"] if a.config else [])
        gone = [o for o in opts if o not in defined_opts(bs)] if os.path.isfile(bs) else []
        if gone: R.add("BOOTSTRAP_VERIFY", "SKIP", f"bootstrap verify not built yet: bootstrap.py has no {', '.join(gone)}")
        elif not (a.verify_tier and a.rebuild_root and a.counters and a.heartbeats): R.add("BOOTSTRAP_VERIFY", "SKIP", "needs --verify-tier, --rebuild-root, --counters and --heartbeats")
        else:
            argv = ["--verify", a.verify_tier, "--root", a.rebuild_root, "--counters", a.counters, "--heartbeats", a.heartbeats]
            if a.project: argv += ["--project", a.project]
            if a.config: argv += ["--config", a.config]
            run_script(R, "BOOTSTRAP_VERIFY", bs, argv, seed, a.mode)
    if want("SCRUB_CHECK"):
        if not a.deny: R.add("SCRUB_CHECK", "SKIP", "needs --deny (denylist kept outside the seed)")
        else: run_script(R, "SCRUB_CHECK", sc("scrub_check.sh"), [a.deny, seed], seed, a.mode)
    if want("LEAK_CHECK"):
        if not a.deny: R.add("LEAK_CHECK", "SKIP", "needs --deny (denylist kept outside the seed)")
        else:
            argv = ["--deny", a.deny, "--dir", seed] + (["--allow", a.allow] if a.allow else [])
            if os.path.isdir(os.path.join(seed, ".git")): argv += ["--history", "--repo", seed]
            run_script(R, "LEAK_CHECK", sc("leak_check.py"), argv, seed, a.mode)
    if want("CHECK_HEARTBEATS"):
        if not (a.hb and a.req and a.bots): R.add("CHECK_HEARTBEATS", "SKIP", "needs --hb, --req and --bots")
        else: run_script(R, "CHECK_HEARTBEATS", sc("check_heartbeats.py"), ["--hb", a.hb, "--req", a.req, "--bots", a.bots], seed, a.mode)
    if want("CHECK_SCRIPTS"):
        argv = ["--seed", seed] + (["--manifest", a.manifest] if a.manifest else [])
        run_script(R, "CHECK_SCRIPTS", sc("check_scripts.py"), argv, seed, a.mode)
    if want("SCORE_REBUILD"):
        if not a.rebuild_root: R.add("SCORE_REBUILD", "SKIP", "needs --rebuild-root (a rebuild test run)")
        else:
            argv = ["--root", a.rebuild_root, "--seed", seed] + (["--log", a.log] if a.log else []) + (["--pin", a.pin] if a.pin else [])
            run_script(R, "SCORE_REBUILD", sc("score_rebuild.py"), argv, seed, a.mode)
    base = os.path.join(a.out, f"TEAM_CHECKS_{start:%Y-%m-%d_%H%M}")
    f, k = base + ".txt", 2
    while os.path.exists(f): f, k = f"{base}_{k}.txt", k + 1
    got = {n: x for n, x, _ in R.rows}
    for n in sorted(req):
        if n not in got: R.add(n, "FAIL", "required check left out by --only")
        elif got[n] == "SKIP":
            R.rows = [(m, "FAIL" if m == n else x, ("required check was skipped: " + w) if m == n else w) for m, x, w in R.rows]
            print(f"{n} | FAIL | required check was skipped")
    cnt = {r: sum(1 for _, x, _ in R.rows if x == r) for r in ("PASS", "FAIL", "SKIP")}
    if not cnt["PASS"]: R.add("NOTHING_CHECKED", "FAIL", "no check passed, so the run proves nothing"); cnt["FAIL"] += 1
    verdict = "FAIL" if cnt["FAIL"] else "PASS"
    _, head, _ = git(seed, "rev-parse", "HEAD") if shutil.which("git") else (1, "", "")
    with open(f, "w", encoding="utf-8", newline="\n") as o:
        o.write(f"TEAM_CHECKS {start.isoformat(timespec='seconds')} | mode {a.mode} | seed HEAD {head[:8] or '-'} | pin {(a.pin or '-')[:8]} | runner {sha8(os.path.abspath(__file__))}\n")
        for n, r, why in R.rows: o.write(f"{n} | {r} | {why}\n")
        o.write(f"TEAM_CHECKS {verdict} | pass={cnt['PASS']} fail={cnt['FAIL']} skip={cnt['SKIP']}\n")
        if R.detail: o.write("\n" + "\n".join(R.detail) + "\n")
    print(f"TEAM_CHECKS {verdict} | pass={cnt['PASS']} fail={cnt['FAIL']} skip={cnt['SKIP']} | results {f}")
    return 1 if cnt["FAIL"] else 0

if __name__ == "__main__":
    sys.exit(main())
