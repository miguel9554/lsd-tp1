******************************************************************
*** Subcircuito de un inversor cargado con otros 30 inversores ***
******************************************************************

** La salida del subcircuito es el nodo de salida del primer inversor
** Dicha salida esta destinada a ser utilizada como señal de clk en el
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
	X16 (OUT AUX VDD VSS) inv_x1y1 
	X17 (OUT AUX VDD VSS) inv_x1y1
	X18 (OUT AUX VDD VSS) inv_x1y1
	X19 (OUT AUX VDD VSS) inv_x1y1 
	X20 (OUT AUX VDD VSS) inv_x1y1
	X21 (OUT AUX VDD VSS) inv_x1y1
	X22 (OUT AUX VDD VSS) inv_x1y1 
	X23 (OUT AUX VDD VSS) inv_x1y1
	X24 (OUT AUX VDD VSS) inv_x1y1
	X25 (OUT AUX VDD VSS) inv_x1y1 
	X26 (OUT AUX VDD VSS) inv_x1y1
	X27 (OUT AUX VDD VSS) inv_x1y1 
	X28 (OUT AUX VDD VSS) inv_x1y1 
	X29 (OUT AUX VDD VSS) inv_x1y1
	X30 (OUT AUX VDD VSS) inv_x1y1

.ends