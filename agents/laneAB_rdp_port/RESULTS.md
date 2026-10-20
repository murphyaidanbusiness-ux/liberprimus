# Lane AB: RuneDecrypterPrime v1.0.0, its v2 transcription against the pin, and its scorer as our second scorer (2026-10-19)

Job: port-community-code. Upstream: mortlach/RuneDecrypterPrime, tag v1.0.0 = `61bf2c7865892944a3a4ae3d72b6c8e9745c86f0`
(commit dated 2026-09-13, released 2026-09-14), cloned to `dl/rdp` by `scripts/fetch_sources.sh`. Source:
research/scout7_discord.md section 3 item 1.

## Verdict

- **The v2 transcription has exactly our LP2 runes.** Pages 0-54 of `assets/liber_primus/liber-primus__transcription--master-v2.txt`
  give 12,956 runes whose comma-joined index sha is the pin (`023312066df4...1585`). There are 0 substitutions, 0 insertions
  and 0 deletions, and every one of the 55 pages has the same rune count and the same runes. RDP's own parser
  (`LPTranscript`) gives the same stream. Numbers computed on runes alone (doublets, IoC, every rune-level statistic) are
  identical for RDP users and for us.
- **Word starts: 4 differences, none in the headline statistics.** v2 has 2,897 word boundaries in LP2 and the pin has 2,895.
  Three apostrophes split words (flat runes 1110, 5138, 10089), and v2 joins one word across a list numeral on page 37
  (flat 9035). The doublet count stays **86** (63 within words, 23 across) and the within-word lag-5 echo stays
  **104/2105 = 4.94%, z = +3.75**, under RDP's word rule and under the loader's.
- **Page numbering.** RDP's canonical page = our page for pages 0-49, and our page + 1 for pages 50-54 (RDP 50 is the
  runeless page). So RDP's "p54/p55" are our p53/p54 (runes 12648-12955, 308 runes). RDP's main-transcript page ID =
  canonical page + 15, so our p00 is RDP main page 15.
- **The port builds on Windows with MSVC, no WSL and no source patch.** RDP's `setup.py` already carries MSVC flags. All
  three native modules (`_fastlm`, `_hamming`, `_span_hamming_fast`) compile with Visual Studio Build Tools 18 under
  Python 3.13. `port.patch` is empty.
- **Kernel = reference; upstream selftest passes; our planted controls recover.** The compiled n-gram kernel equals an
  independent pure-Python re-implementation on all 16 tables of orders 1-4 (largest relative difference 3.2e-6).
  RDP's CI-light tests for scoring, LP data and solved pages give 395 passed and 8 skipped (CUDA). With the LM-large
  assets the 15 full_assets tests also pass, including RDP re-solving all nine solved LP pages. Tutorials 01 and 02
  recover their keys. Our Vigenère plants (260 runes, periods 2-9) are recovered 20/20 by RDP's default scorer and
  40/40 by each RDP character-lane setting and by our quadgram scorer. On 100 runes with periods 6-12, RDP's
  char-bigram average log-probability recovers 35/40 against our quadgram's 16/40 with the same search. All of the
  quadgram's misses are search misses: it judges correctly but gives the search little gradient. At order 4, RDP's
  char 4-gram average log-probability recovers 40/40 and 39/40 with no scorer miss, the best of every scorer tried.
- **LM3/LM4 installed (owner's yes).** Both release archives (899.6 MB) match their pinned sha256; 96 files were
  extracted by our own path-safe installer, and all 129 manifest files verify (section 8).
- **RDP pitfall found:** without an explicit order-weight map, RDP ignores `character_ngram_order` and scores at order 2,
  with no warning. The wrapper passes the map and checks the effective models (section 6).

## 1. Transcription diff (step 1)

Commands (data files only; no RDP code runs in the first):

    python -I agents/laneAB_rdp_port/diff_v2.py > agents/laneAB_rdp_port/out_diff_v2.txt
    dl/rdp_venv/Scripts/python.exe -I agents/laneAB_rdp_port/xcheck_rdp_parser.py > agents/laneAB_rdp_port/out_xcheck_rdp_parser.txt

`diff_v2.py` imports lane R's `transcriptions.py` and `compare.py` (not modified). It adds three families (V2 under RDP's
word rule, V2K under the loader's rule, RV1 for the historical v1 that RDP ships) and runs lane R's `analyse` on them
next to a direct per-page comparison. Tag handling follows RDP's README and parser: `[red]` and `[/red]` are dropped,
each `[dot_N...]` tag is one punctuation mark, digits and letters are neither runes nor separators, and the delimiter
legend before the first blank line is skipped.

Files hashed: v2 = 57,236 bytes, sha256 `431202b7...4979` (its `.part001` companion is byte-identical). RDP's v1 copy =
55,485 bytes, sha256 `b32985da...b05e5d`. Both carry 15,933 runic characters with runic-stream sha12 `d620b4f6e88e`.
aldegonde's master (lane R's family M, `ee1f3d0d10e9`) has the same count but a different runic stream. It differs from
RDP's in one place, an ᛁ moved by one position at runic characters 1750-1751 of 15,933, which is in LP1. On pages 0-54
all three agree with the pin.

Word rules: RDP's parser (`lp_transcript.Delimiters.word_breakers`) ends a word at `- , . ; " '` and at every dot tag.
`& $ §`, line ends `/`, page ends `%` and numerals do not end a word. The loader (lpdata) ends words at `- . & $ §`.

Per page (`per_page_v2.tsv`; RDP page = canonical / main-transcript ID; the word-start columns are the same under RDP's
rule and the loader's rule):

| Pin page | RDP page (canon / main ID) | Pin start | Runes (pin = v2) | Identical | Sub / ins / del | Word starts: v2 lacks / adds |
|---|---|---|---|---|---|---|
| p00 | 0 / 15 | 0 | 262 | yes | 0 / 0 / 0 | 0 / 0 |
| p01 | 1 / 16 | 262 | 266 | yes | 0 / 0 / 0 | 0 / 0 |
| p02 | 2 / 17 | 528 | 201 | yes | 0 / 0 / 0 | 0 / 0 |
| p03 | 3 / 18 | 729 | 217 | yes | 0 / 0 / 0 | 0 / 0 |
| p04 | 4 / 19 | 946 | 261 | yes | 0 / 0 / 0 | 0 / 1 |
| p05 | 5 / 20 | 1207 | 263 | yes | 0 / 0 / 0 | 0 / 0 |
| p06 | 6 / 21 | 1470 | 196 | yes | 0 / 0 / 0 | 0 / 0 |
| p07 | 7 / 22 | 1666 | 208 | yes | 0 / 0 / 0 | 0 / 0 |
| p08 | 8 / 23 | 1874 | 255 | yes | 0 / 0 / 0 | 0 / 0 |
| p09 | 9 / 24 | 2129 | 268 | yes | 0 / 0 / 0 | 0 / 0 |
| p10 | 10 / 25 | 2397 | 263 | yes | 0 / 0 / 0 | 0 / 0 |
| p11 | 11 / 26 | 2660 | 273 | yes | 0 / 0 / 0 | 0 / 0 |
| p12 | 12 / 27 | 2933 | 261 | yes | 0 / 0 / 0 | 0 / 0 |
| p13 | 13 / 28 | 3194 | 272 | yes | 0 / 0 / 0 | 0 / 0 |
| p14 | 14 / 29 | 3466 | 137 | yes | 0 / 0 / 0 | 0 / 0 |
| p15 | 15 / 30 | 3603 | 159 | yes | 0 / 0 / 0 | 0 / 0 |
| p16 | 16 / 31 | 3762 | 267 | yes | 0 / 0 / 0 | 0 / 0 |
| p17 | 17 / 32 | 4029 | 273 | yes | 0 / 0 / 0 | 0 / 0 |
| p18 | 18 / 33 | 4302 | 260 | yes | 0 / 0 / 0 | 0 / 0 |
| p19 | 19 / 34 | 4562 | 271 | yes | 0 / 0 / 0 | 0 / 0 |
| p20 | 20 / 35 | 4833 | 269 | yes | 0 / 0 / 0 | 0 / 0 |
| p21 | 21 / 36 | 5102 | 273 | yes | 0 / 0 / 0 | 0 / 1 |
| p22 | 22 / 37 | 5375 | 131 | yes | 0 / 0 / 0 | 0 / 0 |
| p23 | 23 / 38 | 5506 | 213 | yes | 0 / 0 / 0 | 0 / 0 |
| p24 | 24 / 39 | 5719 | 270 | yes | 0 / 0 / 0 | 0 / 0 |
| p25 | 25 / 40 | 5989 | 273 | yes | 0 / 0 / 0 | 0 / 0 |
| p26 | 26 / 41 | 6262 | 265 | yes | 0 / 0 / 0 | 0 / 0 |
| p27 | 27 / 42 | 6527 | 234 | yes | 0 / 0 / 0 | 0 / 0 |
| p28 | 28 / 43 | 6761 | 269 | yes | 0 / 0 / 0 | 0 / 0 |
| p29 | 29 / 44 | 7030 | 277 | yes | 0 / 0 / 0 | 0 / 0 |
| p30 | 30 / 45 | 7307 | 263 | yes | 0 / 0 / 0 | 0 / 0 |
| p31 | 31 / 46 | 7570 | 269 | yes | 0 / 0 / 0 | 0 / 0 |
| p32 | 32 / 47 | 7839 | 121 | yes | 0 / 0 / 0 | 0 / 0 |
| p33 | 33 / 48 | 7960 | 214 | yes | 0 / 0 / 0 | 0 / 0 |
| p34 | 34 / 49 | 8174 | 261 | yes | 0 / 0 / 0 | 0 / 0 |
| p35 | 35 / 50 | 8435 | 271 | yes | 0 / 0 / 0 | 0 / 0 |
| p36 | 36 / 51 | 8706 | 238 | yes | 0 / 0 / 0 | 0 / 0 |
| p37 | 37 / 52 | 8944 | 228 | yes | 0 / 0 / 0 | 1 / 0 |
| p38 | 38 / 53 | 9172 | 228 | yes | 0 / 0 / 0 | 0 / 0 |
| p39 | 39 / 54 | 9400 | 240 | yes | 0 / 0 / 0 | 0 / 0 |
| p40 | 40 / 55 | 9640 | 231 | yes | 0 / 0 / 0 | 0 / 0 |
| p41 | 41 / 56 | 9871 | 273 | yes | 0 / 0 / 0 | 0 / 1 |
| p42 | 42 / 57 | 10144 | 272 | yes | 0 / 0 / 0 | 0 / 0 |
| p43 | 43 / 58 | 10416 | 274 | yes | 0 / 0 / 0 | 0 / 0 |
| p44 | 44 / 59 | 10690 | 273 | yes | 0 / 0 / 0 | 0 / 0 |
| p45 | 45 / 60 | 10963 | 270 | yes | 0 / 0 / 0 | 0 / 0 |
| p46 | 46 / 61 | 11233 | 270 | yes | 0 / 0 / 0 | 0 / 0 |
| p47 | 47 / 62 | 11503 | 274 | yes | 0 / 0 / 0 | 0 / 0 |
| p48 | 48 / 63 | 11777 | 271 | yes | 0 / 0 / 0 | 0 / 0 |
| p49 | 49 / 64 | 12048 | 66 | yes | 0 / 0 / 0 | 0 / 0 |
| p50 | 51 / 66 | 12114 | 92 | yes | 0 / 0 / 0 | 0 / 0 |
| p51 | 52 / 67 | 12206 | 263 | yes | 0 / 0 / 0 | 0 / 0 |
| p52 | 53 / 68 | 12469 | 179 | yes | 0 / 0 / 0 | 0 / 0 |
| p53 | 54 / 69 | 12648 | 232 | yes | 0 / 0 / 0 | 0 / 0 |
| p54 | 55 / 70 | 12880 | 76 | yes | 0 / 0 / 0 | 0 / 0 |
| **all** | | | **12,956** | **55 / 55** | **0 / 0 / 0** | **1 / 3** |

The four word-start differences (flat index = 0-based position in the pin's LP2 stream):

| Flat | Page | Pin marks | v2 marks | Effect | Note |
|---|---|---|---|---|---|
| 1110 | p04+164 | none | `'` | v2 splits a word | apostrophe |
| 5138 | p21+36 | none | `'` | v2 splits a word | apostrophe |
| 9035 | p37+91 | `./-` | `/` | v2 joins ᚠᛒ and ᛞᚢᛈ into one 5-rune word | the only v1 to v2 boundary change in LP2 |
| 10089 | p41+218 | none | `'` | v2 splits a word | apostrophe |

- **p37 (flat 9035).** This page has a numbered list. Items 1-5 begin lines with red numerals. Before items 1, 2, 4
  and 5 the previous line ends in a dot group in both the pin and v2. Before item 3 the pin reads `ᚠᛒ./3-ᛞᚢᛈ`; v2 drops
  the dot (`ᚠᛒ/[red]3[/red]ᛞᚢᛈ`). RDP's parser counts neither a line end nor a numeral as a word break, so ᚠᛒ and ᛞᚢᛈ
  become one 5-rune word, as v2's README says ("LP37's removed separator joins rune lengths 2 and 3 into 5"). If the
  list numeral counts as a break, v2 agrees with the pin here. This changes RDP's word-length (WLI) input on that page,
  not any rune.
- **Apostrophes.** v2 has exactly three apostrophes in LP2, at 1110, 5138 and 10089; the pin's source has none. solver 3
  listed apostrophes at 1110, 5138, 8515 and 10089 (scout7 item 4). Three of the four match exactly with 0-based flat
  indices. At 8515 (p35+80) neither v2 nor the pin has any mark, and the pin has no word start there.
- **Quotation marks.** v2 has 13 `"` marks in LP2 (flat 1659, 1677, 5459, 5478, 9715, 9727, 9811, 9869, 10211, 10279,
  10439, 12522, 12592). All 13 sit at pin word starts, so none changes a word boundary.
- **Page 50 boundary.** v2 has the pin's word start at the first rune of our p50, under both rules and in RDP's
  parser. Correction to lane R: lane R reported that aldegonde's A and M lack that word start and end page 49 "without
  the chapter and sentence marks". Both files carry `/&` straight after page 49's last rune (then the base-60 art block
  of the runeless page). Lane R's tokenizer drops every non-rune run that contains letters, so it lost the `&`. The `.`
  is absent in A and M; the word start is not. Lane R's A/M boundary rows (2 starts lacking, lag-5 105/2108) therefore
  hold one tokenizer artifact. Henkman's p50 gap also holds letters and was not rechecked.

Statistics on the v2 LP2 stream (own runes, own word starts; `out_diff_v2.txt`, recounted by fresh code in
`out_xcheck_rdp_parser.txt`):

| Stream | Doublets (within / cross) | Lag-5 hits / n | Rate | z |
|---|---|---|---|---|
| Pin (lpdata) | 86 (63 / 23) | 104 / 2105 | 4.94% | +3.75 |
| v2, RDP's word rule (diff_v2.py) | 86 (63 / 23) | 104 / 2105 | 4.94% | +3.75 |
| v2, loader's word rule (diff_v2.py) | 86 (63 / 23) | 104 / 2105 | 4.94% | +3.75 |
| v2, RDP's own parser (xcheck_rdp_parser.py, fresh counting code) | 86 (63 / 23) | 104 / 2105 | 4.94% | +3.75 |
| RDP's v1 copy (RV1, RDP's rule) | 86 (63 / 23) | 104 / 2105 | 4.94% | +3.75 |

The boundary changes leave lag-5 untouched: the joined word has 5 runes (a lag-5 pair needs 6), and none of the three
apostrophe splits removes a within-word pair at distance 5. The doublet count depends on runes only. Lane R's verdicts
stand for v2.

## 2. Static audit and judgements (PROOF line 1)

Audits (ast only, nothing imported), all written before any RDP code ran (section 9):

- `audit/audit_static.txt`: `setup.py`, `install.py`, `src/rdp/api/__init__.py`, the three per-module setup scripts,
  tutorials 01-02 and three scoring/LP tests. Closure 146 files, 28 sites.
- `audit/audit_static_selftest.txt`: every `.py` under tests/scoring, tests/data/liber_primus, tests/solved_lp and
  tests/_helpers, `tests/conftest.py`, solving/solved_lp/*.py and tutorials 01-02 (101 entry files). Closure 245 files,
  36 sites. This is exactly what the selftest ran.
- A first pass over the whole test tree (623 files, about 260 sites) was dropped as too wide to judge site by site. The
  selftest was narrowed to the scorer and LP tests instead (section 5).

| Kind | Site | Judgement |
|---|---|---|
| process | install.py:75 `_run` (Popen), :93 (taskkill) | unreachable: install.py was never run; dependencies were pip-installed into a venv and the modules built with setup.py |
| write | install.py:288, :296 | unreachable (install.py) |
| network, delete | tools/assets/release_asset_installer.py:200 `download_file` (urlopen), :193/:203/:209/:290 (unlink) | unreachable: this is the LM3/LM4 downloader, called only from install.py |
| process | tools/torch_runtime.py:21, :65 (nvidia-smi, python probe) | unreachable (install.py only) |
| dynamic | src/rdp/__init__.py:14 `import_module('rdp.api')` | acceptable: lazy import of RDP's own package |
| dynamic | src/rdp/backends/xp.py:13 `__import__(cupy / torch)` | acceptable: optional-accelerator probe at import. cupy is absent; torch 2.14.1 (system site-packages) is imported but unused on CPU |
| dynamic | scoring/hamming/backend.py:15, scoring/span_hamming/fast_backend.py:19 | acceptable: import RDP's own extensions, built here from the audited C++ |
| process | core/config/logging_config.py:179, :182, :185, :190 (`git rev-parse`, `git diff --quiet`) | acceptable: read-only git metadata of the port copy for run logs |
| write | logging_config.py:250, :263; io/run_logger.py:86, :126; api/display.py:336; api/run_artifact_manifest.py:102; api/solver_report_export.py:21; solving/solve_output.py:245 | acceptable: JSON run artifacts under RDP's output root, pinned to dl/rdp_port/output (`RDP_OUTPUT_ROOT`); none is on the scoring path |
| write | 11 test helpers (tests/scoring/**: index.json, calibration JSON, joint tables, CSV) | acceptable: test fixtures written under pytest's `--basetemp=pytest_tmp` inside the port |
| delete | solvers/kaeding_periodic_structured.py:523, :565; tests/conftest.py:10 | false positives: `list.remove` and `sys.path.remove` |
| process | tests/scoring/test_scoring_package_import_policy.py:17; tests/solved_lp/test_workbook_pages.py:47 | acceptable: `python -I -c` on an in-tree import probe |
| process | tests/solved_lp/test_workbook_pages.py:59; solving/solved_lp/run_all.py:44 | not run: full_assets-marked (deselected). If run, they execute the in-tree workbook scripts locally |
| dynamic | tests/data/liber_primus/test_lp_solved_workspace.py:31; tests/scoring/test_rune_scorer_v1_optional_ngram_import.py:6 | acceptable: import in-tree modules |
| deserialise (not flagged by the tool) | `np.load(allow_pickle=True)` in scoring/language_model/language_model_prime_runtime.py:137, ecdf_validator.py:110, span_hamming/calibrated_assets.py:152, word_ngrams/in_memory.py:99 | acceptable: all 24 bundled `.npz` (48 object members, 2 per file) and, after the LM-large install, all 96 (192 object members) hold str payloads whose pickles name only numpy's `_reconstruct`, `ndarray` and `dtype`. Checked with a restricted unpickler (`audit/npz_dtypes.py` -> `npz_dtypes.txt`, `npz_dtypes_lm_large.txt`) |
| C++ (outside the tool) | language_model/fastlm.cpp; hamming/*.cpp, *.h; span_hamming/FastSpanHamming.h; ngram_hamming/FastNgramHamming.h | acceptable: no file, process, network, environment or Python-eval calls (grep); pure compute over numpy buffers |

The `.bin.zst` tables are parsed by `struct` and `np.frombuffer` only (language_model_prime.py:95-110): no code path
from data.

## 3. Port (steps 2-4)

    bash agents/laneAB_rdp_port/setup_port.sh               # dl/rdp -> dl/rdp_port (+ dl/rdp_venv if missing)
    cmd //c agents\\laneAB_rdp_port\\build_native.bat        # MSVC build of the three modules in place

- `setup_port.sh` refuses a clone that is not at 61bf2c78 or does not match `audit/clone_manifest.sha256` (1,018 files).
  It copies the clone and applies `port.patch` (empty: no source change was needed). It creates `dl/rdp_venv` (system
  site-packages visible) from `requirements_port.txt`: zstandard 0.25.0, tzdata 2026.5, platformdirs 4.13.0,
  pybind11 3.1.0, jsonschema 4.26.0, setuptools 84.0.0, wheel 0.48.0. From the system: numpy 2.5.3, pytest 9.1.1,
  torch 2.14.1.
- `build_native.bat` loads `vcvars64.bat` (Build Tools 18) and runs RDP's own `setup.py -q build_ext --inplace`, which
  uses `/O2 /EHsc /std:c++20 /DNDEBUG`. Output: `_fastlm` (235,520 bytes), `_hamming` (221,184) and
  `_span_hamming_fast` (283,136) `.cp313-win_amd64.pyd`. The only diagnostic is D9025 (`/std:c++latest` overridden by
  `/std:c++20`). The forum's WSL/gcc report does not apply here.
- `run_bn.ps1` runs RDP at BelowNormal with `RDP_OUTPUT_ROOT=dl/rdp_port/output`, `PYTHONPATH=dl/rdp_port/src` and
  `PYTHONUTF8=1`.
- **Rebuild check (PROOF line 4).** `PORT_DIR=dl/rdp_check bash setup_port.sh` plus `build_native.bat dl\rdp_check`
  gives a tree identical to dl/rdp_port, excluding `.git`, `build/`, run outputs and `__pycache__` (`diff -rq`). The
  `.pyd` files have identical sizes and differ in exactly 4 bytes each: the PE link timestamp (offset 272) and its copy
  in the debug directory. `git -C dl/rdp_port status` shows no tracked change against v1.0.0. The check copy was then
  deleted.

## 4. Compiled kernel against a Python reference (PROOF line 5)

    dl/rdp_venv/Scripts/python.exe -I agents/laneAB_rdp_port/ref_fastlm.py > agents/laneAB_rdp_port/out_ref_fastlm.txt

`ref_fastlm.py` re-implements `fastlm.cpp` from its source and the file format only (no RDP import in the reference):
the table parse, auto Good-Turing smoothing (alpha = N1/(K-N1), else 0.5), the minimum-seen OOV floor, XXH64 seed 0
over the packed tokens (rune | pos<<5 | len<<11), linear probing, and the sum of joint n-gram log-probabilities. It
passes the XXH64 empty-string test vector. The scores are compared with RDP's `LanguageModelPrime` over the compiled
kernel on 24 texts per table (half uniform random with random word lengths, half Moby-Dick windows with their own
words, 30-300 runes):

| Table | Seen n-grams K | Total count T | Max abs diff | Max rel diff |
|---|---|---|---|---|
| ltr char 1 | 29 | 1.45e13 | 8.9e-4 | 8.1e-7 |
| ltr char 2 | 837 | 1.33e13 | 6.9e-4 | 4.7e-7 |
| ltr wli 1 | 2,889 | 1.45e13 | 6.4e-4 | 5.1e-7 |
| ltr wli 2 | 117,629 | 1.33e13 | 4.4e-3 | 1.2e-6 |
| rtl char 1 | 29 | 1.53e13 | 8.9e-4 | 1.0e-6 |
| rtl char 2 | 833 | 1.41e13 | 1.0e-3 | 5.2e-7 |
| rtl wli 1 | 3,336 | 1.53e13 | 1.4e-3 | 7.3e-7 |
| rtl wli 2 | 128,360 | 1.41e13 | 5.2e-3 | 9.0e-7 |

Verdict PASS, largest relative difference 1.2e-6. The differences are the kernel's float32 accumulation over sums of
-200 to -4,000 nats. The auto-GT alpha is 0.5 for every bundled table. Each table was pruned (smallest stored count 40-46
for n = 2, about 8.4e8 for n = 1), so N1 = 0 and the fallback alpha applies. Unseen n-grams get the minimum seen logp.

Orders 3 and 4 (after the LM-large install; `ref_fastlm.py --orders 3,4` -> `out_ref_fastlm_lm_large.txt`; the reference
now reads tables through numpy views, and reproduces the order-1/2 output above byte for byte):

| Table | Seen n-grams K | Max abs diff | Max rel diff |
|---|---|---|---|
| ltr char 3 | 21,609 | 9.7e-4 | 4.7e-7 |
| ltr char 4 | 351,808 | 9.1e-3 | 1.5e-6 |
| ltr wli 3 | 1,733,806 | 1.4e-2 | 2.0e-6 |
| ltr wli 4 | 12,497,503 | 1.5e-2 | 2.3e-6 |
| rtl char 3 | 19,501 | 2.8e-3 | 5.9e-7 |
| rtl char 4 | 295,172 | 6.8e-3 | 1.1e-6 |
| rtl wli 3 | 1,757,175 | 2.1e-2 | 3.2e-6 |
| rtl wli 4 | 12,247,114 | 1.4e-2 | 1.8e-6 |

Verdict PASS, largest relative difference 3.2e-6 (alpha 0.5 again on every table).

## 5. Upstream selftest on the port (PROOF line 6)

    $env:PYTEST_ADDOPTS='-m "not full_assets"'; powershell -NoProfile -File agents/laneAB_rdp_port/run_bn.ps1 -Log agents/laneAB_rdp_port/logs/selftest_pytest.log -Cwd dl/rdp_port -Exe dl/rdp_venv/Scripts/python.exe -ArgLine '-m pytest -q -p no:cacheprovider --basetemp=pytest_tmp tests/scoring tests/data/liber_primus tests/solved_lp'

- RDP's CI-light selection (`-m "not full_assets"`, as its `rdp_v1_full_ci.yml`), limited to the scorer, LP-data and
  solved-page tests: **395 passed, 8 skipped (CUDA not available), 15 deselected (full_assets: need LM3/LM4), in 114 s**
  (`logs/selftest_pytest.log`).
- `python -m tutorials.v1.getting_started.01_known_key`: the known-key round trip of FOLLOW THE EVIDENCE under key
  (3, 1, 4) recovers the plaintext. `02_first_search`: recovered key (7,), exact recovery True
  (`logs/selftest_tutorial_*.log`).
- **full_assets tests** (after the LM-large install; `PYTEST_ADDOPTS='-m full_assets'`, same three directories):
  **15 passed, 403 deselected, in 122 s** (`logs/selftest_pytest_full_assets.log`). They include the raw-table integrity
  and ECDF monotonicity checks over the full asset set, the NumPy golden vectors `avg20_char4_fulltext` and
  `pct10_char2`, Torch-vs-NumPy parity at lengths 4-240 (CPU), and `test_run_all_workbook_solves_require_solved_status`.
  That test runs `solving/solved_lp/run_all.py` and requires `solves_passed: 9`, so RDP re-solves all nine solved LP
  pages on this port.
- Not run: the rest of RDP's test tree (solver, API, packaging and workflow contracts; about 620 files whose audit was
  not judged) and the torch-on-CUDA tests.

## 6. The wrapper and our planted control (PROOF lines 7-8)

`rdp_scorer.py` makes RDP's scorer callable from our controls under the system Python with `-I`. It puts the port's
`src` first on sys.path and appends the venv's site-packages:

    import sys; sys.path.insert(0, "agents/laneAB_rdp_port"); import rdp_scorer as RS
    RS.RDPScorer().score_many(seqs, words)          # RDP default: char + WLI lanes, order 2, percentile log-prob, window 10
    RS.RDPScorer(wli=False, objective='avg_logp')   # char lane, average log-probability
    RS.RDPScorer(wli=False, char_order=4, objective='avg_logp')   # LM4 char lane (LM-large assets, installed)
    RS.char_logp(seq, n=2)                          # raw mean joint log-prob per n-gram (nats)

- **Order selection (bug found and fixed).** RDP uses `character_ngram_order` / `wli_ngram_order` only when
  `base_lane_weights` is set. With no order-weight map, `ScoringConfig.effective_lm_model_weights` falls back to
  `{2: 0.5}` per lane, so the first `--lm4` run scored its "order-4" scorers at order 2. Their true-key scores equalled
  the order-2 ones on all 80 plants per tier, with no error or warning. The wrapper now passes `{order: 1.0}` per enabled
  lane and refuses to build if RDP's effective models differ from the request. For order 2 this gives the same
  normalised weights as RDP's default: the recorded order-2 scores reproduce with 0 difference. The 160 invalid rows
  were deleted; their logs are kept as `logs/plants_lm4_*_INVALID_order2.log`.
- Our rune indices are RDP's (both use the Gematria Primus order; RDP's index 11 J accepts ᛄ and ᛂ). Word ids per rune
  (lpdata `word`, `runes.english_stream` W) become RDP's WLI `[position in word, word length]`.
- Score path: RDP's `build_scorer` + `batch_score`, grouped by length exactly as `rdp.api.score_many`. The scorer is
  built once per RDPScorer, as an RDP run does, while `api.score_many` rebuilds it on every call.
  `check_against_api()` runs at the start of every control run: **max |diff| = 0** against `api.score_many`.
- Scale: English 250-rune windows score 0.43-0.57 under the default and random runes 0.001-0.003. `char_logp` gives
  -5.6 for English and -9.8 for random (natural log per bigram).
- Cost: import 4.4 s; a batch of 29 candidates of 260 runes takes 0.27 s (default), 0.14 s (char, percentile) or 0.056 s
  (char, average log-prob); 2,000 char-only candidates take 2.56 s in one batch. Profiling shows the overhead in RDP's
  per-candidate input validation (`RuneInput` WLI checks) and an ECDF path `resolve()` per batch, not in the kernel.
  Peak working set of one control process: 231 MB at order 2, and 1,700 MB once an order-4 WLI lane is loaded
  (char-only order 4 stays small: the char 4-gram table is 20 MB).

**Control** (`plant_control.py`; plants seeded independently of RDP). Each plant is a window of solved LP1 plaintext
(`dl/dukotah/liber-primus/SOLVED-PAGES.json`, 1,769 runes, no word boundaries, so char lane only) or of Moby-Dick with
word ids (`toolbox/runes.english_stream`). It is enciphered as c = p + k[i mod period] (mod 29) under a random key. The
search is the same for every scorer: coordinate ascent, 29 candidates per key position per round, at most 8 rounds,
3 random restarts, best final score kept. Recovered = exact key. A miss is labelled "search" when the true key scores at
least as high as the found key, and "scorer" otherwise.

    python -I agents/laneAB_rdp_port/plant_control.py               # easy tier: 260 runes, periods 2-9
    python -I agents/laneAB_rdp_port/plant_control.py --tier hard   # 100 runes, periods 6-12

Easy tier (`out_plants.jsonl`, `logs/plants_full.log`):

| Scorer | Recovered k/n (LP1 solved, English) | Misses | s/plant | Evals/s |
|---|---|---|---|---|
| rdp_default (char + WLI, n=2, pct log-prob w10) | 20/20 (-, 20/20) | none | 10.9 | 112 |
| rdp_char_pct (char, n=2, pct log-prob w10) | 40/40 (20/20, 20/20) | none | 1.9 | 772 |
| rdp_char_avg (char, n=2, average log-prob) | 40/40 (20/20, 20/20) | none | 0.6 | 1,496 |
| ours_quad (toolbox/score.quadgram) | 40/40 (20/20, 20/20) | none | 0.1 | 11,837 |

Hard tier (`out_plants_hard.jsonl`, `logs/plants_hard.log`; 100 runes, periods 6-12, so 8-17 runes per key position):

| Scorer | Recovered k/n (LP1 solved, English) | Search misses | Scorer misses | s/plant | Evals/s |
|---|---|---|---|---|---|
| rdp_default | 15/20 (-, 15/20) | 5 | 0 | 8.9 | 361 |
| rdp_char_pct | 24/40 (11/20, 13/20) | 16 | 0 | 5.4 | 642 |
| rdp_char_avg | **35/40** (17/20, 18/20) | 2 | 3 | 1.3 | 1,952 |
| ours_quad | 16/40 (9/20, 7/20) | 24 | 0 | 0.1 | 26,718 |

Misses (plant(period, kind)):
- rdp_default: eng01(p10,search) eng07(p8,search) eng12(p8,search) eng16(p10,search) eng17(p10,search).
- rdp_char_pct: eng00(p12) eng08(p7) eng11(p8) eng15(p11) eng16(p10) eng17(p10) eng19(p11) lp100(p10) lp101(p7)
  lp109(p12) lp110(p10) lp112(p8) lp113(p10) lp114(p9) lp117(p10) lp119(p10), all search.
- rdp_char_avg: eng16(p10,search) lp113(p10,search); scorer misses eng17(p10), lp109(p12), lp117(p10).
- ours_quad: eng00(p12) eng01(p10) eng02(p8) eng03(p6) eng04(p7) eng06(p8) eng08(p7) eng13(p12) eng14(p12) eng15(p11)
  eng16(p10) eng17(p10) eng19(p11) lp101(p7) lp104(p7) lp106(p11) lp108(p8) lp109(p12) lp110(p10) lp113(p10) lp116(p8)
  lp117(p10) lp118(p11) lp119(p10), all search.

By period (recovered/plants): rdp_char_avg p6 5/5, p7 4/4, p8 12/12, p9 3/3, p10 4/8, p11 4/4, p12 3/4. ours_quad
p6 4/5, p7 0/4, p8 8/12, p9 3/3, p10 1/8, p11 0/4, p12 0/4.

Reading:
- **For short texts, RDP's character-bigram average log-probability is a much better search fitness than our quadgram
  scorer** (35/40 against 16/40 with the same search and seeds). Every quadgram miss is a search miss: the true key
  outscores the found key, so the quadgram scorer judges correctly. It gives coordinate ascent little gradient,
  because changing one of 6-12 key positions changes few whole quadgrams.
- The percentile objectives (ECDF of window-10 sums, clamped at 1e-6) flatten the landscape while the key is mostly
  wrong, hence 16 and 5 search misses. They judge correctly (0 scorer misses).
- **Step 6 replay** (`replay_misses.py --tier hard`, `logs/replay_misses_hard.log`). The 3 rdp_char_avg scorer misses
  (periods 10-12, 8-10 runes per key position) were rerun with the same keys on 5 fresh windows each, and recovered 1/5
  (lp109, p12), 2/5 (lp117, p10) and 2/5 (eng17, p10). This is the bigram scorer's limit at that length, not a port
  fault: the port matches the reference and `api.score_many` exactly, and the easy tier is 140/140.
- For our controls: use `RDPScorer(wli=False, objective='avg_logp')` as the fitness of a key search on page-length or
  shorter text, and keep `score.quadgram` as a second judge of the final candidates.

Order 4 (LM-large; `plant_control.py --tier easy|hard --lm4`, `logs/plants_lm4_easy.log`, `logs/plants_lm4_hard.log`;
same plants, search and seeds as above):

| Scorer | Easy: k/n (LP1, Eng) | Easy misses | Hard: k/n (LP1, Eng) | Hard misses | Hard s/plant |
|---|---|---|---|---|---|
| rdp_char4_avg (char, n=4, average log-prob) | **40/40** (20/20, 20/20) | none | **39/40** (19/20, 20/20) | lp109(p12) | 1.3 |
| rdp_char4_pct (char, n=4, pct log-prob w10) | 27/40 (11/20, 16/20) | 13 | 8/40 (5/20, 3/20) | 32 | 3.0 |
| rdp_default4 (char + WLI, n=4, pct log-prob w10) | 17/20 (-, 17/20) | 3 | 6/20 (-, 6/20) | 14 | 6.1 |

Every order-4 miss is a search miss: the true key outscores the found key in all 62 cases, so there are no scorer
misses and nothing to replay under step 6. Lists:
- rdp_char4_pct easy: eng00(p7) eng02(p7) eng16(p9) eng17(p8) lp100(p7) lp103(p8) lp105(p7) lp108(p7) lp109(p3)
  lp115(p9) lp116(p7) lp117(p7) lp119(p9).
- rdp_default4 easy: eng02(p7) eng16(p9) eng17(p8).
- rdp_char4_pct hard (32): eng01 eng02 eng04 eng06 eng07 eng08 eng09 eng10 eng11 eng12 eng13 eng14 eng15 eng16 eng17
  eng18 eng19 lp100 lp101 lp103 lp104 lp105 lp106 lp107 lp109 lp110 lp111 lp113 lp116 lp117 lp118 lp119.
- rdp_default4 hard: eng00 eng01 eng02 eng06 eng07 eng09 eng10 eng12 eng13 eng14 eng16 eng17 eng18 eng19.

By period, hard tier, rdp_char4_avg: p6 5/5, p7 4/4, p8 12/12, p9 3/3, p10 8/8, p11 4/4, p12 3/4. The order-2 version's
3 scorer misses (p10-p12) are gone at order 4.

Reading (order 4):
- **RDP's 4-gram average log-probability is the strongest scorer here: 40/40 and 39/40, with no scorer miss.** At 8-17
  runes per key position it both judges correctly and gives the search enough gradient. It costs 1.3 s per hard plant
  (2,232 evals/s).
- Percentile objectives get worse with order: ECDF percentiles of window-10 sums sit at the clamp while most of the key
  is wrong, and at order 4 almost every window does. They still judge correctly, so they suit ranking finished
  candidates, not driving a search.
- For our controls: `RDPScorer(wli=False, char_order=4, objective='avg_logp')` as the key-search fitness (or
  `char_order=2` where the LM-large files are absent), with `score.quadgram` and RDP's percentile score as second judges
  of the final candidates.

**Smoke run and resume (PROOF line 8).** `--limit 1 --scorers rdp_default` finished one task (eng00, period 7,
recovered, 2,033 evaluations, 23.1 s through `api.score_many` before the reusable scorer was added;
`logs/smoke_plants_1.log`). The rerun printed `skip rdp_default eng00 (already in out_plants.jsonl)` and ran eng01
(period 4, recovered, 8.5 s; `logs/smoke_plants_2_resume.log`). Memory per worker: peak working set 231 MB for the full
easy-tier process (one worker; the control is single-process).

## 7. Deviations from upstream

| Deviation | Reason |
|---|---|
| Python 3.13.15 (upstream tests 3.11) | the PC's Python; RDP requires >= 3.11 and its selftest passes |
| Not installed: RDP runs from `dl/rdp_port/src` via PYTHONPATH or sys.path | no pip install of community code; `install.py` (pip install, downloader, CUDA probe) never ran |
| Dependencies in `dl/rdp_venv` with system site-packages; versions in `requirements_port.txt` | the system Python lacked zstandard, tzdata, platformdirs and pybind11 |
| Native build via `setup.py build_ext --inplace` in an MSVC environment | RDP's normal route is `install.py`; the flags are RDP's own |
| `RDP_OUTPUT_ROOT` pinned to `dl/rdp_port/output`; pytest `--basetemp=pytest_tmp` | keep every write inside the port copy |
| Selftest limited to tests/scoring, tests/data/liber_primus, tests/solved_lp and tutorials 01-02 | audited closure; the rest of the tree is not scorer code |
| LM-large installed by our `install_lm_large.py` from curl downloads, not by RDP's installer | keep RDP's network code unused; every file checked against the pinned manifest |
| The archive's CRLF `index.json` not installed; the bundled LF copy kept | the bundled copy matches the manifest sha256; same JSON |
| Wrapper passes explicit order-weight maps | RDP ignores `*_ngram_order` without `base_lane_weights` (section 6) |
| Wrapper keeps one scorer object per configuration | RDP's run path does the same; equality with `api.score_many` is asserted (0 difference) |
| Control texts: our SOLVED-PAGES.json transliteration and Moby-Dick, not RDP's solved_plaintext | plants independent of RDP's data |

## 8. LM3/LM4: fetched, verified and installed (owner's yes, 2026-10-19)

    curl -L --fail -o dl/rdp_downloads/rdp-v1-lm-large-part00N.zip https://github.com/mortlach/rdp_assets/releases/download/rdp-v1.0.0-lm-large/rdp-v1-lm-large-part00N.zip   # N = 1, 2
    python -I agents/laneAB_rdp_port/install_lm_large.py > agents/laneAB_rdp_port/out_install_lm_large.txt
    python -I agents/laneAB_rdp_port/audit/npz_dtypes.py dl/rdp_port/assets > agents/laneAB_rdp_port/audit/npz_dtypes_lm_large.txt

- Payload: `mortlach/rdp_assets` release `rdp-v1.0.0-lm-large`, the URLs pinned in RDP's
  `assets/manifests/assets_manifest_v1.json`. `part001.zip` = 526,399,103 bytes, sha256 `fbd18104...bd09543`;
  `part002.zip` = 373,232,816 bytes, sha256 `ddbecc1d...6ae434`. Both equal the manifest. Fetched by curl (RDP's
  downloader was not used), stored in `dl/rdp_downloads/` (git-ignored).
- `install_lm_large.py` (ours, no network code) admits only safe relative member paths that are manifest
  `final_relpath`s. It streams each member to a temporary file, checks size and sha256, and only then moves it into
  `dl/rdp_port/assets/`. The archives hold 129 members: **96 extracted** and 33 already present and matching (the
  source-bundled LM1/LM2 files), **0 problems**. Afterwards **129 of 129** manifest rows required for
  `v1_lm_runtime_full` are on disk with the manifest size and sha256. The language-model tree is now 859 MB; 267 GB
  disk remain.
- One note: the archive's `language_model/lmp/index.json` is 647 bytes against the manifest's 627. It is the same file
  with CRLF line endings (identical after CRLF -> LF; same JSON). The bundled LF copy matches the manifest and was kept.
- Pickle check on the new `.npz` (`audit/npz_dtypes_lm_large.txt`): 96 files, 192 object members, every one a str
  payload whose pickle names only numpy's `_reconstruct`, `ndarray` and `dtype`. The `allow_pickle=True` judgement in
  section 2 holds for the full asset set.
- Table sizes (decompressed): char n3 1 MB, char n4 10-20 MB, WLI n3 80 MB, WLI n4 640 MB (2^25 slots, 12.2-12.5 M
  seen 4-grams). RDP copies the arrays, so an order-4 WLI lane costs about 1.3 GB of RAM per table.

## 9. PROOF (jobs/port-community-code/PROOF.md)

| Line | Result |
|---|---|
| audit saved; every risky site judged | PASS: `audit/audit_static.txt`, `audit/audit_static_selftest.txt`, `audit/npz_dtypes.txt`; section 2 |
| nothing ran before the audit | PASS: audit_static.txt 18:54:19 is older than the first RDP code run (setup.py build, 18:57:47); audit_static_selftest.txt 19:00:43 is older than the selftest (19:01:59). diff_v2.py reads data files only |
| clone unchanged | PASS: `git -C dl/rdp status --porcelain` is empty; setup_port.sh verifies the 1,018-file manifest |
| patch + setup rebuild an identical copy | PASS: section 3 (empty patch; only .git stat cache and PE timestamps differ) |
| compiled kernel = Python reference | PASS: orders 1-2 max relative 1.2e-6; orders 3-4 max relative 3.2e-6 (section 4) |
| upstream selftest passes | PASS: 395 passed, 8 skipped (CUDA); full_assets 15 passed; tutorials 01-02 OK (section 5) |
| independent planted control, n >= 20, misses listed | PASS: section 6 |
| one-task smoke run, time and memory, rerun skips | PASS: section 6 |
| every deviation listed | PASS: section 7 |
| fixture reproduces `aldegonde_dodge_audit.txt` | PASS after a fix: audit_static.py crashed with UnicodeEncodeError (cp1252) when its output was redirected and the tree had runic source lines. It now writes UTF-8 to stdout (CHANGELOG 2026-10-19) |

## Files

`diff_v2.py`, `out_diff_v2.txt`, `per_page_v2.tsv` (step 1); `xcheck_rdp_parser.py`, `out_xcheck_rdp_parser.txt`
(RDP's parser and fresh counts); `audit/` (static audits, npz check, clone manifest); `setup_port.sh`, `port.patch`
(empty), `requirements_port.txt`, `build_native.bat`, `run_bn.ps1` (port); `ref_fastlm.py`, `out_ref_fastlm.txt`
(kernel check); `rdp_scorer.py` (wrapper); `plant_control.py`, `out_plants.jsonl`, `out_plants_hard.jsonl` (control);
`replay_misses.py` (step-6 replay); `install_lm_large.py`, `out_install_lm_large.txt`, `out_ref_fastlm_lm_large.txt`
(LM-large); `logs/` (build, selftest, full_assets tests, tutorials, smoke, resume, control runs, replay; absolute paths
replaced by `<repo>` and `<python>`). Not committed: `dl/rdp` (clone), `dl/rdp_port` (with the installed LM-large
files), `dl/rdp_venv`, `dl/rdp_downloads` (the two archives).

No LP2 decryption and no lead: this lane checks a transcription and ports a scorer.
