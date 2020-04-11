import sys
sys.path.insert(0, '../wire')
from tabledevice import TableDevice
from moments import RC_line


class Device:
    def __init__(self, device):
        self.device = device
        self.output_slew = None
        self.delay = None
    def set_delay(self, input_slew: float, rising_edge: bool) -> float:
        delay = self.device.get_delay(input_slew, rising_edge)
        self.delay = delay
        return delay
    def set_slew(self, input_slew: float, rising_edge: bool) -> float:
        oslew = self.device.get_output_slew(input_slew, rising_edge)
        self.output_slew = oslew
        return oslew

# Rutas de las talas
ffd_table = 'tabla_datos_FFD.txt'
inverter_table = 'tabla_datos_inversor.txt'

# Datos de resistencia y capacidad por unidad de longitud
# Se suponen líneas de 1 um de ancho
c = 30e-18 + 40e-18 
r = 0.1

# Largo de las líneas, en micrometros
L1 = 50

# El slew inicial, que es el del clock de ffd1
# Para un flanco descendente: 441E-12
# Para un flanco ascendente: 551E-12
input_slew = 551e-12

# Declaramos los compoenentes del circuito
ffd1 = Device(TableDevice(ffd_table))
line1 = Device(RC_line(r*L1, c*L1))
inv1 = Device(TableDevice(inverter_table))

# Definimos la carga de cada componente
ffd1.device.set_connected_device(line1.device)
line1.device.set_CL(inv1.device.get_input_capacitance())

ffd1.set_delay(input_slew, True)
print(f"El delay de ffd1 es de {ffd1.delay}")
ffd1.set_slew(input_slew, True)
print(f"El slew de salida de ffd1 es de {ffd1.output_slew}")
line1.set_delay(ffd1.output_slew, True)
print(f"El delay de la línea es de {line1.delay}")
line1.set_slew(ffd1.output_slew, True)
print(f"El slew de la línea 1 es de {line1.output_slew}")
