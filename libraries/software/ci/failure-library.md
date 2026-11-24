# Failure library + build-to-check (generic)
Library id: software/ci/failure-library | version 0.1.2 | rule + row format
Library status: LIVE 0.1.2 (non-author review PASS)
Link-free, project-free. A shared rule and row format any project that builds code can copy.
Why (the Designer, 2026-11-23 7:51-7:57 PM ET): "I hope that you're really building a good library and a script to check these these bugs"
and "it's important that this knowledge doesn't just stay with you right it needs to move into the GitHub through the librarian".

RULE
1. Each project that builds code keeps two files next to its pre-push checker:
   - FAILURE_LIBRARY: one row per build/test failure that reached CI.
   - the checker script: one check per row.
2. When CI fails, the bot that owns the checker, before the fix goes into the main branch:
   a) adds a row: ID | date | build run or commit | exact error text | cause in one line | check ID
   b) adds a check that FAILs on the old broken commit and PASSes on the fixed one, and records both runs (FAIL on the old commit, PASS on the fix)
   c) tells every author bot to run the new checker version and include its PASS line with each patch
3. Author bots run the checker before sending any patch, and report any CI failure the checker missed right away, without being asked.
4. When the same kind of failure happens twice, or a checker misses one, the bot reports it to the Librarian as a seed bug
   (self-report, without waiting for the Designer).
5. Monthly, or when asked, the owner sends the Librarian a project-free copy of new rows so other projects pick them up.

ROW FORMAT
| ID | Date | Run / commit | Error the build gave | Cause | Check |
|---|---|---|---|---|---|

STARTER ROWS (Swift / iOS, from real failures; no project data)
| ID | Date | Run / commit | Error the build gave | Cause | Check |
|---|---|---|---|---|---|
| SW1 | 2026-11-22 | - | XCTAssertEqual "nil" is not equal to "Optional(<Type>(...))" | `x ?? .none` on a type that has its own `none`; Swift picks Optional.none (nil) | FAIL on `?? .none`; write `?? MyType.none` |
| SW2 | 2026-11-23 | - | 'c' is not a valid digit in integer literal | #"..."# raw string with JSON colors like "#c0ffee" inside; the "# ends the string early | FAIL when a line has #" and "# followed by a letter/digit; use ##"..."## |
| SW3 | 2026-11-22 | - | cannot convert value of type 'String' to expected argument type 'UInt32' | colors written as "#AABBCC" strings where the color helper takes UInt32 | FAIL on 6-hex-digit string constants when the helper takes UInt32; write `let c: UInt32 = 0xAABBCC` |
| SW4 | 2026-11-22 | - | cannot find '<helper>' in scope | called a helper that is `private` in another file | FAIL when the only top-level declaration of a called function is private/fileprivate in a different file |
| SW5 | 2026-11-23 | - | cannot find type '<Name>API' in scope | a patch stack missing the commit that declares a protocol | FAIL on *API/*Client/*Store/*Service types no file declares at the head commit |
| SW6 | 2026-11-23 | - | 'await' is not allowed in an autoclosure; call to actor-isolated instance method '<method>(<label>:)' in a synchronous main actor-isolated context | an async (actor) call was written inside XCTAssert*(...), e.g. XCTAssertNil(await <mock>.<method>(...)); XCTAssert arguments are autoclosures and cannot contain await | C6 FAIL on await inside an XCTAssert* call; fix: let v = await <mock>.<method>(...) then XCTAssertNil(v) |
| SW7 | 2026-11-23 | - | cannot find type '<Name>' in scope | a test uses a type declared under Sources/<Module>/ but the test file never imports <Module> (it imports other modules of the same package only) | C7 FAIL when a changed test file uses a type whose declaring Sources module is not in its import / @testable import lines (string literals ignored, names of 3+ characters); fix: add import <Module> |
| N1 | 2026-11-21 | - | test hangs or fails on a fake host | unit test calls the real network client | FAIL on tests that use the shared URL session or live client without a stub |

CHECK (how to tell the rule is followed)
- Every CI failure in the project's build history after this date has a row, a check ID and both test results.
- The checker's header lists each check ID with the failure it came from.
- Each patch message from an author bot carries the checker's PASS line and version.
