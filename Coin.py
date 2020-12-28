from time import time
from cachetools import LFUCache
from typing import Hashable

class Coin:
    def __init__(self, timelimit=10):
        self.node = [
            ['.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.'],
        ]

        self.turn = 1
        self.nodes = 0
        self.players = ['X', 'O']
        self.timelimit = timelimit

        self.ttsize = 1234567
        self.hashtable = LFUCache(maxsize=self.ttsize)

    def pass_turn(self):
        self.turn = -self.turn

    def get_key(self):
        return "".join(map(lambda x: "".join(x), self.node))

    def is_full(self):  # -> bool //WORKING
        return all((self.node[row][col] != '.' for row in range(6) for col in range(7)))

    def show(self):  # //WORKING
        for row in range(6):
            for col in range(7):
                print(self.node[row][col], end=' ')
            print()
        print()

    def legal_moves(self):  # -> std::vector<int>
        return filter(lambda x: self.node[0][x] == '.', [3, 4, 2, 5, 1, 6, 0])

    def play(self, col):  # //WORKING
        for row in range(6):
            if (self.node[row][col] != '.'):
                if (self.turn == 1):
                    self.node[row - 1][col] = self.players[0]
                    break
                else:
                    self.node[row - 1][col] = self.players[1]
                    break

            elif (row == 5):
                if (self.turn == 1):
                    self.node[row][col] = self.players[0]
                else:
                    self.node[row][col] = self.players[1]
        self.turn = -self.turn

    def unplay(self, col):  # //WORKING
        for row in range(6):
            if (self.node[row][col] != '.'):
                self.node[row][col] = '.'
                break
        self.turn = -self.turn

    def horizontal_term(self):  # -> int
        for row in range(6):
            for col in range(4):
                if (self.node[row][col] == self.node[row][col + 1] and
                        self.node[row][col + 1] == self.node[row][col + 2] and
                        self.node[row][col + 2] == self.node[row][col + 3]):
                    if (self.node[row][col] == self.players[0]):
                        return 1
                    elif (self.node[row][col] == self.players[1]):
                        return -1

    def vertical_term(self):  # -> int
        for row in range(3):
            for col in range(7):
                if (self.node[row][col] == self.node[row + 1][col] and
                        self.node[row + 1][col] == self.node[row + 2][col] and
                        self.node[row + 2][col] == self.node[row + 3][col]):
                    if (self.node[row][col] == self.players[0]):
                        return 1
                    elif (self.node[row][col] == self.players[1]):
                        return -1

    def diagup_term(self):  # -> int
        for row in range(3, 6):
            for col in range(4):
                if (self.node[row][col] == self.node[row - 1][col + 1] and
                        self.node[row - 1][col + 1] == self.node[row -
                                                                 2][col +
                                                                    2] and
                        self.node[row - 2][col + 2] == self.node[row - 3][col +
                                                                          3]):
                    if (self.node[row][col] == self.players[0]):
                        return 1
                    elif (self.node[row][col] == self.players[1]):
                        return -1

    def diagdown_term(self):  # -> int
        for row in range(3):
            for col in range(4):
                if (self.node[row][col] == self.node[row + 1][col + 1] and
                        self.node[row + 1][col + 1] == self.node[row + 2][col + 2] and
                        self.node[row + 2][col + 2] == self.node[row + 3][col + 3]):
                    if (self.node[row][col] == self.players[0]):
                        return 1
                    elif (self.node[row][col] == self.players[1]):
                        return -1

    def evaluate(self):  # -> int
        self.nodes += 1
        v = self.vertical_term()
        if v:
            return v
        h = self.horizontal_term()
        if h:
            return h
        u = self.diagup_term()
        if u:
            return u
        d = self.diagdown_term()
        if d:
            return d

        return 0

    def record_hash(self, key: str, depth: float, a: int,
                    hashDataType: int) -> None:
        if key in self.hashtable:
            entry = self.hashtable[key]
            if entry['depth'] >= depth:
                self.hashtable[key] = {
                    'key': key,
                    'depth': depth,
                    'score': a,
                    'type': hashDataType
                }
        else:
            self.hashtable[key] = {
                'key': key,
                'depth': depth,
                'score': a,
                'type': hashDataType
            }

    def probe_hash(self, key: str, depth: float = 0, a: int = -2,
                   b: int = 2) -> tuple:

        entry = self.hashtable.get(key, False)
        if not entry:
            return (None, None)

        if entry['depth'] >= depth:
            if entry['type'] == 0:
                return (entry['score'], True)
            if entry['type'] == 1 and entry['score'] <= a:
                return (a, True)
            if entry['type'] == 2 and entry['score'] >= b:
                return (b, True)
            return (None, False)
        return (None, False)

    def negamax(self, depth=10, colour=1, a=-2, b=2):  # -> int //WORKING
        if depth < 1:
            return colour * self.evaluate()

        if self.is_game_over():
            return colour * self.evaluate()
        ###############################
        hashDataType = 1
        key = self.get_key()
        probe = self.probe_hash(key, depth, a, b)
        if probe[0] != None:
            if probe[1]:
                return probe[0]
        ###############################
        self.pass_turn()  # MAKE A NULL MOVE
        # PERFORM A LIMITED SEARCH
        value = - self.negamax(depth - 3, -colour, -b, -a)
        self.pass_turn()  # UNMAKE NULL MOVE
        a = max(a, value)
        if a >= b:
            return a
        ###############################
        for col in self.legal_moves():
            self.play(col)
            self.nodes += 1
            score = -self.negamax(depth - 1, -colour, -b, -a)
            self.unplay(col)

            if (score >= b):
                self.record_hash(key, depth, b, 2)
                return b
            if (score > a):
                hashDataType = 0
                a = score
        ###############################
        self.record_hash(key, depth, a, hashDataType)
        return a

    def engine_move(self):  # //WORKING
        self.nodes = 0
        bestcase = -2
        bestmove = None
        d = 0
        sstart = time()
        while time() - sstart < self.timelimit:
            bestcase = -2
            start = time()
            for i, move in enumerate(self.legal_moves()):
                if i == 0:
                    bestmove = move
                self.play(move)
                score = -self.negamax(d, self.turn)
                print("█", end="")
                self.unplay(move)
                if bestcase < score:
                    bestcase = score
                    bestmove = move
            t = (time()-start)
            print(
                f"| {bestmove+1} | {bestcase} | {t:.2f}s at depth {d}, {self.nodes} nodes processed, at {str(int(self.nodes / (t+0.00001)))}NPS."
            )
            d += 1
        self.play(bestmove)

    def show_result(self):  # //WORKING
        r = self.evaluate()
        if (r == 0):
            print("1/2-1/2")
        elif (r > 0):
            print("1-0")
        else:
            print("0-1")

    def is_game_over(self):  # -> int
        return (self.evaluate() != 0 or self.is_full() == True)




if __name__ == "__main__":
    coin = Coin(5)
    coin.show()
    while (coin.is_game_over() == False):
        playermove = int(input("Enter column:\n--> "))-1
        while playermove not in coin.legal_moves():
            playermove = int(input("Enter legal column:\n--> "))-1
        coin.play(playermove)
        coin.show()
        if coin.is_game_over():
            break
        coin.engine_move()
        coin.show()
    coin.show_result()
