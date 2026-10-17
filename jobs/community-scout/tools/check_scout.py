"""Mechanical half of jobs/community-scout/PROOF.md.

    python jobs/community-scout/tools/check_scout.py research/scoutN_<name>.md

Checks: the required sections exist; every table row in section 1 and 2 has a date, a URL or a local path, and a
verified flag (y / n / unclear); no URL points at an onion address or a tor2web-style gateway.
"""
import re
import sys

GATEWAYS = ("onion.to", "onion.cab", "onion.link", "onion.city", "onion.nu", "onion.lu", "onion.sh", "tor2web",
            "onion.ws", "onion.ly", "onion.pet", "onion.ws")
REQUIRED = ["Bottom line", "New since", "change", "Sources checked"]


def main():
    text = open(sys.argv[1], encoding="utf-8").read()
    p = []
    heads = re.findall(r"(?m)^##\s+(.*)$", text)
    for r in REQUIRED:
        if not any(r.lower() in h.lower() for h in heads):
            p.append("no section heading containing '%s'" % r)
    for u in re.findall(r"https?://[^\s)>\]|]+", text):
        host = re.sub(r"^https?://", "", u).split("/")[0].lower()
        if host.endswith(".onion") or any(g in host for g in GATEWAYS):
            p.append("onion or gateway URL: %s" % u)
    rows = [l for l in text.splitlines() if l.startswith("|") and not re.match(r"^\|\s*-", l)]
    for l in rows[1:]:
        cells = [c.strip() for c in l.strip("|").split("|")]
        if len(cells) < 4 or cells[0].lower() in ("date", "work (where)"):
            continue
        if not re.match(r"\d{4}-\d{2}-\d{2}", cells[0]):
            continue
        if not re.search(r"https?://|dl/|\.md|\.json", l):
            p.append("row without a URL or local path: %s" % l[:80])
        if not re.search(r"\b(y|n|unclear)\b", cells[-1]):
            p.append("row without a verified flag (y/n/unclear): %s" % l[:80])
    if p:
        print("FAIL")
        for x in p:
            print("  - " + x)
        sys.exit(1)
    print("PASS")


if __name__ == "__main__":
    main()
