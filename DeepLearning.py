from UCI_TABLE import allmoves
from random import choices
from progress.bar import Bar
from copy import deepcopy
from tensorflow.keras import layers
from tensorflow import keras
import tensorflow as tf
import numpy as np
import chess.pgn
import chess
from tensorflow.keras.layers import Conv2D, Conv3D, Flatten, Dense, SimpleRNN, MaxPooling3D, Dropout, BatchNormalization
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# -*- coding: utf-8 -*-


"""Defining functions:"""


def vectorise_index(index: int, size: int):
    worker = [0 for _ in range(size)]
    worker[index] = 1
    return tuple(worker)


def vectorise_move(m: chess.Move, orientation=chess.WHITE):
    if orientation == chess.BLACK:
        m = mirror_move(m)
    ucistring = m.uci()
    if len(ucistring) == 5 and ucistring[-1] == "n":
        ucistring = ucistring[:-1]
    idx = allmoves.index(ucistring)
    return vectorise_index(idx, len(allmoves))


def legal_distribution(moveVector: tuple, legalMoves: chess.LegalMoveGenerator = None):
    global allmoves
    target = [m.uci() for m in legalMoves] if (
        legalMoves is not None) else allmoves
    validMoves = [allmoves.index(m) for m in target] if (
        legalMoves is not None) else list(range(len(allmoves)))
    return [(i, allmoves[i], moveVector[i]) for i in validMoves]
    # index, uci, score


def mirror_from_uci(uci: str):
    wmove = chess.Move.from_uci(uci)
    wmove.from_square = chess.square_mirror(wmove.from_square)
    wmove.to_square = chess.square_mirror(wmove.to_square)
    return wmove


def mirror_move(m: chess.Move):
    return chess.Move(
        chess.square_mirror(m.from_square),
        chess.square_mirror(m.to_square),
        m.promotion,
        m.drop
    )


def devectorise_move(moveVector: tuple,
                     legalMoves: chess.LegalMoveGenerator = None,
                     orientation=chess.WHITE):

    if orientation == chess.WHITE:
        return chess.Move.from_uci(max(
            legal_distribution(moveVector, legalMoves),
            key=lambda t: t[2])[1])
    else:
        return mirror_from_uci(max(
            legal_distribution(moveVector, legalMoves),
            key=lambda t: t[2])[1])
    # returns the most likely move


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def bb_to_tuple(bb: int):
    out = [0 for _ in range(64)]
    for i in range(64):
        if bb & (1 << i):
            out[i] = 1
    out = list(chunks(out, 8))
    return tuple(map(lambda x: tuple(x), out))


def vectorise_board(board: chess.Board):
    #flipped = False
    # if board.turn == chess.BLACK:
    #    board.apply_mirror()
    #    flipped = True
    bitboards = [
        board.pawns,
        board.knights,
        board.bishops,
        board.rooks,
        board.queens,
        board.kings,
        board.occupied_co[chess.WHITE],
        board.occupied_co[chess.BLACK],
        board.occupied,
        board.castling_rights,
    ]
    # if flipped:
    #    board.apply_mirror()
    vecs = map(bb_to_tuple, bitboards)
    return tuple(vecs)


test = chess.Move.from_uci("d2d4")
testb = chess.Board()
# assert(test == mirror_move(mirror_move(test)))
assert(test == devectorise_move(vectorise_move(
    test, chess.WHITE), testb.legal_moves, chess.WHITE))

assert(test == devectorise_move(vectorise_move(
    test, chess.BLACK), orientation=chess.BLACK))
assert(test == devectorise_move(vectorise_move(
    test, chess.WHITE), orientation=chess.WHITE))

vb = vectorise_board(testb)
assert(len(vb) == 10)
assert(len(vb[-1]) == 8)
assert(len(vb[-1][-1]) == 8)
print("assertion passed!")

# THE PLAN:
# For each game in the series:
# label it with the move made
# label it with the evaluation as 1, 0, -1 based on WDL.
# Shuffle the positions in a list.

"""Doing preprocessing of the dataset:"""

# Iterate through all moves and play them on a board.


# def get_training_data(game: chess.pgn.GameT):
#     x_train = [vectorise_board(game.board())]
#     y_train = []
#     board = game.board()
#     for move in game.mainline_moves():
#         y_train.append(vectorise_move(move, orientation=board.turn))
#         board.push(move)
#         x_train.append(vectorise_board(board))

#     return x_train[:len(y_train)], y_train


def get_training_data(game: chess.pgn.GameT):
    game_result = 0
    if game.headers["Result"] == "1/2-1/2":
        game_result = 0
    elif game.headers["Result"] == "1-0":
        game_result = 100
    elif game.headers["Result"] == "0-1":
        game_result = -100
    x_train = [vectorise_board(game.board())]
    y_train = []
    board = game.board()
    for move in game.mainline_moves():
        y_train.append((game_result,))
        board.push(move)
        x_train.append(vectorise_board(board))
    y_train.append((game_result,))

    return x_train[:len(y_train)], y_train


def all_contents_same_length(xs):
    return all([len(x) == len(xs[0]) for x in xs])

# this function checks if all the contents of container are the same length


def all_subcontents_same_length(xs):
    return all([all_contents_same_length(x) for x in xs])


def prop_x(inputd: "tuple[tuple[tuple[int]]]"):
    assert(all_contents_same_length(inputd))
    assert(all_subcontents_same_length(inputd))
    return len(inputd), len(inputd[0]), len(inputd[0][0])


def iterative_x_dimtest(x_train):
    for i, n in enumerate(x_train):
        assert(np.ndim(n) == 3)
        assert(np.shape(n) == (10, 8, 8))


def iterative_y_dimtest(y_train):
    for i, n in enumerate(y_train):
        assert(np.ndim(n) == 1)
        assert(np.shape(n) == (1858,))


def tensify(arg):
    larg = list(map(lambda x: list(map(list, x)), arg))
    out = tf.convert_to_tensor(larg, dtype=tf.float32)
    return out


BATCH_SIZE = 64
if __name__ == "__main__":
    with open(r"PGNs/Stockfish 10.pgn", encoding="utf-8", mode="r") as pgn:
        limit = 3000  # 3439 max
        bar = Bar("Loading Games", max=limit)
        x_train: "list[tuple[tuple[tuple[int]]]]" = []
        y_train: "list[tuple[int]]" = []
        x_val, y_val = get_training_data(chess.pgn.read_game(pgn))
        for i in range(30):
            x_add, y_add = get_training_data(chess.pgn.read_game(pgn))
            x_val += x_add
            y_val += y_add
        count = 0
        games = []
        while ((game := chess.pgn.read_game(pgn)) and count < limit):
            x_add, y_add = get_training_data(game)
            x_train += x_add
            y_train += y_add
            games.append((game.headers["Result"], len(x_add)))
            bar.next()
            count += 1
        x_train, y_train = x_train[:-(len(x_train) % BATCH_SIZE)
                                   ], y_train[:-(len(y_train) % BATCH_SIZE)]
        bar.finish()
        # x_train = tensify(x_train)
        # assert(len(x_train) == len(y_train))
        # assert(len(x_val) == len(x_val))
        # assert(all([prop_x(n) == prop_x(x_train[0]) for n in x_train]))
        # print(f"Shape of x_train: {np.shape(x_train)}")
        # print(f"Shape of y_train: {np.shape(y_train)}")
        # print(f"Dims of x_train: {np.ndim(x_train)}")
        # print(f"Dims of y_train: {np.ndim(y_train)}")
        # print(f"Shape of x_val: {np.shape(x_val)}")
        # print(f"Shape of y_val: {np.shape(y_val)}")
        # print(f"Dims of x_val: {np.ndim(x_val)}")
        # print(f"Dims of y_val: {np.ndim(y_val)}")
        # iterative_x_dimtest(x_train)
        # iterative_y_dimtest(y_train)
        # print("\n", x_train[0], "\n")

    """Defining a model architecture that can transform a State to a Move:"""

    # tf.debugging.set_log_device_placement(True)

    # moveModel = keras.Sequential(
    #     [
    #         keras.Input(shape=(10, 8, 8, 1), batch_size=BATCH_SIZE),
    #         Conv3D(filters=64, kernel_size=(1),
    #                activation="relu", name="conv1"),
    #         Conv3D(filters=64, kernel_size=(3),
    #                activation="relu", name="conv2"),
    #         Conv3D(filters=32, kernel_size=(3),
    #                activation="relu", name="conv3"),
    #         MaxPooling3D(
    #             pool_size=(2, 2, 2), strides=None, padding="valid", data_format=None, name="pool2"
    #         ),
    #         Flatten(),
    #         Dense(2048, activation="relu", name="layer1"),
    #         Dense(2048, activation="relu", name="layer2"),
    #         Dense(2048, activation="relu", name="layer3"),
    #         Dropout(0.4),
    #         Dense(2048, activation="relu", name="layer4"),
    #         Dense(1024, activation="relu", name="layer5"),
    #         Dense(512, activation="relu", name="layer6"),
    #         Dense(1858, activation="softmax", name="outputMove"),
    #     ]
    # )

    evalModel = keras.Sequential(
        [
            keras.Input(shape=(10, 8, 8), batch_size=BATCH_SIZE),
            Conv2D(64, kernel_size=(1), strides=(1, 1), padding="same",
                   data_format='channels_last'),
            BatchNormalization(axis=-1, center=False,
                               scale=False, epsilon=1e-5,),
            Conv2D(64, kernel_size=(2), strides=(1, 1), padding="same",
                   data_format='channels_last'),
            BatchNormalization(axis=-1, center=False,
                               scale=False, epsilon=1e-5,),
            Conv2D(64, kernel_size=(2), strides=(1, 1), padding="same",
                   data_format='channels_last'),
            BatchNormalization(axis=-1, center=False,
                               scale=False, epsilon=1e-5,),
            Conv2D(64, kernel_size=(2), strides=(1, 1), padding="same",
                   data_format='channels_last'),
            BatchNormalization(axis=-1, center=False,
                               scale=False, epsilon=1e-5,),
            Flatten(),
            Dense(2048, activation="relu", name="layer4"),
            Dense(1024, activation="relu", name="layer5"),
            Dense(512, activation="relu", name="layer6"),
            Dense(1, name="eval"),
        ]
    )

    evalModel.compile(
        optimizer=keras.optimizers.Adam(),
        loss=keras.losses.MeanSquaredError(),
        metrics=[],
    )

    evalModel.summary()

    """Fitting model to data:"""

    import os

    checkpoint_path = "training_7/cp.ckpt"
    checkpoint_dir = os.path.dirname(checkpoint_path)

    # Create a callback that saves the model's weights
    cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                     save_weights_only=True,
                                                     verbose=1,
                                                     save_best_only=True)

    # evalModel.load_weights(checkpoint_path)

    es_callback = keras.callbacks.EarlyStopping(monitor='val_loss', patience=3)

    print("Fit model on training data")
    history = evalModel.fit(
        x_train,
        y_train,
        batch_size=BATCH_SIZE,
        epochs=20,
        # We pass some validation for
        # monitoring validation loss and metrics
        # at the end of each epoch
        validation_data=(x_val, y_val),
        callbacks=[cp_callback]
    )

    evalModel.save(
        "C:/Users/Cosmo/Documents/GitHub/viridithas-chess/evalmodel")

    # """Evaluate model on test data:"""

    print("Evaluate on test data")
    results = evalModel.evaluate(x_val, y_val, batch_size=128)
    print("test loss, test acc:", results)

    # """Make predictions:"""

    print("Generate predictions for 3 samples")
    boards = [chess.Board(), chess.Board(
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"), chess.Board("rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")]
    samples = [vectorise_board(b) for b in boards]
    predictions = evalModel.predict(samples)
    print("predictions shape:", predictions.shape)
    moves_in_order = [sorted(list(enumerate(p)), key=lambda x: x[1])
                      for p in predictions]
    p = [""] * 3
    for i, pred in enumerate(moves_in_order):
        for move in pred:
            if allmoves[move[0]] in list(map(lambda x: x.uci(), boards[i].legal_moves)):
                p[i] = allmoves[move[0]]
                break
    for b in p:
        print(b)

    # print(ngmxs)
    # print(predictions)

    # """Some tests to ensure the loss function is actually correct:"""

    # nodes = [
    #     [0, 0], # 0 not over, X turn
    #     [0b000010000, 0], # 0 not over, O turn
    #     [0b1, 0], # 0 not over, O turn
    #     [1, 0b10], # 1 not over, X turn
    #     [0b000011110, 0b111100000], # -1 over, X turn
    #     [0b001111001, 0b110000110], # 1 over, O turn
    #     [0b000011011, 0b110100000], # -1 not over, O turn
    #     [0b001010001, 0b000001010], # 1 not over, O turn
    #     [0b10, 0], # 0 not over, O turn
    #     [0b10, 0b1000], # 1 not over, X turn
    # ]
    # for node in nodes:
    #     s = nodereader(node)
    #     print(fnegamax(s, (s.turn)) * s.turn, findMove(s))

    # for node in nodes:
    #     s = nodereader(node)
    #     print(s)

    # """Play an example game:"""

    # def argmax(func, iterable):
    #     best = iterable[0]
    #     bestval = func(iterable[0])
    #     for val in iterable:
    #         if func(val) > bestval:
    #             bestval = func(val)
    #             best = val
    #     return best, bestval

    # def best_move(state):
    #     probabilities = list(model.predict([arr_to_tup(state.node)])[0])
    #     print(probabilities)
    #     outcome = probabilities.index(max(probabilities))
    #     return outcome

    # game = State()
    # while not game.is_game_over():
    #     print(game)
    #     game.play(best_move(game))
    #     if game.is_game_over(): break
    #     print(game)
    #     game.play(best_move(game))
    # print(game)
    # game.show_result()
