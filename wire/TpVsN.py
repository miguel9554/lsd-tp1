from wire.Circuit import Circuit
from wire.Simulation import Simulation
from wire.Results import Results


# definimos las variables
C = 10e-6
R = 10e3
N_max = 15
end_time = 1
time_step = end_time/1e3

# creamos los objetos
circuit = Circuit(R, C)
simulation = Simulation(time_step, end_time, circuit)
results = Results()

for N in [N+1 for N in range(N_max)]:
    # Modificamos N
    circuit.N = N
    # simulamos y procesamos los resultados
    simulation.run(results.filename)
    results.process()
    results.plot()
    print('El rise time es de {rise_time}'.format(rise_time=results.get_rise_time()))

exit()

