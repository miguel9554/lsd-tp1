from Circuit import Circuit
from Simulation import Simulation
from Results import Results
from Source import StepSource
from RC_line_simulated import RC_line_simulated
import matplotlib.pyplot as plt
import numpy as np
import uuid
import multiprocessing as mp

# parametros de la línea, res y cap por unidad de long, y longitud
c = 30e-18*1e6+40e-18 
r = 0.1*1e6

# Largo L, en micro
L = 100

line = RC_line_simulated(r, c, L*1e-6)

max_N = 150
tolerance = 1.5

min_sections = line.min_sections(tolerance, max_N, True)

print(f"La cantidad mínima de secciones es {min_sections}")

