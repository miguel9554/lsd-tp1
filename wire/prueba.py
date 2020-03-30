from moments import RC_line
import numpy 
import matplotlib.pyplot as plt

R = 5
C = 1E-16
sections = 10
line = RC_line(R,C,sections)
	
pi_model = line.get_pi_model()
pade = line.get_pade12()
pade2 = line.get_pade22()

delta_t = 1E-12
tau_in = 1E-13
R = pi_model[2]
C = pi_model[1]
Vdd = 2.5

rango_t = numpy.arange(1, 2000, 1)
voltage = []
voltage2 = []
for i in rango_t:
    #voltage.append(line.temp_resp_HL_exp_input_RC_output(i*1E-15, tau_in, R,C, Vdd))
    voltage.append(line.temp_resp_HL_exp_input_2order_output(i*1E-15, tau_in, pade, Vdd))
    voltage2.append(line.temp_resp_HL_exp_input_2order_output_initial_conditions(i*1E-15, tau_in, pade2, Vdd))
    #voltage.append(line.temp_resp_LH_ramp_input_RC_output(i*1E-15, delta_t, R, C, Vdd))
    #voltage.append(line.temp_resp_HL_ramp_input_2order_output(i*1E-15, delta_t, pade, Vdd))

plt.figure(1)
plt.subplot(211)
plt.plot(rango_t, voltage)
plt.subplot(212)
plt.plot(rango_t, voltage2)
plt.show()


