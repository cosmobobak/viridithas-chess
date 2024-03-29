from functools import lru_cache
from chess import BB_FILE_A, BB_KNIGHT_ATTACKS, BB_RANK_1, BB_RANK_2, BB_RANK_3, BB_RANK_4, BB_RANK_5, BB_RANK_6, BB_RANK_7, BB_RANK_8, Board, Move, WHITE, BLACK, lsb, popcount, scan_forward, BB_PAWN_ATTACKS
import chess
from PSTs import PAWN_NORM, mg_pst, eg_pst, piece_values
from itertools import chain

from legal_move_counting import count_legal_moves

p, n, b, r, q, k, P, N, B, R, Q, K = range(12)

MIDGAME = 0
ENDGAME = 1

PAWN_VALUE: float = piece_values[MIDGAME][0] * PAWN_NORM
KNIGHT_VALUE: float = piece_values[MIDGAME][1] * PAWN_NORM
BISHOP_VALUE: float = piece_values[MIDGAME][2] * PAWN_NORM
ROOK_VALUE: float = piece_values[MIDGAME][3] * PAWN_NORM
QUEEN_VALUE: float = piece_values[MIDGAME][4] * PAWN_NORM
MATE_VALUE: int = 1000000000
INF: int = MATE_VALUE * 100
FUTILITY_MARGIN: int = BISHOP_VALUE + 100
FUTILITY_MARGIN_2: int = ROOK_VALUE + 100
FUTILITY_MARGIN_3: int = FUTILITY_MARGIN + FUTILITY_MARGIN_2
MOBILITY_FACTOR: int = 1
ATTACK_FACTOR: int = 10
KING_SAFETY_FACTOR: int = 10
SPACE_FACTOR: int = 10

def see_eval(board) -> float:
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

PawnPhase = 0.1
KnightPhase = 1.0
BishopPhase = 1.0
RookPhase = 2.0
QueenPhase = 4.0
TotalPhase = KnightPhase*4 + BishopPhase*4 + RookPhase*4 + QueenPhase*2 + PawnPhase*16

def game_stage(board: Board) -> float:
    # returns a float from 0->1, where 1 is full endgame and 0 is full midgame

    phase = TotalPhase

    wp = popcount(board.pawns & board.occupied_co[WHITE])
    bp = popcount(board.pawns & board.occupied_co[BLACK])
    wn = popcount(board.knights & board.occupied_co[WHITE])
    bn = popcount(board.knights & board.occupied_co[BLACK])
    wb = popcount(board.bishops & board.occupied_co[WHITE])
    bb = popcount(board.bishops & board.occupied_co[BLACK])
    wr = popcount(board.rooks & board.occupied_co[WHITE])
    br = popcount(board.rooks & board.occupied_co[BLACK])
    wq = popcount(board.queens & board.occupied_co[WHITE])
    bq = popcount(board.queens & board.occupied_co[BLACK])

    phase -= wp * PawnPhase      # White pawns
    phase -= wn * KnightPhase    # White knights
    phase -= wb * BishopPhase    # White bishops
    phase -= wr * RookPhase      # White rooks
    phase -= wq * QueenPhase     # White queens
    phase -= bp * PawnPhase      # Black pawns
    phase -= bn * KnightPhase    # Black knights
    phase -= bb * BishopPhase    # Black bishops
    phase -= br * RookPhase      # Black rooks
    phase -= bq * QueenPhase     # Black queens

    return phase / TotalPhase

def compute_merged_pst(board: Board) -> "list[list[float]]":
    phase = game_stage(board)

    if not (0 <= phase <= 1):
        print(f"{phase}, ")
        raise ValueError("invalid phase")

    print(f"{phase:.3f} endgame, {1-phase:.3f} midgame.")

    out_pst = [[(egval * phase + mgval * (1 - phase)) / 2 for mgval, egval in zip(mgrow, egrow)]
               for mgrow, egrow in zip(mg_pst, eg_pst)]

    return out_pst

def compute_merged_piece_values(board: Board) -> "list[float]":
    phase = game_stage(board)

    mg = piece_values[MIDGAME]
    eg = piece_values[ENDGAME]

    out_vals = [(mgval * phase + egval * (1 - phase)) *
                PAWN_NORM / 2 for mgval, egval in zip(mg, eg)]

    return out_vals

pst = mg_pst

def set_pst(board: Board) -> None:
    global pst
    pst = compute_merged_pst(board)

def set_piece_values(board: Board) -> None:
    global PAWN_VALUE, KNIGHT_VALUE, BISHOP_VALUE, ROOK_VALUE, QUEEN_VALUE
    PAWN_VALUE, KNIGHT_VALUE, BISHOP_VALUE, ROOK_VALUE, QUEEN_VALUE, _ = compute_merged_piece_values(board)

def pst_eval(board: Board) -> float:
    white = board.occupied_co[WHITE]
    black = board.occupied_co[BLACK]
    return sum(chain(
        (pst[p][i] for i in scan_forward(board.pawns & black)),
        (-pst[P][i] for i in scan_forward(board.pawns & white)),
        (pst[n][i] for i in scan_forward(board.knights & black)),
        (-pst[N][i] for i in scan_forward(board.knights & white)),
        (pst[b][i] for i in scan_forward(board.bishops & black)),
        (-pst[B][i] for i in scan_forward(board.bishops & white)),
        (pst[r][i] for i in scan_forward(board.rooks & black)),
        (-pst[R][i] for i in scan_forward(board.rooks & white)),
        (pst[q][i] for i in scan_forward(board.queens & black)),
        (-pst[Q][i] for i in scan_forward(board.queens & white)),
        (pst[k][i] for i in scan_forward(board.kings & black)),
        (-pst[K][i] for i in scan_forward(board.kings & white))))

ISOLATION_MASKS = [
    chess.BB_FILE_A | chess.BB_FILE_B,
    chess.BB_FILE_A | chess.BB_FILE_B | chess.BB_FILE_C,
    chess.BB_FILE_B | chess.BB_FILE_C | chess.BB_FILE_D,
    chess.BB_FILE_C | chess.BB_FILE_D | chess.BB_FILE_E,
    chess.BB_FILE_D | chess.BB_FILE_E | chess.BB_FILE_F,
    chess.BB_FILE_E | chess.BB_FILE_F | chess.BB_FILE_G,
    chess.BB_FILE_F | chess.BB_FILE_G | chess.BB_FILE_H,
    chess.BB_FILE_G | chess.BB_FILE_H,
]

def isolated_pawns(board: Board) -> float:
    white_pawns = board.occupied_co[WHITE] & board.pawns
    black_pawns = board.occupied_co[BLACK] & board.pawns
    isolated_white = 0
    for file_window_mask in ISOLATION_MASKS:
        if popcount(white_pawns & file_window_mask) == 1:
            isolated_white += 1
        if popcount(black_pawns & file_window_mask) == 1:
            isolated_white -= 1
    return -isolated_white


def blocked_pawns(board: Board) -> float:
    white_pawns = board.occupied_co[WHITE] & board.pawns
    black_pawns = board.occupied_co[BLACK] & board.pawns
    blocked_white = 0
    for pawn_sq in scan_forward(white_pawns):
        square_in_front = pawn_sq + 8
        if (1 << square_in_front) & board.occupied_co[BLACK]:
            blocked_white += 1
    for pawn_sq in scan_forward(black_pawns):
        square_in_front = pawn_sq - 8
        if (1 << square_in_front) & board.occupied_co[WHITE]:
            blocked_white -= 1
    return -blocked_white

def doubled_pawns(board: Board) -> float:
    white_pawns = board.occupied_co[WHITE] & board.pawns
    black_pawns = board.occupied_co[BLACK] & board.pawns
    doubled_white = 0
    for file_mask in chess.BB_FILES:
        if popcount(white_pawns & file_mask) >= 2:
            doubled_white += 1
        if popcount(black_pawns & file_mask) >= 2:
            doubled_white -= 1
    return -doubled_white

def passed_pawns(board: Board) -> float:
    white_pawns = board.occupied_co[WHITE] & board.pawns
    black_pawns = board.occupied_co[BLACK] & board.pawns
    passed_white = 0
    for file_mask, file_window_mask in zip(chess.BB_FILES, ISOLATION_MASKS):
        if white_pawns & file_mask:
            if not (black_pawns & file_window_mask):
                passed_white += 1
        if black_pawns & file_mask:
            if not (white_pawns & file_window_mask):
                passed_white -= 1
    return -passed_white

def pawn_structure_eval(board: Board) -> float:
    half_pawn = PAWN_VALUE / 2
    isolated = isolated_pawns(board)
    blocked = blocked_pawns(board)
    doubled = doubled_pawns(board)
    passed = passed_pawns(board)
    # print(f"{isolated=}, {blocked=}, {doubled=}, {passed=}")
    # print(f"{half_pawn=}")
    return half_pawn * (-isolated - blocked - doubled + passed)

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
    one_tenth_pawn = PAWN_VALUE / 10
    mobility = 0
    if board.turn == WHITE:
        mobility -= count_legal_moves(board)
        board.push(Move.null())
        mobility += count_legal_moves(board)
        board.pop()
    else:
        mobility += count_legal_moves(board)
        board.push(Move.null())
        mobility -= count_legal_moves(board)
        board.pop()
    return one_tenth_pawn * mobility

def king_safety(board: Board) -> float:
    wpieces = board.occupied_co[WHITE]
    bpieces = board.occupied_co[BLACK]
    wkingloc = lsb(board.kings & wpieces)
    bkingloc = lsb(board.kings & bpieces)
    safety = 0
    safety += sum(chess.square_distance(bkingloc, sq) * 2 for sq in scan_forward(board.queens & wpieces))
    safety += sum(chess.square_distance(bkingloc, sq) / 2 for sq in scan_forward(board.bishops & wpieces))
    safety += sum(chess.square_distance(bkingloc, sq) / 2 for sq in scan_forward(board.rooks & wpieces))
    safety += sum(chess.square_distance(bkingloc, sq) for sq in scan_forward(board.knights & wpieces))
    safety -= sum(chess.square_distance(wkingloc, sq) * 2 for sq in scan_forward(board.queens & bpieces))
    safety -= sum(chess.square_distance(wkingloc, sq) / 2 for sq in scan_forward(board.bishops & bpieces))
    safety -= sum(chess.square_distance(wkingloc, sq) / 2 for sq in scan_forward(board.rooks & bpieces))
    safety -= sum(chess.square_distance(wkingloc, sq) for sq in scan_forward(board.knights & bpieces))
    return safety

W_AREA = BB_RANK_1 | BB_RANK_2 | BB_RANK_3 | BB_RANK_4
B_AREA = BB_RANK_8 | BB_RANK_7 | BB_RANK_6 | BB_RANK_5
def space(board: Board):
    space = 0
    space -= sum(popcount(BB_PAWN_ATTACKS[WHITE][sq] & B_AREA) for sq in scan_forward(
        board.pawns & board.occupied_co[WHITE]))
    space += sum(popcount(BB_PAWN_ATTACKS[BLACK][sq] & W_AREA) for sq in scan_forward(
        board.pawns & board.occupied_co[BLACK]))
    space -= sum(popcount(BB_KNIGHT_ATTACKS[sq] & B_AREA) for sq in scan_forward(
        board.knights & board.occupied_co[WHITE]))
    space += sum(popcount(BB_KNIGHT_ATTACKS[sq] & W_AREA) for sq in scan_forward(
        board.knights & board.occupied_co[BLACK]))
    return space
