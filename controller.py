from view import cmd_line_view
from model import *
import yaml
import time

class Controller:
      
    view = None
    config = None

    menu_options = ["Particle In a Box", "Load Configuration File", "Exit"]

    backend_options = ["Cirq-QVM", "Qiskit-QVM", "IBM-Q"]

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
        parameters = ['Wavefunction ', 'Particle mass', 'Time Step Size', 'Number of time steps']
        params = self.view.problem_input_page(parameters, "Particle In a Box Simulation", self.backend_options)

        if params == None:
            self.menu()
        
        print(params)
        ## Get user input from view.
        ## Need:
            # wavefunction - already as a probability distrib? or as a mathematical wave?

            # mass of particle -< defualt to 0.5
            # assume h_bar = 0 and mass to be 0.5? 
            # time step value



         ## Format data to build circuit

if __name__ == '__main__':
	controller = Controller()