import numpy as np
from moments import RC_line


class RC_tree:
    def __init__(self, line1: RC_line, line2: RC_line, line3: RC_line):
        self.line1 = line1
        self.line2 = line2
        self.line3 = line3
        self.Vdd = line1.Vdd


    def write_conductance(self, G: np.array, g: float, a: int, b: int) -> np.array:
        """writes a conductance connected between a and b """
        G[a, a] += g
        G[b, b] += g
        G[b, a] -= g
        G[a, b] -= g

        return G


    def write_capacitance(self, C: np.array, c: float, a: int) -> np.array:
        """ Writes a conductance connected between node a and ground """
        C[a, a] = c

        return C


    def get_moments(self, max_moment: int) -> np.array:
        """ 
        Devuelve una matriz con los momentos de la línea cargada con CL

        La columna j representa el momento j
        Cada fila corresponde a una variable. En concreto, la fila i
        representa la tensión del nodo i+1, siguiendo la numeración usada
        en la figura 3.3 de la página 36 del timing, salvo la última fila,
        que repreenta la corriente por la fuente de tensión.
        A esta se le cambio el signo con respecto al ejemplo de la página 47.
        """

        # El vector de estados consiste de las N1+N2+N3+1 tensiones de nodos
        # (Ni es la cantidad de cuadripolos de la línea i), y en la última
        # posición la corriente de la fuente
        state_vector_length = self.line1.sections + self.line2.sections + \
                self.line3.sections + 2

        # Construimos el vector de excitaciones
        # Es igual al de estados, salvo que la última posición es la tensión
        # de la fuente, y no la corriente
        # Este vector representa una única excitación consistenten de una
        # delta temporal de tensión en la fuente
        E = np.zeros(state_vector_length)
        E[state_vector_length-1] = 1

        # Construimos la matriz de conductancias
        G = np.zeros((state_vector_length, state_vector_length))
        # Las entradas correspondientes a la fuente de tensión
        G[G.shape[0]-1, 0] = 1
        G[0, G.shape[1]-1] = 1

        # Agregamos las conductancias de la primer línea
        g1 = 1/(self.line1.R*self.line1.sections)

        for node in range(self.line1.sections):
            G = self.write_conductance(G, g1, node, node+1)

        # Agregamos las conductancias de la segunda línea
        g2 = 1/(self.line2.R*self.line2.sections)
        for node in range(self.line2.sections):
            node += self.line1.sections
            G = self.write_conductance(G, g2, node, node+1)

        # Agregamos las conductancias de la tercer línea
        g3 = 1/(self.line3.R*self.line3.sections)
        # La conductancia que va entre el primer nodo y el último de la 
        # primer línea
        G = self.write_conductance(G, g3, self.line1.sections,\
                self.line1.sections+self.line2.sections+1)
        for node in range(1, self.line3.sections):
            node += self.line1.sections + self.line2.sections
            G = self.write_conductance(G, g3, node, node+1)

        # Construimos la matriz de capacidades
        C = np.zeros((state_vector_length, state_vector_length))
        # Agregamos las capacidades de la primer línea
        c1 = self.line1.C/self.line1.sections
        for node in range(self.line1.sections):
            C = self.write_capacitance(C, c1, node+1)

        # Escribimos las capacidades de la segunda línea
        c2 = self.line2.C/self.line2.sections
        for node in range(self.line2.sections):
            node += self.line1.sections+1
            C = self.write_capacitance(C, c2, node)
        # La última tiene en paralelo la capacidad de carga
        C = self.write_capacitance(C, c2+self.line2.CL, self.line1.sections \
                + self.line2.sections)

        # Escribimos las capacidades de la línea 3
        c3 = self.line3.C/self.line3.sections
        for node in range(self.line3.sections):
            node += self.line1.sections + self.line2.sections + 1
            C = self.write_capacitance(C, c3, node)

        # La última tiene en paralelo la capacidad de carga
        C = self.write_capacitance(C, c3+self.line3.CL, self.line3.sections \
                + self.line2.sections + self.line1.sections)

        # Inicializamos la matriz de momentos en cero
        moments = np.zeros((state_vector_length, max_moment+1))

        invG = np.linalg.inv(G)
        moments[:,0] = invG.dot(E)
        for moment_order in range(1, max_moment+1):
            moments[:, moment_order] = invG.dot(-C.dot(moments[:, moment_order-1]))
        
        moments[moments.shape[0]-1, :] *= -1
        return moments


    def get_pi_model(self):
        """ Devuelve el modelo pi, se sigue la nomenclatura de la página 79 """
        line_moments = self.get_moments(3)
        current_moments = line_moments[line_moments.shape[0]-1, :]
        C1 = current_moments[2]**2/current_moments[3]
        C2 = current_moments[1] - current_moments[2]**2/current_moments[3]
        R = -(current_moments[3]**2)/(current_moments[2]**3)

        return C1, C2, R


    def get_pade12(self):
        # para flanco ascendete
        """ --> Obtiene la aproximacion de Pade [1/2] de la respuesta en frecuencia
        de la linea a partir los momentos m0, m1, m2 y m3
        --> La transferencia a hallar es:
        H(s) = (a0 + a1*s)/(1 + b1*s b1*s^2)}
        --> Devuelve el cero, los dos polos y la constante multiplicativa (A)
        de la siguiente expresion:
        H(s) = A*(s + z)/((s + p1)*(s + p2)) """
        
        # Obtener los momentos de la tension en el ultimo nodo de la linea,
        # que seria la entrada del siguiente inversor/flip-flop
        #print(self.get_moments(3))
        [m0,m1,m2,m3] = self.get_moments(3)[-2]
        #print("Momentos:")
        #print([m0,m1,m2,m3])
        # Obtener los coeficientes de la transferencia
        b2 = (-m2**2 + m1*m3)/(m0*m2 - m1**2)
        b1 = (m1*m2 - m0*m3)/(m0*m2 - m1**2)
        a0 = m0
        a1 = m1 + m0*b1
        
        #print("Constantes transferencia:")
        #print([a0, a1, b1, b2])
        
        # Obtener polos, cero y constante multiplicativa
        z = a0/a1
        A = a1/b2
        p1 = -(-(b1/b2) + ((b1/b2)**2 - 4/b2)**0.5)/2
        p2 = -(-(b1/b2) - ((b1/b2)**2 - 4/b2)**0.5)/2
        
        return [A, z, p1, p2]
        
def main():
    # Cantidad de cuadripolos/resitencias/capacitores
    N1 = 20
    N2 = 20
    N3 = 20
    R1 = 1/N1
    R2 = 1/N2
    R3 = 1/N3
    C1 = N1
    C2 = N2
    C3 = N3
    # Capacidad de carga
    CL = 0

    tree = RC_tree(RC_line(R1, C1, N1, CL),\
            RC_line(R2, C2, N2, CL), RC_line(R3, C3, N3, CL))
    print(tree.get_pi_model())

if __name__ == "__main__":
    main()
