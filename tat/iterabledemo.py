
bools = [False, True]

perms = [(a, b, c) for a in bools for b in bools for c in bools]

def evalu(a, b, c):
    return (a and b and (not c)) or ((not a) and (not b)) or ((not a) and (not c))

for p in perms:
    print([x for x in map(int, p)], int(evalu(*p)))
