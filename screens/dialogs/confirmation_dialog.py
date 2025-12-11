from blessed import Terminal

class ConfirmationDialog:
    def __init__(self, term: Terminal, msg: str, width: int = 60, height: int = 20):
        self.term = term
        self.width = width
        self.height = height



    def _render_borders(self):
        start_x = term.width // 2 - self.width // 2
        end_x = term.width // 2 + self.width // 2
        start_y = term.height // 2 - self.height // 2
        end_y = term.height // 2 + self.height // 2
        print(term.move_xy(start_x, start_y))
        print('+', end='')
        for x in range(start_x+1, end_x):
            print('-', end='')
        print('+')
        
        for y in range(start_y+1, end_y):
            print('|' + ' ' * (height - 2) + '|')

        print('+', end='')
        for x in range(start_x+1, end_x):
            print('-', end='')
        print('+', end='')

    def render(self):
        self._render_borders()
            
