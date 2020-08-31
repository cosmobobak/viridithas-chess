import chess
import chess.svg
import chess.pgn
import random
import chess.variant
import time
#import gmpy
from operator import itemgetter

class MCTS():
    def __init__(self):
        self.node = chess.Board()
        self.wl = 0
        self.games = 0

    def rollout(self):
        if self.node.is_game_over():
            self.games += 1
            result = self.node.result()
            if result == '1/2-1/2':
                self.node.reset()
            if result == '1-0':
                self.wl += 1
                self.node.reset()
            else:
                self.wl -= 1
                self.node.reset()
            return 0
        else:
            moves = [move for move in self.node.legal_moves]
            self.node.push(random.choice(moves))
            self.rollout()
        
    def run(self):
        for i in range(10000):
            self.rollout()
            if i%100 == 0:
                print('progress:',i/100,'%')
        print('white winrate = ' + str(self.wl/self.games*100) + r'% out of ' + str(self.games) + ' games.')
    
print('running!')
start = time.time()
mcts = MCTS()
mcts.run()
print('finished in',time.time()-start)
