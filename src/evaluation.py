from functools import lru_cache
from chess import BB_KNIGHT_ATTACKS, BB_RANK_1, BB_RANK_2, BB_RANK_3, BB_RANK_4, BB_RANK_5, BB_RANK_6, BB_RANK_7, BB_RANK_8, Board, Move, WHITE, BLACK, lsb, popcount, scan_forward, BB_PAWN_ATTACKS
import chess
from PSTs import PAWN_NORM, mg_pst, eg_pst, piece_values
from itertools import chain

p, n, b, r, q, k, P, N, B, R, Q, K = range(12)

MIDGAME = 0

PAWN_VALUE: int = piece_values[MIDGAME][0] * PAWN_NORM
KNIGHT_VALUE: int = piece_values[MIDGAME][1] * PAWN_NORM
BISHOP_VALUE: int = piece_values[MIDGAME][2] * PAWN_NORM
ROOK_VALUE: int = piece_values[MIDGAME][3] * PAWN_NORM
QUEEN_VALUE: int = piece_values[MIDGAME][4] * PAWN_NORM
MATE_VALUE: int = 1000000000
FUTILITY_MARGIN: int = BISHOP_VALUE + 100
FUTILITY_MARGIN_2: int = ROOK_VALUE + 100
FUTILITY_MARGIN_3: int = FUTILITY_MARGIN + FUTILITY_MARGIN_2
MOBILITY_FACTOR: int = 10
ATTACK_FACTOR: int = 10
KING_SAFETY_FACTOR: int = 10
SPACE_FACTOR: int = 10

def see_eval(board) -> int:
    rating =  popcount(board.occupied_co[BLACK] & board.pawns)   * PAWN_VALUE
    rating -= popcount(board.occupied_co[WHITE] & board.pawns)   * PAWN_VALUE
    rating += popcount(board.occupied_co[BLACK] & board.knights) * KNIGHT_VALUE
    rating -= popcount(board.occupied_co[WHITE] & board.knights) * KNIGHT_VALUE
    rating += popcount(board.occupied_co[BLACK] & board.bishops) * BISHOP_VALUE
    rating -= popcount(board.occupied_co[WHITE] & board.bishops) * BISHOP_VALUE
    rating += popcount(board.occupied_co[BLACK] & board.rooks)   * ROOK_VALUE
    rating -= popcount(board.occupied_co[WHITE] & board.rooks)   * ROOK_VALUE
    rating += popcount(board.occupied_co[BLACK] & board.queens)  * QUEEN_VALUE
    rating -= popcount(board.occupied_co[WHITE] & board.queens)  * QUEEN_VALUE
    return rating

def pst_eval(board: Board) -> int:
    white = board.occupied_co[WHITE]
    black = board.occupied_co[BLACK]
    return sum(chain(
        (mg_pst[p][i] for i in scan_forward(
            board.pawns & black)),
        (-mg_pst[P][i] for i in scan_forward(
            board.pawns & white)),
        (mg_pst[n][i] for i in scan_forward(
            board.knights & black)),
        (-mg_pst[N][i] for i in scan_forward(
            board.knights & white)),
        (mg_pst[b][i] for i in scan_forward(
            board.bishops & black)),
        (-mg_pst[B][i] for i in scan_forward(
            board.bishops & white)),
        (mg_pst[r][i] for i in scan_forward(
            board.rooks & black)),
        (-mg_pst[R][i] for i in scan_forward(
            board.rooks & white)),
        (mg_pst[q][i] for i in scan_forward(
            board.queens & black)),
        (-mg_pst[Q][i] for i in scan_forward(
            board.queens & white)),
        (mg_pst[k][i] for i in scan_forward(
            board.kings & black)),
        (-mg_pst[K][i] for i in scan_forward(
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
