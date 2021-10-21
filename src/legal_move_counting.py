from typing import Iterator
from chess import Board, Move, Bitboard, BB_ALL, msb


def count_legal_moves(board: Board, from_mask: Bitboard = BB_ALL, to_mask: Bitboard = BB_ALL) -> int:
    if board.is_variant_end():
        return 0

    total = 0

    king_mask = board.kings & board.occupied_co[board.turn]
    
    king = msb(king_mask)
    blockers = board._slider_blockers(king)
    checkers = board.attackers_mask(not board.turn, king)
    if checkers:
        for move in board._generate_evasions(king, checkers, from_mask, to_mask):
            if board._is_safe(king, blockers, move):
                total += 1
    else:
        for move in board.generate_pseudo_legal_moves(from_mask, to_mask):
            if board._is_safe(king, blockers, move):
                total += 1
    
    return total


def count_pseudo_legal_moves(board: Board, from_mask: Bitboard = BB_ALL, to_mask: Bitboard = BB_ALL) -> int:
    return 0
