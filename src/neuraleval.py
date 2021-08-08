
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import numpy as np
import chess
import tensorflow as tf
from tensorflow.keras.layers import Conv2D, Flatten, Dense, BatchNormalization, Input, concatenate, Reshape, MaxPooling2D, Add
from tensorflow.keras.models import Model
from tensorflow import keras

BEST_MATERIAL_ADVANTAGE = 10300

class SimpleChessNet:
    def __init__(self, dims=(8, 8, 11), xbatch_size=1) -> None:
        print(xbatch_size)
        inputLayer = Input(shape=dims, batch_size=xbatch_size, name="input")
        x = inputLayer
        #################################################################
        ##################### FULLY CONNECTED OUT #######################
        #################################################################
        x = Flatten()(x)
        x = Dense(512, activation="relu", name="Dense1")(x)
        x = Dense(256, activation="relu", name="Dense2")(x)
        x = Dense(128, activation="relu", name="Dense3")(x)

        outputLayer = Dense(1, name="eval", activation="tanh")(x)
        self.evalModel = Model(inputs=inputLayer, outputs=outputLayer)

        self.evalModel.compile(
            optimizer=keras.optimizers.SGD(),
            loss=keras.losses.MeanSquaredError(),
            metrics=[keras.metrics.MeanAbsoluteError()],
        )

        self.evalModel.summary()

    def __call__(self) -> Model:
        return self.evalModel


def vectorise_board(board: chess.Board) -> np.ndarray:
    # if board.turn == chess.BLACK:
    #     board = board.mirror()
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
        0xFFFFFFFFFFFFFFFF if (board.turn == chess.WHITE) else 0
    ]
    out = np.zeros((8, 8, 11))
    for i, bb in enumerate(bitboards):
        for square in chess.scan_forward(bb):
            file = chess.square_file(square)
            rank = chess.square_rank(square)
            out[file][rank][i] = 1

    return out

single_item_model = SimpleChessNet(
    xbatch_size=1
)()

single_item_model.load_weights("neuralnet/cp.ckpt")
single_item_model.compile(
    optimizer=tf.keras.optimizers.SGD(),
    loss=tf.keras.losses.MeanSquaredError(),
    metrics=["accuracy"],
)

def neural_eval(board: chess.Board) -> float:
    return - float(single_item_model(np.array([vectorise_board(board)]), training=False)[0][0]) * BEST_MATERIAL_ADVANTAGE

