from Viridithas import Viridithas
from tqdm import tqdm

def evaluate(fen: str, tl: float) -> float:
    v = Viridithas(time_limit=tl, book=False)
    v.set_position(fen)
    _ = v.search(readout=False)
    pos_eval = v.tt_lookup(v.node).value * -v.turnmod()
    return pos_eval


def raw_eval(fen: str, tl: float) -> float:
    v = Viridithas(time_limit=tl, book=False)
    v.set_position(fen)
    pos_eval = v.evaluate(1, False, False)
    return pos_eval


def main():
    for tl in [0.1, 0.5, 1, 3]:
        diffs = []
        with open("SF_evals.csv", "r", encoding='utf-8-sig') as f:
            for line in f:
                fen, evaluation = line.strip().split(",")
                viri_eval = evaluate(fen, tl=tl)
                # print(viri_eval / 10, evaluation)
                diff = viri_eval / 10 - float(evaluation)
                diffs.append(diff)
        print(f"MSE: {sum(map(lambda x: x*x, diffs)) / len(diffs)} at {tl}s")

if __name__ == "__main__":
    main()
