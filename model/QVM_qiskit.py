## QVM provided by Cirq
from qiskit_aer.noise import NoiseModel, depolarizing_error
import numpy as np
from .Circuit import Circuit
class QVM:

    processor_id = 'weber'
    noisy = True

    noise_model = None
    num_repetitions = 1000
    estimator = None
    
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

    def set_custom_noise_model(self, noise_model: cirq.NoiseModel):
        """ Sets the noise model used by the QVM as a custom one. See https://quantumai.google/cirq/noise/representing_noise#noisemodels for more information. 

        :param noise_model: The noise model to be set. 
        :type noise_model: cirq.NoiseModel
        """
        self.noise_model = noise_model
        self.__noise_update()


    def __noise_update(self):
        """ Used to update the simulator if noise is toggled or the noise model is updated.
        """
        
        

    def construct_default_QVM(self) -> None:
        """ Constructs what is required to run the QVM. A default set up.
        """
        if self.noisy == True:
            # Build a default noise model
            self.noise_model = NoiseModel()
            cx_depolarizing_prob = 0.02
            self.noise_model.add_all_qubit_quantum_error(depolarizing_error(cx_depolarizing_prob, 2), ["cx"])
        else:
            # Not noisy estimator
            self.estimator = Estimator()
            
        self.num_repetitions = 1000
    

    def update_config(self,config:dict):
        """ Updates the configuration of the QVM from a dictionary that will have been produced from a yaml file.

        :param config: A dictionary that has been imported from a yaml file. Contains all settings options for the QVM.
        :type config: dict
        """

        default_noise = True
        default_device = True

        #for setting, value in config.items():
            # TODO:
            #match setting:
                

        #if default_noise and self.noisy:
            
        #elif default_noise:
            
        
            


    def run_circuit(self, circuit: Circuit, optimise: bool) -> cirq.Result:
        """ Runs a particular circuit on the QVM and returns the results.

        :param circuit: The circuit wished to be run on the QVM
        :type circuit: Circuit
        :param repetitions: The number of times that the circuit will be run
        :type repetitions: int
        :return: The results from the simulation
        :rtype: cirq.Result
        """


    



