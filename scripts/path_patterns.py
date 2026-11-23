#!/usr/bin/env python3
"""path_patterns.py (v0.1.0) - the one list of hardcoded-path patterns, shared by check_scripts.py and library_intake_scan.py.
Why one file: the script check and the library intake check must flag the same things; a second copy would drift.
Some patterns spell a word with one letter in brackets (one[d]rive) so this file does not match its own text.
Import only; it has no command line. A script that needs it and cannot find it beside itself exits 24 (ERROR_CODES.txt)."""
import re

PATH_PATTERNS = [
    ("drive_letter", re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]")),                        # a drive letter then a slash
    ("unc_share", re.compile(r"(?:^|(?<=[\s\"'=(,]))\\{2}(?:\\{2})?[A-Za-z0-9._$-]+\\{1,2}[A-Za-z0-9._$-]")),  # a network share
    ("user_folder", re.compile(r"(?i)[\\/](home|users|root|documents and settings)[\\/][^\s\\/\"'|]+")),
    ("system_folder", re.compile(r"(?<![\w.])/(usr|etc|var|opt|tmp|mnt|srv|media|workspace|Library|Applications|Volumes|private)/")),
    ("home_tilde", re.compile(r"(?<![\w$])~[\\/]")),                                          # a tilde then a slash (a user's home)
    ("url", re.compile(r"(?i)\b(https?|ftp|file|smb)://")),                                     # any web or file address
    ("cloud_folder", re.compile(r"(?i)(one[d]rive|share[p]oint|drop[b]ox|google [d]rive|i[c]loud)[^\s\"'|]*[\\/]")),
]

def path_hits(line):
    """Return the names of the patterns a line hits (never the matched text, which may be personal)."""
    return [name for name, rx in PATH_PATTERNS if rx.search(line)]
