from abc import ABC, abstractmethod

class Device(ABC):
    """ Clasa abstracta para los elementos circuitales

    Todos los elementos del circuito deben heredar de
    esta clase e implementar los tres métodos
    """

    @abstractmethod
    def get_input_capacitance(self) -> float:
        pass

    @abstractmethod
    def get_delay(self, input_slew: float, load: float) -> float:
        pass

    @abstractmethod
    def get_output_slew(self, input_slew: float, load: float) -> float:
        pass
