from typing import Any, Callable, List, Optional, Sequence, Union

from .utils import get_column, is_table, resolve_column, uses_names


def sort(
    array: Sequence[Any],
    by: Union[int, str, None] = None,
    key: Optional[Callable[[Any], Any]] = None,
    reverse: bool = False,
) -> List[Any]:
    """Excel-style SORT.

    A flat list is sorted by value. A 2D table (list of rows) is sorted by the
    column `by`, given as a 1-based number or as a column name. `key` overrides
    both for custom sorting.

    Naming a column means the first row is a header: it stays at the top and
    only the rows under it are sorted.

    Raises InvalidIndexError if `by` is out of range for any row.
    """
    if key is not None:
        return sorted(array, key=key, reverse=reverse)

    if by is None:
        return sorted(array, reverse=reverse)

    if not is_table(array):
        raise ValueError("by was given but array is a flat list, not a 2D table")

    if uses_names(by):
        header, body = array[0], array[1:]
        col_num = resolve_column(header, by)
        get_column(body, col_num)  # validates the column against every row
        return [list(header)] + sorted(body, key=lambda row: row[col_num - 1], reverse=reverse)

    get_column(array, by)  # validates `by` against every row
    return sorted(array, key=lambda row: row[by - 1], reverse=reverse)
