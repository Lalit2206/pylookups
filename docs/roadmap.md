# Roadmap

pylookups releases follow a simple sequential series: **0.1.1 → 0.1.2 →
0.1.3 → ...** Each release is small and focused.

Current version: **0.1.1** (see the [Changelog](changelog.md)).

## 0.1.2 — next release

### Conditional math: `sumif` / `countif` / `averageif`

Excel's conditional workhorses — sum, count, or average only the values
that match a condition:

```python
scores = [90, 75, 60, 85]

sumif(scores, lambda x: x > 70)       # 250
countif(scores, lambda x: x > 70)     # 3
averageif(scores, lambda x: x > 70)   # 83.33...
```

With a separate criteria range, like Excel's 3-argument form:

```python
regions = ["east", "west", "east"]
sales = [100, 200, 300]

sumif(regions, "east", sales)   # 400
```

### Multi-condition: `sumifs` / `countifs`

Multiple criteria at once:

```python
sumifs(sales, regions, "east", products, "tea")
countifs(regions, "east", products, "tea")
```

### `sortby`

Sort one list by the order of another (Excel SORTBY):

```python
sortby(names, scores, reverse=True)   # names, highest score first
```

### `transpose`

Flip rows and columns:

```python
transpose([[1, 2, 3], [4, 5, 6]])   # [[1, 4], [2, 5], [3, 6]]
```

### `take` / `drop`

First or last N rows of a table — negative N counts from the end, just
like Excel:

```python
take(table, 3)    # first 3 rows
take(table, -2)   # last 2 rows
drop(table, 1)    # everything except the first row (skip the header!)
```

### `vstack` / `hstack`

Stack tables on top of each other, or side by side:

```python
vstack(table_jan, table_feb)   # rows of both, combined
hstack(ids_col, names_col)     # columns joined into one table
```

## Have a suggestion?

Open an issue on
[GitHub](https://github.com/Lalit2206/pylookups/issues) — feature
requests are welcome, and they shape what lands in the next 0.1.x.
