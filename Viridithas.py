#from __future__ import annotations
import chess
import chess.svg
import chess.pgn
import chess.polyglot
import chess.syzygy
import random
import chess.variant
import time
import operator
import sys
import itertools
from functools import lru_cache
from chess import WHITE, BLACK, Move, Board
from cachetools import LRUCache
from typing import Hashable
from PSTs import PieceSquareTable
print("Python version")
print(sys.version)

getter = PieceSquareTable()
piecesquaretable = getter(1)

class TTEntry():
    def __init__(self, best: Move, depth: float, a: int, hashDataType: int):
        self.bestMove: Move = best
        self.depth: float = depth
        self.score: int = a
        self.type: int = hashDataType

class Viridithas():
    def __init__(self, human: bool = False, fen: str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', pgn: str = '', timeLimit: int = 15, fun: bool = False, contempt: int = 3000, book: bool = True, advancedTC: list = []):
        if pgn == '':
            self.node = Board(fen)
        else:
            self.node = Board()
            for move in pgn.split():
                try:
                    self.node.push_san(move)
                except Exception:
                    continue
        self.timeLimit = timeLimit
        self.startTime = time.time()
        if advancedTC:
            if not human:
                advancedTC[0] = advancedTC[0]*2
            self.endpoint = time.time()+advancedTC[0]*60
            self.increment = advancedTC[1]
        else:
            self.endpoint = 0
            self.increment = 0
        self.fun = fun
        self.contempt = contempt
        self.human = human
        self.nodes = 0
        self.advancedTC = advancedTC
        self.c = len(list(self.node.legal_moves))
        self.tableSize = 2**20+49
        self.hashtable: LRUCache[Hashable, TTEntry] = LRUCache(maxsize=self.tableSize)
        self.ett = dict()
        self.hashstack = dict()
        self.pieces = range(1, 7)
        self.inbook = book
        self.ext = False
        self.searchdata = []

    def __repr__(self) -> str:
        try:
            display(chess.svg.board(board=self.node,
                                    size=400,
                                    flipped=not self.node.turn))  # FOR A JUPYTER NOTEBOOK
            return self.__class__.__name__+"-engine at position "+str(self.node.fen())
        except Exception:
            return str(self.node) + '\n' + self.__class__.__name__+"-engine at position " + str(self.node.fen())

    def __str__(self) -> str:
        return self.__class__.__name__

    def user_setup(self) -> int:
        if input("Do you want to configure the bot? (Y/N) ").upper() == 'Y':
            pass
        else:
            return 0
        print("BEGINNING USER CONFIGURATION OF " +
              self.__class__.__name__.upper() + "-BOT")
        human = True if input(
            "Is there a human opponent? (Y/N) ").upper() == "Y" else False
        fen = True if input(
            "Would you like to set a position from FEN? (Y/N) ").upper() == "Y" else False
        if fen:
            fen = input("FEN: ")
            pgn = ""
        else:
            fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
            pgn = True if input(
                "Would you like to set a position from PGN? (Y/N) ").upper() == "Y" else False
            if pgn:
                pgn = input("PGN: ")
            else:
                pgn = ""

        timeLimit = 15
        advancedTC = []
        controlType = input(
            "Advanced, Simple, or Infinite time control? [A/S/I]: ").upper()
        while controlType not in ["A", "S", "I"]:
            controlType = input("[A/S/I]: ").upper()
        if controlType == 'S':
            timeLimit = int(input("Enter time limit in seconds: "))
        elif controlType == 'A':
            advancedTC = [0, 0]
            advancedTC[0] = int(input("Enter minutes: "))
            advancedTC[1] = int(input("Enter increment: "))
        else:
            timeLimit = 10000000000

        book = True if input(
            "Would you like to use an opening book? (Y/N) ").upper() == 'Y' else False
        if book:
            fun = True if input(
                "Would you like to pick varied openings? (Y/N) ").upper() == 'Y' else False
        else:
            fun = False

        contempt = int(input("Enter contempt in millipawns: "))
        self.__init__(human=human, fen=fen, pgn=pgn, timeLimit=timeLimit, fun=fun,
                      contempt=contempt, book=book, advancedTC=advancedTC)

        return 0

    def see_factor(self) -> int:
        rating = chess.popcount(
            self.node.occupied_co[BLACK] & self.node.pawns) * 1000
        rating -= chess.popcount(
            self.node.occupied_co[WHITE] & self.node.pawns) * 1000
        rating += chess.popcount(
            self.node.occupied_co[BLACK] & self.node.knights) * 3200
        rating -= chess.popcount(
            self.node.occupied_co[WHITE] & self.node.knights) * 3200
        rating += chess.popcount(
            self.node.occupied_co[BLACK] & self.node.bishops) * 3330
        rating -= chess.popcount(
            self.node.occupied_co[WHITE] & self.node.bishops) * 3330
        rating += chess.popcount(
            self.node.occupied_co[BLACK] & self.node.rooks) * 5100
        rating -= chess.popcount(
            self.node.occupied_co[WHITE] & self.node.rooks) * 5100
        rating += chess.popcount(
            self.node.occupied_co[BLACK] & self.node.queens) * 8800
        rating -= chess.popcount(
            self.node.occupied_co[WHITE] & self.node.queens) * 8800
        return rating

    def seepos_factor(self) -> int:
        white = self.node.occupied_co[WHITE]
        black = self.node.occupied_co[BLACK]
        return sum(itertools.chain(
            (piecesquaretable['p'][i] for i in chess.scan_forward(
                self.node.pawns & black)),
            (-piecesquaretable['P'][i] for i in chess.scan_forward(
                self.node.pawns & white)),
            (piecesquaretable['n'][i] for i in chess.scan_forward(
                self.node.knights & black)),
            (-piecesquaretable['N'][i] for i in chess.scan_forward(
                self.node.knights & white)),
            (piecesquaretable['b'][i] for i in chess.scan_forward(
                self.node.bishops & black)),
            (-piecesquaretable['B'][i] for i in chess.scan_forward(
                self.node.bishops & white)),
            (piecesquaretable['r'][i] for i in chess.scan_forward(
                self.node.rooks & black)),
            (-piecesquaretable['R'][i] for i in chess.scan_forward(
                self.node.rooks & white)),
            (piecesquaretable['q'][i] for i in chess.scan_forward(
                self.node.queens & black)),
            (-piecesquaretable['Q'][i] for i in chess.scan_forward(
                self.node.queens & white)),
            (piecesquaretable['k'][i] for i in chess.scan_forward(
                self.node.kings & black)),
            (-piecesquaretable['K'][i] for i in chess.scan_forward(
                self.node.kings & white))))

    def record_eval_hash(self, key: int, smallkey: int, value: int) -> None:
        self.ett[smallkey] = {'key': key, 'score': value}

    def probe_eval_hash(self, key: int, smallkey: int) -> bool:
        if smallkey in self.ett:
            if self.ett[smallkey]["key"] == key:
                return True
        return False

    def evaluate(self, depth: float) -> int:
        self.nodes += 1

        rating: int = 0
        if self.node.is_checkmate():
            return 1000000000 * int(depth+1) * (1 if self.node.turn else -1)
        if self.node.can_claim_fifty_moves():
            rating = -self.contempt * (1 if self.node.turn else -1)

        if self.pos_hash() in self.hashstack:
            rating = -self.contempt * (1 if self.node.turn else -1)

        rating += self.seepos_factor()

        return rating

    def pos_hash(self):
        return self.node._transposition_key()

    def record_stack(self) -> None:
        key = self.pos_hash()
        if key in self.hashstack:
            self.hashstack[key] += 1
        else:
            self.hashstack[key] = 1

    def record_hash(self, key: Hashable, best: Move, depth: float, a: int, hashDataType: int) -> None:
        if key in self.hashtable:
            entry = self.hashtable[key]
            if entry.depth >= depth:
                self.hashtable[key] = TTEntry(best, depth, a, hashDataType)
        else:
            self.hashtable[key] = TTEntry(best, depth, a, hashDataType)

    def probe_hash(self, key: Hashable, depth: float = 0, a: int = -1000, b: int = 1000) -> tuple:
        try:
            entry = self.hashtable[key]
        except Exception:
            return (None, None)
        if entry.depth >= depth:
            if entry.type == 0:
                return (entry.score, True)
            if entry.type == 1 and entry.score <= a:
                return (a, True)
            if entry.type == 2 and entry.score >= b:
                return (b, True)
            return (entry.bestMove, False)
        return (entry.bestMove, False)

    def single_hash_iterator(self, best):
        yield best

    def captures_piece(self, p):  # concentrate on MVV, then LVA
        return itertools.chain(
            self.node.generate_pseudo_legal_moves(self.node.pawns, p),
            self.node.generate_pseudo_legal_moves(self.node.knights, p),
            self.node.generate_pseudo_legal_moves(self.node.bishops, p),
            self.node.generate_pseudo_legal_moves(self.node.rooks, p),
            self.node.generate_pseudo_legal_moves(self.node.queens, p),
            self.node.generate_pseudo_legal_moves(self.node.kings, p),
        )

    def captures(self):  # (MVV/LVA)
        return (m for m in itertools.chain(
            self.captures_piece(
                self.node.occupied_co[not self.node.turn] & self.node.queens),
            self.captures_piece(
                self.node.occupied_co[not self.node.turn] & self.node.rooks),
            self.captures_piece(
                self.node.occupied_co[not self.node.turn] & self.node.bishops),
            self.captures_piece(
                self.node.occupied_co[not self.node.turn] & self.node.knights),
            self.captures_piece(
                self.node.occupied_co[not self.node.turn] & self.node.pawns),
        ) if self.node.is_legal(m))

    def ordered_moves(self, best: Move = Move.from_uci("0000")):
        return (m for m in itertools.chain(
            self.single_hash_iterator(best),
            self.captures_piece(
                self.node.occupied_co[not self.node.turn] & self.node.queens),
            self.captures_piece(
                self.node.occupied_co[not self.node.turn] & self.node.rooks),
            self.captures_piece(
                self.node.occupied_co[not self.node.turn] & self.node.bishops),
            self.captures_piece(
                self.node.occupied_co[not self.node.turn] & self.node.knights),
            self.captures_piece(
                self.node.occupied_co[not self.node.turn] & self.node.pawns),
            self.node.generate_pseudo_legal_moves(
                0xffff_ffff_ffff_ffff, ~self.node.occupied_co[not self.node.turn])
        ) if self.node.is_legal(m))

    def pass_turn(self) -> None:
        self.node.turn = not self.node.turn

    # @profile
    # qsearch hashtable would like speed stuff up
    def qsearch(self, a: int, b: int, depth: float, colour: int) -> int:
        scoreIfNoCaptures = self.evaluate(depth) * colour
        if scoreIfNoCaptures >= b:
            return b
        a = max(scoreIfNoCaptures, a)

        for capture in self.captures():
            self.node.push(capture)
            score = -self.qsearch(-b, -a, depth - 1, -colour)
            self.node.pop()
            if score >= b:
                return b
            a = max(score, a)

        return a

    def negamax_pvs(self, depth: float, colour: int, a: int = -1337000000, b: int = 1337000000) -> int:
        if depth < 1:
            return self.qsearch(a, b, depth, colour)

        if self.node.is_game_over():
            return colour * self.evaluate(depth)
        best = Move.from_uci("0000")
        hashDataType = 1
        key = self.pos_hash()
        probe = self.probe_hash(key, depth, a, b)
        if probe[0] != None:
            if probe[1]:
                return probe[0]
            else:
                best = probe[0]
        # NULLMOVE PRUNING
        if not self.node.is_check():
            self.pass_turn()  # MAKE A NULL MOVE
            # PERFORM A LIMITED SEARCH
            value = - self.negamax_pvs(depth - 3, -colour, -b, -a)
            self.pass_turn()  # UNMAKE NULL MOVE
            a = max(a, value)
            if a >= b:
                return a
            check = False
        else:
            check = True
        # MOVE ORDERING (HASH -> TAKES -> OTHERS)
        moves = self.ordered_moves(best)
        for i, move in enumerate(moves):
            self.node.push(move)  # MAKE MOVE
            if check:
                depth += 1
            if i == 0:
                best = move
                # FULL SEARCH ON MOVE 1
                value = - self.negamax_pvs(depth - 1, -colour, -b, -a)
            else:
                # NULL-WINDOW SEARCH
                value = - self.negamax_pvs(depth - 1, -colour, -a - 1, -a)
                if a < value < b:  # CHECK IF NULLWINDOW FAILED
                    # RE-SEARCH
                    value = - self.negamax_pvs(depth - 1, -colour, - b, -value)
            if check:
                depth -= 1
            self.node.pop()  # UNMAKE MOVE
            if value >= b:
                self.record_hash(key, best, depth, b, 2)
                return b
            if value > a:
                hashDataType = 0
                a = value
                self.best = move
        self.record_hash(key, best, depth, a, hashDataType)
        return a

    def move_sort(self, moves: list, ratings: list):
        pairs = zip(*sorted(zip(moves, ratings), key=operator.itemgetter(1)))
        moves, ratings = [list(pair) for pair in pairs]
        return moves, ratings

    def turnmod(self) -> int:
        return -1 if self.node.turn else 1

    def show_iteration_data(self, moves: list, values: list, depth: float) -> tuple:
        t = round(time.time()-self.startTime, 2)
        print(f"{self.node.san(moves[0])} | {round((self.turnmod()*values[0])/1000, 3)} | {str(t)}s at depth {str(depth + 1)}, {str(self.nodes)} nodes processed, at {str(int(self.nodes / (t+0.00001)))}NPS.")
        return (self.node.san(moves[0]), self.turnmod()*values[0], self.nodes, depth+1, t)

    def search(self, ponder: bool = False):
        self.startTime = time.time()
        self.nodes = 0
        moves = list(self.ordered_moves())
        values = [0.0 for m in moves]
        for depth in range(0, 40):
            self.ett.clear()
            if self.timeLimit*2/3 < time.time()-self.startTime and not ponder:
                return moves[0]
            for i, move in enumerate(moves):
                self.node.push(move)
                values[i] = self.negamax_pvs(depth, self.turnmod())
                self.node.pop()
                if self.timeLimit < time.time()-self.startTime and not ponder:
                    return moves[0]
            moves, values = self.move_sort(moves, values)
            self.searchdata.append(
                self.show_iteration_data(moves, values, depth))
            [print(self.node.san(move), end=" ") for move in moves]
            print("\n")
            # if depth < 7 and abs(values[0]) > 300000000 and not ponder:
            # return moves[0]
        return moves[0]

    def ponder(self) -> None:
        self.origin = self.node.copy()
        self.search(ponder=True)

    def get_book_move(self):
        # book = chess.polyglot.open_reader(
        #     r"ProDeo292/ProDeo292/books/elo2500.bin")
        book = chess.polyglot.open_reader(
            r"books/Human.bin")
        main_entry = book.find(self.node)
        choice = book.weighted_choice(self.node)
        book.close()
        return main_entry.move, choice.move

    def engine_move(self) -> Move:
        # add flag_func for egtb mode
        if self.advancedTC:
            self.timeLimit = (self.endpoint-time.time())/20
        print("Time for move: " + str(round(self.timeLimit, 2)) + "s")
        if self.inbook:
            try:
                best, choice = self.get_book_move()
                if self.fun:
                    self.node.push(choice)
                    return choice
                else:
                    self.node.push(best)
                print(chess.pgn.Game.from_board(self.node)[-1])
            except IndexError:
                self.timeLimit = self.timeLimit*2
                best = self.search()
                self.node.push(best)
                print(chess.pgn.Game.from_board(self.node)[-1])
                self.inbook = False
                self.timeLimit = self.timeLimit/2
        else:
            best = self.search()
            self.node.push(best)
            print(chess.pgn.Game.from_board(self.node)[-1])
        self.record_stack()
        self.endpoint += self.increment

        return best

    def user_move(self) -> str:
        move = input("enter move: ")
        while True:
            try:
                self.node.push_san(move)
                break
            except Exception:
                move = input("enter move: ")
        return move

    def display_ending(self) -> None:
        if self.node.is_stalemate():
            print('END BY STALEMATE')
        elif self.node.is_insufficient_material():
            print('END BY INSUFFICIENT MATERIAL')
        elif self.node.is_fivefold_repetition():
            print('END BY FIVEFOLD REPETITION')
        elif self.node.is_checkmate:
            print("BLACK" if self.node.turn == BLACK else "WHITE", 'WINS ON TURN',
                  self.node.fullmove_number)
        else:
            print('END BY UNKNOWN REASON')

    def run_game(self, indefinite=True) -> str:
        while not self.node.is_game_over():
            print(self.__repr__())
            if self.human and self.node.turn:
                try:
                    self.ponder()
                except KeyboardInterrupt:
                    self.node = self.origin
                    self.user_move()

            else:  # SWAP THESE ASAP

                self.engine_move()
            if not indefinite:
                break
        self.display_ending()
        try:
            return str(chess.pgn.Game.from_board(self.node)[-1])
        except Exception:
            return "PGN ERROR"

    def play_viri(self, fen=None):
        player_colour = input(
            "Enter the human player's colour in the form b/w\n--> ")
        while player_colour not in ['b', 'w']:
            player_colour = input(
                "Enter the human player's colour in the form b/w\n--> ")
        player_colour = WHITE if player_colour == 'w' else BLACK
        timeControl = int(
            input("how many seconds should viri get per move?\n--> "))
        self.__init__(human=True, timeLimit=timeControl, fen=fen)
        while not self.node.is_game_over():
            print(self.__repr__())
            if player_colour == self.node.turn:
                try:
                    self.ponder()
                except KeyboardInterrupt:
                    self.node = self.origin
                    self.user_move()
            else:
                self.engine_move()
        self.display_ending()

    def perftx(self, n):
        if n == 0:
            self.nodes += 1
        else:
            for move in self.ordered_moves():
                self.node.push(move)
                self.perftx(n - 1)
                self.node.pop()

    def perft(self, n):
        self.nodes = 0
        self.perftx(n)
        print(self.nodes)

    def uci(self):
        start = input()
        while start != "uci":
            start = input()
        print("id", end="")
        while True:
            command = input()
            if command == "ucinewgame":
                board = Board()
            elif command.split()[0] == "position":
                fen = command[command.index(
                    "fen") + 3: command.index("moves") - 1]
                moves = command[command.index("moves"):].split()
                if fen == "startpos":
                    fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
                board = Board(fen)
                for move in moves:
                    board.push(Move.from_uci(move))


class Fork(Viridithas):
    def __init__(self, human: bool = False, fen: str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', pgn: str = '', timeLimit: int = 15, fun: bool = False, contempt: int = 3000, book: bool = True, advancedTC: list = []):
        if pgn == '':
            self.node = Board(fen)
        else:
            self.node = Board()
            for move in pgn.split():
                try:
                    self.node.push_san(move)
                except Exception:
                    continue
        self.timeLimit = timeLimit
        self.startTime = time.time()
        if advancedTC:
            if not human:
                advancedTC[0] = advancedTC[0]*2
            self.endpoint = time.time()+advancedTC[0]*60
            self.increment = advancedTC[1]
        else:
            self.endpoint = 0
            self.increment = 0
        self.fun = fun
        self.contempt = contempt
        self.human = human
        self.nodes = 0
        self.advancedTC = advancedTC
        self.c = len(list(self.node.legal_moves))
        self.tableSize = 2**20+49
        self.hashtable = LRUCache(maxsize=self.tableSize)
        self.ett = LRUCache(maxsize=self.tableSize)
        self.hashstack = dict()
        self.pieces = range(1, 7)
        self.best = Move.from_uci('0000')
        self.inbook = book
        self.ext = False
        self.searchdata = []

class Atomic(Viridithas):
    def __init__(self, human=False, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', pgn='', timeLimit=15, fun=False, contempt=3000, book=True, advancedTC=False,):
        super().__init__(human, fen, pgn, timeLimit, fun,
                         contempt, False, advancedTC)
        self.node = chess.variant.AtomicBoard(fen)


class Crazyhouse(Viridithas):
    def __init__(self, human=False, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', pgn='', timeLimit=15, fun=False, contempt=3000, book=True, advancedTC=False):
        super().__init__(human, fen, pgn, timeLimit, fun,
                         contempt, book, advancedTC)
        self.node = chess.variant.CrazyhouseBoard(fen)

    def evaluate(self, depth: float) -> int:
        self.nodes += 1

        rating = 0
        if self.node.is_checkmate():
            return 1000000000 * int(depth+1) * (1 if self.node.turn else -1)
        if self.node.can_claim_fifty_moves():
            rating = -self.contempt * (1 if self.node.turn else -1)

        if self.pos_hash() in self.hashstack:
            rating = -self.contempt * (1 if self.node.turn else -1)

        rating += self.seepos_factor()

        return rating


class Antichess(Viridithas):
    def __init__(self, human=False, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', pgn='', timeLimit=15, fun=False, contempt=3000, book=True, advancedTC=False):
        super().__init__(human, fen, pgn, timeLimit, fun,
                         contempt, False, advancedTC)
        self.node = chess.variant.AntichessBoard(fen)

    def evaluate(self, depth: float) -> int:
        self.nodes += 1
        return sum(itertools.chain((-1 for i in chess.scan_forward(self.node.occupied_co[0])), (1 for i in chess.scan_forward(self.node.occupied_co[1]))))


class AntichessN(Viridithas):
    def __init__(self, human=False, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', pgn='', timeLimit=15, fun=False, contempt=3000, book=True, advancedTC=False):
        super().__init__(human, fen, pgn, timeLimit, fun,
                         contempt, False, advancedTC)
        self.node = chess.variant.AntichessBoard(fen)

    def evaluate(self, depth: float) -> int:
        self.nodes += 1
        return -sum(itertools.chain((-1 for i in chess.scan_forward(self.node.occupied_co[0])), (1 for i in chess.scan_forward(self.node.occupied_co[1]))))


def selfplay(time: int = 15, position: str = "", pgn: str = "", usebook: bool = False, player1=Viridithas, player2=Fork):
    e1 = player1(book=usebook, fun=True, contempt=0,
                 fen=position, pgn=pgn, timeLimit=time)
    e2 = player2(book=usebook, fun=True, contempt=0,
                 fen=position, pgn=pgn, timeLimit=time)

    while not (e1.node.is_game_over() or e2.node.is_game_over()):
        print(e1.__repr__())
        e2.node.push(e1.engine_move())
        if e1.node.is_game_over() or e2.node.is_game_over():
            break
        print(e2.__repr__())
        e1.node.push(e2.engine_move())

    e1.display_ending()
    game1 = e1.node.result()

    e1.clear_tt()
    e2.clear_tt()

    e2 = player1(book=usebook, fun=True, contempt=0,
                 fen=position, timeLimit=time)
    e1 = player2(book=usebook, fun=True, contempt=0,
                 fen=position, timeLimit=time)

    while not (e1.node.is_game_over() or e2.node.is_game_over()):
        print(e1.__repr__())
        e2.node.push(e1.engine_move())
        if e1.node.is_game_over() or e2.node.is_game_over():
            break
        print(e2.__repr__())
        e1.node.push(e2.engine_move())

    e1.display_ending()
    game2 = e1.node.result()

    e1.clear_tt()
    e2.clear_tt()

    insertion = "using book" if usebook else "without book"
    resultstring = f"\nengine selfplay {insertion} with timecontrol of {str(time)} seconds per move each.\n"
    resultstring += f"game1: White: {str(e1)} | Black: {str(e2)} | {game1}\n"
    resultstring += f"game2: White: {str(e2)} | Black: {str(e1)} | {game2}\n"

    return resultstring


def general_purpose():

    engineType = input(
        "Enter variant: Regular, Atomic, Crazyhouse, Antichess, Fork [1/2/3/4/5]: ")
    while engineType not in ['1', '2', '3', '4', '5']:
        engineType = input(
            "Enter variant: Regular, Atomic, Crazyhouse, Antichess, Fork [1/2/3/4/5]: ")

    engines = [Viridithas, Atomic, Crazyhouse, Antichess, Fork]
    engine = engines[int(engineType)-1]

    engine.user_setup()
    engine.run_game()


def analysis(engineType, pos="", usebook=True, limit=1000000000000, indef=False):
    engine = engineType(book=usebook, contempt=0,
                        timeLimit=limit, fun=False, fen=pos)
    engine.run_game(indefinite=indef)
    return [elem[3:] for elem in engine.searchdata]

interestingPosition = "8/b7/4P2p/8/3p2k1/1K1P4/pB6/8 b - - 0 58"

if __name__ == "__main__":
    pass
    fen = "1nb1kbn1/ppp2ppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQ - 0 1"
    engine = Viridithas()
    engine.play_viri("1nb1kbn1/ppp2ppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQ - 0 1")
    #print("\n.".join([selfplay(time=60, usebook=bool(i), position="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1") for i in range(3)]))

    #pos = input()
    #analysis(engineType=Viridithas, pos=pos, usebook=False)
    #engine = Viridithas()
    # engine.play_viri()

# add a separate qsearch hashtable