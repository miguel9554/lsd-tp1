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

rising_edge = True
# El slew inicial, que es el del clock de ffd1
input_slew = 670e-12*0.69

################################################################
### Circuito
################################################################

### Construimos el árbol que representa al circuito

################################
##### Circuito de prueba 1 #####
################################
# Largos de las lineas
#L1 = 100
# Estos son los largos de la línea común y de las dos ramas
#L2 = 20
#L21 = 30
#L22 = 60
# La línea del tramo de arriba
#L3 = 100
# Las de abajo
#L4 = 30
#L5 = 100


# Rama principal
#circuit_tree = anytree.Node(name='source', device=vsource(input_slew))
#ffd1 = anytree.Node(name='ffd1', parent=circuit_tree, device=FFD())
#line1 = anytree.Node(name='line1', parent=ffd1, device=RC_line(r*L1, c*L1, sections))
#inv1 = anytree.Node(name='inv1', parent=line1, device=Inverter())
#tree_line = anytree.Node(name='tree_line', parent=inv1, \
#        device=RC_tree(RC_line(r*L2, c*L2, sections), RC_line(r*L21, c*L21, sections), \
#        RC_line(r*L22, c*L22, sections)))
        
# La rama de arriba
#inv11 = anytree.Node(name='inv11', parent=tree_line, device=Inverter())
#line11 = anytree.Node(name='line11', parent=inv11, device=RC_line( \
#        r*L3, c*L3, sections))
#ffd11 = anytree.Node(name='ffd11', parent=line11, device=FFD())

# Rama de abajo
#inv21 = anytree.Node(name='inv21', parent=tree_line, device=Inverter())
#line21 = anytree.Node(name='line21', parent=inv21, device=RC_line( \
#        r*L4, c*L4, sections))
#inv22 = anytree.Node(name='inv22', parent=line21, device=Inverter())
#line22 = anytree.Node(name='line22', parent=inv22, device=RC_line( \
#        r*L5, c*L5, sections))
#ffd21 = anytree.Node(name='ffd21', parent=line22, device=FFD())

################################
##### Circuito de prueba 2 #####
################################
# Largos de las lineas
#L1 = 10
#L2 = 50
#L3 = 20

# Unica rama
#circuit_tree = anytree.Node(name='source', device=vsource(input_slew))
#ffd1 = anytree.Node(name='ffd1', parent=circuit_tree, device=FFD())
#line1 = anytree.Node(name='line1', parent=ffd1, device=RC_line(r*L1, c*L1, sections))
#inv1 = anytree.Node(name='inv1', parent=line1, device=Inverter())
#line2 = anytree.Node(name='line2', parent=inv1, device=RC_line(r*L2, c*L2, sections))
#inv2 = anytree.Node(name='inv2', parent=line2, device=Inverter())
#line3 = anytree.Node(name='line3', parent=inv2, device=RC_line( \
#        r*L3, c*L3, sections))
#ffd2 = anytree.Node(name='ffd2', parent=line3, device=FFD())

################################
##### Circuito de prueba 3 #####
################################
# Largos de las lineas
L1 = 5
L2 = 70
L3 = 10
L31 = 20
L32 = 30
L4 = 50
L5 = 30
L51 = 40
L52 = 20
L6 = 100
L7 = 80

# Rama principal
circuit_tree = anytree.Node(name='source', device=vsource(input_slew))
ffd1 = anytree.Node(name='ffd1', parent=circuit_tree, device=FFD())
line1 = anytree.Node(name='line1', parent=ffd1, device=RC_line(r*L1, c*L1, sections))
inv1 = anytree.Node(name='inv1', parent=line1, device=Inverter())
line2 = anytree.Node(name='line2', parent=inv1, device=RC_line(r*L2, c*L2, sections))
inv2 = anytree.Node(name='inv2', parent=line2, device=Inverter())
tree_line1 = anytree.Node(name='tree_line', parent=inv2, \
        device=RC_tree(RC_line(r*L3, c*L3, sections), RC_line(r*L31, c*L31, sections), \
        RC_line(r*L32, c*L32, sections)))
        
# Rama superior
inv3 = anytree.Node(name='inv3', parent=tree_line1, device=Inverter())
line4 = anytree.Node(name='line5', parent=inv3, device=RC_line(r*L4, c*L4, sections))
ffd2 = anytree.Node(name='ffd2', parent=line4, device=FFD())  

# Rama inferior
inv4 = anytree.Node(name='inv4', parent=tree_line1, device=Inverter())
tree_line2 = anytree.Node(name='tree_line2', parent=inv4, \
        device=RC_tree(RC_line(r*L5, c*L5, sections), RC_line(r*L51, c*L51, sections), \
        RC_line(r*L52, c*L52, sections)))
inv5 = anytree.Node(name='inv5', parent=tree_line2, device=Inverter())
inv6 = anytree.Node(name='inv6', parent=tree_line2, device=Inverter())       
line6 = anytree.Node(name='line6', parent=inv5, device=RC_line(r*L6, c*L6, sections))
line7 = anytree.Node(name='line7', parent=inv6, device=RC_line(r*L7, c*L7, sections))
ffd3 = anytree.Node(name='ffd4', parent=line6, device=FFD())
ffd4 = anytree.Node(name='ffd5', parent=line7, device=FFD())

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
delay, simulated_delay = circuit.find_delay(ffd3, rising_edge, True)
print(f"El delay total del circuito es: \n" \
      f"Estimado: {delay} \n" \
      f"Simulado: {simulated_delay} \n")


