import pytest

from pylookup import sort
from pylookup.exceptions import InvalidIndexError

TABLE = [
    [2, "bob"],
    [3, "carol"],
    [1, "alice"],
]


def test_sort_flat_ascending():
    assert sort([3, 1, 2]) == [1, 2, 3]


def test_sort_flat_descending():
    assert sort([3, 1, 2], reverse=True) == [3, 2, 1]


def test_sort_table_by_column():
    assert sort(TABLE, by=1) == [[1, "alice"], [2, "bob"], [3, "carol"]]


def test_sort_with_custom_key():
    words = ["banana", "fig", "kiwi"]
    assert sort(words, key=len) == ["fig", "kiwi", "banana"]


def test_sort_flat_with_by_raises():
    with pytest.raises(ValueError):
        sort([3, 1, 2], by=2)


def test_sort_by_out_of_range_raises():
    with pytest.raises(InvalidIndexError):
        sort(TABLE, by=5)


def test_sort_by_column_name_keeps_header_on_top():
    table = [["id", "name"], [2, "bob"], [1, "alice"]]
    assert sort(table, by="id") == [["id", "name"], [1, "alice"], [2, "bob"]]


def test_sort_by_column_name_reverse():
    table = [["id", "name"], [1, "alice"], [2, "bob"]]
    assert sort(table, by="name", reverse=True)[1] == [2, "bob"]


def test_sort_unknown_column_name_raises():
    table = [["id", "name"], [1, "alice"]]
    with pytest.raises(InvalidIndexError):
        sort(table, by="score")


def test_sort_ragged_table_raises():
    ragged = [[2, "bob"], [3]]
    with pytest.raises(InvalidIndexError):
        sort(ragged, by=2)
