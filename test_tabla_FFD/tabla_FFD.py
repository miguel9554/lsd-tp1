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

#########################################################################################

### Obtener el rango de capacidades de salida posibles
## NOTA: se asume como maximo la de 5 inversores
rango_capacidad = numpy.arange(Cmin, Cmax, Cstep)
rango_capacidad = [x*1e-15 for x in rango_capacidad]

# Crear la lista que sera la "tabla" de resultados segun Cout_ext del FFD
tabla_timing = [0 for x in rango_capacidad]  


# Iterar sobre las distintas capacidades de entrada 
# y distintos slew para formar la tabla
for cap_it in range(len(rango_capacidad)):
	modificar_simulacion(rango_capacidad[cap_it])
	ejecutar_simulacion()

	tr = calcular_rise_time(archivo_transicion_LH_FFD)
	t_LH = calcular_tLH(archivo_transicion_LH_FFD)
	tf = calcular_fall_time(archivo_transicion_HL_FFD)
	t_HL = calcular_tHL(archivo_transicion_HL_FFD)

	if t_LH > t_HL:
		t_clk_to_Q = t_HL
	else:
		t_clk_to_Q = t_LH
	
	# Crear una unica lista como elemento de la matriz de timing
	celda_timing = [tr, tf, t_clk_to_Q]

	# Sumar la lista a la tabla de timing
	tabla_timing[cap_it] = celda_timing


with open(archivo_tabla_FFD, 'w') as f:
	for cap in range(len(rango_capacidad)):
		f.write(' , '.join('%.3E' % i for i in tabla_timing[cap]))
		f.write("\n")
