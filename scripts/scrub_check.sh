#!/usr/bin/env bash
# scrub_check.sh (v0.8.3) - FAILS if the seed holds secrets or anything specific to one owner.
# Why: the seed must rebuild a bot system for anyone, so it may carry no names, companies, emails, domains,
# user paths, IDs or customer terms. Owner-specific terms live in a denylist OUTSIDE the repo (one
# case-sensitive regex per line), passed as $1. Usage: scripts/scrub_check.sh /path/to/denylist.txt [dir] [owner-allowlist]
# v0.8.3 (built on v0.8.2): "routine" in its machine-control sense is not a platform term, but only when the
# phrase names ladder, robot or PLC (e.g. "PLC fault routine", "robot routine", "a routine in the PLC"); those
# phrases are removed from a hit line before it is judged. A bare "main/event/periodic routine" still FAILS.
# Exit codes (scripts/ERROR_CODES.txt): 0 PASS, 1 findings, 2 usage, 12 the folder to scan is missing, 20 denylist missing,
# 23 grep missing. v0.8.0 (on v0.7.3): startup checks run before any scan; a missing denylist stops the run (was a FAIL line).
# The default folder is the one above this script (relative, never a fixed path).
set -u
die() { echo "ERROR $1 $2 | $3 | $4" >&2; exit "$1"; }
deny="${1:-}"; root="${2:-$(cd "$(dirname "$0")/.." && pwd)}"; root="${root%/}"; [ -n "$root" ] || root=/; fail=0
allow="${3:-}"; [ -z "$allow" ] || [ -f "$allow" ] || die 20 FILE_MISSING "$allow" "owner allow list not found (it lives outside the seed)"
# v0.7.3: a trailing slash on [dir] is trimmed so the repo-root libraries/ allowance below still matches
[ -n "$deny" ] || { echo "usage: scrub_check.sh <denylist> [folder] [owner-allowlist]" >&2; exit 2; }
[ -f "$deny" ] || die 20 FILE_MISSING "$deny" "denylist not found (it lives outside the seed; pass its path as the first argument)"
[ -d "$root" ] || die 12 ROOT_MISSING "$root" "folder to scan not found"
command -v grep >/dev/null 2>&1 || die 23 TOOL_MISSING grep "install grep"
scan() { grep -rInEZ --exclude-dir=.git --exclude=scrub_check.sh "$@" "$root" | drop_owner_links; }
# v0.8.1 owner links exception (the Designer: owner links live on the repo page only, never in START HERE).
# Root README.md may hold ONE block between a line starting "<!-- OWNER-LINKS BEGIN" and the line
# "<!-- OWNER-LINKS END -->", at most 8 lines inside. The tree scans skip only those lines of that exact file
# (grep -Z puts a NUL after the file name, so a file named "README.md:79" is not mistaken for it). The block is
# then checked by itself: every allow-list entry is removed only where it ends at a space, a closing bracket,
# a quote, a comma, a semicolon or the line end (so a longer link under an allowed one is not removed), and
# any email, domain, user path, GUID, assigned secret, private key marker or denylist hit left FAILS (v0.8.2).
# With no allow list (argument 3) the block gets no exception. A bad marker set or a longer block FAILS.
readme="$root/README.md"; ol_lo=0; ol_hi=0
if [ -f "$readme" ]; then
  nb=$(grep -c '^<!-- OWNER-LINKS BEGIN' "$readme"); ne=$(grep -cx '<!-- OWNER-LINKS END -->' "$readme")
  if [ "$nb" -gt 1 ] || [ "$ne" -gt 1 ] || [ "$nb" -ne "$ne" ]; then echo "FAIL owner links markers (need exactly one BEGIN and one END)"; fail=1
  elif [ "$nb" -eq 1 ] && [ -n "$allow" ]; then
    ol_lo=$(grep -n '^<!-- OWNER-LINKS BEGIN' "$readme" | cut -d: -f1); ol_hi=$(grep -nx '<!-- OWNER-LINKS END -->' "$readme" | cut -d: -f1)
    if [ "$ol_hi" -le "$ol_lo" ] || [ $((ol_hi-ol_lo-1)) -gt 8 ]; then echo "FAIL owner links block (END before BEGIN or more than 8 lines)"; fail=1; ol_lo=0; ol_hi=0; fi
  fi
fi
drop_owner_links() { awk -v f="$readme" -v lo="$ol_lo" -v hi="$ol_hi" 'BEGIN{FS="\0"} { if (hi>0 && $1==f) { n=$2; sub(/:.*/,"",n); n=n+0; if (n>=lo && n<=hi) next } sub(/\0/,":"); print }'; }
check_owner_block() {
  [ "$ol_hi" -gt 0 ] || return 0
  local i=0 line t bad=0
  mapfile -t terms < <(grep -v '^[[:space:]]*\(#\|$\)' "$allow")
  while IFS= read -r line; do
    i=$((i+1)); n=$((ol_lo+i-1))
    for t in "${terms[@]}"; do e=$(printf '%s' "$t" | sed 's/[]\/$*.^[|+?(){}]/\\&/g'); line=$(printf '%s\n' "$line" | sed -E "s/${e}([[:space:]>)\"',;]|\$)/\\1/g"); done
    if printf '%s\n' "$line" | grep -qiE "$pat_email|$pat_domain|$pat_path|$pat_guid|$pat_secret" || printf '%s\n' "$line" | grep -qE -f <(grep -v '^[[:space:]]*\(#\|$\)' "$deny"); then
      echo "$readme:$n: owner links block holds a term or link not on the allow list"; bad=1; fi
  done < <(sed -n "${ol_lo},${ol_hi}p" "$readme")
  [ $bad -eq 0 ] || { echo "FAIL owner links block"; fail=1; }
}
# 1 generic patterns (case-insensitive): emails, URLs/domains, user paths, GUIDs, assigned secrets, private keys
pat_email='[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+\.)+[A-Za-z]{2,}'
pat_domain='(https?://|www\.)[^[:space:]]+|\b[a-z0-9-]+(\.[a-z0-9-]+)*\.(com|net|org|edu|gov|mil|int|io|co|us|uk|ca|de|fr|eu|au|in|jp|cn|ai|dev|app|biz|info|me|tech|cloud|xyz|site|online|llc|inc|sharepoint|onmicrosoft)([^.A-Za-z0-9_-]|$)'
pat_path='[A-Za-z]:[\]Users[\][^\\[:space:]]+|/(home|Users)/[A-Za-z0-9._-]+'
pat_guid='\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b'
pat_secret='(password|passwd|secret|api[_-]?key|token)[[:space:]]*[:=][[:space:]]*[^[:space:]{]|BEGIN [A-Z ]*PRIVATE KEY'
# repo-root libraries/ entries are link-out pages to public vendor manuals, so URLs/domains are allowed there only
# (v0.7.2: the whole tree is scanned and only "$root/libraries/" hits are dropped; a nested libraries/ folder still fails)
for name in email path guid secret; do
  var="pat_$name"; o=$(scan -i "${!var}"); if [ -n "$o" ]; then printf '%s\n' "$o"; echo "FAIL generic:$name"; fail=1; fi
done
out=$(scan -i "$pat_domain" | grep -v "^$root/libraries/")
if [ -n "$out" ]; then printf '%s\n' "$out"; echo "FAIL generic:domain"; fail=1; fi
check_owner_block
# 2 denylist (names, companies, bot names, customer terms) kept outside the repo
o=$(scan -f <(grep -v '^[[:space:]]*\(#\|$\)' "$deny")); if [ -n "$o" ]; then printf '%s\n' "$o"; echo "FAIL denylist"; fail=1; fi
# 3 commit history (inside a git repo): authors, committers and messages must be generic too
if git -C "$root" rev-parse --git-dir >/dev/null 2>&1; then
  meta=$(git -C "$root" log --all --format='%an|%ae|%cn|%ce|%s|%b' 2>/dev/null)
  bad=$(printf '%s\n' "$meta" | grep -iE "$pat_email|$pat_path|$pat_guid")
  [ -n "$deny" ] && [ -f "$deny" ] && bad="$bad$(printf '%s\n' "$meta" | grep -E -f <(grep -v '^[[:space:]]*\(#\|$\)' "$deny"))"
  if [ -n "$bad" ]; then printf '%s\n' "$bad"; echo "FAIL commit metadata"; fail=1; fi
fi
# 5 platform-neutral: platform names, tool names and platform features appear only in PLATFORMS.txt
pat_platform='\b(grok|x\.?ai|cursor|chatgpt|openai|gpts?|claude|anthropic|gemini|bard|copilot|ollama|llama|mistral|mcp|connectors?|routines?|subagent_type|sendtoagent|updateavatar|updateprofile|updateroutine|calldynamictool|getdynamictools|the box)\b'
pat_plc_a='\b(ladder|robot|plc)( (logic|program|fault|main|power[- ]?up|startup|motion|homing|home|recovery|interrupt|event|periodic))?[ -]routines?\b'
pat_plc_b='\broutines? (in|of|inside|within) (the |a |an |this |that )?(ladder|robot|plc)\b'
out=$(grep -rInE -i --exclude-dir=.git --exclude=scrub_check.sh --exclude=PLATFORMS.txt "$pat_platform" "$root" | while IFS= read -r hit; do
  rest=$(printf '%s\n' "$hit" | sed -E "s/$pat_plc_a/ /Ig; s/$pat_plc_b/ /Ig"); printf '%s\n' "$rest" | grep -qiE "$pat_platform" && printf '%s\n' "$hit"; done)
if [ -n "$out" ]; then printf '%s\n' "$out"; echo "FAIL platform-specific term (move it to PLATFORMS.txt or say it generically)"; fail=1; fi
# 4 START HERE template cap
f="$root/START_HERE.template.txt"; if [ -f "$f" ]; then n=$(wc -l < "$f"); [ "$n" -le 60 ] || { echo "FAIL START HERE $n lines > 60"; fail=1; }; fi
[ $fail -eq 0 ] && echo "PASS scrub_check ($(find "$root" -type f -not -path '*/.git/*' | wc -l) files)"; exit $fail
