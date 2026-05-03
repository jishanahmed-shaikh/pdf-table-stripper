"""CLI for pdf-table-stripper."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pdfstripper import __version__
from pdfstripper.extractor import extract_tables
from pdfstripper.writer import tables_to_csv, tables_to_json

_GREEN  = "\033[92m"
_CYAN   = "\033[96m"
_YELLOW = "\033[93m"
_BOLD   = "\033[1m"
_RESET  = "\033[0m"


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        prog="pdfstrip",
        description=(
            "Extract tables from messy PDFs into clean CSVs.\n\n"
            "Requires pdfplumber for real PDF extraction:\n"
            "  pip install 'pdf-table-stripper[pdf]'\n\n"
            "Use --mock to test without a PDF file or pdfplumber installed."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "pdf",
        nargs="?",
        help="Path to the PDF file (omit with --mock)",
    )
    parser.add_argument(
        "--output", "-o",
        default="./output",
        metavar="DIR",
        help="Output directory for CSV files (default: ./output)",
    )
    parser.add_argument(
        "--pages", "-p",
        nargs="+",
        type=int,
        metavar="N",
        help="Page numbers to extract (default: all pages)",
    )
    parser.add_argument(
        "--single-file",
        action="store_true",
        help="Write all tables to a single CSV instead of one per table",
    )
    parser.add_argument(
        "--output-file",
        metavar="FILE",
        help="Filename for single-file output (default: all_tables.csv)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["csv", "json", "excel"],
        default="csv",
        help="Output format: csv, json or excel (default: csv)",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use built-in mock data (no PDF or pdfplumber needed)",
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="List detected tables without writing output",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output",
    )
    parser.add_argument(
        "--version", "-V",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args(argv)
    use_color = sys.stderr.isatty()

    if not args.mock and not args.pdf:
        parser.error("Provide a PDF file path or use --mock for sample data.")

    if not args.mock and not Path(args.pdf).exists():
        print(f"Error: file not found: {args.pdf}", file=sys.stderr)
        sys.exit(1)

    pdf_path = args.pdf or "mock.pdf"

    if not args.quiet:
        b = _BOLD if use_color else ""
        r = _RESET if use_color else ""
        mode = f"{_YELLOW}MOCK{_RESET}" if (args.mock and use_color) else ("MOCK" if args.mock else pdf_path)
        print(f"\n  {b}pdf-table-stripper{r} — {mode}", file=sys.stderr)

    tables = extract_tables(pdf_path, pages=args.pages, use_mock=args.mock)

    if not tables:
        print("  No tables found.", file=sys.stderr)
        sys.exit(0)

    if not args.quiet:
        print(f"  Found {len(tables)} table(s):", file=sys.stderr)
        for t in tables:
            print(f"    {t.summary()}", file=sys.stderr)
        print(file=sys.stderr)

    if args.scan:
        return

    if args.format == "json":
        print(tables_to_json(tables))
        return
    
    elif args.format == "excel":
        from pdfstripper.writer import tables_to_excel
        Path(args.output).mkdir(parents=True, exist_ok=True)
        output_path = Path(args.output) / "all_tables.xlsx"
        tables_to_excel(tables, output_path)
        if not args.quiet:
            g = _GREEN if use_color else ""
            r = _RESET if use_color else ""
            print(f"  {g}Written:{r} {output_path}")
        return


    paths = tables_to_csv(
        tables,
        output_dir=args.output,
        single_file=args.single_file,
        output_file=args.output_file,
    )

    if not args.quiet:
        g = _GREEN if use_color else ""
        r = _RESET if use_color else ""
        for p in paths:
            print(f"  {g}Written:{r} {p}")
        print()


if __name__ == "__main__":
    main()
