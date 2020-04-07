import pathlib
from typing import List
import matplotlib.pyplot as plt
import device


class FFD(device.Device):
    def __init__(self, table_path: pathlib.Path = None):
        self.table_path = table_path

    def get_delay(self) -> float:
        return 60

    def get_input_capacitance(self) -> float:
        return 40

    def get_output_slew(self) -> float:
        return 30

def get_table(filepath: pathlib.Path) \
    -> (List[float], List[float], List[float],\
        List[float], List[float], List[float]):
    """ Devuelve los valores de la tabla que se
    encuentra en filepath """
    load_capacitances = []
    tau_in = []
    rise_time = []
    fall_time = []
    clk2q_hl = []
    clk2q_lh = []
    with open(filepath) as fhandler:
        in_first_line = True
        for line in fhandler:
            if in_first_line:
                in_first_line = False
            else:
                values = line.rstrip('\n').split('\t')
                load_capacitances.append(float(values[0]))
                tau_in.append(float(values[1]))
                rise_time.append(float(values[2]))
                fall_time.append(float(values[3]))
                clk2q_hl.append(float(values[4]))
                clk2q_lh.append(float(values[5]))
    return load_capacitances, tau_in, rise_time, fall_time, \
            clk2q_hl, clk2q_lh

def main():
    """ Testeo del modulo """
    filepath = pathlib.Path(__file__).absolute().parent.parent \
            / 'hallar_tabla_FFD' / 'tabla_datos_FFD.txt'
    capacitances = get_table(filepath)[0]
    plt.hist(capacitances, bins=100)
    plt.show()

if __name__ == "__main__":
    main()
