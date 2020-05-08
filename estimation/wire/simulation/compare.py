from RC_line import RC_line
import matplotlib.pyplot as plt


# parametros de la línea, res y cap por unidad de long, y longitud
c = 30e-18*1e6+40e-18 
r = 0.1*1e6

# el máximo L, en micro
line_length = 100e-6

line = RC_line(r, c, line_length)
time, input_signal, simulation_result = line.simulate_line()

plt.plot(time, input_signal, label='Entrada')
plt.plot(time, simulation_result, label='Salida Simulada')
plt.ylabel('Tensión [V]')
plt.xlabel('Tiempo [s]')
plt.grid()
plt.legend()
plt.show()


