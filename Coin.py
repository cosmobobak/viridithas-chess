
class Coin:
    def __init__(self):
        self.node = [["." for j in range(7)] for i in range(6)]
        self.turn = 1
        self.nodes = 0
        self.players = ['X','O']
    
    def reset(self):
        self.node = [["." for j in range(7)] for i in range(6)]
    
    def fill(self):
        self.node = [["F" for j in range(7)] for i in range(6)]

    def is_full(self):
        for row in self.node:
            for x in row:
                if x == '.':
                    return False
        return True
    
    def show(self):
        for row in self.node:
            for x in row:
                print(x, end=' ')
            print()
        print()

    def play(self, col):
        for row in range(len(self.node)):
            if node[row][col] != '.':
                if turn == 1:
                    node[row - 1][col] = players[0]
                    turn = -1
                    break
                else:
                    node[row - 1][col] = players[1]
                    turn = 1
                    break
            elif row == 5:
                if turn == 1:
                    node[row][col] = players[0]
                    turn = -1
                else:
                    node[row][col] = players[1]
                    turn = 1
    
    def unplay(self, col):
        for row in range(len(self.node)):
            if node[row][col] != '.':
                node[row][col] = '.'
                break
        if turn == 1:
            turn = -1
        else:
            turn = 1
    
    def horizontal_term(self):
        
