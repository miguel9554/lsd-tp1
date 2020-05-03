# Trabajo Práctico de 86.42 Laboratorio de Sistemas Digitales - FIUBA

El objetivo es estimar el retardo de un circuito digital y compararlo con una simulación. Se siguieron los modelos de estimación dados en el libro Timing de Sachin Sapatnekar. Las simulaciones se realizaron con SPICE OPUS en base a modelos BSIM3 de los transistores. Las lineas se modelaron como lineas RC.

## Funcionamiento

En el directorio `estimation` se encuentra todo lo referido a la estimación del retardo. Con la clase `circuit` se puede crear un circuito arbitrario compuesto por líneas y dispositivos cuyo retardo se estima con tablas, y calcular el delay en cualquiera de los nodos. Este circuito puede ser usado con la clase `simulation` para comparar la estimación con la simulación.

## Aclaraciones

Las carpetas “caracteristicas_proceso” y las carpeta “test…” tienen que estar una al lado de la otra dentro de la carpeta “simulaciones” para que funcione el código en python dentro de las carpetas “test….”. Esto es así porque los modelos de transistores que usa el “.cir”  (el circuito que corre spiceopus dentro de las carpetas “test...”)  están dentro de “caracteristicas_proceso”.