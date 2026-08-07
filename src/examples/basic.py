from pylookup import (
    filter,
    hlookup,
    index,
    index_match,
    match,
    sort,
    unique,
    vlookup,
    xlookup,
)

table = [
    ["id", "name", "score"],
    [1, "alice", 90],
    [2, "bob", 75],
    [3, "carol", 60],
]

print(vlookup(2, table, 2))              # bob
print(xlookup(3, [1, 2, 3], ["a", "b", "c"]))  # c
print(match("carol", ["alice", "bob", "carol"]))  # 3
print(index(table, 2, 3))                # 90
print(index_match([90, 75, 60], "bob", ["alice", "bob", "carol"]))  # 75

print(filter([1, 2, 3, 4, 5], lambda x: x % 2 == 0))  # [2, 4]
print(unique([1, 1, 2, 3, 3]))                        # [1, 2, 3]

data_rows = table[1:]                                 # skip the header row
print(sort(data_rows, by=3, reverse=True))             # highest score first
