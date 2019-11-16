from subprocess import call
import re
import numpy as np
import matplotlib.pyplot as plt
import os


class Results:

    def __init__(self, time, vin, vout):
        self.time = time
        self.vin = vin
        self.vout = vout

    def plot(self, time_scale_factor=1):
        plt.plot(self.time * time_scale_factor, self.vin, self.time * time_scale_factor, self.vout)
        plt.ylabel('Tensión [V]')
        plt.xlabel('Tiempo [s]')
        plt.show()


class Circuit:

    CIRCUIT_FILENAME = 'circuit.cir'
    SCRIPT_FILENAME = 'script.nutmeg'
    RESULTS_FILENAME = 'results.dat'

    def __init__(self, l, r, c, n=1):
        self.R = r
        self.C = c
        self.length = l
        self.N = n

    def calculate(self):
        self.generate_files()
        self.run_simulation()
        self.process_results()

    def run_simulation(self):
        print(os.listdir(os.getcwd()))
        call(["spiceopus", "-c", "-b", self.SCRIPT_FILENAME])

    def process_results(self):
        regex = re.compile(r"^(?P<index>\d+)"
                           r"\s+"
                           r"(?P<time>\d+.\d+e[+|-]\d+)"
                           r"\s+"
                           r"(?P<vin>\d+.\d+e[+|-]\d+)"
                           r"\s+"
                           r"(?P<vout>\d+.\d+e[+|-]\d+)"
                           r"\s+$", re.UNICODE | re.VERBOSE)

        time = []
        vin = []
        vout = []
        with open(self.RESULTS_FILENAME, 'r') as fp:
            for line in fp:
                m = regex.match(line)
                if m:
                    time.append(float(m.group('time')))
                    vin.append(float(m.group('vin')))
                    vout.append(float(m.group('vout')))

        return Results(np.array(time), np.array(vin), np.array(vout))

    def generate_files(self):
        with open(self.CIRCUIT_FILENAME, 'wb') as fp:
            fp.write('\n'.encode('ascii'))
            for n in [x+1 for x in range(self.N)]:
                fp.write('{Rname} {node1} {node2} {Rvalue}\n'.format(
                    Rname='R' + str(n), node1=str(n), node2=str(n + 1), Rvalue=self.R).encode('ascii'))
                fp.write('{Cname} {node1} {node2} {Cvalue}\n'.format(
                    Cname='C' + str(n), node1=str(n+1), node2='0', Cvalue=self.C).encode('ascii'))
            fp.write('\nvp 1 0 PULSE 0 2.5 0 0 0 1 10\n\n'.encode('ascii'))
            fp.write('.end\n'.encode('ascii'))
        with open(self.SCRIPT_FILENAME, 'wb') as fp:
            fp.write('\n.control\nsource {circuit_filename}\n'.format(circuit_filename=self.CIRCUIT_FILENAME).encode('ascii'))
            # fp.write('\nset noprintheader\nset noprintindex\nset nobreak\n'.encode('ascii'))
            fp.write('tran {timestep} {end_time}\n'.format(timestep='1u', end_time='20m').encode('ascii'))
            fp.write('print v(1) v({last_node}) > {results_filename}\n'.format(last_node=self.N+1, results_filename=self.RESULTS_FILENAME).encode('ascii'))
            fp.write('.endc\n.end\n'.encode('ascii'))


N = 3
circuit = Circuit(10e-6, 10e3, 1e-6, N)
circuit.generate_files()
circuit.run_simulation()
results = circuit.process_results()
print(results.time)
results.plot()
T = []
N_range = [x+1 for x in range(3)]
for N in N_range:
    circuit.N = N
    T.append(circuit.calculate())
    exit()

plt.plot(N_range, T)
plt.ylabel('Tiempo de propagación [s]')
plt.xlabel('Cuadripolos')
plt.show()
