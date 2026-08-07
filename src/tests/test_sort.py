import pytest

from pylookup import sort

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
