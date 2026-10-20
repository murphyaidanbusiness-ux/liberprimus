"""Apply a private list of regex redactions to the public copy, then check that none survive.

    python scripts/redact_public.py <redactions.tsv>

Run inside the public worktree (scripts/sync_public.sh does this). Every git-tracked UTF-8 file is rewritten in place.
Each non-empty line of the TSV that does not start with # is: regex<TAB>replacement, applied in file order. The TSV
itself stays private (docs/), so the redacted strings are never written into a published file. Exits 1 if a pattern
still matches anywhere after the pass.
"""
import re
import subprocess
import sys


def main():
    rules = []
    for line in open(sys.argv[1], encoding="utf-8"):
        line = line.rstrip("\r\n")
        if not line.strip() or line.startswith("#"):
            continue
        pat, rep = line.split("\t", 1)
        rules.append((re.compile(pat), rep))
    out = subprocess.run(["git", "ls-files", "-z"], capture_output=True, check=True).stdout
    files = [f for f in out.decode("utf-8").split("\0") if f]
    changed, left = 0, set()
    for f in files:
        try:
            text = open(f, "rb").read().decode("utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        new = text
        for rx, rep in rules:
            new = rx.sub(rep, new)
        if new != text:
            open(f, "wb").write(new.encode("utf-8"))
            changed += 1
        if any(rx.search(new) for rx, _ in rules):
            left.add(f)
    print("redactions: %d rules, %d files changed" % (len(rules), changed))
    if left:
        print("ABORT: redactions left matches in:")
        for f in sorted(left):
            print("  " + f)
        sys.exit(1)


if __name__ == "__main__":
    main()
