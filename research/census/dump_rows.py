"""Print census rows for the orchestrator's judging pass: id, strength, control/null, family, method, scope, constraint.

    python research/census/dump_rows.py PART.md [first] [last]
"""
import sys
sys.path.insert(0, "research/census")
from pathlib import Path
from merge import rows_of

rows = rows_of(Path(sys.argv[1]))
a = int(sys.argv[2]) if len(sys.argv) > 2 else 0
b = int(sys.argv[3]) if len(sys.argv) > 3 else len(rows)
for r in rows[a:b]:
    print("%s [%s c%s n%s] %s :: %s || SCOPE %s || CON %s" % (r["id"], r["strength"], r["control"], r["null"], r["family"],
          r["method"][:150], r["scope"][:160], r["constraint"]))
