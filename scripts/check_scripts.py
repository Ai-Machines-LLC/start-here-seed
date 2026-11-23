#!/usr/bin/env python3
"""check_scripts.py v0.2.0 (review build) - does every script the seed depends on exist and appear in the SCRIPTS manifest?
Why: a rebuild bot must find each script the seed names before it writes a new one (reuse or extend, never duplicate).
The T5 rebuild found scripts the seed named but did not ship; this check catches that before a release.
Usage: check_scripts.py --seed <seed folder> [--manifest <file>] [--ignore <regex>] [--strict] [--probes [--codes <file>]]
  --manifest  the SCRIPTS manifest (default: <seed>/scripts/SCRIPTS.txt). One script per line:
              name | job | path | status      e.g.  scrub_check.sh | fails if the seed holds owner data | scripts/scrub_check.sh | shipped
              path is relative to --seed. status: shipped (must exist), planned (may be absent), retired (must not be referenced).
              Blank lines, '#' lines and a header line (first field 'name') are skipped.
  --ignore    regex of script names to leave out (example names in prose); names starting test_ or example are always left out.
  --strict    UNLISTED also makes the exit nonzero.
What counts as a reference: any word ending .py .pyw .sh or .ps1 in a .txt .md .py .sh .ps1 or .csv file under --seed
(.git skipped; the manifest itself does not count as a reference; a file named CHANGELOG or CHANGELOG.<ext> does not count
either, since it records scripts the seed used to ship - v0.1.2, exact name since v0.1.3).
Output, one line per script, sorted by name:
  OK        listed and present at its path (or listed planned and absent but not referenced)
  MISSING   referenced or listed shipped, but no file at the listed path (or, unlisted, nowhere under --seed)
  UNLISTED  referenced or present under scripts/ but not in the manifest
  PLANNED   listed planned, referenced, not present yet (a note, not a failure)
  FLIP      listed planned but the file is present: set its status to shipped (a note; FAIL with --strict) - v0.1.3
  RETIRED   listed retired but still referenced (counts as MISSING: the seed points at a script it no longer ships)
  BADPATH   listed path is absolute or has a '..' part (counts as MISSING)
Then: CHECK_SCRIPTS PASS|FAIL | listed=N referenced=N ok=N missing=N unlisted=N planned=N
v0.2.0 (the Designer 2026-11-22, no exact paths; error codes):
  HARDCODED  every .py .pyw .sh .ps1 file under <seed>/scripts is scanned with path_patterns.py (drive letters, network
             shares, user and system folders, a tilde home, web or file addresses, cloud-drive folders); one line per hit,
             "HARDCODED | <file>:<line> | <pattern names>", and any hit FAILs. The first line is skipped when it starts "#!".
  --probes   also runs every PROBES line in ERROR_CODES.txt (--codes, default <seed>/scripts/ERROR_CODES.txt) in an empty
             temporary folder: each script is started with a missing path and must exit with the listed code, print
             "ERROR <code>" (or "WARN <code>") on standard error and name the missing path. Then:
             PROBE      | <script> | <args> | expected N got N | OK or WRONG (WRONG FAILs)
             NOPROBE    a manifest-shipped script under scripts/ has no probe and is not listed "Import only" (FAILs)
             CODE_UNKNOWN a script exits with a code that is not in the table (FAILs)
Exit (scripts/ERROR_CODES.txt): 0 PASS, 1 any MISSING/RETIRED/BADPATH/HARDCODED (or UNLISTED with --strict, or a probe
  failure), 2 usage, 12 no seed folder, 20 no manifest (or no ERROR_CODES.txt with --probes), 24 path_patterns.py not beside
  this script.
Read-only. Standard library only. Text read as UTF-8, else cp1252."""
import argparse, os, re, shlex, subprocess, sys, tempfile

def fail(code, name, path, what):
    print(f"ERROR {code} {name} | {path} | {what}", file=sys.stderr); sys.exit(code)
HERE = os.path.dirname(os.path.abspath(__file__))
if not os.path.isfile(os.path.join(HERE, "path_patterns.py")):
    fail(24, "SCRIPT_MISSING", os.path.join(HERE, "path_patterns.py"), "keep path_patterns.py beside check_scripts.py")
sys.dont_write_bytecode = True   # read-only: importing path_patterns must not add a cache folder to the seed
sys.path.insert(0, HERE)
from path_patterns import path_hits

EXT_REF = (".txt", ".md", ".py", ".sh", ".ps1", ".csv")
SCRIPT_EXT = (".py", ".pyw", ".sh", ".ps1")
REF = re.compile(r"(?<![\w.-])([A-Za-z][A-Za-z0-9_-]*\.(?:pyw|py|sh|ps1))\b")

def read(f):
    b = open(f, "rb").read()
    try: return b.decode("utf-8")
    except UnicodeDecodeError: return b.decode("cp1252", errors="replace")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", required=True); ap.add_argument("--manifest")
    ap.add_argument("--ignore"); ap.add_argument("--strict", action="store_true")
    ap.add_argument("--probes", action="store_true"); ap.add_argument("--codes")
    a = ap.parse_args()
    seed = os.path.abspath(a.seed)
    if not os.path.isdir(seed): fail(12, "ROOT_MISSING", a.seed, "pass the seed folder with --seed")
    man = os.path.abspath(a.manifest or os.path.join(seed, "scripts", "SCRIPTS.txt"))
    if not os.path.isfile(man): fail(20, "FILE_MISSING", man, "no SCRIPTS manifest (format: name | job | path | status)")
    codes = os.path.abspath(a.codes or os.path.join(seed, "scripts", "ERROR_CODES.txt"))
    if a.probes and not os.path.isfile(codes): fail(20, "FILE_MISSING", codes, "no ERROR_CODES.txt for --probes (pass --codes)")
    ign = re.compile(a.ignore) if a.ignore else None
    listed, bad = {}, []
    for n, line in enumerate(read(man).splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#"): continue
        f = [x.strip() for x in s.split("|")]
        if f[0].lower() == "name": continue
        if len(f) != 4 or not all(f): bad.append(f"manifest line {n}: needs 'name | job | path | status'"); continue
        st = f[3].lower()
        if st not in ("shipped", "planned", "retired"): bad.append(f"manifest line {n}: status '{f[3]}' is not shipped, planned or retired"); continue
        listed[f[0]] = (f[2], st)
    refs = {}
    for d, dirs, files in os.walk(seed):
        dirs[:] = [x for x in dirs if x != ".git"]
        for fn in files:
            fp = os.path.join(d, fn)
            if not fn.endswith(EXT_REF) or os.path.abspath(fp) == man or re.fullmatch(r"(?i)CHANGELOG(\.[a-z0-9]+)?", fn): continue
            for m in REF.finditer(read(fp)):
                nm = m.group(1)
                if nm.startswith(("test_", "example")) or (ign and ign.search(nm)) or nm == fn: continue
                refs.setdefault(nm, os.path.relpath(fp, seed))
    present = {}
    for d, dirs, files in os.walk(seed):
        dirs[:] = [x for x in dirs if x != ".git"]
        for fn in files:
            if fn.endswith(SCRIPT_EXT): present.setdefault(fn, os.path.relpath(os.path.join(d, fn), seed))
    in_scripts = {fn for fn, rel in present.items() if rel.replace("\\", "/").startswith("scripts/")}
    names = sorted(set(listed) | set(refs) | in_scripts)
    c = dict(ok=0, missing=0, unlisted=0, planned=0, flip=0)
    for nm in names:
        where = f"referenced in {refs[nm]}" if nm in refs else "not referenced"
        if nm in listed:
            path, st = listed[nm]
            parts = re.split(r"[\\/]", path)
            if os.path.isabs(path) or re.match(r"^[A-Za-z]:", path) or ".." in parts:
                print(f"BADPATH | {nm} | {path} | {where}"); c["missing"] += 1; continue
            exists = os.path.isfile(os.path.join(seed, path))
            if st == "retired" and nm in refs: print(f"RETIRED | {nm} | {path} | still {where}"); c["missing"] += 1
            elif st == "retired": print(f"OK | {nm} | {path} | retired, not referenced"); c["ok"] += 1
            elif exists and st == "planned": print(f"FLIP | {nm} | {path} | listed planned but present; set status shipped; {where}"); c["flip"] += 1
            elif exists: print(f"OK | {nm} | {path} | {where}"); c["ok"] += 1
            elif st == "planned" and nm in refs: print(f"PLANNED | {nm} | {path} | {where}; not shipped yet"); c["planned"] += 1
            elif st == "planned": print(f"OK | {nm} | {path} | planned, not referenced"); c["ok"] += 1
            else: print(f"MISSING | {nm} | {path} | listed shipped, no file there; {where}"); c["missing"] += 1
        else:
            if nm in present: print(f"UNLISTED | {nm} | {present[nm]} | present, not in manifest; {where}"); c["unlisted"] += 1
            else: print(f"MISSING | {nm} | - | {where}; no file and not in manifest"); c["missing"] += 1  # v0.1.3: counted once
    for b in bad: print(f"BADLINE | {b}")
    hard = hardcoded(seed)
    pf = probes(seed, codes, listed) if a.probes else 0
    bad_run = c["missing"] > 0 or bool(bad) or hard > 0 or pf > 0 or (a.strict and (c["unlisted"] > 0 or c["flip"] > 0))
    print(f"CHECK_SCRIPTS {'FAIL' if bad_run else 'PASS'} | listed={len(listed)} referenced={len(refs)} ok={c['ok']} missing={c['missing']} unlisted={c['unlisted']} planned={c['planned']} flip={c['flip']} badlines={len(bad)} hardcoded={hard}" + (f" probe_failures={pf}" if a.probes else ""))
    return 1 if bad_run else 0

def hardcoded(seed):
    n, sd = 0, os.path.join(seed, "scripts")
    for d, dirs, files in os.walk(sd):
        dirs[:] = sorted(x for x in dirs if x not in (".git", "__pycache__"))
        for fn in sorted(files):
            if not fn.endswith(SCRIPT_EXT): continue
            fp = os.path.join(d, fn)
            for i, line in enumerate(read(fp).splitlines(), 1):
                if i == 1 and line.startswith("#!"): continue
                h = path_hits(line)
                if h: print(f"HARDCODED | {os.path.relpath(fp, seed)}:{i} | {', '.join(h)}"); n += 1
    return n

USED = re.compile(r"\bfail\((\d+)|\bdie (\d+)|sys\.exit\((\d+)\)|\bexit (\d+)|return (\d+)\b|ERROR (\d+) |WARN (\d+) ")

def probes(seed, codes, listed):
    sd = os.path.join(seed, "scripts"); text = read(codes); known, rows, import_only, nf = set(), [], set(), 0
    sect = None
    for ln in text.splitlines():
        if ln.startswith("code |"): sect = "codes"; continue
        if ln.startswith("script |"): sect = "probes"; continue
        m = re.match(r"\s*Import only[^:]*:\s*(.+)", ln, re.I)
        if m: import_only |= {x.strip() for x in m.group(1).split(",") if x.strip()}; continue
        p = [x.strip() for x in ln.split("|")]
        if sect == "codes" and p and p[0].isdigit(): known.add(int(p[0]))
        elif sect == "probes" and len(p) == 3 and p[2].isdigit(): rows.append((p[0], p[1], int(p[2])))
    probed = {r[0] for r in rows}
    for nm, (path, st) in sorted(listed.items()):
        if st == "shipped" and path.replace("\\", "/").startswith("scripts/") and nm.endswith(SCRIPT_EXT) and nm not in probed and nm not in import_only:
            print(f"NOPROBE | {nm} | no PROBES line in {os.path.basename(codes)}"); nf += 1
    for fn in sorted(os.listdir(sd)):
        if not fn.endswith(SCRIPT_EXT): continue
        used = {int(g) for m in USED.finditer(read(os.path.join(sd, fn))) for g in m.groups() if g}
        for u in sorted(used - known): print(f"CODE_UNKNOWN | {fn} | exit code {u} is not in {os.path.basename(codes)}"); nf += 1
    for script, args, want in rows:
        sp = os.path.join(sd, script)
        if not os.path.isfile(sp): print(f"PROBE | {script} | {args} | script not found | WRONG"); nf += 1; continue
        with tempfile.TemporaryDirectory() as tmp:
            empty = os.path.join(tmp, "empty"); os.mkdir(empty); miss = os.path.join(tmp, "missing_probe_path")
            argv = [x.replace("{MISSING}", miss).replace("{EMPTY}", empty).replace("{SCRIPTS}", sd) for x in shlex.split(args)]
            cmd = (["bash", sp] if script.endswith(".sh") else [sys.executable, sp]) + argv
            try: r = subprocess.run(cmd, capture_output=True, text=True, cwd=tmp, timeout=120)
            except subprocess.TimeoutExpired: print(f"PROBE | {script} | {args} | timed out | WRONG"); nf += 1; continue
            why = []
            if r.returncode != want: why.append(f"expected {want} got {r.returncode}")
            if want >= 10 and not re.search(rf"^(ERROR|WARN) {want} ", r.stderr, re.M): why.append(f"no 'ERROR {want}' line on standard error")
            if want >= 10 and "{MISSING}" in args and miss not in r.stderr: why.append("the message does not name the missing path")
            print(f"PROBE | {script} | {args} | expected {want} got {r.returncode} | " + ("OK" if not why else "WRONG: " + "; ".join(why)))
            nf += bool(why)
    return nf

if __name__ == "__main__":
    sys.exit(main())
