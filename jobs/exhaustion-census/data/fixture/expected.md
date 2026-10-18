# Expected output of check_census.py on bad.md --min 3 (exit 1)

FAIL
  - onion or gateway URL: http://abcdefghijklmnop.onion.to/x
  - FX-01: control 'yes' not y/n/unclear
  - FX-02: strength 'E' not A/B/C/D
  - FX-02: source is neither a URL nor an existing local path
  - FX-02: constraint cell must start 'dead C<n>', 'consistent' or 'unclear'
  - FX-03: 8 cells, need 10
  - reopen candidate FX-04 has strength A (only C or D reopen)
