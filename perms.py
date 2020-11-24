import operator

pieces = ['P', 'N', 'B', 'R', 'Q', 'K']

PMV = {'P': 1000, 'N': 3200, 'B': 3330, 'R': 5100, 'Q': 8800, 'K': 1000000000}

perms = [(p1, p2) for p1 in pieces for p2 in pieces[:-1]]

SEEs = [PMV[p2]-PMV[p1] for (p1, p2) in perms]

def move_sort(moves: list, ratings: list):
    pairs = zip(*sorted(zip(moves, ratings), key=operator.itemgetter(1)))
    moves, ratings = [list(pair) for pair in pairs]
    return moves, ratings

#print(perms)
moves, ratings = move_sort(perms, SEEs)
#print([(move, rating) for (move, rating) in zip(moves, ratings)])
for move in reversed(moves):
    print(move)