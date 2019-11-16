from subprocess import call  # Para ejecutar SpiceOpus desde Python
import re
import matplotlib.pyplot as plt
import numpy as np

regex = re.compile(r"^(?P<index>\d+)"
                   r"\s+"
                   r"(?P<time>\d+.\d+e[+|-]\d+)"
                   r"\s+"
                   r"(?P<vin>\d+.\d+e[+|-]\d+)"
                   r"\s+"
                   r"(?P<vout>\d+.\d+e[+|-]\d+)"
                   r"\s+$", re.UNICODE | re.VERBOSE)

nombre_simulacion = "script.nutmeg"

## Los parametros pasados al simulador representan lo siguiente:
# "-c" : ejecutar en modo consola
# "-b" : ejecutar en "modo batch", es decir, el simlador se cierra
#		 una vez que se termino con la simulacion
call(["spiceopus", "-c", "-b", nombre_simulacion])

time = []
vin = []
vout = []

with open('results.dat') as fp:
    for line in fp:
        m = regex.match(line)
        if m:
            time.append(float(m.group('time')))
            vin.append(float(m.group('vin')))
            vout.append(float(m.group('vout')))

time = np.array(time)
vin = np.array(vin)
vout = np.array(vout)

plt.plot(time*1000, vin, time*1000, vout)
plt.ylabel('Tensión [V]')
plt.xlabel('Tiempo [ms]')
plt.show()

