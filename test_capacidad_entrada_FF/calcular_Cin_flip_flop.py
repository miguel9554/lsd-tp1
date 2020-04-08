##################################################
### Estimar la capacidad de entrada de un flip flop
##################################################


from subprocess import call # Para ejecutar SpiceOpus desde Python
import csv



## Ejecutar spiceopus con la simulacion elegida
## Los resultados de las simulaciones se alamacenaran en
## los archivos .txt que esta indica

nombre_simulacion = "test_capacidad_entrada_flip_flop_lento.txt"

## Los parametros pasados al simulador representan lo siguiente: 
# "-c" : ejecutar en modo consola
# "-b" : ejecutar en "modo batch", es decir, el simlador se cierra
#		 una vez que se termino con la simulacion
call(["spiceopus", "-c", "-b", nombre_simulacion]) 

###### Rise time
with open('rise_time_Cin_FF.txt') as csvfile:
	tabla_rise_time = list(csv.reader(csvfile, delimiter='\t'))
	tiempo = [];
	tension = [];

	for row in tabla_rise_time:
		tiempo.append(float(row[0]));
		tension.append(float(row[1]));

	valor_maximo = 0
	for i in range(len(tension)):
		if tension[i] > valor_maximo:
			valor_maximo = tension[i]

	tension_t90 = 0.9*valor_maximo
	t_90 = 0
	for i in range(len(tension)):
		if tension[i] > tension_t90:
			t_90 = tiempo[i]
			break
			
	tension_t10 = 0.1*valor_maximo
	t_10 = 0
	for i in range(len(tension)):
		if tension[i] > tension_t10:
			t_10 = tiempo[i]
			break

	print("*** Rise time ****")
	print("T_10 es: " + str(t_10))
	print("T_90 es: " + str(t_90))
	print("El rise time es: " + str(t_90 - t_10))

	# Obtener la Cin sabiendo que la resistencia es de 1k
	R = 1E3
	Cin_rt = (t_90-t_10)/(2.2*R)

	print("Cin en rise time es: " + str(Cin_rt))


###### Fall time
with open('fall_time_Cin_FF.txt') as csvfile:
	tabla_fall_time = list(csv.reader(csvfile, delimiter='\t'))
	tiempo = [];
	tension = [];

	for row in tabla_fall_time:
		tiempo.append(float(row[0]));
		tension.append(float(row[1]));

	tension_t90 = 0.9*tension[0]
	t_90 = 0
	for i in range(len(tension)):
		if tension[i] < tension_t90:
			t_90 = tiempo[i]
			break
			
	tension_t10 = 0.1*valor_maximo
	t_10 = 0
	for i in range(len(tension)):
		if tension[i] < tension_t10:
			t_10 = tiempo[i]
			break

	print("*** Fall time ****")
	print("T_10 es: " + str(t_10))
	print("T_90 es: " + str(t_90))
	print("El fall time es: " + str(t_10 - t_90))

	# Obtener la Cin sabiendo que la resistencia es de 1k
	R = 1E3
	Cin_ft = (t_10-t_90)/(2.2*R)

	print("Cin en fall time es: " + str(Cin_ft))


	# Obtener una Cin equivalente haciendo el promedio entre 
	# la del fall time y la del rise time
	Cin = (Cin_ft + Cin_rt)/2
	print("Cin promedio: " + str(Cin))