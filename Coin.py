from time import time

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
        
        self.hashtable = dict()
        self.ttsize = 1234567
        
    def __hash__(self):
        return hash("".join(map(lambda x: "".join(x), self.node)))
        
    def is_full(self):# -> bool //WORKING        
        for row in range(6):
            for col in range(7):
                if (self.node[row][col] == '.'):
                    return False                   
        return True
        
    def show(self): #//WORKING                  
        for row in range(6):
            for col in range(7):
                print(self.node[row][col], end=' ')                
            print()       
        print()      

    def legal_moves(self):# -> std::vector<int>
        moves = []
        for col in [3,4,2,5,1,6,0]:           
            if (self.node[0][col] == '.'):               
                moves.append(col);                        
        return moves       

    def play(self, col):# //WORKING
        for row in range(6):
            if (self.node[row][col] != '.'):
                if (self.turn == 1):
                    self.node[row - 1][col] = self.players[0]
                    self.turn = -1
                    break
                else:
                    self.node[row - 1][col] = self.players[1]
                    self.turn = 1
                    break
               
            elif (row == 5):
                if (self.turn == 1):
                    self.node[row][col] = self.players[0]
                    self.turn = -1
                else:
                    self.node[row][col] = self.players[1]
                    self.turn = 1                                                    

    def unplay(self, col):# //WORKING
        for row in range(6):
            if (self.node[row][col] != '.'):
                self.node[row][col] = '.'
                break                           
        if (self.turn == 1):           
            self.turn = -1
        else:
            self.turn = 1                    

    def horizontal_term(self):# -> int       
        score = 0
        for row in range(6):
            for col in range(4):
                if (self.node[row][col] == self.node[row][col + 1] and 
                    self.node[row][col + 1] == self.node[row][col + 2] and 
                    self.node[row][col + 2] == self.node[row][col + 3]):
                    
                    if(self.node[row][col] == self.players[0]):
                        score += 1                        
                    elif (self.node[row][col] == self.players[1]):
                        score -= 1
                                                                        
        return score     

    def vertical_term(self):# -> int                    
        score = 0
        for row in range(3):
            for col in range(7):
                if (self.node[row][col] == self.node[row + 1][col] and
                    self.node[row + 1][col] == self.node[row + 2][col] and
                    self.node[row + 2][col] == self.node[row + 3][col]):
                    
                    if(self.node[row][col] == self.players[0]):
                        score += 1                        
                    elif (self.node[row][col] == self.players[1]):
                        score -= 1
                                                                        
        return score
        

    def diagup_term(self):# -> int
        score = 0
        for row in range(3,6):
            for col in range(4):
                if (self.node[row][col] == self.node[row - 1][col + 1] and self.node[row - 1][col + 1] == self.node[row - 2][col + 2] and self.node[row - 2][col + 2] == self.node[row - 3][col + 3]):
             
                    if (self.node[row][col] == self.players[0]):
                        score += 1                        
                    elif (self.node[row][col] == self.players[1]):
                        score -= 1
                                                                       
        return score
        

    def diagdown_term(self):# -> int
        score = 0
        for row in range(3):
            for col in range(4):
                if (self.node[row][col] == self.node[row + 1][col + 1] and
                    self.node[row + 1][col + 1] == self.node[row + 2][col + 2] and
                    self.node[row + 2][col + 2] == self.node[row + 3][col + 3]):
                    
                    if (self.node[row][col] == self.players[0]):
                        score += 1
                    elif (self.node[row][col] == self.players[1]):
                        score -= 1
                                                                                            
        return score        

    def evaluate(self):# -> int
        self.nodes += 1
        v = self.vertical_term()
        h = self.horizontal_term()
        u = self.diagup_term()
        d = self.diagdown_term()

        return v + h + u + d
        
    def record_hash(self, key: int, depth: float, a: int, hashDataType: int) -> None:
        if key%self.ttsize in self.hashtable:
            entry = self.hashtable[key%self.ttsize]
            if entry['depth'] >= depth:
                self.hashtable[key%self.ttsize] = {
                    'key': key, 'depth': depth, 'score': a, 'type': hashDataType}
        else:
            self.hashtable[key%self.ttsize] = {
                'key': key, 'depth': depth, 'score': a, 'type': hashDataType}
        
    def probe_hash(self, key: int, depth: float = 0, a: int = -2, b: int = 2) -> tuple:
        if key%self.ttsize in self.hashtable:
            entry = self.hashtable[key%self.ttsize]
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
                return (None, False)
            return (None, False)
        return (None, None)

    def negamax(self, depth = 10, colour = 1, a = -2, b = 2):# -> int //WORKING
        if depth < 1: return colour * self.evaluate()
        
        if self.is_game_over(): return colour * self.evaluate()
        
        hashDataType = 1
        key = self.__hash__()
        probe = self.probe_hash(key, depth, a, b)
        if probe[0] != None:
            if probe[1]:
                return probe[0]
            
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
        self.record_hash(key, depth, a, hashDataType)
        return a

    def engine_move(self):# //WORKING            
        self.nodes = 0
        bestcase = -2
        d = 0
        sstart = time()
        while time() - sstart < self.timelimit:
            bestcase = -2
            start = time()
            for i, move in enumerate(self.legal_moves()):
                if i == 0: bestmove = move
                self.play(move) 
                score = -self.negamax(d, self.turn)
                print(score, end=" ")
                self.unplay(move)
                if bestcase < score:
                    bestcase = score
                    bestmove = move
            print(f"best current column: {bestmove}, score for move: {bestcase}, in {(time()-start):.2f}s at depth {d}, {self.nodes} nodes processed.")
            d += 1
        self.play(bestmove)
        
    def show_result(self):# //WORKING            
        r = self.evaluate();
        if (r == 0):            
            print("1/2-1/2")
        elif (r > 0):
            print("1-0")            
        else:            
            print("0-1")                    

    def is_game_over(self):# -> int       
        return (self.evaluate() != 0 or self.is_full() == True)                   

if __name__ == "__main__":
    coin = Coin(20)
    coin.show()
    while (coin.is_game_over() == False):
        coin.engine_move()
        coin.show()
        #if coin.is_game_over(): break
        #playermove = int(input("Enter column:\n--> "))-1
        #while playermove not in coin.legal_moves():
        #    playermove = int(input("Enter legal column:\n--> "))-1
        #coin.play(playermove)
        #coin.show()
    coin.show_result()
