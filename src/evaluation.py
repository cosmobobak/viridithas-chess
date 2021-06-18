from functools import lru_cache
from chess import Board, WHITE, BLACK, popcount, scan_forward
from numpy.core.numeric import binary_repr
from PSTs import PieceSquareTable
from itertools import chain

piecesquaretable = PieceSquareTable()()

p, n, b, r, q, k, P, N, B, R, Q, K = range(12)

def chessboard_static_exchange_eval(board) -> int:
    rating = popcount(board.occupied_co[BLACK] & board.pawns) * 1000
    rating -= popcount(board.occupied_co[WHITE] & board.pawns) * 1000
    rating += popcount(board.occupied_co[BLACK] & board.knights) * 3200
    rating -= popcount(board.occupied_co[WHITE] & board.knights) * 3200
    rating += popcount(board.occupied_co[BLACK] & board.bishops) * 3330
    rating -= popcount(board.occupied_co[WHITE] & board.bishops) * 3330
    rating += popcount(board.occupied_co[BLACK] & board.rooks) * 5100
    rating -= popcount(board.occupied_co[WHITE] & board.rooks) * 5100
    rating += popcount(board.occupied_co[BLACK] & board.queens) * 8800
    rating -= popcount(board.occupied_co[WHITE] & board.queens) * 8800
    return rating


#@profile
@lru_cache(maxsize=64000)
def chessboard_pst_eval(board: Board) -> int:
    white = board.occupied_co[WHITE]
    black = board.occupied_co[BLACK]
    # total = 0
    # for i in scan_forward(board.pawns & black):
    #     total += piecesquaretable[p][i]
    # for i in scan_forward(board.pawns & white):
    #     total -= piecesquaretable[P][i]
    # for i in scan_forward(board.knights & black):
    #     total += piecesquaretable[n][i]
    # for i in scan_forward(board.knights & white):
    #     total -= piecesquaretable[N][i]
    # for i in scan_forward(board.bishops & black):
    #     total += piecesquaretable[b][i]
    # for i in scan_forward(board.bishops & white):
    #     total -= piecesquaretable[B][i]
    # for i in scan_forward(board.rooks & black):
    #     total += piecesquaretable[r][i]
    # for i in scan_forward(board.rooks & white):
    #     total -= piecesquaretable[R][i]
    # for i in scan_forward(board.queens & black):
    #     total += piecesquaretable[q][i]
    # for i in scan_forward(board.queens & white):
    #     total -= piecesquaretable[Q][i]
    # for i in scan_forward(board.kings & black):
    #     total += piecesquaretable[k][i]
    # for i in scan_forward(board.kings & white):
    #     total -= piecesquaretable[K][i]
    # return total
    return sum(chain(
        (piecesquaretable[p][i] for i in scan_forward(
            board.pawns & black)),
        (-piecesquaretable[P][i] for i in scan_forward(
            board.pawns & white)),
        (piecesquaretable[n][i] for i in scan_forward(
            board.knights & black)),
        (-piecesquaretable[N][i] for i in scan_forward(
            board.knights & white)),
        (piecesquaretable[b][i] for i in scan_forward(
            board.bishops & black)),
        (-piecesquaretable[B][i] for i in scan_forward(
            board.bishops & white)),
        (piecesquaretable[r][i] for i in scan_forward(
            board.rooks & black)),
        (-piecesquaretable[R][i] for i in scan_forward(
            board.rooks & white)),
        (piecesquaretable[q][i] for i in scan_forward(
            board.queens & black)),
        (-piecesquaretable[Q][i] for i in scan_forward(
            board.queens & white)),
        (piecesquaretable[k][i] for i in scan_forward(
            board.kings & black)),
        (-piecesquaretable[K][i] for i in scan_forward(
            board.kings & white))))
