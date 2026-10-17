# Lists module-level statements that execute on import (not def/class/import/docstring/simple constants,
# and not the `if __name__ == "__main__"` guard). Static only: ast.parse, nothing executed.
import ast, sys
from pathlib import Path
TREE = Path(sys.argv[1]).resolve()
for rel in open(sys.argv[2]).read().split():
    p = TREE / rel
    tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            continue
        if isinstance(node, ast.Expr) and isinstance(getattr(node, "value", None), ast.Constant):
            continue
        if isinstance(node, ast.If) and "__name__" in ast.unparse(node.test) and "__main__" in ast.unparse(node.test):
            continue
        if isinstance(node, ast.Assign) and all(isinstance(t, ast.Name) for t in node.targets):
            src = ast.unparse(node.value)
            # flag only assignments that call something (I/O, compile, load)
            calls = [n for n in ast.walk(node.value) if isinstance(n, ast.Call)]
            if not calls:
                continue
        if isinstance(node, ast.Try):
            pass
        print(f"{rel}:{node.lineno}: {ast.unparse(node)[:160].splitlines()[0]}")
