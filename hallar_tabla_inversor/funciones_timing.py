import csv

def calcular_rise_time(archivo):
	with open(archivo) as csvfile:
		tabla_rise_time = list(csv.reader(csvfile, delimiter='\t'))
		tiempo = [];
		tension_salida = [];

		for row in tabla_rise_time:
			tiempo.append(float(row[0]));
			tension_salida.append(float(row[2]));

		valor_maximo = 0
		for i in range(len(tension_salida)):
			if tension_salida[i] > valor_maximo:
				valor_maximo = tension_salida[i]

		tension_t90 = 0.9*valor_maximo
		t_90 = 0
		for i in range(len(tension_salida)):
			if tension_salida[i] > tension_t90:
				t_90 = tiempo[i]
				break
				
		tension_t10 = 0.1*valor_maximo
		t_10 = 0
		for i in range(len(tension_salida)):
			if tension_salida[i] > tension_t10:
				t_10 = tiempo[i]
				break

		tr = t_90 - t_10;

	return tr


def calcular_fall_time(archivo):
	with open(archivo) as csvfile:
		tabla_fall_time = list(csv.reader(csvfile, delimiter='\t'))
		tiempo = [];
		tension_salida = [];

		for row in tabla_fall_time:
			tiempo.append(float(row[0]));
			tension_salida.append(float(row[2]));

		valor_maximo = tension_salida[10]

		tension_t90 = 0.9*valor_maximo
		t_90 = 0
		for i in range(len(tension_salida)):
			if tension_salida[i] < tension_t90:
				t_90 = tiempo[i]
				break
				
		tension_t10 = 0.1*valor_maximo
		t_10 = 0
		for i in range(len(tension_salida)):
			if tension_salida[i] < tension_t10:
				t_10 = tiempo[i]
				break

		tf = t_10 - t_90;
	return tf

	
def calcular_tLH(archivo):
	with open(archivo) as csvfile:
		tabla_rise_time = list(csv.reader(csvfile, delimiter='\t'))
		tiempo = []
		tension_entrada = []
		tension_salida = []

		for row in tabla_rise_time:
			tiempo.append(float(row[0]));
			tension_entrada.append(float(row[1]))
			tension_salida.append(float(row[2]))

		valor_maximo_entrada = tension_entrada[10]

		t_50_entrada = 0
		tension_t50_entrada = 0.5*valor_maximo_entrada
		for i in range(len(tension_entrada)):
			if tension_entrada[i] < tension_t50_entrada:
				t_50_entrada = tiempo[i]
				break


		valor_maximo_salida = 0
		for i in range(len(tension_salida)):
			if tension_salida[i] > valor_maximo_salida:
				valor_maximo_salida = tension_salida[i]

		tension_t50_salida = 0.5*valor_maximo_salida
		t_50_salida = 0
		for i in range(len(tension_salida)):
			if tension_salida[i] > tension_t50_salida:
				t_50_salida = tiempo[i]
				break	

	return t_50_salida - t_50_entrada


def calcular_tHL(archivo):
	with open(archivo) as csvfile:
		tabla_rise_time = list(csv.reader(csvfile, delimiter='\t'))
		tiempo = []
		tension_entrada = []
		tension_salida = []

		for row in tabla_rise_time:
			tiempo.append(float(row[0]));
			tension_entrada.append(float(row[1]))
			tension_salida.append(float(row[2]))

		valor_maximo_salida = tension_salida[10]

		t_50_salida = 0
		tension_t50_salida = 0.5*valor_maximo_salida
		for i in range(len(tension_salida)):
			if tension_salida[i] < tension_t50_salida:
				t_50_salida = tiempo[i]
				break


		valor_maximo_entrada = 0
		for i in range(len(tension_entrada)):
			if tension_entrada[i] > valor_maximo_entrada:
				valor_maximo_entrada = tension_entrada[i]

		tension_t50_entrada = 0.5*valor_maximo_entrada
		t_50_entrada = 0
		for i in range(len(tension_entrada)):
			if tension_entrada[i] > tension_t50_entrada:
				t_50_entrada = tiempo[i]
				break	

	return t_50_salida - t_50_entrada