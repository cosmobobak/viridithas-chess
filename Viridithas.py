import chess
import chess.svg
import chess.pgn
import chess.polyglot
import chess.syzygy
import random
import chess.variant
import time
import operator
#import line_profiler
from operator import itemgetter
import requests
import os
from flask import Flask, jsonify
from flask import url_for
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth

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


whiteTime = 0.0

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

#@profile
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

def antiEval(board,depth,endgame):
    return -evaluate(board,depth,endgame)

#@profile
def orderedMoves(board):
    first = []
    last = []

    for move in board.legal_moves:
        if board.is_capture(move):
            first.append(move)
        else:
            last.append(move)

    return first + last

#@profile
def negamax_killer(node, depth, a, b, colour, endgame):
    if depth == 0 or node.is_game_over():
        return colour * evaluate(node, depth, endgame)
    value = -1337000.0
    moves = orderedMoves(node)
    for move in moves:
        node.push(move)
        value = max(value, -negamax_killer(node, depth - 1, -b, -a, -colour, endgame))
        a = max(a, value)
        node.pop()
        if a >= b:
            break
    return value

#@profile
def pvs(node, depth, a, b, colour, endgame):
    if depth == 0 or node.is_game_over():
        return colour * evaluate(node, depth, endgame)
    moves = orderedMoves(node)
    firstmove = True
    for move in moves:
        node.push(move)
        if firstmove:
            value = -pvs(node, depth - 1, -b, -a, -colour, endgame)
            firstmove = False
        else:
            value = -pvs(node, depth - 1, -a - 1, -a, -colour, endgame)
            if a < value and value < b:
                value = -pvs(node, depth - 1, -b, -value, -colour, endgame)
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
    print(board.san(moves[0]),'|',round(values[0], 3),'|',str(round(time.time()-startTime, 2))+'s at depth',depth)

def search(node, timeLimit):
    startTime = time.time()
    depth = 1
    a, b = -1337000, 1337000
    colour = node.turn
    endgame = False
    if pieceCount(node) <= 6:
        endgame = True

    moves = orderedMoves(node)
    values = [0.0]*len(moves)

    while timeLimit > time.time()-startTime:
        for i, move in enumerate(moves):
            node.push(move)
            values[i] = negamax_killer(node, depth, a, b, colour, endgame)
            node.pop()
            if timeLimit < time.time()-startTime:
                return moves[0]
        moves, values = moveSort(moves, values)
        showIterationData(node, moves, values, depth, startTime)
        depth += 1
    return moves[0]

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

    moves = orderedMoves(node)
    values = [0.0]*len(moves)

    while timeLimit > time.time()-startTime:
        for i, move in enumerate(moves):
            node.push(move)
            values[i] = pvs(node, depth, a, b, colour, endgame)
            node.pop()
            if timeLimit < time.time()-startTime:
                return moves[0]
        moves, values = moveSort(moves, values)
        showIterationData(node, moves, values, depth, startTime)
        depth += 1
    return moves[0]

def minimax(node, depth, colour, tablebase):
    DTZ = tablebase.probe_dtz(node)
    if DTZ == 0 or depth == 0:
        return 0
    if colour:
        value = -123456789
        for move in node.legal_moves:
            value = max(value, minimax(node, depth - 1, False, tablebase))
        return value
    else:
        value = 123456789
        for move in node.legal_moves:
            value = min(value, minimax(node, depth - 1, True, tablebase))
        return value

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

#@profile
def pushMove(board, depth, debug):
    start = time.time()

    moves = []
    for move in board.legal_moves:
        moves.append(move)

    endgame = False
    if pieceCount(board) <= 6:
        endgame = True

    if board.turn:
        turn = 1
    else:
        turn = -1

    boards = []
    moveRatings = []
    RESET = board.copy()

    try:
        best = getBookMove(board)
        board.push(best)
        print(best)
        print(chess.pgn.Game.from_board(board)[-1])
    except Exception:
        for move in moves:
            board.push(move)
            moveRatings.append(negamax_killer(board, depth, -1337000, 1337000, turn, endgame))
            board.pop()

        if debug:
            moves, moveRatings = moveSort(moves, moveRatings)
            moveLister(moves)
            print(moveRatings)

        best = moves[moveRatings.index(min(moveRatings))]

        board.push(best)
        print(best)
        print(chess.pgn.Game.from_board(board)[-1])

    end = time.time()
    global whiteTime
    print(end-start)
    whiteTime += (end-start)
    return boards,moveRatings

def getBookMove(node):
    book = chess.polyglot.open_reader(r"C:\Users\Cosmo\Documents\GitHub\Chess\ProDeo292\ProDeo292\books\elo2500.bin")
    main_entry = book.find(node)
    return main_entry.move

#@profile
def play(board, timeLimit):
    moves = orderedMoves(board)
    try:
        best = getBookMove(board)
        board.push(best)
        print(best)
        print(chess.pgn.Game.from_board(board)[-1])
    except Exception:
        best1 = pvsearch(board, timeLimit)
        #best2 = search(board,timeLimit)
        best = best1
        board.push(best)
        print(best)
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

def main(string,rounds,debug,human,side,depth):
    for game in range(rounds):
        board = chess.Board(str(string))
        win = 1

        boardArrays = []
        ratingArrays = []

        while not board.is_game_over():
            show(board)

            #boards,ratings = pushMove(board,depth,debug)
            play(board,10)
            #usermoveKermit(board,1,1)

            #boardArrays.append(boards)
            #ratingArrays.append(ratings)

            if board.is_game_over():
                break

            show(board)

            #boards,ratings = pushMove(board,depth,debug)
            play(board,10)
            #usermoveKermit(board,1,1)

            #boardArrays.append(boards)
            #ratingArrays.append(ratings)

        endingPrinter(board)

    return boardArrays,ratingArrays,board.move_stack

standard = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

whiteMate1 = '8/8/8/8/8/4R1K1/8/6k1 w - - 0 1'
blackMate1 = '8/8/8/8/8/4r1k1/8/6K1 b - - 0 1'

openings = ['rnbqkbnr/pppppppp/8/8/8/6P1/PPPPPP1P/RNBQKBNR b KQkq - 0 1',
            'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
            'rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1',
            'rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq - 1 1',
            'rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq c3 0 1',
            'rnbqkbnr/pppppppp/8/8/8/N7/PPPPPPPP/R1BQKBNR b KQkq - 1 1',
            'rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2']

#g3
#e4
#d4
#Nf3
#c4
#Na3
#sicilian (1. e4 c5)
'''
resp = requests.get('https://todolist.example.com/tasks/')
if resp.status_code != 200:
    # This means something went wrong.
    raise ApiError('GET /tasks/ {}'.format(resp.status_code))
for todo_item in resp.json():
    print('{} {}'.format(todo_item['id'], todo_item['summary']))
'''

headers = {
    'Authorization': 'Bearer lc03sMGM7WpfsymS',
}

response = requests.get('https://lichess.org/api/account', headers=headers)

print(response)

if True:
    test = '8/2p5/8/5p1p/2p2PPP/1k6/1p6/1K6 w - - 0 1'

    boardArrays,ratingArrays,stack = main(test,1,True,True,True,4)
    print('time elapsed while thinking:',whiteTime)
    print(stack)
