import numpy as np

class RC_line:
    def __init__(self, R: int, C: int, sections: int):
        self.R = R
        self.C = C
        self.sections = sections

    def get_moments(self, max_moment: int):
        state_vector_length = self.sections + 2
        moments = np.zeros((state_vector_length, max_moment+1))

        # Los momentos de órden 1 son tensiones unitarias y corriente nula
        moments[:state_vector_length-1, 0] = np.ones(state_vector_length-1)

        for order in range (1, max_moment+1):
            # El último nodo es la corriente por la fuente de tensión, la suma con signo 
            # negativo de todas las corrientes de las fuentes de corriente
            moments[state_vector_length-1, order] = -np.sum(moments[1:state_vector_length-1, order-1])*self.C
            for i in range(1, state_vector_length-1):   
                # La corriente es la suma de todas las fuentes de corriente a la derecha del resistor
                # Cada fuente de corriente vale C*m_i-1(V), es decir, la tensión del momento anterior
                # multiplicada por la capacidad.
                I = np.sum(moments[i:state_vector_length-1, order-1])*self.C
                # La tensión del nodo (el momento) será la suma del nodo ya calculado y la tensión
                # que cae en el resistor (I*R)
                moments[i, order] = moments[i-1, order] - self.R*I

        return moments

if __name__ == "__main__":
    # Cantidad de cuadripolos/resitencias/capacitores
    N = 4 
    # Hasta que momento queremos calcular
    M = 3
    # Resistencia y capacidad de cada elemento
    R = 1
    C = 1

    RC = RC_line(R, C, N)
    print(RC.get_moments(M))

