# Expected checker output on the fixtures

`check_survey.py data/fixture/sample.md --min 2` -> `PASS (2 entries)`

`check_survey.py data/fixture/bad.md --min 2` -> `FAIL`, with exactly these reasons:
- Frequency analysis: LP2 constraints line names none of C1-C6
- Frequency analysis: verdict 'maybe' not one of [...]
- Frequency analysis: cites https://example.org/frequency, which is not in Sources opened
- Hill climbing on n-grams: applicable-untested but Test design lacks a planted control and a null
- Hill climbing on n-grams: Source has neither a URL nor a book page/chapter
- Top 5 item 'Frequency analysis' is not applicable-untested
