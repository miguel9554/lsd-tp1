class Circuit:

    DEFAULT_CIRCUIT_FILENAME = 'circuit.cir'

    def __init__(self, r, c, n=1, filename=DEFAULT_CIRCUIT_FILENAME):
        self.R = r
        self.C = c
        self.N = n
        self.filename = filename

    def generate_file(self):
        with open(self.filename, 'wb') as fp:
            fp.write('\n'.encode('ascii'))
            for n in [x+1 for x in range(self.N)]:
                fp.write('{Rname} {node1} {node2} {Rvalue}\n'.format(
                    Rname='R' + str(n), node1=str(n), node2=str(n + 1), Rvalue=self.R/self.N).encode('ascii'))
                fp.write('{Cname} {node1} {node2} {Cvalue}\n'.format(
                    Cname='C' + str(n), node1=str(n+1), node2='0', Cvalue=self.C/self.N).encode('ascii'))
            fp.write('\nvp 1 0 PULSE {initial_value} {pulsed_value} {delay_time} {rise_time} {fall_time} '
                     '{pulse_width} {period}\n\n'.format(initial_value=0, pulsed_value=2.5, delay_time=0, rise_time=0,
                                                         fall_time=0, pulse_width=100, period=100).encode('ascii'))
            fp.write('.end\n'.encode('ascii'))
