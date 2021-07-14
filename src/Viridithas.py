#from __future__ import annotations
from typing import Hashable
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
from TTEntry import *
from chess import WHITE, BLACK, Move, Board, scan_forward
from chess.variant import CrazyhouseBoard
from cachetools import LRUCache 
from evaluation import ATTACK_FACTOR, KING_SAFETY_FACTOR, MOBILITY_FACTOR, PIECE_VALUES, QUEEN_VALUE, SPACE_FACTOR, chessboard_pst_eval, chessboard_static_exchange_eval, PAWN_VALUE, king_safety, mobility, piece_attack_counts, space
from data_input import get_engine_parameters
from LMR import search_reduction_factor
from copy import deepcopy
print("Python version")
print(sys.version)

class Viridithas():
    def __init__(
        self,
        human: bool = False,
        fen: str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
        pgn: str = '',
        timeLimit: int = 15,
        fun: bool = False,
        contempt: int = 3000,
        book: bool = True,
        advancedTC: list = [],
    ):
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
        self.tableSize = 2**20+49
        self.hashtable: dict[Hashable, TTEntry] = dict()#LRUCache(
            #maxsize=self.tableSize)
        self.pieces = range(1, 7)
        self.inbook = book
        self.ext = False
        self.searchdata = []

    def set_position(self, fen):
        self.node = Board(fen)

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

    def user_setup(self):
        if input("Do you want to configure the bot? (Y/N) ").upper() != 'Y':
            return

        myname = self.__class__.__name__.upper()

        print(f"BEGINNING USER CONFIGURATION OF {myname}-BOT")

        datadict = get_engine_parameters()

        self.__init__(
            human=datadict["human"],
            fen=datadict["fen"],
            pgn=datadict["pgn"],
            timeLimit=datadict["timeLimit"],
            fun=datadict["fun"],
            contempt=datadict["contempt"],
            book=datadict["book"],
            advancedTC=datadict["advancedTC"]
        )

    # @profile
    def evaluate(self, depth: float) -> float:
        self.nodes += 1

        rating: float = 0
        if self.node.is_checkmate():
            return 1000000000 * int(depth+1) * (1 if self.node.turn else -1)
        if self.node.can_claim_fifty_moves():
            rating = -self.contempt * (1 if self.node.turn else -1)

        if self.node.is_repetition(2):
            return  -self.contempt * (1 if self.node.turn else -1)

        rating += chessboard_pst_eval(self.node)
        # rating += chessboard_static_exchange_eval(self.node)

        # rating += mobility(self.node) * MOBILITY_FACTOR
        
        # rating += piece_attack_counts(self.node) * ATTACK_FACTOR

        # rating += king_safety(self.node) * KING_SAFETY_FACTOR

        # rating += space(self.node) * SPACE_FACTOR

        return rating

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

    #@profile
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

    def winning_captures(self):  # (MVV/LVA)
        target_all = self.node.occupied_co[not self.node.turn]
        target_3 = target_all & ~self.node.pawns
        target_5 = target_3 & (~self.node.bishops | ~self.node.knights)
        target_9 = target_5 & ~self.node.rooks
        return itertools.chain(
            self.node.generate_pseudo_legal_moves(self.node.pawns, target_all),
            self.node.generate_pseudo_legal_moves(self.node.knights, target_3),
            self.node.generate_pseudo_legal_moves(self.node.bishops, target_3),
            self.node.generate_pseudo_legal_moves(self.node.rooks, target_5),
            self.node.generate_pseudo_legal_moves(self.node.queens, target_9),
            self.node.generate_pseudo_legal_moves(self.node.kings, target_9),
        )

    def losing_captures(self):  # (MVV/LVA)
        target_pawns = self.node.pawns
        target_pnb = target_pawns | self.node.bishops | self.node.knights
        target_pnbr = target_pnb | self.node.rooks
        return itertools.chain(
            self.node.generate_pseudo_legal_moves(self.node.knights, target_pawns),
            self.node.generate_pseudo_legal_moves(self.node.bishops, target_pawns),
            self.node.generate_pseudo_legal_moves(self.node.rooks, target_pnb),
            self.node.generate_pseudo_legal_moves(self.node.queens, target_pnbr),
            self.node.generate_pseudo_legal_moves(self.node.kings, target_pnbr),
        )

    def ordered_moves(self):
        return (m for m in itertools.chain(
            self.winning_captures(),
            # self.captures_piece(
            #     self.node.occupied_co[not self.node.turn] & self.node.queens),
            # self.captures_piece(
            #     self.node.occupied_co[not self.node.turn] & self.node.rooks),
            # self.captures_piece(
            #     self.node.occupied_co[not self.node.turn] & self.node.bishops),
            # self.captures_piece(
            #     self.node.occupied_co[not self.node.turn] & self.node.knights),
            # self.captures_piece(
            #     self.node.occupied_co[not self.node.turn] & self.node.pawns),
            self.node.generate_pseudo_legal_moves(
                0xffff_ffff_ffff_ffff, ~self.node.occupied_co[not self.node.turn]),
            self.losing_captures()
        ) if self.node.is_legal(m))

    def pass_turn(self) -> None:
        self.node.push(Move.from_uci("0000"))

    #@profile
    def qsearch(self, alpha: float, beta: float, depth: float, colour: int) -> float:
        val = self.evaluate(1) * colour
        if val >= beta:
            return beta
        if (val < alpha - QUEEN_VALUE):
            return alpha
        
        alpha = max(val, alpha)

        for capture in self.captures():
            self.node.push(capture)
            score = -self.qsearch(-beta, -alpha, depth - 1, -colour)
            self.node.pop()
            if score >= beta:
                return score
            alpha = max(score, alpha)

        return alpha

    def tt_lookup(self, board: Board) -> "TTEntry":
        key = board._transposition_key()
        return self.hashtable.get(key, TTEntry.default())

    def tt_store(self, board: Board, entry: TTEntry):
        key = board._transposition_key()    
        self.hashtable[key] = entry

    #@profile
    def wikisearch(self, depth: float, colour: int, alpha: float, beta: float) -> float:
        alphaOrig = alpha

        # (* Transposition Table Lookup; self.node is the lookup key for ttEntry *)
        ttEntry = self.tt_lookup(self.node)
        if not ttEntry.is_null() and ttEntry.depth >= depth:
            if ttEntry.type == EXACT:
                return ttEntry.value
            elif ttEntry.type == LOWERBOUND:
                alpha = max(alpha, ttEntry.value)
            elif ttEntry.type == UPPERBOUND:
                beta = min(beta, ttEntry.value)

            if alpha >= beta:
                return ttEntry.value
            
            if self.node.is_legal(ttEntry.best):
                moves = itertools.chain([ttEntry.best], filter(lambda x: x != ttEntry.best, self.ordered_moves()))
            else:
                moves = self.ordered_moves()
        else:
            moves = self.ordered_moves()

        if depth < 0:
            return self.qsearch(alpha, beta, depth, colour)

        if self.node.is_game_over():
            return colour * self.evaluate(depth)

        current_pos_is_check = self.node.is_check()
        if not current_pos_is_check and depth >= 3:
            # MAKE A NULL MOVE
            self.node.push(Move.null())  
            # PERFORM A LIMITED SEARCH
            value = - self.wikisearch(depth - 3, -colour, -beta, -alpha)
            # UNMAKE NULL MOVE
            self.node.pop()
            if value >= beta:
                return beta

        best_move = Move.null()
        search_pv = True
        value = float("-inf")
        for move_idx, move in enumerate(moves):
            if move_idx == 0:
                best_move = move
            gives_check = self.node.gives_check(move)
            is_capture = self.node.is_capture(move)
            is_promo = bool(move.promotion)
            depth_reduction = search_reduction_factor(
                move_idx, current_pos_is_check, gives_check, is_capture, is_promo, depth)

            self.node.push(move)

            if search_pv:
                r = -self.wikisearch(depth - depth_reduction, -colour, -beta, -alpha)
                value = max(value, r)
            else:
                r = -self.wikisearch(depth - depth_reduction, -colour, -alpha-1, -alpha)
                value = max(value, r)
                if (value > alpha): # // in fail-soft ... & & value < beta) is common
                    r = -self.wikisearch(depth - depth_reduction, -colour, -beta, -alpha) #// re-search
                    value = max(value, r)

            self.node.pop()

            if value > alpha:
                alpha = value
                best_move = move
            alpha = max(alpha, value)
            if alpha >= beta:
                break
            search_pv = False

        # (* Transposition Table Store; self.node is the lookup key for ttEntry *)
        # ttEntry = TTEntry()
        ttEntry.value = value
        if value <= alphaOrig:
            ttEntry.type = UPPERBOUND
        elif value >= beta:
            ttEntry.type = LOWERBOUND
        else:
            ttEntry.type = EXACT
        ttEntry.depth = depth
        ttEntry.best = best_move
        ttEntry.null = False
        self.tt_store(self.node, ttEntry)

        return value

    def move_sort(self, moves: list, ratings: list):
        pairs = zip(*sorted(zip(moves, ratings), key=operator.itemgetter(1)))
        moves, ratings = [list(pair) for pair in pairs]
        return moves, ratings

    def pv_string(self):
        count = 0
        moves = []
        while True:
            e = self.tt_lookup(self.node)
            if e.is_null() or not self.node.is_legal(e.best):
                break

            # print(self.node.__str__())
            # print(self.node.__repr__())
            # print(e.best)
            # print(self.node.san(e.best))

            moves.append(self.node.san(e.best))
            self.node.push(e.best)
            count += 1
        
        for _ in moves:
            self.node.pop()

        if count == 0: return ""
        return " ".join(moves)
        return ""

    def turnmod(self) -> int:
        return -1 if self.node.turn else 1

    def show_iteration_data(self, moves: list, values: list, depth: float) -> tuple:
        t = round(time.time()-self.startTime, 2)
        print(f"{self.node.san(moves[0])} | {-round((self.turnmod()*values[0])/1000, 3)} | {str(t)}s at depth {str(depth + 1)}, {str(self.nodes)} nodes processed, at {str(int(self.nodes / (t+0.00001)))}NPS.\n", f"PV: {self.pv_string()}\n", end="")
        return (self.node.san(moves[0]), self.turnmod()*values[0], self.nodes, depth+1, t)

    def search(self, ponder: bool = False):

        start_time = time.time()
        self.startTime = start_time
        self.nodes = 0
        moves = [next(self.ordered_moves())]
        saved_position = deepcopy(self.node)

        alpha, beta = float("-inf"), float("inf")
        valWINDOW = PAWN_VALUE / 4

        try:
            depth = 0
            while depth < 40:
                best = self.tt_lookup(self.node).best
                time_elapsed = time.time() - start_time
                # check if we aren't going to finish the next search in time
                if time_elapsed > 0.5 * self.timeLimit and not ponder:
                    return best

                val = self.wikisearch(
                    depth, self.turnmod(), alpha=alpha, beta=beta)
                if ((val <= alpha) or (val >= beta)):
                    # We fell outside the window, so try again with a
                    # full-width window (and the same depth).
                    alpha = float("-inf")
                    beta = float("inf")
                    continue

                best = self.tt_lookup(self.node).best
                # check if we've run out of time
                if time_elapsed > self.timeLimit and not ponder:
                    return best

                moves = [self.tt_lookup(self.node).best]
                values = [self.tt_lookup(self.node).value]
                self.searchdata.append(self.show_iteration_data(moves, values, depth))

                alpha = val - valWINDOW # Set up the window for the next iteration.
                beta = val + valWINDOW
                depth += 1
        except KeyboardInterrupt:
            self.node = saved_position
            pass
        return moves[0]

    def ponder(self) -> None:
        self.origin = self.node.copy()
        self.search(ponder=True)

    def get_book_move(self):
        # book = chess.polyglot.open_reader(
        #     r"ProDeo292/ProDeo292/books/elo2500.bin")
        book = chess.polyglot.open_reader(
            r"books/elo2500.bin")
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
        # self.record_stack()
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
        self.__init__(human=True, timeLimit=timeControl, fen=fen, book=True, fun=False)
        self.fun = False
        while not self.node.is_game_over():
            print(self.__repr__())
            if player_colour == self.node.turn:
                # try:
                #     self.ponder()
                # except KeyboardInterrupt:
                #     self.node = self.origin
                #     self.user_move()
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


