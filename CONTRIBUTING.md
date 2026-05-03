# Contributing

1. Fork and clone the repo
2. `python -m venv .venv && source .venv/bin/activate`
3. `pip install -e ".[dev]"`  (tests run without pdfplumber)
4. `pip install -e ".[full]"` (for real PDF testing)
5. Make changes, add tests, run `pytest`
6. Open a pull request

## Good first issues

- Add `--merge-headers` flag to combine multi-row headers into one
- Add Excel (`.xlsx`) export format using `openpyxl` (optional dependency)
- Add `--min-rows N` flag to skip tables with fewer than N rows
- Improve header detection heuristic for tables without clear header rows
