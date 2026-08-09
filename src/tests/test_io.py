import datetime
import json
import zipfile

import pytest

from pylookup import read_csv, read_excel, read_json, read_table, sheet_names
from pylookup.exceptions import SheetNotFoundError, UnsupportedFormatError

# --------------------------------------------------------------------------
# a real .xlsx, built with the standard library so no binary fixture is needed
# --------------------------------------------------------------------------

WORKBOOK = """<?xml version="1.0"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
 <sheets>
  <sheet name="Data" sheetId="1" r:id="rId1"/>
  <sheet name="Extra" sheetId="2" r:id="rId2"/>
 </sheets>
</workbook>"""

RELS = """<?xml version="1.0"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1" Target="worksheets/sheet1.xml"/>
 <Relationship Id="rId2" Target="worksheets/sheet2.xml"/>
</Relationships>"""

STYLES = """<?xml version="1.0"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
 <numFmts count="1"><numFmt numFmtId="164" formatCode="dd/mm/yyyy"/></numFmts>
 <cellXfs count="3">
  <xf numFmtId="0"/>
  <xf numFmtId="14" applyNumberFormat="1"/>
  <xf numFmtId="164" applyNumberFormat="1"/>
 </cellXfs>
</styleSheet>"""

SHARED = """<?xml version="1.0"?>
<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="5">
 <si><t>id</t></si>
 <si><t>name</t></si>
 <si><t>joined</t></si>
 <si><t>alice</t></si>
 <si><r><t>bo</t></r><r><t>b</t></r></si>
</sst>"""

# Row 3 is deliberately sparse (no B cell) and row 5 is blank padding at the end.
SHEET1 = """<?xml version="1.0"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
 <sheetData>
  <row r="1">
   <c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c><c r="C1" t="s"><v>2</v></c>
  </row>
  <row r="2">
   <c r="A2"><v>1</v></c><c r="B2" t="s"><v>3</v></c>
   <c r="C2" s="1"><v>44927</v></c>
  </row>
  <row r="3">
   <c r="A3"><v>2</v></c><c r="C3" s="2"><v>45870</v></c>
  </row>
  <row r="4">
   <c r="A4"><v>3.5</v></c>
   <c r="B4" t="inlineStr"><is><t>carol</t></is></c>
   <c r="C4" t="b"><v>1</v></c>
  </row>
  <row r="6">
   <c r="A6" t="str"><v>=CONCAT()</v></c><c r="B6" t="e"><v>#N/A</v></c>
   <c r="C6" t="s"><v>4</v></c>
  </row>
 </sheetData>
</worksheet>"""

SHEET2 = """<?xml version="1.0"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
 <sheetData>
  <row r="1"><c r="A1" t="inlineStr"><is><t>only</t></is></c></row>
  <row r="2"><c r="A2"><v>42</v></c></row>
 </sheetData>
</worksheet>"""


@pytest.fixture
def workbook(tmp_path):
    path = tmp_path / "book.xlsx"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("xl/workbook.xml", WORKBOOK)
        zf.writestr("xl/_rels/workbook.xml.rels", RELS)
        zf.writestr("xl/styles.xml", STYLES)
        zf.writestr("xl/sharedStrings.xml", SHARED)
        zf.writestr("xl/worksheets/sheet1.xml", SHEET1)
        zf.writestr("xl/worksheets/sheet2.xml", SHEET2)
    return path


# --------------------------------------------------------------------------
# CSV
# --------------------------------------------------------------------------

def test_read_csv_basic(tmp_path):
    path = tmp_path / "t.csv"
    path.write_text("id,name,score\n1,alice,90\n2,bob,75\n")
    assert read_csv(path) == [
        ["id", "name", "score"],
        [1, "alice", 90],
        [2, "bob", 75],
    ]


def test_read_csv_sniffs_tabs(tmp_path):
    path = tmp_path / "t.tsv"
    path.write_text("id\tname\n1\talice\n")
    assert read_csv(path) == [["id", "name"], [1, "alice"]]


def test_read_csv_sniffs_semicolons(tmp_path):
    path = tmp_path / "t.csv"
    path.write_text("id;name\n1;alice\n")
    assert read_csv(path) == [["id", "name"], [1, "alice"]]


def test_read_csv_keeps_leading_zeros(tmp_path):
    path = tmp_path / "t.csv"
    path.write_text("code,qty\n007,2\n0,3\n")
    assert read_csv(path) == [["code", "qty"], ["007", 2], [0, 3]]


def test_read_csv_blank_becomes_none(tmp_path):
    path = tmp_path / "t.csv"
    path.write_text("a,b\n1,\n")
    assert read_csv(path) == [["a", "b"], [1, None]]


def test_read_csv_floats_and_negatives(tmp_path):
    path = tmp_path / "t.csv"
    path.write_text("a,b\n-2,3.5\n")
    assert read_csv(path) == [["a", "b"], [-2, 3.5]]


def test_read_csv_without_conversion(tmp_path):
    path = tmp_path / "t.csv"
    path.write_text("a,b\n1,2\n")
    assert read_csv(path, convert=False) == [["a", "b"], ["1", "2"]]


def test_read_csv_strips_excel_bom(tmp_path):
    path = tmp_path / "t.csv"
    path.write_bytes("﻿id,name\n1,alice\n".encode("utf-8"))
    assert read_csv(path)[0] == ["id", "name"]


def test_read_csv_pads_short_rows(tmp_path):
    path = tmp_path / "t.csv"
    path.write_text("a,b,c\n1\n")
    assert read_csv(path) == [["a", "b", "c"], [1, None, None]]


# --------------------------------------------------------------------------
# JSON
# --------------------------------------------------------------------------

def test_read_json_records(tmp_path):
    path = tmp_path / "t.json"
    path.write_text(json.dumps([{"id": 1, "name": "alice"}, {"id": 2, "name": "bob"}]))
    assert read_json(path) == [["id", "name"], [1, "alice"], [2, "bob"]]


def test_read_json_records_with_missing_keys(tmp_path):
    path = tmp_path / "t.json"
    path.write_text(json.dumps([{"id": 1}, {"id": 2, "city": "pune"}]))
    assert read_json(path) == [["id", "city"], [1, None], [2, "pune"]]


def test_read_json_rows(tmp_path):
    path = tmp_path / "t.json"
    path.write_text(json.dumps([["id", "name"], [1, "alice"]]))
    assert read_json(path) == [["id", "name"], [1, "alice"]]


def test_read_json_columns(tmp_path):
    path = tmp_path / "t.json"
    path.write_text(json.dumps({"id": [1, 2], "name": ["alice", "bob"]}))
    assert read_json(path) == [["id", "name"], [1, "alice"], [2, "bob"]]


def test_read_json_empty_list(tmp_path):
    path = tmp_path / "t.json"
    path.write_text("[]")
    assert read_json(path) == []


def test_read_json_mixed_shape_raises(tmp_path):
    path = tmp_path / "t.json"
    path.write_text(json.dumps([{"id": 1}, [2]]))
    with pytest.raises(UnsupportedFormatError):
        read_json(path)


# --------------------------------------------------------------------------
# Excel
# --------------------------------------------------------------------------

def test_read_excel_header_and_shared_strings(workbook):
    table = read_excel(workbook)
    assert table[0] == ["id", "name", "joined"]
    assert table[1][:2] == [1, "alice"]


def test_read_excel_joins_rich_text_runs(workbook):
    # cell C6 points at a shared string stored as two runs: <r><t>bo</t></r><r><t>b</t></r>
    assert read_excel(workbook)[5][2] == "bob"


def test_read_excel_builtin_date_format(workbook):
    assert read_excel(workbook)[1][2] == datetime.date(2023, 1, 1)


def test_read_excel_custom_date_format(workbook):
    assert read_excel(workbook)[2][2] == datetime.date(2025, 8, 1)


def test_read_excel_sparse_row_fills_none(workbook):
    assert read_excel(workbook)[2] == [2, None, datetime.date(2025, 8, 1)]


def test_read_excel_types(workbook):
    row = read_excel(workbook)[3]
    assert row == [3.5, "carol", True]


def test_read_excel_formula_and_error_cells(workbook):
    # row 5 is empty, so the formula row lands at index 4 of the grid
    assert read_excel(workbook)[5] == ["=CONCAT()", "#N/A", "bob"]


def test_read_excel_by_sheet_name(workbook):
    assert read_excel(workbook, sheet="Extra") == [["only"], [42]]


def test_read_excel_by_sheet_number(workbook):
    assert read_excel(workbook, sheet=2) == [["only"], [42]]


def test_read_excel_unknown_sheet_name(workbook):
    with pytest.raises(SheetNotFoundError):
        read_excel(workbook, sheet="Nope")


def test_read_excel_sheet_number_out_of_range(workbook):
    with pytest.raises(SheetNotFoundError):
        read_excel(workbook, sheet=9)


def test_sheet_names(workbook):
    assert sheet_names(workbook) == ["Data", "Extra"]


def test_read_excel_rejects_old_xls(tmp_path):
    path = tmp_path / "old.xls"
    path.write_bytes(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1padding")
    with pytest.raises(UnsupportedFormatError, match="save as .xlsx"):
        read_excel(path)


def test_read_excel_rejects_junk(tmp_path):
    path = tmp_path / "junk.xlsx"
    path.write_bytes(b"not a zip at all")
    with pytest.raises(UnsupportedFormatError):
        read_excel(path)


# --------------------------------------------------------------------------
# read_table dispatch
# --------------------------------------------------------------------------

def test_read_table_csv(tmp_path):
    path = tmp_path / "t.csv"
    path.write_text("a,b\n1,2\n")
    assert read_table(path) == [["a", "b"], [1, 2]]


def test_read_table_json(tmp_path):
    path = tmp_path / "t.json"
    path.write_text(json.dumps([{"a": 1}]))
    assert read_table(path) == [["a"], [1]]


def test_read_table_excel_passes_options(workbook):
    assert read_table(workbook, sheet="Extra") == [["only"], [42]]


def test_read_table_xls_points_at_conversion(tmp_path):
    path = tmp_path / "old.xls"
    path.write_bytes(b"anything")
    with pytest.raises(UnsupportedFormatError, match="Save it as"):
        read_table(path)


def test_read_table_unknown_extension(tmp_path):
    path = tmp_path / "t.parquet"
    path.write_bytes(b"")
    with pytest.raises(UnsupportedFormatError):
        read_table(path)
