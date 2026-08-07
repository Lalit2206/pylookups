import pytest

from pylookup import hlookup, index, index_match, match, vlookup, xlookup
from pylookup.exceptions import InvalidIndexError, NotFoundError

TABLE = [
    ["id", "name", "score"],
    [1, "alice", 90],
    [2, "bob", 75],
    [3, "carol", 60],
]

H_TABLE = [
    ["id", 1, 2, 3],
    ["name", "alice", "bob", "carol"],
    ["score", 90, 75, 60],
]


def test_match_exact():
    assert match("carol", ["alice", "bob", "carol"]) == 3


def test_match_exact_not_found():
    with pytest.raises(NotFoundError):
        match("dave", ["alice", "bob", "carol"])


def test_match_ascending():
    assert match(6, [1, 3, 5, 9], match_type=1) == 3


def test_match_descending():
    assert match(6, [9, 7, 5, 3], match_type=-1) == 2


def test_index_flat():
    assert index(["a", "b", "c"], 2) == "b"


def test_index_table_cell():
    assert index(TABLE, 3, 2) == "bob"


def test_index_table_row():
    assert index(TABLE, 3) == [2, "bob", 75]


def test_index_out_of_range():
    with pytest.raises(InvalidIndexError):
        index(["a", "b"], 5)


def test_index_match():
    names = ["alice", "bob", "carol"]
    scores = [90, 75, 60]
    assert index_match(scores, "bob", names) == 75


def test_vlookup_exact():
    assert vlookup(2, TABLE, 2) == "bob"


def test_vlookup_not_found():
    with pytest.raises(NotFoundError):
        vlookup(99, TABLE, 2)


def test_hlookup_exact():
    assert hlookup(2, H_TABLE, 2) == "bob"


def test_xlookup_exact():
    ids = [1, 2, 3]
    names = ["alice", "bob", "carol"]
    assert xlookup(2, ids, names) == "bob"


def test_xlookup_if_not_found():
    ids = [1, 2, 3]
    names = ["alice", "bob", "carol"]
    assert xlookup(99, ids, names, if_not_found="n/a") == "n/a"


def test_xlookup_raises_when_missing():
    ids = [1, 2, 3]
    names = ["alice", "bob", "carol"]
    with pytest.raises(NotFoundError):
        xlookup(99, ids, names)


def test_xlookup_approximate_next_smaller():
    ids = [1, 5, 10]
    names = ["alice", "bob", "carol"]
    assert xlookup(7, ids, names, match_mode=-1) == "bob"


def test_xlookup_approximate_next_larger():
    ids = [1, 5, 10]
    names = ["alice", "bob", "carol"]
    assert xlookup(7, ids, names, match_mode=1) == "carol"
