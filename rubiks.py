import numpy as np

FACES = [TOP, BOTTOM, LEFT, RIGHT, BACK, FRONT] = range(0, 6)
COLOURS = [WHITE, YELLOW, RED, ORANGE, GREEN, BLUE] = range(0, 6)


class BaseCube():
    def __init__(self):
        cube = np.array([[[colour for i in range(3)] for j in range(3)]
                for colour in COLOURS])
        self.state = cube

    def __repr__(self):
        return "\n".join([str(face) for face in self.state])

    def __str__(self):
        return self.__repr__()


class Cube(BaseCube):
    def __init__(self):
        super().__init__()

    def __repr__(self):
        return super().__repr__()

    def __str__(self):
        return super().__str__()

    def is_solved(self) -> bool:
        for face in self.state:
            n = face[0][0]
            for row in face:
                for square in row:
                    if n != square:
                        return False
        else:
            return True

    def rot_face(self, face):
        np.rot90(self.state[face])

    def unrot_face(self, face):
        np.rot90(self.state[face], 3)

    def U(self):
        self.rot_face(TOP)
        self.state[FRONT][0], self.state[LEFT][0], self.state[BACK][0], self.state[RIGHT][0] = self.state[RIGHT][0], self.state[FRONT][0], self.state[LEFT][0], self.state[BACK][0]

    def Uprime(self):
        self.unrot_face(TOP)
        self.state[RIGHT][0], self.state[FRONT][0], self.state[LEFT][0], self.state[BACK][0] = self.state[FRONT][0], self.state[LEFT][0], self.state[BACK][0], self.state[RIGHT][0]

    def F(self):
        self.rot_face(FRONT)
        a, b, c, d = self.state[TOP][2], self.state[RIGHT][:, 0], self.state[BOTTOM][2], self.state[LEFT][:, 2]
        self.state[RIGHT][:, 0], self.state[BOTTOM][2], self.state[LEFT][:, 2], self.state[TOP][2] = a, b, c, d

    def Fprime(self):
        self.unrot_face(FRONT)
        a, b, c, d = self.state[RIGHT][:, 0], self.state[BOTTOM][2], self.state[LEFT][:, 2], self.state[TOP][2]
        self.state[TOP][2], self.state[RIGHT][:, 0], self.state[BOTTOM][2], self.state[LEFT][:, 2] = a, b, c, d

    def R(self):
        pass

    def Rprime(self):
        pass

    def L(self):
        pass

    def Lprime(self):
        pass

    def B(self):
        pass

    def Bprime(self):
        pass

    def Dprime(self):
        self.unrot_face(BOTTOM)
        self.state[FRONT][2], self.state[LEFT][2], self.state[BACK][2], self.state[RIGHT][2] = self.state[RIGHT][2], self.state[FRONT][2], self.state[LEFT][2], self.state[BACK][2]

    def D(self):
        self.rot_face(BOTTOM)
        self.state[RIGHT][2], self.state[FRONT][2], self.state[LEFT][2], self.state[BACK][2] = self.state[FRONT][2], self.state[LEFT][2], self.state[BACK][2], self.state[RIGHT][2]


if __name__ == "__main__":
    obj = Cube()
    print(obj.is_solved())
    #obj.U()
    #obj.F()
    obj.D()
    print(obj)
    obj.Dprime()
    #obj.Fprime()
    #obj.Uprime()
    print(obj)
    print(obj.is_solved())
