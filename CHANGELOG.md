# Changelog
Fix notes for each seed version (X.Y.Z): what changed and why. Corrections closed by a revision are listed by their
intake status (FIXED <version>), without any sender's details. Newest first.

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
