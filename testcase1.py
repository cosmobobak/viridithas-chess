import chess
import chess.svg
import random

board = chess.Board()

def points(board,player):
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
    if board.is_checkmate():
        rating += 10000
    if player == 'white':
        return rating
    else:
        return rating*-1

def minimax(board, node, depth, a, b, player):
    print(board, node, depth, a, b, player)
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
        print(value)
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
        print(value)
        return value

minimax(board,0,3,-1000000,1000000,'white')
