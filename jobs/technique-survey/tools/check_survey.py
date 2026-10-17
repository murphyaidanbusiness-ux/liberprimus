"""Mechanical half of jobs/technique-survey/PROOF.md.

    python jobs/technique-survey/tools/check_survey.py FILE [--min N]

Prints PASS, or FAIL and one line per problem. Exit code 0 on PASS, 1 on FAIL.
"""
import re
import sys

FIELDS = ["Source", "Exploits", "LP2 constraints", "Prior coverage", "Verdict", "Test design"]
VERDICTS = {"applicable-untested", "applicable-tested", "not-applicable"}
URL = re.compile(r"https?://[^\s)>\]]+")


def entries(text):
    blocks = re.split(r"(?m)^### T:\s*", text)[1:]
    out = []
    for b in blocks:
        name = b.splitlines()[0].strip()
        body = b.split("\n## ")[0]
        fields = {}
        for f in FIELDS:
            m = re.search(r"(?m)^- \*{0,2}%s\*{0,2}:\s*(.+)$" % re.escape(f), body)
            fields[f] = m.group(1).strip() if m else ""
        out.append((name, fields, body))
    return out


def check(text, minimum):
    problems = []
    es = entries(text)
    if len(es) < minimum:
        problems.append("only %d entries (need >= %d)" % (len(es), minimum))
    m = re.search(r"(?ms)^## Sources opened\s*$(.*?)(?=^## |\Z)", text)
    opened = set(u.rstrip(".,;") for u in URL.findall(m.group(1))) if m else set()
    if not m:
        problems.append("no '## Sources opened' section")
    names = {n for n, _f, _b in es}
    for name, f, body in es:
        for k in FIELDS:
            if not f[k]:
                problems.append("%s: missing field '%s'" % (name, k))
        if f["LP2 constraints"] and not re.search(r"\bC[1-6]b?\b", f["LP2 constraints"]):
            problems.append("%s: LP2 constraints line names none of C1-C6" % name)
        v = f["Verdict"].split()[0].strip("`*.,;") if f["Verdict"] else ""
        if f["Verdict"] and v not in VERDICTS:
            problems.append("%s: verdict '%s' not one of %s" % (name, v, sorted(VERDICTS)))
        if v == "applicable-untested":
            td = f["Test design"].lower()
            if not ("control" in td and "null" in td):
                problems.append("%s: applicable-untested but Test design lacks a planted control and a null" % name)
        if v == "applicable-tested" and not re.search(r"\blane [A-R]\b|ledger|LEDGER|\.md|\.json", f["Prior coverage"]):
            problems.append("%s: applicable-tested but Prior coverage names no lane (A-R) or ledger file" % name)
        urls = [u.rstrip(".,;") for u in URL.findall(body)]
        for u in urls:
            if u not in opened:
                problems.append("%s: cites %s, which is not in Sources opened" % (name, u))
        if not urls and not re.search(r"(?i)\b(p\.|pp\.|chapter|ch\.|section|vol\.)\s*\d", f["Source"]):
            problems.append("%s: Source has neither a URL nor a book page/chapter" % name)
    t = re.search(r"(?ms)^## Top 5\s*$(.*?)(?=^## |\Z)", text)
    if not t:
        problems.append("no '## Top 5' section")
    else:
        ranked = re.findall(r"(?m)^\s*\d+\.\s*\**([^*\n:(]+)", t.group(1))
        ranked = [r.strip() for r in ranked]
        if len(ranked) < 5 and minimum >= 12:
            problems.append("Top 5 lists %d items" % len(ranked))
        verdict = {n: (f["Verdict"].split()[0].strip("`*.,;") if f["Verdict"] else "") for n, f, _b in es}
        for r in ranked:
            match = [n for n in names if n.lower().startswith(r.lower()) or r.lower().startswith(n.lower())]
            if not match:
                problems.append("Top 5 item '%s' is not an entry name" % r)
            elif verdict[match[0]] != "applicable-untested":
                problems.append("Top 5 item '%s' is not applicable-untested" % r)
    return problems


def main():
    args = sys.argv[1:]
    minimum = 12
    if "--min" in args:
        i = args.index("--min")
        minimum = int(args[i + 1])
        del args[i:i + 2]
    text = open(args[0], encoding="utf-8").read()
    problems = check(text, minimum)
    if problems:
        print("FAIL")
        for p in problems:
            print("  - " + p)
        sys.exit(1)
    print("PASS (%d entries)" % len(entries(text)))


if __name__ == "__main__":
    main()
