from typing import Any, Optional, Sequence

from .exceptions import InvalidIndexError, NotFoundError
from .utils import get_column, get_row, is_table


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
    col_index: int,
    exact: bool = True,
) -> Any:
    """Excel-style VLOOKUP. Searches the first column of `table` for
    lookup_value and returns the value at col_index (1-based) of that row."""
    first_column = get_column(table, 1)
    match_type = 0 if exact else 1
    position = match(lookup_value, first_column, match_type)
    row = get_row(table, position)
    if col_index < 1 or col_index > len(row):
        raise InvalidIndexError(f"col_index {col_index} is out of range")
    return row[col_index - 1]


def hlookup(
    lookup_value: Any,
    table: Sequence[Sequence[Any]],
    row_index: int,
    exact: bool = True,
) -> Any:
    """Excel-style HLOOKUP. Searches the first row of `table` for
    lookup_value and returns the value at row_index (1-based) of that column."""
    first_row = get_row(table, 1)
    match_type = 0 if exact else 1
    position = match(lookup_value, first_row, match_type)
    column = get_column(table, position)
    if row_index < 1 or row_index > len(column):
        raise InvalidIndexError(f"row_index {row_index} is out of range")
    return column[row_index - 1]


def xlookup(
    lookup_value: Any,
    lookup_array: Sequence[Any],
    return_array: Sequence[Any],
    if_not_found: Any = None,
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
    """
    if match_mode not in (-1, 0, 1):
        raise ValueError("match_mode must be -1, 0, or 1")
    if search_mode not in (-1, 1):
        raise ValueError("search_mode must be -1 or 1")

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
    if if_not_found is not None:
        return if_not_found
    raise NotFoundError(lookup_value)
