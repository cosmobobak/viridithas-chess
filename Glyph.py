from copy import deepcopy
from random import choice

Move = int

class State:
    def __init__(self, inputG = None):
        if inputG != None:
            self.node = [m for m in inputG.node]
            self.turn = inputG.turn
            self.nodes = inputG.nodes
            self.stack = [m for m in inputG.stack]
        else:
            self.node = [0b000000000, 0b000000000]
            self.turn = 1
            self.nodes = 0
            self.stack = []

    def __hash__(self):
        return hash(self.node[0]) + hash(self.node[1])

    def __eq__(self, other):
        return (self.turn == other.turn) and (self.node[0] == other.node[0]) and (self.node[1] == other.node[1])
    
    def reset_nodes(self):
        self.nodes = 0

    def pos_filled(self, i):
        if ((self.node[0] & (1 << i)) != 0):
            return True
        elif ((self.node[1] & (1 << i)) != 0):
            return True
        return False

    def player_at(self, i): # only valid to use if self.pos_filled() returns True:
        if ((self.node[0] & (1 << i)) != 0):
            return True 
        else:
            return False

    def is_full(self):
        for i in range(9):
            if not self.pos_filled(i):
                return False
        return True

    def __repr__(self):
        builder = ""
        for x in range(3):
            for y in range(3):
                if (self.pos_filled(x * 3 + y)):
                    if (self.player_at(x * 3 + y)):
                        builder += "X "
                    else:
                        builder += "0 "
                else:
                    builder += ". "
            builder += '\n'
        builder += '\n'
        return builder

    def play(self, i):
        #  n ^ (1, k) is a binary XOR where you flip the kth bit of n
        if (self.turn == 1):
            self.node[0] = self.node[0] ^ (1 << i)
        else:
            self.node[1] = self.node[1] ^ (1 << i)
        self.turn = -self.turn
        self.stack.append(i)

    def unplay(self): #  only valid directly after a move, do not unplay on root, or unplay twice in a row:
        i = self.stack.pop()
        if (self.turn == 1):
            self.node[1] = self.node[1] ^ (1 << i)
        else:
            self.node[0] = self.node[0] ^ (1 << i)
        self.turn = -self.turn

    def push(self, i):
        self.play(i)

    def pop(self):
        self.unplay()

    def evaluate(self):
        self.nodes += 1  # increment nodes
        #  check first diagonal
        if (self.pos_filled(0) and self.pos_filled(4) and self.pos_filled(8)):
            if (self.player_at(0) == self.player_at(4) and self.player_at(4) == self.player_at(8)):
                if (self.player_at(0)):
                    return 1
                else:
                    return -1
        
        #  check second diagonal
        if (self.pos_filled(2) and self.pos_filled(4) and self.pos_filled(6)):
            if (self.player_at(2) == self.player_at(4) and self.player_at(4) == self.player_at(6)):
                if (self.player_at(2)):
                    return 1 
                else:
                    return -1
        
        #  check rows
        for i in range(3):
            if (self.pos_filled(i * 3) and self.pos_filled(i * 3 + 1) and self.pos_filled(i * 3 + 2)):
                if (self.player_at(i * 3) == self.player_at(i * 3 + 1) and self.player_at(i * 3 + 1) == self.player_at(i * 3 + 2)):
                    if (self.player_at(i * 3)):
                        return 1
                    else:
                        return -1
        
        #  check columns
        for i in range(3):
            if (self.pos_filled(i) and self.pos_filled(i + 3) and self.pos_filled(i + 6)):
                if (self.player_at(i) == self.player_at(i + 3) and self.player_at(i + 3) == self.player_at(i + 6)):
                    if (self.player_at(i)):
                        return 1
                    else:
                        return -1
        return 0 
    
    def negamax(self, turn, a = -2, b = 2):
        if (self.evaluate() != 0 or self.is_full() == True):
            return self.turn * self.evaluate()
        for i in range(9):
            if (not self.pos_filled(i)):
                self.play(i)
                score = -self.negamax(-turn, -b, -a)
                self.unplay()
                if (score >= b):
                    return b
                if (score > a):
                    a = score
        return a

    def engine_move(self):
        scores = [-2, -2, -2, -2, -2, -2, -2, -2, -2] 
        for i in range(9):
            if (not self.pos_filled(i)):
                self.play(i) 
                scores[i] = -self.negamax(self.turn, -2, 2)
                self.unplay()
        index = scores.index(max(scores))
        self.play(index)

    def show_result(self):
        r = self.evaluate()
        if (r == 0):
            print("1/2-1/2", '\n', end="")
        elif (r == 1):
            print("1-0", '\n', end="")
        else:
            print("0-1", '\n' , end="")

    def copy(self):
        return deepcopy(self)

    def is_game_over(self):
        return self.is_full() or (self.evaluate() != 0)

    def legal_moves(self):
        return [m for m in range(9) if not self.pos_filled(m)]

    def random_play(self):
        self.play(choice(self.legal_moves()))

def fnegamax(node: State, turn, a=-2, b=2):
    if (node.evaluate() != 0 or node.is_full() == True):
        return node.turn * node.evaluate()
    for i in range(9):
        if (not node.pos_filled(i)):
            node.play(i)
            score = -fnegamax(-turn, -b, -a)
            node.unplay()
            if (score >= b):
                return b
            if (score > a):
                a = score
    return a

if __name__ == "__main__":
    glyph = State()
    i = int(input())
    glyph.play(i) 
    print(glyph) 

    while (glyph.evaluate() == 0 and glyph.is_full() == False):
        glyph.engine_move()
        print("Nodes processed for move: ", glyph.nodes, "\n" , end="")
        glyph.reset_nodes() 
        print(glyph) 
        if (glyph.evaluate() != 0 or glyph.is_full() == True):
            break
        i = int(input())
        glyph.play(i) 
        print(glyph) 
    
    glyph.show_result()
