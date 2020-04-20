import anytree
from subprocess import call # Para ejecutar SpiceOpus desde Python

class Simulation:
    """ Representa la simulacion en SpiceOpus de un circuito """
    
    def __init__(self, first_component: anytree.Node, simulacion_circuit_path, simulation_conditions_path) -> None:
        self.first_component = first_component
        self.simulacion_circuit_path = simulacion_circuit_path
        self.simulation_conditions_path = simulation_conditions_path
        
    def build_simulation(self) -> None:
        file = open(self.simulacion_circuit_path,'w+')
             
        header = "********************************************* \n" \
                 "** Cargar el inversor generador de la señal de clock\n" \
                 ".include inversor_clk.inc\n\n" \
                 "********************************************* \n" \
                 "**Fuente de alimentacion \n" \
                 "v1 1 0 dc 2.5 \n" \
                 "********************************************* \n\n" \
                 "********************************************* \n" \
                 "** Senal de reloj \n" \
                 "* Sintaxis: PULSE(V1 V2 DELAY RISE-TIME FALL-TIME DURACION_PULSO PERIODO)\n" \
                 "vp_clk 2 0 PULSE 2.5 0 5n 30ps 30ps 10n 20n \n" \
                 "* inversor_clk IN OUT VDD VSS \n" \
                 "X0 2 3 1 0 inversor_clk \n" \
                 "********************************************* \n\n" \
                 "********************************************* \n" \
                 "** Exitacion de entrada del circuito \n" \
                 "v_in 4 0 PULSE 0 2.5 50n 30ps 30ps 1000n 2000n \n" \
                 "********************************************* \n"
             
        file.write(header)

        self.node_num = 4 # El numero de nodos utilizados comienza en 4
                          # porque los primeros cuatro ya se usaron para la alimentación y la señal de clock
        self.R_num = 0
        self.C_num = 0
        self.device_num = 1
       
        def iterate(component, starting_node):
           
            present_component = component
           
            next_node = starting_node
            while(True):
                component_name = present_component.device.__class__.__name__
                
                if(component_name == "FFD"):
                    self.add_ffd(present_component.device, next_node, file)
                elif(component_name == "Inverter"):
                    self.add_inverter(present_component.device, next_node, file)
                elif(component_name == "RC_line"):
                    self.add_line(present_component.device, next_node, file)
                else:
                    forking_node = self.add_tree_line(present_component.device, next_node, file)
                    iterate(present_component.children[0], self.node_num)
                    iterate(present_component.children[1], forking_node)
                    break
                
                next_node = self.node_num
                if(len(present_component.children) == 0): break
                else: present_component = present_component.children[0]
            ## Fin del bucle ##
            return
       
        iterate(self.first_component, self.node_num)
       
        file.write(".end\n")
        file.truncate()
        file.close()
       
        return
    
    def add_line(self, component, starting_node, file): ## NOTA: AGREGAR EL TIPO DE DATO DE "FILE"
    
        sections = component.sections
        R_per_unit = component.R/sections
        C_per_unit = component.C/sections
 
        line_header = f"""\
*********************************************
** Linea RC 
* Ctotal = {component.C}
* Rtotal = {component.R}
* C por unidad = {C_per_unit}
* R por unidad = {R_per_unit} \n\n"""
                     
        
        file.write(line_header)
            
        if (starting_node == self.node_num):
            initial_unit_text = f"""\
R{self.R_num} ({self.node_num} {self.node_num + 1}) r={R_per_unit}
C{self.C_num} ({self.node_num + 1} 0) c={C_per_unit} \n\n"""

        else:
            initial_unit_text = f"""\
R{self.R_num} ({starting_node} {self.node_num + 1}) r={R_per_unit}
C{self.C_num} ({self.node_num + 1} 0) c={C_per_unit} \n\n"""
                                
        file.write(initial_unit_text)
        self.R_num = self.R_num + 1
        self.C_num = self.C_num + 1
        self.node_num = self.node_num + 1
 
        for i in range(sections - 1):
            line_text = f"""\
R{self.R_num} ({self.node_num} {self.node_num + 1}) r={R_per_unit}
C{self.C_num} ({self.node_num + 1} 0) c={C_per_unit}\n\n"""

            file.write(line_text)
            self.R_num = self.R_num + 1
            self.C_num = self.C_num + 1
            self.node_num = self.node_num + 1     

        component.output_node = self.node_num
        
        return
    
    def add_tree_line(self, component, starting_node, file):
        
        self.add_line(component.line1, self.node_num, file)
        forking_node = self.node_num
        self.add_line(component.line2, self.node_num, file)
        self.add_line(component.line3, forking_node, file)
        
        return forking_node
    
    def add_ffd(self, component, starting_node, file):
          
        component_text = f"""
*********************************************
** Flip-flop {self.device_num}
* dff_x3ry1 RST D CLK QP VDD VSS
* NOTA: El reset se encuentra puesto a masa
X{self.device_num} 0 {starting_node} 3 {self.node_num + 1} 1 0 dff_x3ry1
********************************************* \n\n"""

        file.write(component_text)
        self.device_num = self.device_num + 1
        self.node_num = self.node_num + 1
        
        component.output_node = self.node_num
        
        return        
    
    def add_inverter(self, component, starting_node, file):
          
        component_text = f"""\
*********************************************
** Inversor {self.device_num}
* inv_x1y1 IN OUT VDD VSS
* NOTA: El reset se encuentra puesto a masa
X{self.device_num} {starting_node} {self.node_num + 1} 1 0 inv_x1y1
********************************************* \n\n"""

        file.write(component_text)
        self.device_num = self.device_num + 1
        self.node_num = self.node_num + 1
        
        component.output_node = self.node_num
        
        return  

    
    def simulate_delays(self):
 
        ##########################################################
        # Identificar los nodos cuyo timing va a ser analizado
        
        source_node = 4 # Nodo de la fuente de exitacion del circuito
        simulation_node_list = []
        
        def iterate(component, starting_node):
           
            present_component = component
            previous_node = starting_node
            
            while(True):
                component_name = present_component.device.__class__.__name__
                if(component_name == "RC_tree"):
                    simulation_node_list.append([present_component.device.line2.output_node, previous_node])
                    simulation_node_list.append([present_component.device.line3.output_node, previous_node])
                    iterate(present_component.children[0], present_component.device.line2.output_node)
                    iterate(present_component.children[1], present_component.device.line3.output_node)
                    break
                else:
                    simulation_node_list.append([present_component.device.output_node, previous_node])
                    
                
                previous_node = present_component.device.output_node
                if(len(present_component.children) == 0): break
                else: present_component = present_component.children[0]
            ## Fin del bucle ##
            return
       
        iterate(self.first_component, source_node)
        
        ##########################################################
        ## Preparar las condiciones de simulacion en base a los nodos identificados
        
        file = open(self.simulation_conditions_path,'w+')
        
        header = "********************************************* \n" \
                 "**** Script en NUTMEG para ser llamado por Python **** \n" \
                 "\n.control \n" \
                 "* Cargar circuito \n" \
                 "source archivo_prueba.cir\n\n" \
                 "set noprintheader \n" \
                 "set noprintindex \n" \
                 "set nobreak \n" \
                 "tran 10p 200n 0n \n\n" \
                 "* Guardar resultados de cada nodo \n"
        
        file.write(header)
        
        # Guardar la forma de onda de todos los nodos finales de cada elemento del arbol
        # TODO: EVITAR QUE SE SIMULEN DUPLICADOS
        for i in range(len(simulation_node_list)-1):
            node_file = "forma_onda_nodo_" + str(simulation_node_list[i][1]) + ".txt"
            file.write(f"print v({simulation_node_list[i][1]}) > {node_file}\n")
        
        file.write("\n.endc\n.end\n")
        file.truncate()
        file.close()
        
        # Correr simulacion
        call(["spiceopus", "-c", "-b", self.simulation_conditions_path]) 

        return
    
    
    
    