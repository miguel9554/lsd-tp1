import numpy as np


# Cantidad de cuadripolos/resitencias/capacitores
N = 4 
# Hasta que momento queremos calcular
M = 3
# Resistencia y capacidad de cada elemento
R = 1
C = 1

state_vector_length = N+2
moments = np.zeros((state_vector_length, M+1))

# Los momentos de órden 1 son tensiones unitarias y corriente nula
moments[:state_vector_length-1, 0] = np.ones(state_vector_length-1

for order in range (1, M+1):
    # El último nodo es la corriente por la fuente de tensión, la suma con signo 
    # negativo de todas las corrientes de las fuentes de corriente
    moments[state_vector_length-1, order] = -np.sum(moments[1:N+1, order-1])*C
    for i in range(1, state_vector_length-1):   
        moments[i, order] = moments[i-1, order] - R*np.sum(moments[i:N+1, order-1])*C


print(moments)
