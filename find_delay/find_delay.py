import sys
sys.path.insert(0, '../wire')
from tabledevice import Inverter, FFD
from rc_line import RC_line
from rc_tree import RC_tree
from null_load import null_load
from source import vsource
from circuit import circuit
import anytree


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

# Construimos el árbol que representa al circuito
# Rama principal
circuit_tree = anytree.Node(name='source', device=vsource(input_slew, \
        rising_edge))
ffd1 = anytree.Node(name='ffd1', parent=circuit_tree, device=FFD())
line1 = anytree.Node(name='line1', parent=ffd1, device=RC_line(r*L1, c*L1))
inv1 = anytree.Node(name='inv1', parent=line1, device=Inverter())
tree_line = anytree.Node(name='tree_line', parent=inv1, \
        device=RC_tree(RC_line(r*L2, c*L2), RC_line(r*L21, c*L21), \
        RC_line(r*L22, c*L22)))
# La rama de arriba
inv11 = anytree.Node(name='inv11', parent=tree_line, device=Inverter())
line11 = anytree.Node(name='line11', parent=inv11, device=RC_line( \
        r*L11, c*L11))
ffd11 = anytree.Node(name='ffd11', parent=line11, device=Inverter())
# Rama de abajo
inv21 = anytree.Node(name='inv21', parent=tree_line, device=Inverter())
line21 = anytree.Node(name='line21', parent=inv21, device=RC_line( \
        r*L21, c*L21))
inv22 = anytree.Node(name='inv22', parent=line21, device=Inverter())
line22 = anytree.Node(name='line22', parent=inv22, device=RC_line( \
        r*L22, c*L22))
ffd21 = anytree.Node(name='ffd21', parent=line22, device=FFD())

# Creamos la instancia del circuito y calculamos el delay
circuit = circuit(circuit_tree)
delay = circuit.find_delay(ffd21, True)
print(f"El delay del circuito es de {delay}")

