import curses
from curses.textpad import Textbox, rectangle
import math
class CMD_line_interface:

    stdscr = None
    max_x = None
    max_y = None

    def __init__(self) -> None:

        self.stdscr = curses.initscr()
        self.stdscr.clear()
        self.stdscr.refresh()

        curses.noecho()
        self.stdscr.keypad(True)

        max_x = curses.COLS
        max_y = curses.LINES


    def options_page(self, options, title):
        """ Displays a list of interactive options. Returns the users choice when the Enter key is pressed

        :param menu_options: List of options to display
        :type menu_options: List
        :return: The index of the options choice
        :rtype: int
        """
        
        self.stdscr.clear()
        self.stdscr.nodelay(False)
        choice = 0

        self.stdscr.addstr(1,1,title,curses.A_UNDERLINE)

        while True:
            x_pos = 1
            y_pos = 3
            for i in range(len(options)):
                if i == choice:
                    self.stdscr.addstr(y_pos,x_pos,options[i], curses.A_REVERSE)
                else:
                    self.stdscr.addstr(y_pos,x_pos,options[i])
                y_pos += 1
        
            self.stdscr.refresh()

            c = self.stdscr.get_wch()

            if c == curses.KEY_UP:
                if choice != 0:
                    choice -= 1
            elif c == curses.KEY_DOWN:
                if choice != (len(options) -1):
                    choice += 1
            elif c == '\n':
                break   
   
        return choice

    def get_text_from_user(self, msg:str):
        """ Gets a filepath for the configuration file from the user.

        :return: The user inputted filepath 
        :rtype: str
        """
        self.stdscr.clear()

        msg = msg + " (hit Ctrl-G to send)"
        self.stdscr.addstr(0, 0, msg)

        win = curses.newwin(3,len(msg), 2,1)
        rectangle(self.stdscr, 1,0, 1+3+1, 1+len(msg)+1)
        self.stdscr.refresh()

        box = Textbox(win)

        # Let the user edit until Ctrl-G is struck.
        box.edit()

        # Get resulting contents
        text = box.gather()

        return text

    def display_temp_msg(self,msg:str):
        """ Displays a message on the screen.

        :param msg: The message to display on the screen.
        :type msg: str
        """
        self.stdscr.clear()
        self.stdscr.addstr(1,5, msg)
        self.stdscr.refresh()


    def close_application(self):
        """ Closes the window opened by Curses.
        """
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
    
   
    def problem_input_page(self,parameter_names:list,page_title:str, backend_options:list, note=None) -> dict:
        """ A generic method to display a page of required parameters and return the results inputted by the user.

        :param parameter_names: The names/ descriptions of the required parameters
        :type parameter_names: list[str]
        :param page_title: The title of the problem
        :type page_title: str
        :return: A dictionary containing key,value pairs of parameter name, to input value
        :rtype: dict
        """
        self.stdscr.clear()

        params = {}
        boxes = []

        x_pos = 1
        y_pos = 6
        for i in range(len(parameter_names)):
            params.update({parameter_names[i]:None})

            # create windows for each textbox
            win = curses.newwin(1,50,y_pos,x_pos + len(parameter_names[i]) + 3)
            box = Textbox(win)
            boxes.append(box)
            y_pos += 1

        choice = 0
        backend_index = 0
        note = "-> " + note

        while True:
            x_pos = 1
            y_pos = 5

            self.stdscr.addstr(1,1,page_title, curses.A_UNDERLINE)
            self.stdscr.addstr(3,1,"-> CTRL-G to finish typing or q to go back to menu", curses.A_ITALIC)
            
            if note != None:
                self.stdscr.addstr(4,1,note, curses.A_ITALIC)
                y_pos += 1


            for i in range(len(backend_options)):
                if backend_index == i:
                    length = 16
                    name_length = len(backend_options[i])
                    diff = 16-name_length

                    rotating_str = "<" + (" " * math.floor(diff/2)) + backend_options[i] + (" " * math.ceil(diff/2)) + ">"

                    backend_str = "Backend: " + rotating_str
                    self.stdscr.addstr(y_pos, x_pos, backend_str)
                    break
            
            y_pos += 1

            for i in range(len(parameter_names) + 1):
                if i == len(parameter_names):
                    if i == choice:
                        self.stdscr.addstr(y_pos,x_pos,"Submit",  curses.A_REVERSE)
                    else:
                        self.stdscr.addstr(y_pos,x_pos,"Submit")
                elif i == choice:
                    self.stdscr.addstr(y_pos,x_pos,parameter_names[i] + ": ", curses.A_REVERSE)
                else:
                    self.stdscr.addstr(y_pos,x_pos,parameter_names[i] + ": ")
                
                y_pos += 1
            
        
            self.stdscr.refresh()
            c = self.stdscr.get_wch()

            if c == curses.KEY_UP:
                if choice != 0:
                    choice -= 1
            elif c == curses.KEY_DOWN:
                if choice != (len(parameter_names)):
                    choice += 1
            elif c == curses.KEY_LEFT:
                if backend_index != 0:
                    backend_index -= 1
            elif c == curses.KEY_RIGHT:
                if backend_index != (len(backend_options) -1):
                    backend_index += 1
            elif c == '\n' and choice == len(parameter_names):
                break
            elif c == '\n':
                boxes[choice].edit()
                c = self.stdscr.get_wch()
                if c == '\n':
                    choice += 1
            elif c == ord('q'):
                return None

        for i in range(len(parameter_names)):
            val = boxes[i].gather()
            params.update({parameter_names[i]: val})


        return params, backend_options[backend_index]

    def waiting_page(self, msg:str):
        """ Creates a waiting page that stays the same until next page is called.
        """

        self.stdscr.clear()

        self.stdscr.addstr(1,1,msg)

        self.stdscr.refresh()
    
    def yes_no_question(self, question:str):
        """ Produces a page with a yes or no question.

        :param question: The question to ask
        :type question: str
        :return: True if yes, False if no.
        :rtype: _type_
        """ 
        msg = question
        self.stdscr.clear()

        self.stdscr.addstr(1,1,msg)
        
        choice = 0
        choices = ['yes', 'no']
        while True:
            x_pos = 1
            for i in range(len(choices)):
                if i == choice:
                    self.stdscr.addstr(3,x_pos,choices[i], curses.A_REVERSE)
                else:
                    self.stdscr.addstr(3,x_pos,choices[i])
                x_pos += 6
            
            c = self.stdscr.get_wch()

            if c == curses.KEY_LEFT:
                choice = 0
            elif c == curses.KEY_RIGHT:
                choice = 1
            elif c == '\n':
                if choice == 0:
                    return True
                else:
                    return False
                
        return False
    
    

