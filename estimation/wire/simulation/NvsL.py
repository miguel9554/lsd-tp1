from Circuit import Circuit
from Simulation import Simulation
from Results import Results
from Source import StepSource
from RC_line_simulated import RC_line_simulated
import matplotlib.pyplot as plt
import numpy as np
import uuid
import multiprocessing as mp

def get_N(r: float, c: float, L: float) -> int:    
    line = RC_line_simulated(r, c, L*1e-6)
    return line.parallel_min_sections(1.5, 100, False)

# parametros de la línea, res y cap por unidad de long, y longitud
c = 30e-18*1e6+40e-18 
r = 0.1*1e6

# el máximo L, en micro
L_max = 100

args = [(r, c, l) for l in range(1, L_max+1)]    
p = mp.Pool()
results = p.starmap(get_N, args)

L_vec = []
N_vec = []

for tup in results:
    L_vec.append(tup[0])
    N_vec.append(tup[1])

plt.plot(L_vec, N_vec)
plt.ylabel('Cantidad mínima de cuadripolos')
plt.xlabel('Largo de la línea [um]')
plt.title('Cantidad de cuadripolos para distintos largos de línea')
plt.grid()
plt.savefig('NvsL.png')
plt.show()

