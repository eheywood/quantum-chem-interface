from view import cmd_line_view
from model.Circuit import Circuit
from model.simulations import ParticleInBoxSim
from model.QVM import QVM
from model.QVM_cirq import QVM_cirq
from model.QVM_qiskit import QVM_qiskit
from model.IBM_Q_interface import IBM_Q
import numpy as np
import matplotlib.pyplot as plt

import yaml
import time


class Controller:
      
    view = None
    config = None

    menu_options = ["Particle In a Box", "Load Configuration File", "Check IBM Job Status" "Exit"]

    backend_options = ["cirq-QVM", "qiskit-QVM", "IBM-Q"]

    def __init__(self) -> None:

        ## Initialise View and then go straight to menu
        self.view = cmd_line_view.CMD_line_interface()
        self.menu()

    def menu(self):
        option_index = self.view.menu_page(self.menu_options)

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
        ## Get absolute location of file from user
        path = self.view.get_config_filepath()

        ## Open file and save configuration.
        try:
            config_file = open(path[:-2],'r')
            self.config = yaml.safe_load(config_file)
            msg = "Config file successfully loaded."
        except:
            msg = "ERROR: Loading configuration file failed. Check path spelling."

        ## Confirmation message
        self.view.display_temp_msg(msg)
        time.sleep(1)
        
        self.menu()

    def particle_in_box(self):
        parameters = ['Size of Box', 'Eigenstate/Energy Level', 'Time Step Size', 'Number of time steps']
        params, backend = self.view.problem_input_page(parameters, "Particle In a Box Simulation", self.backend_options)

        ## Check values are not empty
        if params == None or list(params.values()).count(None) > 0:
            self.view.display_temp_msg("All parameters must be filled before submitting.")
            self.menu()

        time_step_size = None
        box_length = None
        num_iters = None
        energy_lvl = None
        ## Input Validation
        try:
            box_length = int(params['Size of Box'])
            if (box_length & (box_length - 1) == 0 ) and box_length != 0:
                self.view.display_temp_msg("Box length must be a power of 2")
                self.menu()            
        except:
            self.view.display_temp_msg("Size of Box must be an integer and be a power 2. Suggest not going above 32 if simulating, as this will be a 7 qubit simulation.")
            self.menu()
        
        try:
            time_step_size = float(params['Time Step Size'])          
        except:
            self.view.display_temp_msg("Time step size must be an integer or float.")
            self.menu()
        
        try:
            num_iters = int(params['Number of time steps'])          
        except:
            self.view.display_temp_msg("Number of time-steps must be an integer")
            self.menu()
        
        try:
            energy_lvl = int(params['Eigenstate/Energy Level'])
        except:
            self.view.display_temp_msg("Energy Level must be an integer.")
            self.menu()    
    
        print(params)

        ## Build circuit
        circuit_name = 'particle_in_box_e' + str(energy_lvl) + "_q" + str(np.log(box_length) + 2)
        initial_name = 'initial_state_circuit_e' + str(energy_lvl) + "_q" + str(np.log(box_length))
        particle_in_box_circuit = Circuit(circuit_name)
        initial_state_circuit = Circuit("initial_state")
        circuit, initial_circuit = ParticleInBoxSim.build_circuit(box_length,energy_lvl,time_step_size,num_iters, backend)
        particle_in_box_circuit.set_cirq_circuit(circuit)  
        initial_state_circuit.set_cirq_circuit(initial_circuit)

        ## Set up for a particular backend
        match backend:
            case "cirq-QVM":
                if self.config != None:
                    virtual_machine = QVM_cirq(config=self.config['cirq-QVM'])
                else:
                    virtual_machine = QVM_cirq()
                
                self.run_QVM_job(virtual_machine,particle_in_box_circuit,initial_state_circuit)
            case "qiskit-QVM":
                if self.config != None:
                    virtual_machine = QVM_qiskit(config=self.config['qiskit-qvm'])
                else:
                    virtual_machine = QVM_qiskit()
                
                self.run_QVM_job(virtual_machine,particle_in_box_circuit,initial_state_circuit)
            case "IBM-Q":
                self.submit_IBMQ_job(particle_in_box_circuit,initial_state_circuit)
            case _:
                raise Exception("Unknown backend name: " +  backend)
                      
   
    def run_QVM_job(self, QVM:QVM, circuit:Circuit, initial_state:Circuit):

        results = QVM.run_circuit(circuit,False)

        initial_state = QVM.run_circuit(initial_state,False)

        for i in range(2 ** circuit.num_qubits):
            count = results.get()
            if count == None:
                results.update({i:0})
            else:
                results.pop(bin(i)[2:],None)
                results.update({i:count})
            
            initial_count = initial_state.get()
            if initial_count == None:
                initial_state.update({i:0})
            else:
                initial_state.pop(bin(i)[2:],None)
                initial_state.update({i:initial_count})
        
        fig, ax = plt.subplots(nrows = 1, ncols = 2)
        ax[0].bar(initial_state.keys(),initial_state.values())
        ax[0].title.set_text("Initial State")

        ax[1].bar(results.keys(),results.values())
        ax[1].title.set_text("Initial State")
        
        #TODO: wht plt not showing
        plt.show()
    
    def submit_IBMQ_job(self, circuit:Circuit, initial_state:Circuit):
        ## Get IBM-Q API Token

        try:
            if self.config != None:
                ibm_interface = IBM_Q(token,self.config)
            else:
                ibm_interface = IBM_Q(token)
        except:
            self.view.display_temp_msg("API Token failed. Check token and try again.")
            

    def check_IBM_job_status(self):
        #TODO: submit job to IBM
        print("ibm")


if __name__ == '__main__':
	controller = Controller()