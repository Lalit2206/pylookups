from typing import Any, List, Sequence

from .exceptions import InvalidIndexError


class _Missing:
    """Type of the MISSING sentinel."""

    def __repr__(self) -> str:
        return "MISSING"


MISSING = _Missing()
"""Sentinel for "argument not supplied", so None can be passed as a real value."""


def is_table(array: Sequence[Any]) -> bool:
    """True if array is 2D (a sequence of rows) rather than a flat list."""
    return len(array) > 0 and isinstance(array[0], (list, tuple))


def get_row(table: Sequence[Sequence[Any]], row_num: int) -> List[Any]:
    """Return row `row_num` (1-based) from a 2D table."""
    if row_num < 1 or row_num > len(table):
        raise InvalidIndexError(f"row_num {row_num} is out of range")
    return list(table[row_num - 1])


def get_column(table: Sequence[Sequence[Any]], col_num: int) -> List[Any]:
    """Return column `col_num` (1-based) from a 2D table."""
    if col_num < 1:
        raise InvalidIndexError(f"col_num {col_num} is out of range")
    column = []
    for row in table:
        if col_num > len(row):
            raise InvalidIndexError(f"col_num {col_num} is out of range")
        column.append(row[col_num - 1])
    return column
