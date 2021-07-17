from functools import lru_cache
from chess import BB_KNIGHT_ATTACKS, BB_RANK_1, BB_RANK_2, BB_RANK_3, BB_RANK_4, BB_RANK_5, BB_RANK_6, BB_RANK_7, BB_RANK_8, Board, Move, WHITE, BLACK, lsb, popcount, scan_forward, BB_PAWN_ATTACKS
import chess
from PSTs import PieceSquareTable
from itertools import chain

piecesquaretable = PieceSquareTable()()

p, n, b, r, q, k, P, N, B, R, Q, K = range(12)

PAWN_VALUE = 1000
KNIGHT_VALUE = 3200
BISHOP_VALUE = 3330
ROOK_VALUE = 5100
QUEEN_VALUE = 8800
MATE_VALUE = 1000000000
FUTILITY_MARGIN = BISHOP_VALUE + 100
MOBILITY_FACTOR = 10
ATTACK_FACTOR = 10
KING_SAFETY_FACTOR = 10
SPACE_FACTOR = 10
PIECE_VALUES = [0, 1000, 3200, 3330, 5100, 8800, 2000000]

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
 
def chessboard_pst_eval(board: Board) -> int:
    white = board.occupied_co[WHITE]
    black = board.occupied_co[BLACK]
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

def piece_attack_counts(board: Board):
    white_pawn_attacks = sum(popcount(BB_PAWN_ATTACKS[WHITE][sq] & board.occupied_co[BLACK]) for sq in scan_forward(
        board.pawns & board.occupied_co[WHITE]))
    black_pawn_attacks = sum(popcount(BB_PAWN_ATTACKS[BLACK][sq] & board.occupied_co[WHITE]) for sq in scan_forward(
        board.pawns & board.occupied_co[BLACK]))
    white_knight_attacks = sum(popcount(BB_KNIGHT_ATTACKS[sq] & board.occupied_co[BLACK]) for sq in scan_forward(
        board.knights & board.occupied_co[WHITE]))
    black_knight_attacks = sum(popcount(BB_KNIGHT_ATTACKS[sq] & board.occupied_co[WHITE]) for sq in scan_forward(
        board.knights & board.occupied_co[BLACK]))
    white_bishop_attacks = sum(popcount(board.attacks_mask(sq) & board.occupied_co[BLACK] & (board.kings | board.queens | board.rooks)) for sq in scan_forward(
        board.bishops & board.occupied_co[WHITE]))
    black_bishop_attacks = sum(popcount(board.attacks_mask(sq) & board.occupied_co[WHITE] & (board.kings | board.queens | board.rooks)) for sq in scan_forward(
        board.bishops & board.occupied_co[BLACK]))
    white_rook_attacks = sum(popcount(board.attacks_mask(sq) & board.occupied_co[BLACK] & (board.kings | board.queens)) for sq in scan_forward(
        board.bishops & board.occupied_co[WHITE]))
    black_rook_attacks = sum(popcount(board.attacks_mask(sq) & board.occupied_co[WHITE] & (board.kings | board.queens)) for sq in scan_forward(
        board.bishops & board.occupied_co[BLACK]))
    white_queen_attacks = sum(popcount(board.attacks_mask(sq) & board.occupied_co[BLACK] & board.kings) for sq in scan_forward(
        board.bishops & board.occupied_co[WHITE]))
    black_queen_attacks = sum(popcount(board.attacks_mask(sq) & board.occupied_co[WHITE] & board.kings) for sq in scan_forward(
        board.bishops & board.occupied_co[BLACK]))
    black = black_pawn_attacks + black_knight_attacks + black_bishop_attacks + black_rook_attacks + black_queen_attacks
    white = white_pawn_attacks + white_knight_attacks + white_bishop_attacks + white_rook_attacks + white_queen_attacks
    return black - white

def mobility(board: Board):
    mobility = 0
    if board.turn == WHITE:
        mobility -= sum(1 for m in board.generate_pseudo_legal_moves() if not board.is_into_check(m))
        board.push(Move.null())
        mobility += sum(1 for m in board.generate_pseudo_legal_moves() if not board.is_into_check(m))
        board.pop()
    else:
        mobility += sum(1 for m in board.generate_pseudo_legal_moves() if not board.is_into_check(m))
        board.push(Move.null())
        mobility -= sum(1 for m in board.generate_pseudo_legal_moves() if not board.is_into_check(m))
        board.pop()
    return mobility

def king_safety(board: Board):
    wpieces = board.occupied_co[WHITE]
    bpieces = board.occupied_co[BLACK]
    wkingloc = lsb(board.kings & wpieces)
    bkingloc = lsb(board.kings & bpieces)
    safety: float = 0
    safety += sum(chess.square_distance(bkingloc, sq) * 2 for sq in scan_forward(board.queens & wpieces))
    safety -= sum(chess.square_distance(wkingloc, sq) * 2 for sq in scan_forward(board.queens & bpieces))
    safety += sum(chess.square_distance(bkingloc, sq) / 2 for sq in scan_forward(board.bishops & wpieces))
    safety -= sum(chess.square_distance(wkingloc, sq) / 2 for sq in scan_forward(board.bishops & bpieces))
    safety += sum(chess.square_distance(bkingloc, sq) / 2 for sq in scan_forward(board.rooks & wpieces))
    safety -= sum(chess.square_distance(wkingloc, sq) / 2 for sq in scan_forward(board.rooks & bpieces))
    safety += sum(chess.square_distance(bkingloc, sq) for sq in scan_forward(board.knights & wpieces))
    safety -= sum(chess.square_distance(wkingloc, sq) for sq in scan_forward(board.knights & bpieces))
    return safety

def space(board: Board):
    w_area = BB_RANK_1 | BB_RANK_2 | BB_RANK_3 | BB_RANK_4
    b_area = BB_RANK_8 | BB_RANK_7 | BB_RANK_6 | BB_RANK_5
    space = 0
    space -= sum(popcount(BB_PAWN_ATTACKS[WHITE][sq] & b_area) for sq in scan_forward(
        board.pawns & board.occupied_co[WHITE]))
    space += sum(popcount(BB_PAWN_ATTACKS[BLACK][sq] & w_area) for sq in scan_forward(
        board.pawns & board.occupied_co[BLACK]))
    space -= sum(popcount(BB_KNIGHT_ATTACKS[sq] & b_area) for sq in scan_forward(
        board.knights & board.occupied_co[WHITE]))
    space += sum(popcount(BB_KNIGHT_ATTACKS[sq] & w_area) for sq in scan_forward(
        board.knights & board.occupied_co[BLACK]))
    return space
