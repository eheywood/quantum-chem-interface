## QVM provided by Cirq
import cirq
import cirq_google
import qsimcirq
import numpy as np
from .Circuit import Circuit
class QVM:

    processor_id = 'weber'
    noisy = True

    noise_property = None
    noise_model = None
    simulator = None
    device = None
    engine = None
    num_repetitions = 1000
    
    def __init__(self, default=True, config=None) -> None:
        """ Constructor for the Quantum Virtual Machine Class. 

        :param processor: The type of google (cirq) processor being simulated, defaults to 'weber'
        :type processor: str, optional
        :param noisy: True if the QVM will simulate noise in the machine, False if there is no noise model being set, defaults to False
        :type noisy: bool, optional
        """
        
        if default:
            self.construct_default_QVM()

        if config != None:
            self.update_config(config)
    

    def toggle_noise(self):
        """ Toggles the noisy boolean. Turns the noise in the QVM on or off
        """
        self.noisy = not self.noisy

    #TODO: Come back and fix problem with this not updating all the config.
    def set_custom_noise_model(self, noise_model: cirq.NoiseModel):
        """ Sets the noise model used by the QVM as a custom one. See https://quantumai.google/cirq/noise/representing_noise#noisemodels for more information. 

        :param noise_model: The noise model to be set. 
        :type noise_model: cirq.NoiseModel
        """
        self.noise_model = noise_model

    def set_custom_device(self, device: cirq.Device):
        """ If the user wishes to describe and build their own device, this method sets it for the QVM to use. See https://quantumai.google/cirq/hardware/devices for  more information on how to do this.

        :param device: The custom device class to be set.
        :type device: cirq.Device
        """

        self.device = device
        cal = cirq_google.engine.load_median_device_calibration(self.processor_id)
        processor = cirq_google.engine.SimulatedLocalProcessor(processor_id=self.processor_id, sampler=self.simulator, device=self.device, calibrations={cal.timestamp // 1000: cal})
        self.engine = cirq_google.engine.SimulatedLocalEngine([processor])

    def construct_default_QVM(self) -> None:
        """ Constructs what is required to run the QVM. A default set up.
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
        self.num_repetitions = 1000
    
    def update_config(self,config:dict):
        """ Updates the configuration of the QVM from a dictionary that will have been produced from a yaml file.

        :param config: _description_
        :type config: dict
        """

        default_noise = True
        default_device = True

        for setting, value in config.items():

            match setting:
                case'processor_id':
                    self.processor_id = value
                case 'noise_on':
                    if type(value) == bool:
                        self.noisy = value
                    else:
                        raise TypeError("noise_on must be a Boolean")
                case 'repetitions':
                    if type(value) == int:
                        self.num_repetitions = value
                    else:
                        raise TypeError('Repetitions must be an integer')
                case 'noise_model':
                    if value == 'default':
                        default_noise = True
                    elif value == 'custom':
                        default_noise = False
                    else:
                        raise AttributeError(value + "is not a known key/value mapping within the configuration file.")
                case 'device':
                    if value == 'default':
                        default_device = True
                    elif value == 'custom':
                        default_device = False
                    else:
                        raise AttributeError(value + "is not a known key/value mapping within the configuration file.")
                case _:
                    raise AttributeError(setting + "is not a known key within the configuration file.")

        if default_noise and self.noisy:
            self.noise_property = cirq_google.noise_properties_from_calibration(cirq_google.engine.load_median_device_calibration(self.processor_id))
            self.noise_model = cirq_google.NoiseModelFromGoogleNoiseProperties(self.noise_property)
            self.simulator = qsimcirq.QSimSimulator(noise=self.noise_model)
        elif default_noise:
            self.noise_property = None
            self.noise_model = None 
            self.simulator = qsimcirq.QSimSimulator()
        
        if default_device:
            self.device = cirq_google.engine.create_device_from_processor_id(self.processor_id)
            cal = cirq_google.engine.load_median_device_calibration(self.processor_id)
            processor = cirq_google.engine.SimulatedLocalProcessor(processor_id=self.processor_id, sampler=self.simulator, device=self.device, calibrations={cal.timestamp // 1000: cal})
            self.engine = cirq_google.engine.SimulatedLocalEngine([processor])


    def run_circuit(self, circuit: Circuit, optimisation: bool) -> cirq.Result:
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
        results = self.engine.get_sampler(self.processor_id).run(transformed_circuit, repetitions=self.num_repetitions)

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

    



