from Circuit import Circuit
from Simulation import Simulation
from Results import Results
from Source import StepSource, ExpSource
import matplotlib.pyplot as plt
import numpy as np
import uuid
import multiprocessing as mp
from typing import List, Tuple


class RC_line_simulated:

    def __init__(self, r: float, c:float, L: float):
        """r y c, resistencia y capacidad por unidad de long, L longitud"""
        self.r = r
        self.c = c
        self.L = L
        self.uid = str(uuid.uuid4())

    def simulate_line(self, rise_time: float, N: int = 50, plot: bool = True) -> \
            Tuple[List[float], List[float], List[float]]:
        """
        Simula la respuesta de la línea a un escalón
        """
        # parametros del circuito
        C = self.c*self.L
        R = self.r*self.L
        tao = 5*R*C

        # parametros de la simulacion
        end_time = rise_time*10
        time_step = end_time/1e5

        # creamos los objetos
        source = ExpSource(2.5, rise_time)
        circuit = Circuit(R, C, source, self.uid, N)
        simulation = Simulation(time_step, end_time, circuit, self.uid)
        results = Results(self.uid)

        # simulamos y procesamos los resultados
        simulation.run(results.filename)
        results.process()

        # limpiamos los archivos
        circuit.clean()
        simulation.clean()
        results.clean()

        return results.time, results.vin, results.vout
        
    def min_sections(self, tolerance: float = 5, N_max: int = 150, plot: bool = False) -> int:
        """
        Obtiene el mínimo N con el que se puede representar a la línea
        con cuadripolos RC, cada uno con valores rL/N y cL/N
        tolerance es el porcentaje del punto de la asíntota que consideramos
        Con plot se decide si plotear TpVsN
        """
        # parametros del circuito
        C = self.c*self.L
        R = self.r*self.L
        tao = 5*R*C

        # parametros de la fuente
        V = 2.5
        pulse_width = tao
        period = pulse_width

        # parametros de la simulacion
        end_time = pulse_width
        time_step = end_time/1e4

        # contenedores de los resultados
        T_vec = []
        N_vec = []

        for N in [N+1 for N in range(N_max)]:

            # creamos los objetos
            source = StepSource(V, pulse_width, period)
            circuit = Circuit(R, C, source, self.uid, N)
            simulation = Simulation(time_step, end_time, circuit, self.uid)
            results = Results(self.uid)

            # simulamos y procesamos los resultados
            simulation.run(results.filename)
            results.process()
            T_vec.append(results.get_rise_time())
            N_vec.append(N)

            # limpiamos los archivos
            circuit.clean()
            simulation.clean()
            results.clean()
        
        if plot:
            plt.plot([int(n) for n in N_vec], [t*1e15 for t in T_vec])
            plt.ylabel('Tiempo de crecimiento [fs]')
            plt.xlabel('Cantidad de cuadripolos')
            plt.title(f'Tiempo de crecimiento para línea de {int(np.ceil(self.L*1e6))} micro')
            plt.grid()
            plt.savefig('TpVsN.png')
            plt.show()
        
        # Consideramos el N mínimo como el mínimo de los N que tienen un tiempo
        # de propagación no mayor a un {tolerancia}% de la asíntota
        N_min = N_vec[np.min(np.nonzero(T_vec < np.min(T_vec)*(1+tolerance/100)))]

        return N_min
    
    def parallel_min_sections(self, tolerance: float = 5, N_max: int = 150, plot: bool = False) -> int:
        """Para correr en paralelo, devuelve también L para saber a cual corresponde ese N"""
        return self.L*1e6, self.min_sections(tolerance, N_max, plot)

