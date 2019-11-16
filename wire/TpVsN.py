from wire.Circuit import Circuit
from wire.Simulation import Simulation
from wire.Results import Results


# definimos las variables
C = 10e-6
R = 10e3
N = 4
end_time = 10
time_step = end_time/1e3

# creamos los objetos
circuit = Circuit(R, C, N)
simulation = Simulation(time_step, end_time, circuit)
results = Results()

# simulamos y procesamos los resultados
simulation.run(results.filename)
results.process()
results.plot()
