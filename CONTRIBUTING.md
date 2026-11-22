# Contributing improvements back (v0.5.0 draft)
Other users run their own bot systems from this seed. When yours finds a better rule, send it back so every system improves.

## What to send
- One change per proposal: the file, the exact old text, the exact new text, and a one-line why (H22).
- Evidence: what went wrong or got slow (log line, correction, time taken). No customer data, names, companies, emails, paths, IDs or secrets.
- For START HERE changes: show it still fits in 60 lines.

## How (users outside the seed owner's team: suggestions only)
1. Write the proposal, run `scripts/scrub_check.sh <your denylist>` on it, and paste its output in.
2. Send it to the seed owner's private intake (write-only for you; see proposals/CORRECTIONS_INTAKE.txt, pending approval) or straight to the seed owner. Never post it in public issues. Outside users never push or commit here.
3. The seed owner's team marks it OPEN, FIXED <version> or WONTFIX <why>, tests it, a non-author reviewer checks only the changed lines (H19, H23), and the owner's team commits it.
You see the result as a fix note in CHANGELOG.md. Local changes for your own system go in your LOCAL START HERE, not here.

## Commit rules (all contributors, including bots)
- History must never contain private data: commit only reviewed, scrubbed revisions; the first commit must already be clean.
- Use a generic identity, never a real person or company: `git -c user.name=seed-bot -c user.email=noreply commit ...`
- Commit messages say what changed and why, with no names, customers or paths.
- `scripts/scrub_check.sh` also scans commit authors and messages when run inside the repo.
