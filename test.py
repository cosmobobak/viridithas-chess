import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
from Glyph import State
from copy import deepcopy

def arr_to_tup(arr):
    flat = [(int(c),) for c in format(arr[0], '#011b')
            [2:] + format(arr[1], '#011b')[2:]]
    interm = [flat[:9], flat[9:]]
    out = [(), ()]
    out[0] = tuple([tuple(interm[0][i:i+3]) for i in range(0, 9, 3)])
    out[1] = tuple([tuple(interm[1][i:i+3]) for i in range(0, 9, 3)])
    return tuple(out)


class TTTAI():
    def __init__(self):
        self.model = tf.keras.models.load_model('TTT')

    def best_move(self, state: State):
        probabilities = list(self.model.predict([arr_to_tup(state.node)])[0])
        print(probabilities)
        outcome = probabilities.index(max(probabilities))
        return outcome

    def __call__(self, state: State) -> State:
        out = deepcopy(state)
        best = self.best_move(state)
        out.play(best)
        return out

if __name__ == "__main__":
    ai = TTTAI()
    ai.model.summary()
    game = State()
    player = int(input("Is the human player going first? [1/0]\n--> "))
    if player == 0:
        player = -1
    turn = 1
    while not game.is_game_over():
        print(game)
        if turn == player:
            game.play(
                int(input(f"Your legal moves are: {list(map(lambda x: x + 1, game.legal_moves()))}\n--> ")) - 1
            )
        else:
            game = ai(game)
        turn = -turn
    print(game)
    game.show_result()
