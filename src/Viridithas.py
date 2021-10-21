#from __future__ import annotations
from typing import Hashable, Iterator
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
from chess import BB_ALL, WHITE, BLACK, Move, Board, scan_forward
from chess.variant import CrazyhouseBoard
from cachetools import LRUCache 
import evaluation
from evaluation import ATTACK_FACTOR, BISHOP_VALUE, FUTILITY_MARGIN, FUTILITY_MARGIN_2, FUTILITY_MARGIN_3, INF, KING_SAFETY_FACTOR, MATE_VALUE, MOBILITY_FACTOR, QUEEN_VALUE, ROOK_VALUE, SPACE_FACTOR, pawn_structure_eval, pst_eval, see_eval, PAWN_VALUE, king_safety, mobility, piece_attack_counts, space
from data_input import get_engine_parameters
from LMR import search_reduction_factor
from copy import deepcopy

# from neuraleval import neural_eval
print("Python version")
print(sys.version)

class Viridithas():
    def __init__(
        self,
        human: bool = False,
        fen: str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
        pgn: str = '',
        time_limit: float = 15,
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
        self.time_limit = time_limit
        if advancedTC:
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
        self.hashtable: dict[Hashable, TTEntry] = dict()
        self.inbook = book

    def set_position(self, fen):
        self.node = Board(fen)

    def __repr__(self) -> str:
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
            time_limit=datadict["time_limit"],
            fun=datadict["fun"],
            contempt=datadict["contempt"],
            book=datadict["book"],
            advancedTC=datadict["advancedTC"]
        )

    def gameover_check_info(self):
        checkmate = self.node.is_checkmate()
        draw = self.node.is_stalemate() or \
            self.node.is_insufficient_material( ) or \
            self.node.is_repetition() or self.node.is_seventyfive_moves() or not any(self.node.generate_legal_moves())
        return checkmate or draw, checkmate, draw

    # @profile
    def evaluate(self, depth: float, checkmate: bool, draw: bool) -> float:
        self.nodes += 1

        if checkmate:
            return MATE_VALUE * int(max(depth+1, 1)) * (1 if self.node.turn else -1)
        if draw:
            return -self.contempt * (1 if self.node.turn == WHITE else -1)

        rating: float = 0

        rating += pst_eval(self.node)
        rating += pawn_structure_eval(self.node)
        # rating += mobility(self.node)
        
        # rating += piece_attack_counts(self.node) * ATTACK_FACTOR
        # rating += king_safety(self.node) * KING_SAFETY_FACTOR
        # rating += space(self.node) * SPACE_FACTOR
        # rating += neural_eval(self.node) / 10

        return rating

    def cheap_evaluate(self, depth: float, checkmate: bool, draw: bool) -> float:
        self.nodes += 1

        if checkmate:
            return MATE_VALUE * int(max(depth+1, 1)) * (1 if self.node.turn else -1)
        if draw:
            return -self.contempt * (1 if self.node.turn == WHITE else -1)

        rating: float = 0

        rating += see_eval(self.node)

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

    def checks(self):
        """
        Generate all the checks in a position.
        """
        return (m for m in self.node.generate_pseudo_legal_moves(BB_ALL, ~self.node.occupied) if self.node.gives_check(m) and self.node.is_legal(m))

    def captures(self):  # (MVV/LVA)
        return (m for m in itertools.chain(
            self.captures_piece(
                self.node.occupied_co[not self.node.turn] & self.node.queens),
            self.captures_piece(
                self.node.occupied_co[not self.node.turn] & self.node.rooks),
            self.captures_piece(
                self.node.occupied_co[not self.node.turn] & (
                    self.node.bishops | self.node.knights)),
            self.captures_piece(
                self.node.occupied_co[not self.node.turn] & self.node.pawns),
        ) if self.node.is_legal(m))

    def checks_and_captures(self):
        return itertools.chain(self.captures(), self.checks())

    def ordered_moves(self):
        return (m for m in itertools.chain(
            self.captures_piece(
                self.node.occupied_co[not self.node.turn] & self.node.queens),
            self.captures_piece(
                self.node.occupied_co[not self.node.turn] & self.node.rooks),
            self.captures_piece(
                self.node.occupied_co[not self.node.turn] & (
                    self.node.bishops | self.node.knights)),
            self.captures_piece(
                self.node.occupied_co[not self.node.turn] & self.node.pawns),
            self.node.generate_pseudo_legal_moves(
                0xffff_ffff_ffff_ffff, ~self.node.occupied_co[not self.node.turn]),
        ) if self.node.is_legal(m))

    def pass_turn(self) -> None:
        self.node.push(Move.from_uci("0000"))

    #@profile
    def qsearch(self, alpha: float, beta: float, depth: float, colour: int, gameover: bool, checkmate: bool, draw: bool) -> float:

        val = self.evaluate(0.5, checkmate, draw) * colour
        
        if gameover:
            return val
        if val >= beta:
            return beta
        # basic delta pruning, more can be done mid-qsearch
        if (val < alpha - QUEEN_VALUE):
            return alpha
        
        alpha = max(val, alpha)

        for move in self.captures():
            self.node.push(move)
            gameover, checkmate, draw = self.gameover_check_info()
            score = -self.qsearch(-beta, -alpha, depth - 1, -colour, gameover, checkmate, draw)
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
    def negamax(self, depth: float, colour: int, alpha: float, beta: float) -> float:
        initial_alpha = alpha

        # (* Transposition Table Lookup; self.node is the lookup key for ttEntry *)
        tt_entry = self.tt_lookup(self.node)
        if not tt_entry.is_null() and tt_entry.depth >= depth:
            if tt_entry.type == EXACT:
                return tt_entry.value
            elif tt_entry.type == LOWERBOUND:
                alpha = max(alpha, tt_entry.value)
            elif tt_entry.type == UPPERBOUND:
                beta = min(beta, tt_entry.value)

            if alpha >= beta:
                return tt_entry.value
            
            if self.node.is_legal(tt_entry.best):
                moves = itertools.chain([tt_entry.best], filter(lambda x: x != tt_entry.best, self.ordered_moves()))
            else:
                moves = self.ordered_moves()
        else:
            moves = self.ordered_moves()

        gameover, checkmate, draw = self.gameover_check_info()

        if gameover:
            return colour * self.evaluate(depth, checkmate, draw)

        if depth < 1:
            # return colour * self.evaluate(depth, checkmate, draw)
            return self.qsearch(alpha, beta, depth, colour, gameover, checkmate, draw)

        current_pos_is_check = self.node.is_check()
        if not current_pos_is_check and depth >= 3 and abs(alpha) < MATE_VALUE and abs(beta) < MATE_VALUE:
            # MAKE A NULL MOVE
            self.node.push(Move.null())  
            # PERFORM A LIMITED SEARCH
            value = - self.negamax(depth - 3, -colour, -beta, -beta + 1)
            # UNMAKE NULL MOVE
            self.node.pop()

            if value >= beta:
                return beta

        do_fprune = self.do_futility_pruning(depth, colour, alpha, beta, current_pos_is_check)

        best_move = Move.null()
        search_pv = True
        value = -INF
        for move_idx, move in enumerate(moves):
            if move_idx == 0:
                best_move = move
            
            is_capture = self.node.is_capture(move)
                
            if do_fprune:
                if not is_capture and not self.node.gives_check(move): 
                    continue

            self.node.push(move)

            gives_check = self.node.is_check()
            is_promo = bool(move.promotion)

            depth_reduction = search_reduction_factor(
                move_idx, current_pos_is_check, gives_check, is_capture, is_promo, depth)
            # depth_reduction = 1
            
            if search_pv:
                r = -self.negamax(depth - depth_reduction, -colour, -beta, -alpha)
            else:
                r = -self.negamax(depth - depth_reduction, -colour, -alpha-1, -alpha)
                if (r > alpha): # // in fail-soft ... && value < beta) is common
                    # null-window failed, so re-search
                    r = -self.negamax(depth - depth_reduction, -colour, -beta, -alpha) 
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
        tt_entry.value = value
        if value <= initial_alpha:
            tt_entry.type = UPPERBOUND
        elif value >= beta:
            tt_entry.type = LOWERBOUND
        else:
            tt_entry.type = EXACT
        tt_entry.depth = depth
        tt_entry.best = best_move
        tt_entry.null = False
        self.tt_store(self.node, tt_entry)

        return value

    def do_futility_pruning(self, depth, colour, alpha, beta, current_pos_is_check):
        if not (not current_pos_is_check and abs(
                alpha) < MATE_VALUE / 2 and abs(beta) < MATE_VALUE / 2):
            return False

        see = pst_eval(self.node) * colour

        return (depth <= 1 and see + FUTILITY_MARGIN < alpha) or \
            (depth <= 2 and see + FUTILITY_MARGIN_2 < alpha) or \
            (depth <= 3 and see + FUTILITY_MARGIN_3 < alpha)

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

    def turnmod(self) -> int:
        return -1 if self.node.turn else 1

    def show_iteration_data(self, moves: list, values: list, depth: float, start: float) -> tuple:
        t = round(time.time()-start, 2)
        print(f"{self.node.san(moves[0])} | {-round((self.turnmod()*values[0])/1000, 3)} | {str(t)}s at depth {str(depth + 1)}, {str(self.nodes)} nodes processed, at {str(int(self.nodes / (t+0.00001)))}NPS.\n", f"PV: {self.pv_string()}\n", end="")
        return (self.node.san(moves[0]), self.turnmod()*values[0], self.nodes, depth+1, t)

    def windows(self):
        exps = [PAWN_VALUE / 16, PAWN_VALUE / 4, PAWN_VALUE, BISHOP_VALUE, ROOK_VALUE, QUEEN_VALUE]
        return (window for window in exps)

    def search(self, ponder: bool = False, readout: bool = True):
        val = -INF
        start_time = time.time()
        self.nodes = 0
        moves = [next(self.ordered_moves())]
        saved_position = deepcopy(self.node)

        # load the tapered eval for the position
        # yes, we are using at-root game stage eval
        # as a search-value, but it's the only way to
        # run efficiently in python
        evaluation.set_pst(self.node)
        evaluation.set_piece_values(self.node)

        alpha, beta = -INF, INF
        winds = self.windows()
        curw = next(winds)

        phasepcnt = evaluation.game_stage(self.node) * 100
        print(f"game stage: {100 - phasepcnt:.1f}% middlegame, {phasepcnt:.1f}% endgame.")

        WINDOW_FAILED = False

        try:
            depth = 1
            while depth < 40:
                best = self.tt_lookup(self.node).best
                time_elapsed = time.time() - start_time
                # check if we aren't going to finish the next search in time
                if time_elapsed > 0.5 * self.time_limit and not ponder and not WINDOW_FAILED:
                    return best, val

                val = self.negamax(
                    depth, self.turnmod(), alpha=alpha, beta=beta)

                WINDOW_FAILED = val <= alpha or val >= beta
                if WINDOW_FAILED:
                    print(
                        f"Window {curw/1000:.2f} failed: a: {-self.turnmod()*(1/1000)*alpha:.1f} b: {-self.turnmod()*(1/1000)*beta:.1f} value: {-self.turnmod()*(1/1000)*val:.1f}")
                    try:
                        curw = next(winds)
                        # We fell outside the window, so try again with a
                        # full-width window (and the same depth).
                        # Set up the window for the next iteration.
                    except StopIteration:
                        curw = float("inf")
                    alpha = alpha - curw
                    beta = beta + curw
                    continue

                best = self.tt_lookup(self.node).best
                # check if we've run out of time
                if time_elapsed > self.time_limit and not ponder:
                    return best, val

                moves = [self.tt_lookup(self.node).best]
                values = [self.tt_lookup(self.node).value]

                if readout:
                    self.show_iteration_data(moves, values, depth, start_time)

                # Set up the window for the next iteration.
                winds = self.windows()
                curw = next(winds)
                alpha = val - curw 
                beta = val + curw

                depth += 1
        except KeyboardInterrupt:
            self.node = saved_position
            pass
        return moves[0], val

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
            self.time_limit = (self.endpoint-time.time())/20
        print("Time for move: " + str(round(self.time_limit, 2)) + "s")
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
                self.time_limit = self.time_limit*2
                best, _ = self.search()
                self.node.push(best)
                print(chess.pgn.Game.from_board(self.node)[-1])
                self.inbook = False
                self.time_limit = self.time_limit/2
        else:
            best, _ = self.search()
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
        self.__init__(human=True, time_limit=timeControl, fen=fen, book=True, fun=False)
        self.fun = False
        while not self.node.is_game_over():
            print(self.__repr__())
            if player_colour == self.node.turn:
                try:
                    self.ponder()
                except KeyboardInterrupt:
                    self.node = self.origin
                    self.user_move()
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


