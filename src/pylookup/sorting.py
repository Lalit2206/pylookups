from typing import Any, Callable, List, Optional, Sequence

from .utils import is_table


def sort(
    array: Sequence[Any],
    by: Optional[int] = None,
    key: Optional[Callable[[Any], Any]] = None,
    reverse: bool = False,
) -> List[Any]:
    """Excel-style SORT.

    A flat list is sorted by value. A 2D table (list of rows) is sorted
    by the column `by` (1-based). `key` overrides both for custom sorting.
    """
    if key is not None:
        sort_key = key
    elif is_table(array) and by is not None:
        sort_key = lambda row: row[by - 1]
    else:
        sort_key = None

    return sorted(array, key=sort_key, reverse=reverse)
