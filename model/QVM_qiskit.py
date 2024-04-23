## QVM provided by Qiskit
from qiskit_aer.noise import NoiseModel
from qiskit import QuantumCircuit, transpile
from qiskit.providers import fake_provider 
from qiskit_ibm_runtime.fake_provider import FakeBrisbane,FakeSherbrooke,FakeKyoto,FakeOsaka
from qiskit_aer import AerSimulator
from model import QVM,Circuit
class QVM_qiskit(QVM.QVM):

    ## See https://docs.quantum.ibm.com/api/qiskit/providers_fake_provider for other examples of fake backends. 
    noisy = False

    backend = fake_provider.Fake20QV1()
    noise_model = None
    num_repetitions = 1000
    simulator = None
    
    def __init__(self, config=None) -> None:
        """ Constructor for the Quantum Virtual Machine Class. 

        :param config: A dictionary containing the configuration details of the QVM, defaults to None
        :type config: dict, optional
        """
        
        if config != None:
            self.update_config(config)
        else: 
            self.construct_default_QVM()

    def toggle_noise(self):
        """ Toggles the noisy boolean. Turns the noise in the QVM on or off
        """
        self.noisy = not self.noisy
        self.__noise_update()

    def set_custom_noise_model(self, noise_model: NoiseModel):
        """ Sets the noise model used by the QVM as a custom one. See https://quantumai.google/cirq/noise/representing_noise#noisemodels for more information. 

        :param noise_model: The noise model to be set. 
        :type noise_model: cirq.NoiseModel
        """
        self.noise_model = noise_model
        self.simulator = self.simulator.set_option("noise_model",self.noise_model)

    def set_custom_device(self, custom_fake_backend: fake_provider.GenericBackendV2):
        """ Allows the QVM  to run off a custom backend.

        :param custom_fake_backend: The generic backend to set it to
        :type custom_fake_backend: fake_provider.GenericBackendV2
        """
        self.backend = custom_fake_backend
        self.__backend_update()



    def __backend_update(self):
        """ Updates the backend. Called if ever changes.
        """
        if self.noisy:
            self.simulator = AerSimulator().from_backend(self.backend)
        else:
            self.simulator = AerSimulator()
        self.simulator.set_option('shots',self.num_repetitions)



    def construct_default_QVM(self) -> None:
        """ Constructs what is required to run the QVM. A default set up.
        """

        if self.noisy == True:
            # Build a default noise model
            self.simulator = AerSimulator().from_backend(self.backend)
        else:
            # Not noisy estimator
            self.noise_model = None
            self.simulator = AerSimulator()
            
        self.num_repetitions = 1000
        self.simulator.set_option('shots',self.num_repetitions)

    def update_config(self,config:dict):
        """ Updates the configuration of the QVM from a dictionary that will have been produced from a yaml file.

        :param config: A dictionary that has been imported from a yaml file. Contains all settings options for the QVM.
        :type config: dict
        """

        default_backend = True

        for setting, value in config.items():
            match setting:
                case 'noise_on':
                    if type(value) == bool:
                        self.noisy = value
                    else:
                        raise TypeError("noise_on must be a Boolean")
                case 'repetitions':
                    if type(value) == int:
                        self.num_repetitions = value
                    else:
                        raise TypeError('repetitions must be an integer')
                case 'noise_model':
                    if value == 'default':
                        default_noise = True
                    elif value == 'custom':
                        default_noise = False
                    else:
                        raise AttributeError(value + " is not a known key/value mapping within the configuration file.")
                case 'backend_name':
                    if value == 'default':
                        default_backend = True
                    else:
                        default_backend = False
                case _:
                    raise AttributeError(setting + " is not a known key within the configuration file.")
        
        ## Sets the backend to the specified one according to the name
        if not default_backend:
            match value:
                case 'ibm_sherbrooke':
                    self.backend = FakeSherbrooke()
                case 'ibm_brisbane':
                    self.backend = FakeBrisbane()
                case 'ibm_osaka':
                    self.backend = FakeOsaka()
                case 'ibm_kyoto':
                    self.backend = FakeKyoto()
                case _:
                    raise AttributeError(value + " is an unknown fake backend. See https://docs.quantum.ibm.com/api/qiskit/providers_fake_provider for options")

        self.__backend_update()
        
            
        

    def run_circuit(self, circuit: Circuit,optimised:bool):
        """ Runs the circuit on the QVM.

        :param circuit: The circuit to be run
        :type circuit: QuantumCircuit
        :return: A dictionary with the counts of the different states.
        :rtype: dict
        """

        ## Transpiled circuit
        circ = transpile(circuit.get_qiskit_circuit(),backend=self.simulator)
        
        ## Run and get counts:
        result = self.simulator.run(circ).result()
        counts = result.get_counts(circ)

        return counts

        


    



