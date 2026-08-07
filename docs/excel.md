# Coming from Excel

If you know Excel formulas, you already know pylookups. This page maps
each Excel formula to its pylookup equivalent.

Imagine this spreadsheet data as a Python table:

| | A | B | C |
|---|---|---|---|
| **1** | id | name | score |
| **2** | 1 | alice | 90 |
| **3** | 2 | bob | 75 |
| **4** | 3 | carol | 60 |

```python
table = [
    ["id", "name", "score"],
    [1, "alice", 90],
    [2, "bob", 75],
    [3, "carol", 60],
]

ids    = [1, 2, 3]
names  = ["alice", "bob", "carol"]
scores = [90, 75, 60]
```

## Formula translation table

| Excel formula | pylookup code |
|---|---|
| `=XLOOKUP(2, A:A, B:B)` | `xlookup(2, ids, names)` |
| `=XLOOKUP(9, A:A, B:B, "n/a")` | `xlookup(9, ids, names, if_not_found="n/a")` |
| `=VLOOKUP(2, A2:C4, 2, FALSE)` | `vlookup(2, table, 2)` |
| `=VLOOKUP(2, A2:C4, 2, TRUE)` | `vlookup(2, table, 2, exact=False)` |
| `=HLOOKUP(2, A1:D3, 2, FALSE)` | `hlookup(2, h_table, 2)` |
| `=INDEX(A2:C4, 3, 2)` | `index(table_rows, 3, 2)` |
| `=MATCH("bob", B:B, 0)` | `match("bob", names)` |
| `=INDEX(C:C, MATCH("bob", B:B, 0))` | `index_match(scores, "bob", names)` |
| `=FILTER(B2:B4, C2:C4>70)` | `filter(names, [s > 70 for s in scores])` |
| `=FILTER(B2:B4, C2:C4>99, "none")` | `filter(names, [s > 99 for s in scores], if_empty="none")` |
| `=UNIQUE(A2:A10)` | `unique(items)` |
| `=SORT(A2:C4, 3, -1)` | `sort(table[1:], by=3, reverse=True)` |

## Key differences from Excel

**No cell references.** Excel formulas point at ranges (`A2:C4`); in Python
you pass the data itself — a list, or a list of rows.

**Positions are still 1-based.** `col_index=2` means the second column,
exactly like Excel. No confusing 0-based counting.

**Errors are exceptions, not `#N/A`.** Where Excel shows `#N/A`, pylookup
raises `NotFoundError`; where Excel shows `#REF!`, pylookup raises
`InvalidIndexError`. You can handle them the Python way:

```python
from pylookup import vlookup
from pylookup.exceptions import NotFoundError

try:
    result = vlookup(99, table, 2)
except NotFoundError:
    result = "not found"
```

Or, with `xlookup`, skip try/except entirely — just like Excel's
`if_not_found` argument:

```python
xlookup(99, ids, names, if_not_found="not found")
```

**`filter` conditions are Python expressions.** Excel's `C2:C4>70`
becomes a list comprehension `[s > 70 for s in scores]` or a function
`lambda s: s > 70` — whichever you find more readable.
