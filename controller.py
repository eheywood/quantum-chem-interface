from view import cmd_line_view
from model import *

class Controller:
      
    view = None
    config = None

    menu_options = ["Particle In a Box", "Exit"]

    def __init__(self) -> None:
        self.view = cmd_line_view.CMD_line_interface()
        self.menu()

    def menu(self):
        option_index = self.view.menu_page(self.menu_options)

        match self.menu_options[option_index]:
            case "Particle In a Box":
                print ("Particle In a Box")
            case "Exit":
                self.view.close_application()
                exit()
            
    #def get_config_file(self):
        ## Get absolute location of file from user

        ## Open file and save configuration.

    #def particle_in_box(self):
         ## Get user input from view.

         ## Format data to build circuit

         
    
if __name__ == '__main__':
	controller = Controller()