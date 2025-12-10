import blessed

from screens.menu_screen import MenuScreen
from model.todoapp import TodoApp

if __name__ == '__main__':
    term = blessed.Terminal()
    todoapp = TodoApp('.')

    menu_screen = MenuScreen(term)
    menu_screen.run()

