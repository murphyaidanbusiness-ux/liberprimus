NAME = "Quagmire-odometer with the doublet dodge (lane O's family; community doublet_phase_test.encipher, 'advance')"
DESCRIPTION = """Random keyed alphabet K, a random one-zero five-step schedule, random odometer dials, enciphered by the community's
own function (dl/aldegonde_port/experiments/doublet_phase_test.py, audited in agents/laneO_quagmire_dodge/audit/)."""
import os
import sys

PORT = os.path.join("dl", "aldegonde_port")
sys.path[:0] = [os.path.join(PORT, "src"), os.path.join(PORT, "experiments")]


def encrypt(plain, words, rng):
    from doublet_phase_test import encipher
    from pure_quagmire_restart import schedule
    K = rng.sample(range(29), 29)
    offsets = schedule(rng)
    dials = (rng.randrange(29), rng.randrange(29))
    ws, cur, last = [], [], None
    for r, w in zip(plain, words):
        if w != last and cur:
            ws.append(cur)
            cur = []
        cur.append(r)
        last = w
    ws.append(cur)
    return [c for word in encipher(ws, K, offsets, dials, 0, "advance") for c in word]
