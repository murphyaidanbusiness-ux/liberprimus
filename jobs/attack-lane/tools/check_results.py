"""Mechanical half of jobs/attack-lane/PROOF.md.

    python jobs/attack-lane/tools/check_results.py agents/<lane>/RESULTS.md

Prints PASS, or FAIL and one line per problem.
"""
import re
import sys

SECTIONS = ["Hypothesis", "Control", "Null", "Real result", "Verdict"]
VERDICTS = ("NULL", "CANDIDATE", "INCONCLUSIVE (power)")


def section(text, name):
    m = re.search(r"(?ms)^##\s*(?:\d+\.\s*)?%s\b.*?$(.*?)(?=^##\s|\Z)" % re.escape(name), text)
    return m.group(1) if m else None


def check(text):
    p = []
    secs = {s: section(text, s) for s in SECTIONS}
    for s, body in secs.items():
        if body is None:
            p.append("missing section '## %s'" % s)
    if not re.search(r"(?m)^\s*-?\s*\**Gate:?\**:?\s*\S", text):
        p.append("no 'Gate:' line")
    c = secs["Control"] or ""
    m = re.search(r"recovered\s+(\d+)\s*/\s*(\d+)", c, re.I)
    if not m:
        p.append("Control: no 'recovered k/n' count")
    elif int(m.group(1)) == 0:
        p.append("Control: no plant recovered")
    if c and not re.search(r"rank\s*1\b|rank-1|rank one", c, re.I):
        p.append("Control: rank 1 recovery not stated")
    nl = secs["Null"] or ""
    if nl:
        m = re.search(r"(\d+)\s+(?:shuffles|null runs|nulls|shuffled)", nl)
        if not m or int(m.group(1)) < 20:
            p.append("Null: fewer than 20 shuffles stated")
        for k in ("mean", "sd", "max"):
            if not re.search(r"\b%s\b" % k, nl):
                p.append("Null: '%s' not given" % k)
    r = secs["Real result"] or ""
    if r and not re.search(r"\bz\s*[=:]?\s*[+-]?\d", r):
        p.append("Real result: no z-score")
    v = (secs["Verdict"] or "").strip()
    first = re.sub(r"[*`]", "", v.splitlines()[0]).strip() if v else ""
    if v and not first.startswith(VERDICTS):
        p.append("Verdict: first line must start with one of %s" % (VERDICTS,))
    if first.startswith("CANDIDATE"):
        if not re.search(r"oracle.*\b(PASS|FAIL)\b", v, re.I | re.S):
            p.append("Verdict: CANDIDATE without an oracle PASS/FAIL")
    return p


def main():
    text = open(sys.argv[1], encoding="utf-8").read()
    p = check(text)
    if p:
        print("FAIL")
        for x in p:
            print("  - " + x)
        sys.exit(1)
    print("PASS")


if __name__ == "__main__":
    main()
