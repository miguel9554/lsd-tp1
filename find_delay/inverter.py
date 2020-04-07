import pathlib
import device


class Inverter(device.Device):

    def __init__(self, table_path: pathlib.Path = None):
        self.table_path = table_path

    def get_delay(self) -> float:
        return 80

    def get_input_capacitance(self) -> float:
        return 90

    def get_output_slew(self) -> float:
        return 10
