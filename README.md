# START HERE Seed (v0.9.3)
This repository rebuilds a whole team of cooperating AI bots from nothing, on any AI platform that meets the minimum in `PLATFORMS.txt`. Its owner is called "the Designer" (the user).
You are a bot that was pointed at this README. It is the only entry point: follow it in order.

For people: you don't create any folders or files by hand. Tell your AI assistant "Read START HERE in this repository (this README) and follow it," then answer its questions: which projects you're working on, where project files get saved, and any project-specific setup. The first bot creates the folders, read counters, role files and everything else itself, and reads each one back. Where a platform can't set its own standing instruction, the bot gives you one short block to paste into its settings.

## Two layers
- SHARED (this repo): `START_HERE.template.txt` and `roles/` are generic. Every bot reads the latest version each turn, so improvements reach every system by themselves.
- LOCAL (the user's own storage): a short LOCAL START HERE made from `bootstrap/LOCAL_START_HERE.template.txt`. It holds that user's values, owners, projects, counters and company rules. Bootstrap creates it; the seed never overwrites it.

## BOOTSTRAP MODE (use it when no system exists yet)
You are in BOOTSTRAP MODE if the Designer cannot name an existing START HERE file or working root. Ask once:
"Is there an existing START HERE file or bot working folder I should use?" If yes, open that START HERE: if it exists, follow it instead and stop here.
If the named START HERE file does not exist yet, do not ask again: you are in BOOTSTRAP MODE, and you build it at that location in Step 3.
In BOOTSTRAP MODE:
- Before your first message of every turn (acks and quick replies too), add 1 to a scratch counter in your own workspace (missing: start at 0 and create it), write it back, read it back,
  then open with: `Reading instructions from the START HERE seed README (don't use sub agents use scripts when you can) [read #N]` (never invent or reuse N).
- Follow the rules in `START_HERE.template.txt` now, except where they name files that don't exist yet.

## Step 1 - Read (nothing else is required)
0. `PLATFORMS.txt` - what your platform must be able to do, and where each piece goes on it.
1. `START_HERE.template.txt` - the page every bot reads every turn (current cap 60 lines, H13).
2. `bootstrap/FIRST_BOT_QUESTIONS.txt` - what to ask the Designer, in order; the answers fill `bootstrap/USER_CONFIG.template.txt` (made-up sample: `bootstrap/USER_CONFIG.example.txt`).
3. `bootstrap/MANIFEST.txt` - what to build, in order.
4. `bootstrap/LOCAL_START_HERE.template.txt` - the user's own page (values, projects, company rules).
4b. `bootstrap/SUPPORT_STATUS.template.txt` - the local-only record of the one "Is it helping?" ask (never sent anywhere).
5. `bootstrap/BOT_DESCRIPTION.template.txt` - the every-turn block each bot's standing instructions carry.
6. `roles/*.template.txt` - CONTROLLER, WATCHDOG, LEADERS, LIBRARIAN, FEEDBACK. Read the full text only for a role you will hold.

## Step 2 - Ask the Designer
Ask the questions ONE at a time. Keep each answer with the Designer's exact words and time in a scratch note; it moves into DECISIONS.txt at Step 3.
Skip a question only when an earlier answer settles it. Every `{{PLACEHOLDER}}` must come from an answer; never guess one. The exceptions are the support links `{{DONATE_LINK}}`, `{{REPO_URL}}`, `{{REVIEW_URL}}`, `{{SHARE_X_URL}}` and `{{SHARE_LINKEDIN_URL}}`: the seed owner sets each in this repo at publish time (none until then), never the Designer's answers. Before publishing, the seed owner sets {{DONATE_LINK}} or deletes the Support sentence on START_HERE's END line; the raw placeholder is never published.

## Step 3 - Build
Do MANIFEST steps 0-11 in order (0 writes USER_CONFIG.txt): LOCAL START HERE, folders, roles, read counters (create YOUR counter first, holding your latest bootstrap N),
then `python3 scripts/bootstrap.py` into a staging folder, uploaded to the working root in the shared store (folders, DECISIONS, OWNERS, _BOT_IDS, MOVE_LOCK, CORRECTIONS_LOG, CHANGE_LOG, logs, scripts);
after bootstrap.py, in MANIFEST step 7 register yourself like any other bot (your own row, with name, role and counter, in USER_CONFIG BOT and _BOT_IDS; the Designer or your leader may overrule).
Each step: check the parent path exists, create, read back, log one line. Never overwrite an existing file; flag it.

## Step 4 - Leave BOOTSTRAP MODE
Once your counter and the LOCAL START HERE exist, switch to the normal H1 read (N keeps counting from your bootstrap N): read the shared page and the LOCAL START HERE every turn, add 1 to your counter,
and open with `Reading instructions from <LOCAL START HERE location> (don't use sub agents use scripts when you can) [read #N]`.
A missing counter file means: start at 0 and create it, except the bootstrap bot's own counter, which starts from its latest bootstrap N.

## Step 5 - Verify and hand off
List every created path with its size, confirm the LOCAL START HERE is 60 lines or fewer, and report to the Designer in two lines:
what exists (verified by reading it back) and what is missing. Then hand off to the Controller bot.

## How to give this to a new person's bots
1. The Designer gives the new person read access to this repository (they never get write access).
2. The new person tells their first bot to read this README and answers its questions; they create nothing by hand. The bot runs BOOTSTRAP MODE and builds their LOCAL layer, folders, counters and files in their own storage.
3. Their bots read the shared pages here every turn, so later improvements reach them by themselves. Their local page stays theirs.
4. Their improvements come back as suggestions only (see CONTRIBUTING.md).

## Contents
- `PLATFORMS.txt` - minimum platform capabilities and setup notes per platform
- `START_HERE.template.txt` - every bot's per-turn page
- `roles/` - CONTROLLER, WATCHDOG, LEADERS, LIBRARIAN, FEEDBACK role templates
- `bootstrap/` - MANIFEST, FIRST_BOT_QUESTIONS, USER_CONFIG (template and made-up example), NAMING (bot names and badge pictures), FIRST_SETUP_TRAINING (worked examples, read only at bootstrap or by a new bot), LOCAL_START_HERE, BOT_DESCRIPTION and SUPPORT_STATUS templates
- `libraries/` - shared library entries, one file per entry (`libraries/robot/kuka/kuka-manuals.md`, link-out only; `libraries/software/ci/failure-library.md`, the failure library rule and row format); each is a byte-exact copy of a LIVE entry listed in the store's `Libraries\LIBRARY_CHANGES.txt`
- `scripts/bootstrap.py` - folder tree and control files, including `Libraries\LIBRARY_CHANGES.txt` and `Libraries\_suggested\` (never overwrites)
- `scripts/log_event.py`, `scripts/toggle.py` - event log and ON/OFF switch the rules call (Python 3, standard library; run on a downloaded copy, then write back)
- `proposals/` - ideas PENDING APPROVAL, off by default (private correction intake)
- `CHANGELOG.md` - fix notes for each seed version (X.Y.Z) (what changed and which correction it closed)
- `scripts/check_corrections.py` - lists Designer corrections no bot saved as a file (Controller CT-10)
- `scripts/make_avatar.py` - draws a bot's badge avatar from the company's logo and colors (kept in the local layer)
- `scripts/feedback_scorecard.py` - the FEEDBACK role's scorecard: one row per live START HERE version (corrections, repeats, saved-check misses)
- `scripts/scrub_check.sh <denylist>` - FAILS on emails, domains, user paths, GUIDs, secrets, commit identities, any denylist term, or platform-specific terms outside PLATFORMS.txt (the README owner links block, checked against an allow list, is the one exception)
- `CONTRIBUTING.md` - how other users send improvements back; `LICENSE` - to be decided by the Designer

## Repo rules
Fully generic and platform-neutral: platform names and features appear only in PLATFORMS.txt. No person names, companies, emails, domains, user paths, IDs, customer terms or secrets. Use "the Designer" / "the user". One exception: the marked owner links block at the end of this README may name the maintaining owner and link to its public pages. `scripts/scrub_check.sh` allows there only the exact terms and links listed (a link passes only where it ends exactly as listed) in an owner allow list kept outside the repo (like the denylist; passed as its third argument), in root README.md between the OWNER-LINKS markers, at most 8 lines; anything else in the block, and the same terms in any other file, still fail. If you reuse this seed, replace or delete that block and supply your own allow list.
Run `scripts/scrub_check.sh <denylist> . <owner-allowlist>` (both lists are kept outside the repo; MANIFEST step 10) before every commit; leave out the allow list if this README has no owner links block.
Commit only reviewed, scrubbed revisions, under a generic identity (see CONTRIBUTING.md).
The first commit is the scrubbed tree only, with no draft history.
Public on the Designer's decision; no license is granted, all rights reserved (see LICENSE).

<!-- OWNER-LINKS BEGIN (the only place owner names and domains are allowed; scrub_check enforces this) -->
## Links
Maintained by Ai Machines.
- Website: [Ai Machines](https://aimachinesllc.com)
- YouTube: [Ai Machines channel](https://www.youtube.com/@AiMachinesLLC)
- How-to videos: approved video links are added here once they are uploaded.
<!-- OWNER-LINKS END -->
