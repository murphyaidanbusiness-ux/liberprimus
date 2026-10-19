# ABOUTME: Verify-lane check 3 for lane Z: the lane's own pipeline.attack, run on one fresh line-dial plant that
# ABOUTME: laneZ_verify.py enciphered with our encipher. Only this file imports the lane's code.
"""Run by laneZ_verify.py in a subprocess, or by hand from the repository root:

    PYTHONUTF8=1 python -I -X utf8 jobs/verify-lane/runs/laneZ_replay.py <plant.json> <out.json>

The plant JSON holds the cipher units (lists of runes, cut at LP2's lines) and the true plaintext; this file reads the
units only and writes the attack's s1_score, space skip, schedule and decrypted plaintext.
"""
import ctypes
import json
import os
import site
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
os.chdir(ROOT)
sys.path.append(site.getusersitepackages())  # -I hides user site-packages (numpy and scipy live there)
LANE = ROOT / "agents" / "laneZ_dial_units"
XLANE = ROOT / "agents" / "laneX_general_alphabet"


def below_normal():
    if sys.platform == "win32":
        k32 = ctypes.windll.kernel32
        k32.SetPriorityClass(k32.GetCurrentProcess(), 0x4000)


def main():
    below_normal()
    plant_path, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    plant = json.loads(plant_path.read_text(encoding="utf-8"))
    units = plant["units"]
    sys.path[:0] = [str(LANE), str(XLANE)]
    import numpy as np  # noqa: E402
    import xlib, pipeline  # noqa: E402  (the lane's code, imported only here)
    # does the lane's own plant generator give our cipher for the same plaintext, key, schedule and dials?
    lane_units, _ph = xlib.encipher_trace(plant["plain_units"], plant["K"], plant["offsets"], tuple(plant["start"]), 0,
                                          plant["variant"])
    lane_same = [list(map(int, u)) for u in lane_units] == units
    xlib.FLOOR = 1e-4
    t0 = time.time()
    rec = pipeline.attack(units, seed=1)
    out = {"lane_encipher_trace_equal": lane_same,
           "s1_score": float(rec["s1_score"]), "kspace": int(rec["kspace"]), "S": [int(x) for x in rec["S"]],
           "anchors": int(rec["anchors"]), "dead_chains": int(rec["dead_chains"]), "quad_full": float(rec["quad_full"]),
           "plain": [int(x) for x in np.asarray(rec["plain"]).ravel()],
           "phase": [int(x) for x in np.asarray(rec["phase"]).ravel()], "seconds": time.time() - t0}
    out_path.write_text(json.dumps(out), encoding="utf-8")
    print(f"replay: s1_score {out['s1_score']:+.4f}, space skip {out['kspace']}, {len(units)} units, "
          f"{out['seconds']:.0f} s")


if __name__ == "__main__":
    main()
