#from chess import Board, Move, popcount, BLACK, WHITE, BoardT, Union
from random import choice
from math import sqrt, log
from time import time
from copy import deepcopy, copy
from itertools import chain
from typing import Optional
from Glyph import State, Move
from chess import Board, popcount, BLACK, WHITE

EXP_FACTOR = 5



class State(Board):
    def __init__(self) -> None:
        super().__init__()

    def copy(self):
        out = State()
        out.pawns = self.pawns
        out.bishops = self.bishops
        out.knights = self.knights
        out.rooks = self.rooks
        out.queens = self.queens
        out.pawns = self.pawns
        out.occupied_co = self.occupied_co
        out.occupied = self.occupied
        out.castling_rights = self.castling_rights
        out.turn = self.turn
        out.ep_square = self.ep_square
        out.fullmove_number = self.fullmove_number
        out.halfmove_clock = self.halfmove_clock
        out.promoted = self.promoted
        out.move_stack = self.move_stack
        return out

    def see_factor(self) -> int:
        rating = popcount(self.occupied_co[BLACK] & self.pawns) * 1000
        rating -= popcount(self.occupied_co[WHITE] & self.pawns) * 1000
        rating += popcount(self.occupied_co[BLACK] & self.knights) * 3200
        rating -= popcount(self.occupied_co[WHITE] & self.knights) * 3200
        rating += popcount(self.occupied_co[BLACK] & self.bishops) * 3330
        rating -= popcount(self.occupied_co[WHITE] & self.bishops) * 3330
        rating += popcount(self.occupied_co[BLACK] & self.rooks) * 5100
        rating -= popcount(self.occupied_co[WHITE] & self.rooks) * 5100
        rating += popcount(self.occupied_co[BLACK] & self.queens) * 8800
        rating -= popcount(self.occupied_co[WHITE] & self.queens) * 8800
        return rating

    def evaluate(self) -> int:
        rating: int = 0
        if self.is_checkmate():
            return 1000000000 * (1 if self.turn else -1)

        rating += self.see_factor()

        return rating

    def captures_piece(self, p):  # concentrate on MVV, then LVA
        return chain(
            self.generate_pseudo_legal_moves(self.pawns, p),
            self.generate_pseudo_legal_moves(self.knights, p),
            self.generate_pseudo_legal_moves(self.bishops, p),
            self.generate_pseudo_legal_moves(self.rooks, p),
            self.generate_pseudo_legal_moves(self.queens, p),
            self.generate_pseudo_legal_moves(self.kings, p),
        )

    def legal_moves(self):
        return [m for m in chain(
            self.captures_piece(self.occupied_co[not self.turn] & self.queens),
            self.captures_piece(self.occupied_co[not self.turn] & self.rooks),
            self.captures_piece(self.occupied_co[not self.turn] & self.bishops),
            self.captures_piece(self.occupied_co[not self.turn] & self.knights),
            self.captures_piece(self.occupied_co[not self.turn] & self.pawns),
            self.generate_pseudo_legal_moves(0xffff_ffff_ffff_ffff, ~self.occupied_co[not self.turn])
        ) if self.is_legal(m)]

    def random_play(self):
        self.push(choice(self.legal_moves()))

class TreeNode:
    def __init__(self, board: State = State()) -> None:
        self.winScore: int = 0
        self.visits: int = 0
        self.playerNo: int = 1
        self.board: State = State()
        self.parent: Optional[TreeNode] = None
        self.children: "list[TreeNode]" = []
        self.board = board

    def set_player_no(self, playerNo: int):
        self.playerNo = playerNo

    def get_player_no(self) -> int:
        return self.playerNo

    def get_opponent(self) -> int:
        return -self.playerNo

    def set_parent(self, parent):
        self.parent = parent

    def set_state(self, board):
        self.board = board

    # def show(self)
    #     print( "My state is:\n"
    #     board.show()
    #     if (parent)
    #     {
    #         print( "My parent's state is:\n"
    #         parent->show()
    #     }
    #     print( "and I have " << children.size() << " children.\n"

    def get_children(self) -> list:
        return self.children

    def get_children_as_states(self) -> list:
        childStates = []
        for move in self.board.legal_moves():
            self.board.push(move)
            childStates.append(self.board.copy())
            self.board.pop()
        return childStates

    def get_win_score(self) -> int:
        return self.winScore

    def get_visit_count(self) -> int:
        return self.visits

    def get_parent_visits(self) -> int:
        return self.parent.get_visit_count()

    def increment_visits(self):
        self.visits += 1

    def add_score(self, s: int):
        self.winScore += s

    def set_win_score(self, s: int):
        self.winScore = s

    def get_parent(self):
        return self.parent

    def get_state(self) -> State:
        return self.board

    def random_child(self):
        return choice(self.children)

    def get_winrate(self) -> float:
        return self.winScore / self.visits

    def best_child(self):
        return max(self.children, key=lambda a: a.get_visit_count())

    def best_child_as_move(self) -> Move:
        return self.board.legal_moves()[self.children.index(self.best_child())]

    def show_child_winrates(self):
        for child in self.children:
            print(f"{child.get_win_score()} ", end="")
        print()

    def show_child_visitrates(self):
        for child in self.children:
            print(f"{child.get_visit_count()} ", end="")
        print()

####################################################################################################
def uct_value(totalVisit: int, nodeWinScore: float, nodeVisit: int) -> float:
        if (nodeVisit == 0):
            return 100000000
        return (nodeWinScore / nodeVisit) + 1.41 * sqrt(log(totalVisit) / nodeVisit) * EXP_FACTOR

def uct_key(a: TreeNode) -> float:
    return uct_value(
            a.get_parent_visits(),
            a.get_win_score(),
            a.get_visit_count())

def best_node_uct(node: TreeNode) -> TreeNode:
    return max(node.get_children(), key=lambda x: uct_key(x))
####################################################################################################

class MCTS:
    WIN_SCORE = 10
    def __init__(self, timeLimit = 99, player = 1) -> None:
        self.timeLimit: int = timeLimit # limiter on search time
        self.opponent: int = -player # the win score that the opponent wants
        self.reward: int = player # the win score that the agent wants
        self.nodes: int = 0

    # def deleteTree(self, TreeNode *root):
    # {
    #     /* first delete the subtrees */
    #     for (TreeNode *child : root->children)
    #     {
    #         deleteTree(child)
    #     }
    #     /* then delete the node */
    #     delete root
    # }

    def set_opponent(self, i: int):
        self.opponent = i
        self.reward = -i

    def find_best_next_board(self, board: State) -> State:
        self.nodes = 0
        self.set_opponent(-board.turn)
        # define an end time which will act as a terminating condition
        end = time()
        end += self.timeLimit / 1000
        rootNode = TreeNode(board)
        rootNode.set_state(board)
        rootNode.set_player_no(self.opponent)

        while (time() < end):
            promisingNode: TreeNode = TreeNode(
                self.select_promising_node(rootNode).board.copy())

            if (not promisingNode.get_state().is_game_over()):
                self.expand_node(promisingNode)

            nodeToExplore: TreeNode = TreeNode(promisingNode.board.copy())
            if any(promisingNode.get_children()):
                nodeToExplore = TreeNode(
                    promisingNode.random_child().board.copy())
            playoutResult: int = self.simulate_playout(nodeToExplore)
            self.backpropagate(nodeToExplore, playoutResult)
        out: State = rootNode.best_child().get_state()
        print( "ZERO:\n")
        print(self.nodes, " nodes processed.\n")
        print( "Zero win prediction: ", int((rootNode.best_child().get_winrate() * (100 / self.WIN_SCORE))), "%\n")
        rootNode.show_child_visitrates()
        print( '\n')
        return out

    def select_promising_node(self, rootNode: TreeNode) -> TreeNode:
        node: TreeNode = rootNode
        while any(node.get_children()):
            node = best_node_uct(node)
        return node

    def expand_node(self, node: TreeNode):
        possibleStates: list = node.get_children_as_states()
        for state in possibleStates:
            newNode: TreeNode = TreeNode(state)
            newNode.set_parent(node)
            newNode.set_player_no(node.get_opponent())
            node.children.append(newNode)

    def backpropagate(self, nodeToExplore: TreeNode, winner: int):
        tempNode: Optional[TreeNode] = nodeToExplore
        while tempNode:
            tempNode.increment_visits()
            if (tempNode.get_player_no() == winner):
                tempNode.add_score(self.WIN_SCORE)
            tempNode = tempNode.get_parent()

    def simulate_playout(self, node: TreeNode) -> int:
        self.nodes += 1
        tempState: State = node.get_state().copy()
        boardStatus: int = tempState.evaluate()
        if (boardStatus == self.opponent):
            node.get_parent().set_win_score(-1000000)
            return boardStatus
        while (not tempState.is_game_over()):
            tempState.random_play()
        boardStatus = tempState.evaluate()
        return boardStatus

if __name__ == "__main__":
    agent = MCTS(3000)
    game = State()
    print(game)
    while not game.is_game_over():
        game = agent.find_best_next_board(game)
        print(game)
