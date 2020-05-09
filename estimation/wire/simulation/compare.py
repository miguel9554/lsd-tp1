import sys
sys.path.insert(0, '../')
sys.path.insert(0, '../../')
from RC_line_simulated import RC_line_simulated
from rc_line import RC_line
import matplotlib.pyplot as plt
import numpy as np


# parametros de a línea, res y cap por unidad de long, y longitud
c = 13e-18 + 25e-18 
r = 0.1
sections = 50

# Largo de la línea, en micro
line_length = 100
input_slew = 100e-12

simulation_line = RC_line_simulated(r, c, line_length)
time, simulation_input_signal, simulation_result = simulation_line.simulate_line(input_slew/0.69)

estimation_line = RC_line(r*line_length, c*line_length, sections)
time_estimation, estimation_result = estimation_line.get_waveforms(input_slew, True)

plt.plot(time, simulation_input_signal, label='Entrada de simulacion')
plt.plot(time, simulation_result, label='Salida Simulada')
plt.plot(time_estimation, 2.5*(1-np.exp(-np.array(time_estimation)/(input_slew/0.69))), label='Entrada estimada')
plt.plot(time_estimation, estimation_result, label='Salida estimada')
plt.ylabel('Tensión [V]')
plt.xlabel('Tiempo [s]')
plt.grid()
plt.legend()
plt.show()

