from Viridithas import Viridithas

if __name__ == "__main__":
    engine = Viridithas(
        timeLimit=60,
        book=False,
        use_alphabeta=True,
        use_mvvlva=True,
        use_nmp=True,
        use_pvs=True,
        use_qsearch=True,
        use_tt=True,
    )

    testPositions = [
        "6K1/4k1P1/8/8/8/8/7r/5R2 w - - 0 1",
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
        "r1bqkb1r/pppp1ppp/2N2n2/8/4P3/8/PPPP1PPP/RNBQKB1R b KQkq - 0 4",
        "rnbqkbnr/pppppppp/8/8/8/1P6/P1PPPPPP/RNBQKBNR b KQkq - 0 1",
    ]

    for fen in testPositions[:1]:
        engine.set_position(fen)
        print(engine.node)
        engine.engine_move()
