import pathlib
import device


class Vsource():

    def __init__(self, table_path: pathlib.Path = None):
        self.table_path = table_path

    def get_output_slew(self) -> float:
        return 23
