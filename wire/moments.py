import numpy as np
from math import e as euler


class RC_line:
    def __init__(self, R: int, C: int, sections: int, CL: float=0):
        self.R = R
        self.C = C
        self.CL = CL
        self.sections = sections

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
        # Construimos el vector de capacidades, representa la capacidad conectada
        # a cada nodo. C para todos los nodos, salvo el último que tiene CL en paralelo
        capacitances = np.ones(self.sections)*self.C
        capacitances[self.sections-1] = C + CL

        # Vector de resistencias, representa la resistencia entre los nodos i-1 e i
        # Vale R para todos los nodos
        resistances = np.ones(self.sections)*self.R

        # Inicializamos la matriz de momentos en cero
        state_vector_length = self.sections + 2
        moments = np.zeros((state_vector_length, max_moment+1))

        # Los momentos de órden 0 son tensiones unitarias y corriente nula
        moments[:state_vector_length-1, 0] = np.ones(state_vector_length-1)

        for order in range (1, max_moment+1):
            # La última variable del vector de momentos es la corriente que circula por la fuente de tensión
            # Esta corriente es la suma (con signo cambiado) de todas las corrientes de las fuentes de corriente
            # Cada una de estas fuentes de corriente tiene como valor la tensión del nodo en la iteración anterior
            # multiplicada por la capacidad del nodo. Es decir, el producto escalar entre el vector de tensiones 
            # y el vector de capacidades
            last_iteration_node_voltages = moments[1:state_vector_length-1, order-1]
            voltage_source_current = np.dot(last_iteration_node_voltages, capacitances)
            moments[state_vector_length-1, order] = voltage_source_current
            # Ahora, computamos la tensión de cada nodo
            for i in range(1, state_vector_length-1):
                # La tensión del nodo será la tensión del nodo anterior MAS la tensión que cae sobre el resistor
                # que une los nodos
                # La corriente es la suma de todas las fuentes de corriente a la derecha del resistor
                # Cada fuente de corriente vale C*m_i-1(V), es decir, la tensión del momento anterior
                # multiplicada por la capacidad.
                I = np.dot(last_iteration_node_voltages[i-1:], capacitances[i-1:])
                # La tensión del nodo (el momento) será la suma del nodo ya calculado y la tensión
                # que cae en el resistor (I*R)
                moments[i, order] = moments[i-1, order] - resistances[i-1]*I

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
        
    def get_pade22(self):
        """ --> Obtiene la aproximacion de Pade [2/2] de la respuesta en frecuencia
        de la linea a partir los momentos m0, m1, m2 y m3
        --> La transferencia a hallar es:
        H(s) = (a0 + a1*s + a2*s^2)/(1 + b1*s b1*s^2)}
        --> Devuelve el cero, los dos polos y la constante multiplicativa (A)
        de la siguiente expresion:
        H(s) = A*(s + z1)*(s + z3)/((s + p1)*(s + p2)) """
        
        # Obtener los momentos de la tension en el ultimo nodo de la linea,
        # que seria la entrada del siguiente inversor/flip-flop
        print(self.get_moments(3))
        [m0,m1,m2,m3] = self.get_moments(3)[-2]
        print("Momentos:")
        print([m0,m1,m2,m3])
        # Obtener los coeficientes de la transferencia
        b2 = -m3**2/(m1*m3 - m2**2)
        b1 = m2*m3/(m1*m3 - m2**2)
        a0 = m0
        a1 = m1 + m0*b1
        a2 = m0*b2 + m1*b1
        
        print("Constantes transferencia:")
        print([a0, a1, a2, b1, b2])
        
        # Obtener polos, cero y constante multiplicativa
        A = a2/b2
        z1 = -(-(a1/a2) + ((a1/a2)**2 - 4*(a0/a2))**0.5)/2
        z2 = -(-(a1/a2) - ((a1/a2)**2 - 4*(a0/a2))**0.5)/2
        p1 = -(-(b1/b2) + ((b1/b2)**2 - 4/b2)**0.5)/2
        p2 = -(-(b1/b2) - ((b1/b2)**2 - 4/b2)**0.5)/2

        #print(A*z1*z2/(p1*p2))        
        return [A, z1, z2, p1, p2]


    
    def temp_resp_LH_exp_input_RC_output(self, t, tau_in, R, C, Vdd):
        """ Calcular la respuesta temporal a la salida de la linea para:
        # --> Entrada de forma exponencial con constante de tiempo tau_in
        # --> Linea representada por un equivalente RC obtenido mediante los parametros
        # R y C2 del equivalente pi
        # --> Flanco ascendente
        # Recibe: R = resistencia equivalente de la linea
        #         C = capacidad equivalente de la linea"""
        
        p1 = 1/tau_in # Polo de la dseñal de entrada
        p2 = 1/(R*C)# Polo de la linea

        A = p2/(p2-p1)
        B = p2/(p1-p2)
        return Vdd*(A*(1 - euler**(-p1*t)) + (p1/p2)*B*(1 - euler**(-p2*t)))

    def temp_resp_HL_exp_input_RC_output(self, t, tau_in, R, C, Vdd):
        """Calcular la respuesta temporal a la salida de la linea para:
        --> Entrada de forma exponencial con constante de tiempo tau_in
        --> Linea representada por un equivalente RC obtenido mediante los parametros
        R y C2 del equivalente pi
        --> Flanco descendente
        Recibe: R = resistencia equivalente de la linea
        C = capacidad equivalente de la linea """
        
        p1 = 1/tau_in # Polo de la dseñal de entrada
        p2 = 1/(R*C)# Polo de la linea

        A = p2/(p2-p1)
        B = p2/(p1-p2)
        return Vdd*(A*euler**(-p1*t) + B*euler**(-p2*t))

    def temp_resp_LH_exp_input_2order_output(self, t, tau_in, line_transf, Vdd):
        """ Calcular la respuesta temporal a la salida de la linea para:
        --> Entrada de forma exponencial con constante de tiempo tau_in
        --> Tension de salida de la linea representada por la siguiente transferencia:
        H(s) = D*(s + z)/((s + p2)*(s + p3)) 
        --> Flanco ascendente
        Recibe: line_transf = [A,z,p1,p2]"""
    
        p1 = 1/tau_in # Polo de la dseñal de entrada
        [D, z, p2, p3] = line_transf
        
        aux_matrix = np.array([ [1,1,1], [p2+p3 , p1+p3, p1+p2], [p2*p3, p1*p3, p1*p2] ])
        aux_matrix = np.linalg.inv(aux_matrix)
        aux_vect = np.array([0,1,z])
        [A, B, C] = np.dot(aux_matrix,aux_vect)
        return Vdd*D*p1*((A/p1)*(1 - euler**(-p1*t)) + (B/p2)*(1 - euler**(-p2*t)) + (C/p3)*(1 - euler**(-p3*t)))

    def temp_resp_HL_exp_input_2order_output(self, t, tau_in, line_transf, Vdd):
        """ Calcular la respuesta temporal a la salida de la linea para:
        --> Entrada de forma exponencial con constante de tiempo tau_in
        --> Tension de salida de la linea representada por la siguiente transferencia:
        H(s) = D*(s + z)/((s + p2)*(s + p3)) 
        --> Flanco descendente
        Recibe: line_transf = [A,z,p1,p2] """
    
        p1 = 1/tau_in # Polo de la dseñal de entrada
        [D, z, p2, p3] = line_transf

        aux_matrix = np.array([ [1,1,1], [p2+p3 , p1+p3, p1+p2], [p2*p3, p1*p3, p1*p2] ])
        aux_matrix = np.linalg.inv(aux_matrix)
        aux_vect = np.array([0,1,z])
        [A, B, C] = np.dot(aux_matrix,aux_vect)
        
        return Vdd*D*(A*euler**(-p1*t) + B*euler**(-p2*t) + C*euler**(-p3*t))

    def temp_resp_HL_exp_input_2order_output_initial_conditions(self, t, tau_in, line_transf, Vdd):
        p1 = 1/tau_in # Polo de la dseñal de entrada
        [D, z1, z2, p2, p3] = line_transf
        
        B = (z1*p3 + z1*p2 + p2*z2 - p3*z1 - z1*z2 - p2*p3)/(p2 - p3)
        C = (z1*z2 - z1*p3 - z2*p3 + p3**2)/(p2 - p3)
        
        A1 = 1/(p2 - p1)
        A2 = 1/(p1 - p2)
        
        B1 = 1/(p2 - p1)
        B2 = 1/(p1 - p2)
        
        C1 = 1/(p3 - p1)
        C2 = 1/(p1 - p3)
       
        #print([p1, p2, p3])
        #return Vdd*( ((-A2*p2) + B*B2)*euler**(-p2*t) + (C*C2)*euler**(-p3*t))
        return Vdd*D*(((-A1*p1) + B*B1 + C*C1)*euler**(-p1*t) + ((-A2*p2) + B*B2)*euler**(-p2*t) + (C*C2)*euler**(-p3*t))
        
    def temp_resp_HL_ramp_input_RC_output(self, t, delta_t, R, C, Vdd):
        """ Calcular la respuesta temporal a la salida de la linea para:
         --> Entrada con forma de rampa con slew delta_t
         --> Linea representada por un equivalente RC obtenido mediante los parametros
         R y C2 del equivalente pi
         --> Flanco ascendente
         Recibe: R = resistencia equivalente de la linea
                 C = capacidad equivalente de la linea """
    
        p = 1/(R*C) # Polo de la linea
        
        if (t < delta_t):
            return (Vdd/delta_t)*(delta_t*(1 - euler**(-p*t)) - t - euler**(-p*t) + 1/p)
        else:
            return (Vdd/delta_t)*(delta_t*(1 - euler**(-p*t)) - t - euler**(-p*t) + 1/p) + \
                    (Vdd/delta_t)*(t - delta_t + euler**(-p*(t - delta_t))/p - 1/p)

    def temp_resp_LH_ramp_input_RC_output(self, t, delta_t, R, C, Vdd):
        """ Calcular la respuesta temporal a la salida de la linea para:
        --> Entrada con forma de rampa con slew delta_t
        --> Linea representada por un equivalente RC obtenido mediante los parametros
        R y C2 del equivalente pi
        --> Flanco descendente
        Recibe: R = resistencia equivalente de la linea
                C = capacidad equivalente de la linea """
    
        p = 1/(R*C) # Polo de la linea

        if (t < delta_t):
            return (Vdd/delta_t)*(t + euler**(-p*t)/p - 1/p)
        else:
            return (Vdd/delta_t)*(t + euler**(-p*t)/p - 1/p) - \
                    (Vdd/delta_t)*(t - delta_t + euler**(-p*(t - delta_t))/p - 1/p)    
        
    def temp_resp_HL_ramp_input_2order_output(self, t, delta_t, line_transf, Vdd):
        """ Calcular la respuesta temporal a la salida de la linea para:
        --> Entrada de forma de rampa con slew delta_t
        --> Tension de salida de la linea representada por la siguiente transferencia:
        H(s) = C*(s + z)/((s + p1)*(s + p2))
        --> Flanco ascendente
        Recibe: line_transf = [A,z,p1,p2] """
        [C, z, p1, p2] = line_transf
        
        A = (p1 - z)/(p1 - p2)
        B = (z - p2)/(p1 - p2)

        aux = C*Vdd*((A/p1)*(1 - euler**(-p1*t)) + (B/p2)*(1 - euler**(-p2*t))) - \
              C*(Vdd/delta_t)*((A/p1)*(t + euler**(-p1*t)/p1 - 1/p1) + (B/p2)*(t + euler**(-p2*t)/p2 - 1/p2))
        
        if (t < delta_t):
            return aux
        else:
            return aux + C*(Vdd/delta_t)*((A/p1)*(t - delta_t + euler**(-p1*(t - delta_t))/p1 - 1/p1) + \
                   (B/p2)*(t - delta_t + euler**(-p2*(t - delta_t))/p2 - 1/p2))
        
    def temp_resp_LH_ramp_input_2order_output(self, t, delta_t, line_transf, Vdd):
        """ Calcular la respuesta temporal a la salida de la linea para:
        --> Entrada de forma de rampa con slew delta_t
        --> Tension de salida de la linea representada por la siguiente transferencia:
        H(s) = C*(s + z)/((s + p1)*(s + p2))
        --> Flanco descendente
        Recibe: line_transf = [A,z,p1,p2] """
        
        [C, z, p1, p2] = line_transf
        
        A = (p1 - z)/(p1 - p2)
        B = (z - p2)/(p1 - p2)
        
        aux = C*(Vdd/delta_t)*((A/p1)*(t - euler**(-p1*t)/p1 - 1/p1) + \
                   (B/p2)*(t + euler**(-p2*t)/p2 - 1/p2))
                   
        if (t < delta_t):
            return aux 
        else:
            return aux - C*(Vdd/delta_t)*((A/p1)*(t - delta_t + euler**(-p1*(t - delta_t))/p1 - 1/p1) + \
                   (B/p2)*(t - delta_t + euler**(-p2*(t - delta_t))/p2 - 1/p2))        

if __name__ == "__main__":
    # Cantidad de cuadripolos/resitencias/capacitores
    N = 4 
    # Hasta que momento queremos calcular
    M = 3
    # Resistencia y capacidad de cada elemento
    R = 1
    C = 1
    # Capacidad de carga
    CL = 0

    RC = RC_line(R, C, N, CL)
    print(RC.get_moments(M))
    print(RC.get_pi_model())

