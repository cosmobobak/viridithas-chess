from Glyph import State
from time import time

game = State()


def negamax(game, a=-2, b=2):
    if game.is_game_over():
        return game.evaluate() * game.turn

    best = -2 # this can be anything < -1
    for move in game.legal_moves():
        game.play(move)
        value = -negamax(game, -b, -a)
        game.unplay()
        best = max(value, best)
        if (value >= b):
            return b
        a = max(a, value)

    return best

if __name__ == "__main__":
    start = time()
    print(negamax(game))
    print(f"search took {time()-start}s")
