from wire import Utils
from wire.Source import Source

class Circuit:

    DEFAULT_CIRCUIT_FILENAME = 'circuit.cir'

    def __init__(self, r, c, source: Source, n=1, filename=DEFAULT_CIRCUIT_FILENAME):
        self.R = r
        self.C = c
        self.N = n
        self.Source = source
        self.filename = filename

    def generate_file(self):
        with open(self.filename, 'wb') as fp:
            fp.write('\n'.encode('ascii'))
            for n in [x+1 for x in range(self.N)]:
                fp.write('{Rname} {node1} {node2} {Rvalue}\n'.format(
                    Rname='R' + str(n), node1=str(n), node2=str(n + 1), Rvalue=Utils.float_to_string(self.R/self.N)).encode('ascii'))
                fp.write('{Cname} {node1} {node2} {Cvalue}\n'.format(
                    Cname='C' + str(n), node1=str(n+1), node2='0', Cvalue=Utils.float_to_string(self.C/self.N)).encode('ascii'))
            fp.write(self.Source.get_spiceopus_definition().encode('ascii'))
            fp.write('\n\n.end\n'.encode('ascii'))
