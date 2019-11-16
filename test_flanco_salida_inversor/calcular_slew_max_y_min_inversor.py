##################################################
### Calcular los slew promedio con una carga de
### 1) 5 inversores
### 2) Ningun inversor
##################################################

from funciones_timing import calcular_rise_time
from funciones_timing import calcular_fall_time
from subprocess import call # Para ejecutar SpiceOpus desde Python
import csv



## Ejecutar spiceopus con la simulacion elegida
## Los resultados de las simulaciones se alamacenaran en
## los archivos .txt que esta indica

nombre_simulacion = "test_slew_salida_inversor_cargado.txt"

## Los parametros pasados al simulador representan lo siguiente: 
# "-c" : ejecutar en modo consola
# "-b" : ejecutar en "modo batch", es decir, el simlador se cierra
#		 una vez que se termino con la simulacion
call(["spiceopus", "-c", "-b", nombre_simulacion]) 

##################################################
### 1) 5 inversores como carga
##################################################

###### Rise time
tr = calcular_rise_time("rise_time_salida_inversor_cargado_max.txt")

###### Fall time
tf = calcular_fall_time("fall_time_salida_inversor_cargado_max.txt")

print("El rise-time con 5 inversores de carga es: " + str(tr))
print("El fall-time con 5 inversores de carga es: " + str(tf))
print("El slew promedio con 5 inversores de carga es: " + str((tf + tr)/2))

##################################################
### 2) Ningun inversor
##################################################

###### Rise time
tr = calcular_rise_time("rise_time_salida_inversor_sin_cargar.txt")

###### Fall time
tf = calcular_fall_time("fall_time_salida_inversor_sin_cargar.txt")

print("El rise-time sin inversores como carga es: " + str(tr))
print("El fall-time sin inversores como carga es: " + str(tf))
print("El slew promedio sin inversores como carga es: " + str((tf + tr)/2))