import numpy as np


# Cantidad de cuadripolos/resitencias/capacitores
N = 4 
# Hasta que momento queremos calcular
M = 3
# Resistencia y capacidad de cada elemento
R = 1
C = 1

state_vector_length = N+2

# m0 es un vector de unos salvo un cero en la última posición
m0 = np.ones(state_vector_length)
m0[len(m0)-1] = 0

# m1 es más turbio
m1 = np.zeros(state_vector_length)
m1[0] = 0
m1[1] = -N*R
m1[len(m1)-1] = -N
for i in range(2, len(m1)-1):
    m1[i] = m1[i-1] - (N+1-i)*R

# m2, otro hijo de puta
m2 = np.zeros(state_vector_length)
# El nodo 0 está a tierra
m2[0] = 0
# El último nodo es la corriente por la fuente de tensión, la suma con signo 
# negativo de todas las corrientes de las fuentes de corriente
m2[len(m2)-1] = -np.sum(m1[1:N+1])
for i in range(1, len(m2)-1):   
    m2[i] = m2[i-1] - np.sum(m1[i:N+1])*R

print(m0)
print(m1)
print(m2)
