"""
Data models for pdf-table-stripper.

All models are plain dataclasses — no external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


# A single row is a list of cell strings (empty string for blank cells)
TableRow = List[str]


@dataclass
class Table:
    """A single table extracted from a PDF page.

    Attributes
    ----------
    page_number:
        1-indexed page number where the table was found.
    table_index:
        0-indexed position of this table on the page (if multiple tables exist).
    headers:
        List of column header strings.  Empty list if no header row was detected.
    rows:
        List of data rows, each a list of cell strings.
    bbox:
        Bounding box ``(x0, y0, x1, y1)`` of the table on the page, or ``None``.
    source_file:
        Path to the source PDF file.
    """

    page_number: int
    table_index: int
    headers: List[str] = field(default_factory=list)
    rows: List[TableRow] = field(default_factory=list)
    bbox: Optional[tuple] = None
    source_file: str = ""

    @property
    def row_count(self) -> int:
        """Number of data rows (excluding header)."""
        return len(self.rows)

    @property
    def col_count(self) -> int:
        """Number of columns (from header or first row)."""
        if self.headers:
            return len(self.headers)
        return len(self.rows[0]) if self.rows else 0

    @property
    def is_empty(self) -> bool:
        """True if the table has no data rows."""
        return len(self.rows) == 0

    def to_dict_rows(self) -> List[dict]:
        """Return rows as a list of dicts keyed by header.

        Returns
        -------
        List[dict]
            Each row as ``{header: cell_value}``.
            If no headers, keys are ``col_0``, ``col_1``, etc.
        """
        if self.headers:
            keys = self.headers
        else:
            keys = [f"col_{i}" for i in range(self.col_count)]

        result = []
        for row in self.rows:
            # Pad or truncate row to match key count
            padded = list(row) + [""] * max(0, len(keys) - len(row))
            result.append(dict(zip(keys, padded[:len(keys)])))
        return result

    def summary(self) -> str:
        """Return a one-line summary string."""
        return (
            f"Page {self.page_number}, Table {self.table_index + 1}: "
            f"{self.row_count} rows x {self.col_count} cols"
        )
