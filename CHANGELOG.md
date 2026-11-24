# Changelog
Fix notes for each seed version (X.Y.Z): what changed and why. Corrections closed by a revision are listed by their
intake status (FIXED <version>), without any sender's details. Newest first.

## 0.10.29 (review build, on top of 0.10.28 70fdd2a9; a repeated correction from the Designer on running the release gate before review and before placing)
- START_HERE.template.txt H19 REVIEW GATE: new RELEASE GATE CHECK. Where the How-Tos index (or a how-to it lists) names a pre-review gate script for a build type, the author runs it and puts its 'CHECKS OK <sha>' line in the master doc row before review; the reviewer runs it too and pastes that line into its verdict (a verdict without it is a FAIL; a reviewer that cannot run the gate says so, confirms the author's line names the reviewed sha, and the placer's rerun becomes required); the placer relabels to X.Y.0 by byte replace only and reruns the gate on the relabeled file before placing. CHECK: each build verdict carries the line or the note, and the placer logs its rerun.
- START_HERE.template.txt L1: the page's own version is now 0.9.5. The page is still 59 lines (cap 60).

## 0.10.28 (review build, on top of 0.10.26 d6ea0daf; the Designer's corrections on reporting corrections, housekeeping and plain-digit versions; 0.10.27 failed review with 2 findings and is not reused, H35)
- START_HERE.template.txt H1: the opener adds "and report error to librarian"; a TRANSITION note keeps an old-text opener from counting as a miss on a turn that read the page before this version. New REPORT CORRECTIONS clause: the "error" is being corrected by the Designer, not a mistake a bot catches itself; the corrected bot saves its one CORRECTION file (L23, still file-only, no message) and then tells the Designer in one short line that it reported it to the librarian.
- START_HERE.template.txt H43 HOUSEKEEPING (new; H42 is not used in the seed): unused or stale items found in any work are listed and cleaned up in the same job; anything still referenced is kept; archive first (H7, H12); a removal with no archive needs the Designer's yes on the exact item (H7); the reviewer checks the cleanup list.
- START_HERE.template.txt H35 CHECK: a version label that is not plain MAJOR.MINOR.PATCH digits (such as 'rev c' or '1.2.3b') is a FAIL, checked by script against ^\d+\.\d+\.\d+$. The Designer: "ther is no rev c" / "thats not how we version controle".
- START_HERE.template.txt L4: the local page may not loosen H1-H43. L1: the page's own version is now 0.9.4 (was '0.9.3 review build'). The page is 59 lines (cap 60).

## 0.10.26 (review build, on top of 0.10.23 67a1a68; lessons from a fresh-install test run, part 1, and the project-wide MAJOR; 0.10.24 and 0.10.25 failed review and are not reused)
- The Designer (2026-11-24): "OK after you've updated Start here with all your learning". A test bootstrap on a fresh install greeted before the H1 line, bumped a scratch counter without reading the page, wrote defaults into USER_CONFIG before asking, edited shared files with no lock until late, named no how-to, and had no way to ask for a review when it could message only its lead.
- README.md BOOTSTRAP MODE: 'this page' means README.md until START HERE exists; read it every turn before the counter and the first message; no greeting before the H1 line; MOVE_LOCK and archive-first from read #1; save each correction the same turn; name the how-to or say there is none; SUGGESTION files go in Bots\Libraries\_suggested\ (a scratch suggestions folder until MANIFEST step 5 creates it); corrections go in a scratch corrections folder until MANIFEST step 2 makes {{CORRECTIONS_DIR}}, then move in with none lost; a test bot that may message only its lead asks the lead to route its H19 review, naming file and sha.
- START_HERE.template.txt H1: the same BOOTSTRAP MODE meaning of 'this page', and a first-run greeting waits for the H1 line.
- bootstrap/FIRST_BOT_QUESTIONS.txt 0.9.1: ask about any default before writing it into USER_CONFIG.
- bootstrap/FIRST_SETUP_TRAINING.txt 0.4.3 (0.4.1 and 0.4.2 not reused): new example 12 FIRST TURNS ON A FRESH INSTALL, with the scratch corrections folder and ASK, DON'T GUESS on its RULE line; drill 0 lists examples 1-12; example 8 RIGHT numbers a build with the project's X.
- START_HERE.template.txt H35 VERSIONS: MAJOR (X) is project wide. Every program and file in one project carries the same X at all times, and a cross-platform update moves all of them to the next X together. The CHECK now fails any build whose X does not match. The Designer (2026-11-24): "The x. Should be project wide". In one install, a project's programs had drifted to two different majors because the old wording only covered cross-platform updates.
- Known tool gaps, not fixed in this version: scrub_check can PASS a file with CRLF line endings that it did not fully check; bootstrap.py has text-encoding problems and does not run git init; the scripts folder location is unclear; USER_CONFIG is written with LF line endings; a rerun --diff option is needed; the event log needs an unknown-name check; a badge file is missing for bots that were not created; the bot-name question (Q8) and one cycle name need clearer wording.

## 0.10.23 (review build, on top of 0.10.20 5928aa5; 0.10.21 was superseded and 0.10.22 failed review with 1 finding, neither is reused, H35; the Designer's corrections that the first seed bot builds the Controller and the librarian)
- The Designer (2026-11-24): "the seed bot should become the controller or they build a controller", and whoever stands in for the user in a test represents only the user; then "it should not think that the controller already exists because it needs to build a control controller and the librarian". A test bootstrap had left Controller duties (badge clashes, bot ids, reviewers, role words) blank "for the Controller" while a tester stood in for it.
- bootstrap/FIRST_BOT_QUESTIONS.txt 0.9.0: Q9 says no Controller or librarian exists yet; the bootstrap bot is the Controller by default (or builds the named one), always builds the librarian (never none), and holds both roles' duties until each exists; new TEST RUNS line.
- bootstrap/MANIFEST.txt 0.10.1: new CONTROLLER AND LIBRARIAN FROM THE START lines before step 0; step 0 no longer allows a librarian of none; LIBRARY_CHANGES is held by the bootstrap bot, then the Controller, until the librarian exists; step 11 hands each built role bot the list and its open items.
- roles/CONTROLLER.template.txt 0.10.1: new CT-0 FIRST HOLDER. roles/LIBRARIAN.template.txt 0.7.0: LB-10 holder until the librarian exists.
- bootstrap/USER_CONFIG.template.txt and USER_CONFIG.example.txt 0.9.0: LIBRARIAN_BOT is never none; the example has a GEN-Librarian.
- scripts/bootstrap.py 0.5.4: the LIBRARY_CHANGES header names who holds it until the librarian exists.
- bootstrap/FIRST_SETUP_TRAINING.txt 0.3.1: new example 11 BUILD THE CONTROLLER AND THE LIBRARIAN; drill 0 lists examples 1-11.
- README.md Step 5: never assume a Controller or a librarian exists; hand each built bot its open items.
- bootstrap/NAMING.txt 0.5.1 (N8) and scripts/make_avatar.py 0.6.1 (header comment only): a gray-disc avatar flag is recorded by the Controller, which during setup is the bootstrap bot itself (CT-0), not left for a Controller that may not exist yet. MANIFEST 0.10.1 and CONTROLLER 0.10.1 add gray-disc flags to the setup duty lists.

## 0.10.20 (review build, on top of 0.10.19 da68451; two updated LIVE library entries after their non-author review PASS)
- Library entry update: `libraries/software/ci/check_patch.py` 2.3.1 (sha256 first 8 = 76d589db), a byte-exact copy of the LIVE entry, as listed in the store's LIBRARY_CHANGES 1.6.0 (sha256 first 8 = 8842ccb9). It replaces 2.2.1 (c15756f0). It fixes C8 so only a type's own member lines are checked (code is stripped of strings and comments first, and braces are counted), and it adds C9: assigning `d[k] = ...` on a `[K: V?]` dictionary, where `updateValue` is needed. Each has self-test cases. Not yet verified: that C9 FAILs the real failing commit it came from (the author's claim only). Known gaps for a later version: C9 misses `self.d[k] = nil` and `Dictionary<K, V?>`, and it also flags a safe non-nil assign.
- Library entry update: `libraries/software/ci/failure-library.md` 0.1.5 (sha256 first 8 = 1b05dd64), a byte-exact copy of the LIVE entry, as listed in the same LIBRARY_CHANGES 1.6.0. It replaces 0.1.2 (e180be17) and adds rows SW8 and SW9 (checks C8 and C9) and T1, INFRA1 and RUN-BASE. Rule 2d covers failures no text check can catch: their rows say 'no checker ID' and give the required action. Rule 3 says to run the checker with main as the base.
- scripts/SCRIPTS.txt: the check_patch.py line names version 2.3.1.

## 0.10.19 (review build, on top of 0.10.18 19374d0; two updated LIVE library entries after their non-author review PASS)
- Library entry update: `libraries/software/ci/check_patch.py` 2.2.1 (sha256 first 8 = c15756f0), a byte-exact copy of the LIVE entry, as listed in the store's LIBRARY_CHANGES 1.4.0 (sha256 first 8 = 3239c3c6). It replaces 2.1.0 (d38acbc4) and adds two Swift checks with self-test cases: C6 (await inside an XCTAssert* call, which that autoclosure does not allow) and C7 (a test uses a type declared in a Sources module that the test file does not import). Nothing else changed, and `check_patch.example.json` 2.1.0 stays as it is. Why: two new compile failures reached CI.
- Library entry update: `libraries/software/ci/failure-library.md` 0.1.2 (sha256 first 8 = e180be17), a byte-exact copy of the LIVE entry, as listed in the store's LIBRARY_CHANGES 1.5.0 (sha256 first 8 = 68740284). It replaces 0.1.0 (65834499) and adds the generic rows SW6 and SW7 that go with checks C6 and C7.
- scripts/SCRIPTS.txt: the check_patch.py line names version 2.2.1.

## 0.10.18 (review build, on top of 0.10.15 5cc653d; 0.10.16 2b2a554 and 0.10.17 217135e failed review with 1 finding each and are not reused, H35; two new LIVE library entries after their non-author review PASS)
- New library entry: `libraries/software/ci/check_patch.py` 2.1.0 (sha256 first 8 = d38acbc4), a byte-exact copy of the LIVE entry, as listed in the store's LIBRARY_CHANGES 1.3.0 (sha256 first 8 = e7cc53ef). It is a generic pre-push check: each failure library row gets a check that FAILs on the broken commit and PASSes on the fix, plus a self-test case (`--self-test`). Every project detail comes from a JSON config. Why: failures should be caught before CI, not after.
- New library entry: `libraries/software/ci/check_patch.example.json` 2.1.0 (sha256 first 8 = d884def2), the example config with placeholders only, listed in the same LIBRARY_CHANGES 1.3.0.
- README: the `libraries/` line names the new entries.
- scripts/SCRIPTS.txt: lists the check_patch.py library entry so check_scripts stays clean.

## 0.10.15 (review build, on top of 0.10.14 9100a9a; a new LIVE library entry after its non-author review PASS)
- New library entry: `libraries/software/ci/failure-library.md` 0.1.0 (sha256 first 8 = 65834499), a byte-exact copy of the LIVE entry, as listed in the store's LIBRARY_CHANGES 1.2.0 (sha256 first 8 = 6e97aa27). It holds a generic rule (every build failure that reaches CI gets a row and a check that FAILs on the old commit and PASSes on the fix), the row format and 6 Swift starter rows, with no project data. Why: the Designer wants failure knowledge to reach the shared seed, not stay with one bot.
- README: the `libraries/` line names both entries.

## 0.10.14 (review build, on top of 0.10.13 1baee95; the START HERE team's script after its non-author review PASS, handed over by the team's builder on the lead's go)
- scripts/sheet_coverage.py 0.1.1: flags any START HERE rule or CHECK with no answer-sheet item, an edited rule (CHANGED), a stale row or an undefined item (exit 1), so a new rule can't go untested; ERROR_CODES v0.1.4 adds its probes.
- scripts/SCRIPTS.txt: new sheet_coverage.py line.

## 0.10.13 (review build, on top of 0.10.12 bce63ec; the START HERE team's script after its non-author review PASS, handed over by the team's builder on the lead's go)
- score_rebuild.py 0.2.3: finds the rebuilt Bots and roles folders up to 2 levels below --root (a tie = ERROR 30); new GATE G1 checks every own-chat turn opens with the H1 line, N rises with no reuse, and the last N equals the counter (--replies, --counter, --h1-regex); a G1 FAIL exits 1. Why: RUN-02 scored 33/38 while its tester skipped the H1 line and counter.
- scripts/SCRIPTS.txt: the score_rebuild.py line names GATE G1.

## 0.10.12 (review build, on top of 0.10.10 6ec8e22; 0.10.11 d240e60 failed review with 1 finding and is not reused, H35; mirrored from the START HERE team's page 1.22.0 after its non-author review PASS, from the Designer's correction that bots sent a quick reply before the read)
- START_HERE template H1: ORDER. Filling out the header (read the page, count, then the H1 line) comes first every turn, before any ack, reaction or quick reply, and messages to the Designer in the bot's own chat count too. The CHECK now names the first message of every turn.
- H1 BOOTSTRAP MODE uses a real number: the bootstrap bot keeps a scratch counter before the counters folder exists, and its real counter file starts from that number instead of 0. The "[read #bootstrap]" opening is gone (README BOOTSTRAP MODE, Steps 3 and 4, including the missing-counter line; MANIFEST v0.9.5 step 4).
- bootstrap/BOT_DESCRIPTION.template.txt v0.8.1: the every-turn block says the read and the counter come before any other message.

## 0.10.10 (review build, on top of 0.10.9 e038b3d; first-setup training file, mirrored from the START HERE team's file 0.2.0 after its non-author review PASS)
- New bootstrap/FIRST_SETUP_TRAINING.txt 0.2.0: ten worked examples (situation, wrong, right, rule) and drill 0, read only when a new system is bootstrapped or a new bot is created, never every turn.
- bootstrap/LOCAL_START_HERE.template.txt: new FIRST SETUP line pointing to it, with its CHECK (a new bot's first turn names the file and its version).
- bootstrap/MANIFEST.txt v0.9.4: the bootstrap bot reads the training file once before step 0; step 7 has the creating bot hand it to each new bot in its first message.
- README: the bootstrap/ folder list names the training file.

## 0.10.9 (review build, on top of 0.10.8, pushed as main 55be8bf; the START HERE lead's layout decision: the seed follows the live system)
- bootstrap.py 0.5.3: the How-Tos INDEX.txt it creates uses the live layout, one line per how-to "folder | open it when", with a title line naming it the one how-to library (structure owner: the Controller) and the rule that Libraries hold code and config only and project notes live in the project's Master doc. The old header was "file | what it covers | owner".

## 0.10.8 (review build, on top of 0.10.7 8a084b2; RUN-01 gap 3, mirrored from the START HERE team's page after its non-author review PASS)
- START_HERE template H19: CORRECTION EDITS TOO. An edit made from a correction is reviewed by one non-author team bot before it is placed, and the placer appends one CORRECTIONS_LOG row (what went wrong, cause, change made, check added) and reads it back. This append is allowed even though the Controller owns the file; other rows are never edited or removed. The CHECK adds the CORRECTIONS_LOG row.

## 0.10.7 (review build, from 0.10.6 d8ad2a6, which failed review with 1 finding and is not reused, H35)
- README Step 3: self-registration moves after bootstrap.py (MANIFEST step 7), because bootstrap.py creates _BOT_IDS.txt and no script or step may recreate a missing target before it (H24).

## 0.10.6 (review build, on top of 0.10.5; RUN-01 gaps, the Designer's "go ahead and fix the gaps")
- README BOOTSTRAP MODE: when the named START HERE file does not exist yet, the bot decides BOOTSTRAP MODE itself and builds it there, without asking the Designer again.
- README Step 3: the setup bot registers itself like any other bot (its own row, with name, role and counter, in USER_CONFIG BOT and _BOT_IDS); the Designer or its leader may overrule.

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
