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

#############################

# Parametros del objeto:
#
# --> Vdd: tension de alimentacion de todo el circuito
#
# --> Tau_in: constante de tiempo del flanco de entrada (para el inversor)
#         o del clock (para el flip-flop)
#
# --> tabla_fall/tabla_rise: string con el nombre del archivo donde se encuentra almacenada 
#            la tabla del inversor o del FF
#
# --> modelo_pi: arreglo con los componentes del modelo pi [R, C1, C2]
# 
# --> umbral_err: condicion de corvergencia del algoritmo. Es un error relativo expresado
#                 en forma no porcentual. Se aplica al parametro t_50 
#                 (tiempo entre que comienza la transicion hasta que se alcanza Vdd/2). 
#                 Por ejemplo: umbral_err = 0.001 para considerar que hubo
#                 convergencia cuando la diferencia entre el resultado de una iteración (N) y la precendente (N-1) es menor
#                 al 0.1% del valor de la iteracion N-1


class Estimador:

    def __init__(self, modelo_pi, Tau_in, Vdd, nombre_tabla_timing, umbral_err):
        
        [self.R, self.C1, self.C2] = modelo_pi
        
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
            

    def estimar_retardo_rise(self):
            
        ## Obtener estimacion de Rd en base a la capacidad y retardos de entrada
        ## mas altos posibles para el inversor o FF que va a ser el "driver" de la linea
        CL = self.tabla_timing[-1][0]
        t_90 = -(self.tabla_timing[-1][2]/2.2)*ln(0.1); # Extraccion de tiempos de interes a partir del RISE TIME
        t_50 = -(self.tabla_timing[-1][2]/2.2)*ln(0.5); # Extraccion de tiempos de interes a partir del RISE TIME
        t_20 = -(self.tabla_timing[-1][2]/2.2)*ln(0.8); # Extraccion de tiempos de interes a partir del RISE TIME
        Rd = (t_90 - t_50)/(CL*ln(5));
        
        ## Obtener semilla de Delta_t y t_0
        delta_t = t_90
        t0 = t_90/10
        
        ## Comenzar a iterar hasta llegar al umbral
        error_relativo = 1;
        print("\nComienza el bucle\n")
        while error_relativo > self.umbral_err:
            print("Siguiente iteracion")
            # Resolver la capacidad equivalente a partir de
            # igualar las corrientes del modelo pi y del modelo
            # RC equivalente
            CL = newton_raphson(self.i_promedio_newton_raphson, CL, self.derivada_i_promedio_newton_raphson, args=[delta_t, Rd, self.C1, self.R, self.C2], tol=0.05E-15, maxiter=10);
            
            print("Termino NR para corrientes")

            # Buscar en la tabla del FF o del inversor
            # [t_50, t_20] = buscar_en_tabla_FF(CL);
            [t_50_sig, t_20, t_LH] = self.buscar_en_tabla(self.tabla_timing, CL, self.Tau_in, False);
            
            
            # Obtener la siguiente iteracion de t0 y delta_t
            t0 = newton_raphson(self.v_o_newton_raphson, t0, self.derivada_v_o_newton_raphson, args=[CL, t_50_sig + self.t_50_in, t_20 + self.t_50_in, Rd, 0.5*self.Vdd, 0.8*self.Vdd]);
            
            print("Termino NR para tension")
            
            delta_t = self.delta_t_vs_CL_y_t0(CL, t0, t_50_sig, 0.5*self.Vdd, Rd);
            
            print("Calcular error relativo:")
            error_relativo = (t_50_sig - t_50)/t_50
            t_50 = t_50_sig
            if error_relativo < 0:
                error_relativo = -error_relativo
            
            print(error_relativo)
            print('\n')
        # Fin de la iteracion
        #####################
        
        print("Resultados:")
        print("CL: ")
        print(CL)
        print("t_50: ")    
        print(t_50)
        
        return [CL, t_50, t_LH]
        

    def estimar_retardo_fall(self):
            
        ## Obtener estimacion de Rd en base a la capacidad y retardos de entrada
        ## mas altos posibles para el inversor o FF que va a ser el "driver" de la linea
        CL = self.tabla_timing[-1][0]
        t_90 = -(self.tabla_timing[-1][3]/2.2)*ln(0.9); # Extraccion de tiempos de interes a partir del RISE TIME
        t_50 = -(self.tabla_timing[-1][3]/2.2)*ln(0.5); # Extraccion de tiempos de interes a partir del RISE TIME
        t_20 = -(self.tabla_timing[-1][3]/2.2)*ln(0.2); # Extraccion de tiempos de interes a partir del RISE TIME
        Rd = (t_50 - t_90)/(CL*ln(5));
        
        ## Obtener semilla de Delta_t y t_0
        delta_t = t_90
        t0 = t_90/10
        
        ## Comenzar a iterar hasta llegar al umbral
        error_relativo = 1;
        
        ## Comenzar a iterar hasta llegar al umbral
        error_relativo = 1;

        print("\nComienza el bucle\n")
        while error_relativo > self.umbral_err:
            print("Siguiente iteracion")
            
            # Resolver la capacidad equivalente a partir de
            # igualar las corrientes del modelo pi y del modelo
            # RC equivalente
            CL = newton_raphson(self.i_promedio_newton_raphson, CL, self.derivada_i_promedio_newton_raphson, args=[delta_t, Rd, self.C1, self.R, self.C2], tol=0.05E-15, maxiter=10);
            
            print("Termino NR para corrientes")

            # Buscar en la tabla del FF o del inversor
            # [t_50, t_20] = buscar_en_tabla_FF(CL);
            [t_50_sig, t_20, t_HL] = self.buscar_en_tabla(self.tabla_timing, CL, self.Tau_in, True);
            
            # Obtener la siguiente iteracion de t0 y delta_t
            sol = newton_raphson_multivariable(self.v_o_newton_raphson_fall_time, [t0, delta_t], jac=self.jacobiano_v_o_newton_raphson, args=(CL, t_50_sig + self.t_50_in, t_20 + self.t_50_in, Rd, 0.5*self.Vdd, 0.2*self.Vdd));
            [t0, delta_t] = sol.x
            
            print("Termino NR para tension")
            
            print("Calcular error relativo:")
            error_relativo = (t_50_sig - t_50)/t_50
            t_50 = t_50_sig
            if error_relativo < 0:
                error_relativo = -error_relativo
            
            print(error_relativo)
            print('\n')
        # Fin de la iteracion
        #####################
        
        print("Resultados:")
        print("CL: ")
        print(CL)
        print("t_50: ")    
        print(t_50)
        
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
        
        #print("wz:")
        #print(wz)

        #print("wp1:")
        #print(wp1)
        
        #print("wp2:")
        #print(wp2)
        
        
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
        err_rel_CL = 1
        err_rel_tau = 1
        
        indice_CL_elegido = 0
        tau_por_CL_determinado = False
        tau_por_CL = 0
        tau_anterior = 0
        CL_elegido = tabla_timing[0][0]
        for i in range(len(tabla_timing)):
            row = tabla_timing[i]
            err_rel_sig = (row[0] - CL)/CL
            if err_rel_sig < 0: err_rel_sig = -err_rel_sig
            if err_rel_sig < err_rel_CL:
                err_rel_CL = err_rel_sig
                CL_elegido = row[0]
                indice_CL_elegido = i
            
            if not tau_por_CL_determinado:
                if (row[1] > tau_anterior):
                    tau_por_CL = tau_por_CL + 1
                    tau_anterior = row[1]
                else:
                    tau_por_CL_determinado = True
        
        fila_elegida = tabla_timing[0]        
        for i in range(len(tabla_timing)):
            row = tabla_timing[i]
            if ((i >= indice_CL_elegido) or (i <= (indice_CL_elegido + tau_por_CL))):
                err_rel_sig = (row[1] - Tau_in)/Tau_in
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
