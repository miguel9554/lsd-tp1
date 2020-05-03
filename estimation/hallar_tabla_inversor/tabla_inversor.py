##########################################
### Determinacion de la tabla del inversor
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

# Nombres de archivos
archivo_rise_time = "rise_time_tabla_inversor.txt"
archivo_fall_time = "fall_time_tabla_inversor.txt"
archivo_tabla_inversor = "tabla_datos_inversor.txt"

# Valores de capacidad de salida y slew de entrada para la tabla
Cmin = 1 # En pF
Cmax =  15 # En pF
Cstep = 1 # En pF
slew_min = 10# En ps
slew_max = 500# En ps
slew_step = 10# En ps

#########################################################################

## Generar un rango de tiempos de slew de entrada
# NOTA: se ha tomado como maximo slew el provisto por un inversor cargado
# con otros 5 inversores
rango_slew = numpy.arange(slew_min, slew_max, slew_step)
rango_slew = [x*1e-12 for x in rango_slew]

# Obtener la resistencia que se reemplazara en la entrada
# del inversor para crear el slew deseado

# Se asume que la capacidad de entrada del inversor,
# segun lo simulado, es 3fF
Cin_inv = 3e-15

rango_resistencias = [x*0.69/Cin_inv for x in rango_slew]

## Generar un rango de capacidades de salida
# NOTA: se ha tomado como maxima capacidad la de 5 invesores
rango_capacidad = numpy.arange(Cmin, Cmax, Cstep)
rango_capacidad = [x*1e-15 for x in rango_capacidad]

# Crear la matriz de timing
res, cap = len(rango_resistencias), len(rango_capacidad)
matriz_timing = [[0 for x in range(res)] for y in range(cap)]  

# Iterar sobre las distintas capacidades de entrada 
# y distintos slew para formar la tabla
for cap_it in range(len(rango_capacidad)):
	for res_it in range(len(rango_resistencias)):
		modificar_simulacion(rango_capacidad[cap_it], rango_resistencias[res_it])
		ejecutar_simulacion()

		tr = calcular_rise_time(archivo_rise_time)
		t_LH = calcular_tLH(archivo_rise_time)
		tf = calcular_fall_time(archivo_fall_time)
		t_HL = calcular_tHL(archivo_fall_time)

		# Crear una unica lista como elemento de la matriz de timing
		celda_timing = [rango_capacidad[cap_it], rango_slew[res_it],tr, tf, t_HL, t_LH]

		# Sumar la lista a la matriz de timing
		matriz_timing[cap_it][res_it] = celda_timing


with open(archivo_tabla_inversor, 'w') as f:
	f.write('CL, Tau_in, Rise Time, Fall Time, t_HL, t_LH')
	f.write("\n")
	for cap in range(len(rango_capacidad)):
		for res in range(len(rango_resistencias)):
			f.write(','.join('{:.6e}'.format(i) for i in matriz_timing[cap][res]))
			f.write("\n")




