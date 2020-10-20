import random

def roll():
    return random.randint(1, 6)

total = 0
for i in range(1000000):
    total += roll() + roll() + roll() + roll()

print(total / 1000000)