import chess
import chess.svg
import random

from __future__ import division

from copy import deepcopy
from mcts import mcts
from functools import reduce
import operator

def evaluate(board):
    endgame = False
    rating = 0.0
    string = board.board_fen()
    map = board.piece_map()

    rating += -200*(string.count('K')-string.count('k'))
    rating += -1*(string.count('P')-string.count('p'))
    rating += -3*(string.count('N')-string.count('n'))
    rating += -3.5*(string.count('B')-string.count('b'))
    rating += -9*(string.count('Q')-string.count('q'))
    rating += -5*(string.count('R')-string.count('r'))

    x = 0.001
    for counter in range(64):
        try:
            if map[counter] == chess.Piece.from_symbol('p'):
                rating -= -pawnSpacesB[counter]*x
            elif map[counter] == chess.Piece.from_symbol('P'):
                rating += -pawnSpacesW[counter]*x
            elif map[counter] == chess.Piece.from_symbol('n'):
                rating -= -knightSpacesB[counter]*x
            elif map[counter] == chess.Piece.from_symbol('b'):
                rating -= -bishopSpacesB[counter]*x
            elif map[counter] == chess.Piece.from_symbol('r'):
                rating -= -rookSpacesB[counter]*x
            elif map[counter] == chess.Piece.from_symbol('q'):
                rating -= -queenSpacesB[counter]*x
            elif map[counter] == chess.Piece.from_symbol('k'):
                if endgame:
                    rating -= -kingSpacesEndgameB[counter]*x
                else:
                    rating -= -kingSpacesB[counter]*x
            elif map[counter] == chess.Piece.from_symbol('N'):
                rating += -knightSpacesW[counter]*x
            elif map[counter] == chess.Piece.from_symbol('B'):
                rating += -bishopSpacesW[counter]*x
            elif map[counter] == chess.Piece.from_symbol('R'):
                rating += -rookSpacesW[counter]*x
            elif map[counter] == chess.Piece.from_symbol('Q'):
                rating += -queenSpacesW[counter]*x
            elif map[counter] == chess.Piece.from_symbol('K'):
                if endgame:
                    rating += -kingSpacesEndgameW[counter]*x
                else:
                    rating += -kingSpacesW[counter]*x
            else:
                continue
        except Exception:
            continue

    if board.is_check() and board.turn:
        rating += 0.9
    elif board.is_check():
        rating += -0.9
    if board.is_checkmate() and board.turn:
        rating = 10000
    elif board.is_checkmate():
        rating = -10000
    if board.is_fivefold_repetition() and board.turn:
        rating = -20000
    elif board.is_fivefold_repetition():
        rating = 20000
    #incentivises castling
    if board.move_stack:
        move = board.peek()
        if chess.square_distance(move.from_square,move.to_square) == 2:
            if board.piece_at(move.to_square).symbol().upper() == 'K':
                if board.turn:
                    rating += -7
                else:
                    rating += 7
        elif chess.square_distance(move.from_square,move.to_square) == 1:
            if board.piece_at(move.to_square).symbol().upper() == 'K':
                if board.turn:
                    rating += 0.05
                else:
                    rating += -0.05

    return rating

class boardState():
    def __init__(self, board):
        self.board = board
        self.currentPlayer = 1

    def getCurrentPlayer(self):
        return self.currentPlayer

    def getPossibleActions(self):
        legalMoves = []
        for move in self.board.legal_moves:
            legalMoves.append(Action(player=self.currentPlayer, move=move, string=move.uci()))
        return legalMoves

    def takeAction(self, action):
        newState = deepcopy(self)
        newState.board.push(action.move)
        newState.currentPlayer = self.currentPlayer * -1
        return newState

    def isTerminal(self):
        return self.board.is_game_over()

    def getReward(self):
        return evaluate(self.board)


class Action():
    def __init__(self, player, move, string):
        self.player = player
        self.move = move
        self.string = string

    def __str__(self):
        return self.string

    def __repr__(self):
        return str(self.string,self.player)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.string == other.string and self.player == other.player

    def __hash__(self):
        return hash((self.string, self.player))

def pushMCTS(board):
    initialState = boardState(board)
    global tree
    tree = mcts(timeLimit=10000)
    action = tree.search(initialState=initialState)
    print(action)
    board.push(action.move)
    display(chess.svg.board(board=board,size=400,flipped=True))

board = chess.Board()
while not board.is_game_over():
    pushMCTS(board)
