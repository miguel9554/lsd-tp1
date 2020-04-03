from Circuit import Circuit
from Simulation import Simulation
from Results import Results
from Source import StepSource
import matplotlib.pyplot as plt


# parametros del circuito
L = 100e-6
C = 30e-18*L*1e6+40e-18*L 
R = 0.1*L*1e6
tao = 5*R*C
N_max = 150

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
    circuit = Circuit(R, C, source, N)
    simulation = Simulation(time_step, end_time, circuit)
    results = Results()

    # simulamos y procesamos los resultados
    simulation.run(results.filename)
    results.process()
    T_vec.append(results.get_rise_time())
    N_vec.append(N)

plt.plot(N_vec, T_vec)
plt.ylabel('Tiempo de crecimiento [s]')
plt.xlabel('Ctdad de cuadripolos')
plt.show()

