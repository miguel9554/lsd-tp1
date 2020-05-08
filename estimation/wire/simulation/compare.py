import sys
sys.path.insert(0, '../')
sys.path.insert(0, '../../')
from RC_line_simulated import RC_line_simulated
from rc_line import RC_line
import matplotlib.pyplot as plt


# parametros de la línea, res y cap por unidad de long, y longitud
c = 13e-18 + 25e-18 
r = 0.1*1e6
sections = 50

# el máximo L, en micro
line_length = 100e-6

simulation_line = RC_line_simulated(r, c, line_length)
time, input_signal, simulation_result = simulation_line.simulate_line()

# estimation_line = rc_line(r*line_length, c*line_length, sections)

plt.plot(time, input_signal, label='Entrada')
plt.plot(time, simulation_result, label='Salida Simulada')
plt.ylabel('Tensión [V]')
plt.xlabel('Tiempo [s]')
plt.grid()
plt.legend()
plt.show()


