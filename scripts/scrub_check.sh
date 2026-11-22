#!/usr/bin/env bash
# scrub_check.sh (v0.7.0) - FAILS if the seed holds secrets or anything specific to one owner.
# Why: the seed must rebuild a bot system for anyone, so it may carry no names, companies, emails, domains,
# user paths, IDs or customer terms. Owner-specific terms live in a denylist OUTSIDE the repo (one
# case-sensitive regex per line), passed as $1. Usage: scripts/scrub_check.sh /path/to/denylist.txt [dir]
set -u
deny="${1:-}"; root="${2:-$(cd "$(dirname "$0")/.." && pwd)}"; fail=0
scan() { grep -rInE --exclude-dir=.git --exclude=scrub_check.sh "$@" "$root"; }
# 1 generic patterns (case-insensitive): emails, URLs/domains, user paths, GUIDs, assigned secrets, private keys
pat_email='[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+\.)+[A-Za-z]{2,}'
pat_domain='(https?://|www\.)[^[:space:]]+|\b[a-z0-9-]+(\.[a-z0-9-]+)*\.(com|net|org|edu|gov|mil|int|io|co|us|uk|ca|de|fr|eu|au|in|jp|cn|ai|dev|app|biz|info|me|tech|cloud|xyz|site|online|llc|inc|sharepoint|onmicrosoft)([^.A-Za-z0-9_-]|$)'
pat_path='[A-Za-z]:\\Users\\[^\\[:space:]]+|/(home|Users)/[A-Za-z0-9._-]+'
pat_guid='\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b'
pat_secret='(password|passwd|secret|api[_-]?key|token)[[:space:]]*[:=][[:space:]]*[^[:space:]{]|BEGIN [A-Z ]*PRIVATE KEY'
for name in email domain path guid secret; do
  var="pat_$name"; if scan -i "${!var}"; then echo "FAIL generic:$name"; fail=1; fi
done
# 2 denylist (names, companies, bot names, customer terms) kept outside the repo
if [ -z "$deny" ] || [ ! -f "$deny" ]; then echo "FAIL denylist missing (pass its path as \$1)"; fail=1
elif scan -f <(grep -v '^[[:space:]]*\(#\|$\)' "$deny"); then echo "FAIL denylist"; fail=1; fi
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
