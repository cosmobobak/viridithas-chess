list1 = ["c", "b", "d", "a"]
list2 = [2, 3, 1, 4]

zipped_lists = zip(list1, list2)
sorted_pairs = sorted(zipped_lists)

tuples = zip(*sorted_pairs)
list1, list2 = [ list(tuple) for tuple in  tuples]
