import sys
sys.path.insert(0, './estimation')
sys.path.insert(0, '..')
import numpy as np
from math import e as euler
import matplotlib.pyplot as plt
from typing import Tuple, List
from device import Device


class RC_line(Device):
    def __init__(self, R: float, C: float, sections: int = 20, CL: float=0, Vdd: float=2.5):
        self.R = R
        self.C = C
        self.CL = CL
        self.sections = sections
        self.Vdd = Vdd
        self.output_node = None # TODO: ver si esta bien inicializar esta variable asi
        self.simulated_slew = 0
        self.simulated_delay = 0
 
    def get_simulated_delay(self) -> float:
        return self.simulated_delay

    def get_simulated_slew(self) -> float:
        return self.simulated_slew
 
    def set_connected_devices(self, devices: List[Device]) -> None:
        self.CL = devices[0].get_input_capacitance()

    def get_50_percent_time(self, time: list, voltage: list, rising_edge: bool):
        voltage = np.array(voltage)
        time = np.array(time)

        v_50 = np.max(voltage)*0.5
        v_ini = 0 if rising_edge else np.max(voltage)*1
        max_voltage_index = np.argmax(voltage)
        t_ini = 0 if rising_edge else time[max_voltage_index]
        t_50 = time[np.min(np.nonzero(voltage >= v_50))] if rising_edge else \
        time[max_voltage_index+np.max(np.nonzero(voltage[max_voltage_index:] >= v_50))]

        return t_50 - t_ini

    def set_output_device(self, device: Device) -> None:
        pass

    def get_slew(self, input_slew: float, rising_edge: bool, plot: bool = False) -> float:
        time, voltage = self.get_waveforms(input_slew, rising_edge) 
        if plot:
            plt.plot(time, voltage, label='Salida')
            if rising_edge:
                plt.plot(time, self.Vdd*(1-np.exp(-np.array(time)/(input_slew/0.69))), label='Entrada')
            else:
                plt.plot(time, self.Vdd*np.exp(-np.array(time)/(input_slew/0.69)), label='Entrada')
            plt.legend()
            plt.ylabel('Tensión [V]')
            plt.xlabel('Tiempo [s]')
            plt.title('Entrada y salida de la línea')
            plt.grid()
            plt.show()

        return self.get_50_percent_time(time, voltage, rising_edge)

    def get_waveforms(self, input_slew: float, rising_edge: bool) -> Tuple[List[float], List[float]]:
        pade = self.get_pade12()
        voltage = []
        time = []
        for time_step in np.linspace(0, 10*input_slew, 10000):
            time.append(time_step)
            voltage_value = self.temp_resp_LH_exp_input_2order_output(\
                    time_step, input_slew/0.69, pade, self.Vdd) if rising_edge \
            else self.temp_resp_HL_exp_input_2order_output(\
            time_step, input_slew/0.69, pade, self.Vdd)
            voltage.append(voltage_value)
        return time, voltage

    def get_output_slew(self, input_slew: float, rising_edge: bool, plot: bool = False) -> float:
        return self.get_slew(input_slew, rising_edge, plot)


    def get_delay(self, input_slew: float, rising_edge: bool, plot: bool = False) -> float:
#        input_50_percent_time = input_slew*np.log(input_slew)
        input_50_percent_time = input_slew
        output_slew = self.get_slew(input_slew, rising_edge, plot)
        delay = output_slew - input_50_percent_time
        return delay

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

        # El vector de estados consiste de las N+1 tensiones de nodos
        # (N es la cantidad de cuadripolos de la línea), y en la última
        # posición la corriente de la fuente
        state_vector_length = self.sections + 2

        # Construimos el vector de excitaciones
        # Es igual al de estados, salvo que la última posición es la tensión
        # de la fuente, y no la corriente
        # Este vector representa una única excitación consistenten de una
        #delta temporal de tensión en la fuente
        E = np.zeros(state_vector_length)
        E[state_vector_length-1] = 1

        # Conductancia y capacidad por cuadripolo
        g = self.sections/self.R
        c = self.C/self.sections
        # Construimos la matriz de conductancias
        G = np.zeros((state_vector_length, state_vector_length))
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

        # Construimos la matriz de capacidades
        C = np.zeros((state_vector_length, state_vector_length))
        for column in range(C.shape[0]-1):
            for row in range(C.shape[0]-1):
                if (row == column) and (row != 0):
                    C[row, column] = c+self.CL if row == C.shape[0]-2 else c
                else:
                    continue

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
        
    def get_pade22(self):
        # para flanco descendente
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
    R = 1/N
    C = N
    # Capacidad de carga
    CL = 0

    RC = RC_line(R, C, N, CL)
    print(RC.get_moments(3))
