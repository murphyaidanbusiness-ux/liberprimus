# ABOUTME: Conservative name-based reachability from the community functions lane W calls, over the
# ABOUTME: port's closure; reports whether any reached function holds a network or process call.
"""python -I -X utf8 agents/laneW_clock_dodge/audit/reach_laneW.py

Starts from the functions lane W's code calls in the community modules, follows every call whose
name matches a function defined in the closure (name-based, so it over-approximates), and reports
the sinks (urlretrieve, urlopen, curl, subprocess, run, Popen, system, popen) and any call to main()
or fetch() that the reached set contains.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TREE = REPO / "dl" / "aldegonde_port"
CLOSURE = [
    *(f"experiments/{m}.py" for m in (
        "dodge_aware_scorer", "quagmire_dodge", "doublet_phase_test", "pure_quagmire_restart",
        "quagmire_runner", "base_free_verifier", "ea_direction_test", "fingerprint_battery",
        "d5_partial_leak", "doublet_position_profile", "doublet_word_position", "two_rune_gradient",
        "lp_corpus", "compact_state_models", "external_text_length_match", "sigma_algebraic_floor")),
]
START = {  # functions lane W calls, by module
    "dodge_aware_scorer": ["letter_maps", "word_shifts", "assign"],
    "quagmire_dodge": ["alphabets", "encipher", "schedule"],
    "doublet_phase_test": ["encipher"],
    "pure_quagmire_restart": ["matched_register", "schedule"],
    "quagmire_runner": ["conj_shift", "load_clean", "load_register"],
    "base_free_verifier": ["log_frequencies"],
    "ea_direction_test": ["prose_words"],
    "fingerprint_battery": ["compose"],
}
SINKS = {"urlretrieve", "urlopen", "curl", "subprocess", "run", "Popen", "system", "popen"}


def main() -> int:
    defs: dict[str, list[tuple[str, ast.FunctionDef]]] = {}
    for rel in CLOSURE:
        path = TREE / rel
        if not path.exists():
            print("missing", rel)
            return 2
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                defs.setdefault(node.name, []).append((rel, node))
    todo = [name for names in START.values() for name in names]
    seen: set[str] = set()
    sinks_hit: list[str] = []
    while todo:
        name = todo.pop()
        if name in seen or name not in defs:
            continue
        seen.add(name)
        for rel, fn in defs[name]:
            for node in ast.walk(fn):
                if isinstance(node, ast.Call):
                    f = node.func
                    cname = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
                    if cname in SINKS:
                        sinks_hit.append(f"{rel}:{node.lineno} {name} -> {cname}")
                    if cname:
                        todo.append(cname)
    print(f"reached {len(seen)} community function names from lane W's calls")
    print("sink calls reached:", sinks_hit or "none")
    print("main/fetch reached:", sorted(n for n in seen if n in ("main", "fetch", "selftest")) or "none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
