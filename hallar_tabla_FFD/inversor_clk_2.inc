****************************************************************** 
*** Subcircuito de un inversor cargado con otros 30 inversores *** 
****************************************************************** 

** La salida del subcircuito es el nodo de salida del primer inversor 
** Dicha salida esta destinada a ser utilizada como se�al de clk en el 
** trabajo practico 

.include ../caracteristicas_proceso/dig_0p25u_2p5V_stdcells_slow.inc 

.subckt inversor_clk IN OUT VDD VSS 
** Inversor a medir 
X0 (IN OUT VDD VSS) inv_x1y1 
** Inversores de carga 

X1 (OUT AUX VDD VSS) inv_x1y1 
X2 (OUT AUX VDD VSS) inv_x1y1 
X3 (OUT AUX VDD VSS) inv_x1y1 
X4 (OUT AUX VDD VSS) inv_x1y1 
X5 (OUT AUX VDD VSS) inv_x1y1 
X6 (OUT AUX VDD VSS) inv_x1y1 
X7 (OUT AUX VDD VSS) inv_x1y1 
X8 (OUT AUX VDD VSS) inv_x1y1 
X9 (OUT AUX VDD VSS) inv_x1y1 
X10 (OUT AUX VDD VSS) inv_x1y1 
X11 (OUT AUX VDD VSS) inv_x1y1 
X12 (OUT AUX VDD VSS) inv_x1y1 
X13 (OUT AUX VDD VSS) inv_x1y1 
X14 (OUT AUX VDD VSS) inv_x1y1 
X15 (OUT AUX VDD VSS) inv_x1y1 
.ends