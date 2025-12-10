import blessed

from screens.todo_screen import TodoScreen


if __name__ == '__main__':
    term = blessed.Terminal()

    todo_screen = TodoScreen(term)
    todo_screen.run()

