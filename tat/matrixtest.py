import numpy as np
import random as r

a = np.array([[8, 4],
              [4, 0]])

b = np.array([[36, 16],
              [8, 4]])

e1 = np.array([[1, 0],
               [0, 1]])

e2 = np.array([[1, 0],
               [0, 1]])

out = np.matmul(e2, np.matmul(e1, a))
while out[0][0] != b[0][0] or out[0][1] != b[0][1] or out[1][0] != b[1][0] or out[1][1] != b[1][1]:
    e1[r.randint(0, 1)][r.randint(0, 1)] = r.randint(-1, 2)
    e2[r.randint(0, 1)][r.randint(0, 1)] = r.randint(-1, 2)
    out = np.matmul(e2, np.matmul(e1, a))

print(e1, '\n', e2)
print(np.matmul(e2, np.matmul(e1, a)))
