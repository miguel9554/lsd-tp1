import pathlib
from device import Device
from typing import List

class vsource(Device):
    def __init__(self, output_slew: float):
        self.output_slew: float = output_slew
         
    def set_output_device(self, device: Device) -> None:
        pass

    def set_connected_devices(self, devices: List[Device]) -> None:
        pass


    def get_output_slew(self) -> float:
        return self.output_slew

    def get_delay(self, input_slew: float, rising_edge: bool) -> float:
        return 0

