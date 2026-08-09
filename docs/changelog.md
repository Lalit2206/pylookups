# Changelog

All notable changes to pylookups are documented here.

## 0.1.3 — 2026-08-09 (current)

**Two tables instead of one, and data straight from files.**

- New `join()` — attaches a second table's columns to every matching row, so
  you get a whole joined table in one call instead of dragging a VLOOKUP down
  a column. Unmatched rows are kept and filled, the first of any repeated key
  wins, and the right table is indexed once so large joins stay fast.
- New file readers, all standard library — **no pandas, no polars, no
  openpyxl**:
    - `read_csv()` — detects the delimiter, converts number-like fields,
      keeps leading zeros on ids, strips Excel's UTF-8 BOM.
    - `read_excel()` — reads `.xlsx`/`.xlsm` directly, by sheet name or tab
      number, turning date cells into real `date`/`datetime` objects.
    - `read_json()` — records, rows or columns.
    - `read_table()` — picks the right reader from the file extension.
    - `sheet_names()` — lists the tabs in a workbook.
- `vlookup()` and `hlookup()` take **column names**, a list of columns, or
  `None` for the whole row/column, and accept `if_not_found` like `xlookup`.
- `sort()` takes a column name too, keeping the header row on top.
- The old binary `.xls` format is rejected with a message telling you to save
  as `.xlsx` or `.csv`, rather than a confusing parse error.

## 0.1.2 — 2026-08-08

**Fixes and corrections — no new functions.**

- `xlookup(..., if_not_found=None)` now returns `None` instead of raising.
  The default is an internal sentinel, so every value — `None`, `0`, `""` —
  is returned as given, and only omitting the argument raises
  `NotFoundError`.
- `filter(..., if_empty=None)` likewise returns `None` on an empty result;
  omitting `if_empty` still returns `[]`.
- `sort()` now raises `InvalidIndexError` when `by` is out of range for any
  row (ragged tables included), instead of a raw `IndexError` from the sort
  key. This matches `vlookup`/`hlookup`/`index`.

## 0.1.1 — 2026-08-07

**Fixes and corrections — no new functions.**

- Added a `py.typed` marker, so editors and type checkers now pick up the
  library's type hints (autocomplete, error checking).
- `index()` now raises a clear `ValueError` when `col_num` is passed for a
  flat list (it was silently ignored before).
- `sort()` now raises a clear `ValueError` when `by` is passed for a flat
  list (also silently ignored before).
- `xlookup()` now validates that `lookup_array` and `return_array` are the
  same length, raising `ValueError` instead of a confusing `IndexError`.
- `hlookup()` on a ragged table (rows with missing columns) now raises the
  library's own `InvalidIndexError` instead of a raw `IndexError`.
- `xlookup()` now rejects invalid `search_mode` values with `ValueError`.
- Documented that `exact=False` in `vlookup()`/`hlookup()` requires the
  first column/row to be sorted ascending.

## 0.1.0 — 2026-08-07

**Initial release.**

- Lookup functions: `xlookup`, `vlookup`, `hlookup`, `index`, `match`,
  `index_match`
- Filtering: `filter`, `unique`
- Sorting: `sort`
- Zero dependencies, full type hints, 1-based Excel-style positions.
