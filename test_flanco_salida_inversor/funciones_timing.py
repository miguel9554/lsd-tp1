import csv

def calcular_rise_time(archivo):
	with open(archivo) as csvfile:
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

		tr = t_90 - t_10;

	return tr


def calcular_fall_time(archivo):
	with open(archivo) as csvfile:
		tabla_fall_time = list(csv.reader(csvfile, delimiter='\t'))
		tiempo = [];
		tension = [];

		for row in tabla_fall_time:
			tiempo.append(float(row[0]));
			tension.append(float(row[1]));

		valor_maximo = tension[10]

		tension_t90 = 0.9*valor_maximo
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

		tf = t_10 - t_90;
	return tf