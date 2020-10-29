

def seepos_factor(dict evaltable, ):
    int rating = 0
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