import pathlib
from typing import List
from Estimador import Estimador
from device import Device

class TableDevice(Device):

    def __init__(self, table_path: pathlib.Path, c_in=3.1e-15, vdd=2.5, \
            error_threshold=1e-3):
        self.table_path = table_path
        self.c_in = c_in # Esta capacidad es de 3.1fF
        self.vdd = vdd
        self.error_threshold = error_threshold 
        self.connected_device = None
        self.output_node = None # TODO: chequear si esta bien inicializar esta variable asi
        self.simulated_slew = 0
        self.simulated_delay = 0
        
    def set_connected_devices(self, devices: List[Device]) -> None:
        """ Configura la carga del circuito """
        if len(devices) == 1:
            self.connected_device = devices[0]
        else:
            self.connected_device = None

    def get_delay(self, input_slew: float, rising_edge : bool) -> float:
        if not ((hasattr(self, "delay_rise") and rising_edge) or (hasattr(self, "delay_fall") and not rising_edge)):
            estimador = Estimador(self.connected_device.get_pi_model(), input_slew/0.69, self.vdd, self.table_path, self.error_threshold)        
            
            if self.connected_device.__class__.__name__ == 'null_load':
                aux_slew, _, aux_delay = estimador.buscar_en_tabla(estimador.tabla_timing, 0, estimador.Tau_in, rising_edge)
                if rising_edge:
                    self.slew_rise = aux_slew
                    self.delay_rise = aux_delay
                    return self.delay_rise
                else:
                    self.slew_fall = aux_slew
                    self.delay_fall = aux_delay
                    return self.delay_fall
            else:
                if rising_edge:
                    [self.load_ceff, self.slew_rise, self.delay_rise] = estimador.estimar_retardo_rise()
                    return self.delay_rise
                else:
                    [self.load_ceff, self.slew_fall, self.delay_fall] = estimador.estimar_retardo_fall()
                    return self.delay_fall
        
        if rising_edge:
            return self.delay_rise
        else:
            return self.delay_fall
        

    def get_input_capacitance(self) -> float:
        return self.c_in

    def set_output_device(self, device: Device) -> None:
        pass

    def get_output_slew(self, input_slew: float, rising_edge: bool) -> float:
        estimador = Estimador(self.connected_device.get_pi_model(), input_slew, \
                    self.vdd, self.table_path, self.error_threshold)
                    
        if self.connected_device.__class__.__name__ == 'null_load':
            aux_slew, _, aux_delay = estimador.buscar_en_tabla(estimador.tabla_timing, 0, estimador.Tau_in, rising_edge)
            if rising_edge:
                self.slew_rise = aux_slew
                self.delay_rise = aux_delay
                return self.slew_rise
            else:
                self.slew_fall = aux_slew
                self.delay_fall = aux_delay   
                return self.slew_fall
        else:
            if rising_edge:
                _, slew, _ = estimador.estimar_retardo_rise()
            else:
                _, slew, _ = estimador.estimar_retardo_fall()
            return slew  

    def get_simulated_delay(self) -> float:
        return self.simulated_delay

    def get_simulated_slew(self) -> float:
        return self.simulated_slew
        
class Inverter(TableDevice):

    def __init__(self, table_path: pathlib.Path = 'tabla_datos_inversor.txt', c_in=3.1e-15, vdd=2.5, \
            error_threshold=1e-3):
        super(Inverter, self).__init__(table_path, c_in, vdd, error_threshold)

class FFD(TableDevice):

    def __init__(self, table_path: pathlib.Path = 'tabla_datos_FFD.txt', c_in=3.1e-15, vdd=2.5, \
            error_threshold=1e-3):
        super(FFD, self).__init__(table_path, c_in, vdd, error_threshold)
