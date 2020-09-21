#####################################################
### Funciones para estimar el retardo de salida de una etapa
### a partir de los valores del equivalente pi
#####################################################

#############################
## Dependencias
#############################
import csv
from numpy import log as ln
from scipy.optimize import newton as newton_raphson
from scipy.optimize import root as newton_raphson_multivariable
from math import e as euler
from numpy import log as ln
import numpy as np
import sys
import os

class Estimador:
    """ Encargada de realizar la estimacion del delay y del slew para 
        de salida para los inversores y flip-flops empleando sus tablas """

    def __init__(self, modelo_pi, Tau_in, Vdd, nombre_tabla_timing, umbral_err, \
            debug: bool = False):
        
        [self.C2, self.C1, self.R] = modelo_pi
       
        
        self.Vdd = Vdd
        self.umbral_err = umbral_err
        
        # Slew de entrada obtenido a partir de la constante de tiempo
        # de entrada
        self.t_50_in = 0.69*Tau_in
        self.Tau_in = Tau_in
        
        ## Abrir tabla del rising edge
        f=open(nombre_tabla_timing, "r")
        self.tabla_timing = list(csv.reader(f, delimiter=','))
        self.tabla_timing.pop(0) # Quitar la primera linea de la tabla, que se corresponde con los nombres de cada columna
        
        for i in range(len(self.tabla_timing)):
            self.tabla_timing[i] = [float(j) for j in self.tabla_timing[i]]            

        self.output_stream = sys.stdout if debug else open(os.devnull, 'w')
            

    def estimar_retardo_rise(self):
        
        print("### Estimando retardo ### ", file=self.output_stream)
         
        ## Se comienza por obtener los valores semillas para el proceso iterativo
        
        ########################################################################
        # METODO 1: obtenido del paper de Pillegi 1996
        if ((self.C1 + self.C2) < self.tabla_timing[-1][0]):
            CL = self.C1 + self.C2
        else:
            CL = self.tabla_timing[-1][0]
            
        [t_50, t_20, t_delay] = self.buscar_en_tabla(self.tabla_timing, CL, self.Tau_in, True)     
        t_90 = -(t_50/ln(2))*ln(0.1)
        
        Rd = (t_90 - t_50)/(CL*ln(5))
        
        delta_t = (10/3)*(t_50 - t_20)
        t0 = t_50 - 0.69*Rd*CL - delta_t/2 ### NOTA: OBSERVAR QUE ESTE VALOR ES NEGATIVO, PERO NO PARECIERA
                                           ### PERJUDICAR LA CONVERGENCIA 
        ########################################################################
         
        ########################################################################    
        # METODO 2: propio, diverge
        ## Obtener estimacion de Rd en base a la capacidad y retardos de entrada
        ## mas altos posibles para el inversor o FF que va a ser el "driver" de la linea
        #CL = self.tabla_timing[-1][0]
        #t_90 = -(self.tabla_timing[-1][2]/2.2)*ln(0.1); # Extraccion de tiempos de interes a partir del RISE TIME
        #t_50 = -(self.tabla_timing[-1][2]/2.2)*ln(0.5); # Extraccion de tiempos de interes a partir del RISE TIME
        #t_20 = -(self.tabla_timing[-1][2]/2.2)*ln(0.8); # Extraccion de tiempos de interes a partir del RISE TIME
        #Rd = (t_90 - t_50)/(CL*ln(5));
        #
        ## Obtener semilla de Delta_t y t_0
        # delta_t = t_90
        # t0 = t_90/10
        ########################################################################
        
        ## Comenzar a iterar hasta llegar al umbral
        error_relativo = 1;
        while error_relativo > self.umbral_err:
            print("--> Siguiente iteracion <--", file=self.output_stream)
            # Resolver la capacidad equivalente a partir de
            # igualar las corrientes del modelo pi y del modelo
            # RC equivalente
            CL = newton_raphson(self.i_promedio_newton_raphson, CL, self.derivada_i_promedio_newton_raphson, args=[delta_t, Rd, self.C1, self.R, self.C2], tol=0.05E-15, maxiter=10);
            
            #print("Termino NR para corrientes", file=self.output_stream)

            # Buscar en la tabla del FF o del inversor
            # [t_50, t_20] = buscar_en_tabla_FF(CL);
            [t_50_sig, t_20, t_LH] = self.buscar_en_tabla(self.tabla_timing, CL, self.Tau_in, True);
            
            
            # Obtener la siguiente iteracion de t0 y delta_t
            t0 = newton_raphson(self.v_o_newton_raphson, t0, self.derivada_v_o_newton_raphson, args=[CL, t_50_sig + self.t_50_in, t_20 + self.t_50_in, Rd, 0.5*self.Vdd, 0.8*self.Vdd]);
            
            #print("Termino NR para tension", file=self.output_stream)
            
            delta_t = self.delta_t_vs_CL_y_t0(CL, t0, t_50_sig, 0.5*self.Vdd, Rd);
            
            print("Error relativo de la iteracion:", file=self.output_stream)
            error_relativo = (t_50_sig - t_50)/t_50
            t_50 = t_50_sig
            if error_relativo < 0:
                error_relativo = -error_relativo
            
            print(error_relativo, file=self.output_stream)
            print('\n', file=self.output_stream)
        # Fin de la iteracion
        #####################
        
        print("### Fin de la estimacion ###", file=self.output_stream)
        #print("Resultados:", file=self.output_stream)
        #print("CL: ", file=self.output_stream)
        #print(CL, file=self.output_stream)
        #print("t_50: ", file=self.output_stream)
        #print(t_50, file=self.output_stream)
        
        return [CL, t_50, t_LH]
        

    def estimar_retardo_fall(self):
    
        ########################################################################
        # METODO 1: obtenido del paper de Pillegi 1996
        if ((self.C1 + self.C2) < self.tabla_timing[-1][0]):
            CL = self.C1 + self.C2
        else:
            CL = self.tabla_timing[-1][0]
            
        [t_50, t_20, t_delay] = self.buscar_en_tabla(self.tabla_timing, CL, self.Tau_in, False)     
        t_90 = -(t_50/ln(2))*ln(0.9)
        
        Rd = (t_50 - t_90)/(CL*ln(5));
        
        delta_t = (10/3)*(t_20 - t_50)
        t0 = t_50 - 0.69*Rd*CL - delta_t/2
        ########################################################################    
    

        ########################################################################    
        # METODO 2: propio, diverge    
        ## Obtener estimacion de Rd en base a la capacidad y retardos de entrada
        ## mas altos posibles para el inversor o FF que va a ser el "driver" de la linea
        #CL = self.tabla_timing[-1][0]
        #t_90 = -(self.tabla_timing[-1][3]/2.2)*ln(0.9); # Extraccion de tiempos de interes a partir del RISE TIME
        #t_50 = -(self.tabla_timing[-1][3]/2.2)*ln(0.5); # Extraccion de tiempos de interes a partir del RISE TIME
        #t_20 = -(self.tabla_timing[-1][3]/2.2)*ln(0.2); # Extraccion de tiempos de interes a partir del RISE TIME
        #Rd = (t_50 - t_90)/(CL*ln(5));
        #
        ## Obtener semilla de Delta_t y t_0
        #delta_t = t_90
        #t0 = t_90/10
        ########################################################################
        
        ## Comenzar a iterar hasta llegar al umbral
        error_relativo = 1;
        
        ## Comenzar a iterar hasta llegar al umbral
        error_relativo = 1;

        print("\nComienza el bucle\n", file=self.output_stream)
        while error_relativo > self.umbral_err:
            print("Siguiente iteracion", file=self.output_stream)
            
            # Resolver la capacidad equivalente a partir de
            # igualar las corrientes del modelo pi y del modelo
            # RC equivalente
            CL = newton_raphson(self.i_promedio_newton_raphson, CL, self.derivada_i_promedio_newton_raphson, args=[delta_t, Rd, self.C1, self.R, self.C2], tol=0.05E-15, maxiter=10);
            
            print("Termino NR para corrientes", file=self.output_stream)

            # Buscar en la tabla del FF o del inversor
            # [t_50, t_20] = buscar_en_tabla_FF(CL);
            [t_50_sig, t_20, t_HL] = self.buscar_en_tabla(self.tabla_timing, CL, self.Tau_in, False);
            
            # Obtener la siguiente iteracion de t0 y delta_t
            sol = newton_raphson_multivariable(self.v_o_newton_raphson_fall_time, [t0, delta_t], jac=self.jacobiano_v_o_newton_raphson, args=(CL, t_50_sig + self.t_50_in, t_20 + self.t_50_in, Rd, 0.5*self.Vdd, 0.2*self.Vdd));
            [t0, delta_t] = sol.x
            
            print("Termino NR para tension", file=self.output_stream)
            
            print("Calcular error relativo:", file=self.output_stream)
            error_relativo = (t_50_sig - t_50)/t_50
            t_50 = t_50_sig
            if error_relativo < 0:
                error_relativo = -error_relativo
            
            print(error_relativo, file=self.output_stream)
            print('\n', file=self.output_stream)
        # Fin de la iteracion
        #####################
        
        #print("Resultados:", file=self.output_stream)
        #print("CL: ", file=self.output_stream)
        #print(CL, file=self.output_stream)
        #print("t_50: ", file=self.output_stream)
        #print(t_50, file=self.output_stream)
        
        return [CL, t_50, t_HL]
        
    ##### FUNCIONES SOLO PARA RISE-TIME #####
    def v_o_newton_raphson(self, t0, CL, t_50, t_20, Rd, V_50, V_20):
        
        #Alternativa 1
        #return (t_50 - t0 - Rd*CL*(1-euler**(-(t_50-t0)/(Rd*CL))))/(t_20 - t0 - Rd*CL*(1-euler**(-(t_20-t0)/(Rd*CL)))) - V_50/V_20
        
        #Alternativa 2
        #return ln(t_50 - t0 - Rd*CL*(1-euler**(-(t_50-t0)/(Rd*CL)))) - ln(t_20 - t0 - Rd*CL*(1-euler**(-(t_20-t0)/(Rd*CL)))) - ln(V_50/V_20)
        
        #Alternativa 3
        return Rd*CL*(V_50 - V_20) + V_50*t_20 - V_20*t_50 + (V_20 - V_50)*t0 + Rd*CL*(V_50*euler**(-(t_20 - t0)/(Rd*CL)) - V_20*euler**(-(t_50-t0)/(Rd*CL)))

    def derivada_v_o_newton_raphson(self, t0, CL, t_50, t_20, Rd, V_50, V_20):
        
        #Alternativa 1
        #return (-1 + (t_50 - t0)*euler**(-(t_50 - t0)/(Rd*CL)))/(t_50 - t0 - Rd*CL*(1-euler**(-(t_50-t0)/(Rd*CL)))) # FALTA COMPLETAR
        
        #Alternativa 2
        #return (-1 + (t_50 - t0)*(euler**(-(t_50-t0)/(Rd*CL)))/(Rd*CL))/(t_50 - t0 - Rd*CL*(1-(euler**(-(t_50-t0)/(Rd*CL))))) - (-1 + (t_20 - t0)*(euler**(-(t_20-t0)/(Rd*CL)))/(Rd*CL))/(t_20 - t0 - Rd*CL*(1-(euler**(-(t_20-t0)/(Rd*CL)))))

        #Alternativa 3
        return V_20 - V_50 + ((t_20 - t0)*V_50*euler**(-(t_20-t0)/(Rd*CL)) - (t_50 - t0)*V_20*euler**(-(t_50-t0)/(Rd*CL)))/(Rd*CL)

    def delta_t_vs_CL_y_t0(self, CL, t0, t1, V_1, Rd):
        return ((self.Vdd)/V_1)*(t1 - t0 - Rd*CL*(1 - euler**(-(t1-t0)/(Rd*CL))))
        
        
    ##### FUNCIONES SOLO PARA FALL-TIME #####

    # timing = [t0, delta_t]
    def v_o_newton_raphson_fall_time(self, timing, CL, t_50, t_20, Rd, V_50, V_20):
        return [((self.Vdd) - V_20)*timing[1] - (self.Vdd)*((t_20-timing[0]) - Rd*CL*(1 - euler**(-(t_20 - timing[0])/(Rd*CL)))),
        ((self.Vdd) - V_50)*timing[1] - (self.Vdd)*((t_50-timing[0]) - Rd*CL*(1 - euler**(-(t_50 - timing[0])/(Rd*CL))))]
        
    # timing = [t0, delta_t]
    def jacobiano_v_o_newton_raphson(self, timing, CL, t_50, t_20, Rd, V_50, V_20):
        return [[(self.Vdd)*(1 + euler**(-(t_20 - timing[0])/(Rd*CL))), (self.Vdd) - V_20],
        [(self.Vdd)*(1 + euler**(-(t_50 - timing[0])/(Rd*CL))), (self.Vdd) - V_50]]

        
    ##### FUNCIONES GENERALES #####
        
    def i_promedio_newton_raphson(self, CL, delta_t, Rd, C1, R, C2):
        # Cero de la corriente del equivalente Pi
        wz = (C1 + C2)/(R*C1*C2)

        # Coeficientes del polinomio de segundo orden en el denominador de la
        # transferencia
        a_coef = 1
        b_coef = (Rd*(C1 + C2) + C1*R)/(R*Rd*C1*C2)
        c_coef = 1/(R*Rd*C1*C2)
        
        # Polos de la corriente del equivalente Pi
        wp1 = -(-b_coef - (b_coef**2 - 4*a_coef*c_coef)**(0.5))/(2*a_coef)
        wp2 = -(-b_coef + (b_coef**2 - 4*a_coef*c_coef)**(0.5))/(2*a_coef)
        
        #print("wz:", file=self.output_stream)
        #print(wz, file=self.output_stream)

        #print("wp1:", file=self.output_stream)
        #print(wp1, file=self.output_stream)
        
        #print("wp2:", file=self.output_stream)
        #print(wp2, file=self.output_stream)
        
        
        if wp2 < wp1:
            aux = wp2
            wp2 = wp1
            wp1 = aux
        
        # Constantes para la equacion obtenidas a partir de los ceros y polos
        A = wz/(wp1*wp2)
        B = (wz - wp1)/(wp1*(wp1 - wp2))
        D = (wz - wp2)/(wp2*(wp2 - wp1))
        
        Ipi = ((self.Vdd)/(Rd*delta_t**2))*(A*delta_t + (B/wp1)*(1 - euler**(-wp1*delta_t)) + (D/wp2)*(1 - euler**(-wp2*delta_t)))
        
        Iceff = ((self.Vdd)/(Rd*delta_t**2))*(Rd*CL*delta_t - (Rd*CL)**2*(1 - euler**(-delta_t/(Rd*CL))))
        
        return Iceff - Ipi
        
    def derivada_i_promedio_newton_raphson(self, CL, delta_t, Rd, C1, R, C2):
        return ((self.Vdd)/(Rd*delta_t**2))*(Rd*delta_t - 2*(Rd**2)*CL*(1 - euler**(-delta_t/(Rd*CL))) + delta_t*Rd*euler**(-delta_t/(Rd*CL)))
        
    def buscar_en_tabla(self, tabla_timing, CL, Tau_in, es_rise_time):

        err_rel_CL = CL
        err_rel_tau = Tau_in
        
        indice_CL_elegido = 0
        tau_por_CL_determinado = False
        tau_por_CL = 0
        tau_anterior = 0
        CL_elegido = tabla_timing[0][0]
        
        # Determinar la cantidad de variaciones de Tau por cada valor de CL que existen en la tabla
        for i in range(len(tabla_timing)):
            if not tau_por_CL_determinado:
                row = tabla_timing[i]
                if (row[1] > tau_anterior):
                    tau_por_CL = tau_por_CL + 1
                    tau_anterior = row[1]
                else:
                    tau_por_CL_determinado = True
        

        for i in range(1, len(tabla_timing), tau_por_CL):
            row = tabla_timing[i]
            err_rel_sig = (row[0] - CL)
            if err_rel_sig < 0: err_rel_sig = -err_rel_sig
            if err_rel_sig < err_rel_CL:
                err_rel_CL = err_rel_sig
                CL_elegido = row[0]
                indice_CL_elegido = i
            
        fila_elegida = tabla_timing[indice_CL_elegido]      
        for i in range(len(tabla_timing)):
            row = tabla_timing[i]
            if ((i >= indice_CL_elegido) and (i <= (indice_CL_elegido + tau_por_CL))):
                err_rel_sig = (row[1] - Tau_in)
                if err_rel_sig < 0: err_rel_sig = -err_rel_sig
                if err_rel_sig < err_rel_tau:
                    err_rel_tau = err_rel_sig
                    fila_elegida = row
        
        if (es_rise_time):
            t_50 = -(fila_elegida[2]/2.2)*ln(0.5)
            t_20 = -(fila_elegida[2]/2.2)*ln(0.8)
            t_delay = fila_elegida[5] # Si es un flanco ascendente, el delay es el valor t_LH de la tabla
        else:
            t_50 = -(fila_elegida[3]/2.2)*ln(0.5)
            t_20 = -(fila_elegida[3]/2.2)*ln(0.2)
            t_delay = fila_elegida[4] # Si es un flanco descendente, el delay es el valor t_HL de la tabla            
        

        return [t_50, t_20, t_delay]
