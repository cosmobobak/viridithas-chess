import chess
import chess.svg
import random

board = chess.Board()

def points(board,player):
    rating = 0.0
    for letter in board.board_fen():
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
    if board.is_checkmate():
        rating += 10000
    if player == 'white':
        return rating
    else:
        return rating*-1

def eval(board,player):
    rating = 0.0
    string = board.board_fen()
    rating += 200*(string.count(k)-string.count(K))
    rating += 1*(string.count(p)-string.count(P))
    rating += 3*(string.count(n)-string.count(N))
    rating += 3.5*(string.count(b)-string.count(B))
    rating += 9*(string.count(q)-string.count(Q))
    rating += 5*(string.count(r)-string.count(R))
    rating -= 0.1*(board.legal_moves.count())

def minimax(board, node, depth, a, b, player):
    if depth == 0 or node >= depth:
        return points(board,player)
    if player == 'white':
        value = -100000
        for move in board.legal_moves:
            board.push(move)
            value = max([value, minimax(board, node, depth-1, a, b, 'black')])
            a = max([a,value])
            board.pop()
            if a>=b:
                break
        return value
    else:
        value = 100000
        for move in board.legal_moves:
            board.push(move)
            value = min([value, minimax(board, node, depth-1, a, b, 'white')])
            b = min(b,value)
            board.pop()
            if b<=a:
                break
        return value

def userMove(board):
    move = input("enter move: ")
    while True:
        try:
            board.push_san(move)
            break
        except Exception:
            move = input("enter move: ")

def bestMoveMinimax(board,player):
    moveRatings = [] #the piece values for the opponent after each move
    moves = [] #corresponding moves

    for move in board.legal_moves:
        board.push(move)
        moves.append(move)
        moveRatings.append(minimax(board,0,4,-1000000,1000000,player))
        board.pop()

    return moves[moveRatings.index(max(moveRatings))]

display(chess.svg.board(board=board,size=400,flipped=True))

player = input('enter side: ')
while player not in ['white','black']:
    player = input('enter side: ')

if player != 'white':
    userMove(board)

while not board.is_game_over():
    board.push(bestMoveMinimax(board,player))
    display(chess.svg.board(board=board,size=400,flipped=True))
    print(board.legal_moves)
    userMove(board)
