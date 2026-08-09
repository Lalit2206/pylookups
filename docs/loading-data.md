# Loading data

Your data usually starts life in a file — a CSV export, an Excel sheet, an API
response saved as JSON. These readers turn any of those into the same plain
list of rows the rest of pylookups works on.

Everything here uses the Python standard library. **No pandas, no polars, no
openpyxl** — installing pylookups installs nothing else.

## read_table

One function for every supported format; the file extension picks the reader.

```python
from pylookup import read_table

table = read_table("sales.csv")
table = read_table("sales.xlsx", sheet="Q1")
table = read_table("sales.json")
```

| Extension | Read by |
|---|---|
| `.csv` `.tsv` `.txt` | [read_csv](#read_csv) |
| `.json` | [read_json](#read_json) |
| `.xlsx` `.xlsm` `.xltx` | [read_excel](#read_excel) |

What you get back is a **list of rows, header first** — exactly the shape
`vlookup`, `filter`, `sort` and `join` expect:

```python
[["order_id", "cust_id", "amount"],
 [101, 2, 250],
 [102, 1, 90]]
```

Any extra arguments are passed to the reader underneath, so
`read_table("f.csv", delimiter=";")` and `read_table("f.xlsx", sheet=2)` both
work.

---

## read_csv

```python
read_csv(path, delimiter=None, encoding="utf-8-sig", convert=True)
```

```python
read_csv("sales.csv")
read_csv("export.tsv")                 # tabs detected on their own
read_csv("euro.csv", delimiter=";")    # or say it outright
```

- **The delimiter is detected for you** — commas, semicolons, tabs and pipes.
- **Numbers become numbers.** `"90"` reads as `90`, not `"90"`, so
  `vlookup(2, table, ...)` matches without you converting anything first.
- **Ids keep their leading zeros.** `007` and `0561` stay text, because losing
  those digits silently corrupts pin codes, phone numbers and product ids.
- **Empty cells become `None`**, the same as a blank cell in a spreadsheet.
- **Excel's "CSV UTF-8" works as-is** — the byte-order mark it writes is
  stripped, so your first column heading isn't `﻿id`.

Pass `convert=False` to switch all of that off and get every cell as text.

---

## read_excel

```python
read_excel(path, sheet=None)
```

```python
read_excel("report.xlsx")              # first sheet
read_excel("report.xlsx", sheet="Q1")  # by tab name
read_excel("report.xlsx", sheet=2)     # by tab number, 1-based
```

Reads `.xlsx` / `.xlsm` straight out of the file — an xlsx is a zip of XML,
which `zipfile` and `xml.etree` in the standard library handle fine.

- **Dates come back as `date`/`datetime` objects**, not the raw serial numbers
  Excel stores. Both built-in and custom date formats are recognised.
- **Formulas come back as their last saved result** — the value Excel was
  showing on screen. Nothing is recalculated.
- **Blank rows and columns around your data are trimmed** from the edges.
- Booleans read as `True`/`False`, and error cells as their text (`"#N/A"`).

List the tabs before deciding:

```python
from pylookup import sheet_names

sheet_names("report.xlsx")     # ["Q1", "Q2", "Summary"]
```

!!! warning "The old `.xls` format is not supported"
    `.xls` is a completely different binary format from before 2007. Open it
    in Excel or LibreOffice and save as `.xlsx` or `.csv`. pylookups tells you
    this rather than failing with a confusing error.

---

## read_json

```python
read_json(path, encoding="utf-8")
```

Three common shapes are understood:

```python
# records — the usual API response; keys become the header
[{"id": 1, "name": "alice"}, {"id": 2, "name": "bob"}]

# rows — used as they are
[["id", "name"], [1, "alice"], [2, "bob"]]

# columns — keys become the header
{"id": [1, 2], "name": ["alice", "bob"]}
```

All three read into the same table:

```python
[["id", "name"], [1, "alice"], [2, "bob"]]
```

Records with different keys are fine — every key that appears anywhere becomes
a column, and rows missing it get `None`.

---

## Putting it together

Load two files, join them, then look things up by name:

```python
from pylookup import read_table, join, vlookup, sort

orders = read_table("orders.csv")
customers = read_table("customers.xlsx", sheet="Master")

full = join(orders, customers, by="cust_id", if_not_found="unknown")

vlookup(103, full, ["name", "city"])     # ["carol", "jaipur"]
sort(full, by="amount", reverse=True)    # biggest order first
```

No dataframes, no dependencies — just lists.
