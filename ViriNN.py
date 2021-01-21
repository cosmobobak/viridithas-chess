import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from copy import deepcopy
from DeepLearning import vectorise_board
#from TreeNode import State
from chess import Board, BoardT, Move, WHITE, BLACK
from UCI_TABLE import allmoves
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.layers import Conv2D, Conv3D, Flatten, Dense, SimpleRNN
import tensorflow as tf


class State:
    def __init__(self, boardin = Board()) -> None:
        self.node = boardin

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
        self.model = keras.Sequential(
            [
                keras.Input(shape=(10, 8, 8, 1), batch_size=64),
                Conv3D(filters=640, kernel_size=(1),
                       activation="relu", name="conv1"),
                Conv3D(filters=640, kernel_size=(3),
                       activation="relu", name="conv2"),
                Conv3D(filters=320, kernel_size=(3),
                       activation="relu", name="conv3"),
                Flatten(),
                Dense(2048, activation="relu", name="layer1"),
                Dense(2048, activation="relu", name="layer2"),
                Dense(2048, activation="relu", name="layer3"),
                Dense(2048, activation="relu", name="layer4"),
                Dense(2048, activation="relu", name="layer5"),
                Dense(2048, activation="relu", name="layer6"),
                Dense(1858, activation="softmax", name="outputMove"),
            ]
        )

        self.model.compile(
            optimizer=keras.optimizers.Adam(),
            loss=keras.losses.CategoricalCrossentropy(),
            metrics=[],
        )

        checkpoint_path = "training_2/cp.ckpt"
        checkpoint_dir = os.path.dirname(checkpoint_path)

        self.model.load_weights(checkpoint_path)

    def best_move(self, state: State):
        probabilities = list(self.model.predict(
            [vectorise_board(state.node)])[0])
        if state.node.turn == BLACK:
            state.node.apply_mirror()
        options = [x.uci() for x in state.node.legal_moves]
        probabilities = [(p if (allmoves[i] in options) else 0.0) for i, p in enumerate(probabilities)]
        outcome = probabilities.index(max(probabilities))
        return outcome

    def __call__(self, state: State) -> State:
        global allmoves
        out = deepcopy(state)
        flipped = False
        if out.node.turn == BLACK:
            out.node.apply_mirror()
            flipped = True
        best = self.best_move(state)
        out.node.push(Move.from_uci(allmoves[best]))
        if flipped:
            out.node.apply_mirror()
        return out


if __name__ == "__main__":
    ai = TTTAI()
    ai.model.summary()
    game = State()
    player = int(input("Is the human player going first? [1/0]\n--> "))
    if player == 0:
        player = -1
    turn = 1
    while not game.node.is_game_over():
        print(game.node, end="\n")
        if turn == player:
            game.node.push_san(
                input(f"Your legal moves are: {game.node.legal_moves}\n--> ")
            )
        else:
            game = ai(game)
        turn = -turn
    print(game.node, end="\n")
    #game.show_result()
