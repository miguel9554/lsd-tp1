from Estimador import Estimador
Vdd = 2.5
Tau_in = 250E-12
tabla_inversor = "tabla_datos_inversor.txt"
tabla_ffd = "tabla_datos_FFD.txt"
tau_por_CL = 42
modelo_pi = [5,5E-15, 5E-15]
umbral_err = 0.001
estimador1 = Estimador(modelo_pi, Tau_in, Vdd, tabla_inversor, umbral_err)
estimador1.estimar_retardo_rise()