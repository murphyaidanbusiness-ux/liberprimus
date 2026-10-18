"""Size-matched nulls for LP2 tests (the AGENTS.md rule: chain-model nulls keep the doublet deficit).

    import sys; sys.path.insert(0, "toolbox"); import nulls
    pages = nulls.lp_pages()                       # list of rune lists, pages 0-54
    nulls.shuffle_runes(pages, rng)                # runes permuted within each page (kills the deficit)
    nulls.shuffle_increments(pages, rng)           # increments permuted within each page, runes rebuilt (keeps it)
"""
import sys

sys.path.insert(0, "lp")
import lpdata  # noqa: E402

M = 29


def lp_pages():
    U, _C, sha = lpdata.unsolved()
    assert sha == "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
    return [list(p["idx"]) for p in U]


def shuffle_runes(pages, rng):
    out = []
    for p in pages:
        q = list(p)
        rng.shuffle(q)
        out.append(q)
    return out


def shuffle_increments(pages, rng):
    out = []
    for p in pages:
        if len(p) < 2:
            out.append(list(p))
            continue
        d = [(p[i] - p[i - 1]) % M for i in range(1, len(p))]
        rng.shuffle(d)
        q = [p[0]]
        for x in d:
            q.append((q[-1] + x) % M)
        out.append(q)
    return out
