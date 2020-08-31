import chess
import chess.svg
import chess.pgn
import chess.polyglot
import chess.syzygy
import random
import chess.variant
import time
#import gmpy
from operator import itemgetter

whiteTime = 0.0
tableSize = 2**29+49
table = dict()
PMV = {'p': 1000, 'n': 3200, 'b': 3330, 'r': 5100, 'q': 8800, 'k': 0,
       'P': 1000, 'N': 3200, 'B': 3330, 'R': 5100, 'Q': 8800, 'K': 0}
PST = {
    'p': (0, 0, 0, 0, 0, 0, 0, 0, 50, 50, 50, 50, 50, 50, 50, 50, 10, 10, 20, 30, 30, 20, 10, 10, 5, 5, 10, 25, 25, 10, 5, 5, 0, 0, 0, 20, 20, 0, 0, 0, 5, -5, -10, 0, 0, -10, -5, 5, 5, 10, 10, -20, -20, 10, 10, 5, 0, 0, 0, 0, 0, 0, 0, 0),
    'n': (-50, -40, -30, -30, -30, -30, -40, -50, -40, -20, 0, 0, 0, 0, -20, -40, -30, 0, 10, 15, 15, 10, 0, -30, -30, 5, 15, 20, 20, 15, 5, -30, -30, 0, 15, 20, 20, 15, 0, -30, -30, 5, 10, 15, 15, 10, 5, -30, -40, -20, 0, 5, 5, 0, -20, -40, -50, -40, -30, -30, -30, -30, -40, -50),
    'b': (-20, -10, -10, -10, -10, -10, -10, -20, -10, 0, 0, 0, 0, 0, 0, -10, -10, 0, 5, 10, 10, 5, 0, -10, -10, 5, 5, 10, 10, 5, 5, -10, -10, 0, 10, 10, 10, 10, 0, -10, -10, 10, 10, 10, 10, 10, 10, -10, -10, 5, 0, 0, 0, 0, 5, -10, -20, -10, -10, -10, -10, -10, -10, -20,),
    'r': (0, 0, 0, 0, 0, 0, 0, 0, 5, 10, 10, 10, 10, 10, 10, 5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 5, 5, 0, 0, 0),
    'q': (-20, -10, -10, -5, -5, -10, -10, -20, -10, 0, 0, 0, 0, 0, 0, -10, -10, 0, 5, 5, 5, 5, 0, -10, -5, 0, 5, 5, 5, 5, 0, -5, 0, 0, 5, 5, 5, 5, 0, -5, -10, 5, 5, 5, 5, 5, 0, -10, -10, 0, 5, 0, 0, 0, 0, -10, -20, -10, -10, -5, -5, -10, -10, -20),
    'k': (-30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30, -20, -30, -30, -40, -40, -30, -30, -20, -10, -20, -20, -20, -20, -20, -20, -10, 20, 20, 0, 0, 0, 0, 20, 20, 20, 30, 10, 0, 0, 10, 30, 20),
    'P': (0, 0, 0, 0, 0, 0, 0, 0, 5, 10, 10, -20, -20, 10, 10, 5, 5, -5, -10, 0, 0, -10, -5, 5, 0, 0, 0, 20, 20, 0, 0, 0, 5, 5, 10, 25, 25, 10, 5, 5, 10, 10, 20, 30, 30, 20, 10, 10, 50, 50, 50, 50, 50, 50, 50, 50, 0, 0, 0, 0, 0, 0, 0, 0),
    'N': (-50, -40, -30, -30, -30, -30, -40, -50, -40, -20, 0, 5, 5, 0, -20, -40, -30, 5, 10, 15, 15, 10, 5, -30, -30, 0, 15, 20, 20, 15, 0, -30, -30, 5, 15, 20, 20, 15, 5, -30, -30, 0, 10, 15, 15, 10, 0, -30, -40, -20, 0, 0, 0, 0, -20, -40, -50, -40, -30, -30, -30, -30, -40, -50),
    'B': (-20, -10, -10, -10, -10, -10, -10, -20, -10, 5, 0, 0, 0, 0, 5, -10, -10, 10, 10, 10, 10, 10, 10, -10, -10, 0, 10, 10, 10, 10, 0, -10, -10, 5, 5, 10, 10, 5, 5, -10, -10, 0, 5, 10, 10, 5, 0, -10, -10, 0, 0, 0, 0, 0, 0, -10, -20, -10, -10, -10, -10, -10, -10, -20),
    'R': (0, 0, 0, 5, 5, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, 5, 10, 10, 10, 10, 10, 10, 5, 0, 0, 0, 0, 0, 0, 0, 0),
    'Q': (-20, -10, -10, -5, -5, -10, -10, -20, -10, 0, 0, 0, 0, 5, 0, -10, -10, 0, 5, 5, 5, 5, 5, -10, -5, 0, 5, 5, 5, 5, 0, 0, -5, 0, 5, 5, 5, 5, 0, -5, -10, 0, 5, 5, 5, 5, 0, -10, -10, 0, 0, 0, 0, 0, 0, -10, -20, -10, -10, -5, -5, -10, -10, -20),
    'K': (20, 30, 10, 0, 0, 10, 30, 20, 20, 20, 0, 0, 0, 0, 20, 20, -10, -20, -20, -20, -20, -20, -20, -10, -20, -30, -30, -40, -40, -30, -30, -20, -30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30)
}

for key in PMV:
    # evaltable is accessed via evaltable[key][square]
    # this should probably be updated to have the squares in dicts too, but eh
    PST[key] = [PST[key][i]+PMV[key] for i in range(64)]

isodd = True

standard = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

whiteMate1 = '8/8/8/8/8/4R1K1/8/6k1 w - - 0 1'
blackMate1 = '8/8/8/8/8/4r1k1/8/6K1 b - - 0 1'

openings = ['rnbqkbnr/pppppppp/8/8/8/6P1/PPPPPP1P/RNBQKBNR b KQkq - 0 1',
            'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
            'rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1',
            'rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq - 1 1',
            'rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq c3 0 1',
            'rnbqkbnr/pppppppp/8/8/8/N7/PPPPPPPP/R1BQKBNR b KQkq - 1 1']

names = ['#g3', '#e4', '#d4', '#Nf3', '#c4', '#Na3']

test = 'r1bqkbnr/pp1p1ppp/8/2p5/3QP3/8/PPP2PPP/RNB1KB1R w KQkq - 0 1'

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
def static_exchange_eval(board):
    mod = 1 if board.turn else -1
    
    if board.can_claim_fifty_moves(): return -20001000*mod

    white = board.occupied_co[True]
    black = board.occupied_co[False]

    rating = 0
    
    rating -= (bin(board.pawns & white).count('1')-bin(board.pawns & black).count('1'))*1000
    rating -= (bin(board.knights & white).count('1')-bin(board.knights & black).count('1'))*3200
    rating -= (bin(board.bishops & white).count('1')-bin(board.bishops & black).count('1'))*3330
    rating -= (bin(board.rooks & white).count('1')-bin(board.rooks & black).count('1'))*5200
    rating -= (bin(board.queens & white).count('1')-bin(board.queens & black).count('1'))*8800
    rating -= (bin(board.kings & white).count('1')-bin(board.kings & black).count('1'))*200000

    return rating
#@profile
def evaluate(board, depth, endgame):
    mod = 1 if board.turn else -1

    if board.is_checkmate(): return 1000000000*(depth+1)*mod
    if board.can_claim_draw():
        return 20001000*mod
    if board.can_claim_fifty_moves(): return -20001000*mod

    rating = 0
    rating += sum([pawnSpacesB[i] for i in board.pieces(chess.PAWN, chess.BLACK)])-sum([pawnSpacesW[i] for i in board.pieces(chess.PAWN, chess.WHITE)])
    rating += sum([knightSpacesB[i] for i in board.pieces(chess.KNIGHT, chess.BLACK)])-sum([knightSpacesW[i] for i in board.pieces(chess.KNIGHT, chess.WHITE)])
    rating += sum([bishopSpacesB[i] for i in board.pieces(chess.BISHOP, chess.BLACK)])-sum([bishopSpacesW[i] for i in board.pieces(chess.BISHOP, chess.WHITE)])
    rating += sum([rookSpacesB[i] for i in board.pieces(chess.ROOK, chess.BLACK)])-sum([rookSpacesW[i] for i in board.pieces(chess.ROOK, chess.WHITE)])
    rating += sum([queenSpacesB[i] for i in board.pieces(chess.QUEEN, chess.BLACK)])-sum([queenSpacesW[i] for i in board.pieces(chess.QUEEN, chess.WHITE)])
    rating += sum([kingSpacesEndgameB[i] for i in board.pieces(chess.KING, chess.BLACK)])-sum([kingSpacesEndgameW[i] for i in board.pieces(chess.KING, chess.WHITE)])
    
    return rating
def ordered_moves(board, best):
    moves = [move for move in board.legal_moves]
    hash = [moves.pop(i) for i, move in enumerate(moves) if move.uci()==best]
    takes = [moves.pop(i) for i, move in enumerate(moves) if board.is_capture(move)]
    return hash + takes + moves
#@profile
def probe_hash(key, hash, depth, a, b):
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
def recordHash(key, hash, bestMove, depth, a, hashDataType):
    if abs(a) > 999999000: 
        a = 999999000*a/abs(a)
    try:
        entry = table[hash]
        if entry['depth'] >= depth:
            table[hash] = {'key':key, 'bestMove':bestMove, 'depth':depth, 'score':a, 'type':hashDataType}
        else:
            return
    except Exception:
        table[hash] = {'key':key, 'bestMove':bestMove, 'depth':depth, 'score':a, 'type':hashDataType}

def captures(node):
    return [move for move in node.legal_moves if node.is_capture(move)]

def quiescence_search(a, b, node, colour):
    for move in captures(node):
        node.push(move)
        value = static_exchange_eval(node)
        node.pop()
        if value >= b:
            return b
        if value > a:
            a = value
    return a

#@profile
def principal_variation_search(node, depth, a, b, colour):
    global isodd
    hashDataType = 1
    if depth <= 0:
        return colour * evaluate(node, depth, colour)
    if node.is_game_over():
        return colour * evaluate(node, depth, colour)
    key = chess.polyglot.zobrist_hash(node)
    hash = key%tableSize
    probe = probe_hash(key, hash, depth, a, b)
    if probe[0] != None:
        if probe[1]:
            return probe[0]
        else:
            bestMove = probe[0]
    #NULLMOVE PRUNING
    check = False
    if not node.is_check():
        node.push(chess.Move.null())
        value = -principal_variation_search(node, depth - 3, -b, -a, -colour)
        a = max(a, value)
        node.pop()
        if a >= b:
            return a
    else:
        check = True
    if 'bestMove' in locals():
        moves = ordered_moves(node, bestMove) #MOVE ORDERING
    else:
        moves = ordered_moves(node, '')
    currentBest = moves[0].uci()
    firstmove = True
    for i, move in enumerate(moves):
        if check: 
            depth+=1
            isodd = not isodd
        node.push(move)
        if firstmove:
            value = -principal_variation_search(node, depth - 1, -b, -a, -colour)
            firstmove = False
        else:
            value = -principal_variation_search(node, depth - 1, -a - 1, -a, -colour)
            if a < value and value < b:
                value = -principal_variation_search(node, depth - 1, -b, -value, -colour)
        node.pop()
        if check: 
            depth-=1
            isodd = not isodd
        if value >= b:
            recordHash(key, hash, currentBest, depth, b, 2)
            return b
        if value > a:
            hashDataType = 0
            a = value
            currentBest = moves[i].uci()
    recordHash(key, hash, currentBest, depth, a, hashDataType)
    return a

def move_sort(moves, ratings):
    pairs = zip(*sorted(zip(moves, ratings),key=itemgetter(1)))
    moves, ratings = [list(pair) for pair in pairs]
    return moves, ratings

def move_lister(moves):
    for move in moves:
        print(move.uci(), end=', ')

def show_iteration_data(board, moves, values, depth, startTime):
    print(board.san(moves[0]),'|',round(-values[0], 3),'|',str(round(time.time()-startTime, 2))+'s at depth',depth)

def pvsearch(node, timeLimit):
    global isodd
    startTime = time.time()
    depth = 1
    a, b = -1337000000000000, 1337000000000000
    if node.turn:
        colour = 1
    else:
        colour = -1

    moves = ordered_moves(node, '')
    values = [0.0]*len(moves)

    for depth in [1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]:
        isodd = True if depth%2 == 1 else False
        for i, move in enumerate(moves):
            node.push(move)
            values[i] = principal_variation_search(node, depth, a, b, colour)
            node.pop()
            if timeLimit < time.time()-startTime:
                return moves[0]
        moves, values = move_sort(moves, values)
        show_iteration_data(node, moves, values, depth, startTime)
    return moves[0]

def piece_count(board):
    count = 0
    count += len(board.pieces(chess.PAWN, chess.BLACK))
    count += len(board.pieces(chess.PAWN, chess.WHITE))
    count += len(board.pieces(chess.KNIGHT, chess.BLACK))
    count += len(board.pieces(chess.KNIGHT, chess.WHITE))
    count += len(board.pieces(chess.BISHOP, chess.BLACK))
    count += len(board.pieces(chess.BISHOP, chess.WHITE))
    count += len(board.pieces(chess.ROOK, chess.BLACK))
    count += len(board.pieces(chess.ROOK, chess.WHITE))
    count += len(board.pieces(chess.QUEEN, chess.BLACK))
    count += len(board.pieces(chess.QUEEN, chess.WHITE))
    return count

def get_book_move(node):
    book = chess.polyglot.open_reader(r"ProDeo292/ProDeo292/books/elo2500.bin")
    main_entry = book.find(node)
    choice = book.weighted_choice(node)
    book.close()
    return main_entry.move, choice.move

def play(board, timeLimit):
    try:
        best, choice = get_book_move(board)
        #board.push(choice)
        board.push(best)
        print(chess.pgn.Game.from_board(board)[-1])
    except IndexError:
        best = pvsearch(board, timeLimit)
        board.push(best)
        print(chess.pgn.Game.from_board(board)[-1])

def show(board):
    try:
        display(chess.svg.board(board=board,size=400,flipped=board.turn))
    except Exception:
        print(board)

def user_move(board,a,b):
    move = input("enter move: ")
    while True:
        try:
            board.push_san(move)
            break
        except Exception:
            move = input("enter move: ")

def display_ending(board):
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

def pickMover(human, side, turn):
    if not human:
        return True
    else:
        if side and turn:
            return False
        else:
            return True

def main(string, debug, human, side, timeLimit):
    board = chess.Board(str(string))
    #board = chess.variant.CrazyhouseBoard(str(string))

    while not board.is_game_over():
        show(board)
        if pickMover(human, side, board.turn):
            play(board, timeLimit)
        else:
            user_move(board, 1, 1)
        if board.is_game_over():
            break
    display_ending(board)
    return str(chess.pgn.Game.from_board(board)[-1])

timeLimit = 15
main(standard, True, False, False, timeLimit)