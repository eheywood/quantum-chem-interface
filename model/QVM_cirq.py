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

    # TODO: def setup_with_config_file(): -> take yaml file and update QVM accordingly
        
    def run_circuit(self, circuit: Circuit, repetitions:int, optimisation: bool) -> cirq.Result:
        """ Runs a particular circuit on the QVM and returns the results.

        :param circuit: The circuit wished to be run on the QVM
        :type circuit: Circuit
        :param repetitions: The number of times that the circuit will be run
        :type repetitions: int
        :return: The results from the simulation
        :rtype: cirq.Result
        """

        # Map circuit onto physical qubits using Router. This takes into account that two-qubit gates must operate on adjacent qubits.
        device_graph = self.device.metadata.nx_graph
        router = cirq.RouteCQC(device_graph)

        routed_circuit, _, _ = router.route_circuit(circuit.get_cirq_circuit())

        # TODO: Get transformed circuit from Circuit. depends on what sort of optimizations depending on what processor. GET ISWAP, or FSIM or SYCAMORE 
        ## https://quantumai.google/reference/python/cirq/CompilationTargetGateset

        transformed_circuit = cirq.optimize_for_target_gateset(routed_circuit, context=cirq.TransformerContext(deep=True), gateset=cirq.SqrtIswapTargetGateset())
        
        # Further optimisations on the circuit could be performed here. 
        results = self.engine.get_sampler(self.processor_id).run(transformed_circuit, repetitions=repetitions)

        return results

    def get_two_gate_error_graph(self, targetGateset = 'ISwapPowGate'):
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
            qubits = self.device.metadata.qubit_set
            print(self.device.metadata.compilation_target_gatesets)
            cirq.convert_to_target_gateset(self.device.metadata.compilation_target_gatesets)
            

        nodes = sorted(list(qubits))
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
        return nodes, edges, smallestNode

    def get_QVM_qubit_grid(self) -> str:
        """ Gets a string representation of the qubit grid for the current virtual machine.

        :return: Representation of the qubit grid for the current virtual machine
        :rtype: str
        """
        return self.engine.get_processor(self.processor_id).get_device()

    



