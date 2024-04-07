import curses
from curses.textpad import Textbox, rectangle

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


    def menu_page(self, menu_options):
        
        self.stdscr.clear()
        self.stdscr.nodelay(False)
        choice = 0

        while True:
            x_pos = 1
            y_pos = 5
            for i in range(len(menu_options)):
                if i == choice:
                    self.stdscr.addstr(y_pos,x_pos,menu_options[i], curses.A_REVERSE)
                else:
                    self.stdscr.addstr(y_pos,x_pos,menu_options[i])
                y_pos += 1
        
            self.stdscr.refresh()

            c = self.stdscr.get_wch()

            if c == curses.KEY_UP:
                if choice != 0:
                    choice -= 1
            elif c == curses.KEY_DOWN:
                if choice != (len(menu_options) -1):
                    choice += 1
            elif c == '\n':
                break   
   
        return choice

    def get_config_filepath(self):
        self.stdscr.clear()

        msg = "Enter path to configuration file: (hit Ctrl-G to send)"
        self.stdscr.addstr(0, 0, msg)

        editwin = curses.newwin(3,len(msg), 2,1)
        rectangle(self.stdscr, 1,0, 1+3+1, 1+len(msg)+1)
        self.stdscr.refresh()

        box = Textbox(editwin)

        # Let the user edit until Ctrl-G is struck.
        box.edit()

        # Get resulting contents
        path = box.gather()

        return path

    def p_in_box_input_page(self):
        self.stdscr.clear()


    def display_temp_msg(self,msg):
        self.stdscr.clear()
        self.stdscr.addstr(1,5, msg)
        self.stdscr.refresh()


    def close_application(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
    
    # def p_in_box_problem()
        
    
    # Add other problems here...
    

