import math
import os
from view import cmd_line_view
from model.Circuit import Circuit
from model.simulations import ParticleInBoxSim
from model.QVM import QVM
from model.QVM_cirq import QVM_cirq
from model.QVM_qiskit import QVM_qiskit
from model.IBM_Q_interface import IBM_Q
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from  qiskit.providers import JobStatus

import yaml
import time

# TODO: bug fix issues with config file and api token


class Controller:
      
    view = None
    config = None

    qvm = None
    ibmq_interface = None

    menu_options = ["Particle In a Box", "Load Configuration File", "Check IBM Job Status", "Exit"]

    backend_options = ["cirq-QVM", "qiskit-QVM", "IBM-Q"]

    def __init__(self) -> None:

        ## Initialise View and then go straight to menu
        self.view = cmd_line_view.CMD_line_interface()
        self.menu()

    def menu(self):
        """ Creates a menu page using the view and sends the view the menu options for the user to choose from. 
        """

        option_index = self.view.options_page(self.menu_options, "Quantum-Chem-Interface")

        match self.menu_options[option_index]:
            case "Particle In a Box":
                self.particle_in_box()
            case "Load Configuration File":
                self.get_config_file()
            case "Check IBM Job Status":
                self.check_IBM_job_status()
            case "Exit":
                self.view.close_application()
                exit()
            
    def get_config_file(self):
        """ Gets the configuration file from the user and parses it into a dictionary. 
        """

        ## Get absolute location of file from user
        path = self.view.get_text_from_user("Enter path to configuration file:")

        ## Open file and save configuration.
        #try:
        path = path.replace("\n","")

        config_file = open(path,'r')
        self.config = yaml.safe_load(config_file)
        msg = "Config file successfully loaded."

        if self.qvm != None:
            self.qvm.update_config(self.config)
        
        if self.ibmq_interface != None:
            self.ibmq_interface.set_up_config(self.config)

        #except:
        msg = "ERROR: Loading configuration file failed. Could not find " + path

        ## Confirmation message
        self.view.display_temp_msg(msg)
        time.sleep(1)
        
        self.menu()

    def particle_in_box(self):
        """ Runs the particle in a box problem, sends the names of the parameters required to the view to have the user submit the values. 

        :raises Exception: If the backend name chosen is unknown
        """

        parameters = ['Size of Box', 'Eigenstate/Energy Level', 'Time Step Size', 'Number of time steps','Optimised(y/n)']
        params, backend = self.view.problem_input_page(parameters, "Particle In a Box Simulation", self.backend_options)

        ## Check values are not empty
        if params == None or list(params.values()).count(None) > 0:
            self.view.display_temp_msg("All parameters must be filled before submitting.")
            time.sleep(1)
            self.menu()
            return

        time_step_size = None
        box_length = None
        num_iters = None
        energy_lvl = None
        optimised = None

        ## Input Validation
        try:
            box_length = int(params['Size of Box'])
            
        except:
            self.view.display_temp_msg("Size of Box must be an integer and be a power 2.")
            time.sleep(2)
            self.menu()
        
        if not (math.log(box_length)/math.log(2)).is_integer():
            self.view.display_temp_msg("A Box length of " + str(box_length) + " is not a power of 2")
            time.sleep(2)
            self.menu()    
            return        
        
        try:
            time_step_size = float(params['Time Step Size'])          
        except:
            self.view.display_temp_msg("Time step size must be an integer or float.")
            time.sleep(1)
            self.menu()
        
        try:
            num_iters = int(params['Number of time steps'])          
        except:
            self.view.display_temp_msg("Number of time-steps must be an integer")
            time.sleep(1)
            self.menu()
        
        try:
            energy_lvl = int(params['Eigenstate/Energy Level'])
        except:
            self.view.display_temp_msg("Energy Level must be an integer.")
            time.sleep(1)
            self.menu()    

        try:
            if params['Optimised(y/n)'].strip() == "y":
                optimised = True
            elif params['Optimised(y/n)'].strip() == "n":
                optimised = False
            else: 
                self.view.display_temp_msg("Optimised must be a string of either y or n. Not " + str(params['Optimised(y/n)']))
                time.sleep(1)
                self.menu()
        except:
            self.view.display_temp_msg("Optimised must be a string of either y or n")
            time.sleep(1)
            self.menu()

        self.view.waiting_page("Building Circuit...")

        ## Build circuit
        circuit_name = 'particle_in_box_e' + str(energy_lvl) + "_q" + str(np.log(box_length) + 2)
        initial_name = 'initial_state_circuit_e' + str(energy_lvl) + "_q" + str(np.log(box_length))
        particle_in_box_circuit = Circuit(circuit_name)
        initial_state_circuit = Circuit(initial_name)
        circuit, initial_circuit = ParticleInBoxSim.build_circuit(box_length,energy_lvl,time_step_size,num_iters, backend)
        particle_in_box_circuit.set_cirq_circuit(circuit)  
        initial_state_circuit.set_cirq_circuit(initial_circuit)


        ## Set up for a particular backend
        match backend:
            case "cirq-QVM":
                if self.qvm == None:
                    if self.config != None:
                        self.qvm = QVM_cirq(config=self.config['cirq-qvm'])
                    else:
                        self.qvm = QVM_cirq()
                 
                self.run_QVM_job(self.qvm,particle_in_box_circuit,initial_state_circuit,optimised)
            case "qiskit-QVM":
                if self.qvm == None:
                    if self.config != None:
                        self.qvm = QVM_qiskit(config=self.config['qiskit-qvm'])
                    else:
                        self.qvm = QVM_qiskit()
                
                self.run_QVM_job(self.qvm,particle_in_box_circuit,initial_state_circuit,optimised)
            case "IBM-Q":
                self.submit_IBMQ_job(particle_in_box_circuit,params)
            case _:
                raise Exception("Unknown backend name: " +  backend)
                      
   
    def run_QVM_job(self, QVM:QVM, circuit:Circuit, initial_state:Circuit,optimised:bool):
        """ Runs a circuit on a quantum virtual machine backend.

        :param QVM: The QVM to run the circuit on .
        :type QVM: QVM
        :param circuit: The circuit in question
        :type circuit: Circuit
        :param initial_state: The initial state of the circuit, after the state preparation algorithm had been applied.
        :type initial_state: Circuit
        """
        self.view.waiting_page("Simulating...")

        results = QVM.run_circuit(circuit,optimised)

        initial_state = QVM.run_circuit(initial_state,optimised)

        for i in range(2 ** (circuit.num_qubits-1)):
            count = results.get(bin(i)[2:])
            if count == None:
                results.update({i:0})
            else:
                results.pop(bin(i)[2:],None)
                results.update({i:count})
            
            initial_count = initial_state.get(bin(i)[2:])
            if initial_count == None:
                initial_state.update({i:0})
            else:
                initial_state.pop(bin(i)[2:],None)
                initial_state.update({i:initial_count})
        
        box_len = ((2 ** (circuit.num_qubits-1)) / 2) - 0.5
        fig, ax = plt.subplots(nrows = 1, ncols = 2)
        ax[0].bar(initial_state.keys(),initial_state.values())
        ax[0].axvline(box_len,color='b',label='Box end')
        ax[0].title.set_text("Initial State")
        ax[0].legend()

        ax[1].bar(results.keys(),results.values())
        ax[1].axvline(box_len,color='b',label='Box end')

        ax[1].title.set_text("Resulting state")
        ax[1].legend()
        
        plt.show()
        
        self.menu()
    
    def submit_IBMQ_job(self, circuit:Circuit, params:dict):
        """ SUbmits a circuit to run on the IBM Quantum platform.

        :param circuit: The circuit to run.
        :type circuit: Circuit
        :param initial_state: The initial state of the circuit after state preparation has been applied.
        :type initial_state: Circuit
        """
                                   
        if self.ibmq_interface == None:

            token = self.view.get_text_from_user("Input API token for IBM-Q: ")
            token = token.replace(" ","")
            token = token.replace("\n","")

            self.view.waiting_page("Connecting...")

            try:
                if self.config != None:
                    self.ibmq_interface = IBM_Q(token,self.config)
                else:
                    self.ibmq_interface  = IBM_Q(token)
            except:
                self.view.display_temp_msg("API Token failed. Check token and try again.")
                time.sleep(3)
                self.menu()
        
        self.view.waiting_page("Successfully connected to IBM-Q. Simulating expected results... ")

        simulated_results, expected_results = self.ibmq_interface.verify_via_sim(circuit)

        if simulated_results == None:
            self.view.display_temp_msg("Simulation failed. Circuit is broken")
            time.sleep(3)
            self.menu()
        
        if expected_results == None:
            self.view.display_temp_msg("Exact results failed. Circuit is broken")
            time.sleep(3)
            self.menu()
        
        print(expected_results)
        print(simulated_results)

        num_measures = circuit.num_qubits - 1

        for i in range(2 ** num_measures):
                bin_num = bin(i)[2:]

                while len(bin_num) != len(bin((2 ** num_measures) -1)[2:]):
                    bin_num = '0' + bin_num
                
                count = simulated_results.get(bin_num)
                if count == None:
                    simulated_results.update({i:0})
                else:
                    simulated_results.pop(bin_num,None)
                    simulated_results.update({i:count})
                
                expected_count = expected_results.get(bin_num)
                if expected_count == None:
                    expected_results.update({i:0})
                else:
                    expected_results.pop(bin_num,None)
                    expected_results.update({i:expected_count})

        box_len = ((2 ** (circuit.num_qubits-1)) / 2) - 0.5
        fig, ax = plt.subplots(nrows = 1, ncols = 2)
        ax[0].bar(expected_results.keys(),expected_results.values())
        ax[0].axvline(box_len,color='m',label='Box end')
        ax[0].title.set_text("Exact expected results")
        ax[0].legend()

        ax[1].bar(simulated_results.keys(),simulated_results.values())
        ax[1].axvline(box_len,color='m',label='Box end')

        ax[1].title.set_text("Noisy simulated results")
        ax[1].legend()
        
        plt.show()

        if self.view.yes_no_question("Submit job to " + self.ibmq_interface.backend_name):
            job_id = self.ibmq_interface.submit_job(circuit)

            if job_id != None:
                path = "./job_ids.yaml"

                with open(path, 'w') as file:
                    cur_file = yaml.safe_load(file)
                    params.update({'date': datetime.now().strftime("%d/%m/%Y %H:%M"),'backend':self.ibmq_interface.backend_name})
                    cur_file.update({job_id:params})

                    yaml.dump(cur_file,file,default_flow_style=False)
                
                self.view.display_temp_msg("Job successfully submitted. Job ID = " + str(job_id) + "\n Details saved in " + path)
                time.sleep(5)
            else: 
                self.view.display_temp_msg("Job submission failed, please try again")
                time.sleep(3)

        self.menu()

    def check_IBM_job_status(self):
        """ Checks and gets the status of a job set to an IBM-Q machine.
        """

        if self.ibmq_interface == None:    

            token = self.view.get_text_from_user("Input API token for IBM-Q: ")
            token = token.replace(" ","")
            token = token.replace("\n","")

            self.view.waiting_page("Connecting...")
                                    
            if self.ibmq_interface == None:
                try:
                    if self.config != None:
                        self.ibmq_interface = IBM_Q(token,self.config)
                    else:
                        self.ibmq_interface  = IBM_Q(token)
                except:
                    self.view.display_temp_msg("API Token failed. Check token and try again.")
                    time.sleep(3)
                    self.menu()
        
        ## Get list of jobs from yaml file
        path = "./job_ids.yaml"
        
        try:
            file = open(path,'r')
            job_ids = yaml.safe_load(file)   
        except:
            self.view.display_temp_msg("No job-ids found. Please check " + path + " exists and contains job-ids.")
            time.sleep(3)
            self.menu()
        
        job_strs = []
        for job,details in job_ids.items():
            details = job + ' -> ' + details['date'] + " backend: " + details['backend'] + " L: " + details['Size of Box'] + " energy level: " + details['Eigenstate/Energy Level'] + " time step: " + details['Time Step Size'] + "x " + details['Number of time steps']
            job_strs.append(details)

        option = self.view.options_page(job_strs, "Job ID's")        

        job_id = list(job_ids.keys())[option]

        status = self.ibmq_interface.check_job_status(job_id)

        if status == JobStatus.DONE:
            ## Get results
            self.view.waiting_page("Job complete, getting results...")
            _, result= self.ibmq_interface.get_results_from_job(job_id)

            box_len = int(job_ids[job_id]['Size of Box'])
            num_measures = int(np.log2(box_len) + 1)

            for i in range(2 ** num_measures):
                    bin_num = bin(i)[2:]

                    while len(bin_num) != len(bin((2 ** num_measures) -1)[2:]):
                        bin_num = '0' + bin_num
                    
                    count = result.get(bin_num)
                    if count == None:
                        result.update({i:0})
                    else:
                        result.pop(bin_num,None)
                        result.update({i:count})
                    
            fig,ax = plt.subplots()
            ax.bar(result.keys(),result.values())
            ax.axvline(box_len-0.5,color='m',label='Box end')
            ax.legend()
            plt.show()

            self.menu()

        else:
            self.view.display_temp_msg("Job is not yet complete. Please try again later. ")
            time.sleep(2)
            self.menu()

if __name__ == '__main__':
	controller = Controller()