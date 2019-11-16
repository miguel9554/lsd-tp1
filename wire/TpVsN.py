from wire.Circuit import Circuit
from wire.Simulation import Simulation
from wire.Results import Results
import matplotlib.pyplot as plt


# definimos las variables
C = 10e-6
R = 10e3
N_max = 40
end_time = 100
time_step = end_time/1e3
T_vec = []
N_vec = []

for N in [N+1 for N in range(N_max)]:

    # creamos los objetos
    circuit = Circuit(R, C, N)
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

