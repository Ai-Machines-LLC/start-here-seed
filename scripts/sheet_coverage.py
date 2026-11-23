#!/usr/bin/env python3
"""sheet_coverage.py 0.1.1 (review build) - flags any START HERE rule or CHECK that has no answer-sheet item (stdlib only).
Why (the Designer, 2026-11-23 3:52 PM ET, relayed by the Lead: "Maybe our test is shit." / "The test didn't even include the
most basic part"): the answer sheet is generated from START HERE itself, so a new or changed rule can never go untested.
Usage:
  sheet_coverage.py --page TAG=<START HERE file> [--page TAG2=<file> ...] --emit            print one COVER row per rule/CHECK
  sheet_coverage.py --page TAG=<file> [...] --sheet <answer sheet>                         check the sheet covers every row
ROWS (one per rule, one per CHECK; ids are stable across line moves):
  <TAG>.<H id>               every hard rule: a line that starts with H<n> (e.g. LOCAL.H1).
  <TAG>.<ANCHOR>.C<k>        the k-th CHECK under ANCHOR. ANCHOR is the line's H id; else a leading CAPS label before ':' or
                             '(' (e.g. FALLBACK); else, for an indented continuation line, the anchor above it.
  Each row carries h=<first 8 hex of sha256 of the rule line or CHECK sentence>, so an edited rule shows as CHANGED.
SHEET FORMAT: lines "COVER | <row id> | h=<hash> | <item ids, comma-separated> | <how it is verified>". Item ids must be
  defined on the sheet as lines starting with the id followed by two spaces (e.g. "G1  ...", "S3  ...", "R12  ...").
FINDINGS (exit 1): MISSING row not on the sheet; CHANGED hash differs (re-check the item, then update h=); STALE sheet row
  for a rule no page has now; NO_ITEM a COVER row with no item, or naming an item the sheet does not define; NO_METHOD.
Exit (scripts/ERROR_CODES.txt): 0 every row covered; 1 findings; 2 usage; 20 a --page or --sheet file missing; 30 a page
  with no H rules (wrong file). Paths come only from the command line."""
import argparse, hashlib, os, re, sys
ap = argparse.ArgumentParser()
ap.add_argument("--page", action="append", required=True, help="TAG=path of a START HERE page (LOCAL, SEED, ...)")
ap.add_argument("--sheet"); ap.add_argument("--emit", action="store_true")
a = ap.parse_args()
if bool(a.sheet) == bool(a.emit): ap.error("give exactly one of --sheet or --emit")
def fail(code, name, path, what): print(f"ERROR {code} {name} | {path} | {what}", file=sys.stderr); sys.exit(code)
pages = []
for pv in a.page:
    tag, eq, path = pv.partition("=")
    if not eq or not re.fullmatch(r"[A-Z][A-Z0-9_]*", tag): ap.error(f"--page needs TAG=path with an upper-case TAG: {pv}")
    if not os.path.isfile(path): fail(20, "FILE_MISSING", path, f"--page {tag} not found")
    pages.append((tag, path))
if a.sheet and not os.path.isfile(a.sheet): fail(20, "FILE_MISSING", a.sheet, "--sheet not found")
h8 = lambda s: hashlib.sha256(" ".join(s.split()).encode("utf-8")).hexdigest()[:8]
LABEL = re.compile(r"^\s*([A-Z][A-Z0-9'/&-]*(?:[ ,][A-Z0-9'/&-]+)*)\s*[:(]")
CHECK = re.compile(r"CHECK:\s*(.+?\.)(?=\s|$)|CHECK:\s*(.+)$")
def rows_of(tag, path):
    out, anchor, k = [], None, {}
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    for no, l in enumerate(lines, 1):
        defs = [(m.start(1), m.group(1)) for m in re.finditer(r"(?:^|(?<=[.)?]\s))(H\d+)\s+[A-Z][A-Z?]", l)]
        if defs and defs[0][0] == 0:
            anchor = defs[0][1]
        elif LABEL.match(l) and not l.startswith("    "):
            anchor = re.sub(r"[^A-Z0-9]+", "_", LABEL.match(l).group(1)).strip("_")
        elif not l.startswith(" "):
            anchor = None
        line_anchor = anchor
        for pos, hid in defs:
            seg_end = next((p for p, _ in defs if p > pos), len(l))
            out.append((f"{tag}.{hid}", h8(l[pos:seg_end]), no, l[pos:seg_end].strip()[:110]))
        for c in CHECK.finditer(l):
            an = next((hid for pos, hid in reversed(defs) if pos < c.start()), line_anchor) or f"L{no}"
            k[an] = k.get(an, 0) + 1
            txt = c.group(1) or c.group(2)
            out.append((f"{tag}.{an}.C{k[an]}", h8(txt), no, "CHECK: " + txt.strip()[:100]))
        if defs: anchor = defs[-1][1] if defs[0][0] == 0 else anchor
    if not any(re.fullmatch(r"[A-Z]+\.H\d+", r[0]) for r in out): fail(30, "BAD_FORMAT", path, "no H<n> rule lines; is this a START HERE page?")
    return out
rows = [r for t, p in pages for r in rows_of(t, p)]
dup = sorted({r[0] for r in rows if [x[0] for x in rows].count(r[0]) > 1})
if dup: fail(30, "BAD_FORMAT", ",".join(p for _, p in pages), f"duplicate row ids {dup}")
if a.emit:
    for rid, h, no, txt in rows: print(f"COVER | {rid} | h={h} | ? | ?   # L{no} {txt}")
    print(f"ROWS {len(rows)}"); sys.exit(0)
sheet = open(a.sheet, encoding="utf-8", errors="replace").read().splitlines()
items = {m.group(1) for l in sheet for m in [re.match(r"^([A-Z]\d+[a-z]?)  ", l)] if m}
cover = {}
for l in sheet:
    if l.startswith("COVER |"):
        f = [x.strip() for x in l.split("|")]
        if len(f) >= 5: cover[f[1]] = (f[2].removeprefix("h="), [i.strip() for i in f[3].split(",") if i.strip()], f[4].split("#")[0].strip())
find = []
for rid, h, no, txt in rows:
    if rid not in cover: find.append(f"MISSING | {rid} | L{no} {txt}"); continue
    ch, its, how = cover[rid]
    if ch != h: find.append(f"CHANGED | {rid} | sheet h={ch} page h={h} | L{no} {txt}")
    bad = [i for i in its if i not in items]
    if not its or "?" in its or bad: find.append(f"NO_ITEM | {rid} | items {its or 'none'} undefined {bad or 'none'}")
    if not how or how == "?": find.append(f"NO_METHOD | {rid}")
ids = {r[0] for r in rows}
find += [f"STALE | {rid} | no page has this row now" for rid in cover if rid not in ids]
for x in find: print(x)
print(f"SHEET_COVERAGE {'PASS' if not find else 'FAIL'} | pages {[t for t, _ in pages]} | rows {len(rows)} | covered {sum(1 for r in rows if r[0] in cover)} | findings {len(find)} | items defined {len(items)}")
sys.exit(1 if find else 0)
