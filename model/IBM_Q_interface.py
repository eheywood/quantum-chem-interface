from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import BackendSampler
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer import AerSimulator

class IBM_Q:

    optimisation_lvl = 1
    backend_name = 'ibm_brisbane'

    num_repetitions = 1000
    service = None
    token = None


    def __init__(self,token,config=None) -> None:
        
        try:
            self.service = QiskitRuntimeService(channel='ibm_quantum',token=token)
            self.token = token
            print('Successfully connected to qiskit runtime service')
            
        except Exception:
            raise Exception("Qiskit Runtime service failed. Check token is correct.")
    
    #def default_set_up(self):


    def set_up_config(self,config):

        for setting, value in config.items():

            match setting:
                case 'backend_name':
                    self.backend_name = value
                case 'optimisation_lvl':
                    self.optimisation_lvl = value
                case _:
                    raise AttributeError(setting + " is not a known key within the configuration file.")

    def check_job_status(self,job_id):
        """ Checks the status of a job.

        :param job_id: The ID of the job in question.
        :type job_id: str
        :raises Exception: If the job id is incorrect,
        :return: The status of the job.
        :rtype: JobStatus (Enum)
        """
        
        try:
            job = self.service(job_id)
        except:
            raise Exception("Could not find job. Check job ID")
        
        return job.status()

    def get_results_from_job(self,job_id):
        """ Gets the results from a job submitted to a quantum machine.

        :param job_id: The ID of the job in question.
        :type job_id: str
        :raises Exception: If the job ID is incorrect
        :return: Returns a boolean with if the job completes and the probability distribution of results.
        :rtype: bool, dict
        """

        try:
            job = self.service(job_id)
        except:
            raise Exception("Could not find job. Check job ID")

        status = job.status()

        match status.name():
            case 'DONE':
                result = job.results()
                distribution = result.quasi_dist[0].binary_probabilities()
                complete = True

            case _:
                complete = False
                distribution = None

        return complete, distribution
        


    def submit_job(self, circuit:QuantumCircuit):
        print('Submitting circuit...')

        ### Transpile circuit

        ### Verify

        ### Run

    def verify_via_sim(self, circuit:QuantumCircuit):
        """ Verifies the circuit works using a simulator. Returns the results from the simulation.

        :param circuit: The circuit to validate.
        :type circuit: QuantumCircuit
        :return: A dictionary of the counts from the measurements
        :rtype: dict
        """
        print('Verifying circuit...')

        try:
            backend = self.service.backend(self.backend_name)
            simulator = AerSimulator.from_backend(backend)

            circuit.measure_all()

            circ = transpile(circuit,simulator)

            sampler = Sampler(simulator)

            job = sampler.run([circ],shots = self.num_repetitions)
            
            #TODO: improve this to remove 'meas' name requirement
            result = job.result()[0].data.meas.get_counts()
        except:
            return None
        return result

        


        
