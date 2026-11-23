#!/usr/bin/env python3
"""library_intake_scan.py v0.1.1 (review build) - the librarian runs this on every incoming library before it is accepted.
Why: a library must carry no paths, personal data, machine data or secrets (H5, H26), so a new system can use it as is.
Usage: library_intake_scan.py --dir <incoming library folder> --config <USER_CONFIG file> [--max-mb 20]
  --config  a "KEY = value" file (USER_CONFIG, or a .conf it names). Keys read:
              INTAKE_DENY       comma-separated names, companies and emails that must not appear (required, may be empty
                                only if INTAKE_DENY_FILE is given)
              INTAKE_DENY_FILE  optional file of more terms, one per line ('#' lines skipped); a relative path is taken
                                from the config file's own folder
            No names or emails are written in this script; they come only from the config. No environment variables.
What is flagged, one line per hit, "HIT | <file>:<line> | <kind>" (the matched text is never printed, so a secret or a
personal detail is not copied into a log):
  path:<name>   any hardcoded path from path_patterns.py (the same list check_scripts.py uses)
  email         any email address
  deny          a term from the config's denylist (whole word, any case)
  machine:<x>   an IPv4 address other than 0.0.0.0 and 127.x, a MAC address, a GUID, or a computer name like DESKTOP-XXXX
  cred:<x>      an assigned password, token or key; a private key block; or a known token shape
Files that are not text (a zero byte in the first 4 KB) or larger than --max-mb are listed as SKIPPED_BINARY or SKIPPED_LARGE
and count as hits, so nothing unread is accepted.
Last line: INTAKE PASS|FAIL | files=N hits=N skipped=N
Exit (scripts/ERROR_CODES.txt): 0 clean, 40 SCAN_HITS, 2 usage, 10 config missing, 11 INTAKE_DENY and INTAKE_DENY_FILE both
  missing from the config, or either one still '?' (the template's UNFILLED mark; v0.1.1, Lead #242), 20 INTAKE_DENY_FILE missing, 21 --dir missing, 24 path_patterns.py not beside this script.
Read-only. Standard library only. Text read as UTF-8, else cp1252."""
import argparse, os, re, sys

def fail(code, name, path, what):
    print(f"ERROR {code} {name} | {path} | {what}", file=sys.stderr); sys.exit(code)
HERE = os.path.dirname(os.path.abspath(__file__))
if not os.path.isfile(os.path.join(HERE, "path_patterns.py")):
    fail(24, "SCRIPT_MISSING", os.path.join(HERE, "path_patterns.py"), "keep path_patterns.py beside library_intake_scan.py")
sys.dont_write_bytecode = True   # read-only: importing path_patterns must not add a cache folder to the seed
sys.path.insert(0, HERE)
from path_patterns import path_hits

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}")
MACHINE = [
    ("ipv4", re.compile(r"(?<![\d.])(?!0\.0\.0\.0(?![\d.]))(?!127\.)(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}(?![\d.])")),
    ("mac", re.compile(r"(?i)\b[0-9a-f]{2}(?::[0-9a-f]{2}){5}\b|\b[0-9a-f]{2}(?:-[0-9a-f]{2}){5}\b")),
    ("guid", re.compile(r"(?i)\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b")),
    ("computer_name", re.compile(r"\b(?:DESKTOP|LAPTOP|WIN)-[A-Z0-9]{5,}\b")),
]
CRED = [
    ("assigned", re.compile(r"(?i)\b(?:password|passwd|pwd|secret|api[_-]?key|access[_-]?key|token|client[_-]?secret)\b\s*[:=]\s*[\"']?[^\s\"'{<]{4,}")),
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("token_shape", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|xox[abpr]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{30,})")),
]

def read_cfg(path):
    cfg = {}
    for ln in open(path, encoding="utf-8-sig", errors="replace"):
        if "=" in ln and not ln.lstrip().startswith("#"):
            k, v = ln.split("=", 1); cfg[k.strip().upper()] = v.strip()
    return cfg

def text_of(fp):
    b = open(fp, "rb").read()
    if b"\0" in b[:4096]: return None
    try: return b.decode("utf-8")
    except UnicodeDecodeError: return b.decode("cp1252", errors="replace")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True); ap.add_argument("--config", required=True); ap.add_argument("--max-mb", type=float, default=20)
    a = ap.parse_args()
    if not os.path.isdir(a.dir): fail(21, "FOLDER_MISSING", a.dir, "incoming library folder not found")
    if not os.path.isfile(a.config): fail(10, "CONFIG_MISSING", a.config, "pass USER_CONFIG (or the .conf it names) with --config")
    cfg = read_cfg(a.config)
    if "INTAKE_DENY" not in cfg and "INTAKE_DENY_FILE" not in cfg:
        fail(11, "CONFIG_KEY_MISSING", "INTAKE_DENY", f"add INTAKE_DENY (and/or INTAKE_DENY_FILE) to {a.config}")
    for k in ("INTAKE_DENY", "INTAKE_DENY_FILE"):   # '?' is the template's UNFILLED mark, never a deny term or a file name
        if cfg.get(k) == "?": fail(11, "CONFIG_KEY_MISSING", k, f"{k} not filled (still '?') in {a.config}")
    terms = [t.strip() for t in cfg.get("INTAKE_DENY", "").split(",") if t.strip()]
    if cfg.get("INTAKE_DENY_FILE"):
        df = cfg["INTAKE_DENY_FILE"]
        if not os.path.isabs(df): df = os.path.join(os.path.dirname(os.path.abspath(a.config)), df)
        if not os.path.isfile(df): fail(20, "FILE_MISSING", df, "INTAKE_DENY_FILE not found")
        terms += [l.strip() for l in open(df, encoding="utf-8-sig", errors="replace") if l.strip() and not l.lstrip().startswith("#")]
    deny = re.compile(r"(?i)(?<![\w])(?:" + "|".join(re.escape(t) for t in terms) + r")(?![\w])") if terms else None
    files = hits = skipped = 0
    for d, dirs, fns in os.walk(a.dir):
        dirs[:] = sorted(x for x in dirs if x != ".git")
        for fn in sorted(fns):
            fp = os.path.join(d, fn); rel = os.path.relpath(fp, a.dir); files += 1
            for kind in path_hits(rel): print(f"HIT | {rel}:0 | path:{kind} (in the file name)"); hits += 1
            if deny and deny.search(rel): print(f"HIT | {rel}:0 | deny (in the file name)"); hits += 1
            if os.path.getsize(fp) > a.max_mb * 1024 * 1024: print(f"SKIPPED_LARGE | {rel} | over {a.max_mb} MB, not read"); skipped += 1; continue
            t = text_of(fp)
            if t is None: print(f"SKIPPED_BINARY | {rel} | not text, not read"); skipped += 1; continue
            for i, line in enumerate(t.splitlines(), 1):
                kinds = ["path:" + k for k in path_hits(line)]
                if EMAIL.search(line): kinds.append("email")
                if deny and deny.search(line): kinds.append("deny")
                kinds += ["machine:" + k for k, rx in MACHINE if rx.search(line)]
                kinds += ["cred:" + k for k, rx in CRED if rx.search(line)]
                if kinds: print(f"HIT | {rel}:{i} | {', '.join(kinds)}"); hits += 1
    bad = hits + skipped
    print(f"INTAKE {'FAIL' if bad else 'PASS'} | files={files} hits={hits} skipped={skipped}")
    return 40 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
