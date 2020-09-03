from estimation.tabledevice import Inverter, FFD
from estimation.wire.rc_line import RC_line
from estimation.wire.rc_tree import RC_tree
from estimation.null_load import null_load
from estimation.source import vsource
from estimation.circuit import circuit
from simulation.simulation import Simulation
import anytree


################################################################
### Constantes
################################################################

# Tension de alimentacion de todo el circuito
vdd = 2.5

# Datos de resistencia y capacidad por unidad de longitud de las lineas de METAL 2
# Se suponen líneas de 1 um de ancho
c = 13e-18 + 25e-18 
r = 0.1
sections = 50


################################################################
### Largos de las lineas del circuito en micrometros
################################################################
L1 = 5
# Estos son los largos de la línea común y de las dos ramas
L2 = 2
L21 = 3
L22 = 6
# La línea del tramo de arriba
L3 = 5
# Las de abajo
L4 = 3
L5 = 10

rising_edge = True
# El slew inicial, que es el del clock de ffd1
input_slew = 670e-12*0.69

################################################################
### Circuito
################################################################

### Construimos el árbol que representa al circuito

# Rama principal
circuit_tree = anytree.Node(name='source', device=vsource(input_slew))
ffd1 = anytree.Node(name='ffd1', parent=circuit_tree, device=FFD())
line1 = anytree.Node(name='line1', parent=ffd1, device=RC_line(r*L1, c*L1, sections))
inv1 = anytree.Node(name='inv1', parent=line1, device=Inverter())
tree_line = anytree.Node(name='tree_line', parent=inv1, \
        device=RC_tree(RC_line(r*L2, c*L2, sections), RC_line(r*L21, c*L21, sections), \
        RC_line(r*L22, c*L22, sections)))
        
# La rama de arriba
inv11 = anytree.Node(name='inv11', parent=tree_line, device=Inverter())
line11 = anytree.Node(name='line11', parent=inv11, device=RC_line( \
        r*L3, c*L3, sections))
ffd11 = anytree.Node(name='ffd11', parent=line11, device=FFD())

# Rama de abajo
inv21 = anytree.Node(name='inv21', parent=tree_line, device=Inverter())
line21 = anytree.Node(name='line21', parent=inv21, device=RC_line( \
        r*L4, c*L4, sections))
inv22 = anytree.Node(name='inv22', parent=line21, device=Inverter())
line22 = anytree.Node(name='line22', parent=inv22, device=RC_line( \
        r*L5, c*L5, sections))
ffd21 = anytree.Node(name='ffd21', parent=line22, device=FFD())


################################################################
### Estimacion, simulacion y comparacion de los resultados
################################################################

# Creamos una simulacion y mostramos los resultados 
sim = Simulation(ffd1, "simulation/circuit.cir", "simulation/simulation.txt", vdd, True)
sim.build_simulation(rising_edge)
[t50_vector, slew_vector] = sim.simulate_delays()
#print("************* Delays **************")
#print(t50_vector)
#print("************* Slew **************")
#print(slew_vector)

# Creamos la instancia del circuito y calculamos el delay
circuit = circuit(circuit_tree)
delay, simulated_delay = circuit.find_delay(ffd21, rising_edge, True)
print(f"El delay total del circuito es: \n" \
      f"Estimado: {delay} \n" \
      f"Simulado: {simulated_delay} \n")


