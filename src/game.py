import chess.variant
from Viridithas import Viridithas


def selfplay(time: int = 15, position: str = "", pgn: str = "", usebook: bool = False, player1=Viridithas, player2=Viridithas):
    e1 = player1(book=usebook, fun=True, contempt=0,
                 fen=position, pgn=pgn, time_limit=time)
    e2 = player2(book=usebook, fun=True, contempt=0,
                 fen=position, pgn=pgn, time_limit=time)

    while not (e1.node.is_game_over() or e2.node.is_game_over()):
        print(e1.__repr__())
        e2.node.push(e1.engine_move())
        if e1.node.is_game_over() or e2.node.is_game_over():
            break
        print(e2.__repr__())
        e1.node.push(e2.engine_move())

    e1.display_ending()
    game1 = e1.node.result()

    e2 = player1(book=usebook, fun=True, contempt=0,
                 fen=position, time_limit=time)
    e1 = player2(book=usebook, fun=True, contempt=0,
                 fen=position, time_limit=time)

    while not (e1.node.is_game_over() or e2.node.is_game_over()):
        print(e1.__repr__())
        e2.node.push(e1.engine_move())
        if e1.node.is_game_over() or e2.node.is_game_over():
            break
        print(e2.__repr__())
        e1.node.push(e2.engine_move())

    e1.display_ending()
    game2 = e1.node.result()

    insertion = "using book" if usebook else "without book"
    resultstring = f"\nengine selfplay {insertion} with timecontrol of {str(time)} seconds per move each.\n"
    resultstring += f"game1: White: {str(e1)} | Black: {str(e2)} | {game1}\n"
    resultstring += f"game2: White: {str(e2)} | Black: {str(e1)} | {game2}\n"

    return resultstring


def analysis(engineType, pos="", usebook=True, limit=1000000000000, indef=False):
    engine = engineType(book=usebook, contempt=0,
                        time_limit=limit, fun=False, fen=pos)
    engine.run_game(indefinite=indef)
    return [elem[3:] for elem in engine.searchdata]


interestingPosition = "8/b7/4P2p/8/3p2k1/1K1P4/pB6/8 b - - 0 58"

viriQueenSacPosition = "r4qk1/1rp2pp1/p2p1n2/P2Pp3/4P3/1B4QP/2P2PP1/3RR1K1 w - - 0 30"


class CrazyHouse(Viridithas):
    def __init__(self,
                 human: bool = False,
                 fen: str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                 pgn: str = '',
                 time_limit: int = 15,
                 fun: bool = False,
                 contempt: int = 3000,
                 book: bool = True,
                 advancedTC: list = [],):
        super().__init__(human=human, fen=fen, pgn=pgn, time_limit=time_limit,
                         fun=fun, contempt=contempt, book=book, advancedTC=advancedTC)
        self.node = chess.variant.CrazyhouseBoard(fen=fen)


if __name__ == "__main__":
    pass
    fen = "8/3Q4/6kp/6p1/3Bq1K1/8/6PP/8 w - - 0 1"
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    test = "3r1b1r/1k1qpppp/1pn2n2/p2p1b2/Q2P1B2/P1N2NPP/1P2PPB1/2R1K2R w K - 0 13"
    high_branch_fen = "1r6/3kp3/4Rp2/1prP2p1/p7/P6P/1PPR1PPK/8 w - - 7 32"
    # analysis(Viridithas, input(), usebook=False)
    engine = Viridithas(
        human=True,
        time_limit=15,
        fun=False,
        book=False,
    )
    engine.play_viri(fen)

    # analysis(Viridithas, viriQueenSacPosition, usebook=False)
    # analysis(Viridithas, fen, usebook=False, limit=10)

    # engine = Viridithas()
    # engine.node.set_fen(high_branch_fen)

    # for d in range(10):
    #     engine.perft(d)

    selfplay(time=15, position=fen, usebook=False,
             player1=Viridithas, player2=Viridithas)

# add a separate qsearch hashtable
