## QVM provided by Cirq
import cirq
import cirq_google
import qsimcirq
from Circuit import Circuit
class QVM:

    def __init__(self, *args: tuple) -> None:
        """ Constructor for the Quantum Virtual Machine Class

        :param *args: Arguments for the constructor, contains details of how to setup the QVM. If empty, will result in default QVM implementation. TODO: expand on what makes up *args
        :type *args: tuple
        """

        # need to specify type, noise/no noise, num of quibits, processor type etc...
        
        # Default case:
        
        self.implementation = str
        self.implementation = 'cirq' # type: str
        self.processor_id = 'weber'
        self.noisy = False

        self.noise_property = None
        self.noise_model = None
        self.simulator = None
        self.device = None
        self.engine = None

        self.construct_QVM()
    
    def construct_QVM(self) -> None:
        """ Constructs what is required to run the QVM. Must be called every time a change is made to the settings of the QVM.
        """
        if self.noisy == True:
            self.noise_property = cirq_google.noise_properties_from_calibration(cirq_google.engine.load_median_device_calibration(self.processor_id))
            self.noise_model = cirq_google.NoiseModelFromGoogleNoiseProperties(self.noise_props)
            self.simulator = qsimcirq.QSimSimulator(noise=self.noise_model)
        else:
            self.simulator = qsimcirq.QSimSimulator()

        self.device = cirq_google.engine.create_device_from_processor_id(self.processor_id)

        processor = cirq_google.engine.SimulatedLocalProcessor(processor_id=self.processor_id, sampler=self.simulator, device=self.device, calibrations={cal.timestamp // 1000: cal})
        self.engine = cirq_google.engine.SimulatedLocalEngine([processor])

    def run_circuit(self, circuit: Circuit, repetitions:int, intelligent_qubits: bool) -> cirq.Result:
        """ Runs a particular circuit on the QVM and returns the results.

        :param circuit: The circuit wished to be run on the QVM
        :type circuit: Circuit
        :param repetitions: The number of times that the circuit will be run
        :type repetitions: int
        :return: The results from the simulation
        :rtype: cirq.Result
        """

        # Get transformed circuit from Circuit. depends on what sort of optimizations depending on what processor. 

        # Find qubits that will map to it correctly (intelligent with error checking or without)

        # Run on simulator

        # Return results


    #def setup_with_config_file(): -> take yaml file and update QVM accordingly


    def get_QVM_qubit_grid(self) -> str:
        """ Gets a string representation of the qubit grid for the current virtual machine.

        :return: Representation of the qubit grid for the current virtual machine
        :rtype: str
        """
        return self.engine.get_processor(self.processor_id).get_device()

    



