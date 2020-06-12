import chess
import chess.svg
import random

board = chess.Board()

def points(boardState):
    rating = 0.0
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
        elif letter == 'P':
            rating -= 1
        elif letter == 'K':
            rating -= 1000
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
            moveRatings[-1]+=0.9

    newRatings = []
    for move in moveRatings:
        newRatings.append(move+(random.randint(1,99)/1000))

    return moves[newRatings.index(max(newRatings))]

def bestMove3(board):
    for move in board.legal_moves:
        pass

def userMove(board):
    move = input("enter move: ")
    while True:
        try:
            board.push_san(move)
            break
        except Exception:
            move = input("enter move: ")

def londonMove(board):
    if board.is_legal(chess.Move(chess.D2,chess.D4)) and trackerArray[0]==False:
        board.push_san("d4")
        trackerArray[0]=True
    elif board.is_legal(chess.Move(chess.C1,chess.F4)) and trackerArray[1]==False:
        board.push_san("Bf4")
        trackerArray[1]=True
    elif board.is_legal(chess.Move(chess.E2,chess.E3)) and trackerArray[2]==False:
        board.push_san("e3")
        trackerArray[2]=True
    elif board.is_legal(chess.Move(chess.B1,chess.D2)) and trackerArray[3]==False:
        board.push_san("Nd2")
        trackerArray[3]=True
    elif board.is_legal(chess.Move(chess.C2,chess.C3)) and trackerArray[4]==False:
        board.push_san("c3")
        trackerArray[4]=True
    elif board.is_legal(chess.Move(chess.G1,chess.F3)) and trackerArray[5]==False:
        board.push_san("Ngf3")
        trackerArray[5]=True
    elif board.is_legal(chess.Move(chess.F1,chess.D3)) and trackerArray[6]==False:
        board.push_san("Bd3")
        trackerArray[6]=True
    else:
        board.push(bestMove2(board))

while not board.is_game_over():
    exit = False
    trackerArray = [False,False,False,False,False,False,False]
    expectedValue = bestMoveValue(board)
    if board.fullmove_number < 8 and not exit:
        londonMove(board)
        print(expectedValue,points(board))
        if expectedValue > (points(board)+0.5):
            board.pop()
            board.push(bestMove2(board))

    display(chess.svg.board(board=board,size=400,flipped=True))
    print(board.legal_moves)
    userMove(board)

#treesearch
#prune high-risk strategies from the tree
