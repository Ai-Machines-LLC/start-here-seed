# Failure library + build-to-check (generic)
Library id: software/ci/failure-library | version 0.1.5 | rule + row format
Library status: LIVE 0.1.5 (non-author review PASS)
Link-free, project-free. A shared rule and row format any project that builds code can copy.
Why (the Designer, 2026-11-23 7:51-7:57 PM ET): "I hope that you're really building a good library and a script to check these these bugs"
and "it's important that this knowledge doesn't just stay with you right it needs to move into the GitHub through the librarian".

RULE
1. Each project that builds code keeps two files next to its pre-push checker:
   - FAILURE_LIBRARY: one row per build/test failure that reached CI.
   - the checker script: one check per row that a text check can catch.
2. When CI fails, the bot that owns the checker, before the fix goes into the main branch:
   a) adds a row: ID | date | build run or commit | exact error text | cause in one line | check ID
   b) adds a check that FAILs on the old broken commit and PASSes on the fixed one, and records both runs (FAIL on the old commit, PASS on the fix)
   c) tells every author bot to run the new checker version and include its PASS line with each patch
   d) a failure no text check can catch (test logic, CI infrastructure) or a process lesson still gets a row, with Check = 'no checker ID' plus the required action; it needs no check in the script
3. Author bots run the checker, with main (the merge target) as the base, before sending any patch, and report any CI failure the checker missed right away, without being asked.
4. When the same kind of failure happens twice, or a checker misses one, the bot reports it to the Librarian as a seed bug
   (self-report, without waiting for the Designer).
5. Monthly, or when asked, the owner sends the Librarian a project-free copy of new rows so other projects pick them up.

ROW FORMAT
| ID | Date | Run / commit | Error the build gave | Cause | Check |
|---|---|---|---|---|---|

STARTER ROWS (Swift / iOS plus general rows, from real failures; no project data)
| ID | Date | Run / commit | Error the build gave | Cause | Check |
|---|---|---|---|---|---|
| SW1 | 2026-11-22 | - | XCTAssertEqual "nil" is not equal to "Optional(<Type>(...))" | `x ?? .none` on a type that has its own `none`; Swift picks Optional.none (nil) | FAIL on `?? .none`; write `?? MyType.none` |
| SW2 | 2026-11-23 | - | 'c' is not a valid digit in integer literal | #"..."# raw string with JSON colors like "#c0ffee" inside; the "# ends the string early | FAIL when a line has #" and "# followed by a letter/digit; use ##"..."## |
| SW3 | 2026-11-22 | - | cannot convert value of type 'String' to expected argument type 'UInt32' | colors written as "#AABBCC" strings where the color helper takes UInt32 | FAIL on 6-hex-digit string constants when the helper takes UInt32; write `let c: UInt32 = 0xAABBCC` |
| SW4 | 2026-11-22 | - | cannot find '<helper>' in scope | called a helper that is `private` in another file | FAIL when the only top-level declaration of a called function is private/fileprivate in a different file |
| SW5 | 2026-11-23 | - | cannot find type '<Name>API' in scope | a patch stack missing the commit that declares a protocol | FAIL on *API/*Client/*Store/*Service types no file declares at the head commit |
| SW6 | 2026-11-23 | - | 'await' is not allowed in an autoclosure; call to actor-isolated instance method '<method>(<label>:)' in a synchronous main actor-isolated context | an async (actor) call was written inside XCTAssert*(...), e.g. XCTAssertNil(await <mock>.<method>(...)); XCTAssert arguments are autoclosures and cannot contain await | C6 FAIL on await inside an XCTAssert* call; fix: let v = await <mock>.<method>(...) then XCTAssertNil(v) |
| SW7 | 2026-11-23 | - | cannot find type '<Name>' in scope | a test uses a type declared under Sources/<Module>/ but the test file never imports <Module> (it imports other modules of the same package only) | C7 FAIL when a changed test file uses a type whose declaring Sources module is not in its import / @testable import lines (string literals ignored, names of 3+ characters); fix: add import <Module> |
| SW8 | 2026-11-23 | - | cannot assign to property: '<b>' is a 'let' constant | a SwiftUI binding $<v>.<b>.<c> goes through a property <b> that <v>'s type declares `let`, so the binding cannot write through it | C8 FAIL on $v.b.c when b is `let` in v's declared type (if the type is not found: b is declared `let` in the tree and never `var`); fix: make b `var` or bind a local copy |
| SW9 | 2026-11-23 | - | XCTAssertEqual mismatch after a skip/clear action (the key is gone instead of holding nil) | `d[k] = x` on a [K: V?] dictionary: when x is nil (even from .map or ??) Swift removes the key instead of storing nil | C9 FAIL on `d[k] = ...` when d is declared [K: V?]; fix: d.updateValue(x, forKey: k) |
| N1 | 2026-11-21 | - | test hangs or fails on a fake host | unit test calls the real network client | FAIL on tests that use the shared URL session or live client without a stub |
| T1 | 2026-11-23 | - | a unit test assertion fails (the code compiles) | wrong logic; no text check can see it | no checker ID (not text-checkable); the owner runs the unit tests before handing the patch over |
| INFRA1 | 2026-11-23 | - | Could not resolve host (only in a CI upload or push step) | a temporary network/DNS failure on the CI runner, not the code | no checker ID; when only an upload/push step fails this way, re-run the job; do not send the change back |
| RUN-BASE | 2026-11-23 | - | a failure the checker covers still reached CI | the checker was run against the parent branch instead of main (the merge target), so bugs already in the parent slipped through | no checker ID (process); run the checker with main (the merge target) as the base |

CHECK (how to tell the rule is followed)
- Every CI failure in the project's build history after this date has a row, and either a check ID with both test results, or 'no checker ID' with the required action.
- The checker's header lists each check ID with the failure it came from.
- Each patch message from an author bot carries the checker's PASS line and version.
