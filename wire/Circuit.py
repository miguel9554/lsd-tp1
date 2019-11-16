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
                    Rname='R' + str(n), node1=str(n), node2=str(n + 1), Rvalue=self.R).encode('ascii'))
                fp.write('{Cname} {node1} {node2} {Cvalue}\n'.format(
                    Cname='C' + str(n), node1=str(n+1), node2='0', Cvalue=self.C).encode('ascii'))
            fp.write('\nvp 1 0 PULSE 0 2.5 0 0 0 1 10\n\n'.encode('ascii'))
            fp.write('.end\n'.encode('ascii'))
