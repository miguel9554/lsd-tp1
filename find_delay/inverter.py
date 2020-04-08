import pathlib
import device
from Estimador import Estimador
from line import Line


class Inverter(device.Device):

    def __init__(self, c_in, vdd, error_threshold, table_path: pathlib.Path = None):
        self.table_path = table_path
        self.c_in = c_in # Esta capacidad es de 3.1fF
        self.vdd = vdd
        self.error_threshold = error_threshold 
        
        
    def get_delay(self, input_slew: float, connected_device, rising_edge : bool) -> float:
        if not ((hasattr(self, "delay_rise") and rising_edge) or (hasattr(self, "delay_fall") and not rising_edge)):
            estimador = Estimador(connected_device, input_slew/0.69, self.vdd, self.table_path, self.error_threshold)
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

    def get_output_slew(self, input_slew: float, load) -> float:
        if not ((hasattr(self, "slew_rise") and rising_edge) or (hasattr(self, "slew_fall") and not rising_edge)):
            estimador = Estimador(connected_device.pi_model, input_slew, self.vdd, self.table_path, self.error_threshold)
            if slope:
                [self.load_ceff, self.slew_rise, self.delay_rise] = estimador.estimar_retardo_rise()
                return self.slew_rise
            else:
                [self.load_ceff, self.slew_fall, self.delay_fall] = estimador.estimar_retardo_fall()
                return self.slew_fall
        
        if slope:
            return self.slew_rise
        else:
            return self.slew_fall
