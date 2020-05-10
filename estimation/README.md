## Carpeta Estimation

Los archivos de código de la carpeta son los siguientes:

- `circuit.py`: clase que representa a un circuito compuesto por líneas, inversores y flip-flops. Es utilizada por `compare_delays.py` para crear el circuito cuyo retardo será estimado y luego simulado. 
- `tabledevice.py`: clase que describe a los inversores y flip-flops.
- `Estimador.py`: clase que representa al método para estimar los delays de salida de los flip-flops e inversores descrito  en el libro "Timing".
- `source.py`: clase que representa una fuente de alimentación en el circuito.
- `null_load.py`: clase que representa una carga nula colocada a la salida de un inversor o flip-flop.

Los archivos `.txt`:

- `tabla_datos_inversor`: tabla del inversor utilizada en la estimación de los retardos.
- `tabla_datos_FFD`:  tabla del flip-flop empleada en la estimación de los retardos. 

Las carpetas son:

- wire: contiene las clases que representan a las líneas del circuito.
- hallar_tabla_FFD: contiene el código que permite hallar la tabla de un flip-flop. Allí se encuentran las simulaciones correspondientes de Spice Opus.
- hallar_tabla_inversor: contiene el código que encuentra la tabla de un inversor. Al igual que "hallar_tabla_FFD", también contiene las simulaciones necesarias.
- test_capacidad_entrada_FF: código con la simulación para determinar la capacidad de entrada de un flip-flop.
- test_capacidad_entrada_inversor: código con la simulación para determinar la capacidad de entrada de un inversor.

