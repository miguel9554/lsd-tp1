import pathlib
import device


class Vsource(device.Device):

    def __init__(self, table_path: pathlib.Path = None):
        self.table_path = table_path

    def get_delay(self) -> float:
        return None

    def get_input_capacitance(self) -> float:
        return None

    def get_output_slew(self) -> float:
        return 23
