import chess
import chess.svg
import random

def pointsKermit(board):
    rating = 0.0
    string = board.board_fen()
    map = board.piece_map()

    #incentivises king to stay back
    ranks = string.split('/')
    rankIndex = 1
    for rank in ranks:
        if 'k' in rank:
            rating += 0.5*(9-rankIndex)
        if 'K' in rank:
            rating -= 0.5*(9-rankIndex)
        rankIndex+=1

    #aggregates piece score
    '''
    IF WHITE:
        ADD CAPITALS, SUBTRACT LOWERCASE
    ELSE:
        ADD LOWERCASE, SUBTRACT CAPITALS
    '''
    rating += 200*(string.count('k')-string.count('K'))
    rating += 1*(string.count('p')-string.count('P'))
    rating += 3*(string.count('n')-string.count('N'))
    rating += 3.5*(string.count('b')-string.count('B'))
    rating += 9*(string.count('q')-string.count('Q'))
    rating += 5*(string.count('r')-string.count('R'))
    #maintain castling rights incentive
    if board.has_kingside_castling_rights(True) and board.has_queenside_castling_rights(True):
        rating += -1.2
    elif board.has_kingside_castling_rights(True) or board.has_queenside_castling_rights(True):
        rating += -0.6
    else:
        rating += 1.2
    if board.has_kingside_castling_rights(False) and board.has_queenside_castling_rights(False):
        rating += 1.2
    elif board.has_kingside_castling_rights(False) or board.has_queenside_castling_rights(False):
        rating += 0.6
    else:
        rating += -1.2
    #try to give check
    if board.is_check():
        rating += 0.9
    if board.is_checkmate():
        rating += 10000
    if board.is_fivefold_repetition():
        rating += -20000
    #incentivises castling
    if board.move_stack:
        move = board.peek()
        if chess.square_distance(move.from_square,move.to_square) == 2:
            if board.piece_at(move.to_square).symbol().upper() == 'K':
                rating += (7)
        elif chess.square_distance(move.from_square,move.to_square) == 1:
            if board.piece_at(move.to_square).symbol().upper() == 'K':
                rating -= 0.05
    try:
        pass
    except Exception:
        pass
    return rating

def minimax(depth,board,player): #takes a board state, returns a rating
    if depth == 1 or board.is_game_over():
        return pointsKermit(board)*player
    else:
        ratings = []
        moveable = False
        for move in board.legal_moves:
            board.push(move)
            ratings.append(minimax(depth-1,board,player))
            board.pop()
            moveable = True
        if player == 1:
            return min(ratings)
        else:
            return max(ratings)

board = chess.Board('r2qk2r/pb4pp/1n2Pb2/2B2Q2/p1p5/2P5/2B2PPP/RN2R1K1 w - - 1 0')

def moveKermit(board):
    if board.turn:
        turn = 1
    else:
        turn = -1
    moves = []
    moveRatings = []
    for move in board.legal_moves:
        moves.append(move)
        board.push(move)
        moveRatings.append(minimax(3,board,turn))
        board.pop()
    for move,moveRating in zip(moves,moveRatings):
        print(move,moveRating)
    board.push(moves[moveRatings.index(min(moveRatings))])

def usermoveKermit(board):
    move = input("enter move: ")
    while True:
        try:
            board.push_san(move)
            break
        except Exception:
            move = input("enter move: ")

while not board.is_game_over():
    display(chess.svg.board(board=board,size=400,flipped=True))
    moveKermit(board)
display(chess.svg.board(board=board,size=400,flipped=True))
