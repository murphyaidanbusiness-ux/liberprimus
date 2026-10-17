# PROOF: technique-survey

Run on the survey file you are about to return (in `runs/`). Every line pass or fail. Fix every fail first.

## Output (checked by `python jobs/technique-survey/tools/check_survey.py <file>`)
- [ ] File is `runs/YYYY-MM-DD-<topic>.md` with today's date
- [ ] At least 12 technique entries, each a `### T:` block with all six fields: Source, Exploits, LP2 constraints, Prior coverage, Verdict, Test design
- [ ] Every entry's `LP2 constraints` line names at least one of C1-C6 (from `toolbox/CONSTRAINTS.md`)
- [ ] Every Verdict is one of `applicable-untested`, `applicable-tested`, `not-applicable`
- [ ] Every `applicable-untested` entry has a Test design with a planted control and a null
- [ ] Every URL cited in an entry appears in the `## Sources opened` list, and every entry cites a URL or a book with page/chapter
- [ ] A `## Top 5` section ranks five entry names that exist in the file, all `applicable-untested`
- [ ] Every `applicable-tested` entry names the lane (A-R) or ledger file that tested it

## By reading (two people would agree)
- [ ] No source is leaked or classified material; agency sources are official public releases (nsa.gov, cia.gov, archives of declassified documents, published books)
- [ ] Each `not-applicable` verdict quotes the constraint that kills it, with the number

## Fixture
- [ ] `python jobs/technique-survey/tools/check_survey.py jobs/technique-survey/data/fixture/sample.md --min 2` prints PASS, and
      `... data/fixture/bad.md --min 2` prints FAIL with the reasons listed in `data/fixture/expected.md`
