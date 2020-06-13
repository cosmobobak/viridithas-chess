import chess
import chess.svg
import random

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
    x = 0.5
    if True:
        for counter in range(64):
            try:
                if map[counter] == 'p':
                    rating += pawnSpaces[counter]*x
                elif map[counter] == 'P':
                    rating += pawnSpaces[counter]*-x
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
                    rating += knightSpaces[counter]*-x
                elif map[counter] == 'B':
                    rating += bishopSpaces[counter]*-x
                elif map[counter] == 'R':
                    rating += rookSpaces[counter]*-x
                elif map[counter] == 'Q':
                    rating += queenSpaces[counter]*-x
                elif map[counter] == 'K':
                    rating += kingSpaces[counter]*-x
                else:
                    pass
                    #print('something has gone horribly wrong')
                    #return False
            except Exception:
                continue
    '''
    #incentivises king to stay back
    ranks = string.split('/')
    rankIndex = 1
    for rank in ranks:
        if 'k' in rank:
            rating += 0.5*(9-rankIndex)
            #print(0.5*(9-rankIndex))
        if 'K' in rank:
            rating -= 0.5*(9-rankIndex)
            #print(-0.5*(9-rankIndex))
        rankIndex+=1
    '''
    #aggregates piece score

    rating += 200*(string.count('k')-string.count('K'))
    rating += 1*(string.count('p')-string.count('P'))
    rating += 3*(string.count('n')-string.count('N'))
    rating += 3.5*(string.count('b')-string.count('B'))
    rating += 9*(string.count('q')-string.count('Q'))
    rating += 5*(string.count('r')-string.count('R'))
    rating += 0.01*(board.legal_moves.count())

    #maintain castling rights incentive
    if board.has_kingside_castling_rights(chess.WHITE) and board.has_queenside_castling_rights(chess.WHITE):
        rating += -1.2
    elif board.has_kingside_castling_rights(chess.WHITE) or board.has_queenside_castling_rights(chess.WHITE):
        rating += -0.6
    else:
        rating -= -1.2
    if board.has_kingside_castling_rights(chess.BLACK) and board.has_queenside_castling_rights(chess.BLACK):
        rating += 1.2
    elif board.has_kingside_castling_rights(chess.BLACK) or board.has_queenside_castling_rights(chess.BLACK):
        rating += 0.6
    else:
        rating -= 1.2
    #try to give check
    if board.is_check():
        rating += -0.9
    if board.is_checkmate():
        rating += -10000
    #incentivises threatening pieces by worth
    #for piece in board.pieces('PAWN','WHITE'):
        #pass
    #incentivises castling
    if board.move_stack:
        move = board.peek()
        if chess.square_distance(move.from_square,move.to_square) == 2:
            if board.piece_at(move.to_square).symbol().upper() == 'K':
                rating -= (7)
        elif chess.square_distance(move.from_square,move.to_square) == 1:
            if board.piece_at(move.to_square).symbol().upper() == 'K':
                rating += 0.05
    #flip to reverse scores for minimax
    if board.turn:
        return rating*-1
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
    return min(moveRatings)

def bestMove2(board):
    moveRatings = [] #the piece values for the opponent after each move
    moves = [] #corresponding moves
    for move in board.legal_moves:
        moves.append(move)
        board.push(move)
        #print(round(bestMoveValue(board),3),round(points(board),3),move,board.board_fen())
        moveRatings.append((bestMoveValue(board)+points(board))/2)
        board.pop()

    newRatings = []
    for move in moveRatings:
        newRatings.append(move+(random.randint(1,99)/1000))
    #print(moves[newRatings.index(max(newRatings))])
    return moves[newRatings.index(max(newRatings))]

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

        else:
            board.push(bestMove2(board))

        display(chess.svg.board(board=board,size=400,flipped=True))
        #print(board)
        #print('WIN PREDICTION:',str(min([round(n+random.randint(1,30)/3,3),100.0]))+'% CHANCE OF WHITE WIN.')
        n += 5
        if not board.is_game_over():
            print(board.legal_moves)
            userMove(board)
            #board.push(bestMove2(board))
            #display(chess.svg.board(board=board,size=400,flipped=True))
            #print(board)
        else:
            print('WHITE WINS ON TURN',board.fullmove_number)
            display(chess.svg.board(board=board,size=400,flipped=True))
            blackwin = False
            #print(board)
            break
        #display(chess.svg.board(board=board,size=400,flipped=True))
    if blackwin == True:
        print('BLACK WINS ON TURN',board.fullmove_number)
        display(chess.svg.board(board=board,size=400,flipped=True))

    #treesearch
    #prune high-risk strategies from the tree

for counter in range(10):
    main()
