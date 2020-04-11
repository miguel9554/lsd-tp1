import sys
sys.path.insert(0, '../wire')
from tabledevice import TableDevice
from moments import RC_line
from rc_tree import RC_tree
from null_load import null_load


class Device:
    def __init__(self, device):
        self.device = device
        self.output_slew = None
        self.delay = None
    def set_delay(self, input_slew: float, rising_edge: bool, \
            line_number: int = None) -> float:
        if line_number:
            delay = self.device.get_delay(input_slew, line_number, \
                    rising_edge)
        else:
            delay = self.device.get_delay(input_slew, rising_edge)
        self.delay = delay
        return delay
    def set_slew(self, input_slew: float, rising_edge: bool, \
            line_number: int = None) -> float:
        if line_number:
            oslew = self.device.get_output_slew(input_slew, line_number, \
                    rising_edge)
        else:
            oslew = self.device.get_output_slew(input_slew, rising_edge)
        self.output_slew = oslew
        return oslew
    def print_status(self, name: str):
        print(f"{name} tiene un delay de {self.delay:.2e} y un " \
                f"slew de {self.output_slew:.2e}")

# Rutas de las talas
ffd_table = 'tabla_datos_FFD.txt'
inverter_table = 'tabla_datos_inversor.txt'

# Datos de resistencia y capacidad por unidad de longitud
# Se suponen líneas de 1 um de ancho
c = 30e-18 + 40e-18 
r = 0.1

# Largo de las líneas, en micrometros
L1 = 50
# Estos son los largos de la línea común y de las dos ramas
L2 = 20
L21 = 30
L22 = 60
# La línea del tramo de arriba
L11 = 50
# Las de abajo
L21 = 30
L22 = 100

# El slew inicial, que es el del clock de ffd1
# Para un flanco descendente: 441E-12
# Para un flanco ascendente: 551E-12
rising_edge = True
input_slew = 551e-12 if rising_edge else 441e-12

# Declaramos los compoenentes del circuito
ffd1 = Device(TableDevice(ffd_table))
line1 = Device(RC_line(r*L1, c*L1))
inv1 = Device(TableDevice(inverter_table))
tree_line = Device(RC_tree(RC_line(r*L2, c*L2), RC_line(r*L21, c*L21), \
        RC_line(r*L22, c*L22)))
# La rama de arriba
inv11 = Device(TableDevice(inverter_table))
line11 = Device(RC_line(r*L11, c*L11))
ffd11 = Device(TableDevice(ffd_table))
# La rama de abajo
inv21 = Device(TableDevice(inverter_table))
line21 = Device(RC_line(r*L21, c*L21))
inv22 = Device(TableDevice(inverter_table))
line22 = Device(RC_line(r*L22, c*L22))
ffd21 = Device(TableDevice(ffd_table))

# Definimos la carga de cada componente
ffd1.device.set_connected_device(line1.device)
line1.device.set_CL(inv1.device.get_input_capacitance())
inv1.device.set_connected_device(tree_line.device)
tree_line.device.set_CL(inv11.device.get_input_capacitance(), 1)
tree_line.device.set_CL(inv21.device.get_input_capacitance(), 2)
# La rama de arriba
inv11.device.set_connected_device(line11.device)
line11.device.set_CL(ffd11.device.get_input_capacitance())
ffd11.device.set_connected_device(null_load())
# La rama de abajo
inv21.device.set_connected_device(line21.device)
line21.device.set_CL(inv22.device.get_input_capacitance())
inv22.device.set_connected_device(line22.device)
line22.device.set_CL(ffd21.device.get_input_capacitance())
ffd21.device.set_connected_device(null_load())

# Calculamos el delay total, etapa por etapa
ffd1.set_delay(input_slew, rising_edge)
ffd1.set_slew(input_slew, rising_edge)
ffd1.print_status('ffd1')

line1.set_delay(ffd1.output_slew, rising_edge)
line1.set_slew(ffd1.output_slew, rising_edge)
line1.print_status('line1')

inv1.set_delay(line1.output_slew, rising_edge)
inv1.set_slew(line1.output_slew, rising_edge)
rising_edge = not rising_edge
inv1.print_status('inv1')

# Guardamos dos rising edges, uno para la parte de arriba y otro para abajo
urising_edge = rising_edge
lrising_edge = rising_edge

# Seguimos con la parte de arriba
tree_line.set_delay(inv1.output_slew, urising_edge, 1)
tree_line.set_slew(inv1.output_slew, urising_edge, 1)
tree_line.print_status('linea1')

inv11.set_delay(tree_line.output_slew, urising_edge)
inv11.set_slew(tree_line.output_slew, urising_edge)
urising_edge = not urising_edge
inv11.print_status('inv11')

line11.set_delay(inv11.output_slew, urising_edge)
line11.set_slew(inv11.output_slew, urising_edge)
line11.print_status('line11')

# Se rompe por la carga nula
#ffd11.set_delay(line11.output_slew, urising_edge)
#ffd11.print_status('ffd11')

# La parte de abajo
tree_line.set_delay(inv1.output_slew, urising_edge, 2)
tree_line.set_slew(inv1.output_slew, urising_edge, 2)
tree_line.print_status('linea2')

inv21.set_delay(tree_line.output_slew, lrising_edge)
inv21.set_slew(tree_line.output_slew, lrising_edge)
lrising_edge = not lrising_edge
inv21.print_status('inv21')

line21.set_delay(inv21.output_slew, lrising_edge)
line21.set_slew(inv21.output_slew, lrising_edge)
line21.print_status('line21')

inv22.set_delay(line21.output_slew, lrising_edge)
inv22.set_slew(line21.output_slew, lrising_edge)
lrising_edge = not lrising_edge
inv22.print_status('inv22')

line22.set_delay(inv22.output_slew, lrising_edge)
line22.set_slew(inv22.output_slew, lrising_edge)
line22.print_status('line22')

# Se rompe por la carga nula
#ffd21.set_delay(line22.output_slew, lrising_edge)
#ffd21.print_status('ffd21')
