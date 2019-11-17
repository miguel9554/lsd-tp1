from wire.Circuit import Circuit
from wire.Simulation import Simulation
from wire.Results import Results
from wire.Source import StepSource
import matplotlib.pyplot as plt


# parametros del circuito
C = 10e-6
R = 10e3
N_max = 40

# parametros de la fuente
V = 2.5
pulse_width = 100
period = 100

# parametros de la simulacion
end_time = 100
time_step = end_time/1e3

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

