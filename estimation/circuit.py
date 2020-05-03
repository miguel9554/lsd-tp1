import anytree
from tabledevice import Inverter
from null_load import null_load

class circuit:
    """" Representa al circuito del que se quiere analizar el retardo. """
    def __init__(self, tree: anytree.Node) -> None:
        self.tree: anytree.Node = tree
        self.configure_loads()

    def __str__(self):
        return str(anytree.RenderTree(self.tree))

    def configure_loads(self) -> None:
        """ Configura la carga de todos los elementos del circuito """

        # Conectamos la carga nula a cada elemento de salida
        for leave in self.tree.leaves:
            null_load_node = anytree.AnyNode(device=null_load())
            leave.children = [null_load_node]

        # Recorremos todos los nodos (salvo las cargas nulas) y
        # seteamos el dispositivo que los carga
        for node in anytree.PreOrderIter(self.tree, \
                filter_=lambda node: not node.is_leaf):
            node.device.set_connected_devices([child.device for child in node.children])

    def find_delay(self, output_node: anytree.Node, debug: bool = False) -> float:
        """ Calcula el delay saliendo por el nodo indicado """

        w = anytree.Walker()
        upward, common, downwards = w.walk(self.tree.root, output_node.children[0])

        last_slew = self.tree.root.device.get_output_slew()
        rising_edge = self.tree.root.device.get_rising_edge()

        total_delay = 0
        total_simulated_delay = 0

        for idx, node in enumerate(downwards[:-2]):
            node.device.set_output_device(downwards[idx+1])
            delay = node.device.get_delay(last_slew, rising_edge)
            simulated_delay = node.device.get_simulated_delay()
            last_slew = node.device.get_output_slew(last_slew, rising_edge)
            last_simulated_slew = node.device.get_simulated_slew()
            if isinstance(node.device, Inverter):
                rising_edge = not rising_edge
            if debug:
                #print(f"{node.name} tiene un delay de {delay:.2e} " \
                #    f"y un slew de {last_slew:.2e}")
                print(f"{node.name}: \n" \
                      f"Delay estimado: {delay:.2e} \n" \
                      f"Delay simulado: {simulated_delay:.2e} \n"
                      f"Slew estimado: {last_slew:.2e} \n" \
                      f"Slew simulado: {last_simulated_slew:.2e} \n")                        
            total_delay += delay
            total_simulated_delay += simulated_delay

        return [total_delay, total_simulated_delay]

