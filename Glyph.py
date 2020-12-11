class Glyph:
    def __init__(self):
        self.node = [0b000000000, 0b000000000]
        self.turn = 1
        self.nodes = 0
    
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
            self.turn = -1
        else:
            self.node[1] = self.node[1] ^ (1 << i) 
            self.turn = 1

    def unplay(self, i): #  only valid directly after a move, do not unplay on root, or unplay twice in a row:
        if (self.turn == 1):
            self.node[1] = self.node[1] ^ (1 << i) 
            self.turn = -1
        else:
            self.node[0] = self.node[0] ^ (1 << i) 
            self.turn = 1    

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
                self.unplay(i)
                if (score > b):
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
                self.unplay(i)
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

def main():
    glyph = Glyph()
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
    return 0 

main()
