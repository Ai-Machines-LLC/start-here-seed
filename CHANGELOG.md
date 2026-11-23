# Changelog
Fix notes for each seed version (X.Y.Z): what changed and why. Corrections closed by a revision are listed by their
intake status (FIXED <version>), without any sender's details. Newest first.

## 0.10.5 (review build, from main 30b3f57; 0.10.4 is not used because a 0.10.4 package name already exists, H35)
- CONTRIBUTING v0.8.1: step 2 drops the "while the repo is private" private-intake detour (the repo is public now); pull requests into `suggested` are the one path, and proposals are still never posted as public issues.
- SCRIPTS.txt: check_scripts.py, run_team_checks.py, score_rebuild.py, read_check.py, path_patterns.py and library_intake_scan.py are present in scripts/ and now listed as shipped, not planned (check_scripts.py reported FLIP=6).

## 0.10.3 (review build PRE-T6 0.1.0, from main 78ae0f1; fixes found by the T6 mechanical pre-check and review #216, on the START HERE lead's go)
- bootstrap.py 0.5.2: the CHANGE_LOG.csv header column is "version" (the H35 word), not "revision", so a rebuilt system can pass the scorecard's S6 header check.
- LICENSE: an all-rights-reserved notice for the public repo (the Designer's decision: no license); README no longer says the repo stays private.
- Planned scripts (bot_metrics, route_check, confirm_change, leak_check, heartbeat, check_heartbeats) are marked "planned, not shipped yet: do this step by hand" wherever role, template or manifest text names them; run_team_checks says they SKIP until shipped.
- MOVE_LOCK is a folder with one file per bot, written with move_lock.py: MANIFEST, the START HERE template's H12 and its folder list now say so (the old text named one shared MOVE_LOCK.txt).
- score_rebuild.py 0.2.2: S18 scores 2 when every named planned script is marked planned or by hand; S14 accepts bootstrap.py's own ROOT_MISSING error as the missing-root refusal (the old pattern never matched it).

## 0.10.0 (placed from review build 0.10.2: CHANGES a6870144, DIFF 64d516cc, non-author review PASS; from main after 0.9.3; 0.10.1 FAIL 1, not reused, H35; seed library update per the START HERE team's LIBRARY_UPDATE_PLAN 0.1.6, which passed non-author review)
- First library entry: `libraries/robot/kuka/kuka-manuals.md` 0.3.0 (sha256 first 8 = 162de766), a byte-exact copy of the LIVE entry, as listed in the store's LIBRARY_CHANGES 1.1.0 (sha256 first 8 = befabf4d). Link-out only: no vendor manual is copied. Why: the library ships where-to-get-it pages, never vendor documents.
- Libraries folder: bootstrap.py and MANIFEST create `Bots\Libraries\LIBRARY_CHANGES.txt` (header: only LIVE entries; library | version | sha256 | Reviewer PASS | category | placed time | what changed) and `Bots\Libraries\_suggested\`. The folder is now "Libraries" (was "02 Libraries") until the Designer decides the layout. Why: leaders update projects only from LIVE entries, and need one list to work from.
- START HERE template line 57 adds LIBRARY UPDATES (update only to LIVE entries; shared definitions, then programs and pages, then docs; archive, new version, non-author review, leader placement, cite the entry's version + sha; nothing downloaded, run or deployed without the Designer's go). Folded into the existing line, so the page stays at 58 lines (H13).
- LIBRARIAN v0.6.1 (from v0.5.0; 0.6.0 is given only when this passes and is placed, H35): LB-10, the librarian owns LIBRARY_CHANGES (the Controller when there is none). FIRST_BOT_QUESTIONS Q9 says the same.
- scrub_check.sh v0.7.2: URLs and domains are allowed only inside the repo-root `libraries/` folder (public vendor manual links); everything else, including any nested folder named libraries, still fails on any URL. README lists `libraries/`.

## 0.9.3 (review build, from 0.8.0; folds in 0.9.2 unchanged plus the items below; 0.9.2 was sent for review and is not reused, H35)
- H17 RESEARCH removed (the Designer: the Controller no longer runs the monthly research re-check; a best-practices research loop run by the START HERE team replaces it, and that loop is a team workflow, not a seed rule). The CONTROLLER CT-4 monthly research check goes with it. H17 is left unused instead of renumbering, because H18 onward are cited by number in role sections, profiles and logs.
- H19 GOAL line (the Designer approved research proposal 5): every review report adds one PASS/FAIL line on whether the change meets the requirement it was made for, quoting it; the CHECK names it. Why: a change can be correct line by line and still miss what it was for.
- Machine-only wording left after 0.9.2: LEADERS L-4 "Test-Path" is now "read-back hash"; PLATFORMS drops the "Task Scheduler" example.

## 0.9.2 (review build, from 0.8.0; folds in 0.9.1, request #14 FAIL 1)
- NO MACHINE DEPENDENCY (the Designer: "no PC dependency should remain"): WORKING_ROOT is a folder in the shared store, never one machine's disk (H24, Q4, USER_CONFIG). bootstrap.ps1, log_event.ps1 and toggle.ps1 are replaced by bootstrap.py, log_event.py and toggle.py (Python 3, standard library): a bot runs them on its own computer against a downloaded copy and writes the file back; bootstrap.py builds into a staging folder that is uploaded without overwriting (MANIFEST step 5). bootstrap.py also creates 05 Logs\WATCHDOG_MISSES.csv, which MANIFEST step 5 listed but bootstrap.ps1 never made. The SEED_ROLES_FOLDER environment variable is gone; toggle.py takes --file. H30, LEADERS L-9/L-16/L-17/L-18, WATCHDOG W-1f, README and PLATFORMS P2c follow. Why: any bot on any computer can run every step, and a rebuild test scores every step instead of marking machine steps N/A.
- H41/CT-12 one source (review #14): the Designer's promotion words are read from {{ROLES_FOLDER}}\LEADER_PROMOTIONS.txt, which the Controller writes verbatim the turn the forward arrives; H41's CHECK and CT-12 both cite it.

## 0.9.1 (review build, from 0.8.0)
- H40 EVERY RULE HAS A CHECK (the Designer: "every rule in START HERE needs an enforcement mechanism ... so silence is visible and every duty can be checked"): every shared rule now ends with a CHECK (a receipt, counter, timestamp or file write-back); a new rule with no CHECK fails review; the LOCAL page template says the same for local rules. WATCHDOG W-1h runs the CHECKs each pass and writes Bots\05 Logs\WATCHDOG_MISSES.csv (one row per pass even with no misses, so a skipped pass shows); MANIFEST step 5 creates it.
- H41 LEADER PROMOTIONS: a bot the Designer promotes forwards their words to its leader and the Controller and waits; the Controller writes ACK or VETO in {{ROLES_FOLDER}}\LEADER_PROMOTIONS.txt (new, MANIFEST step 3) and on ACK adds it to USER_CONFIG LEADER_LIST and OWNERS (new CONTROLLER CT-12). The ROLES line now names {{LEADER_LIST}}; LEADERS L-0 notes the ACK gate. WATCHDOG W-1i flags a LEADER_LIST vs OWNERS mismatch (why: L-0 is filled from LEADER_LIST, so OWNERS is the copy that can drift) and any promotion with no ACK/VETO after one pass.
- BADGE WRITE-BACK (the Designer: badge generation is part of START HERE so no future seed forgets it): after making or checking its badge each bot writes <bot>.txt (name, avatar sha256, time, maker version) in "05 Badges" beside the LOCAL page; MANIFEST step 2 creates the folder and step 7 has each new bot write its file; WATCHDOG W-1j flags bots without one. Why beside the LOCAL page: Bots\05 is already Logs under the working root.
- Role changes travel through the pages like rule changes (the Designer: "all rule changes and role changes flow through the START HERE document, not through direct messages to bots outside your project").
- Line budget (cap 60): H15+H16 and H21+H22 each share a line, and READ CHAIN steps 1-4 are one line; the page is 59 lines. "never loosen H1-H35" is now H1-H41 on both pages.
- Not carried from the maintaining team's own page in this build: its relay, chain-of-command, repo-team and decision-weight rules (open item for a later MINOR).

## 0.8.0 (passed review as build 0.8.4; 0.8.1 FAIL 3, 0.8.2 FAIL 2, 0.8.3 superseded before review)
- CONTRIBUTING (passed as the v0.7.1 draft): one path for everyone outside the maintaining team, the seed owner's own bots included: a pull request into branch `suggested` (private intake while the repo is private); only the maintaining team's designated member merges into `main`.
- USER_CONFIG template RULES and LOCAL VALUES no longer contain double braces (they name placeholders in words), so the step-0 "no {{ left" check and a filled LOCAL page can pass.
- New USER_CONFIG key SCRIPTS_FOLDER (section C, default "04 Scripts" beside the LOCAL page), per the reviewer's ruling on the first filled config.
- USER_CONFIG (the Designer, 3:04 PM): one per-user config file holds the bot roster, names, badge look, START HERE and file locations and storage. New bootstrap/USER_CONFIG.template.txt (blank schema) and USER_CONFIG.example.txt (made-up data). FIRST_BOT_QUESTIONS answers fill it; MANIFEST step 0 writes it; the LOCAL page's values block now points to it; START_HERE.template and README mention it.
- Support links ({{DONATE_LINK}}, {{REPO_URL}}, {{REVIEW_URL}}, {{SHARE_X_URL}}, {{SHARE_LINKEDIN_URL}}) stay set by the seed owner, not USER_CONFIG: DONATE_LINK key removed; template RULES and LOCAL VALUES name the exception.
- MANIFEST step 10 uses {{DENYLIST_PATH}} instead of a fixed path.
- Step 0 and template FORMAT: format lines (COMPANY, COMPANY_MARKS, BOT, PROJECT) are replaced by filled lines, then the format lines and [bracket] notes are deleted.
- BOT_DESCRIPTION fields come from the USER_CONFIG BOT and PROJECT rows (template F and the BOT_DESCRIPTION Fill line).

## 0.7.0 (passed review as build 0.7.5; 0.7.4 FAIL 1)
- SUPPORT_STATUS NO path: the saved FEEDBACK file line is now "HELPING: <answer>" (was "Q7: <answer>", which clashed with FIRST_BOT_QUESTIONS Q7 and was read by no role).
- FEEDBACK F4A: the feedback owner also reads *_FEEDBACK.txt HELPING lines in {{CORRECTIONS_DIR}} as improvement input; the scorecard ignores them.

## 0.7.4 (FAIL 1 in review; superseded by 0.7.5)
- "Is it helping?" ask (the Designer, 2:17 PM): folded into the same one-time CT-11 ask, no second ask. YES offers star, review, share (pre-filled links the Designer clicks) and donate ($10 suggested) in one message; NO asks "What would make it better?" and saves a local FEEDBACK file (Q7 line); an issue is opened only on the Designer's yes. SUPPORT_STATUS adds helping and not-helping. Never asked again after any answer; one re-ask at most after 90 days of silence. Bots never post, star, share or donate.
- New support-link placeholders {{REPO_URL}}, {{REVIEW_URL}}, {{SHARE_X_URL}}, {{SHARE_LINKEDIN_URL}}: set by the seed owner at publish time like {{DONATE_LINK}}; a link that is none is left out of the ask.
- Publish rule: before publishing, the seed owner sets {{DONATE_LINK}} or deletes the Support sentence on START_HERE's END line; the raw placeholder is never published (README Step 2).
- New roles/WATCHDOG.template.txt (generic): what the watchdog checks, how often, how it reports, and its limits. The Controller holds it; CONTROLLER CT-4 now points to it. Listed in START_HERE ROLES, README and MANIFEST step 3.
- LOCAL MESSAGE_ROUTE is now the {{MESSAGE_ROUTE}} placeholder (Q0), not hard-coded "direct".
- PLATFORMS: one platform's per-bot setup note updated to its current help page (per-bot instructions moved to its newer feature; details stay in PLATFORMS.txt only).

## 0.7.3 (superseded before review by 0.7.4)
- scripts/feedback_scorecard.py added, byte-identical to the feedback owner's passed build: one scorecard row per live START HERE version from the corrections folder, the tracker and the Controller's saved-check counts (FEEDBACK F4C).
- Support ask, local only (the Designer, 2:15 PM): new bootstrap/SUPPORT_STATUS.template.txt (not-asked / asked <date> / donated / no-thanks). The Controller (CT-11) asks once, in a normal reply, after SUPPORT_ASK_READS combined counter reads (default 200) AND SUPPORT_ASK_DAYS days (default 14); never again after donated or no-thanks; at most one re-ask 90 days after an unanswered ask. Nothing is sent anywhere. Replaces the setup-time mention; the shared page keeps only its one passive closing line.
- Platform-neutral seed (the Designer: it should work on anybody's AI platform). New PLATFORMS.txt: the minimum a platform needs, the fallbacks, and short setup notes per platform, each claim tied to the vendor's own help page.
- No platform names, tool names or platform features outside PLATFORMS.txt: "scheduled job", "integration", "standing instructions", "badge picture" replace platform words.
- Q0 asks which platform runs the bots and whether they can message each other; LOCAL gets PLATFORM and MESSAGE_ROUTE (direct or inbox). With no bot-to-bot messages, bots use an "04 Inbox" folder (MANIFEST step 2, PLATFORMS.txt P3) and read it each turn (BOT_DESCRIPTION {{INBOX_LINE}}).
- scrub_check.sh step 5 FAILS on platform-specific terms anywhere but PLATFORMS.txt.
- roles/FEEDBACK.template.txt resynced to the feedback owner's rev 0.14.2 (HHMM names for both file types, "FIXED <version>").
- Support line: one closing line on the shared page ("Like this? Support it: {{DONATE_LINK}}", no rule) (the setup-time mention became the local support ask below). The seed owner sets the link at publish time.
- LOCAL page fix: "never loosen the shared H1-H35" (was H1-H31).

## 0.6.0 (passed as review build 0.6.2; 0.6.1 was superseded before review)
- CONTROLLER CT-10 is now the SAVED-CHECK: missing correction files are saved by the bot or the Controller, each miss is logged with bot and time (no customer content) and feeds the scorecard.
- roles/FEEDBACK.template.txt resynced to the feedback owner's passed rev 0.13.1.
- H35 VERSIONS (new core rule): MAJOR.MINOR.PATCH; review builds are X.Y.1+, each FAIL bumps PATCH, numbers are never reused; X.Y.0 = passed and in use; MINOR = new feature or fix set; MAJOR = cross-platform update, every program in the project moves to it; cite version + hash. Old "rev 0.N" labels map to 0.N.0; the LOCAL page starts at 1.0.0.
- Correction files: <YYYY-MM-DD_HHMM>_<bot>_CORRECTION.txt, feedback answers <YYYY-MM-DD_HHMM>_<bot>_FEEDBACK.txt, _2/_3 when taken, never overwritten; check_corrections.py counts only CORRECTION files.
- The feedback role proposes LOCAL-page fixes to the Controller (the Controller owns that page).
- {{CORRECTIONS_DIR}} is a LOCAL value (default "03 StartHere_Corrections"); change requests for either page go in as correction files.
- {{FEEDBACK_SCORECARD_PATH}} added to the LOCAL values, Q14 and MANIFEST step 9.

## 0.5.0 (draft)
- Literal revision stamps on line 1 of the shared page and every role file (files read live are never filled in).
- WATCHDOG role renamed CONTROLLER everywhere (file, placeholders, labels CT-n).
- Roles nobody holds are set to "none" in the LOCAL page and skipped.
- The Controller owns the LOCAL START HERE; the shared page and role files change only by upstream suggestion.
- Every correction from the Designer is saved the same turn as one new file in {{CORRECTIONS_DIR}} (default "03 StartHere_Corrections") (rule-relevant words only, project details stripped), never sent as a message; the feedback role (none: the Controller) marks each OPEN, FIXED rev <N> or WONTFIX <why>. The Controller audits that every correction was saved (CT-10, scripts/check_corrections.py).
- Bot naming rule (bootstrap/NAMING.txt) and a generic avatar generator (scripts/make_avatar.py), used at bot creation.
- Line cap is a current value (60 per page) the page owner may raise only on measured data, with the why logged here (CT-1a matches).
- New bots may be created by a leader (L-12/L-13) as well as the Designer; the creator runs the MANIFEST step 7 checklist.
- Rule changes spread only through the START HERE pages; no team gives orders to bots outside its project. Every bot checks its own name and badge.
- make_avatar.py: --logo is optional (plain disc when a company has no logo yet).
- Proposal, pending approval and off by default: private, write-only correction intake (proposals/CORRECTIONS_INTAKE.txt).

## 0.4.0 (draft)
- Two layers: shared START HERE read from the repo every turn, plus a LOCAL START HERE per user.
