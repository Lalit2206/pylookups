# Changelog

All notable changes to pylookups are documented here.

## 0.1.2 — 2026-08-08 (current)

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
