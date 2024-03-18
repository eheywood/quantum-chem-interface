## QVM provided by Cirq
import cirq
import cirq_google
import qsimcirq
import numpy as np
from .Circuit import Circuit
class QVM:

    processor_id = None
    noisy = None

    noise_property = None
    noise_model = None
    simulator = None
    device = None
    engine = None
    
    def __init__(self, processor = 'weber', noisy=False ) -> None:
        """ Constructor for the Quantum Virtual Machine Class. 

        :param processor: The type of google (cirq) processor being simulated, defaults to 'weber'
        :type processor: str, optional
        :param noisy: True if the QVM will simulate noise in the machine, False if there is no noise model being set, defaults to False
        :type noisy: bool, optional
        """
        
        self.processor_id = processor
        self.noisy = noisy

        self.construct_QVM()
    

    def toggle_noise(self):
        """ Toggles the noisy boolean. Turns the noise in the QVM on or off
        """
        self.noisy = not self.noisy

    def set_custom_noise_model(self, noise_model: cirq.NoiseModel):
        """ Sets the noise model used by the QVM as a custom one. See https://quantumai.google/cirq/noise/representing_noise#noisemodels for more information. 

        :param noise_model: The noise model to be set. 
        :type noise_model: cirq.NoiseModel
        """
        self.noise_model = noise_model

    def construct_QVM(self) -> None:
        """ Constructs what is required to run the QVM. Must be called every time a change is made to the settings of the QVM.
        """
        if self.noisy == True:
            self.noise_property = cirq_google.noise_properties_from_calibration(cirq_google.engine.load_median_device_calibration(self.processor_id))
            self.noise_model = cirq_google.NoiseModelFromGoogleNoiseProperties(self.noise_property)
            self.simulator = qsimcirq.QSimSimulator(noise=self.noise_model)
        else:
            self.simulator = qsimcirq.QSimSimulator()

        self.device = cirq_google.engine.create_device_from_processor_id(self.processor_id)
        cal = cirq_google.engine.load_median_device_calibration(self.processor_id)
        processor = cirq_google.engine.SimulatedLocalProcessor(processor_id=self.processor_id, sampler=self.simulator, device=self.device, calibrations={cal.timestamp // 1000: cal})
        self.engine = cirq_google.engine.SimulatedLocalEngine([processor])

    def run_circuit(self, circuit: Circuit, repetitions:int, optimisation: bool) -> cirq.Result:
        """ Runs a particular circuit on the QVM and returns the results.

        :param circuit: The circuit wished to be run on the QVM
        :type circuit: Circuit
        :param repetitions: The number of times that the circuit will be run
        :type repetitions: int
        :return: The results from the simulation
        :rtype: cirq.Result
        """

        #TODO: very average gate optimisation, find most used gate and optimise according to that. 

        #gates = self.noise_property.two_qubit_gates()
        #error_measures = []
        #avg_errors = []
        #for gate in gates:
        #    measures = {op_id.qubits: fsim_error 
        #                for op_id, fsim_error in self.noise_property.fsim_errors.items() 
        #                if op_id.gate_type == gate
        #                }
        #    error_measures.append(measures)
        #    avg_errors.append(np.average(measures.values()))
        

        # TODO: Get transformed circuit from Circuit. depends on what sort of optimizations depending on what processor. GET ISWAP, or FSIM or SYCAMORE 
        ## https://quantumai.google/reference/python/cirq/CompilationTargetGateset
        transformed_circuit = cirq.optimize_for_target_gateset(circuit.get_cirq_circuit(), context=cirq.TransformerContext(deep=True), gateset=cirq.SqrtIswapTargetGateset())
        
        err_nodes, err_edges, err_smallest = self.__get_error_graph()

        # TODO: Add in optimisation option using maze finding alg
        device_path = self.__greedy_pathfinder(len(transformed_circuit.all_qubits()),err_smallest,err_nodes,err_edges)

        qubit_map = {}
        count = 0
        for q in transformed_circuit.all_qubits():
            qubit_map.update({q:device_path[count]})
            count +=1

        device_ready_circuit = transformed_circuit.transform_qubits(lambda q: qubit_map[q])

        results = self.engine.get_sampler(self.processor_id).run(device_ready_circuit, repetitions=repetitions)

        return results

    def __get_error_graph(self, targetGateset = 'ISwapPowGate'):
        """ Produces the error graph for the current simulated hardware with a target gateset in mind, and returns the nodes, the edges and smallest node to start with.

        :param targetGateset: The name of the target gateset that the error will be produced for, defaults to 'ISwapPowGate'
        :type targetGateset: str, optional
        :return: The nodes, edges and smallest nodes of the error graph.
        :rtype: list, list, tuple
        """
        qubits = set()

        if self.noisy:
            gates = list(self.noise_property.two_qubit_gates())
            error_measures = {}
            for gate in gates:
                measures = {
                op_id.qubits: pauli_error
                for op_id, pauli_error in self.noise_property.gate_pauli_errors.items()
                if op_id.gate_type == gate
            }
                error_measures.update({gate.__name__:measures})

            errors = error_measures[targetGateset]


            for transition in list(errors.keys()):
                q1, q2 = transition
                qubits.add(q1)
                qubits.add(q2)

        else:
            print(self.device)
            qubits = self.device.metadata.qubit_set
            

        nodes = sorted(list(qubits))
        print(nodes)
        edges = np.zeros((len(nodes),len(nodes)))
        smallestNode_val = 1000
        smallestNode = (None,None)
        for i in range(len(nodes)):
            for j in range(len(nodes)):
                if i == j:
                    edges[i][j] = 100
                    continue
                else:
                    try:
                        if self.noisy:
                            edges[i][j] = errors[(nodes[i],nodes[j])]

                            if edges[i][j] < smallestNode_val:
                                smallestNode = (nodes[i],nodes[j])
                                smallestNode_val = edges[i][j]
                        else:
                            i_row = nodes[i].row
                            i_col = nodes[i].col
                            j_row = nodes[j].row
                            j_col = nodes[j].col

                            if ((i_row == j_row) and ((i_col == (j_col +1)) or (i_col == (j_col -1)) )) or ((i_col == j_col) and ((i_row == (j_row +1)) or (i_row == (j_row -1)))):
                                edges[i][j] = 0
                                if edges[i][j] < smallestNode_val:
                                    smallestNode = (nodes[i],nodes[j])
                                    smallestNode_val = edges[i][j]
                            else:
                                edges[i][j] = 100
                    except:
                        edges[i][j] = 100
        print(smallestNode)
        print(edges)
        return nodes, edges, smallestNode

    def __greedy_pathfinder(self,pathLength,err_smallest,err_edges,err_nodes):
        device_path = []
        n1, n2 = err_smallest
        if n1 > n2:
            device_path.append(n1)
            device_path.append(n2)
        else:
            device_path.append(n2)
            device_path.append(n1)

        while len(device_path) != pathLength:
            curNode = device_path[-1]
            searchEdges = err_edges[err_nodes.index(curNode)]
            nextNodeIndexes = np.argpartition(searchEdges,4)[:4]
            for i in range(len(nextNodeIndexes)):
                if device_path.count(err_nodes[nextNodeIndexes[i]]) == 0:
                    device_path.append(err_nodes[nextNodeIndexes[i]])
                    break
                if i == (len(nextNodeIndexes)-1):
                    raise ValueError
        print(device_path)
        return device_path

    # TODO: def setup_with_config_file(): -> take yaml file and update QVM accordingly


    def get_QVM_qubit_grid(self) -> str:
        """ Gets a string representation of the qubit grid for the current virtual machine.

        :return: Representation of the qubit grid for the current virtual machine
        :rtype: str
        """
        return self.engine.get_processor(self.processor_id).get_device()

    



