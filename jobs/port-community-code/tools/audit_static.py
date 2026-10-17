"""Static safety audit of community code before anything from it runs. ast.parse only: nothing is imported or executed.

    python jobs/port-community-code/tools/audit_static.py TREE ENTRY.py [ENTRY.py ...]

TREE is the community checkout (e.g. dl/aldegonde_clone); ENTRY paths are relative to TREE. Prints:
  1. the import closure of the entry points inside TREE (by module name; stdlib and third-party are listed, not followed)
  2. every risky call site in the closure, with file:line and the enclosing function
     (network, process, deletion, dynamic code, deserialisation, native libraries, file writes)
  3. statements that run at import time (anything at module level except def/class/import/constants/main guard)
Exit code 0. Judging the findings is the job's step, not the script's.
"""
import ast
import sys
from pathlib import Path

RISKY = {
    "network": {"urlopen", "urlretrieve", "Request", "socket", "create_connection", "HTTPConnection",
                "HTTPSConnection", "get", "post", "requests"},
    "process": {"system", "popen", "Popen", "run", "call", "check_call", "check_output", "spawn", "startfile"},
    "delete": {"remove", "unlink", "rmtree", "rmdir", "removedirs"},
    "dynamic": {"eval", "exec", "compile", "__import__", "import_module"},
    "deserialise": {"load", "loads"},
    "native": {"CDLL", "WinDLL", "LoadLibrary", "cdll"},
    "write": {"write_text", "write_bytes"},
}
MODS_FOR = {"network": {"urllib", "urllib.request", "http", "socket", "requests", "httpx", "ftplib"},
            "process": {"subprocess", "os"}, "deserialise": {"pickle", "marshal", "shelve", "dill"}}


def closure(tree, entries):
    dotted = {}                        # every dotted suffix of every module path -> files
    for p in tree.rglob("*.py"):
        parts = list(p.relative_to(tree).with_suffix("").parts)
        if parts[-1] == "__init__":
            parts = parts[:-1]
        for i in range(len(parts)):
            dotted.setdefault(".".join(parts[i:]), []).append(p)
    std = set(sys.stdlib_module_names)
    seen, todo, external = {}, [tree / e for e in entries], set()
    while todo:
        p = todo.pop()
        if p in seen or not p.exists():
            continue
        t = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        seen[p] = t
        for n in ast.walk(t):
            names = []
            if isinstance(n, ast.Import):
                names = [a.name for a in n.names]
            elif isinstance(n, ast.ImportFrom) and n.module:
                names = [n.module] + [n.module + "." + a.name for a in n.names]
            for nm in names:
                root = nm.split(".")[0]
                if root in std:
                    external.add(root)
                    continue
                hit = False
                for k in range(nm.count(".") + 1, 0, -1):          # longest dotted prefix that is a module in the tree
                    cand = ".".join(nm.split(".")[:k])
                    if cand in dotted:
                        todo.extend(dotted[cand])
                        hit = True
                        break
                if not hit:
                    external.add(root)
    return seen, external


def findings(path, t):
    parents = {c: n for n in ast.walk(t) for c in ast.iter_child_nodes(n)}
    imported = {a.name.split(".")[0] for n in ast.walk(t) if isinstance(n, ast.Import) for a in n.names}
    imported |= {n.module.split(".")[0] for n in ast.walk(t) if isinstance(n, ast.ImportFrom) and n.module}
    out = []
    for n in ast.walk(t):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
        base = ast.unparse(f.value) if isinstance(f, ast.Attribute) else ""
        for kind, calls in RISKY.items():
            if name not in calls:
                continue
            if kind in MODS_FOR and not (MODS_FOR[kind] & ({base.split(".")[0]} | imported)) and kind != "process":
                continue
            if kind == "network" and name in {"get", "post"} and not base.startswith(("requests", "httpx", "session")):
                continue
            if kind == "dynamic" and base and name in {"compile"}:
                continue
            if kind == "process" and not (base.startswith(("subprocess", "os")) or name in {"Popen", "startfile"}):
                continue
            if kind == "deserialise" and not base.startswith(("pickle", "marshal", "shelve", "dill")):
                continue
            fn = n
            while fn in parents and not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn = parents[fn]
            where = fn.name if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) else "<module>"
            out.append((kind, n.lineno, where, ast.unparse(n)[:110]))
        if name == "open" and len(n.args) > 1 and isinstance(n.args[1], ast.Constant) and set(str(n.args[1].value)) & set("wax"):
            out.append(("write", n.lineno, "?", ast.unparse(n)[:110]))
    return sorted(out, key=lambda r: r[1])


def import_time(t):
    rows = []
    for node in t.body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue
        if isinstance(node, ast.If) and "__main__" in ast.unparse(node.test):
            continue
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and all(
                isinstance(v, (ast.Constant, ast.Tuple, ast.List, ast.Dict, ast.Set, ast.Name, ast.BinOp, ast.UnaryOp,
                               ast.Attribute, ast.Subscript, ast.Call, ast.ListComp, ast.DictComp, ast.SetComp))
                for v in [node.value] if v is not None) and not any(isinstance(c, ast.Call) and getattr(c.func, "id", "") in ("open",) for c in ast.walk(node)):
            if not any(isinstance(c, ast.Call) for c in ast.walk(node)):
                continue
        rows.append((node.lineno, ast.unparse(node).splitlines()[0][:110]))
    return rows


def main():
    tree = Path(sys.argv[1]).resolve()
    seen, external = closure(tree, sys.argv[2:])
    print("== 1. closure: %d files inside the tree" % len(seen))
    for p in sorted(seen):
        print("  ", p.relative_to(tree).as_posix())
    print("   outside the tree (not followed):", ", ".join(sorted(external)))
    print("== 2. risky call sites")
    for p in sorted(seen):
        for kind, line, where, src in findings(p, seen[p]):
            print("  %-11s %s:%d in %s: %s" % (kind, p.relative_to(tree).as_posix(), line, where, src))
    print("== 3. statements with calls that run at import time")
    for p in sorted(seen):
        for line, src in import_time(seen[p]):
            print("  %s:%d: %s" % (p.relative_to(tree).as_posix(), line, src))


if __name__ == "__main__":
    main()
