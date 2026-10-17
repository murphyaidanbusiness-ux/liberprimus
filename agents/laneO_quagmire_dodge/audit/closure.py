# Static import-closure walk: ast.parse only, nothing is imported or executed.
import ast, sys, os
from pathlib import Path
TREE = Path(sys.argv[1]).resolve()
ENTRY = [TREE/"experiments"/f for f in [
 "dodge_priority_sweep.py","dodge_score_kernel.py","dodge_aware_scorer.py",
 "quagmire_dodge.py","quagmire_dodge_decode.py"]]
# module search: any .py under the tree, keyed by dotted name relative to tree root and by bare name (experiments siblings)
allpy = {}
for p in TREE.rglob("*.py"):
    rel = p.relative_to(TREE)
    allpy.setdefault(p.stem, []).append(p)
STDLIB = set(sys.stdlib_module_names)
seen = {}
stdlib_used = set(); thirdparty = set(); unresolved = set()
def resolve(name):
    top = name.split(".")[0]
    return allpy.get(top, [])
def visit(path):
    if path in seen: return
    seen[path] = True
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError as e:
        print("SYNTAX", path, e); return
    names = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            names += [a.name for a in n.names]
        elif isinstance(n, ast.ImportFrom):
            if n.level and n.level > 0:
                names.append("." * n.level + (n.module or ""))
            elif n.module:
                names.append(n.module)
    for nm in names:
        if nm.startswith("."):
            # relative import: resolve in the file's dir
            mod = nm.lstrip(".")
            base = path.parent
            cand = base / (mod.replace(".", "/") + ".py") if mod else None
            if cand and cand.exists(): visit(cand.resolve())
            else: unresolved.add(f"{path.relative_to(TREE)} -> {nm}")
            continue
        top = nm.split(".")[0]
        if top == "aldegonde":
            parts = nm.split(".")
            base = TREE / "src" / "aldegonde"
            cand = base.joinpath(*parts[1:])
            for c in (cand.with_suffix(".py"), cand / "__init__.py"):
                if c.exists(): visit(c.resolve()); break
            else:
                # package-level name re-exported from __init__
                init = base / "__init__.py"
                if init.exists(): visit(init.resolve())
                unresolved.add(f"aldegonde-name {nm} from {path.relative_to(TREE)}")
            continue
        if top in STDLIB and not allpy.get(top):
            stdlib_used.add(top); continue
        hits = resolve(nm)
        if hits:
            # prefer the file in the same experiments dir, else the only one
            same = [h for h in hits if h.parent == path.parent]
            for h in (same or hits): visit(h.resolve())
        elif top in STDLIB:
            stdlib_used.add(top)
        else:
            thirdparty.add(top)
for e in ENTRY: visit(e.resolve())
print("CLOSURE (%d files):" % len(seen))
for p in sorted(seen, key=lambda x: str(x)): print("  " + str(p.relative_to(TREE)).replace("\\","/"))
print("STDLIB:", " ".join(sorted(stdlib_used)))
print("UNRESOLVED-ALDEGONDE:", [u for u in unresolved if "aldegonde-name" in u][:20])
print("THIRD-PARTY:", " ".join(sorted(thirdparty)))
print("UNRESOLVED RELATIVE:", sorted(unresolved))
