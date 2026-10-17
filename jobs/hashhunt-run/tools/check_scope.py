"""Proof that a hashhunt run stayed inside its allowlist.

    python jobs/hashhunt-run/tools/check_scope.py hashhunt/data hashhunt/cicada_onions_allowlist.txt

Checks queries.json (every query host-scoped to an allowlisted label, no domain or wildcard query), captures.jsonl
(every capture's onion label allowlisted), store/*.json (every stored capture allowlisted) and plan_state.jsonl
(reports off-list rows the archives returned and the tool dropped). Prints PASS or FAIL with reasons.
"""
import json
import os
import re
import sys

sys.path.insert(0, "hashhunt")
import hashhunt  # noqa: E402


def main():
    d, allow_path = sys.argv[1], sys.argv[2]
    allow = hashhunt.load_allowlist(allow_path)
    problems = []
    q = json.load(open(os.path.join(d, "queries.json")))["queries"]
    for x in q:
        url = hashhunt.qurl(x)
        if "matchType=domain" in url or "url=*." in url:
            problems.append("blind query: %s" % x["id"])
        label = hashhunt.onion_label(dict(x["params"])["url"])
        if label not in allow:
            problems.append("query for a host off the allowlist: %s" % x["id"])
    caps = [json.loads(l) for l in open(os.path.join(d, "captures.jsonl"))] if os.path.exists(os.path.join(d, "captures.jsonl")) else []
    for c in caps:
        if hashhunt.onion_label(c["url"]) not in allow:
            problems.append("capture off the allowlist: %s" % c["id"][:12])
    store = os.path.join(d, "store")
    n_store = 0
    for f in (os.listdir(store) if os.path.isdir(store) else []):
        if f.endswith(".json"):
            n_store += 1
            if hashhunt.onion_label(json.load(open(os.path.join(store, f)))["url"]) not in allow:
                problems.append("stored capture off the allowlist: %s" % f[:12])
    offlist = 0
    if os.path.exists(os.path.join(d, "plan_state.jsonl")):
        offlist = sum(json.loads(l).get("offlist", 0) for l in open(os.path.join(d, "plan_state.jsonl")))
    print("%d queries, %d captures, %d stored, %d off-list rows dropped by the tool" % (len(q), len(caps), n_store, offlist))
    if problems:
        print("FAIL")
        for p in problems[:50]:
            print("  - " + p)
        sys.exit(1)
    print("PASS")


if __name__ == "__main__":
    main()
