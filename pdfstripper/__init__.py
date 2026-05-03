"""
pdf-table-stripper
==================
Extract tabular data from messy PDFs into clean CSVs.

Uses ``pdfplumber`` for accurate table detection and extraction.
Install the PDF dependency with::

    pip install "pdf-table-stripper[pdf]"

Without ``pdfplumber`` installed, the :class:`~pdfstripper.extractor.MockPDFExtractor`
is used automatically — it returns realistic sample tables so the full
pipeline can be tested without any PDF files.

To use with a real PDF::

    from pdfstripper import extract_tables, tables_to_csv
    tables = extract_tables("statement.pdf")
    tables_to_csv(tables, output_dir="./output")

Public API
----------
- :func:`~pdfstripper.extractor.extract_tables`  — extract all tables from a PDF
- :func:`~pdfstripper.writer.tables_to_csv`      — write tables to CSV files
- :class:`~pdfstripper.models.Table`             — a single extracted table
"""

__version__ = "1.0.0"
__author__  = "Jishanahmed AR Shaikh"
__license__ = "MIT"

from pdfstripper.extractor import extract_tables   # noqa: F401
from pdfstripper.models import Table, TableRow     # noqa: F401
from pdfstripper.writer import tables_to_csv       # noqa: F401
