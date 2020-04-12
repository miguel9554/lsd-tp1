from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

class Device(ABC):
    """ Clasa abstracta para los elementos circuitales

    Todos los elementos del circuito deben heredar de
    esta clase e implementar los tres métodos
    """

    @abstractmethod
    def set_connected_devices(self, devices: List[Device]) -> None:
        """ Configura las cargas del dispositivo """

    @abstractmethod
    def get_delay(self, input_slew: float, rising_edge: bool) -> float:
        """ Obtiene el retardo del dispositivo """

    @abstractmethod
    def get_output_slew(self, input_slew: float, rising_edge: bool) -> float:
        """ Obtiene el slew de salida del dispositivo """

    @abstractmethod
    def set_output_device(self, device: Device) -> None:
        """ Configura cual será el dispositivo de salida """
