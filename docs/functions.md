# Function Reference

All row/column positions follow Excel's convention: **1-based**, not 0-based.

Most functions raise `pylookup.exceptions.NotFoundError` when a value isn't
found and `pylookup.exceptions.InvalidIndexError` when a position is out of
range. Both inherit from `pylookup.exceptions.PyLookupError`, so you can
catch everything with one `except`.

This sample table is used in the examples below:

```python
table = [
    ["id", "name", "score"],
    [1, "alice", 90],
    [2, "bob", 75],
    [3, "carol", 60],
]
```

---

## xlookup

```python
xlookup(lookup_value, lookup_array, return_array,
        if_not_found=None, match_mode=0, search_mode=1)
```

Search `lookup_array` for `lookup_value` and return the item at the same
position in `return_array`. Both arrays must be the same length.

| Parameter | Values |
|---|---|
| `match_mode` | `0` exact · `-1` exact or next smaller · `1` exact or next larger |
| `search_mode` | `1` first-to-last · `-1` last-to-first |
| `if_not_found` | returned instead of raising `NotFoundError` |

```python
ids = [1, 2, 3]
names = ["alice", "bob", "carol"]

xlookup(2, ids, names)                        # "bob"
xlookup(99, ids, names, if_not_found="n/a")   # "n/a"
xlookup(7, [1, 5, 10], names, match_mode=-1)  # "bob"  (next smaller: 5)
```

---

## vlookup

```python
vlookup(lookup_value, table, col_index, exact=True)
```

Search the **first column** of `table` for `lookup_value`, return the value
at `col_index` of the matching row.

```python
vlookup(2, table, 2)   # "bob"
vlookup(2, table, 3)   # 75
```

!!! note
    With `exact=False` the first column must be sorted ascending; the
    largest value <= `lookup_value` is matched (same as Excel).

---

## hlookup

```python
hlookup(lookup_value, table, row_index, exact=True)
```

Like `vlookup`, but horizontal: search the **first row**, return the value
at `row_index` of the matching column.

```python
h_table = [
    ["id", 1, 2, 3],
    ["name", "alice", "bob", "carol"],
]

hlookup(2, h_table, 2)   # "bob"
```

---

## index

```python
index(array, row_num, col_num=None)
```

Value at a position. Flat list → pass only `row_num`. 2D table → pass
`col_num` too, or omit it to get the whole row.

```python
index(["a", "b", "c"], 2)   # "b"
index(table, 3, 2)          # "bob"
index(table, 3)             # [2, "bob", 75]
```

---

## match

```python
match(lookup_value, lookup_array, match_type=0)
```

The 1-based **position** of `lookup_value` in `lookup_array`.

| `match_type` | Meaning |
|---|---|
| `0` | exact match, any order |
| `1` | largest value <= target — array must be sorted ascending |
| `-1` | smallest value >= target — array must be sorted descending |

```python
match("carol", ["alice", "bob", "carol"])   # 3
match(6, [1, 3, 5, 9], match_type=1)        # 3  (5 is largest <= 6)
```

---

## index_match

```python
index_match(return_array, lookup_value, lookup_array, match_type=0)
```

The classic Excel INDEX+MATCH combo in one call: find `lookup_value` in
`lookup_array`, return the item at that position in `return_array`.

```python
names = ["alice", "bob", "carol"]
scores = [90, 75, 60]

index_match(scores, "bob", names)   # 75
```

---

## filter

```python
filter(array, condition, if_empty=None)
```

Keep items where `condition` is true. `condition` is either a function or
a boolean list the same length as `array` (like Excel's include array).

```python
filter([1, 2, 3, 4, 5], lambda x: x % 2 == 0)    # [2, 4]
filter(["a", "b", "c"], [True, False, True])     # ["a", "c"]
filter([1, 2], lambda x: x > 10, if_empty="-")   # "-"
```

!!! warning
    Importing `filter` by name shadows Python's built-in `filter` in that
    file. If you need both, use `import pylookup as pl` and call
    `pl.filter(...)`.

---

## unique

```python
unique(array, keep="first")
```

Distinct items, original order preserved. `keep="last"` keeps the last
occurrence of each value instead of the first.

```python
unique([1, 2, 2, 3, 1])                # [1, 2, 3]
unique([1, 2, 2, 3, 1], keep="last")   # [2, 3, 1]
unique([["a", 1], ["b", 2], ["a", 1]]) # [["a", 1], ["b", 2]]
```

---

## sort

```python
sort(array, by=None, key=None, reverse=False)
```

Returns a new sorted list (the input is not modified). Flat lists sort by
value; 2D tables sort by column `by` (1-based). `key` overrides both.

```python
sort([3, 1, 2])                      # [1, 2, 3]
sort(table[1:], by=3, reverse=True)  # rows by score, highest first
sort(["banana", "fig"], key=len)     # ["fig", "banana"]
```
