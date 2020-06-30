import chess
import chess.svg
import random
import chess.variant
import time
import operator
import line_profiler

whiteTime = 0.0
blackTime = 0.0

pawnSpacesB =  [0,0,0,0,0,0,0,0,50,50,50,50,50,50,50,50,10,10,20,30,30,20,10,10,5,5,10,25,25,10,5,5,0,0,0,20,20,0,0,0,5,-5,-10,0,0,-10,-5,5,5,10,10,-20,-20,10,10,5,0,0,0,0,0,0,0,0]
knightSpacesB = [-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,0,0,0,-20,-40,-30,0,10,15,15,10,0,-30,-30,5,15,20,20,15,5,-30,-30,0,15,20,20,15,0,-30,-30,5,10,15,15,10,5,-30,-40,-20,0,5,5,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50,]
bishopSpacesB = [-20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,10,10,5,0,-10,-10,5,5,10,10,5,5,-10,-10,0,10,10,10,10,0,-10,-10,10,10,10,10,10,10,-10,-10,5,0,0,0,0,5,-10,-20,-10,-10,-10,-10,-10,-10,-20,]
rookSpacesB = [0,0,0,0,0,0,0,0,5,10,10,10,10,10,10,5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,0,0,0,5,5,0,0,0]
queenSpacesB = [-20,-10,-10,-5,-5,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,5,5,5,0,-10,-5,0,5,5,5,5,0,-5,0,0,5,5,5,5,0,-5,-10,5,5,5,5,5,0,-10,-10,0,5,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20]
kingSpacesB = [-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-20,-30,-30,-40,-40,-30,-30,-20,-10,-20,-20,-20,-20,-20,-20,-10,20,20,0,0,0,0,20,20,20,30,10,0,0,10,30,20]
kingSpacesEndgameB = [-50,-40,-30,-20,-20,-30,-40,-50,-30,-20,-10,0,0,-10,-20,-30,-30,-10,20,30,30,20,-10,-30,-30,-10,30,40,40,30,-10,-30,-30,-10,30,40,40,30,-10,-30,-30,-10,20,30,30,20,-10,-30,-30,-30,0,0,0,0,-30,-30,-50,-30,-30,-30,-30,-30,-30,-50]

pawnSpacesW = list(reversed(pawnSpacesB))
knightSpacesW = list(reversed(knightSpacesB))
bishopSpacesW = list(reversed(bishopSpacesB))
rookSpacesW = list(reversed(rookSpacesB))
queenSpacesW = list(reversed(queenSpacesB))
kingSpacesW = list(reversed(kingSpacesB))
kingSpacesEndgameW = list(reversed(kingSpacesEndgameB))

@profile
def evaluate(board,depth):
    if board.turn:
        mod = 1
    else:
        mod = -1

    if board.is_checkmate():
        return 10000.0*depth*mod
    if board.is_repetition(2):
        return -20000.0*mod

    endgame = False
    rating = 0.0

    rating += -sum([pawnSpacesW[i]+1000 for i in board.pieces(chess.PAWN, chess.WHITE)])*0.001
    rating -= -sum([pawnSpacesB[i]+1000 for i in board.pieces(chess.PAWN, chess.BLACK)])*0.001
    rating += -sum([knightSpacesW[i]+3200 for i in board.pieces(chess.KNIGHT, chess.WHITE)])*0.001
    rating -= -sum([knightSpacesB[i]+3200 for i in board.pieces(chess.KNIGHT, chess.BLACK)])*0.001
    rating += -sum([bishopSpacesW[i]+3330 for i in board.pieces(chess.BISHOP, chess.WHITE)])*0.001
    rating -= -sum([bishopSpacesB[i]+3330 for i in board.pieces(chess.BISHOP, chess.BLACK)])*0.001
    rating += -sum([rookSpacesW[i]+5100 for i in board.pieces(chess.ROOK, chess.WHITE)])*0.001
    rating -= -sum([rookSpacesB[i]+5100 for i in board.pieces(chess.ROOK, chess.BLACK)])*0.001
    rating += -sum([queenSpacesW[i]+8800 for i in board.pieces(chess.QUEEN, chess.WHITE)])*0.001
    rating -= -sum([queenSpacesB[i]+8800 for i in board.pieces(chess.QUEEN, chess.BLACK)])*0.001
    rating += -sum([kingSpacesW[i] for i in board.pieces(chess.KING, chess.WHITE)])*0.001
    rating -= -sum([kingSpacesB[i] for i in board.pieces(chess.KING, chess.BLACK)])*0.001

    return rating

def orderedMoves(board,killer):


@profile
def negamax(node, depth, a, b, colour, killer):
    if depth == 0 or node.is_game_over():
        return colour * evaluate(node,depth)
    value = -1337000.0
    for move in node.legal_moves:
        node.push(move)
        value = max(value, -negamax(node, depth-1, -b, -a, -colour, killer))
        a = max(a, value)
        node.pop()
        if a >= b:
            killer = move
            break
    return value

@profile
def pushMove(board,depth,debug):
    start = time.time()
    if board.turn:
        turn = 1
    else:
        turn = -1
    moves = []
    for move in board.legal_moves:
        moves.append(move)
    boards = []
    moveRatings = []
    heuristicRatings = []
    for move in board.legal_moves:
        board.push(move)

        moveRatings.append(negamax(board, depth, -1337000, 1337000, turn, move))

        boards.append(board.copy())

        board.pop()
    if debug:
        for move,moveRating in zip(moves,moveRatings):
            print(move,moveRating)
    board.push(moves[moveRatings.index(min(moveRatings))])
    end = time.time()
    global whiteTime
    print(end-start)
    whiteTime += (end-start)
    return boards,moveRatings

def show(board):
    try:
        display(chess.svg.board(board=board,size=400,flipped=board.turn))
    except Exception:
        print(board)

def usermoveKermit(board,a,b):
    move = input("enter move: ")
    while True:
        try:
            board.push_san(move)
            break
        except Exception:
            move = input("enter move: ")

@profile
def main(string,rounds,debug,human,side,depth):
    for game in range(rounds):
        board = chess.Board(str(string))
        win = 1

        boardArrays = []
        ratingArrays = []

        while not board.is_game_over():
            show(board)

            boards,ratings = pushMove(board,depth,debug)
            boardArrays.append(boards)
            ratingArrays.append(ratings)

            if board.is_game_over():
                break

            show(board)

            boards,ratings = pushMove(board,depth,debug)
            boardArrays.append(boards)
            ratingArrays.append(ratings)

        show(board)
        if board.is_stalemate():
            print('END BY STALEMATE')
        elif board.is_insufficient_material():
            print('END BY INSUFFICIENT MATERIAL')
        elif board.is_fivefold_repetition():
            print('END BY FIVEFOLD REPETITION')
        elif board.is_checkmate:
            print(board.turn,'WINS ON TURN',board.fullmove_number)
        else:
            print('END BY UNKNOWN REASON')
    return boardArrays,ratingArrays,board.move_stack

standard = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

whiteMate1 = '8/8/8/8/8/4R1K1/8/6k1 w - - 0 1'
blackMate1 = '8/8/8/8/8/4r1k1/8/6K1 b - - 0 1'

test = 'r3k2r/pp1n1pp1/2p1p2p/q1Pp1b2/1b1PnB2/PQN1PN1P/1P3PP1/R3KB1R w - - 0 1'

boardArrays,ratingArrays,stack = main(test,1,False,False,True,4)
print('time elapsed while white was thinking:',whiteTime)
print('time elapsed while black was thinking:',blackTime)
print(stack)

'''
pawn = 1000
knight = 3000
bishop = 3500
rook = 5000
queen = 9000

pieces = [pawn,knight,bishop,rook,queen]
diffs = []
for boards,ratings in zip(boardArrays,ratingArrays):
    for board,rating in zip(boards,ratings):
        if abs(float(rating)) < 900:
            diffs.append((float(rating)-float(evaluateTuned(board,pawn,knight,bishop,rook,queen)))**2)
        else:
            diffs.append(0.0)
print(diffs)

for counter in range(5):
    newdiffs = []
    modifier = 100
    index = 0
    for piece in pieces:
        piece += modifier
        for boards,ratings in zip(boardArrays,ratingArrays):
            for board,rating in zip(boards,ratings):
                if abs(float(rating)) < 900:
                    newdiffs.append((float(rating)-float(evaluateTuned(board,pawn,knight,bishop,rook,queen)))**2)
                else:
                    newdiffs.append(0.0)
        if sum(newdiffs) > sum(diffs):
            piece -= modifier*2
            for boards,ratings in zip(boardArrays,ratingArrays):
                for board,rating in zip(boards,ratings):
                    if abs(float(rating)) < 900:
                        newdiffs.append((float(rating)-float(evaluateTuned(board,pawn,knight,bishop,rook,queen)))**2)
                    else:
                        newdiffs.append(0.0)
            if sum(newdiffs) > sum(diffs):
                piece += modifier
            else:
                pieces[index] = piece
        else:
            pieces[index] = piece
        index+=1
print(pieces)
'''
