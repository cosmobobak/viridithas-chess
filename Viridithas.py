import chess
import chess.svg
import chess.pgn
import chess.polyglot
import chess.syzygy
import random
import chess.variant
import time
#import line_profiler
from operator import itemgetter
#import requests
#import os
#from flask import Flask, jsonify
#from flask import url_for
#from dotenv import load_dotenv
#from authlib.integrations.flask_client import OAuth
if True:
    '''
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")
    print(app.secret_key)
    app.config['LICHESS_CLIENT_ID'] =  os.getenv("LICHESS_CLIENT_ID")
    app.config['LICHESS_CLIENT_SECRET'] = os.getenv("LICHESS_CLIENT_SECRET")
    app.config['LICHESS_ACCESS_TOKEN_URL'] = 'https://oauth.lichess.org/oauth'
    app.config['LICHESS_AUTHORIZE_URL'] = 'https://oauth.lichess.org/oauth/authorize'

    oauth = OAuth(app)
    oauth.register('lichess')

    @app.route('/')
    def login():
        redirect_uri = url_for("authorize", _external=True)
        """
        If you need to append scopes to your requests, add the `scope=...` named argument
        to the `.authorize_redirect()` method. For admissible values refer to https://lichess.org/api#section/Authentication.
        Example with scopes for allowing the app to read the user's email address:
        `return oauth.lichess.authorize_redirect(redirect_uri, scope="email:read")`
        """
        return oauth.lichess.authorize_redirect(redirect_uri)

    @app.route('/authorize')
    def authorize():
        token = oauth.lichess.authorize_access_token()
        bearer = token['access_token']
        headers = {'Authorization': f'Bearer {bearer}'}
        response = requests.get("https://lichess.org/api/account", headers=headers)
        return jsonify(**response.json())

    if __name__ == '__main__':
        app.run()
    '''

whiteTime = 0.0

variations = dict()

table = dict()
#this will be a transposition table, storing evaluations, and the depth at which the evaluation was calculated, keyed by the Zobrist hash.

if True:
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

def evaluate(board, depth, endgame):
    if board.turn:
        mod = 1
    else:
        mod = -1

    if board.is_checkmate():
        return 1000000.0*(depth+1)*mod
    if board.is_repetition(2) or board.can_claim_fifty_moves():
        return -20001.0*mod

    rating = 0.0
    rating += sum([pawnSpacesB[i]+1000 for i in board.pieces(chess.PAWN, chess.BLACK)])-sum([pawnSpacesW[i]+1000 for i in board.pieces(chess.PAWN, chess.WHITE)])
    rating += sum([knightSpacesB[i]+3200 for i in board.pieces(chess.KNIGHT, chess.BLACK)])-sum([knightSpacesW[i]+3200 for i in board.pieces(chess.KNIGHT, chess.WHITE)])
    rating += sum([bishopSpacesB[i]+3330 for i in board.pieces(chess.BISHOP, chess.BLACK)])-sum([bishopSpacesW[i]+3330 for i in board.pieces(chess.BISHOP, chess.WHITE)])
    rating += sum([rookSpacesB[i]+5100 for i in board.pieces(chess.ROOK, chess.BLACK)])-sum([rookSpacesW[i]+5100 for i in board.pieces(chess.ROOK, chess.WHITE)])
    rating += sum([queenSpacesB[i]+8800 for i in board.pieces(chess.QUEEN, chess.BLACK)])-sum([queenSpacesW[i]+8800 for i in board.pieces(chess.QUEEN, chess.WHITE)])
    if endgame:
        rating += sum([kingSpacesEndgameB[i] for i in board.pieces(chess.KING, chess.BLACK)])-sum([kingSpacesEndgameW[i] for i in board.pieces(chess.KING, chess.WHITE)])
        #if pieceCount(board) <= 3:
            #with chess.syzygy.open_tablebase(r'C:\Users\Cosmo\Documents\GitHub\Chess\3-4-5piecesSyzygy\3-4-5') as tablebase:
                #WDL = tablebase.probe_wdl(board)
                #return WDL*10000*board.turn
    else:
        rating += sum([kingSpacesB[i] for i in board.pieces(chess.KING, chess.BLACK)])-sum([kingSpacesW[i] for i in board.pieces(chess.KING, chess.WHITE)])
    return rating*0.001

def orderedMoves(board, oldcuts):
    cuts = []
    takes = []
    last = []

    for move in board.legal_moves:
        if move.uci() in oldcuts:
            cuts.append(move)
        elif board.is_capture(move):
            takes.append(move)
        else:
            last.append(move)

    return cuts + takes + last

def isLateCandidate(depth, node, move, set):
    if depth < 3:
        return False
    if node.is_capture(move):
        return False
    if move.promotion:
        return False
    if move in set[0:2]:
        return False
    if node.is_check():
        return False
    if node.gives_check(move):
        return False
    return True

def pvs(node, depth, a, b, colour):
    if depth <= 0:
        return colour * evaluate(node, depth, False)
    if node.is_game_over():
        return colour * evaluate(node, depth, False)

    if not node.is_check():
        node.push(chess.Move.null())
        value = -pvs(node, depth - 3, -b, -a, -colour)
        a = max(a, value)
        node.pop()
        if a >= b:
            return a

    moves = orderedMoves(node, [])
    firstmove = True
    for i, move in enumerate(moves):
        node.push(move)
        if firstmove:
            value = -pvs(node, depth - 1, -b, -a, -colour)
            firstmove = False
        else:
            value = -pvs(node, depth - 1, -a - 1, -a, -colour)
            if a < value and value < b:
                value = -pvs(node, depth - 1, -b, -value, -colour)
        a = max(a, value)
        node.pop()
        if a >= b:
            break
    return a

def pvsTest(node, depth, a, b, colour):
    if depth <= 0:
        return colour * evaluate(node, depth, False)
    if node.is_game_over():
        return colour * evaluate(node, depth, False)

    #NULLMOVE PRUNING
    if not node.is_check():
        node.push(chess.Move.null())
        value = -pvsTest(node, depth - 3, -b, -a, -colour)
        a = max(a, value)
        node.pop()
        if a >= b:
            return a

    moves = orderedMoves(node) #MOVE ORDERING
    firstmove = True
    for i, move in enumerate(moves):
        node.push(move)
        if firstmove:
            value = -pvsTest(node, depth - 1, -b, -a, -colour)
            firstmove = False
        else:
            value = -pvsTest(node, depth - 1, -a - 1, -a, -colour) #NULLWINDOW SEARCH
            if a < value and value < b:
                value = -pvsTest(node, depth - 1, -b, -value, -colour) #RE-SEARCH ON FAIL
        a = max(a, value)
        node.pop()
        if a >= b:
            break
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
    a, b = -1337000, 1337000
    colour = node.turn
    if colour:
        colour = 1
    else:
        colour = -1
    endgame = False
    if pieceCount(node) <= 6:
        endgame = True

    moves = orderedMoves(node, [])
    values = [0.0]*len(moves)

    while timeLimit > time.time()-startTime:
        for i, move in enumerate(moves):
            node.push(move)
            values[i] = pvs(node, depth, a, b, colour)
            node.pop()
            if timeLimit < time.time()-startTime:
                return moves[0]
        moves, values = moveSort(moves, values)
        showIterationData(node, moves, values, depth, startTime)
        depth += 1
    return moves[0]

def testsearch(node, timeLimit):
    startTime = time.time()
    depth = 1
    a, b = -1337000, 1337000
    colour = node.turn
    if colour:
        colour = 1
    else:
        colour = -1
    endgame = False
    if pieceCount(node) <= 6:
        endgame = True

    moves = orderedMoves(node, [])
    values = [0.0]*len(moves)

    while timeLimit > time.time()-startTime:
        for i, move in enumerate(moves):
            node.push(move)
            values[i] = pvsTest(node, depth, a, b, colour)
            node.pop()
            if timeLimit < time.time()-startTime:
                return moves[0]
        moves, values = moveSort(moves, values)
        showIterationData(node, moves, values, depth, startTime)
        depth += 1
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

def getBookMove(node):
    book = chess.polyglot.open_reader(r"ProDeo292/ProDeo292/books/elo2500.bin")
    main_entry = book.find(node)
    choice = book.weighted_choice(node)
    book.close()
    return main_entry.move, choice.move

def play(board, timeLimit):
    start = time.time()
    moves = orderedMoves(board, [])
    try:
        best, choice = getBookMove(board)
        board.push(choice)
        print(chess.pgn.Game.from_board(board)[-1])
    except Exception:
        best = pvsearch(board, timeLimit)
        #best2 = testsearch(board, timeLimit)
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
    board = chess.Board(str(string))
    win = 1

    boardArrays = []
    ratingArrays = []

    while not board.is_game_over():
        show(board)
        play(board,timeLimit)
        #usermoveKermit(board,1,1)
        if board.is_game_over():
            break
        show(board)
        #play(board,timeLimit)
        usermoveKermit(board,1,1)
    endingPrinter(board)
    return str(chess.pgn.Game.from_board(board)[-1])

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

test = '7b/3bkp1p/4p3/1n6/3P4/3RP3/2rn1PPP/R5K1 w - - 0 1'

timeLimit = 20
stacks = []
for i, opening in enumerate(openings):
    stacks.append(main(standard, True, True, True, timeLimit))
    print('time elapsed while thinking:',whiteTime)
    print(stacks[i])

filename = 'games'+str(timeLimit)+'.txt'
with open(filename, 'w') as games:
    for i, game in enumerate(stacks):
        games.write(names[i]+' '+game+'\n')
