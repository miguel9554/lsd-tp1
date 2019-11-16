from subprocess import call


class Simulation:

    DEFAULT_SCRIPT_FILENAME = 'script.nutmeg'

    def __init__(self, step, end_time, circuit, filename=DEFAULT_SCRIPT_FILENAME):
        self.step = step
        self.end_time = end_time
        self.circuit = circuit
        self.filename = filename

    def generate_file(self, results_filename):
        with open(self.filename, 'wb') as fp:
            fp.write('\n.control\nsource {circuit_filename}\n'.format(circuit_filename=self.circuit.filename).encode(
                'ascii'))
            # fp.write('\nset noprintheader\nset noprintindex\nset nobreak\n'.encode('ascii'))
            fp.write('tran {timestep} {end_time}\n'.format(timestep=self.step, end_time=self.end_time).encode('ascii'))
            fp.write('print v(1) v({last_node}) > {results_filename}\n'.format(last_node=self.circuit.N + 1,
                                                                               results_filename=results_filename).encode(
                'ascii'))
            fp.write('.endc\n.end\n'.encode('ascii'))

    def run(self, results_filename):
        self.circuit.generate_file()
        self.generate_file(results_filename)
        call(["spiceopus", "-c", "-b", self.filename])
