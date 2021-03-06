from Circuit import Circuit
import Utils
from subprocess import call
import os


class Simulation:

    DEFAULT_SCRIPT_FILENAME = 'script.nutmeg'

    def __init__(self, step, end_time, circuit: Circuit, uid: str, filename=DEFAULT_SCRIPT_FILENAME):
        self.step = step
        self.end_time = end_time
        self.circuit = circuit
        self.filename = uid + '.' + filename

    def generate_file(self, results_filename):
        with open(self.filename, 'wb') as fp:
            fp.write('\n.control\nsource {circuit_filename}\n'.format(circuit_filename=self.circuit.filename).encode(
                'ascii'))
            # fp.write('\nset noprintheader\nset noprintindex\nset nobreak\n'.encode('ascii'))
            fp.write('tran {timestep} {end_time}\n'.format(timestep=Utils.float_to_string(self.step), end_time=Utils.float_to_string(self.end_time)).encode('ascii'))
            fp.write('print v(1) v({last_node}) > {results_filename}\n'.format(last_node=self.circuit.N + 1,
                                                                               results_filename=results_filename).encode(
                'ascii'))
            fp.write('.endc\n.end\n'.encode('ascii'))

    def run(self, results_filename: str):
        self.circuit.generate_file()
        self.generate_file(results_filename)
        call(["spiceopus", "-c", "-b", self.filename])
    
    def clean(self):
        os.remove(self.filename)
