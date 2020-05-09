##########################################
### Funcion para abrir el la simulacion
### y modificar los valores de la
### resistencia de entrada y 
### la capacidad de salida
##########################################

from subprocess import call # Para ejecutar SpiceOpus desde Python
import re     

def construir_header(archivo_inversor_clk): 
    header = "****************************************************************** \n" \
             "*** Subcircuito de un inversor cargado con otros 30 inversores *** \n" \
             "****************************************************************** \n\n" \
             "** La salida del subcircuito es el nodo de salida del primer inversor \n" \
             "** Dicha salida esta destinada a ser utilizada como señal de clk en el \n" \
             "** trabajo practico \n\n" \
             ".include ../../caracteristicas_proceso/dig_0p25u_2p5V_stdcells_slow.inc \n\n"  \
             ".subckt inversor_clk IN OUT VDD VSS \n"  \
             "** Inversor a medir \n"  \
             "X0 (IN OUT VDD VSS) inv_x1y1 \n"  \
             "** Inversores de carga \n\n"
    
    archivo_inversor_clk.write(header) 
    
    return

def modificar_simulacion(cap, inv):
    # Abrir el arhivo del circuito para cambiar la capacidad de salida
    # o el numero de inversores que cargan al inversor de clock
    circuito = "test_tabla_clock_to_Q_FFD.cir"
    inversor_clk = "inversor_clk.inc"
    
    # Modificar el archivo del circuito
    archivo_circuito = open(circuito,'r+')
    texto_archivo_circuito = archivo_circuito.read()    
    texto_archivo_circuito = re.sub(r'(?<=c\=)(.*)(?=f)', str(cap*1e-15), texto_archivo_circuito)
    archivo_circuito.seek(0)
    archivo_circuito.write(texto_archivo_circuito)
    archivo_circuito.truncate()
    archivo_circuito.close()
    
    # Modificar el archivo del inversor
    archivo_inversor_clk = open(inversor_clk, 'w+') 
    construir_header(archivo_inversor_clk) 
   
    for i in range(inv):
        archivo_inversor_clk.write("X" + str(i+1) + " (OUT AUX VDD VSS) inv_x1y1 \n")
  
    archivo_inversor_clk.write(".ends")
    archivo_inversor_clk.truncate()
    archivo_inversor_clk.close()

 
    return

def ejecutar_simulacion():

    ## Ejecutar spiceopus con la simulacion elegida
    ## Los resultados de las simulaciones se alamacenaran en
    ## los archivos .txt que esta indica

    nombre_simulacion = "test_tabla_clock_to_Q_FFD.txt"

    ## Los parametros pasados al simulador representan lo siguiente: 
    # "-c" : ejecutar en modo consola
    # "-b" : ejecutar en "modo batch", es decir, el simlador se cierra
    #         una vez que se termino con la simulacion
    call(["spiceopus", "-c", "-b", nombre_simulacion]) 

    return