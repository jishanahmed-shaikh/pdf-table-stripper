<div align="center">

# pdf-table-stripper

**Extract tables from messy PDFs into clean CSVs. Built for financial and accounting data.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![pdfplumber](https://img.shields.io/badge/Powered%20by-pdfplumber-orange?style=flat)](https://github.com/jsvine/pdfplumber)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat)](CONTRIBUTING.md)
[![CI](https://github.com/jishanahmed-shaikh/pdf-table-stripper/actions/workflows/ci.yml/badge.svg)](https://github.com/jishanahmed-shaikh/pdf-table-stripper/actions)

</div>

---

## Why this exists

Bank statements, invoices, and financial reports come as PDFs. The data you need is locked in tables. Copy-pasting into Excel is error-prone and slow. `pdf-table-stripper` detects every table in a PDF, cleans the cells, detects header rows, and writes each table to a separate CSV — ready for pandas, Excel, or any data pipeline.

---

## Install

```bash
# With PDF extraction support (recommended)
pip install "pdf-table-stripper[pdf]"

# Base only (use --mock for testing without pdfplumber)
pip install pdf-table-stripper
```

Requires [pdfplumber](https://github.com/jsvine/pdfplumber) for real PDF extraction.

---

## Quick start

```bash
# Extract all tables from a PDF
pdfstrip statement.pdf

# Extract to a specific directory
pdfstrip statement.pdf --output ./csv_output

# Extract only pages 1 and 3
pdfstrip statement.pdf --pages 1 3

# Write all tables to a single CSV
pdfstrip statement.pdf --single-file

# Output as JSON
pdfstrip statement.pdf --format json

# Scan — list tables without writing output
pdfstrip statement.pdf --scan

# Test without a PDF (uses built-in bank statement sample)
pdfstrip --mock
```

---

## Example output

```
  pdf-table-stripper — statement.pdf
  Found 3 table(s):
    Page 1, Table 1: 9 rows x 5 cols
    Page 1, Table 2: 7 rows x 2 cols
    Page 2, Table 1: 3 rows x 3 cols

  Written: ./output/statement_page1_table1.csv
  Written: ./output/statement_page1_table2.csv
  Written: ./output/statement_page2_table1.csv
```

`statement_page1_table1.csv`:
```
Date,Description,Debit,Credit,Balance
03/04/2026,NEFT - Salary,,50000.00,60000.00
05/04/2026,Amazon Purchase,2499.00,,57501.00
07/04/2026,Electricity Bill,1200.00,,56301.00
```

---

## All flags

| Flag | Description |
|------|-------------|
| `pdf` | Path to the PDF file |
| `--output DIR` | Output directory (default: `./output`) |
| `--pages N...` | Page numbers to extract (default: all) |
| `--single-file` | Write all tables to one CSV |
| `--output-file FILE` | Filename for single-file output |
| `--format` | `csv` or `json` (default: `csv`) |
| `--mock` | Use built-in sample data (no PDF needed) |
| `--scan` | List tables without writing output |

---

## Library usage

```python
from pdfstripper import extract_tables, tables_to_csv

# Extract from a real PDF
tables = extract_tables("statement.pdf")

for table in tables:
    print(table.summary())
    # Page 1, Table 1: 9 rows x 5 cols

# Write to CSV
paths = tables_to_csv(tables, output_dir="./output")

# Or get as JSON
from pdfstripper.writer import tables_to_json
print(tables_to_json(tables))

# Access as dicts
for row in tables[0].to_dict_rows():
    print(row["Date"], row["Amount"])
```

---

## How it works

1. Opens the PDF with `pdfplumber`
2. Calls `page.extract_tables()` for each page
3. Cleans each cell: strips whitespace, collapses spaces, converts `None` to `""`
4. Detects header rows using a heuristic (majority non-numeric cells)
5. Drops fully empty rows
6. Writes each table to a separate CSV with a descriptive filename

---

## Project structure

```
pdf-table-stripper/
├── pdfstripper/
│   ├── __init__.py      # Public API
│   ├── models.py        # Table and TableRow dataclasses
│   ├── extractor.py     # pdfplumber extractor + MockPDFExtractor
│   ├── writer.py        # CSV and JSON writers
│   └── cli.py           # CLI entry point
├── tests/
│   └── test_stripper.py # 28 tests, all run without pdfplumber
└── pyproject.toml
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Issues labelled [`good first issue`](https://github.com/jishanahmed-shaikh/pdf-table-stripper/issues?q=label%3A%22good+first+issue%22) are a great place to start.

---

## License

[MIT](LICENSE) © 2026 [Jishanahmed AR Shaikh](https://github.com/jishanahmed-shaikh)
