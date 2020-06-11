import chess
import chess.svg
import random

board = chess.Board()

def points(boardState):
    rating = 0.00000
    if not chess.Color:
        for letter in board.fen()[:-12]:
            if letter == 'p':
                rating += 1
            elif letter == 'k':
                rating += 1000
            elif letter == 'n':
                rating += 3
            elif letter == 'b':
                rating += 3.5
            elif letter == 'q':
                rating += 9
            elif letter == 'r':
                rating += 5
    else:
        for letter in board.fen()[:-12]:
            if letter == 'P':
                rating += 1
            elif letter == 'K':
                rating += 1000
            elif letter == 'N':
                rating += 3
            elif letter == 'B':
                rating += 3.5
            elif letter == 'Q':
                rating += 9
            elif letter == 'R':
                rating += 5
    return rating

def bestMove(board):
    moveRatings = [] #the piece values for the opponent after each move
    moves = [] #corresponding moves

    for move in board.legal_moves:
        board.push(move)
        moves.append(move)
        moveRatings.append(points(board))
        if board.is_checkmate():
            moveRatings[-1]+=1000
        board.pop()
        if board.gives_check(move):
            moveRatings[-1]+=0.1

    newRatings = []
    for move in moveRatings:
        newRatings.append(move+(random.randint(1,99)/10000))

    return moves[newRatings.index(min(newRatings))]

def bestMoveValue(board):
    moveRatings = []
    for move in board.legal_moves:
        board.push(move)
        moveRatings.append(points(board))
        board.pop()
    if moveRatings == []:
        return 0.00000
    return min(moveRatings)

def bestMove2(board):
    moveRatings = [] #the piece values for the opponent after each move
    moves = [] #corresponding moves
    for move in board.legal_moves:
        moves.append(move)
        board.push(move)
        print(bestMoveValue(board),points(board))
        moveRatings.append(2000-bestMoveValue(board))
        board.pop()

    newRatings = []
    for move in moveRatings:
        newRatings.append(move+(random.randint(1,100)/1000))

    return moves[newRatings.index(min(newRatings))]

while not board.is_game_over():
    board.push(bestMove(board))
    display(chess.svg.board(board=board,size=400,flipped=True))
    print(board.legal_moves)
    board.push_san(input())

#treesearch
#prune high-risk strategies from the tree
