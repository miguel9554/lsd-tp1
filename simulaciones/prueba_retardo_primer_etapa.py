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

nombre_simulacion = "circuito_prueba.txt"

## Los parametros pasados al simulador representan lo siguiente: 
# "-c" : ejecutar en modo consola
# "-b" : ejecutar en "modo batch", es decir, el simlador se cierra
#		 una vez que se termino con la simulacion
call(["spiceopus", "-c", "-b", nombre_simulacion]) 

###### Rise time
tr = calcular_rise_time("rise_time_salida_ffd.txt")

###### Fall time
tf = calcular_fall_time("fall_time_salida_ffd.txt")

print("El rise-time es " + str(tr))
print("El fall-time es " + str(tf))
