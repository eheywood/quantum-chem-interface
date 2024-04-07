import curses

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


    def close_application(self):
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
    
    # def p_in_box_problem()
        
    
    # Add other problems here...
    

