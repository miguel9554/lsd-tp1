import numpy as np


N = 4 # Cantidad de cuadripolos/resitencias/capacitores
R = 1
g = 1/R
c = 1
CL = 1

# Vector de excitaciones, una delta en la fuente de tensión
E = np.zeros(N+2)
E[len(E)-1] = 1

G = np.zeros((N+2, N+2)) # Matriz de conductancias
for column in range(G.shape[0]-1):
    for row in range(G.shape[0]-1):
        if row == column:
            if row == 0 or row == G.shape[0]-2:
                G[row, column] = g
            else:
                G[row, column] = 2*g
        elif abs(row - column) == 1:
            G[row, column] = -g
        else:
            continue
G[G.shape[0]-1, 0] = 1
G[0, G.shape[1]-1] = 1

C = np.zeros((N+2, N+2)) # Matriz de conductancias
for column in range(C.shape[0]-1):
    for row in range(C.shape[0]-1):
        if (row == column) and (row != 0):
            C[row, column] = c+CL if row == C.shape[0]-2 else c
        else:
            continue
print(G)
print(E)
invG = np.linalg.inv(G)
m0 = invG.dot(E)
m1 = invG.dot(-C.dot(m0))
m2 = invG.dot(-C.dot(m1))
m3 = invG.dot(-C.dot(m2))
print(m0)
print(m1)
print(m2)
print(m3)
