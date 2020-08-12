import chess
import chess.svg
import chess.pgn
import chess.polyglot
import chess.syzygy
import random
import chess.variant
import time
from operator import itemgetter

whiteTime = 0.0
tableSize = 2**29+49
table = dict()
PMV = {
    chess.Piece.from_symbol('p'):1000,
    chess.Piece.from_symbol('n'):3200,
    chess.Piece.from_symbol('b'):3330,
    chess.Piece.from_symbol('r'):5100,
    chess.Piece.from_symbol('q'):8800,
    chess.Piece.from_symbol('k'):0,
    chess.Piece.from_symbol('P'):1000,
    chess.Piece.from_symbol('N'):3200,
    chess.Piece.from_symbol('B'):3330,
    chess.Piece.from_symbol('R'):5100,
    chess.Piece.from_symbol('Q'):8800,
    chess.Piece.from_symbol('K'):0,
    }
PST = {
    chess.Piece.from_symbol('p'):(0,0,0,0,0,0,0,0,50,50,50,50,50,50,50,50,10,10,20,30,30,20,10,10,5,5,10,25,25,10,5,5,0,0,0,20,20,0,0,0,5,-5,-10,0,0,-10,-5,5,5,10,10,-20,-20,10,10,5,0,0,0,0,0,0,0,0),
    chess.Piece.from_symbol('n'):(-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,0,0,0,-20,-40,-30,0,10,15,15,10,0,-30,-30,5,15,20,20,15,5,-30,-30,0,15,20,20,15,0,-30,-30,5,10,15,15,10,5,-30,-40,-20,0,5,5,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50),
    chess.Piece.from_symbol('b'):(-20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,10,10,5,0,-10,-10,5,5,10,10,5,5,-10,-10,0,10,10,10,10,0,-10,-10,10,10,10,10,10,10,-10,-10,5,0,0,0,0,5,-10,-20,-10,-10,-10,-10,-10,-10,-20,),
    chess.Piece.from_symbol('r'):(0,0,0,0,0,0,0,0,5,10,10,10,10,10,10,5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,0,0,0,5,5,0,0,0),
    chess.Piece.from_symbol('q'):(-20,-10,-10,-5,-5,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,5,5,5,0,-10,-5,0,5,5,5,5,0,-5,0,0,5,5,5,5,0,-5,-10,5,5,5,5,5,0,-10,-10,0,5,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20),
    chess.Piece.from_symbol('k'):(-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-20,-30,-30,-40,-40,-30,-30,-20,-10,-20,-20,-20,-20,-20,-20,-10,20,20,0,0,0,0,20,20,20,30,10,0,0,10,30,20),
    chess.Piece.from_symbol('P'):(0, 0, 0, 0, 0, 0, 0, 0, 5, 10, 10, -20, -20, 10, 10, 5, 5, -5, -10, 0, 0, -10, -5, 5, 0, 0, 0, 20, 20, 0, 0, 0, 5, 5, 10, 25, 25, 10, 5, 5, 10, 10, 20, 30, 30, 20, 10, 10, 50, 50, 50, 50, 50, 50, 50, 50, 0, 0, 0, 0, 0, 0, 0, 0),
    chess.Piece.from_symbol('N'):(-50, -40, -30, -30, -30, -30, -40, -50, -40, -20, 0, 5, 5, 0, -20, -40, -30, 5, 10, 15, 15, 10, 5, -30, -30, 0, 15, 20, 20, 15, 0, -30, -30, 5, 15, 20, 20, 15, 5, -30, -30, 0, 10, 15, 15, 10, 0, -30, -40, -20, 0, 0, 0, 0, -20, -40, -50, -40, -30, -30, -30, -30, -40, -50),
    chess.Piece.from_symbol('B'):(-20, -10, -10, -10, -10, -10, -10, -20, -10, 5, 0, 0, 0, 0, 5, -10, -10, 10, 10, 10, 10, 10, 10, -10, -10, 0, 10, 10, 10, 10, 0, -10, -10, 5, 5, 10, 10, 5, 5, -10, -10, 0, 5, 10, 10, 5, 0, -10, -10, 0, 0, 0, 0, 0, 0, -10, -20, -10, -10, -10, -10, -10, -10, -20),
    chess.Piece.from_symbol('R'):(0, 0, 0, 5, 5, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, 5, 10, 10, 10, 10, 10, 10, 5, 0, 0, 0, 0, 0, 0, 0, 0),
    chess.Piece.from_symbol('Q'):(-20, -10, -10, -5, -5, -10, -10, -20, -10, 0, 0, 0, 0, 5, 0, -10, -10, 0, 5, 5, 5, 5, 5, -10, -5, 0, 5, 5, 5, 5, 0, 0, -5, 0, 5, 5, 5, 5, 0, -5, -10, 0, 5, 5, 5, 5, 0, -10, -10, 0, 0, 0, 0, 0, 0, -10, -20, -10, -10, -5, -5, -10, -10, -20),
    chess.Piece.from_symbol('K'):(20, 30, 10, 0, 0, 10, 30, 20, 20, 20, 0, 0, 0, 0, 20, 20, -10, -20, -20, -20, -20, -20, -20, -10, -20, -30, -30, -40, -40, -30, -30, -20, -30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30)
}

if True:
    pawnSpacesB =  (1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1050, 1050, 1050, 1050, 1050, 1050, 1050, 1050, 1010, 1010, 1020, 1030, 1030, 1020, 1010, 1010, 1005, 1005, 1010, 1025, 1025, 1010, 1005, 1005, 1000, 1000, 1000, 1020, 1020, 1000, 1000, 1000, 1005, 995, 990, 1000, 1000, 990, 995, 1005, 1005, 1010, 1010, 980, 980, 1010, 1010, 1005, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000)
    knightSpacesB = (3150, 3160, 3170, 3170, 3170, 3170, 3160, 3150, 3160, 3180, 3200, 3200, 3200, 3200, 3180, 3160, 3170, 3200, 3210, 3215, 3215, 3210, 3200, 3170, 3170, 3205, 3215, 3220, 3220, 3215, 3205, 3170, 3170, 3200, 3215, 3220, 3220, 3215, 3200, 3170, 3170, 3205, 3210, 3215, 3215, 3210, 3205, 3170, 3160, 3180, 3200, 3205, 3205, 3200, 3180, 3160, 3150, 3160, 3170, 3170, 3170, 3170, 3160, 3150)
    bishopSpacesB = (3310, 3320, 3320, 3320, 3320, 3320, 3320, 3310, 3320, 3330, 3330, 3330, 3330, 3330, 3330, 3320, 3320, 3330, 3335, 3340, 3340, 3335, 3330, 3320, 3320, 3335, 3335, 3340, 3340, 3335, 3335, 3320, 3320, 3330, 3340, 3340, 3340, 3340, 3330, 3320, 3320, 3340, 3340, 3340, 3340, 3340, 3340, 3320, 3320, 3335, 3330, 3330, 3330, 3330, 3335, 3320, 3310, 3320, 3320, 3320, 3320, 3320, 3320, 3310)
    rookSpacesB = (5100, 5100, 5100, 5100, 5100, 5100, 5100, 5100, 5105, 5110, 5110, 5110, 5110, 5110, 5110, 5105, 5095, 5100, 5100, 5100, 5100, 5100, 5100, 5095, 5095, 5100, 5100, 5100, 5100, 5100, 5100, 5095, 5095, 5100, 5100, 5100, 5100, 5100, 5100, 5095, 5095, 5100, 5100, 5100, 5100, 5100, 5100, 5095, 5095, 5100, 5100, 5100, 5100, 5100, 5100, 5095, 5100, 5100, 5100, 5105, 5105, 5100, 5100, 5100)
    queenSpacesB = (8780, 8790, 8790, 8795, 8795, 8790, 8790, 8780, 8790, 8800, 8800, 8800, 8800, 8800, 8800, 8790, 8790, 8800, 8805, 8805, 8805, 8805, 8800, 8790, 8795, 8800, 8805, 8805, 8805, 8805, 8800, 8795, 8800, 8800, 8805, 8805, 8805, 8805, 8800, 8795, 8790, 8805, 8805, 8805, 8805, 8805, 8800, 8790, 8790, 8800, 8805, 8800, 8800, 8800, 8800, 8790, 8780, 8790, 8790, 8795, 8795, 8790, 8790, 8780)
    kingSpacesB = (-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-20,-30,-30,-40,-40,-30,-30,-20,-10,-20,-20,-20,-20,-20,-20,-10,20,20,0,0,0,0,20,20,20,30,10,0,0,10,30,20)
    kingSpacesEndgameB = (-50,-40,-30,-20,-20,-30,-40,-50,-30,-20,-10,0,0,-10,-20,-30,-30,-10,20,30,30,20,-10,-30,-30,-10,30,40,40,30,-10,-30,-30,-10,30,40,40,30,-10,-30,-30,-10,20,30,30,20,-10,-30,-30,-30,0,0,0,0,-30,-30,-50,-30,-30,-30,-30,-30,-30,-50)

    pawnSpacesW = list(reversed(pawnSpacesB))
    knightSpacesW = list(reversed(knightSpacesB))
    bishopSpacesW = list(reversed(bishopSpacesB))
    rookSpacesW = list(reversed(rookSpacesB))
    queenSpacesW = list(reversed(queenSpacesB))
    kingSpacesW = list(reversed(kingSpacesB))
    kingSpacesEndgameW = list(reversed(kingSpacesEndgameB))
#@profile
def pieceDiff(board):
    count = 0
    for piece in board.pieces(chess.PAWN, chess.BLACK):
        count += -1
    for piece in board.pieces(chess.PAWN, chess.WHITE):
        count += 1
    for piece in board.pieces(chess.KNIGHT, chess.BLACK):
        count += -1
    for piece in board.pieces(chess.KNIGHT, chess.WHITE):
        count += 1
    for piece in board.pieces(chess.BISHOP, chess.BLACK):
        count += -1
    for piece in board.pieces(chess.BISHOP, chess.WHITE):
        count += 1
    for piece in board.pieces(chess.ROOK, chess.BLACK):
        count += -1
    for piece in board.pieces(chess.ROOK, chess.WHITE):
        count += 1
    for piece in board.pieces(chess.QUEEN, chess.BLACK):
        count += -1
    for piece in board.pieces(chess.QUEEN, chess.WHITE):
        count += 1
    return count
#@profile
def orderedMoves(board, best):
    hash = []
    takes = []
    last = []
    for move in board.legal_moves:
        if move.uci() == best:
            hash.append(move)
        elif board.is_capture(move):
            takes.append(move)
        else:
            last.append(move)
    return hash + takes + last
#@profile
def probeHash(key, hash, depth, a, b):
    try:
        entry = table[hash]
    except KeyError:
        return (None, None)
    if entry['key'] == key:
        if entry['depth'] >= depth:
            if entry['type'] == 0:
                return (entry['score'], True)
            if entry['type'] == 1 and entry['score'] <= a:
                return (a, True)
            if entry['type'] == 2 and entry['score'] >= b:
                return (b, True)
            return (entry['bestMove'], False)
        return (entry['bestMove'], False)
    return (None, None)
#@profile
def recordHash(key, hash, bestMove, depth, a, hashf):
    if abs(a) > 999999: 999999*a/abs(a)
    table[hash] = {'key':key, 'bestMove':bestMove, 'depth':depth, 'score':a, 'type':hashf}
#@profile
def pvs(node, depth, a, b, colour):
    hashf = 1
    if depth <= 0:
        #evaluate2(node, depth, False)
        value = colour * pieceDiff(node)
        #value = colour * qsearch(a, b, node, depth, False)
        return value
    if node.is_game_over():
        #evaluate2(node, depth, False)
        value = colour * pieceDiff(node)
        #value = colour * qsearch(a, b, node, depth, False)
        return value
    key = chess.polyglot.zobrist_hash(node)
    hash = key%tableSize
    probe = probeHash(key, hash, depth, a, b)
    if probe[0] != None:
        if probe[1]:
            return probe[0]
        else:
            bestMove = probe[0]
    #NULLMOVE PRUNING
    check = False
    if not node.is_check():
        node.push(chess.Move.null())
        value = -pvs(node, depth - 3, -b, -a, -colour)
        a = max(a, value)
        node.pop()
        if a >= b:
            return a
    else:
        check = True
    if 'bestMove' in locals():
        moves = orderedMoves(node, bestMove) #MOVE ORDERING
    else:
        moves = orderedMoves(node, '')
    currentBest = moves[0].uci()
    firstmove = True
    for i, move in enumerate(moves):
        if check:
            depth+=1
        node.push(move)
        if firstmove:
            value = -pvs(node, depth - 1, -b, -a, -colour)
            firstmove = False
        else:
            value = -pvs(node, depth - 1, -a - 1, -a, -colour)
            if a < value and value < b:
                value = -pvs(node, depth - 1, -b, -value, -colour)
        node.pop()
        if check:
            depth-=1
        if value >= b:
            recordHash(key, hash, currentBest, depth, b, 2)
            return b
        if value > a:
            hashf = 0
            a = value
            currentBest = moves[i].uci()
    recordHash(key, hash, currentBest, depth, a, hashf)
    return a

def moveSort(moves, ratings):
    pairs = zip(*sorted(zip(moves, ratings),key=itemgetter(1)))
    moves, ratings = [list(pair) for pair in pairs]
    return moves, ratings

def moveLister(moves):
    for move in moves:
        print(move.uci(), end=', ')

def showIterationData(board, moves, values, depth, startTime):
    print(board.san(moves[0]),'|',round(-values[0], 3),'|',str(round(time.time()-startTime, 2))+'s at depth',depth)

def pvsearch(node, timeLimit):
    startTime = time.time()
    depth = 1
    a, b = -1337000000000, 1337000000000
    colour = node.turn
    if colour:
        colour = 1
    else:
        colour = -1
    endgame = False
    if pieceCount(node) <= 6:
        endgame = True

    moves = orderedMoves(node, '')
    values = [0.0]*len(moves)

    for depth in range(1, 20):
        for i, move in enumerate(moves):
            node.push(move)
            values[i] = pvs(node, depth, a, b, colour)
            node.pop()
            if timeLimit < time.time()-startTime:
                return moves[0]
        moves, values = moveSort(moves, values)
        showIterationData(node, moves, values, depth, startTime)
    return moves[0]

def pieceCount(board):
    count = 0
    for piece in board.pieces(chess.PAWN, chess.BLACK):
        count += 1
    for piece in board.pieces(chess.PAWN, chess.WHITE):
        count += 1
    for piece in board.pieces(chess.KNIGHT, chess.BLACK):
        count += 1
    for piece in board.pieces(chess.KNIGHT, chess.WHITE):
        count += 1
    for piece in board.pieces(chess.BISHOP, chess.BLACK):
        count += 1
    for piece in board.pieces(chess.BISHOP, chess.WHITE):
        count += 1
    for piece in board.pieces(chess.ROOK, chess.BLACK):
        count += 1
    for piece in board.pieces(chess.ROOK, chess.WHITE):
        count += 1
    for piece in board.pieces(chess.QUEEN, chess.BLACK):
        count += 1
    for piece in board.pieces(chess.QUEEN, chess.WHITE):
        count += 1
    return count

def play(board, timeLimit):
    best = pvsearch(board, timeLimit)
    board.push(best)
    print(chess.pgn.Game.from_board(board)[-1])

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

def endingPrinter(board):
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

def main(string, debug, human, side, timeLimit):
    board = chess.variant.AntichessBoard(str(string))
    #board = chess.variant.CrazyhouseBoard(str(string))
    win = 1

    boardArrays = []
    ratingArrays = []
    while not board.is_game_over():
        show(board)
        play(board,timeLimit)
        #print(table)
        #usermoveKermit(board,1,1)
        if board.is_game_over():
            break
        show(board)
        play(board,timeLimit)
        #print(table)
        #usermoveKermit(board,1,1)
    endingPrinter(board)
    return str(chess.pgn.Game.from_board(board)[-1])

standard = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

timeLimit = 15
main(standard, True, True, True, timeLimit)
print('time elapsed while thinking:',whiteTime)
