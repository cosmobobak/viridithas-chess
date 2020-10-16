
class Node:
    state = [[0 for i in range(9)] for i in range(9)]
    turn = -1
    captures = [0, 0]

    def play(x: int, y: int):
        state[x][y] = turn
        turn = -turn

    def unplay(x: int, y: int):
        state[x][y] = 0
        turn = -turn
    
    def eval() -> int:
        score = 0



        return score - captures[0] + captures[1]

