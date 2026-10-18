import ast, sys
from pathlib import Path
TREE = Path(sys.argv[1]).resolve()
targets = ("urlretrieve", "urlopen", "Request", "subprocess", "remove", "unlink", "rmtree", "system", "popen", "mkdir", "CDLL", "exec", "eval")
for rel in open(sys.argv[2]).read().split():
    p = TREE / rel
    tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    parents = {}
    for n in ast.walk(tree):
        for c in ast.iter_child_nodes(n): parents[c] = n
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            name = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
            if name in targets:
                cur = n; fn = "<module>"
                while cur in parents:
                    cur = parents[cur]
                    if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        fn = cur.name; break
                gated = False
                cur = n
                while cur in parents:
                    cur = parents[cur]
                    if isinstance(cur, ast.If) and "__main__" in ast.unparse(cur.test): gated = True
                print(f"{rel}:{n.lineno} {name}() in {fn}  (under __main__ guard: {gated})")
