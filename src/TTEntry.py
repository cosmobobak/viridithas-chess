from dataclasses import dataclass

from chess import Move

@dataclass
class TTEntry():
    best: Move = Move.null()
    depth: float = 0
    value: float = 0
    type: int = 0
    null: bool = True

    @classmethod
    def default(cls):
        return TTEntry()

    def is_null(self) -> bool:
        return self.null == True

[EXACT, LOWERBOUND, UPPERBOUND] = range(3)
