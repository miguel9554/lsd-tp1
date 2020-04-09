import pathlib
import device


class Line(device.Device):

    def __init__(self, table_path: pathlib.Path = None):
        self.table_path = table_path

    def get_delay(self, input_slew: float, load: float) -> float:
        return 55

    def get_input_capacitance(self) -> float:
        return 130

    def get_output_slew(self, input_slew: float, load: float) -> float:
        return 40