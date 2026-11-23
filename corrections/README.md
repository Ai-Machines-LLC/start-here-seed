# Corrections log

This folder holds the maintaining team's own corrections. Each time the system owner corrects one of their bots, the correction is turned into a generic lesson so that every user's seed learns from it.

- Outside contributors still follow CONTRIBUTING.md step 2. This folder is only for corrections the maintaining team writes itself. Its designated member commits them to `main` after a scrub and a non-author review.
- One file per correction: `corrections/YYYY-MM-DD_HHMM_<role>.txt`. The time is when the owner gave the correction, and the role is generic (for example `controller` or `builder`). There are no bot names, people, companies, customers, paths or IDs.
- Each file has these lines:
  - `CORRECTION:` what went wrong, in generic words
  - `TAGS:` optional, for example `UNVERIFIED-DONE`
  - `RULE:` the file and rule it changes
  - `OLD:` the exact current text being changed
  - `NEW:` the exact proposed text
  - `STATUS:` OPEN, FIXED <seed version> or WONTFIX <why>
- One file per correction means writers never share a file, so no entry can be lost to a same-minute overwrite.
- Before any commit, every file passes `scripts/scrub_check.sh` and a non-author review (H19). Commits use the generic identity in CONTRIBUTING.md.
- Fixed entries also get a fix note in CHANGELOG.md.
