l = [1, 2, 3]

strlist = ["a b", "c d", "e f"]

def double(x):
    return x * 2

def splitter(string):
    return string.split(" ")


# gives [['a', 'b'], ['c', 'd'], ['e', 'f']]
print(list(map(splitter, strlist)))
