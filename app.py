import blessed

from screens.todo_screen import TodoScreen
from model.todoapp import TodoApp


if __name__ == '__main__':
    term = blessed.Terminal()
    todoapp = TodoApp('.')

    todo_screen = TodoScreen(term, todoapp)
    todo_screen.run()

