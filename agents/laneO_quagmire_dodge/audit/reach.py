# Conservative reachability: from each entry point's module-level functions, follow calls that resolve
# (by same-module definition or by `from X import name`) to function definitions inside the closure.
# Reports whether any reachable function contains a network / subprocess / delete call.
import ast, sys
from pathlib import Path
TREE = Path(sys.argv[1]).resolve()
files = [l.strip() for l in open(sys.argv[2]) if l.strip()]
mods = {}  # modname -> path
for f in files:
    p = TREE / f
    mod = p.stem if f.startswith("experiments/") else "aldegonde." + p.stem
    mods[mod] = p
def modname(p):
    return p.stem
defs, imports = {}, {}
for f in files:
    p = TREE / f
    tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    m = modname(p)
    defs[m] = {n.name: n for n in tree.body if isinstance(n, (ast.FunctionDef,))}
    imp = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module and not n.level:
            src = n.module.split(".")[-1]
            for a in n.names: imp[a.asname or a.name] = (src, a.name)
    imports[m] = imp
SINKS = {"urlretrieve", "urlopen", "run", "Popen", "system", "popen", "remove", "unlink", "rmtree", "CDLL"}
def calls_of(fn):
    out = []
    for n in ast.walk(fn):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name): out.append(("name", f.id))
            elif isinstance(f, ast.Attribute):
                out.append(("attr", f.attr, ast.unparse(f.value)))
    return out
def walk(entry_mod, entry_fn):
    seen, todo, sinks = set(), [(entry_mod, entry_fn)], []
    while todo:
        m, fn = todo.pop()
        if (m, fn) in seen or m not in defs or fn not in defs[m]: continue
        seen.add((m, fn))
        for c in calls_of(defs[m][fn]):
            if c[0] == "name":
                name = c[1]
                if name in imports[m]:
                    src, real = imports[m][name]; todo.append((src, real))
                elif name in defs[m]:
                    todo.append((m, name))
            else:
                attr, base = c[1], c[2]
                if attr in SINKS: sinks.append((m, fn, attr, base))
                if base in imports[m] or base in [mm for mm in defs]:
                    pass
                # module attribute call e.g. lp_corpus.load_clean
                if base in defs:  # never
                    pass
    return seen, sinks
for entry in [("dodge_priority_sweep", "main"), ("dodge_priority_sweep", "selftest"),
              ("dodge_score_kernel", "main"), ("dodge_aware_scorer", "main"),
              ("quagmire_dodge", "self_test"), ("quagmire_dodge_decode", "self_test")]:
    seen, sinks = walk(*entry)
    print(f"{entry[0]}.{entry[1]}: reaches {len(seen)} functions; sink calls: {sorted(set((s[0],s[1],s[2]) for s in sinks))}")
