from typing import Any, List, Optional, Sequence, Union

from .exceptions import InvalidIndexError, NotFoundError
from .utils import MISSING, get_column, get_row, is_table, resolve_column, uses_names

ColumnRef = Union[int, str]


def match(lookup_value: Any, lookup_array: Sequence[Any], match_type: int = 0) -> int:
    """Excel-style MATCH. Returns the 1-based position of lookup_value.

    match_type:
        0  exact match, any order.
        1  largest value <= lookup_value; lookup_array must be ascending.
       -1  smallest value >= lookup_value; lookup_array must be descending.
    """
    if match_type == 0:
        for i, item in enumerate(lookup_array):
            if item == lookup_value:
                return i + 1
        raise NotFoundError(lookup_value)

    if match_type == 1:
        best = None
        for i, item in enumerate(lookup_array):
            if item <= lookup_value:
                best = i + 1
            else:
                break
        if best is None:
            raise NotFoundError(lookup_value)
        return best

    if match_type == -1:
        best = None
        for i, item in enumerate(lookup_array):
            if item >= lookup_value:
                best = i + 1
            else:
                break
        if best is None:
            raise NotFoundError(lookup_value)
        return best

    raise ValueError("match_type must be -1, 0, or 1")


def index(
    array: Sequence[Any], row_num: int, col_num: Optional[int] = None
) -> Any:
    """Excel-style INDEX. row_num/col_num are 1-based.

    For a flat list, pass only row_num. For a 2D table (list of rows),
    pass col_num too; omit it to get the whole row back.
    """
    if is_table(array):
        row = get_row(array, row_num)
        if col_num is None:
            return row
        if col_num < 1 or col_num > len(row):
            raise InvalidIndexError(f"col_num {col_num} is out of range")
        return row[col_num - 1]

    if col_num is not None:
        raise ValueError("col_num was given but array is a flat list, not a 2D table")
    if row_num < 1 or row_num > len(array):
        raise InvalidIndexError(f"row_num {row_num} is out of range")
    return array[row_num - 1]


def index_match(
    return_array: Sequence[Any],
    lookup_value: Any,
    lookup_array: Sequence[Any],
    match_type: int = 0,
) -> Any:
    """Excel-style INDEX+MATCH combo: locate lookup_value in lookup_array,
    then return the item at that same position in return_array."""
    position = match(lookup_value, lookup_array, match_type)
    return index(return_array, position)


def vlookup(
    lookup_value: Any,
    table: Sequence[Sequence[Any]],
    col_index: Union[ColumnRef, Sequence[ColumnRef], None] = None,
    exact: bool = True,
    if_not_found: Any = MISSING,
) -> Any:
    """Excel-style VLOOKUP. Searches the first column of `table` for
    lookup_value and returns something from the matching row.

    col_index decides what comes back:
        3                 the value in column 3 (1-based, like Excel)
        "score"           the value under the "score" heading
        ["name", "city"]  those columns, as a list
        None              the whole matching row

    Column names are read from the table's first row, which is then treated
    as a header and left out of the search.

    With exact=False the first column must be sorted ascending; the largest
    value <= lookup_value is matched (same as Excel).
    if_not_found is returned instead of raising NotFoundError when there is
    no match; omit it to get the exception.
    """
    wants_list = isinstance(col_index, (list, tuple))
    refs: Sequence[ColumnRef] = col_index if wants_list else [col_index]  # type: ignore[assignment]

    header = list(table[0]) if len(table) else []
    body = table[1:] if uses_names(*refs) else table

    try:
        position = match(lookup_value, get_column(body, 1), 0 if exact else 1)
    except NotFoundError:
        if if_not_found is not MISSING:
            return if_not_found
        raise

    row = get_row(body, position)
    if col_index is None:
        return row

    values = []
    for ref in refs:
        col_num = resolve_column(header, ref)
        if col_num < 1 or col_num > len(row):
            raise InvalidIndexError(f"col_index {ref!r} is out of range")
        values.append(row[col_num - 1])
    return values if wants_list else values[0]


def hlookup(
    lookup_value: Any,
    table: Sequence[Sequence[Any]],
    row_index: Union[ColumnRef, Sequence[ColumnRef], None] = None,
    exact: bool = True,
    if_not_found: Any = MISSING,
) -> Any:
    """Excel-style HLOOKUP. Searches the first row of `table` for
    lookup_value and returns something from the matching column.

    row_index mirrors vlookup's col_index: a 1-based number, a row label,
    a list of either, or None for the whole matching column. Row labels are
    read from the table's first column, which is then left out of the search.

    With exact=False the first row must be sorted ascending; the largest
    value <= lookup_value is matched (same as Excel).
    if_not_found is returned instead of raising NotFoundError when there is
    no match; omit it to get the exception.
    """
    wants_list = isinstance(row_index, (list, tuple))
    refs: Sequence[ColumnRef] = row_index if wants_list else [row_index]  # type: ignore[assignment]

    by_name = uses_names(*refs)
    labels = get_column(table, 1) if by_name else []
    body = [list(row)[1:] for row in table] if by_name else table

    try:
        position = match(lookup_value, get_row(body, 1), 0 if exact else 1)
    except NotFoundError:
        if if_not_found is not MISSING:
            return if_not_found
        raise

    column = get_column(body, position)
    if row_index is None:
        return column

    values = []
    for ref in refs:
        row_num = resolve_column(labels, ref)
        if row_num < 1 or row_num > len(column):
            raise InvalidIndexError(f"row_index {ref!r} is out of range")
        values.append(column[row_num - 1])
    return values if wants_list else values[0]


def xlookup(
    lookup_value: Any,
    lookup_array: Sequence[Any],
    return_array: Sequence[Any],
    if_not_found: Any = MISSING,
    match_mode: int = 0,
    search_mode: int = 1,
) -> Any:
    """Excel-style XLOOKUP.

    match_mode:
        0  exact match.
       -1  exact match, else the next smaller item.
        1  exact match, else the next larger item.
    search_mode:
        1  search first to last (default).
       -1  search last to first.
    if_not_found:
        value returned instead of raising NotFoundError when nothing matches.
        Omit it to get the exception; any value is accepted, including None.
    """
    if match_mode not in (-1, 0, 1):
        raise ValueError("match_mode must be -1, 0, or 1")
    if search_mode not in (-1, 1):
        raise ValueError("search_mode must be -1 or 1")
    if len(lookup_array) != len(return_array):
        raise ValueError("lookup_array and return_array must be the same length")

    indices = range(len(lookup_array))
    if search_mode == -1:
        indices = reversed(indices)

    closest_i, closest_value = None, None
    for i in indices:
        item = lookup_array[i]
        if item == lookup_value:
            return return_array[i]
        if match_mode == -1 and item < lookup_value:
            if closest_value is None or item > closest_value:
                closest_i, closest_value = i, item
        elif match_mode == 1 and item > lookup_value:
            if closest_value is None or item < closest_value:
                closest_i, closest_value = i, item

    if closest_i is not None:
        return return_array[closest_i]
    if if_not_found is not MISSING:
        return if_not_found
    raise NotFoundError(lookup_value)
