# Trabajo Práctico de 86.42 Laboratorio de Sistemas Digitales - FIUBA


El objetivo del trabajo es estimar el retardo de un circuito digital y compararlo con una simulación. Se siguieron los modelos de estimación dados en el libro Timing de Sachin Sapatnekar. Las simulaciones se realizaron con SPICE OPUS en base a modelos BSIM3 de los transistores. Las lineas se modelaron como lineas RC.

## Funcionamiento

La estimación del retardo de una topología circuital dada y su comparación con la simulación se realiza ejecutando el archivo`compare_delays.py`. En este mismo archivo  se encuentra descrita la topología cuyo retardo se desea estimar por métodos numéricos y, a su vez, contrastar con una simulación.

## Descripción de la estructura del repositorio

- estimation: se encuentra el código dedicado a la estimación del retardo del circuito, así como las clases que representan a las líneas, inversores y flip-flops. Más información se encuentra detalla en el archivo README.md de la correspondiente carpeta.
- simulation: allí se halla el código dedicado a armar y realizar la simulación del circuito descrito en `compare_delays.py` .
- caracteristicas_proceso:  contiene los modelos de Spice de los inversores y flip-flops. También incluye las características de las líneas.



## Armado de un circuito para calcular su retardo

Para ver el ejemplo del circuito armado por default ir al archivo `compare_delays.py` y ver allí la sección "Circuito".

Todo árbol circuital comienza con la siguiente declaración:

`circuit_tree = anytree.Node(name='source', device=vsource(input_slew))`

Esta crea el árbol y le indica el slew de la fuente de alimentación, dado por `input_slew`.  Se entiende por "slew " al tiempo que le toma a la señal ir desde su valor inicial a Vdd/2.

De momento, el algoritmo solamente acepta que el primer componente del árbol sea un flip-flop. De este modo, el "generador de entrada" es la señal de reloj del flip-flop, cuyo flanco ascendente (con un slew dado por `input_slew`)  dispara la copia del valor de la entrada D a la salida Q.

Dado que el primer componente solamente puede ser un FF, a continuación de la línea que instancia el circuito se debe colorar:

`ffd1 = anytree.Node(name='ffd1', parent=circuit_tree, device=FFD())`

Que crea un nodo del circuito identificado como "ffd1" cuya padre en el árbol es la fuente de alimentación, ya que se encuentra conectada a su entrada.

Entre cada inversor y FF debe conectarse necesariamente una línea, que es identificada por:

`line11 = anytree.Node(name='line11', parent=inv11, device=RC_line( \
        R, C, sections))`

Donde se ve que la línea se encuentra conectada a la salida del inversor ya que este es su padre. Los campos R y C identifican la resistencia y capacidad total de la línea y `sections` representa la cantidad de secciones en la que se la dividirá para representarla mediante una serie de capacidades y resistencias distribuidas a la hora de llevar a cabo la estimación del retardo y su simulación.

Para crear una red que comienza en un flip-flop, luego es seguida por una línea y termina en otro flip-flop, se puede hacer:

`circuit_tree = anytree.Node(name='source', device=vsource(input_slew))`

`ffd1 = anytree.Node(name='ffd1', parent=circuit_tree, device=FFD())`

`line11 = anytree.Node(name='line11', parent=ffd1 , device=RC_line(R, L, sections))`

`ffd11 = anytree.Node(name='ffd11', parent=line11, device=FFD())`

Las líneas pueden terminar en un flip-flop o un inversor. Sin embargo, el delay del último componente de la red no será tenido en cuenta en el delay total del circuito.

También pueden crearse puntos de bifurcación del circuito utilizando un nodo "tree_line", como el siguiente:

`tree_line = anytree.Node(name='tree_line', parent=inv1, \
        device=RC_tree(RC_line(R1, C1, sections), RC_line(R2, C2, sections), \
        RC_line(R3, C3, sections)))`

Se observa que esta línea que se bifurca está conectada a la salida del inversor "inv11". El primer tramo de la línea antes de la bifurcación es el primer parámetro de RC_Tree() y tienen R = R1 y L = C1. Luego, la línea se bifurca en dos tramos de R = R2 y C = C2, y R = R3 y C = C3 respectivamente. Un ejemplo de un circuito con una bifurcación es:

`circuit_tree = anytree.Node(name='source', device=vsource(input_slew))`

`ffd1 = anytree.Node(name='ffd1', parent=circuit_tree, device=FFD())`

`tree_line = anytree.Node(name='tree_line', parent=inv1, \
        device=RC_tree(RC_line(R1, C1, sections), RC_line(R2, C2, sections), \
        RC_line(R3, C3, sections)))`

`ffd2 = anytree.Node(name='ffd11', parent=tree_line, device=FFD())`

`ffd3 = anytree.Node(name='ffd11', parent=tree_line, device=FFD())`

Donde ffd2 estará conectada a la línea de R = R2 y ffd3 a la línea de R=R3.

Cuando existe una bifurcación, debe elegirse el delay de que rama se quiere calcular. Para ello debe completarse la siguiente línea en `compare_delays.py`:

`delay, simulated_delay = circuit.find_delay(ffd2, True, True)`

Con el flip-flop final del circuito en cuya entrada quiere calcularse el delay con respecto al primer flip-flop. En el ejemplo anterior, se calculará el delay entre ffd1 y ffd2. Si se quiere el de ffd3:

`delay, simulated_delay = circuit.find_delay(ffd3, True, True)`



Por último, en el archivo `compare_delays.py` son de relevancia las siguientes variables:

- `vdd` : tensión de alimentación de todos los componentes del circuito.
- `c` : capacidad por micrómetro de largo de la línea (asumiendo un ancho de 1um).
- `r`: resistencia por micrómetro de largo de la línea (asumiendo un ancho de 1um).
- `sections`: número de secciones RC en las que se dividirá la línea para la estimación de su retardo y su simulación.
- `rising_edge:`el flanco de salida del primer FF del circuito será ascendente si esta variable es `true`. De otro modo, el flanco será descendente.

 