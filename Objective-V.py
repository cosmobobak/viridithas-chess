import chess
import chess.svg
import chess.pgn
import chess.polyglot
import chess.syzygy
import random
import chess.variant
import time
import operator
import pickle

class Viridithas():
    def __init__(self, human=False, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', pgn='', timeLimit=15, fun=False, contempt=3000, book=True, oddeven='unspec'):
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
        self.fun = fun
        self.contempt = contempt
        self.human = human
        if oddeven == 'unspec':
            self.oddeven = self.human
        else:
            self.oddeven = oddeven
        self.c = len(list(self.node.legal_moves))
        self.tableSize = 2**29+49
        self.hashtable = dict()
        self.hashstack = dict()
        self.pieces = range(1, 7)
        self.best = '0000'
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
        self.evaltable = dict()
        for key in self.PMV:
            for square in self.PST[key]:
                self.evaltable[key] = dict()
            for i, square in enumerate(self.PST[key]):
                self.evaltable[key][i] = square+self.PMV[key]

    def __repr__(self):
        try:
            display(chess.svg.board(board=self.node,
                                    size=400,
                                    flipped=not self.node.turn)) # FOR A JUPYTER NOTEBOOK
            return "Viridithas-engine at position "+str(self.node.fen())
        except Exception:
            return str(self.node) + '\n' + "Viridithas-engine at position " + str(self.node.fen())

    def __str__(self):
        return "please don't try to make a chess engine into a string"

    #@profile
    def evaluate(self, depth):
        mod = 1 if self.node.turn else -1

        if self.node.is_checkmate():
            return 1000000000*(depth+1)*mod
        if self.node.is_repetition():
            rating = -self.contempt*mod
        elif self.node.can_claim_fifty_moves():
            rating = -self.contempt*mod
        else:
            rating = 0
        rating += sum([self.evaltable['p'][i] for i in self.node.pieces(chess.PAWN, chess.BLACK)])
        rating -= sum([self.evaltable['P'][i] for i in self.node.pieces(chess.PAWN, chess.WHITE)])
        rating += sum([self.evaltable['n'][i] for i in self.node.pieces(chess.KNIGHT, chess.BLACK)]) 
        rating -= sum([self.evaltable['N'][i] for i in self.node.pieces(chess.KNIGHT, chess.WHITE)])
        rating += sum([self.evaltable['b'][i] for i in self.node.pieces(chess.BISHOP, chess.BLACK)])
        rating -= sum([self.evaltable['B'][i] for i in self.node.pieces(chess.BISHOP, chess.WHITE)])
        rating += sum([self.evaltable['r'][i] for i in self.node.pieces(chess.ROOK, chess.BLACK)])
        rating -= sum([self.evaltable['R'][i] for i in self.node.pieces(chess.ROOK, chess.WHITE)])
        rating += sum([self.evaltable['q'][i] for i in self.node.pieces(chess.QUEEN, chess.BLACK)])
        rating -= sum([self.evaltable['Q'][i] for i in self.node.pieces(chess.QUEEN, chess.WHITE)])
        rating += sum([self.evaltable['k'][i] for i in self.node.pieces(chess.KING, chess.BLACK)])
        rating -= sum([self.evaltable['K'][i] for i in self.node.pieces(chess.KING, chess.WHITE)])
        
        return rating

    def record_stack(self):
        key = self.pos_hash()
        try:
            self.hashstack[key] += 1
        except Exception:
            self.hashstack[key] = 1

    def record_hash(self, key, hash, depth, a, hashDataType):
        if abs(a) > 999999000:
            a = 999999000*a/abs(a)
        try:
            entry = self.hashtable[hash]
            if entry['depth'] >= depth:
                self.hashtable[hash] = {
                    'key': key, 'bestMove': self.best, 'depth': depth, 'score': a, 'type': hashDataType}
        except Exception:
            try:
                self.hashtable[hash] = {
                    'key': key, 'bestMove': self.best, 'depth': depth, 'score': a, 'type': hashDataType}
            except MemoryError:
                self.hashtable.clear()

    def probe_hash(self, key, hash, depth, a, b):
        try:
            entry = self.hashtable[hash]
        except KeyError:
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

    #@profile
    def ordered_moves(self):
        moves = list(self.node.legal_moves)
        hashmove = [moves.pop(i) for i, move in enumerate(moves) if move == self.best]
        takes = [moves.pop(i) for i, move in enumerate(moves) if self.node.is_capture(move)]
        return hashmove + takes + moves

    def pos_hash(self):
        key = hash(self.node._transposition_key())
        small = key % self.tableSize
        return key, small

    #@profile
    def principal_variation_search(self, depth, colour, a=-1337000000, b=1337000000):
        hashDataType = 1
        if depth < 1:
            return colour * self.evaluate(depth)
        if self.node.is_game_over():
            return colour * self.evaluate(depth)
        key, hash = self.pos_hash()
        probe = self.probe_hash(key, hash, depth, a, b)
        if probe[0] != None:
            if probe[1]:
                return probe[0]
            else:
                self.best = probe[0]
        # NULLMOVE PRUNING
        if not self.node.is_check():
            self.node.push(chess.Move.null()) # MAKE A NULL MOVE
            value = - self.principal_variation_search(depth - 3, -colour, -b, -a) # PERFORM A LIMITED SEARCH
            self.node.pop() # UNMAKE NULL MOVE
            a = max(a, value)
            if a >= b:
                return a
            check = False
        else:
            check = True
        moves = self.ordered_moves()  # MOVE ORDERING (HASH -> TAKES -> OTHERS)
        self.best = moves[0]
        firstmove = True
        for i, move in enumerate(moves):
            if check: # CHECK EXTENSION ON MOVES FROM THIS NODE
                depth += 1
            self.node.push(move) # MAKE MOVE
            if firstmove:
                value = - self.principal_variation_search(depth - 1, -colour, -b, -a) # FULL SEARCH ON MOVE 1
                firstmove = False
            else:
                value = - self.principal_variation_search(depth - 1, -colour, -a - 1, -a) # NULL-WINDOW SEARCH
                if a < value and value < b: # CHECK IF NULLWINDOW FAILED
                    value = - self.principal_variation_search(depth - 1, -colour, - b, -value) # RE-SEARCH
            self.node.pop()  # UNMAKE MOVE
            if check: # CHECK NODE FINISHED, UNEXTEND
                depth -= 1
            if value >= b:
                self.record_hash(key, hash, depth, b, 2)
                return b
            if value > a:
                hashDataType = 0
                a = value
                self.best = moves[i]
        self.record_hash(key, hash, depth, a, hashDataType)
        return a

    def move_sort(self, moves, ratings):
        pairs = zip(*sorted(zip(moves, ratings), key=operator.itemgetter(1)))
        moves, ratings = [list(pair) for pair in pairs]
        return moves, ratings

    def turnmod(self):
        return -1 if self.node.turn else 1

    def show_iteration_data(self, moves, values, depth):
        print(self.node.san(moves[0]), '|', round(self.turnmod()*values[0], 3), '|',
              str(round(time.time()-self.startTime, 2))+'s at depth', depth + 1)

    def search(self):
        self.startTime = time.time()

        moves = self.ordered_moves()
        values = [0.0]*len(moves)
        step = 2 if self.oddeven else 1

        for depth in range(1, 30, step):
            if self.timeLimit*2/3 < time.time()-self.startTime:
                return moves[0]
            for i, move in enumerate(moves):
                self.node.push(move)
                values[i] = self.principal_variation_search(depth, self.turnmod())
                self.node.pop()
                if self.timeLimit < time.time()-self.startTime:
                    return moves[0]
            moves, values = self.move_sort(moves, values)
            self.show_iteration_data(moves, values, depth)
        return moves[0]

    def get_book_move(self):
        book = chess.polyglot.open_reader(
            r"ProDeo292/ProDeo292/books/elo2500.bin")
        main_entry = book.find(self.node)
        choice = book.weighted_choice(self.node)
        book.close()
        return main_entry.move, choice.move

    def play(self):
        if self.inbook:
            try:
                best, choice = self.get_book_move()
                if self.fun:
                    self.node.push(choice)
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

    def display_ending(self):
        if self.node.is_stalemate():
            print('END BY STALEMATE')
        elif self.node.is_insufficient_material():
            print('END BY INSUFFICIENT MATERIAL')
        elif self.node.is_fivefold_repetition():
            print('END BY FIVEFOLD REPETITION')
        elif self.node.is_checkmate:
            print(self.node.turn, 'WINS ON TURN',
                  self.node.fullmove_number)
        else:
            print('END BY UNKNOWN REASON')

    def user_move(self):
        move = input("enter move: ")
        while True:
            try:
                self.node.push_san(move)
                break
            except Exception:
                move = input("enter move: ")

    def run_game(self, string=''):
        while not self.node.is_game_over():
            print(self.__repr__())
            if self.human and self.node.turn:
                self.user_move()
            else: # SWAP THESE ASAP
                self.play()
        self.display_ending()
        return str(chess.pgn.Game.from_board(self.node)[-1])

class Atomic(Viridithas):
    def __init__(self, human=False, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', pgn='', timeLimit=15, fun=False, contempt=3000, book=True, oddeven='unspec'):
        super().__init__(human, fen, pgn, timeLimit, fun, contempt, False, oddeven)
        self.node = chess.variant.AtomicBoard(fen)

class Crazyhouse(Viridithas):
    def __init__(self, human=False, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', pgn='', timeLimit=15, fun=False, contempt=3000, book=True, oddeven='unspec'):
        super().__init__(human, fen, pgn, timeLimit, fun, contempt, book, oddeven)
        self.node = chess.variant.CrazyhouseBoard(fen)
        self.tracker = (1000, 3200, 3330, 5100, 8800)
    
    def evaluate(self, depth):
        pocketmod = sum([v * self.node.pockets[0].count(i) for i, v in enumerate(self.tracker)])
        pocketmod -= sum([v * self.node.pockets[1].count(i) for i, v in enumerate(self.tracker)])
        return super().evaluate(depth) + pocketmod

class Antichess(Viridithas):
    def __init__(self, human=False, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', pgn='', timeLimit=15, fun=False, contempt=3000, book=True, oddeven='unspec'):
        super().__init__(human, fen, pgn, timeLimit, fun, contempt, False, oddeven)
        self.node = chess.variant.AntichessBoard(fen)
        try:  # THIS DOES NOT SEEM TO WORK YET
            f = open("antichess_hash.pkl", "wb")
            self.hashtable = pickle.load(f)
            f.close()
        except Exception:
            try:
                f.close()
            except Exception:
                pass
    
    def pickle_populate(self):  # THIS DOES NOT SEEM TO WORK YET
        try:
            save = self.timeLimit
            self.timeLimit = 10000000000
            self.search()
        except KeyboardInterrupt:
            self.timeLimit = save
            f = open("antichess_hash.pkl", "wb")
            pickle.dump(self.hashtable, f)
            f.close()

    def evaluate(self, depth):
        #ADD WHITE, SUB BLACK

        mod = 1 if self.node.turn else -1
        if self.node.is_repetition():
            return -self.contempt*mod
        elif self.node.can_claim_fifty_moves():
            return -self.contempt*mod
        else:
            return sum([-1 for i in chess.SquareSet(self.node.occupied_co[0])])+sum([1 for i in chess.SquareSet(self.node.occupied_co[1])])

init = "r2qk2r/p1p2ppp/2b1pn2/p2p4/3P1B2/2P1PN2/P3QPPP/RN2K2R w KQkq - 0 1"

engine = Antichess(oddeven=True, timeLimit=5, human=True)

engine.run_game()