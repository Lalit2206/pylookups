# pylookups

[![PyPI](https://img.shields.io/badge/PyPI-{{ version }}-3775A9?logo=pypi&logoColor=white)](https://pypi.org/project/pylookups/)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**Excel-style lookup, filter, and sort functions for plain Python lists — no pandas or numpy required.**

Current version: **[{{ version }}](changelog.md)** — click it to see what's
new, or grab it on [PyPI](https://pypi.org/project/pylookups/).

If you know Excel, you already know this library. `VLOOKUP`, `XLOOKUP`, `INDEX`, `MATCH`, `FILTER`, `UNIQUE`, `SORT` — all as simple Python functions that work on ordinary lists.

## Install

```bash
pip install pylookups
```

The install name is `pylookups`, but the import name is `pylookup`:

```python
from pylookup import vlookup, xlookup, match, index, index_match, filter, unique, sort
```

## Quick example

```python
from pylookup import vlookup, xlookup, sort

table = [
    ["id", "name", "score"],
    [1, "alice", 90],
    [2, "bob", 75],
    [3, "carol", 60],
]

vlookup(2, table, "name")                # "bob"    — by column name
vlookup(2, table, None)                  # [2, "bob", 75]  — the whole row
xlookup(3, [1, 2, 3], ["a", "b", "c"])   # "c"
sort(table, by="score", reverse=True)    # highest score first
```

## From file to answer

Load a real file and join two tables — still with nothing installed but pylookups:

```python
from pylookup import read_table, join, vlookup

orders = read_table("orders.csv")                      # or .xlsx, .json, .tsv
customers = read_table("customers.xlsx", sheet="Q1")

full = join(orders, customers, by="cust_id")
vlookup(103, full, ["name", "city"])                   # ["carol", "jaipur"]
```

## Why pylookups?

- **Zero dependencies** — pure Python, nothing else to install. Even the Excel and CSV readers are standard library.
- **Familiar names** — the exact functions you already use in Excel.
- **Excel conventions** — positions are 1-based, just like spreadsheet rows and columns.
- **Column names** — say `"score"` instead of counting to 3.
- **Typed** — full type hints, so your editor autocompletes everything.

## Where next?

- [Coming from Excel](excel.md) — Excel formula ↔ Python code, side by side.
- [Loading data](loading-data.md) — read CSV, Excel and JSON files into a table.
- [Function Reference](functions.md) — every function with examples.
- [Roadmap](roadmap.md) — how releases are numbered, and the latest fixes.
- [FAQ](faq.md) — common questions answered.
- [Support](support.md) — found a bug or have a question?
