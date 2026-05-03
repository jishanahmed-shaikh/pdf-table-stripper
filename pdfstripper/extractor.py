"""
PDF table extractor.

Uses ``pdfplumber`` when installed.  Falls back to :class:`MockPDFExtractor`
automatically when ``pdfplumber`` is not available, so the full pipeline
can be tested without any PDF files or the pdfplumber dependency.

Install pdfplumber for real PDF extraction::

    pip install "pdf-table-stripper[pdf]"

The :class:`MockPDFExtractor` returns realistic sample tables that mirror
the structure of real financial/accounting PDFs.  Swapping it for the real
extractor requires zero code changes — just install pdfplumber.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

from pdfstripper.models import Table


# ---------------------------------------------------------------------------
# Cleaner helpers
# ---------------------------------------------------------------------------

def _clean_cell(value) -> str:
    """Normalise a raw cell value to a clean string.

    Parameters
    ----------
    value:
        Raw cell value from pdfplumber (may be None, str, int, float).

    Returns
    -------
    str
        Cleaned string with leading/trailing whitespace removed.
    """
    if value is None:
        return ""
    text = str(value).strip()
    # Collapse internal whitespace
    import re
    text = re.sub(r"\s+", " ", text)
    return text


def _clean_row(row: list) -> List[str]:
    """Clean all cells in a row."""
    return [_clean_cell(cell) for cell in row]


def _is_header_row(row: List[str]) -> bool:
    """Heuristic: a row is likely a header if most cells are non-numeric strings."""
    if not row:
        return False
    non_numeric = sum(
        1 for cell in row
        if cell and not _is_numeric(cell)
    )
    return non_numeric >= len(row) * 0.5


def _is_numeric(s: str) -> bool:
    """Return True if *s* looks like a number (int, float, currency)."""
    import re
    cleaned = re.sub(r"[,$%\s]", "", s)
    try:
        float(cleaned)
        return True
    except ValueError:
        return False


def _drop_empty_rows(rows: List[List[str]]) -> List[List[str]]:
    """Remove rows where all cells are empty."""
    return [row for row in rows if any(cell.strip() for cell in row)]


# ---------------------------------------------------------------------------
# Post-process tables
# ---------------------------------------------------------------------------

def _filter_tables(
    tables: List[Table],
    min_rows: int,
) -> List[Table]:
    """Filters out tables with row counts below `min_rows` (if defined).

    Parameters
    ----------
    tables:
       All tables found in the PDF.
    min_rows:
        Minimum rows in a table required to not be filtered.

    Returns
    -------
    List[Table]
        Tables found in the PDF with row counts of at least `min_rows`.
    """
    if min_rows is not None:
        tables = [t for t in tables if t.row_count >= min_rows]
    return tables


# ---------------------------------------------------------------------------
# Real extractor (requires pdfplumber)
# ---------------------------------------------------------------------------

def _extract_with_pdfplumber(pdf_path: str, pages: Optional[List[int]] = None) -> List[Table]:
    """Extract tables from a PDF using pdfplumber.

    Parameters
    ----------
    pdf_path:
        Path to the PDF file.
    pages:
        1-indexed list of page numbers to process.  ``None`` = all pages.

    Returns
    -------
    List[Table]
        All tables found in the PDF.
    """
    import pdfplumber  # type: ignore

    tables: List[Table] = []

    with pdfplumber.open(pdf_path) as pdf:
        page_iter = pdf.pages
        if pages:
            page_iter = [pdf.pages[p - 1] for p in pages if 1 <= p <= len(pdf.pages)]

        for page in page_iter:
            page_num = page.page_number
            raw_tables = page.extract_tables()

            for t_idx, raw_table in enumerate(raw_tables):
                if not raw_table:
                    continue

                cleaned = [_clean_row(row) for row in raw_table]
                cleaned = _drop_empty_rows(cleaned)

                if not cleaned:
                    continue

                # Detect header row
                headers: List[str] = []
                data_rows = cleaned

                if len(cleaned) > 1 and _is_header_row(cleaned[0]):
                    headers   = cleaned[0]
                    data_rows = cleaned[1:]

                tables.append(Table(
                    page_number=page_num,
                    table_index=t_idx,
                    headers=headers,
                    rows=data_rows,
                    source_file=str(pdf_path),
                ))

    return tables


# ---------------------------------------------------------------------------
# Mock extractor — no PDF or pdfplumber required
# ---------------------------------------------------------------------------

class MockPDFExtractor:
    """Returns realistic sample tables without needing a real PDF.

    Simulates a bank statement PDF with two pages:
    - Page 1: Transaction table (date, description, debit, credit, balance)
    - Page 2: Summary table (account details)

    Swapping this for real pdfplumber extraction requires zero code changes.
    Just install pdfplumber and call :func:`extract_tables` with a real PDF path.
    """

    @staticmethod
    def extract(source_file: str = "mock.pdf") -> List[Table]:
        """Return sample tables mimicking a bank statement PDF."""
        # Page 1 — transaction table
        t1 = Table(
            page_number=1,
            table_index=0,
            headers=["Date", "Description", "Debit", "Credit", "Balance"],
            rows=[
                ["01/04/2026", "Opening Balance",    "",         "",         "10,000.00"],
                ["03/04/2026", "NEFT - Salary",      "",         "50,000.00","60,000.00"],
                ["05/04/2026", "Amazon Purchase",    "2,499.00", "",         "57,501.00"],
                ["07/04/2026", "Electricity Bill",   "1,200.00", "",         "56,301.00"],
                ["10/04/2026", "ATM Withdrawal",     "5,000.00", "",         "51,301.00"],
                ["15/04/2026", "UPI - Zomato",       "450.00",   "",         "50,851.00"],
                ["20/04/2026", "Interest Credit",    "",         "312.50",   "51,163.50"],
                ["25/04/2026", "Insurance Premium",  "8,500.00", "",         "42,663.50"],
                ["30/04/2026", "Closing Balance",    "",         "",         "42,663.50"],
            ],
            source_file=source_file,
        )

        # Page 1 — second table (account summary)
        t2 = Table(
            page_number=1,
            table_index=1,
            headers=["Field", "Value"],
            rows=[
                ["Account Number", "XXXX-XXXX-1234"],
                ["Account Holder", "John Doe"],
                ["Statement Period", "01 Apr 2026 - 30 Apr 2026"],
                ["Opening Balance", "10,000.00"],
                ["Closing Balance", "42,663.50"],
                ["Total Credits", "50,312.50"],
                ["Total Debits", "17,649.00"],
            ],
            source_file=source_file,
        )

        # Page 2 — charges table
        t3 = Table(
            page_number=2,
            table_index=0,
            headers=["Charge Type", "Amount", "Date"],
            rows=[
                ["Annual Maintenance Fee", "500.00",  "01/04/2026"],
                ["SMS Alert Charges",      "15.00",   "01/04/2026"],
                ["NEFT Charges",           "0.00",    "03/04/2026"],
            ],
            source_file=source_file,
        )

        return [t1, t2, t3]


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def extract_tables(
    pdf_path: str,
    pages: Optional[List[int]] = None,
    min_rows: Optional[int] = None,
    use_mock: bool = False,
) -> List[Table]:
    """Extract all tables from a PDF file.

    Automatically uses ``pdfplumber`` if installed.  Falls back to
    :class:`MockPDFExtractor` if ``pdfplumber`` is not available or
    ``use_mock=True`` is passed.

    Filters out tables with row counts below `min_rows` (if defined). 

    Parameters
    ----------
    pdf_path:
        Path to the PDF file.  Ignored when using mock extractor.
    pages:
        1-indexed list of page numbers to process.  ``None`` = all pages.
        Only used with the real pdfplumber extractor.
    min_rows : optional
        Minimum rows in a table required to extract it.
    use_mock:
        Force use of the mock extractor (useful for testing).

    Returns
    -------
    List[Table]
        All tables found, in page order.

    Notes
    -----
    To use with a real PDF, install pdfplumber::

        pip install "pdf-table-stripper[pdf]"

    Then call::

        tables = extract_tables("statement.pdf")
    """
    if use_mock:
        return _filter_tables(
            MockPDFExtractor.extract(source_file=pdf_path),
            min_rows=min_rows
        )
    try:
        import pdfplumber  # noqa: F401
        return _filter_tables(
            _extract_with_pdfplumber(pdf_path, pages=pages),
            min_rows=min_rows
        )
    except ImportError:
        # pdfplumber not installed — use mock and warn
        import sys
        print(
            "Warning: pdfplumber is not installed. Using mock extractor.\n"
            "Install it with: pip install 'pdf-table-stripper[pdf]'",
            file=sys.stderr,
        )
        return _filter_tables(
            MockPDFExtractor.extract(source_file=pdf_path),
            min_rows=min_rows
        )