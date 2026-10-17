# Expected gate verdicts on the fixture ciphers (`gate_sim.py <file> --seeds 2`, measured 2026-10-16, re-measured after C2c was added)

| fixture | final line | why |
|---|---|---|
| `otp_dodge5.py` | `GATE PASS` | doublets about 0.86% (inside 0.4-1.0%), IoC 1.00, conditional IoC flat; C5 soft fail on one seed is allowed |
| `vigenere7.py` | `GATE FAIL: C1 C2 C2b C2c C3 C6` | periodic (IoC about 1.1) and additive (doublets about 3.3-4.3%) |
| `norepeat.py` | `GATE FAIL: C2 C6` | strict no-repeat gives 0 doublets against LP2's 86 |

Since the majority rule (2026-10-16), each run also prints `fails per constraint over N seeds: {...}` before the final line.
