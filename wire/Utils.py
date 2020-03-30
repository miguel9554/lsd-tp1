def float_to_string(number: float, decimals: int = 3):
    if 1e-15 <= number < 1e-12:
        return '{number:.{decimals}f}f'.format(decimals=decimals, number=number/1e-15)
    if 1e-12 <= number < 1e-9:
        return '{number:.{decimals}f}p'.format(decimals=decimals, number=number/1e-12)
    if 1e-9 <= number < 1e-6:
        return '{number:.{decimals}f}n'.format(decimals=decimals, number=number/1e-9)
    if 1e-6 <= number < 1e-3:
        return '{number:.{decimals}f}u'.format(decimals=decimals, number=number/1e-6)
    if 1e-3 <= number < 1:
        return '{number:.{decimals}f}m'.format(decimals=decimals, number=number/1e-3)
    if 1 <= number < 1e3:
        return '{number:.{decimals}f}'.format(decimals=decimals, number=number)
    if 1e3 <= number < 1e6:
        return '{number:.{decimals}f}K'.format(decimals=decimals, number=number/1e3)
    if 1e6 <= number < 1e9:
        return '{number:.{decimals}f}Meg'.format(decimals=decimals, number=number/1e6)
    if 1e9 <= number < 1e12:
        return '{number:.{decimals}f}G'.format(decimals=decimals, number=number/1e9)
    if 1e12 <= number < 1e15:
        return '{number:.{decimals}f}T'.format(decimals=decimals, number=number/1e12)
    else:
        return str(number)
		
# Halla el punto temporal donde se alcanza Vdd/2 (llamado t_50) para 
# una dada respuesta temporal de una linea representada por la funcion
# "resp"
# Recibe: resp : funcion que representa la respuesta temporal
#         max_time : maximo tiempo hasta el que iterar
#		  step : paso temporal para iterar
#		  Vdd : tension de alimentacion del circuito
#         *args : argumentos que recibe resp
#	  
def search_for_t50(resp, max_time, step, Vdd, *args)

	t = 0
	while (t < max_time):
		voltage = resp(t, *args)
		if(voltage > Vdd/2): break
		t = t + step
	
	t_aux = t
	t = 0
	while (t < max_time):
		voltage = resp(t, *args)
		if(voltage < Vdd/2): break
		t = t + step		
	
	if (t > t_aux):
		return t
	else:
		return t_aux
			
	
	
