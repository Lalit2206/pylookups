import pytest

from pylookup import join
from pylookup.exceptions import InvalidIndexError

ORDERS = [
    ["order_id", "cust_id", "amount"],
    [101, 2, 250],
    [102, 1, 90],
    [103, 3, 400],
]

CUSTOMERS = [
    ["cust_id", "name", "city"],
    [1, "alice", "delhi"],
    [2, "bob", "pune"],
    [3, "carol", "jaipur"],
]


def test_join_by_shared_column_name():
    assert join(ORDERS, CUSTOMERS, by="cust_id") == [
        ["order_id", "cust_id", "amount", "name", "city"],
        [101, 2, 250, "bob", "pune"],
        [102, 1, 90, "alice", "delhi"],
        [103, 3, 400, "carol", "jaipur"],
    ]


def test_join_keeps_left_row_order():
    result = join(ORDERS, CUSTOMERS, by="cust_id")
    assert [row[0] for row in result[1:]] == [101, 102, 103]


def test_join_unmatched_row_gets_if_not_found():
    orders = ORDERS + [[104, 9, 75]]
    assert join(orders, CUSTOMERS, by="cust_id", if_not_found="—")[-1] == [
        104, 9, 75, "—", "—",
    ]


def test_join_unmatched_defaults_to_none():
    orders = ORDERS + [[104, 9, 75]]
    assert join(orders, CUSTOMERS, by="cust_id")[-1] == [104, 9, 75, None, None]


def test_join_with_different_key_names():
    customers = [["id", "name"], [1, "alice"], [2, "bob"], [3, "carol"]]
    result = join(ORDERS, customers, by=("cust_id", "id"))
    assert result[0] == ["order_id", "cust_id", "amount", "name"]
    assert result[1] == [101, 2, 250, "bob"]


def test_join_by_column_number_per_side():
    # cust_id is column 2 on the left but column 1 on the right
    result = join(ORDERS, CUSTOMERS, by=(2, 1))
    assert result[1] == [101, 2, 250, "bob", "pune"]


def test_join_by_one_column_number_uses_it_on_both_sides():
    left = [["k", "v"], [1, "x"]]
    right = [["k", "w"], [1, "y"]]
    assert join(left, right, by=1) == [["k", "v", "w"], [1, "x", "y"]]


def test_join_first_match_wins_for_duplicate_keys():
    customers = [
        ["cust_id", "name"],
        [2, "bob"],
        [2, "bobby"],
    ]
    assert join(ORDERS, customers, by="cust_id")[1] == [101, 2, 250, "bob"]


def test_join_unknown_column_name_raises():
    with pytest.raises(InvalidIndexError):
        join(ORDERS, CUSTOMERS, by="nope")


def test_join_empty_table_raises():
    with pytest.raises(InvalidIndexError):
        join([], CUSTOMERS, by="cust_id")


def test_join_with_no_data_rows_returns_header_only():
    assert join([ORDERS[0]], CUSTOMERS, by="cust_id") == [
        ["order_id", "cust_id", "amount", "name", "city"]
    ]


def test_join_handles_ragged_left_row():
    orders = ORDERS + [[104]]
    assert join(orders, CUSTOMERS, by="cust_id", if_not_found="—")[-1] == [104, "—", "—"]
