
class SubBoard():
    def __init__(self):
        self.state = [0b000000000, 0b000000000]

    def pos_filled(self, i):
        if ((self.state[0] & (1 << i)) != 0):
            return True
        elif ((self.state[1] & (1 << i)) != 0):
            return True
        return False

    def player_at(self, i): # only valid to use if self.pos_filled() returns True:
        if ((self.state[0] & (1 << i)) != 0):
            return True 
        else:
            return False

    def is_full(self):
        return all(map(self.pos_filled, range(9)))

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

class UUTboard():
    def __init__(self):
        self.boards = [SubBoard() for i in range(9)]

    def __repr__(self) -> str:
        return super().__repr__()
