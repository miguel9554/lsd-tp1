import numpy as np


N = 4 # Cantidad de cuadripolos/resitencias/capacitores
R = 1
g = 1/R
c = 1

E = np.zeros(N+1)
E[0] = 1

G = np.zeros((N+2, N+2)) # Matriz de conductancias
for column in range(N+1):
    for row in range(N+1):
        if row == column:
            if row == 0 or row == N:
                G[row, column] = g
            else:
                G[row, column] = 2*g
        elif abs(row - column) == 1:
            G[row, column] = -g
        else:
            continue

C = np.zeros((N+2, N+2)) # Matriz de conductancias
for column in range(N+2):
    for row in range(N+2):
        if (row == column) and (row != 0):
            C[row, column] = c
        elif ((row == N+1) and (column > 0)) or ((column == N+1) and (row > 0)):
            C[row, column] = -c
        else:
            continue

print(np.linalg.inv(G))
print(C)
print(E.transpose())
