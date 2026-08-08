from typing import Any, Callable, List, Optional, Sequence

from .utils import get_column, is_table


def sort(
    array: Sequence[Any],
    by: Optional[int] = None,
    key: Optional[Callable[[Any], Any]] = None,
    reverse: bool = False,
) -> List[Any]:
    """Excel-style SORT.

    A flat list is sorted by value. A 2D table (list of rows) is sorted
    by the column `by` (1-based). `key` overrides both for custom sorting.

    Raises InvalidIndexError if `by` is out of range for any row.
    """
    if key is not None:
        sort_key = key
    elif by is not None:
        if not is_table(array):
            raise ValueError("by was given but array is a flat list, not a 2D table")
        get_column(array, by)  # validates `by` against every row
        sort_key = lambda row: row[by - 1]
    else:
        sort_key = None

    return sorted(array, key=sort_key, reverse=reverse)
