import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from chess import Board, Move, BoardT, WHITE, BLACK
from Viridithas import Viridithas
from DeepLearning import vectorise_board
import tensorflow as tf

class ViridithasNN(Viridithas):
    def __init__(self, human: bool = False, fen: str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', pgn: str = '', timeLimit: int = 15, fun: bool = False, contempt: int = 3000, book: bool = True, advancedTC: list = []):
        super().__init__(human=human, fen=fen, pgn=pgn, timeLimit=timeLimit, fun=fun, contempt=contempt, book=book, advancedTC=advancedTC)
        self.model = tf.keras.models.load_model('evalmodel')
    
    def evaluate(self, depth: float = 1.0) -> float:
        self.nodes += 1
        return self.see_factor()+20 * float(self.model.predict([vectorise_board(self.node)]))

if __name__ == "__main__":
    engine = ViridithasNN()
    engine.user_setup()
    engine.run_game()
