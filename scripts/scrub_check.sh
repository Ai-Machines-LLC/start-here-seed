#!/usr/bin/env bash
# scrub_check.sh (v0.8.0) - FAILS if the seed holds secrets or anything specific to one owner.
# Why: the seed must rebuild a bot system for anyone, so it may carry no names, companies, emails, domains,
# user paths, IDs or customer terms. Owner-specific terms live in a denylist OUTSIDE the repo (one
# case-sensitive regex per line), passed as $1. Usage: scripts/scrub_check.sh /path/to/denylist.txt [dir]
# Exit codes (scripts/ERROR_CODES.txt): 0 PASS, 1 findings, 2 usage, 12 the folder to scan is missing, 20 denylist missing,
# 23 grep missing. v0.8.0 (on v0.7.3): startup checks run before any scan; a missing denylist stops the run (was a FAIL line).
# The default folder is the one above this script (relative, never a fixed path).
set -u
die() { echo "ERROR $1 $2 | $3 | $4" >&2; exit "$1"; }
deny="${1:-}"; root="${2:-$(cd "$(dirname "$0")/.." && pwd)}"; root="${root%/}"; [ -n "$root" ] || root=/; fail=0
# v0.7.3: a trailing slash on [dir] is trimmed so the repo-root libraries/ allowance below still matches
[ -n "$deny" ] || { echo "usage: scrub_check.sh <denylist> [folder]" >&2; exit 2; }
[ -f "$deny" ] || die 20 FILE_MISSING "$deny" "denylist not found (it lives outside the seed; pass its path as the first argument)"
[ -d "$root" ] || die 12 ROOT_MISSING "$root" "folder to scan not found"
command -v grep >/dev/null 2>&1 || die 23 TOOL_MISSING grep "install grep"
scan() { grep -rInE --exclude-dir=.git --exclude=scrub_check.sh "$@" "$root"; }
# 1 generic patterns (case-insensitive): emails, URLs/domains, user paths, GUIDs, assigned secrets, private keys
pat_email='[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+\.)+[A-Za-z]{2,}'
pat_domain='(https?://|www\.)[^[:space:]]+|\b[a-z0-9-]+(\.[a-z0-9-]+)*\.(com|net|org|edu|gov|mil|int|io|co|us|uk|ca|de|fr|eu|au|in|jp|cn|ai|dev|app|biz|info|me|tech|cloud|xyz|site|online|llc|inc|sharepoint|onmicrosoft)([^.A-Za-z0-9_-]|$)'
pat_path='[A-Za-z]:[\]Users[\][^\\[:space:]]+|/(home|Users)/[A-Za-z0-9._-]+'
pat_guid='\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b'
pat_secret='(password|passwd|secret|api[_-]?key|token)[[:space:]]*[:=][[:space:]]*[^[:space:]{]|BEGIN [A-Z ]*PRIVATE KEY'
# repo-root libraries/ entries are link-out pages to public vendor manuals, so URLs/domains are allowed there only
# (v0.7.2: the whole tree is scanned and only "$root/libraries/" hits are dropped; a nested libraries/ folder still fails)
for name in email path guid secret; do
  var="pat_$name"; if scan -i "${!var}"; then echo "FAIL generic:$name"; fail=1; fi
done
out=$(scan -i "$pat_domain" | grep -v "^$root/libraries/")
if [ -n "$out" ]; then printf '%s\n' "$out"; echo "FAIL generic:domain"; fail=1; fi
# 2 denylist (names, companies, bot names, customer terms) kept outside the repo
if scan -f <(grep -v '^[[:space:]]*\(#\|$\)' "$deny"); then echo "FAIL denylist"; fail=1; fi
# 3 commit history (inside a git repo): authors, committers and messages must be generic too
if git -C "$root" rev-parse --git-dir >/dev/null 2>&1; then
  meta=$(git -C "$root" log --all --format='%an|%ae|%cn|%ce|%s|%b' 2>/dev/null)
  bad=$(printf '%s\n' "$meta" | grep -iE "$pat_email|$pat_path|$pat_guid")
  [ -n "$deny" ] && [ -f "$deny" ] && bad="$bad$(printf '%s\n' "$meta" | grep -E -f <(grep -v '^[[:space:]]*\(#\|$\)' "$deny"))"
  if [ -n "$bad" ]; then printf '%s\n' "$bad"; echo "FAIL commit metadata"; fail=1; fi
fi
# 5 platform-neutral: platform names, tool names and platform features appear only in PLATFORMS.txt
pat_platform='\b(grok|x\.?ai|cursor|chatgpt|openai|gpts?|claude|anthropic|gemini|bard|copilot|ollama|llama|mistral|mcp|connectors?|routines?|subagent_type|sendtoagent|updateavatar|updateprofile|updateroutine|calldynamictool|getdynamictools|the box)\b'
if grep -rInE -i --exclude-dir=.git --exclude=scrub_check.sh --exclude=PLATFORMS.txt "$pat_platform" "$root"; then echo "FAIL platform-specific term (move it to PLATFORMS.txt or say it generically)"; fail=1; fi
# 4 START HERE template cap
f="$root/START_HERE.template.txt"; if [ -f "$f" ]; then n=$(wc -l < "$f"); [ "$n" -le 60 ] || { echo "FAIL START HERE $n lines > 60"; fail=1; }; fi
[ $fail -eq 0 ] && echo "PASS scrub_check ($(find "$root" -type f -not -path '*/.git/*' | wc -l) files)"; exit $fail
