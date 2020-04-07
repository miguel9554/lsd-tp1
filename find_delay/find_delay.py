from anytree import Node
from anytree.walker import Walker
from FFD import FFD
from line import Line
from inverter import Inverter
from vsource import Vsource

# Construimos el árbol que representa al circuito
source = Node(name='source', device=Vsource())
ffd1 = Node(name='ffd1', parent=source, device=FFD())
line1 = Node(name='line1', parent=ffd1, device=Line())
inv1 = Node(name='inv1', parent=line1, device=Inverter())
line2 = Node(name='line2', parent=inv1, device=Line())
inv2 = Node(name='inv2', parent=line2, device=Inverter())
line3 = Node(name='line3', parent=inv2, device=Line())
ffd2 = Node(name='ffd2', parent=line3, device=FFD())

# Inicializamos el retardo en 0
total_delay = 0

# Recorremos el circuito elemento por elemento
# El último elemento no lo iteramos, solo nos interesa
# su capacidad de entrada, la carga que representa
w = Walker()
upward, common, downwards = w.walk(source, ffd2)
for node in downwards[:-1]:
    print(f"Analizando el dispositivo {node.name}")
    # Obtenemos los parametros necesarios para computar
    # las cantidades del dispositivo
    input_slew = node.parent.device.get_output_slew()
    load = node.children[0].device.get_input_capacitance()
    print(f"{node.name} tiene un slew de entrada de {input_slew}" \
            f" y una carga de {load}")
    print(f"Con estos parámetros, el retardo del dispositivo es " \
            f"de {node.device.get_delay()}")
    # Sumamos el retardo al retardo total
    total_delay += node.device.get_delay()

print(f"El retardo total es {total_delay}")
