from dataclasses import dataclass
from chess import BLACK, Board, Color, Move, WHITE
from Viridithas import Viridithas
from tqdm import tqdm

@dataclass
class TestPosition:
    winning_color: Color
    move: str
    fen: str
    name: str
    time: float = 1

test_positions = [
    TestPosition(
        WHITE, "Qxf7#", "r1bqkbnr/pppp1pp1/2n4p/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 0 4", "white_mate_in_1"),
    TestPosition(
        BLACK, "Qh4#", "rnbqkbnr/pppp1ppp/8/4p3/6P1/5P2/PPPPP2P/RNBQKBNR b KQkq - 0 2", "black_mate_in_1"),
    TestPosition(
        WHITE, "Qh6+", "r1bq2r1/b4pk1/p1pp1p2/1p2pP2/1P2P1PB/3P4/1PPQ2P1/R3K2R w - - 0 1", "white_mate_in_2"),
    TestPosition(
        BLACK, "Rg1+", "2kr4/1bp5/ppqp1N1p/4pp1Q/2Pn4/BP1P4/P4RrP/R4K2 b - - 0 1", "black_mate_in_2"),
    TestPosition(
        WHITE, "Ra6+", "r5rk/5p1p/5R2/4B3/8/8/7P/7K w", "white_mate_in_3"),
    TestPosition(
        BLACK, "Qxf2+", "r2n1rk1/1ppb2pp/1p1p4/3Ppq1n/2B3P1/2P4P/PP1N1P1K/R2Q1RN1 b - - 0 1", "black_mate_in_3"),
]

def check_position(position: TestPosition, debug = True):
    v = Viridithas(time_limit=position.time, book=False)
    v.set_position(position.fen)
    result = v.search(readout=False)
    pos_eval = v.tt_lookup(v.node).value * -v.turnmod()
    san = v.node.san(result)

    move_correct = san == position.move
    if not move_correct and debug:
        print(f"FAILED: {position.name}")
        print(f"  Expected: {position.move}")
        print(f"  Found:    {san}")
    parity_correct = pos_eval > 0 if position.winning_color == WHITE else pos_eval < 0
    if not parity_correct and debug:
        print(f"FAILED: {position.name}")
        print(f"  Expected: {'+1' if position.winning_color == WHITE else '-1'}")
        print(f"  Found:    {'+1' if pos_eval > 0 else '-1'}")
    magnitude_correct = abs(pos_eval) > 100000
    if not magnitude_correct and debug:
        print(f"FAILED: {position.name}")
        print(f"  Expected: >MATE_SCORE")
        print(f"  Found:    {pos_eval}")

    return move_correct and parity_correct and magnitude_correct

def parse_pgn(pgn: str):
    xs = pgn.split(" ")
    leader = xs[0]
    if leader == "1.":
        winner = WHITE
    else:
        winner = BLACK
    move = xs[1]
    return winner, move


def read_positions(limit: float = 0.25):
    with open("mate_in_threes.txt", "r") as f:
        for _idx, line in enumerate(f):
            idx = _idx + 1
            if idx < 10:
                continue
            if idx % 5 == 0:
                fen = line.strip()
            if idx % 5 == 1:
                winner, move = parse_pgn(line.strip())
                yield TestPosition(winner, move, fen, f"{idx // 5}", limit)
            

def main():
    print("CORRECTNESS TESTS:")
    for position in test_positions:
        if check_position(position):
            print(f"{position.name}: OK")
        else:
            print(f"{position.name}: FAIL")

    print("THE GAUNTLET:")
    NUM_POSITIONS = 400
    for tl in [0.001, 0.01, 0.1, 0.25, 1, 3]:
        successes = 0
        failures = 0
        for _, position in tqdm(zip(range(NUM_POSITIONS), read_positions(limit=tl)), total=NUM_POSITIONS):
            if check_position(position, debug=False):
                successes += 1
            else:
                failures += 1
        print(f"{successes * 100 // (successes + failures)}% success rate at {tl}s to think")

if __name__ == "__main__":
    main()
