##########################################
### Determinacion de la tabla del FFD
##########################################

from simulacion import modificar_simulacion
from simulacion import ejecutar_simulacion
from funciones_timing import calcular_rise_time
from funciones_timing import calcular_fall_time
from funciones_timing import calcular_tLH
from funciones_timing import calcular_tHL

from decimal import Decimal # Para imprimir los resultados de la matriz en forma legible
import numpy
import csv
import re 

# Archivos
archivo_transicion_LH_FFD = "transicion_LH_FFD.txt"
archivo_transicion_HL_FFD = "transicion_HL_FFD.txt"
archivo_tabla_FFD = "tabla_datos_FFD.txt"

# Valores de capacidad de salida para la tabla
Cmin = 1
Cmax = 15
Cstep = 1
slew_min = 100# En ps
slew_max = 1400# En ps
slew_step = 100# En ps

#########################################################################################

## Generar un rango de tiempos de slew de entrada
# NOTA: se ha tomado como maximo slew aquel provisto por un inversor
# cargado a su vez con otros 30 inversores
rango_slew = numpy.arange(slew_min, slew_max, slew_step)
rango_slew = [x*1e-12 for x in rango_slew]

# Se asume que la capacidad de entrada del inversor,
# segun lo simulado, es 3fF
C_load_clock = 150e-15

rango_resistencias = [x*0.69/C_load_clock for x in rango_slew]

### Obtener el rango de capacidades de salida posibles
## NOTA: se asume como maximo la de 5 inversores
rango_capacidad = numpy.arange(Cmin, Cmax, Cstep)
rango_capacidad = [x*1e-15 for x in rango_capacidad]

# Crear la lista que sera la "tabla" de resultados segun Cout_ext del FFD
tabla_timing = [0 for x in rango_capacidad]  

# Crear la matriz de timing
res, cap = len(rango_resistencias), len(rango_capacidad)
matriz_timing = [[0 for x in range(res)] for y in range(cap)]  

# Iterar sobre las distintas capacidades de entrada 
# y distintos slew para formar la tabla
for cap_it in range(len(rango_capacidad)):
	for res_it in range(len(rango_resistencias)):
		modificar_simulacion(rango_capacidad[cap_it], rango_resistencias[res_it])
		ejecutar_simulacion()

		tr = calcular_rise_time(archivo_transicion_LH_FFD)
		t_LH = calcular_tLH(archivo_transicion_LH_FFD)
		tf = calcular_fall_time(archivo_transicion_HL_FFD)
		t_HL = calcular_tHL(archivo_transicion_HL_FFD)

		# Crear una unica lista como elemento de la matriz de timing
		celda_timing = [rango_capacidad[cap_it], rango_slew[res_it],tr, tf, t_HL, t_LH]

		# Sumar la lista a la matriz de timing
		matriz_timing[cap_it][res_it] = celda_timing


with open(archivo_tabla_FFD, 'w') as f:
	f.write('CL, Tau_in, Rise Time, Fall Time, Clock-to-Q-HL, Clock-to-Q-LH')
	f.write("\n")
	for cap in range(len(rango_capacidad)):
		for res in range(len(rango_resistencias)):
			f.write(','.join('{:.6e}'.format(i) for i in matriz_timing[cap][res]))
			f.write("\n")