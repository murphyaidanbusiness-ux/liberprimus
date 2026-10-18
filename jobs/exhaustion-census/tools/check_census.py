"""Mechanical half of jobs/exhaustion-census/PROOF.md.

    python jobs/exhaustion-census/tools/check_census.py research/census/<part>.md [--min N]

Checks the four sections, the census table (10 cells per row, flag and strength vocabularies, a URL or an existing
local path as source, the constraint cell's form), that reopen candidates cite C/D rows that are not dead, and that no
URL points at an onion address or a gateway. Run from the repository root.
"""
import os
import re
import sys

GATEWAYS = ("onion.to", "onion.cab", "onion.link", "onion.city", "onion.nu", "onion.lu", "onion.sh", "tor2web",
            "onion.ws", "onion.ly", "onion.pet", "onion.direct")
REQUIRED = ["Bottom line", "Census", "Reopen candidates", "Sources checked"]
FLAGS = {"y", "n", "unclear"}


def section(text, name):
    m = re.search(r"(?ms)^##\s+%s[^\n]*\n(.*?)(?=^##\s|\Z)" % re.escape(name), text)
    return m.group(1) if m else ""


def local_exists(src):
    for tok in re.findall(r"`([^`]+)`|((?:dl|agents|research|lp|toolbox|jobs)/[^\s,;)]+)", src):
        path = (tok[0] or tok[1]).strip()
        path = re.split(r"[:#]", path)[0]
        if path and os.path.exists(path):
            return True
    return False


def main():
    args = sys.argv[1:]
    n_min = 15
    if "--min" in args:
        i = args.index("--min")
        n_min = int(args[i + 1])
        del args[i:i + 2]
    text = open(args[0], encoding="utf-8").read()
    p = []
    heads = re.findall(r"(?m)^##\s+(.*)$", text)
    for r in REQUIRED:
        if not any(h.strip().lower().startswith(r.lower()) for h in heads):
            p.append("missing section '## %s'" % r)
    for u in re.findall(r"https?://[^\s)>\]|`]+", text):
        host = re.sub(r"^https?://", "", u).split("/")[0].lower()
        if host.endswith(".onion") or any(g in host for g in GATEWAYS):
            p.append("onion or gateway URL: %s" % u)

    rows = {}
    for line in section(text, "Census").splitlines():
        if not line.startswith("|") or re.match(r"^\|\s*:?-", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0].lower() == "id":
            continue
        rid = cells[0] if cells else "?"
        if len(cells) != 10:
            p.append("%s: %d cells, need 10" % (rid, len(cells)))
            continue
        _id, _method, _family, _scope, control, null, source, strength, _cov, constraint = cells
        if control not in FLAGS:
            p.append("%s: control '%s' not y/n/unclear" % (rid, control))
        if null not in FLAGS:
            p.append("%s: null '%s' not y/n/unclear" % (rid, null))
        if strength not in ("A", "B", "C", "D"):
            p.append("%s: strength '%s' not A/B/C/D" % (rid, strength))
        if not (re.search(r"https?://", source) or local_exists(source)):
            p.append("%s: source is neither a URL nor an existing local path" % rid)
        if not re.match(r"(dead C\d|consistent|unclear)", constraint):
            p.append("%s: constraint cell must start 'dead C<n>', 'consistent' or 'unclear'" % rid)
        rows[rid] = (strength, constraint)
    if len(rows) < n_min:
        p.append("census has %d rows, need at least %d" % (len(rows), n_min))

    reopen = section(text, "Reopen candidates")
    if reopen.strip().lower().rstrip(".") != "none":
        cited = set(re.findall(r"\b[A-Z]{2,4}-\d+\b", reopen))
        if not cited:
            p.append("reopen candidates cite no census id (write 'none' if there are none)")
        for rid in sorted(cited):
            if rid not in rows:
                p.append("reopen candidate %s is not a census id" % rid)
            elif rows[rid][0] not in ("C", "D"):
                p.append("reopen candidate %s has strength %s (only C or D reopen)" % (rid, rows[rid][0]))
            elif rows[rid][1].startswith("dead"):
                p.append("reopen candidate %s is dead by a constraint" % rid)
    if p:
        print("FAIL")
        for x in p:
            print("  - " + x)
        sys.exit(1)
    print("PASS (%d rows)" % len(rows))


if __name__ == "__main__":
    main()
