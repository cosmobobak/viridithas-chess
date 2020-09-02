import chess
import chess.svg
import random

board = chess.Board()

def points(boardState):
    rating = 0.0
    for letter in board.fen()[:-12]:
        if letter == 'p':
            rating += 1
        elif letter == 'n':
            rating += 3
        elif letter == 'b':
            rating += 3.5
        elif letter == 'q':
            rating += 9
        elif letter == 'r':
            rating += 5
        elif letter == 'P':
            rating -= 1
        elif letter == 'N':
            rating -= 3
        elif letter == 'B':
            rating -= 3.5
        elif letter == 'Q':
            rating -= 9
        elif letter == 'R':
            rating -= 5
    if not chess.Color:
        return rating
    else:
        return rating*-1

def bestMove(board):
    moveRatings = [] #the piece values for the opponent after each move
    moves = [] #corresponding moves

    for move in board.legal_moves:
        board.push(move)
        moves.append(move)
        moveRatings.append(points(board))
        board.pop()

    newRatings = []
    for move in moveRatings:
        newRatings.append(move+(random.randint(1,100)/1000))

    return moves[newRatings.index(min(newRatings))]

def bestMoveValue(board):
    moveRatings = []
    for move in board.legal_moves:
        board.push(move)
        moveRatings.append(points(board))
        board.pop()
    if moveRatings == []:
        return 0
    return min(moveRatings)

def bestMove2(board):
    moveRatings = [] #the piece values for the opponent after each move
    moves = [] #corresponding moves
    for move in board.legal_moves:
        moves.append(move)
        board.push(move)
        print(bestMoveValue(board),points(board))
        if board.is_checkmate():
            board.pop()
            return move
        moveRatings.append(bestMoveValue(board))
        board.pop()
        if board.gives_check(move):
            moveRatings[-1]+=0.1

    newRatings = []
    for move in moveRatings:
        newRatings.append(move+(random.randint(1,99)/1000))

    return moves[newRatings.index(max(newRatings))]

def userMove(board):
    move = input("enter move: ")
    while move not in board.legal_moves:
        move = input("enter move: ")
    board.push_san(move)

while not board.is_game_over():
    while board.fullmove_number < 11 and not exit:
        if board.fullmove_number == 1 and "e5" in board.legal_moves:
            board.push_san("e5")
        if board.fullmove_number == 2 and "Bf4" in board.legal_moves:
            board.push_san("Bf4")
        if board.fullmove_number == 3 and "e3" in board.legal_moves:
            board.push_san("e3")

    board.push(bestMove2(board))
    display(chess.svg.board(board=board,size=400,flipped=True))
    print(board.legal_moves)


#treesearch
#prune high-risk strategies from the tree
