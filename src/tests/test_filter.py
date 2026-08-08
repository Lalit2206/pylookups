from pylookup import filter, unique


def test_filter_with_predicate():
    assert filter([1, 2, 3, 4, 5], lambda x: x % 2 == 0) == [2, 4]


def test_filter_with_boolean_array():
    assert filter(["a", "b", "c"], [True, False, True]) == ["a", "c"]


def test_filter_if_empty():
    assert filter([1, 2, 3], lambda x: x > 10, if_empty="none") == "none"


def test_filter_if_empty_none():
    assert filter([1, 2, 3], lambda x: x > 10, if_empty=None) is None


def test_filter_no_if_empty_returns_empty_list():
    assert filter([1, 2, 3], lambda x: x > 10) == []


def test_unique_keeps_first_by_default():
    assert unique([1, 2, 2, 3, 1]) == [1, 2, 3]


def test_unique_keep_last():
    assert unique([1, 2, 2, 3, 1], keep="last") == [2, 3, 1]


def test_unique_with_rows():
    rows = [["a", 1], ["b", 2], ["a", 1]]
    assert unique(rows) == [["a", 1], ["b", 2]]
