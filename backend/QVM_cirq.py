## QVM provided by Cirq
import cirq
import cirq_google
import qsimcirq
from Circuit import Circuit
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

        # TODO: Get transformed circuit from Circuit. depends on what sort of optimizations depending on what processor. 

        # TODO: Find qubits that will map to it correctly (intelligent with error checking or without)

        # TODO: Run on simulator

        # TODO: Return results


    # TODO: def setup_with_config_file(): -> take yaml file and update QVM accordingly


    def get_QVM_qubit_grid(self) -> str:
        """ Gets a string representation of the qubit grid for the current virtual machine.

        :return: Representation of the qubit grid for the current virtual machine
        :rtype: str
        """
        return self.engine.get_processor(self.processor_id).get_device()

    



