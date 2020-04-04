import re
import numpy as np
import matplotlib.pyplot as plt
import os


class Results:

    DEFAULT_RESULTS_FILENAME = 'results.dat'

    def __init__(self, uid: str, time=None, vin=None, vout=None, filename=DEFAULT_RESULTS_FILENAME):
        self.filename = uid + '.' + filename
        self.time = np.array([]) if not time else time
        self.vin = np.array([]) if not vin else vin
        self.vout = np.array([]) if not vout else vout

    def process(self):
        regex = re.compile(r"^(?P<index>\d+)"
                           r"\s+"
                           r"(?P<time>\d+.\d+e[+|-]\d+)"
                           r"\s+"
                           r"(?P<vin>\d+.\d+e[+|-]\d+)"
                           r"\s+"
                           r"(?P<vout>\d+.\d+e[+|-]\d+)"
                           r"\s+$", re.UNICODE | re.VERBOSE)

        with open(self.filename, 'r') as fp:
            for line in fp:
                m = regex.match(line)
                if m:
                    self.time = np.append(self.time, [float(m.group('time'))])
                    self.vin = np.append(self.vin, [float(m.group('vin'))])
                    self.vout = np.append(self.vout, [float(m.group('vout'))])

    def plot(self, time_scale_factor=1):
        plt.plot(self.time * time_scale_factor, self.vin, self.time * time_scale_factor, self.vout)
        plt.ylabel('Tensión [V]')
        plt.xlabel('Tiempo [s]')
        plt.show()

    def get_rise_time(self):
        v_inf = np.max(self.vout)*0.1
        v_top = np.max(self.vout) * 0.9

        t_inf = self.time[np.max(np.nonzero(self.vout < v_inf))]
        t_top = self.time[np.min(np.nonzero(self.vout > v_top))]

        return t_top - t_inf
    
    def clean(self):
        os.remove(self.filename)

