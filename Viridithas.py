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
print("Python version")
print(sys.version)


class Viridithas():
    def __init__(self, human=False, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', pgn='', timeLimit=15, fun=False, contempt=3000, book=True, advancedTC=False):
        if pgn == '':
            self.node = chess.Board(fen)
        else:
            self.node = chess.Board()
            for move in pgn.split(' '):
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
        self.hashtable = dict()
        self.ett = dict()
        self.hashstack = dict()
        self.pieces = range(1, 7)
        self.best = chess.Move.from_uci('0000')
        self.inbook = book
        self.PMV = {'p': 1000, 'n': 3200, 'b': 3330, 'r': 5100, 'q': 8800, 'k': 0,
                    'P': 1000, 'N': 3200, 'B': 3330, 'R': 5100, 'Q': 8800, 'K': 0}
        self.PST = {'p': (0, 0, 0, 0, 0, 0, 0, 0, 50, 50, 50, 50, 50, 50, 50, 50, 10, 10, 20, 30, 30, 20, 10, 10, 5, 5, 10, 25, 25, 10, 5, 5, 0, 0, 0, 20, 20, 0, 0, 0, 5, -5, -10, 0, 0, -10, -5, 5, 5, 10, 10, -20, -20, 10, 10, 5, 0, 0, 0, 0, 0, 0, 0, 0),
                    'n': (-50, -40, -30, -30, -30, -30, -40, -50, -40, -20, 0, 0, 0, 0, -20, -40, -30, 0, 10, 15, 15, 10, 0, -30, -30, 5, 15, 20, 20, 15, 5, -30, -30, 0, 15, 20, 20, 15, 0, -30, -30, 5, 10, 15, 15, 10, 5, -30, -40, -20, 0, 5, 5, 0, -20, -40, -50, -40, -30, -30, -30, -30, -40, -50),
                    'b': (-20, -10, -10, -10, -10, -10, -10, -20, -10, 0, 0, 0, 0, 0, 0, -10, -10, 0, 5, 10, 10, 5, 0, -10, -10, 5, 5, 10, 10, 5, 5, -10, -10, 0, 10, 10, 10, 10, 0, -10, -10, 10, 10, 10, 10, 10, 10, -10, -10, 5, 0, 0, 0, 0, 5, -10, -20, -10, -10, -10, -10, -10, -10, -20,),
                    'r': (0, 0, 0, 0, 0, 0, 0, 0, 5, 10, 10, 10, 10, 10, 10, 5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 5, 5, 0, 0, 0),
                    'q': (-20, -10, -10, -5, -5, -10, -10, -20, -10, 0, 0, 0, 0, 0, 0, -10, -10, 0, 5, 5, 5, 5, 0, -10, -5, 0, 5, 5, 5, 5, 0, -5, 0, 0, 5, 5, 5, 5, 0, -5, -10, 5, 5, 5, 5, 5, 0, -10, -10, 0, 5, 0, 0, 0, 0, -10, -20, -10, -10, -5, -5, -10, -10, -20),
                    'k': (-30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30, -20, -30, -30, -40, -40, -30, -30, -20, -10, -20, -20, -20, -20, -20, -20, -10, 20, 20, 0, 0, 0, 0, 20, 20, 20, 30, 10, 0, 0, 10, 30, 20),
                    'P': (0, 0, 0, 0, 0, 0, 0, 0, 5, 10, 10, -20, -20, 10, 10, 5, 5, -5, -10, 0, 0, -10, -5, 5, 0, 0, 0, 20, 20, 0, 0, 0, 5, 5, 10, 25, 25, 10, 5, 5, 10, 10, 20, 30, 30, 20, 10, 10, 50, 50, 50, 50, 50, 50, 50, 50, 0, 0, 0, 0, 0, 0, 0, 0),
                    'N': (-50, -40, -30, -30, -30, -30, -40, -50, -40, -20, 0, 5, 5, 0, -20, -40, -30, 5, 10, 15, 15, 10, 5, -30, -30, 0, 15, 20, 20, 15, 0, -30, -30, 5, 15, 20, 20, 15, 5, -30, -30, 0, 10, 15, 15, 10, 0, -30, -40, -20, 0, 0, 0, 0, -20, -40, -50, -40, -30, -30, -30, -30, -40, -50),
                    'B': (-20, -10, -10, -10, -10, -10, -10, -20, -10, 5, 0, 0, 0, 0, 5, -10, -10, 10, 10, 10, 10, 10, 10, -10, -10, 0, 10, 10, 10, 10, 0, -10, -10, 5, 5, 10, 10, 5, 5, -10, -10, 0, 5, 10, 10, 5, 0, -10, -10, 0, 0, 0, 0, 0, 0, -10, -20, -10, -10, -10, -10, -10, -10, -20),
                    'R': (0, 0, 0, 5, 5, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, 5, 10, 10, 10, 10, 10, 10, 5, 0, 0, 0, 0, 0, 0, 0, 0),
                    'Q': (-20, -10, -10, -5, -5, -10, -10, -20, -10, 0, 0, 0, 0, 5, 0, -10, -10, 0, 5, 5, 5, 5, 5, -10, -5, 0, 5, 5, 5, 5, 0, 0, -5, 0, 5, 5, 5, 5, 0, -5, -10, 0, 5, 5, 5, 5, 0, -10, -10, 0, 0, 0, 0, 0, 0, -10, -20, -10, -10, -5, -5, -10, -10, -20),
                    'K': (20, 30, 10, 0, 0, 10, 30, 20, 20, 20, 0, 0, 0, 0, 20, 20, -10, -20, -20, -20, -20, -20, -20, -10, -20, -30, -30, -40, -40, -30, -30, -20, -30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30)}
        self.piecesquaretable = dict()
        for key in self.PMV:
            for square in self.PST[key]:
                self.piecesquaretable[key] = dict()
            for i, square in enumerate(self.PST[key]):
                self.piecesquaretable[key][i] = square + self.PMV[key]
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
        return "please don't try to make a chess engine into a string"

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
        advancedTC = False
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
        rating = chess.popcount(self.node.occupied_co[chess.BLACK] & self.node.pawns) * 1000
        rating -= chess.popcount(self.node.occupied_co[chess.WHITE] & self.node.pawns) * 1000
        rating += chess.popcount(self.node.occupied_co[chess.BLACK] & self.node.knights) * 3200
        rating -= chess.popcount(self.node.occupied_co[chess.WHITE] & self.node.knights) * 3200
        rating += chess.popcount(self.node.occupied_co[chess.BLACK] & self.node.bishops) * 3330
        rating -= chess.popcount(self.node.occupied_co[chess.WHITE] & self.node.bishops) * 3330
        rating += chess.popcount(self.node.occupied_co[chess.BLACK] & self.node.rooks) * 5100
        rating -= chess.popcount(self.node.occupied_co[chess.WHITE] & self.node.rooks) * 5100
        rating += chess.popcount(self.node.occupied_co[chess.BLACK] & self.node.queens) * 8800
        rating -= chess.popcount(self.node.occupied_co[chess.WHITE] & self.node.queens) * 8800
        return rating

    def seepos_factor(self) -> int:
        rating = sum([self.piecesquaretable['p'][i] for i in self.node.pieces(chess.PAWN, chess.BLACK)])
        rating -= sum([self.piecesquaretable['P'][i] for i in self.node.pieces(chess.PAWN, chess.WHITE)])
        rating += sum([self.piecesquaretable['n'][i] for i in self.node.pieces(chess.KNIGHT, chess.BLACK)])
        rating -= sum([self.piecesquaretable['N'][i] for i in self.node.pieces(chess.KNIGHT, chess.WHITE)])
        rating += sum([self.piecesquaretable['b'][i] for i in self.node.pieces(chess.BISHOP, chess.BLACK)])
        rating -= sum([self.piecesquaretable['B'][i] for i in self.node.pieces(chess.BISHOP, chess.WHITE)])
        rating += sum([self.piecesquaretable['r'][i] for i in self.node.pieces(chess.ROOK, chess.BLACK)])
        rating -= sum([self.piecesquaretable['R'][i] for i in self.node.pieces(chess.ROOK, chess.WHITE)])
        rating += sum([self.piecesquaretable['q'][i] for i in self.node.pieces(chess.QUEEN, chess.BLACK)])
        rating -= sum([self.piecesquaretable['Q'][i] for i in self.node.pieces(chess.QUEEN, chess.WHITE)])
        rating += sum([self.piecesquaretable['k'][i] for i in self.node.pieces(chess.KING, chess.BLACK)])
        rating -= sum([self.piecesquaretable['K'][i] for i in self.node.pieces(chess.KING, chess.WHITE)])
        return rating

    def record_eval_hash(self, key: int, smallkey: int, value: int) -> None:
        self.ett[smallkey] = {'key': key, 'score': value}

    def probe_eval_hash(self, key: int, smallkey: int) -> tuple:
        if smallkey in self.ett:
            if self.ett[smallkey]["key"] == key:
                return True
        return False

    #@profile
    def evaluate(self, depth: int) -> int:
        self.nodes += 1

        key, smallkey = self.pos_hash()
        if self.probe_eval_hash(key, smallkey):
            return self.ett[smallkey]["score"]

        rating = 0
        if self.node.is_checkmate():
            return 1000000000 * (depth+1) * (1 if self.node.turn else -1)
        if self.node.can_claim_fifty_moves():
            rating = -self.contempt * (1 if self.node.turn else -1)

        if self.pos_hash()[1] in self.hashstack:
            rating = -self.contempt * (1 if self.node.turn else -1)

        rating += self.seepos_factor()

        self.record_eval_hash(key, smallkey, rating)
        return rating

    def pos_hash(self, node=False):
            if not node: node = self.node
            key = hash(node._transposition_key())
            smallkey = key % self.tableSize
            return key, smallkey

    def record_stack(self) -> None:
        key, small = self.pos_hash()
        try:
            self.hashstack[small] += 1
        except Exception:
            self.hashstack[small] = 1

    def record_hash(self, key: int, smallkey: int, depth: int, a: int, hashDataType: int) -> None:
        if smallkey in self.hashtable:
            entry = self.hashtable[smallkey]
            if entry['depth'] >= depth:
                self.hashtable[smallkey] = {
                    'key': key, 'bestMove': self.best, 'depth': depth, 'score': a, 'type': hashDataType}
        else:
            self.hashtable[smallkey] = {
                'key': key, 'bestMove': self.best, 'depth': depth, 'score': a, 'type': hashDataType}

    def probe_hash(self, key: int, smallkey: int, depth: int = 0, a: int = -1000, b: int = 1000) -> tuple:
        if smallkey in self.hashtable:
            entry = self.hashtable[smallkey]
        else:
            return (None, None)
        if entry['key'] == key:
            if entry['depth'] >= depth:
                if entry['type'] == 0:
                    return (entry['score'], True)
                if entry['type'] == 1 and entry['score'] <= a:
                    return (a, True)
                if entry['type'] == 2 and entry['score'] >= b:
                    return (b, True)
                return (entry['bestMove'], False)
            return (entry['bestMove'], False)
        return (None, None)

    def clear_tt(self):
        self.hashtable.clear()

    def captures(self):
        return (m for m in self.node.generate_pseudo_legal_captures() if self.node.is_legal(m))

    def single_hash_iterator(self):
        yield self.best

    def ordered_moves(self):
        return (m for m in itertools.chain(
            self.single_hash_iterator(),
            self.node.generate_pseudo_legal_moves(0xffff_ffff_ffff_ffff, self.node.occupied_co[not self.node.turn]),
            self.node.generate_pseudo_legal_moves(0xffff_ffff_ffff_ffff, ~self.node.occupied_co[not self.node.turn])
        ) if self.node.is_legal(m))

    def pass_turn(self) -> None:
        self.node.turn = not self.node.turn

    def qsearch(self, a: int, b: int, depth: int, colour: int) -> int:
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

    def negamax_pvs(self, depth: int, colour: int, a: int = -1337000000, b: int = 1337000000) -> int:
        if depth < 1:
            #return colour * self.evaluate(depth)
            return self.qsearch(a, b, depth, colour)

        if self.node.is_game_over():
            return colour * self.evaluate(depth)

        hashDataType = 1
        key, smallkey = self.pos_hash()
        probe = self.probe_hash(key, smallkey, depth, a, b)
        if probe[0] != None:
            if probe[1]:
                return probe[0]
            else:
                self.best = probe[0]
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
        moves = self.ordered_moves()  # MOVE ORDERING (HASH -> TAKES -> OTHERS)
        for i, move in enumerate(moves):
            self.node.push(move)  # MAKE MOVE
            if check: depth += 1
            if i == 0:
                self.best = move
                # FULL SEARCH ON MOVE 1
                value = - self.negamax_pvs(depth - 1, -colour, -b, -a)
            else:
                # NULL-WINDOW SEARCH
                value = - self.negamax_pvs(depth - 1, -colour, -a - 1, -a)
                if a < value and value < b:  # CHECK IF NULLWINDOW FAILED
                    # RE-SEARCH
                    value = - self.negamax_pvs(depth - 1, -colour, - b, -value)
            if check: depth -= 1
            self.node.pop()  # UNMAKE MOVE
            if value >= b:
                self.record_hash(key, smallkey, depth, b, 2)
                return b
            if value > a:
                hashDataType = 0
                a = value
                self.best = move
        self.record_hash(key, smallkey, depth, a, hashDataType)
        return a

    def move_sort(self, moves: list, ratings: list):
        pairs = zip(*sorted(zip(moves, ratings), key=operator.itemgetter(1)))
        moves, ratings = [list(pair) for pair in pairs]
        return moves, ratings

    def turnmod(self) -> int:
        return -1 if self.node.turn else 1

    def show_iteration_data(self, moves: list, values: list, depth: int) -> None:
        t = round(time.time()-self.startTime, 2)
        print(self.node.san(moves[0]), '|', round((self.turnmod()*values[0])/1000, 3), '|',
              str(t)+'s at depth', str(depth + 1)+", "+str(self.nodes), "nodes processed, at " + str(int(self.nodes / (t+0.00001)))+"NPS.")
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
            self.searchdata.append(self.show_iteration_data(moves, values, depth))
            # if depth < 7 and abs(values[0]) > 300000000 and not ponder:
            # return moves[0]
        return moves[0]

    def ponder(self) -> None:
        self.origin = self.node.copy()
        self.search(ponder=True)

    def get_book_move(self):
        book = chess.polyglot.open_reader(
            r"ProDeo292/ProDeo292/books/elo2500.bin")
        main_entry = book.find(self.node)
        choice = book.weighted_choice(self.node)
        book.close()
        return main_entry.move, choice.move

    def engine_move(self) -> chess.Move:
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

    def user_move(self) -> chess.Move:
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
            print("BLACK" if self.node.turn else "WHITE", 'WINS ON TURN',
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

class Fork(Viridithas):
    def __init__(self, human=False, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', pgn='', timeLimit=15, fun=False, contempt=3000, book=True, advancedTC=False):
        super().__init__(human, fen, pgn, timeLimit, fun,
                         contempt, book, advancedTC)

    def captures(self):
        return (m for m in itertools.chain(
            self.captures_piece(self.node.queens),
            self.captures_piece(self.node.rooks),
            self.captures_piece(self.node.bishops),
            self.captures_piece(self.node.knights),
            self.captures_piece(self.node.pawns),
        ) if self.node.is_legal(m))

    def single_hash_iterator(self):
        yield self.best

    def captures_piece(self, p): # concentrate on MVV, then LVA
        return itertools.chain(
            self.node.generate_pseudo_legal_moves(self.node.occupied_co[not self.node.turn] & self.node.pawns, p),
            self.node.generate_pseudo_legal_moves(self.node.occupied_co[not self.node.turn] & self.node.knights, p),
            self.node.generate_pseudo_legal_moves(self.node.occupied_co[not self.node.turn] & self.node.bishops, p),
            self.node.generate_pseudo_legal_moves(self.node.occupied_co[not self.node.turn] & self.node.rooks, p),
            self.node.generate_pseudo_legal_moves(self.node.occupied_co[not self.node.turn] & self.node.queens, p),
            )

    def ordered_moves(self):
        return (m for m in itertools.chain(
            self.single_hash_iterator(),
            self.captures_piece(self.node.queens),
            self.captures_piece(self.node.rooks),
            self.captures_piece(self.node.bishops),
            self.captures_piece(self.node.knights),
            self.captures_piece(self.node.pawns),
            self.node.generate_pseudo_legal_moves(0xffff_ffff_ffff_ffff, ~self.node.occupied_co[not self.node.turn])
        ) if self.node.is_legal(m))

    def seepos_factor(self) -> int:
        white = self.node.occupied_co[chess.WHITE]
        black = self.node.occupied_co[chess.BLACK]
        return sum(itertools.chain(
            (self.piecesquaretable['p'][i] for i in chess.scan_forward(
                self.node.pawns & black)),
            (-self.piecesquaretable['P'][i] for i in chess.scan_forward(
                self.node.pawns & white)),
            (self.piecesquaretable['n'][i] for i in chess.scan_forward(
                self.node.knights & black)),
            (-self.piecesquaretable['N'][i] for i in chess.scan_forward(
                self.node.knights & white)),
            (self.piecesquaretable['b'][i] for i in chess.scan_forward(
                self.node.bishops & black)),
            (-self.piecesquaretable['B'][i] for i in chess.scan_forward(
                self.node.bishops & white)),
            (self.piecesquaretable['r'][i] for i in chess.scan_forward(
                self.node.rooks & black)),
            (-self.piecesquaretable['R'][i] for i in chess.scan_forward(
                self.node.rooks & white)),
            (self.piecesquaretable['q'][i] for i in chess.scan_forward(
                self.node.queens & black)),
            (-self.piecesquaretable['Q'][i] for i in chess.scan_forward(
                self.node.queens & white)),
            (self.piecesquaretable['k'][i] for i in chess.scan_forward(
                self.node.kings & black)),
            (-self.piecesquaretable['K'][i] for i in chess.scan_forward(
                self.node.kings & white))))

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

    def evaluate(self, depth: int) -> int:
        self.nodes += 1

        rating = 0
        if self.node.is_checkmate():
            return 1000000000 * (depth+1) * (1 if self.node.turn else -1)
        if self.node.can_claim_fifty_moves():
            rating = -self.contempt * (1 if self.node.turn else -1)

        if self.pos_hash()[1] in self.hashstack:
            rating = -self.contempt * (1 if self.node.turn else -1)

        rating += self.seepos_factor()

        return rating


class Antichess(Viridithas):
    def __init__(self, human=False, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', pgn='', timeLimit=15, fun=False, contempt=3000, book=True, advancedTC=False):
        super().__init__(human, fen, pgn, timeLimit, fun,
                         contempt, False, advancedTC)
        self.node = chess.variant.AntichessBoard(fen)

    def evaluate(self, depth: int) -> int:
        return sum([-1 for i in chess.SquareSet(self.node.occupied_co[0])])+sum([1 for i in chess.SquareSet(self.node.occupied_co[1])])

def selfplay(time=15, position="", usebook=False, player1=Viridithas, player2=Fork):
    e1 = player1(book=usebook, fun=True, contempt=0, fen=position, timeLimit=time)
    e2 = player2(book=usebook, fun=True, contempt=0, fen=position, timeLimit=time)

    while (not e1.node.is_game_over()) and (not e2.node.is_game_over()):
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

    e2 = player1(book=usebook, fun=True, contempt=0, fen=position, timeLimit=time)
    e1 = player2(book=usebook, fun=True, contempt=0, fen=position, timeLimit=time)
    
    while (not e1.node.is_game_over()) and (not e2.node.is_game_over()):
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
    
    return game1, game2

def general_purpose():
    init = "r1b1k1nr/1pp2ppp/p1n1pq2/3p4/3P1b2/2PBPN2/PP3PPP/RN1QK2R w KQkq - 0 1"

    engineType = input("Enter variant: Regular, Atomic, Crazyhouse, Antichess, Fork [1/2/3/4/5]: ")
    while engineType not in ['1', '2', '3', '4', '5']:
        engineType = input("Enter variant: Regular, Atomic, Crazyhouse, Antichess, Fork [1/2/3/4/5]: ")
    
    engines = [Viridithas, Atomic, Crazyhouse, Antichess, Fork]
    engine = engines[int(engineType)-1]

    engine.user_setup()
    engine.run_game()

def analysis(engineType, pos="", usebook=True, limit=1000000000000, indef=False):
    engine = engineType(book=usebook, contempt=0,
                        timeLimit=limit, fun=False, fen=pos)
    engine.run_game(indefinite=indef)
    return [elem[3:] for elem in engine.searchdata]

if __name__ == "__main__":
    #general_purpose()
    fen = input("enter fen for analysis: ")
    #fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    #fen = 'r1bqkb1r/ppp2ppp/2p2n2/8/4P3/8/PPPP1PPP/RNBQKB1R w KQkq - 0 5'
    #fen = "r1bqkb1r/ppp2ppp/2p2n2/8/4P3/8/PPPP1PPP/RNBQKB1R w KQkq - 0 5" # stafford accepted
    analysis(Viridithas, fen, False, indef=True)
    #print(selfplay(100, position=fen, player1=Viridithas, player2=Fork, usebook=False))

    #general_purpose()

# add a sorting comparison function based on moved piece
# add a separate qsearch hashtable
# add an eval hashtable -- semidone
# reimplement check ext

