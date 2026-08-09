# FAQ

## Why is it `pip install pylookups` but `import pylookup`?

The name `pylookup` (without the "s") was already taken on PyPI by an
unrelated package — and PyPI names are case-insensitive, so `PyLookup`
and `pylookup` count as the same name. The install name became
`pylookups`, while the import stays the natural `pylookup`. This
install-name ≠ import-name pattern is common in Python (for example,
`pip install beautifulsoup4` → `import bs4`).

## Why are positions 1-based instead of 0-based?

Because Excel is 1-based, and this library exists for people who think in
Excel. `vlookup(2, table, 2)` means "second column" — the same thing it
means in a spreadsheet. Mixing Excel-style function names with 0-based
Python indexing would be the worst of both worlds.

## Doesn't `filter` clash with Python's built-in `filter`?

Only if you import it by name — `from pylookup import filter` shadows the
built-in *in that one file*. Nothing global changes. If you need both,
use the namespaced style:

```python
import pylookup as pl

pl.filter([1, 2, 3, 4], lambda x: x > 2)   # pylookup's filter
filter(lambda x: x > 2, [1, 2, 3, 4])      # Python's built-in
```

## Do I need pandas or numpy?

No. pylookups has **zero dependencies** — it works on plain Python lists.
That's the point: quick Excel-style operations without pulling in a data
science stack.

## Which Python versions are supported?

Python 3.9 and newer.

## Why does `vlookup(..., exact=False)` give wrong results?

Approximate match requires **sorted data** — the first column must be
sorted ascending, exactly like in Excel. With unsorted data, use the
default `exact=True`.

## Can I look up by column name instead of number?

Yes, since 0.1.3 — `vlookup`, `hlookup`, `sort` and `join` all take a column
name wherever they take a column number:

```python
vlookup(2, table, "score")
sort(table, by="score", reverse=True)
```

Using a name means the first row is treated as a header. Matching ignores
case, so `"Score"` finds a `score` heading.

## A value isn't found — why the error instead of `#N/A`?

Python surfaces problems as exceptions (`NotFoundError`), not silent
error values. If you'd rather get a default back, `xlookup` has
`if_not_found`:

```python
xlookup(99, ids, names, if_not_found="n/a")   # no exception
```

## Something else?

Ask on [GitHub issues](https://github.com/Lalit2206/pylookups/issues) —
see the [Support](support.md) page.
