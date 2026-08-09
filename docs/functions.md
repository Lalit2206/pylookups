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
        if_not_found=..., match_mode=0, search_mode=1)
```

Search `lookup_array` for `lookup_value` and return the item at the same
position in `return_array`. Both arrays must be the same length.

| Parameter | Values |
|---|---|
| `match_mode` | `0` exact · `-1` exact or next smaller · `1` exact or next larger |
| `search_mode` | `1` first-to-last · `-1` last-to-first |
| `if_not_found` | returned instead of raising `NotFoundError`; omit it to get the exception |

**Basic lookup** — find an id, get the name:

```python
ids = [1, 2, 3]
names = ["alice", "bob", "carol"]

xlookup(2, ids, names)        # "bob"
xlookup(3, ids, names)        # "carol"
```

**Reverse direction too** — find a name, get the id:

```python
xlookup("bob", names, ids)    # 2
```

**Missing value with a default** — no try/except needed:

```python
xlookup(99, ids, names, if_not_found="n/a")   # "n/a"
xlookup(99, ids, names, if_not_found=None)    # None
xlookup(99, ids, names)                       # raises NotFoundError
```

Any value is accepted as `if_not_found` — `None`, `0`, and `""` all come
back as-is. Only omitting the argument produces the exception.

**Approximate match** — great for ranges like tax brackets or grades:

```python
cutoffs = [0, 60, 75, 90]
grades = ["F", "C", "B", "A"]

xlookup(82, cutoffs, grades, match_mode=-1)   # "B"  (next smaller: 75)
xlookup(60, cutoffs, grades, match_mode=-1)   # "C"  (exact hit)
xlookup(82, cutoffs, grades, match_mode=1)    # "A"  (next larger: 90)
```

**Search from the end** — when duplicates exist and you want the last one:

```python
codes = ["x", "y", "x"]
values = [10, 20, 30]

xlookup("x", codes, values)                   # 10  (first "x")
xlookup("x", codes, values, search_mode=-1)   # 30  (last "x")
```

---

## vlookup

```python
vlookup(lookup_value, table, col_index=None, exact=True, if_not_found=...)
```

Search the **first column** of `table` for `lookup_value`, then return
something from the matching row.

**Basic lookup** — find id 2, get values from its row:

```python
vlookup(2, table, 2)   # "bob"   (column 2 = name)
vlookup(2, table, 3)   # 75      (column 3 = score)
vlookup(1, table, 1)   # 1       (column 1 = the id itself)
```

**Use column names instead of counting columns:**

```python
vlookup(2, table, "name")     # "bob"
vlookup(2, table, "Score")    # 75    — matching ignores case
```

Naming a column means the first row is treated as a header: it supplies the
names and is left out of the search.

**Get several columns, or the whole row:**

```python
vlookup(2, table, ["name", "score"])   # ["bob", 75]
vlookup(2, table, ["name", 3])         # ["bob", 75]  — mix names and numbers
vlookup(2, table, None)                # [2, "bob", 75]  — the entire row
```

**Handling a missing value** — either catch it, or ask for a default:

```python
vlookup(99, table, "name", if_not_found="—")   # "—"

from pylookup.exceptions import NotFoundError

try:
    vlookup(99, table, 2)      # no if_not_found given
except NotFoundError:
    print("id 99 does not exist")
```

!!! tip "Looking up a whole table at once"
    `vlookup` answers one question at a time. To attach a second table's
    columns to *every* row — Excel's "drag the formula down" — use
    [join](#join).

**Approximate match** — commission slabs, price tiers, grade bands:

```python
slabs = [
    [0, "0%"],
    [10000, "5%"],
    [50000, "10%"],
]

vlookup(30000, slabs, 2, exact=False)   # "5%"  (largest value <= 30000 is 10000)
vlookup(50000, slabs, 2, exact=False)   # "10%" (exact hit)
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

Use it when your data runs sideways — headers in the first **row**,
records in **columns**:

```python
h_table = [
    ["id", 1, 2, 3],
    ["name", "alice", "bob", "carol"],
    ["score", 90, 75, 60],
]

hlookup(2, h_table, 2)   # "bob"  (row 2 = name)
hlookup(2, h_table, 3)   # 75     (row 3 = score)
hlookup(3, h_table, 2)   # "carol"
```

Approximate match works the same way as `vlookup` — pass `exact=False`
with the first row sorted ascending:

```python
month_table = [
    [1, 4, 7, 10],
    ["Q1", "Q2", "Q3", "Q4"],
]

hlookup(8, month_table, 2, exact=False)   # "Q3"  (month 8 falls in the 7 slab)
```

---

## index

```python
index(array, row_num, col_num=None)
```

Value at a position. Flat list → pass only `row_num`. 2D table → pass
`col_num` too, or omit it to get the whole row.

**Flat list** — just a position:

```python
index(["a", "b", "c"], 2)   # "b"
index(["a", "b", "c"], 9)   # raises InvalidIndexError
```

**2D table** — row and column:

```python
index(table, 3, 2)   # "bob"  (row 3, column 2)
index(table, 2, 3)   # 90     (row 2, column 3)
```

**Whole row** — omit `col_num`:

```python
index(table, 3)      # [2, "bob", 75]
```

`index` is rarely used alone — its real power is together with `match`,
which is exactly what [`index_match`](#index_match) packages up for you.

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

**Exact match** (default) — works on unsorted data:

```python
match("carol", ["alice", "bob", "carol"])   # 3
match(75, [90, 75, 60])                     # 2
match("dave", ["alice", "bob"])             # raises NotFoundError
```

**Approximate on ascending data** — where does a value fall?

```python
match(6, [1, 3, 5, 9], match_type=1)    # 3  (5 is the largest value <= 6)
match(0.5, [1, 3, 5, 9], match_type=1)  # raises NotFoundError (nothing <= 0.5)
```

**Approximate on descending data:**

```python
match(6, [9, 7, 5, 3], match_type=-1)   # 2  (7 is the smallest value >= 6)
```

The position `match` returns feeds straight into `index` — or use
[`index_match`](#index_match) to do both in one call.

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
cities = ["delhi", "mumbai", "pune"]

index_match(scores, "bob", names)    # 75      (bob's score)
index_match(cities, "bob", names)    # "mumbai" (bob's city)
index_match(names, 90, scores)       # "alice"  (who scored 90?)
```

Unlike `vlookup`, the lookup column doesn't have to be first — you can
look up in *any* list and return from *any* other list, in any direction.
That's why Excel power users prefer INDEX+MATCH, and it's the same here.

Approximate matching works too, via `match_type`:

```python
cutoffs = [0, 60, 75, 90]
grades = ["F", "C", "B", "A"]

index_match(grades, 82, cutoffs, match_type=1)   # "B"
```

---

## filter

```python
filter(array, condition, if_empty=...)
```

Keep items where `condition` is true. `condition` is either a function or
a boolean list the same length as `array` (like Excel's include array).

```python
filter([1, 2, 3, 4, 5], lambda x: x % 2 == 0)    # [2, 4]
filter(["a", "b", "c"], [True, False, True])     # ["a", "c"]
filter([1, 2], lambda x: x > 10, if_empty="-")   # "-"
filter([1, 2], lambda x: x > 10)                 # []  (no if_empty given)
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
value; 2D tables sort by column `by`, given as a 1-based number or a column
name. `key` overrides both.

```python
sort([3, 1, 2])                        # [1, 2, 3]
sort(table[1:], by=3, reverse=True)    # rows by score, highest first
sort(table, by="score", reverse=True)  # same, header kept on top
sort(["banana", "fig"], key=len)       # ["fig", "banana"]
```

Naming a column means the first row is a header: it stays at the top and only
the rows under it move.

A `by` that is out of range for any row raises `InvalidIndexError`, the
same error the other column-based functions raise.

---

## join

```python
join(left, right, by, if_not_found=None)
```

Attach every column of `right` to the rows of `left` that match on a key —
"drag the VLOOKUP down the whole column", as one call. Both tables start with
a header row.

```python
orders = [["order_id", "cust_id", "amount"],
          [101, 2, 250],
          [102, 1, 90],
          [104, 9, 75]]

customers = [["cust_id", "name", "city"],
             [1, "alice", "delhi"],
             [2, "bob", "pune"]]

join(orders, customers, by="cust_id", if_not_found="—")
```

```python
[["order_id", "cust_id", "amount", "name", "city"],
 [101, 2, 250, "bob",   "pune"],
 [102, 1, 90,  "alice", "delhi"],
 [104, 9, 75,  "—",     "—"]]      # id 9 has no customer
```

| `by` | Meaning |
|---|---|
| `"cust_id"` | key column, named the same in both tables |
| `("id", "cust_id")` | different names on each side |
| `2` | a 1-based column number, used on **both** sides |

- Rows keep the order of `left`, and every one of them survives — an
  unmatched row is filled with `if_not_found` rather than dropped.
- When `right` holds the same key twice, the first of those rows wins, which
  is what dragging a VLOOKUP down does.
- The right table is indexed once up front, so a join stays fast on big
  inputs instead of rescanning for every row.
