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
Cmin = 0
Cmax = 15
Cstep = 1

min_inversores = 25
max_inversores = 40
step_inversores = 5

#########################################################################################
### Obtener el rango  de inversores que cargan al inversor de clock
rango_inversores = range(min_inversores, max_inversores, step_inversores)

### Obtener el rango de capacidades de salida posibles
## NOTA: se asume como maximo la de 5 inversores
rango_capacidad = numpy.arange(Cmin, Cmax, Cstep)

# Crear la matriz de timing
inv, cap = len(rango_inversores), len(rango_capacidad)
matriz_timing = [[0 for x in range(inv)] for y in range(cap)]  

# Iterar sobre las distintas capacidades de entrada
# y distintos slew para formar la tabla
for cap_it in range(len(rango_capacidad)):
    for inv_it in range(len(rango_inversores)):
        modificar_simulacion(rango_capacidad[cap_it], rango_inversores[inv_it])
        ejecutar_simulacion()

        tr = calcular_rise_time(archivo_transicion_LH_FFD)
        [t_LH, slew_clock] = calcular_tLH(archivo_transicion_LH_FFD)
        tf = calcular_fall_time(archivo_transicion_HL_FFD)
        t_HL = calcular_tHL(archivo_transicion_HL_FFD)

        # Crear una unica lista como elemento de la matriz de timing
        celda_timing = [rango_capacidad[cap_it]*1e-15, slew_clock, tr, tf, t_HL, t_LH]

        # Sumar la lista a la matriz de timing
        matriz_timing[cap_it][inv_it] = celda_timing    

        
print("FIN")        
with open(archivo_tabla_FFD, 'w') as f:
    f.write('CL, Tau_in, Rise Time, Fall Time, Clock-to-Q-HL, Clock-to-Q-LH')
    f.write("\n")
    for cap in range(len(rango_capacidad)):
        for inv_it in range(len(rango_inversores)):
            f.write(','.join('{:.6e}'.format(inv_it) for inv_it in matriz_timing[cap][inv_it]))
            f.write("\n")
            
            