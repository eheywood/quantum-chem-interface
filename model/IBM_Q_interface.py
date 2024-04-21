from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer import AerSimulator
from model.Circuit import Circuit
from  qiskit.providers import JobStatus
class IBM_Q:

    optimisation_lvl = 1
    backend_name = 'ibm_brisbane'

    num_repetitions = 1000
    service = None
    token = None
    backend = None


    def __init__(self,token:str,config=None):
        """ Initializes the IBM Q interface and returns true if a successful connection is made.

        :param token: The API token to connect to an IBMQ account.
        :type token: str
        :param config: A specification of configuration for the interface , defaults to None
        :type config: dict, optional
        :return: True if successfully connect, False otherwise.
        :rtype: bool
        """
        
        try:
            self.service = QiskitRuntimeService(channel='ibm_quantum',token=token)
            self.token = token

            if config == None:
                self.backend = self.service.backend(self.backend_name)
            else:
                self.set_up_config()

        except:
            raise Exception("Could not successfully connect to Qiskit Runtime Service. Check API token.")

    def set_up_config(self,config:dict):
        """ Sets the configuration options specified from a configuration file.

        :param config: A dictionary of different configuration options. Will have been produced from a yaml file.
        :type config: dict
        :raises AttributeError: If the yaml file is not correctly formatted or named.
        """

        for setting, value in config.items():

            match setting:
                case 'backend_name':
                    self.backend_name = value
                case 'optimisation_lvl':
                    self.optimisation_lvl = value
                case _:
                    raise AttributeError(setting + " is not a known key within the configuration file.")
        
        ## See https://docs.quantum.ibm.com/api/qiskit-ibm-runtime/options for more potential configuration options.
        
        self.backend = self.service.backend(self.backend_name)


    def check_job_status(self,job_id):
        """ Checks the status of a job.

        :param job_id: The ID of the job in question.
        :type job_id: str
        :raises Exception: If the job id is incorrect,
        :return: The status of the job.
        :rtype: JobStatus (Enum)
        """
        try:
            job = self.service.job(job_id)
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
            job = self.service.job(job_id)
        except:
            raise Exception("Could not find job. Check job ID")

        status = job.status()
        
        match status:
            case JobStatus.DONE:
                result = job.result()
                distribution = result[0].data.m_meas.get_counts()
                complete = True

            case _:
                complete = False
                distribution = None

        return complete, distribution
        

    def submit_job(self, circuit:Circuit):
        """ Submits a job to IBM Q according to pre-specified setup.

        :param circuit: The circuit to submit
        :type circuit: QuantumCircuit
        :return: The job_id if successful.
        :rtype: str
        """

        ### Transpile circuit
        pm = generate_preset_pass_manager(optimization_level=self.optimisation_lvl, backend=self.backend)
        circ = pm.run(circuit.get_qiskit_circuit())

        ### Run
        sampler = Sampler(self.backend)
        job = sampler.run([circ], shots = self.num_repetitions)
        job_id = job.job_id()

        return job_id


    def verify_via_sim(self, circuit:Circuit):
        """ Verifies the circuit works using a simulator. Returns the results from the simulation.

        :param circuit: The circuit to validate.
        :type circuit: QuantumCircuit
        :return: A dictionary of the counts from the measurements
        :rtype: dict
        """

        try:
            simulator = AerSimulator.from_backend(self.backend)

            circ = transpile(circuit.get_qiskit_circuit(),simulator)

            sampler = Sampler(simulator)
            job = sampler.run([circ],shots = self.num_repetitions)
            
            result = job.result()[0].data.m_meas.get_counts()

            simulator = AerSimulator()

            circ = transpile(circuit.get_qiskit_circuit(),simulator)

            sampler = Sampler(simulator)
            job = sampler.run([circ],shots = self.num_repetitions)
            
            exact_result = job.result()[0].data.m_meas.get_counts()
        except:
            return None
        
        return result, exact_result

        


        
