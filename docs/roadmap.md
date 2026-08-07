# Roadmap

pylookups releases follow a simple sequential series: **0.1.1 → 0.1.2 →
0.1.3 → ...** Each release is small and focused.

Current version: **0.1.1** (see the [Changelog](changelog.md)).

## 0.1.2 — next release: completing the lookup family

Three new functions, all cousins of the ones already here:

### `xmatch()`
The modern version of `match` — same relationship as `xlookup` has to
`vlookup`. Returns a position with flexible matching:

```python
xmatch(7, [1, 5, 10], match_mode=-1)   # 2  (next smaller: 5)
xmatch(2, [1, 2, 2, 3], search_mode=-1)  # 3  (search from the end)
```

### `lookup()`
Excel's classic LOOKUP: search one list, return from another. Always
approximate-match on sorted data — the old-school workhorse:

```python
lookup(6, [1, 3, 5, 9], ["a", "b", "c", "d"])   # "c"
```

### `choose()`
Pick a value by its 1-based position:

```python
choose(2, "red", "green", "blue")   # "green"
```

## 0.1.3 — table slicing

- `chooserows(table, 1, 3)` / `choosecols(table, 1, 3)` — pick specific rows or columns
- `take(table, 3)` / `drop(table, 3)` — first/last N rows, or skip them
- `transpose(table)` — flip rows and columns

## 0.1.4 — sorting upgrades

- `sortby(array, by_array)` — sort one list by the order of another (Excel SORTBY)
- Multi-level sort: `sort(table, by=[2, 1])`

## Future 0.1.x ideas (order not decided yet)

- `sumif` / `countif` / `averageif` — the conditional math family
- Column **names** instead of numbers: `vlookup(2, table, "score")`
- Wildcard matching: `xlookup("al*", names, scores)`
- CSV helper: look up directly from a `.csv` file
- List-of-dicts support: `[{"id": 1, "name": "alice"}, ...]`

## Have a suggestion?

Open an issue on
[GitHub](https://github.com/Lalit2206/pylookups/issues) — feature
requests are welcome, and they shape what lands in the next 0.1.x.
