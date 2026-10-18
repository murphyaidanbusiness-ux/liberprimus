"""Turn a sweep progress file (top KEEP_PER_TASK keys per task) into an adjudicate.py candidates file, so every
retained key gets the held-out test, not only the global top KEEP.

    python agents/laneO_quagmire_dodge/progress_to_candidates.py out/tierA_progress.jsonl out/tierA_all_candidates.jsonl
"""
import json
import sys

src, dst = sys.argv[1], sys.argv[2]
rows, seen = [], set()
for line in open(src, encoding="utf-8"):
    rec = json.loads(line)
    for score, kwname, K, sched, dial in rec["best"]:
        key = (tuple(K), tuple(sched), int(dial))
        if key not in seen:
            seen.add(key)
            rows.append({"score": score, "keyword": kwname, "K": K, "sched": sched, "dial": dial, "task": rec["task"]})
rows.sort(key=lambda r: -r["score"])
with open(dst, "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print("%d candidates from %s -> %s (best %+.4f)" % (len(rows), src, dst, rows[0]["score"] if rows else float("nan")))
