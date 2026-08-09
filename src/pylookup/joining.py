from typing import Any, List, Sequence, Tuple, Union

from .exceptions import InvalidIndexError
from .utils import resolve_column

KeyRef = Union[int, str]


def join(
    left: Sequence[Sequence[Any]],
    right: Sequence[Sequence[Any]],
    by: Union[KeyRef, Tuple[KeyRef, KeyRef]],
    if_not_found: Any = None,
) -> List[List[Any]]:
    """Attach every column of `right` to the rows of `left` that match on a key.

    This is "drag the VLOOKUP down the whole column" as one call: instead of
    one value, you get both tables joined into a new one.

    Both tables start with a header row, which is how column names are
    resolved and what the returned header is built from.

    by:
        "cust_id"                the key column, named the same in both tables
        ("id", "cust_id")        different names on each side
        2                        or a 1-based column number, used on both sides
    if_not_found:
        filled into the right-hand columns for rows with no match (None by
        default, like Excel leaving the cell blank).

    Rows keep the order of `left`. When `right` holds a key more than once the
    first of those rows wins, matching what dragging a VLOOKUP down does.
    """
    if not len(left) or not len(right):
        raise InvalidIndexError("join needs a header row in both tables")

    left_by, right_by = by if isinstance(by, tuple) else (by, by)
    left_head, right_head = list(left[0]), list(right[0])

    li = resolve_column(left_head, left_by) - 1
    ri = resolve_column(right_head, right_by) - 1
    if li < 0 or li >= len(left_head):
        raise InvalidIndexError(f"key column {left_by!r} is out of range for the left table")
    if ri < 0 or ri >= len(right_head):
        raise InvalidIndexError(f"key column {right_by!r} is out of range for the right table")

    carried = [i for i in range(len(right_head)) if i != ri]

    # Index the right table once, so each left row is an O(1) dict hit rather
    # than a fresh scan. setdefault keeps the first row for a repeated key.
    index: dict = {}
    for row in right[1:]:
        if ri < len(row):
            index.setdefault(row[ri], [row[i] if i < len(row) else None for i in carried])

    blank = [if_not_found] * len(carried)

    header = left_head + [right_head[i] for i in carried]
    rows = [
        list(row) + index.get(row[li] if li < len(row) else None, blank)
        for row in left[1:]
    ]
    return [header] + rows
