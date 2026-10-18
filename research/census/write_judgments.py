"""The orchestrator's judging pass (2026-10-18, claude-opus-5-5): one verdict for every census row.

Writes research/census/judgments.tsv: id, verdict, bucket, constraint (when re-graded), strength (when re-graded), note.
Every row of every part was read and judged; a row with no entry here makes merge.py fail.

    python research/census/write_judgments.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from merge import PARTS, rows_of  # noqa: E402

TRANSPOSE = ("dead C1: a pure rearrangement keeps English unigram statistics (IoC about 1.78; LP2 1.000); as a layer "
             "after the cipher it would also scramble the adjacency deficit (C2)")
DIGRAPH = ("dead C1: a fixed digraphic table leaves non-flat unigrams (bifid and Polybius measured at IoC 1.39-1.55, "
           "DK-37); LP2 1.000")
WORDLEN = "dead C4: LP2's word lengths have no sequential structure, so an exact word-length run is not plaintext evidence"

# Re-graded constraint cells: the agent wrote `unclear` or `consistent` where a quick exclusion applies.
REGRADE = {
    "WB-01": "dead C2: an additive periodic key at any period, independent of the ciphertext, predicts about 3.4% doublets (LP2 0.66%)",
    "WB-02": "dead C2: raw sequence keys predict about 3.4% doublets; the chain form with steps 1..28 predicts 0 (LP2 86)",
    "WB-03": "dead C2: unfiltered autokeys give 3.3-4.2% doublets (DK-15), and a fixed feedback table is excluded by C2b",
    "WB-04": "dead C2b: a fixed prime feedback table is a fixed feedback table (LZ-07); conditional IoC 1.026 is flat",
    "WB-07": DIGRAPH, "LZ-03": DIGRAPH,
    "WB-16": "dead C1: rune 0 is flat (458 against 447 expected); F-passthrough would add about 190",
    "WB-17": TRANSPOSE, "WB-18": TRANSPOSE, "WB-19": TRANSPOSE, "WB-20": TRANSPOSE, "WB-22": TRANSPOSE,
    "WB-24": TRANSPOSE, "WB-28": TRANSPOSE,
    "WB-21": ("dead C1/C2 under either reading: a reading-direction rule is a rearrangement (C1); a number-driven shift "
              "direction is an additive key independent of the ciphertext (C2)"),
    "WB-29": "dead C4: line breaks are a glyph-width fill, so line-initial runes carry no plaintext layout",
    "WB-41": "dead C3: a small per-word state forces hundreds of repeated cipher words (LP2 has 16)",
    "AL-26": "dead C1: keyword Vigenere, Beaufort and Atbash families are periodic keys of 1500 or less (F-interrupts dead by WB-16)",
    "TE-01": WORDLEN, "TX-11": WORDLEN,
    "TE-03": "dead C2 as an additive key; its use as a grid for the walk's g is AL-15",
    "DK-21": "dead C1: an operation on the cipher stream alone (decimation, interleave) keeps LP2's flat IoC, so it cannot read as English",
    "DK-38": "dead C2: a no-repeat premise predicts 0 doublets (LP2 86)",
    "DK-59": "dead C2: a Smirnov rewrite (no adjacent repeat) predicts 0 doublets (LP2 86)",
    "AX-07": ("dead C2: a keystream independent of the ciphertext on the chain's step gives step 0 at about 1/29 "
              "(additive) or at rune 0's frequency (multiplicative), against LP2's 0.66%"),
    "AX-14": "dead C2: a fixed-key block cipher emits adjacent repeats at about 1/29 unless a preventer is added; LP2 0.66%",
}
RESTRENGTH = {
    "AL-15": ("B", "154,096,488 keys is the whole pool (190,008 g x 812 sigma); C only because base_0 is hill-climbed"),
}
BUCKET = {
    "full": "AL-14 AL-15 AL-17 AL-29 LZ-05 DK-09 DK-16 AX-01 AX-02 AX-03 AX-15 AX-24 AX-25 AX-43 AX-46 AX-65",
    "test": "DK-15 AL-25 AL-31 AX-16 AX-27",
    "probe": ("WB-14 AL-18 AX-08 AX-09 AX-17 AX-19 AX-26 AX-31 AX-32 AX-37 AX-39 AX-44 AX-45 AX-47 AX-59 AX-60 AX-62 "
              "AX-63 AX-64 AX-66"),
    "open": ("DK-01 DK-02 DK-03 DK-04 DK-05 DK-06 DK-07 DK-08 DK-10 DK-11 DK-12 DK-13 DK-24 DK-25 DK-26 DK-57 DK-58 "
             "WB-26 WB-27 AX-04 AX-58"),
    "off": ("WB-25 WB-31 WB-33 WB-36 WB-38 WB-43 LZ-11 LZ-12 TE-04 TE-05 DK-22 DK-27 DK-28 DK-29 DK-30 DK-31 DK-32 "
            "DK-40 DK-41 DK-42 DK-43 DK-44 DK-45 DK-46 DK-47 DK-49 DK-50 DK-51 DK-52 DK-53 DK-54 DK-55 DK-56 DK-60"),
    "partial": "AL-27 AX-20 AX-29 AX-36 AX-53 DK-17",
}
NOTE = {
    "DK-15": "refuted by the iteration-9 diagonal test (z -17.25)",
    "AL-25": "a fixed restart makes the seam bimodal (doublets at every boundary or none); LP2's seam/d1w ratio is 1.25",
    "AL-31": "11 word-initial doublets where the hold predicts about 0",
    "AX-16": "same positional-profile refutation as AL-31",
    "AX-27": "one doublet across the page 50 boundary excludes a page reset",
    "AX-42": "C5 is a soft constraint (about 2.5 sigma), so this exclusion is weaker than the hard ones",
    "DK-09": "the exact keyskip1 relation (S2) stopped at 44.14%; finishing it is a finite job",
    "AL-27": "the clock-form dodge; no working scorer (lane W, 0/20)",
    "AX-29": "keyword-grid g; overlaps lane L's keyword corner",
    "AX-53": "keyword-filled 5x5 squares; same construction family as AX-29",
    "AX-36": "one simulation only; a gate run would settle it cheaply",
    "AX-20": "random draws only; a global search is infeasible for the walk (lane K)",
    "DK-17": "the unfiltered forms are dead (AL-32, AL-05, LZ-06); the skip-filtered forms were never counted",
    "DK-22": "readings of number channels, not a key search",
}
for i in ("01", "02", "03", "04", "05", "06", "07", "08", "10", "11", "12", "13", "24", "25", "26", "57"):
    NOTE.setdefault("DK-" + i, "consistent only as a filtered keystream; a word-blind stream does not explain the "
                               "within-word lag-5 echo (C5, soft; AX-59)")


def main():
    rows = []
    for name in PARTS:
        if (HERE / name).exists():
            rows += rows_of(HERE / name)
    ids = {r["id"] for r in rows}
    where = {}
    for b, s in BUCKET.items():
        for rid in s.split():
            assert rid in ids, "judgment for a row that does not exist: " + rid
            assert rid not in where, "row in two buckets: " + rid
            where[rid] = b
    for rid in list(REGRADE) + list(RESTRENGTH) + list(NOTE):
        assert rid in ids, "judgment for a row that does not exist: " + rid
    out = ["id\tverdict\tbucket\tconstraint\tstrength\tnote"]
    for r in rows:
        con = REGRADE.get(r["id"], "")
        dead = (con or r["constraint"]).startswith("dead")
        bucket = where.get(r["id"], "dead" if dead else None)
        assert bucket, "row not judged: %s (%s)" % (r["id"], r["constraint"][:60])
        assert not (dead and r["id"] in where), "dead row also bucketed: " + r["id"]
        st, st_note = RESTRENGTH.get(r["id"], ("", ""))
        verdict = "regrade" if (con or st) else "agree"
        note = "; ".join(x for x in (NOTE.get(r["id"], ""), st_note) if x)
        out.append("\t".join([r["id"], verdict, bucket, con, st, note]))
    (HERE / "judgments.tsv").write_text("\n".join(out) + "\n", encoding="utf-8")
    n = len(out) - 1
    print("%d rows judged: %d agree, %d re-graded" % (n, sum("\tagree\t" in l for l in out), sum("\tregrade\t" in l for l in out)))


if __name__ == "__main__":
    main()
