from Viridithas import Viridithas
from tqdm import tqdm

def evaluate(fen: str, tl: float) -> "tuple[float, float]":
    v = Viridithas(time_limit=tl, book=False)
    v.set_position(fen)
    _, pos_eval = v.search(readout=False) 
    alt_pos_eval = v.tt_lookup(v.node).value * -v.turnmod()
    # print(pos_eval, alt_pos_eval)
    return pos_eval * -v.turnmod(), alt_pos_eval


def raw_eval(fen: str, tl: float) -> "tuple[float, float]":
    v = Viridithas(time_limit=tl, book=False)
    v.set_position(fen)
    pos_eval = v.evaluate(1, False, False)
    return -pos_eval, -pos_eval


def main():
    for tl in [0.1, 0.5, 1, 3]:
        diffs = []
        with open("SF_evals.csv", "r", encoding='utf-8-sig') as f:
            for line in tqdm(f, total=500):
                fen, evaluation = line.strip().split(",")
                viri_eval, alt_eval = evaluate(fen, tl)
                # viri_eval, alt_eval = raw_eval(fen, tl)
                diff = viri_eval / 10 - float(evaluation)
                alt_diff = alt_eval / 10 - float(evaluation)
                diffs.append((diff, alt_diff))
        # print(diffs)
        print(
            f"MSE: {sum(map(lambda x: x[0]*x[0], diffs)) / len(diffs)} at {tl}s \nalt: {sum(map(lambda x: x[1]*x[1], diffs)) / len(diffs)} at {tl}s ")

if __name__ == "__main__":
    main()
