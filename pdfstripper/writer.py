"""
CSV writer for extracted tables.

Writes each :class:`~pdfstripper.models.Table` to a separate CSV file
with a descriptive filename.  Also supports writing all tables to a
single CSV with a page/table separator row.
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import List, Optional

from pdfstripper.models import Table


def _safe_filename(source_file: str, page: int, table_idx: int) -> str:
    """Build a safe output filename for a table CSV.

    Parameters
    ----------
    source_file:
        Path to the source PDF.
    page:
        1-indexed page number.
    table_idx:
        0-indexed table index on the page.

    Returns
    -------
    str
        Filename like ``statement_page1_table1.csv``.
    """
    stem = Path(source_file).stem if source_file else "output"
    # Sanitise stem
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in stem)
    return f"{safe}_page{page}_table{table_idx + 1}.csv"


def table_to_csv_string(table: Table) -> str:
    """Serialise a single table to a CSV string.

    Parameters
    ----------
    table:
        The :class:`~pdfstripper.models.Table` to serialise.

    Returns
    -------
    str
        CSV-formatted string with headers (if present) followed by data rows.
    """
    import io
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")

    if table.headers:
        writer.writerow(table.headers)
    for row in table.rows:
        writer.writerow(row)

    return buf.getvalue()


def tables_to_csv(
    tables: List[Table],
    output_dir: str = ".",
    single_file: bool = False,
    output_file: Optional[str] = None,
) -> List[str]:
    """Write extracted tables to CSV files.

    Parameters
    ----------
    tables:
        List of :class:`~pdfstripper.models.Table` objects to write.
    output_dir:
        Directory to write CSV files into.
    single_file:
        If ``True``, write all tables to a single CSV with separator rows.
        If ``False`` (default), write one CSV per table.
    output_file:
        Filename for the single-file output (used when ``single_file=True``).
        Defaults to ``all_tables.csv``.

    Returns
    -------
    List[str]
        Paths to all created CSV files.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    created: List[str] = []

    if single_file:
        fname = output_file or "all_tables.csv"
        dest  = out / fname
        with dest.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for i, table in enumerate(tables):
                if i > 0:
                    writer.writerow([])  # blank separator row
                writer.writerow([f"# Page {table.page_number}, Table {table.table_index + 1}"])
                if table.headers:
                    writer.writerow(table.headers)
                for row in table.rows:
                    writer.writerow(row)
        created.append(str(dest))
    else:
        for table in tables:
            fname = _safe_filename(table.source_file, table.page_number, table.table_index)
            dest  = out / fname
            with dest.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if table.headers:
                    writer.writerow(table.headers)
                for row in table.rows:
                    writer.writerow(row)
            created.append(str(dest))

    return created


def tables_to_json(tables: List[Table]) -> str:
    """Serialise all tables to a JSON string.

    Parameters
    ----------
    tables:
        List of :class:`~pdfstripper.models.Table` objects.

    Returns
    -------
    str
        JSON array of table objects.
    """
    data = [
        {
            "page":        t.page_number,
            "table_index": t.table_index,
            "headers":     t.headers,
            "rows":        t.rows,
            "row_count":   t.row_count,
            "col_count":   t.col_count,
            "source_file": t.source_file,
        }
        for t in tables
    ]
    return json.dumps(data, indent=2, ensure_ascii=False)
