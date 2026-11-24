#!/usr/bin/env python3
"""check_patch 2.2.1 - generic pre-push check: catch known CI failures before CI runs.
Project-free. Every project detail comes from a JSON config (see check_patch.example.json).
Rule (libraries/software/ci/failure-library.md): every CI failure adds a library row plus a check here
that FAILS on the broken commit and PASSES on the fix, and a self-test case for it.

Usage:
  check_patch.py --config cfg.json <repo> <commit> [<base>]   exit 0 PASS, 1 FAIL
  check_patch.py --self-test                                  builds a throwaway repo, checks each rule
Exit codes: 0 PASS, 1 FAIL, 2 bad usage, 3 config file missing or not JSON,
  4 repo path is not a git repo, 5 commit or base not found, 6 live_client_file set but missing at commit.
No paths are built in: repo, commit, base and config come from the command line.

Checks (Swift compile traps; network-in-tests; words; secrets), each with its failure-library row:
  N1 (N1) a test calls routes of the configured live client whose bodies use the configured
     real-network call pattern, without the configured stub argument
  N2 (no library row yet) a test uses a configured real-network symbol (e.g. URLSession.shared)
  N3 (no library row yet) a JVM test opens a real connection (openConnection / OkHttpClient) without MockWebServer
  N2w (no library row yet) (warn) a changed test names a host not in allowed_hosts
  W1 (no library row yet) (warn) a configured banned word inside a string literal on an added line
  S1 (no library row yet) a secret-looking string on an added line
  C1 (SW1) `?? .none`  (Swift reads it as Optional.none = nil, not your enum's case none)
  C2 (SW2) a #"..."# raw string containing "# followed by a letter/digit (closes early)
  C3 (SW3) a 6-hex color written as a String constant when the diff uses a hex( helper that takes an integer
  C4 (SW4) calling a function that exists only as top-level private/fileprivate in another file
  C5 (SW5) using a type named *<suffix> (configured suffixes) that nothing in the tree declares
  C6 (SW6) await inside an XCTAssert* call (await is not allowed in that autoclosure)
  C7 (SW7) a test uses a type declared in a Sources module that the test file does not import
"""
import json, os, re, subprocess, sys, tempfile

DEFAULTS = {
    "test_path_markers": ["/Tests/", "/test/", "/androidTest/"],
    "test_exts": [".swift", ".kt", ".java"],
    "live_client_file": "",          # path of a client whose routes may hit the real network
    "live_client_type": "",          # its type name, e.g. "LiveAPIClient"
    "live_route_pattern": r"\brest\.(send|call)\b",  # body pattern meaning 'real network'
    "stub_arg": "",                  # init argument that stubs the network, e.g. "restFetch:"
    "network_symbols": [r"URLSession\.shared"],
    "allowed_hosts": ["localhost", "127.0.0.1", "example.com"],
    "allowed_host_suffixes": [".test"],
    "banned_words": [],              # e.g. ["word1", "word2s?"] regex fragments
    "banned_word_exceptions": [r"\bupdate", r"Date\(", r"dateFormat"],
    "secret_pattern": r"(ghp_|github_pat_|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY)",
    "type_suffixes": ["API", "Client", "Store", "Service"],
    "hex_helper": "hex(",
}

def run(cfg, repo, commit, base):
    def git(*a): return subprocess.run(["git", "-C", repo, *a], capture_output=True, check=True).stdout.decode("utf-8", "replace")
    def show(p):
        try: return git("show", f"{commit}:{p}")
        except subprocess.CalledProcessError: return ""
    files = [l for l in git("diff", "--name-only", base, commit).splitlines() if l]
    tests = [l for l in git("ls-tree", "-r", "--name-only", commit).splitlines()
             if any(m in l for m in cfg["test_path_markers"]) and l.endswith(tuple(cfg["test_exts"]))]
    fails, warns = [], []
    rest_funcs, cur = set(), None
    if cfg["live_client_file"]:
        for line in show(cfg["live_client_file"]).splitlines():
            m = re.search(r"\bfunc\s+([A-Za-z_]\w*)\s*\(", line)
            if m: cur = m.group(1)
            if cur and re.search(cfg["live_route_pattern"], line): rest_funcs.add(cur)
    for f in tests:
        src = show(f)
        if not src: continue
        if f.endswith(".swift"):
            lt = cfg["live_client_type"]
            if lt and lt + "(" in src and not (cfg["stub_arg"] and cfg["stub_arg"] in src):
                hit = sorted(n for n in rest_funcs if re.search(r"\.\s*" + re.escape(n) + r"\s*\(", src))
                if hit: fails.append(f"N1 {f}: calls {lt} routes that use the real network: {', '.join(hit)}")
            for sym in cfg["network_symbols"]:
                if re.search(sym, src): fails.append(f"N2 {f}: test uses {sym} (real network)")
        if f.endswith((".kt", ".java")) and re.search(r"openConnection\(|OkHttpClient\(", src) and "MockWebServer" not in src:
            fails.append(f"N3 {f}: JVM test opens a real network connection")
        if f in files:
            for u in re.findall(r"https?://([A-Za-z0-9.-]+)", src):
                if u not in cfg["allowed_hosts"] and not u.endswith(tuple(cfg["allowed_host_suffixes"])):
                    warns.append(f"N2w {f}: test mentions real host {u}")
    diff = git("diff", "-U0", base, commit)
    bw = re.compile(r"\b(" + "|".join(cfg["banned_words"]) + r")\b", re.I) if cfg["banned_words"] else None
    exc = re.compile("|".join(cfg["banned_word_exceptions"])) if cfg["banned_word_exceptions"] else None
    added = []
    fname = None
    for line in diff.splitlines():
        if line.startswith("+++ "): fname = line[6:]; continue
        if line.startswith("+") and not line.startswith("+++"): added.append((fname, line[1:]))
    for fname, s in added:
        quoted = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', s) + (re.findall(r">([^<]+)<", s) if (fname or "").endswith(".xml") else [])
        if bw:
            for q in quoted:
                if bw.search(q) and not (exc and exc.search(q)): warns.append(f"W1 {fname}: possible banned word: \"{q[:60]}\"")
        if re.search(cfg["secret_pattern"], s): fails.append(f"S1 {fname}: looks like a secret")
    def tree_grep(pat):
        return subprocess.run(["git", "-C", repo, "grep", "-h", "-E", pat, commit, "--", "*.swift"], capture_output=True).stdout.decode("utf-8", "replace")
    decls = tree_grep(r"\b(func|protocol|class|struct|enum|typealias|actor)\s+[A-Za-z_]")
    declared = set(re.findall(r"\b(?:func|protocol|class|struct|enum|typealias|actor)\s+([A-Za-z_]\w*)", decls))
    top_private = set(re.findall(r"^(?:private|fileprivate)\s+func\s+([A-Za-z_]\w*)", decls, re.M))
    top_open = set(re.findall(r"^(?:public\s+|internal\s+|@\w+\s+)*func\s+([A-Za-z_]\w*)", decls, re.M))
    type_mods = {}
    decl_out = subprocess.run(["git", "-C", repo, "grep", "-n", "-E",
        r"(public |internal |open |private |fileprivate |package )*(struct|class|enum|protocol|actor|typealias) [A-Za-z_][A-Za-z0-9_]*",
        commit, "--", "*.swift"], capture_output=True).stdout.decode("utf-8", "replace")
    for gl in decl_out.splitlines():
        parts = gl.split(":", 3)
        if len(parts) < 4: continue
        path, text = parts[1], parts[3]
        mm = re.search(r"(?:^|/)Sources/([^/]+)/", path)
        tm = re.search(r"\b(?:struct|class|enum|protocol|actor|typealias)\s+([A-Za-z_]\w*)", text)
        if mm and tm:
            type_mods.setdefault(tm.group(1), set()).add(mm.group(1))
    KW = set("if guard switch while for return catch try await some any init super self Self in where let var case func set get as is do else repeat defer".split())
    suf = "|".join(map(re.escape, cfg["type_suffixes"]))
    hexh = cfg["hex_helper"]
    for fname, raw in added:
        if not (fname or "").endswith(".swift"): continue
        code = re.sub(r"//.*$", "", raw); short = code.strip()[:90]
        if re.search(r"\?\?\s*\.none\b", code):
            fails.append(f"C1 {fname}: `?? .none` means nil here; write `?? YourEnum.none`. Line: {short}")
        if re.search(r'(?<!#)#"', raw) and re.search(r'(?<!#)"#[0-9A-Za-z]', raw):
            fails.append(f"C2 {fname}: raw string contains \"# so it ends early; use ##\"...\"##. Line: {short}")
        if hexh and hexh in diff and re.search(r'"#?[0-9A-Fa-f]{6}"', code) and re.search(r"\blet\s+\w+\s*(:\s*String\s*)?=", code):
            fails.append(f"C3 {fname}: color written as a String but {hexh}...) takes an integer; write 0xRRGGBB. Line: {short}")
        fsrc = show(fname)
        for name in set(re.findall(r"(?<![\.\w])([a-z]\w*)\s*\(", code)) - KW:
            if name in top_private and name not in top_open and not re.search(r"\bfunc\s+" + re.escape(name) + r"\b", fsrc):
                fails.append(f"C4 {fname}: calls {name}(...) but it is private to another file. Line: {short}")
        if suf:
            for t in set(re.findall(r"\b([A-Z]\w*(?:" + suf + r"))\b", code)):
                if t not in declared: fails.append(f"C5 {fname}: uses type {t} that nothing declares (missing commit?)")
        if re.search(r"\bXCTAssert\w*\s*\(.*\bawait\b", code):
            fails.append(f"C6 {fname}: await inside XCTAssert is not allowed in that autoclosure; await first, then assert. Line: {short}")
        is_test = any(m in (fname or "") for m in cfg["test_path_markers"]) and (fname or "").endswith(".swift")
        if is_test:
            imports = set(re.findall(r"^(?:@testable\s+)?import\s+([A-Za-z_]\w*)", fsrc, re.M))
            local = set(re.findall(r"\b(?:struct|class|enum|protocol|actor|typealias)\s+([A-Za-z_]\w*)", fsrc))
            bare = re.sub(r'#+"#', '""', re.sub(r'#+".*?"+#', '""', re.sub(r"'(?:\\.|[^'\\])*'", "''", re.sub(r'"(?:\\.|[^"\\])*"', '""', code))))
            for t in set(re.findall(r"(?<![.\w])([A-Z]\w{2,})\b", bare)) - local - KW:
                mods = type_mods.get(t) or set()
                if mods and imports.isdisjoint(mods):
                    fails.append(f"C7 {fname}: uses type {t} from {', '.join(sorted(mods))} but does not import it. Line: {short}")
    return files, tests, fails, warns

def report(files, tests, fails, warns, commit, base):
    for w in warns: print("WARN", w)
    for x in fails: print("FAIL", x)
    print(("FAIL" if fails else "PASS") + f": {commit[:7]} vs {base[:12]}, {len(files)} changed files, {len(tests)} test files, {len(fails)} fail, {len(warns)} warn")
    return 1 if fails else 0

SELF_TEST_CFG = dict(DEFAULTS, live_client_file="Src/Live.swift", live_client_type="LiveClient",
                     stub_arg="fetch:", banned_words=["badword"])
CASES = {  # name: (path, content, expected check id or None for PASS)
    "C1": ("Src/A.swift", "enum Mode { case none, on }\nlet m: Mode = x ?? .none\n", "C1"),
    "C1fix": ("Src/A.swift", "enum Mode { case none, on }\nlet m: Mode = x ?? Mode.none\n", None),
    "C2": ("Src/B.swift", 'let j = #"{"c":"#c0ffee"}"#\n', "C2"),
    "C2fix": ("Src/B.swift", 'let j = ##"{"c":"#c0ffee"}"##\n', None),
    "C3": ("Src/C.swift", 'func use() { _ = hex(1) }\nstatic let ring = "9A8FA3"\n', "C3"),
    "C3fix": ("Src/C.swift", "func use() { _ = hex(1) }\nstatic let ring: UInt32 = 0x9A8FA3\n", None),
    "C4": ("Src/D.swift", "func paint() { _ = helper(1) }\n", "C4"),
    "C4fix": ("Src/D.swift", "private func helper(_ x: Int) -> Int { x }\nfunc paint() { _ = helper(1) }\n", None),
    "C5": ("Src/E.swift", "func f(api: WidgetAPI) {}\n", "C5"),
    "C5fix": ("Src/E.swift", "protocol WidgetAPI {}\nfunc f(api: WidgetAPI) {}\n", None),
    "N1": ("App/Tests/LiveTests.swift", "let c = LiveClient(host: \"x.test\")\nc.load()\n", "N1"),
    "N1fix": ("App/Tests/LiveTests.swift", "let c = LiveClient(host: \"x.test\", fetch: stub)\nc.load()\n", None),
    "N2": ("App/Tests/NetTests.swift", "let s = URLSession.shared\n", "N2"),
    "N2fix": ("App/Tests/NetTests.swift", "let s = StubSession()\n", None),
    "N3": ("app/src/test/NetTest.kt", "val c = OkHttpClient()\n", "N3"),
    "N3fix": ("app/src/test/NetTest.kt", "val c = OkHttpClient(); val m = MockWebServer()\n", None),
    "S1": ("Src/F.swift", 'let k = "ghp_' + "x" * 20 + '"\n', "S1"),
    "S1fix": ("Src/F.swift", 'let k = ProcessInfo.processInfo.environment["TOKEN"]\n', None),
    "W1": ("Src/G.swift", 'let t = "a badword here"\n', None),  # warn only, still PASS
    "C6": ("App/Tests/AwaitTests.swift", "XCTAssertNil(await api.saved())\n", "C6"),
    "C6fix": ("App/Tests/AwaitTests.swift", "let v = await api.saved()\nXCTAssertNil(v)\n", None),
    "C7": ("App/Tests/ImportTests.swift", "func session() -> TicketSession { TicketSession() }\n", "C7"),
    "C7fix": ("App/Tests/ImportTests.swift", "@testable import Models\nfunc session() -> TicketSession { TicketSession() }\n", None),
}

def self_test():
    ok = True
    for name, (path, content, expect) in CASES.items():
        d = tempfile.mkdtemp()
        g = lambda *a: subprocess.run(["git", "-C", d, *a], capture_output=True, check=True)
        g("init", "-q"); g("config", "user.email", ""); g("config", "user.name", "t")
        os.makedirs(os.path.join(d, "Src"), exist_ok=True)
        os.makedirs(os.path.join(d, "Sources/Models"), exist_ok=True)
        open(os.path.join(d, "Src/Live.swift"), "w").write("struct LiveClient {\n func load() { rest.send() }\n}\nprivate func helper(_ x: Int) -> Int { x }\n")
        open(os.path.join(d, "Sources/Models/Models.swift"), "w").write("public struct TicketSession {}\n")
        g("add", "-A"); g("commit", "-qm", "base")
        base = subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True).stdout.decode().strip()
        os.makedirs(os.path.dirname(os.path.join(d, path)), exist_ok=True)
        open(os.path.join(d, path), "w").write(content)
        g("add", "-A"); g("commit", "-qm", name)
        _, _, fails, warns = run(SELF_TEST_CFG, d, "HEAD", base)
        ids = {x.split()[0] for x in fails}
        good = (expect in ids) if expect else not fails
        if name == "W1": good = good and any(w.startswith("W1") for w in warns)
        print(("ok  " if good else "BAD ") + f"{name}: expected {expect or 'PASS'}, got {sorted(ids) or 'PASS'}")
        ok &= good
    print("SELF-TEST " + ("PASS" if ok else "FAIL")); return 0 if ok else 1

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--self-test"]: sys.exit(self_test())
    cfg = dict(DEFAULTS)
    def die(code, msg): print(f"ERROR {code}: {msg}", file=sys.stderr); sys.exit(code)
    if a[:1] == ["--config"]:
        if len(a) < 2: die(2, "--config needs a file")
        try: cfg.update(json.load(open(a[1])))
        except (OSError, ValueError) as e: die(3, f"config {a[1]} missing or not JSON: {e}")
        a = a[2:]
    if len(a) < 2: die(2, "usage: check_patch.py [--config cfg.json] <repo> <commit> [<base>]")
    repo, commit = a[0], a[1]; base = a[2] if len(a) > 2 else "origin/main"
    if subprocess.run(["git", "-C", repo, "rev-parse", "--git-dir"], capture_output=True).returncode: die(4, f"{repo} is not a git repo")
    for r in (commit, base):
        if subprocess.run(["git", "-C", repo, "rev-parse", "--verify", "-q", r + "^{commit}"], capture_output=True).returncode: die(5, f"{r} not found in {repo}")
    if cfg["live_client_file"] and subprocess.run(["git", "-C", repo, "cat-file", "-e", f"{commit}:{cfg['live_client_file']}"], capture_output=True).returncode:
        die(6, f"live_client_file {cfg['live_client_file']} not found at {commit}")
    sys.exit(report(*run(cfg, repo, commit, base), commit, base))
