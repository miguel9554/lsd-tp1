##########################################
### Funcion para abrir el la simulacion
### y modificar los valores de la
### resistencia de entrada y 
### la capacidad de salida
##########################################

from subprocess import call # Para ejecutar SpiceOpus desde Python
import re 	

def modificar_simulacion(cap, res):
	# Abrir el arhivo del circuito para cambiar la resistencia de entrada
	# o la capacidad de salida 
	circuito = "test_tabla_clock_to_Q_FFD.cir"
	archivo_circuito = open(circuito,'r+')
	texto_archivo_circuito = archivo_circuito.read()
	texto_archivo_circuito = re.sub(r'(?<=c\=)(.*)(?=f)', str(cap*1e15), texto_archivo_circuito)
	texto_archivo_circuito = re.sub(r'(?<=r\=)(.*)(?=k)', str(res/1e3), texto_archivo_circuito)
	archivo_circuito.seek(0)
	archivo_circuito.write(texto_archivo_circuito)
	archivo_circuito.truncate()
	archivo_circuito.close()

	return

def ejecutar_simulacion():

	## Ejecutar spiceopus con la simulacion elegida
	## Los resultados de las simulaciones se alamacenaran en
	## los archivos .txt que esta indica

	nombre_simulacion = "test_tabla_clock_to_Q_FFD.txt"

	## Los parametros pasados al simulador representan lo siguiente: 
	# "-c" : ejecutar en modo consola
	# "-b" : ejecutar en "modo batch", es decir, el simlador se cierra
	#		 una vez que se termino con la simulacion
	call(["spiceopus", "-c", "-b", nombre_simulacion]) 

	return