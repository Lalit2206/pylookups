"""Load a table out of a file — CSV, TSV, JSON or Excel .xlsx.

Everything here uses the standard library only: no pandas, no polars, no
openpyxl. A "table" is what the rest of pylookups works on — a list of rows,
with the header as the first row — so anything read here can go straight into
vlookup, filter, sort or join.
"""

import csv
import datetime
import json
import re
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union
from xml.etree import ElementTree as ET

from .exceptions import SheetNotFoundError, UnsupportedFormatError

PathLike = Union[str, "Path"]
Table = List[List[Any]]

__all__ = [
    "read_table",
    "read_csv",
    "read_json",
    "read_excel",
    "sheet_names",
]


# --------------------------------------------------------------------------
# value conversion
# --------------------------------------------------------------------------

def _to_number(text: str) -> Any:
    """Turn a CSV field into an int/float where that is clearly what it is.

    Blank becomes None (an empty spreadsheet cell). Anything with a leading
    zero stays text, so ids, phone numbers and pin codes survive intact.
    """
    value = text.strip()
    if not value:
        return None

    digits = value[1:] if value[0] in "+-" else value
    if digits[:1] == "0" and digits not in ("0",) and not digits.startswith("0."):
        return text

    try:
        return int(value)
    except ValueError:
        pass
    try:
        number = float(value)
    except ValueError:
        return text
    # "nan"/"inf" are words a spreadsheet would have meant as text
    if number != number or number in (float("inf"), float("-inf")):
        return text
    return number


def _pad(rows: List[List[Any]]) -> Table:
    """Make every row the same length by filling short ones with None."""
    width = max((len(r) for r in rows), default=0)
    return [list(r) + [None] * (width - len(r)) for r in rows]


def _trim_blank_edges(rows: List[List[Any]]) -> List[List[Any]]:
    """Drop entirely empty rows from the start and end of a sheet."""
    def blank(row: Sequence[Any]) -> bool:
        return all(cell is None or cell == "" for cell in row)

    start, end = 0, len(rows)
    while start < end and blank(rows[start]):
        start += 1
    while end > start and blank(rows[end - 1]):
        end -= 1
    return rows[start:end]


# --------------------------------------------------------------------------
# CSV / TSV / delimited text
# --------------------------------------------------------------------------

def read_csv(
    path: PathLike,
    delimiter: Optional[str] = None,
    encoding: str = "utf-8-sig",
    convert: bool = True,
) -> Table:
    """Read a CSV, TSV or other delimited file into a table.

    delimiter is worked out from the file when you leave it as None, so commas,
    tabs and semicolons all just work. convert=False keeps every cell as text
    instead of turning number-like fields into int/float.

    The default encoding strips a UTF-8 BOM, which is what Excel writes when
    you "Save as CSV UTF-8".
    """
    text = Path(path).read_text(encoding=encoding, errors="replace")

    if delimiter is None:
        sample = text[:8192]
        try:
            delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
        except csv.Error:
            delimiter = "\t" if "\t" in sample.split("\n", 1)[0] else ","

    rows = list(csv.reader(text.splitlines(), delimiter=delimiter))
    if convert:
        rows = [[_to_number(cell) for cell in row] for row in rows]
    return _pad(rows)


# --------------------------------------------------------------------------
# JSON
# --------------------------------------------------------------------------

def read_json(path: PathLike, encoding: str = "utf-8") -> Table:
    """Read JSON into a table. Three common shapes are understood:

        [{"id": 1, "name": "alice"}, ...]     records  -> keys become the header
        [["id", "name"], [1, "alice"], ...]   rows     -> used as-is
        {"id": [1, 2], "name": ["a", "b"]}    columns  -> keys become the header
    """
    data = json.loads(Path(path).read_text(encoding=encoding))

    if isinstance(data, dict):
        if not data:
            return []
        if all(isinstance(v, list) for v in data.values()):
            header = list(data.keys())
            height = max((len(v) for v in data.values()), default=0)
            rows = [
                [data[name][i] if i < len(data[name]) else None for name in header]
                for i in range(height)
            ]
            return [header] + rows
        raise UnsupportedFormatError(
            "JSON object must map column names to lists of values"
        )

    if not isinstance(data, list):
        raise UnsupportedFormatError("JSON must hold a list of records or rows")
    if not data:
        return []

    if all(isinstance(item, dict) for item in data):
        header: List[Any] = []
        for record in data:
            for name in record:
                if name not in header:
                    header.append(name)
        rows = [[record.get(name) for name in header] for record in data]
        return [header] + rows

    if all(isinstance(item, (list, tuple)) for item in data):
        return _pad([list(item) for item in data])

    raise UnsupportedFormatError(
        "JSON list must hold either all objects (records) or all lists (rows)"
    )


# --------------------------------------------------------------------------
# Excel .xlsx / .xlsm
# --------------------------------------------------------------------------

_MAIN = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
_PKG = "{http://schemas.openxmlformats.org/package/2006/relationships}"

# Number formats Excel ships with that mean "this is a date or a time".
_DATE_STYLE_IDS = set(range(14, 23)) | set(range(27, 37)) | set(range(45, 48)) | set(
    range(50, 59)
)
_CELL_REF = re.compile(r"^([A-Z]+)")


def _column_number(ref: str) -> int:
    """'A' -> 1, 'B' -> 2, 'AA' -> 27."""
    letters = _CELL_REF.match(ref or "")
    if not letters:
        return 0
    number = 0
    for char in letters.group(1):
        number = number * 26 + (ord(char) - 64)
    return number


def _looks_like_a_date(format_code: str) -> bool:
    """True if a custom number format renders a date or a time."""
    cleaned = re.sub(r'"[^"]*"|\[[^\]]*\]|\\.', "", format_code)
    return any(char in cleaned for char in "ymdhs")


def _from_serial(serial: float, date1904: bool) -> Any:
    """Turn an Excel date serial into a date/datetime."""
    if date1904:
        base = datetime.datetime(1904, 1, 1)
    else:
        # Excel thinks 1900 was a leap year; before serial 61 the offset differs.
        base = datetime.datetime(1899, 12, 31 if serial < 61 else 30)
    try:
        moment = base + datetime.timedelta(days=float(serial))
    except OverflowError:
        return serial
    if moment.time() == datetime.time(0, 0):
        return moment.date()
    return moment


def _open_workbook(path: PathLike) -> zipfile.ZipFile:
    file = Path(path)
    try:
        return zipfile.ZipFile(file)
    except zipfile.BadZipFile:
        head = file.open("rb").read(8)
        if head.startswith(b"\xd0\xcf\x11\xe0"):
            raise UnsupportedFormatError(
                f"{file.name} is the old binary .xls format. Open it in Excel or "
                "LibreOffice and save as .xlsx or .csv, then read that."
            ) from None
        raise UnsupportedFormatError(f"{file.name} is not a readable .xlsx file") from None


def _shared_strings(book: zipfile.ZipFile) -> List[str]:
    if "xl/sharedStrings.xml" not in book.namelist():
        return []
    root = ET.fromstring(book.read("xl/sharedStrings.xml"))
    strings = []
    for item in root.findall(f"{_MAIN}si"):
        # Rich text splits one string across several <r><t> runs.
        strings.append("".join(node.text or "" for node in item.iter(f"{_MAIN}t")))
    return strings


def _date_styles(book: zipfile.ZipFile) -> List[bool]:
    """For each cell style, whether it formats its number as a date."""
    if "xl/styles.xml" not in book.namelist():
        return []
    root = ET.fromstring(book.read("xl/styles.xml"))

    custom: Dict[int, str] = {}
    for fmt in root.iter(f"{_MAIN}numFmt"):
        try:
            custom[int(fmt.get("numFmtId", "-1"))] = fmt.get("formatCode", "")
        except ValueError:
            continue

    styles = []
    container = root.find(f"{_MAIN}cellXfs")
    for xf in container.findall(f"{_MAIN}xf") if container is not None else []:
        try:
            fmt_id = int(xf.get("numFmtId", "0"))
        except ValueError:
            fmt_id = 0
        if fmt_id in _DATE_STYLE_IDS:
            styles.append(True)
        elif fmt_id in custom:
            styles.append(_looks_like_a_date(custom[fmt_id]))
        else:
            styles.append(False)
    return styles


def _sheet_paths(book: zipfile.ZipFile) -> List[tuple]:
    """[(sheet name, path inside the zip), ...] in workbook order."""
    root = ET.fromstring(book.read("xl/workbook.xml"))

    targets: Dict[str, str] = {}
    if "xl/_rels/workbook.xml.rels" in book.namelist():
        rels = ET.fromstring(book.read("xl/_rels/workbook.xml.rels"))
        for rel in rels.findall(f"{_PKG}Relationship"):
            target = rel.get("Target", "")
            if target.startswith("/"):
                target = target[1:]
            elif not target.startswith("xl/"):
                target = "xl/" + target.replace("../", "")
            targets[rel.get("Id", "")] = target

    sheets = []
    container = root.find(f"{_MAIN}sheets")
    for index, sheet in enumerate(
        container.findall(f"{_MAIN}sheet") if container is not None else [], start=1
    ):
        name = sheet.get("name", f"Sheet{index}")
        path = targets.get(sheet.get(f"{_REL}id", ""), f"xl/worksheets/sheet{index}.xml")
        sheets.append((name, path))
    return sheets


def sheet_names(path: PathLike) -> List[str]:
    """List the sheet names in an .xlsx workbook, in tab order."""
    with _open_workbook(path) as book:
        return [name for name, _ in _sheet_paths(book)]


def read_excel(path: PathLike, sheet: Union[int, str, None] = None) -> Table:
    """Read one sheet of an .xlsx/.xlsm workbook into a table.

    sheet is a sheet name, or a 1-based tab number; the first sheet is used
    when you leave it out. Formulas come back as their last saved result,
    which is what Excel shows on screen. Dates come back as date/datetime
    objects rather than raw serial numbers.

    The old binary .xls format is not supported — save it as .xlsx or .csv.
    """
    with _open_workbook(path) as book:
        sheets = _sheet_paths(book)
        if not sheets:
            raise SheetNotFoundError("this workbook has no sheets")

        if sheet is None:
            name, inner_path = sheets[0]
        elif isinstance(sheet, str):
            found = [s for s in sheets if s[0] == sheet]
            if not found:
                available = ", ".join(repr(s[0]) for s in sheets)
                raise SheetNotFoundError(
                    f"no sheet named {sheet!r} — this workbook has: {available}"
                )
            name, inner_path = found[0]
        else:
            if sheet < 1 or sheet > len(sheets):
                raise SheetNotFoundError(
                    f"sheet {sheet} is out of range — this workbook has {len(sheets)}"
                )
            name, inner_path = sheets[sheet - 1]

        if inner_path not in book.namelist():
            raise SheetNotFoundError(f"sheet {name!r} is missing from the file")

        strings = _shared_strings(book)
        date_styles = _date_styles(book)

        workbook_root = ET.fromstring(book.read("xl/workbook.xml"))
        properties = workbook_root.find(f"{_MAIN}workbookPr")
        date1904 = bool(properties is not None and properties.get("date1904") in ("1", "true"))

        root = ET.fromstring(book.read(inner_path))
        data = root.find(f"{_MAIN}sheetData")
        if data is None:
            return []

        rows: Dict[int, Dict[int, Any]] = {}
        for row_index, row in enumerate(data.findall(f"{_MAIN}row"), start=1):
            try:
                row_number = int(row.get("r", row_index))
            except ValueError:
                row_number = row_index
            cells: Dict[int, Any] = {}
            for cell_index, cell in enumerate(row.findall(f"{_MAIN}c"), start=1):
                column = _column_number(cell.get("r", "")) or cell_index
                cells[column] = _cell_value(cell, strings, date_styles, date1904)
            rows[row_number] = cells

    if not rows:
        return []

    height = max(rows)
    width = max((max(cells) for cells in rows.values() if cells), default=0)
    grid = [
        [rows.get(r, {}).get(c) for c in range(1, width + 1)]
        for r in range(1, height + 1)
    ]
    return _trim_blank_edges(grid)


def _cell_value(
    cell: ET.Element, strings: List[str], date_styles: List[bool], date1904: bool
) -> Any:
    kind = cell.get("t", "n")

    if kind == "inlineStr":
        node = cell.find(f"{_MAIN}is")
        return "".join(t.text or "" for t in node.iter(f"{_MAIN}t")) if node is not None else None

    raw = cell.find(f"{_MAIN}v")
    if raw is None or raw.text is None:
        return None
    text = raw.text

    if kind == "s":
        try:
            return strings[int(text)]
        except (ValueError, IndexError):
            return text
    if kind in ("str", "e"):
        return text
    if kind == "b":
        return text == "1"

    try:
        number = float(text)
    except ValueError:
        return text

    try:
        style = int(cell.get("s", "-1"))
    except ValueError:
        style = -1
    if 0 <= style < len(date_styles) and date_styles[style]:
        return _from_serial(number, date1904)

    return int(number) if number.is_integer() else number


# --------------------------------------------------------------------------
# one entry point for every format
# --------------------------------------------------------------------------

_READERS = {
    ".csv": read_csv,
    ".tsv": read_csv,
    ".txt": read_csv,
    ".json": read_json,
    ".xlsx": read_excel,
    ".xlsm": read_excel,
    ".xltx": read_excel,
}


def read_table(path: PathLike, **options: Any) -> Table:
    """Read any supported file into a table, picked by its extension.

        read_table("sales.csv")
        read_table("sales.xlsx", sheet="Q1")
        read_table("sales.json")

    Extra keyword arguments go through to the matching reader, so
    `delimiter`, `encoding`, `convert` and `sheet` all work here.
    """
    suffix = Path(path).suffix.lower()
    reader = _READERS.get(suffix)
    if reader is None:
        supported = ", ".join(sorted(_READERS))
        if suffix == ".xls":
            raise UnsupportedFormatError(
                ".xls is the old binary Excel format. Save it as .xlsx or .csv "
                "and read that instead."
            )
        raise UnsupportedFormatError(
            f"don't know how to read {suffix or 'a file with no extension'} — "
            f"supported: {supported}"
        )
    return reader(path, **options)
