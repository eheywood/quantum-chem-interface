from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer.primitives import Estimator
from qiskit_ibm_runtime import QiskitRuntimeService

class IBM_Q:

    optimisation_lvl = None
    backend_name = 'ibm-brisbane'

    service = None

    def __init__(self,token,config=None) -> None:
        
        self.service = QiskitRuntimeService(channel='ibm_quantum',token=token)
    
    def set_up_config(self,config):

        for setting, value in config.items():

            match setting:
                case 'backend_name':
                    self.backend_name = value
                case 'optimisation_lvl':
                    self.optimisation_lvl = value
                case _:
                    raise AttributeError(setting + " is not a known key within the configuration file.")



    def run(self, circuit:QuantumCircuit):
        print('Running circuit...')

        ### Transpile circuit

        ### Verify

        ### Run

    def verify_via_sim(self, circuit:QuantumCircuit):
        print('Verifying circuit...')

        ## Need a circuit without measurements...
        
