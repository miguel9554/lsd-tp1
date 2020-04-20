import anytree

class Simulation:
    """ Representa la simulacion en SpiceOpus de un circuito """
    
    def __init__(self, first_component: anytree.Node, simulation_path) -> None:
        self.first_component = first_component
        self.simulation_path = simulation_path
        self.simulation_node_list = [] 
        
    def build_simulation(self) -> None:
        file = open(self.simulation_path,'w+')
             
        header = "********************************************* \n" \
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
                 "v_in 4 0 PULSE 0 2.5 20n 30ps 30ps 40n 80n \n" \
                 "********************************************* \n"
             
        file.write(header)

        self.node_num = 4 # El numero de nodos utilizados comienza en 4
                          # porque los primeros cuatro ya se usaron para la alimentación y la señal de clock
        self.R_num = 0
        self.C_num = 0
        self.ffd_num = 0
        self.inv_num = 0
       
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
R{self.R_num} {self.node_num} {self.node_num + 1}
C{self.C_num} {self.node_num + 1} 0 \n\n"""

        else:
            initial_unit_text = f"""\
R{self.R_num} {starting_node} {self.node_num + 1}
C{self.C_num} {self.node_num + 1} 0 \n\n"""
                                
        file.write(initial_unit_text)
        self.R_num = self.R_num + 1
        self.C_num = self.C_num + 1
        self.node_num = self.node_num + 1
 
        for i in range(sections - 1):
            line_text = f"""\
R{self.R_num} {self.node_num} {self.node_num + 1}
C{self.C_num} {self.node_num + 1} 0 \n\n"""

            file.write(line_text)
            self.R_num = self.R_num + 1
            self.C_num = self.C_num + 1
            self.node_num = self.node_num + 1     

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
** Flip-flop {self.ffd_num}
* dff_x3ry1 RST D CLK QP VDD VSS
* NOTA: El reset se encuentra puesto a masa
X{self.ffd_num} 0 {starting_node} 3 {self.node_num + 1} 1 0 dff_x3ry1
********************************************* \n\n"""

        file.write(component_text)
        self.ffd_num = self.ffd_num + 1
        self.node_num = self.node_num + 1
        return        
    
    def add_inverter(self, component, starting_node, file):
          
        component_text = f"""\
*********************************************
** Inversor {self.inv_num}
* inv_x1y1 IN OUT VDD VSS
* NOTA: El reset se encuentra puesto a masa
X{self.inv_num} {starting_node} {self.node_num + 1} 1 0 inv_x1y1
********************************************* \n\n"""

        file.write(component_text)
        self.inv_num = self.inv_num + 1
        self.node_num = self.node_num + 1
        return  

    
    def find_delays(self):
    
    
    
    