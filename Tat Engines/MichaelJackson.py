import chess
import chess.svg
import random

'''
CAPITAL LETTERS ARE WHITE
'''

pawnSpaces =  reversed([0,0,0,0,0,0,0,0,50,50,50,50,50,50,50,50,10,10,20,30,30,20,10,10,5,5,10,25,25,10,5,5,0,0,0,20,20,0,0,0,5,-5,-10,0,0,-10,-5,5,5,10,10,-20,-20,10,10,5,0,0,0,0,0,0,0,0])
knightSpaces = reversed([-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,0,0,0,-20,-40,-30,0,10,15,15,10,0,-30,-30,5,15,20,20,15,5,-30,-30,0,15,20,20,15,0,-30,-30,5,10,15,15,10,5,-30,-40,-20,0,5,5,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50,])
bishopSpaces = reversed([-20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,10,10,5,0,-10,-10,5,5,10,10,5,5,-10,-10,0,10,10,10,10,0,-10,-10,10,10,10,10,10,10,-10,-10,5,0,0,0,0,5,-10,-20,-10,-10,-10,-10,-10,-10,-20,])
rookSpaces = reversed([0,0,0,0,0,0,0,0,5,10,10,10,10,10,10,5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,0,0,0,5,5,0,0,0])
queenSpaces = reversed([-20,-10,-10,-5,-5,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,5,5,5,0,-10,-5,0,5,5,5,5,0,-5,0,0,5,5,5,5,0,-5,-10,5,5,5,5,5,0,-10,-10,0,5,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20])
kingSpaces = reversed([-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-20,-30,-30,-40,-40,-30,-30,-20,-10,-20,-20,-20,-20,-20,-20,-10,20,20,0,0,0,0,20,20,20,30,10,0,0,10,30,20])
kingSpacesEndgame = reversed([-50,-40,-30,-20,-20,-30,-40,-50,-30,-20,-10,0,0,-10,-20,-30,-30,-10,20,30,30,20,-10,-30,-30,-10,30,40,40,30,-10,-30,-30,-10,30,40,40,30,-10,-30,-30,-10,20,30,30,20,-10,-30,-30,-30,0,0,0,0,-30,-30,-50,-30,-30,-30,-30,-30,-30,-50])

def points(board):
    rating = 0.0
    string = board.board_fen()
    map = board.piece_map()
    x = 0
    if board.turn:
        x=x*-1
    if False:
        for counter in range(64):
            try:
                if map[counter] == 'p':
                    rating += pawnSpaces[counter]*x
                elif map[counter] == 'P':
                    rating += -pawnSpaces[counter]*x
                elif map[counter] == 'n':
                    rating += knightSpaces[counter]*x
                elif map[counter] == 'b':
                    rating += bishopSpaces[counter]*x
                elif map[counter] == 'r':
                    rating += rookSpaces[counter]*x
                elif map[counter] == 'q':
                    rating += queenSpaces[counter]*x
                elif map[counter] == 'k':
                    rating += kingSpaces[counter]*x
                elif map[counter] == 'N':
                    rating += -knightSpaces[counter]*x
                elif map[counter] == 'B':
                    rating += -bishopSpaces[counter]*x
                elif map[counter] == 'R':
                    rating += -rookSpaces[counter]*x
                elif map[counter] == 'Q':
                    rating += -queenSpaces[counter]*x
                elif map[counter] == 'K':
                    rating += -kingSpaces[counter]*x
                else:
                    pass
                    #print('something has gone horribly wrong')
                    #return False
            except Exception:
                continue

    #incentivises king to stay back
    ranks = string.split('/')
    rankIndex = 1
    y=1
    if board.turn:
        y=-1
    for rank in ranks:
        if 'k' in rank:
            rating += 0.5*(9-rankIndex)*y
        if 'K' in rank:
            rating -= 0.5*(9-rankIndex)*y
        rankIndex+=1

    #aggregates piece score
    '''
    IF WHITE:
        ADD CAPITALS, SUBTRACT LOWERCASE
    ELSE:
        ADD LOWERCASE, SUBTRACT CAPITALS
    '''
    if board.turn: #rating for the turn before, so this is 'IF BLACK:'
        rating += 200*(string.count('k')-string.count('K'))
        rating += 1*(string.count('p')-string.count('P'))
        rating += 3*(string.count('n')-string.count('N'))
        rating += 3.5*(string.count('b')-string.count('B'))
        rating += 9*(string.count('q')-string.count('Q'))
        rating += 5*(string.count('r')-string.count('R'))
    else:
        rating += -200*(string.count('k')-string.count('K'))
        rating += -1*(string.count('p')-string.count('P'))
        rating += -3*(string.count('n')-string.count('N'))
        rating += -3.5*(string.count('b')-string.count('B'))
        rating += -9*(string.count('q')-string.count('Q'))
        rating += -5*(string.count('r')-string.count('R'))

    #rating -= 0.01*(board.legal_moves.count())
    #for xmove in board.legal_moves:
        #board.push(xmove)
        #rating += 0.0005*(board.legal_moves.count())
        #board.pop()

    #maintain castling rights incentive
    if board.has_kingside_castling_rights(board.turn) and board.has_queenside_castling_rights(board.turn):
        rating += -1.2
    elif board.has_kingside_castling_rights(board.turn) or board.has_queenside_castling_rights(board.turn):
        rating += -0.6
    else:
        rating += 1.2
    if board.has_kingside_castling_rights(not board.turn) and board.has_queenside_castling_rights(not board.turn):
        rating += 1.2
    elif board.has_kingside_castling_rights(not board.turn) or board.has_queenside_castling_rights(not board.turn):
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
        #print(rating,board.peek())
        pass
    except Exception:
        pass
    return rating

def bestMoveValue(board):
    moveRatings = []
    for move in board.legal_moves:
        board.push(move)
        moveRatings.append(points(board))
        if board.is_checkmate():
            moveRatings[-1] -= 100000000
        board.pop()
    if moveRatings == []:
        return 100
    return max(moveRatings)

def bestMoveValue2(board):
    moveRatings = []
    for move in board.legal_moves:
        board.push(move)
        moveRatings.append(points(board))
        if board.is_checkmate():
            moveRatings[-1] += 100000000
        board.pop()
    if moveRatings == []:
        return 100
    return max(moveRatings)

def recurseMoveValue(depth,board):
    if depth == 1:
        #print('test: ',depth,points(board))
        return points(board)
    else:
        moveRatings = []
        for move in board.legal_moves:
            board.push(move)
            moveRatings.append(recurseMoveValue(depth-1,board))
            if board.is_checkmate():
                moveRatings[-1] += 100000000
            board.pop()
        if moveRatings == []:
            return 100
        #print('test: ',depth,max(moveRatings))
        return max(moveRatings)

def bestMove2(board):
    moveRatings = []
    moves = []
    for move in board.legal_moves:
        moves.append(move)
        board.push(move)
        moveRatings.append(-bestMoveValue2(board))
        #moveRatings.append(recurseMoveValue(3,board))
        board.pop()
    for move,moveRating in zip(moves,moveRatings):
        print(move,moveRating)
    return moves[moveRatings.index(max(moveRatings))]

def userMove(board):
    move = input("enter move: ")
    while True:
        try:
            board.push_san(move)
            break
        except Exception:
            move = input("enter move: ")

def londonMove(board,trackerArray):
    londonMoves = [chess.Move(chess.D2,chess.D4),chess.Move(chess.C1,chess.F4),]
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

def main():
    board = chess.Board()
    n = 40
    blackwin = True
    while not board.is_game_over():
        trackerArray = [False,False,False,False,False,False,False]
        board.push(bestMove2(board))
        standardValue = points(board)
        expectedValue = bestMoveValue(board)
        board.pop()
        if board.fullmove_number < 8:
            londonMove(board,trackerArray)
            '''
            print('points for: the normal move, the london move. ')
            print(round(standardValue,3),round(points(board),3))
            print('opponent expectation for: the normal move, the london move')
            print(round(expectedValue,3),round(bestMoveValue(board),3))
            '''
            if standardValue > (points(board)+0.5) or expectedValue > (bestMoveValue(board)+0.5):
                board.pop()
                board.push(bestMove2(board))
            print(board.peek())

        else:
            board.push(bestMove2(board))
            print(board.peek())

        #display(chess.svg.board(board=board,size=400,flipped=True))
        print(board)
        #print('WIN PREDICTION:',str(min([round(n+random.randint(1,30)/3,3),100.0]))+'% CHANCE OF WHITE WIN.')
        n += 5
        if not board.is_game_over():
            #print(board.legal_moves)
            userMove(board)
            #board.push(bestMove2(board))
            #display(chess.svg.board(board=board,size=400,flipped=True))
            print(board)
        elif board.is_checkmate() and not board.turn:
            print('WHITE WINS ON TURN',board.fullmove_number)
            blackwin = False
            #print(board)
            break
        #display(chess.svg.board(board=board,size=400,flipped=True))
        if board.is_game_over() and not board.is_checkmate():
            print('ABNORMAL END ON TURN',board.fullmove_number)
            blackwin = False
            if board.is_stalemate():
                print('END BY STALEMATE')
            elif board.is_insufficient_material():
                print('END BY INSUFFICIENT MATERIAL')
            elif board.is_fivefold_repetition():
                print('END BY FIVEFOLD REPETITION')
            else:
                print('END BY UNKNOWN REASON')
            break
    #print()
    #display(chess.svg.board(board=board,size=400,flipped=True))
    if blackwin == True:
        print('BLACK WINS ON TURN',board.fullmove_number)

main()
