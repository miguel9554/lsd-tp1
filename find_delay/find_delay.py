import sys
sys.path.insert(0, '../wire')
from tabledevice import TableDevice
from moments import RC_line


# Rutas de las talas
ffd_table = 'tabla_datos_FFD.txt'
inverter_table = 'tabla_datos_inversor.txt'

# Datos de resistencia y capacidad por unidad de longitud
#c = 30e-18*1e6+40e-18 
#r = 0.1*1e6
c = 30e-18 + 40e-18 
r = 0.1

# Largo de las líneas
#L1 = 50e-6
L1 = 50

# El slew inicial, que es el del clock de ffd1
# Para un flanco descendente: 441E-12
# Para un flanco ascendente: 551E-12
input_slew = 441E-12

# Declaramos los compoenentes del circuito
ffd1 = TableDevice(ffd_table)
line1 = RC_line(r*L1, c*L1)
inv1 = device=TableDevice(inverter_table)

# Definimos la carga de cada componente
ffd1.set_connected_device(line1)
line1.set_CL(inv1.get_input_capacitance())

print(ffd1.get_delay(input_slew, True))
