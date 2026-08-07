from typing import Any, Callable, Sequence, Union


def filter(
    array: Sequence[Any],
    condition: Union[Callable[[Any], bool], Sequence[bool]],
    if_empty: Any = None,
) -> Any:
    """Excel-style FILTER. Keeps items where condition is truthy.

    condition can be a predicate function, or a sequence of booleans the
    same length as array (mirrors Excel's boolean include array).
    if_empty is returned instead of an empty list when nothing matches.
    """
    if callable(condition):
        result = [item for item in array if condition(item)]
    else:
        if len(condition) != len(array):
            raise ValueError("condition must be the same length as array")
        result = [item for item, keep in zip(array, condition) if keep]

    if not result and if_empty is not None:
        return if_empty
    return result


def unique(array: Sequence[Any], keep: str = "first") -> list:
    """Excel-style UNIQUE. Returns distinct items, preserving order.

    keep: "first" keeps the first occurrence of each value, "last" keeps
    the last. Rows (lists/tuples) are compared by value.
    """
    if keep not in ("first", "last"):
        raise ValueError('keep must be "first" or "last"')

    items = list(reversed(array)) if keep == "last" else list(array)

    seen = set()
    result = []
    for item in items:
        key = tuple(item) if isinstance(item, (list, tuple)) else item
        if key not in seen:
            seen.add(key)
            result.append(item)

    if keep == "last":
        result.reverse()
    return result
