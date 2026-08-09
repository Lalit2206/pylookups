# pylookups

Excel-style lookup, filter, and sort functions for plain Python lists — no
pandas or numpy required.

**Docs:** https://lalit2206.github.io/pylookups/

```bash
pip install pylookups
```

The install name is `pylookups`, but the import name is `pylookup`:

```python
from pylookup import vlookup, xlookup, match, index, index_match, filter, unique, sort, join, read_table
```

> **Note:** `filter` shadows Python's built-in `filter` in any module that
> imports it by name. If you still need the built-in in the same file, use
> the namespaced style instead:
>
> ```python
> import pylookup as pl
>
> pl.filter([1, 2, 3, 4], lambda x: x > 2)
> ```

## Install (local development)

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e ".[dev]"
pytest
```

## Functions

Row/column positions follow Excel's convention: **1-based**, not 0-based.

### `match(lookup_value, lookup_array, match_type=0)`
Position (1-based) of `lookup_value` in `lookup_array`.
`match_type`: `0` exact, `1` largest value <= target (ascending array),
`-1` smallest value >= target (descending array). Raises `NotFoundError`.

### `index(array, row_num, col_num=None)`
Value at `row_num` (and `col_num` for a 2D table). Omit `col_num` to get
the whole row.

### `index_match(return_array, lookup_value, lookup_array, match_type=0)`
`index` + `match` combined: find `lookup_value` in `lookup_array`, return
the item at that position in `return_array`.

### `vlookup(lookup_value, table, col_index=None, exact=True, if_not_found=...)`
Search the first column of `table` (list of rows) for `lookup_value`, then
return something from the matching row. `col_index` can be a 1-based number,
a column name (`"score"`), a list of either, or `None` for the whole row.
Using a name treats the first row as a header.

### `hlookup(lookup_value, table, row_index=None, exact=True, if_not_found=...)`
The same thing sideways: search the first row of `table`, return from the
matching column. `row_index` accepts a number, a row label, a list, or `None`.

### `join(left, right, by, if_not_found=None)`
Attach every column of `right` to the rows of `left` that share a key —
"drag the VLOOKUP down the column", as one call. `by` is a shared column
name, a `(left_key, right_key)` pair, or a 1-based number. Unmatched rows are
kept and filled with `if_not_found`.

### `xlookup(lookup_value, lookup_array, return_array, if_not_found=..., match_mode=0, search_mode=1)`
Search `lookup_array` for `lookup_value`, return the corresponding item
from `return_array`. `match_mode`: `0` exact, `-1` exact or next smaller,
`1` exact or next larger. `search_mode`: `1` first-to-last, `-1` last-to-first.
Pass `if_not_found` to get that value back instead of a `NotFoundError`;
omit it entirely to get the exception. Any value works, including `None`.

### `filter(array, condition, if_empty=...)`
Keep items where `condition` is true. `condition` is a predicate function
or a boolean list the same length as `array`. Pass `if_empty` to get that
value back instead of `[]` when nothing matches.

### `unique(array, keep="first")`
Distinct items, order preserved. `keep="last"` keeps the last occurrence
instead of the first.

### `sort(array, by=None, key=None, reverse=False)`
Sort a flat list, or a 2D table by column `by` (a 1-based number or a column
name). `key` overrides both with a custom function.

## Loading data

Read a file straight into a table — standard library only, no pandas, polars
or openpyxl:

```python
from pylookup import read_table

read_table("sales.csv")                  # CSV, TSV, delimiter detected
read_table("sales.xlsx", sheet="Q1")     # .xlsx/.xlsm, dates become date objects
read_table("sales.json")                 # records, rows or columns
```

`read_csv`, `read_excel`, `read_json` and `sheet_names` are available
individually. The old binary `.xls` format is not supported — save it as
`.xlsx` or `.csv` first.

## Example

```python
table = [
    ["id", "name", "score"],
    [1, "alice", 90],
    [2, "bob", 75],
    [3, "carol", 60],
]

vlookup(2, table, 2)                     # "bob"
xlookup(3, [1, 2, 3], ["a", "b", "c"])   # "c"
sort(table[1:], by=3, reverse=True)      # highest score first (skip header row)
```

See `src/examples/basic.py` for more.

## Publishing to PyPI

```bash
pip install build twine
python -m build
twine upload dist/*
```
