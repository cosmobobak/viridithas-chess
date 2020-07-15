values = ["c", "b", "d", "a"]
moves = [2, 3, 1, 4]

zipped_lists = zip(values, moves)
sorted_pairs = sorted(zipped_lists)

pairs = zip(*sorted_pairs)
values, moves = [list(pair) for pair in pairs]

print(zipped_lists)
print(sorted_pairs)
print(values)
print(moves)
