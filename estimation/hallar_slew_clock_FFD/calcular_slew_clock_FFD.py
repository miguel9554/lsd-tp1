##################################################
### Estimar el slew del reloj del FFD
##################################################


from subprocess import call # Para ejecutar SpiceOpus desde Python
import csv
from funciones_timing import *

## Ejecutar spiceopus con la simulacion elegida
## Los resultados de las simulaciones se alamacenaran en
## los archivos .txt que esta indica

nombre_simulacion = "test_slew_clock_FFD.txt"
archivo_LH = "transicion_LH_clock.txt"
archivo_HL = "transicion_HL_clock.txt"

## Los parametros pasados al simulador representan lo siguiente: 
# "-c" : ejecutar en modo consola
# "-b" : ejecutar en "modo batch", es decir, el simlador se cierra
#         una vez que se termino con la simulacion
call(["spiceopus", "-c", "-b", nombre_simulacion]) 

###### Rise time
tr = calcular_rise_time(archivo_LH)

print("Rise time:")
print(tr)
        
###### Fall time
tf = calcular_fall_time(archivo_HL)
    
print("Fall time:")
print(tf)