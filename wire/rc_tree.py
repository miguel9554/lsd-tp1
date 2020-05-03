import sys
sys.path.insert(0, './estimation')
import numpy as np
from math import e as euler
from wire.rc_line import RC_line
import matplotlib.pyplot as plt
from typing import List
from device import Device

class RC_tree(Device):
    def __init__(self, line1: RC_line, line2: RC_line, line3: RC_line):
        self.line1 = line1
        self.line2 = line2
        self.line3 = line3
        self.Vdd = line1.Vdd
        self.output_device = None
        self.device1 = None
        self.device2 = None

    def set_connected_devices(self, devices: List[Device]) -> None:
        self.line1.CL = 0
        self.line2.CL = devices[0].get_input_capacitance()
        self.line3.CL = devices[1].get_input_capacitance()

        self.device1 = devices[0]
        self.device2 = devices[1]

    def set_output_device(self, device: Device) -> None:
        self.output_device = device

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

    def get_delay(self, input_slew: float, rising_edge: bool, plot: bool = False) -> float:
        line_number = 1 if self.output_device == self.device1 else 2
#        input_50_percent_time = input_slew*np.log(input_slew)
        input_50_percent_time = input_slew
        output_slew = self.get_slew(line_number, input_slew, rising_edge, plot)
        delay = output_slew - input_50_percent_time
        return delay

    def get_simulated_delay(self):
        line = self.line1 if self.output_device == self.device1 else self.line2
        simulated_delay = line.get_simulated_delay()
        
        return simulated_delay
        
    def get_output_slew(self, input_slew: float, rising_edge: bool, plot: bool = False) -> float:
        line_number = 1 if self.output_device == self.device1 else 2
        output_slew = self.get_slew(line_number, input_slew, rising_edge, plot)
        return output_slew
        
    def get_simulated_slew(self):
        line = self.line1 if self.output_device == self.device1 else self.line2
        simulated_delay = line.get_simulated_slew()
        
        return simulated_delay

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


    def get_slew(self, line_number: int, input_slew: float, rising_edge: bool, \
            plot: bool = False) -> float:

        pade = self.get_pade12(line_number)
        voltage = []
        time = []
        for time_step in np.linspace(0, 10*input_slew, 10000):
            time.append(time_step)
            voltage_value = self.temp_resp_LH_exp_input_2order_output(\
                    time_step, input_slew, pade, self.Vdd) if rising_edge \
            else self.temp_resp_HL_exp_input_2order_output(\
            time_step, input_slew, pade, self.Vdd)
            voltage.append(voltage_value)
        
        if plot:
            plt.plot(time, voltage, label='Salida')
            if rising_edge:
                plt.plot(time, self.Vdd*(1-np.exp(-np.array(time)/input_slew)), \
                        label='Entrada')
            else:
                plt.plot(time, self.Vdd*np.exp(-np.array(time)/input_slew), \
                        label='Entrada')
            plt.legend()
            plt.ylabel('Tensión [V]')
            plt.xlabel('Tiempo [s]')
            plt.title('Entrada y salida de la línea')
            plt.show()

        return self.get_50_percent_time(time, voltage, rising_edge)


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


    def get_pade12(self, line_number: int):
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
        if line_number == 1:
            node_number = self.line1.sections + self.line2.sections
            [m0, m1, m2, m3] = self.get_moments(3)[node_number, :]
        else:
            node_number = self.line1.sections + self.line2.sections + \
                    self.line3.sections
            [m0, m1, m2, m3] = self.get_moments(3)[node_number, :]

                    
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
    N = 20
    N1 = N
    N2 = N
    N3 = N
    # Parametros de la línea, res y cap por unidad de long
    c = 30e-18*1e6+40e-18 
    r = 0.1*1e6

    # Largo de cada línea
    L1 = 20e-6
    L2 = 30e-16
    L3 = 60e-6

    # Capacidades y resistencia de cada línea
    R1 = r*L1
    R2 = r*L2
    R3 = r*L3
    C1 = c*L1
    C2 = c*L2
    C3 = c*L3
    # Capacidad de carga
    CL = 0

    tree = RC_tree(RC_line(R1, C1, N1, CL),\
            RC_line(R2, C2, N2, CL), RC_line(R3, C3, N3, CL))
    delay = tree.get_delay(100e-13, 1, True, True)
    slew = tree.get_output_slew(100e-13, 1, True, True)
    print(f"El delay es de {delay} y el slew de {slew}")

if __name__ == "__main__":
    main()
