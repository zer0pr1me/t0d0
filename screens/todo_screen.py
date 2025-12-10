from blessed import Terminal
from blessed.keyboard import Keystroke

from model.todo import Todo
from model.todoapp import TodoApp
from screens.screen import Screen, hotkey

class TodoScreen(Screen):
    def __init__(self, term: Terminal, todoapp: TodoApp):
        super().__init__(term)
        self.mode = 'normal'
        self.i = 0
        self.todoapp = todoapp

    @property
    def todos(self):
        return self.todoapp.todos

    @todos.setter
    def todos(self, value):
        self.todoapp.todos = value

    @hotkey('n', ctrl = True)
    def swap_with_next(self):
        if self.i != len(self.todos) - 1:
            self.todos[self.i], self.todos[self.i+1] = self.todos[self.i+1], self.todos[self.i]
            self.i += 1

    @hotkey('p', ctrl = True)
    def swap_with_prev(self):
        if self.i != 0:
            self.i -= 1
            self.todos[self.i], self.todos[self.i+1] = self.todos[self.i+1], self.todos[self.i]

    @hotkey('t', ctrl = True)
    def move_to_top(self):
        i = self.i
        self.todos = [self.todos[i]] + self.todos[:i] + self.todos[i+1:]
        self.i = 0

    @hotkey('b', ctrl = True)
    def move_to_bottom(self):
        i = self.i
        self.todos = self.todos[:i] + self.todos[i+1:] + [self.todos[i]] 
        self.i = len(self.todos) - 1

    @hotkey('q', mode='normal')
    def quit(self):
        self.exit()

    @hotkey('j', mode='normal')
    def move_down(self):
        self.i = min(self.i + 1, len(self.todos) - 1)

    @hotkey('k', mode='normal')
    def move_up(self):
        self.i = max(self.i - 1, 0)

    @hotkey('t', mode='normal')
    def move_to_top(self):
        self.i = 0

    @hotkey('b', mode='normal')
    def move_to_bottom(self):
        self.i = len(self.todos) - 1

    @hotkey(' ', mode='normal')
    def toggle_todo(self):
        self.todos[self.i].done = not self.todos[self.i].done

    @hotkey('a', mode='normal')
    def add_todo_to_top(self):
        self.todos = [Todo('', False)] + self.todos
        self.i = 0
        self.mode = 'edit'

    @hotkey('e', mode='normal')
    def edit_todo(self):
        self.mode = 'edit'

    @hotkey('i', mode='normal')
    def insert_todo(self):
        self.todos = self.todos[:self.i+1] + [Todo('', False)] + self.todos[self.i+1:]
        self.i += 1
        self.mode = 'edit'

    @hotkey('d', mode='normal')
    def delete_todo(self):
        # TODO: delete confirmation
        self.todos = self.todos[:self.i] + self.todos[self.i+1:]
        self.i = min(self.i, len(self.todos) - 1)

    def handle_key(self, key: str, ctrl: bool) -> bool:
        # TODO: find better way
        if not super().handle_key(key, ctrl) and self.mode == 'edit':
            if key == 'KEY_ENTER' or key == 'KEY_ESCAPE' or (key == '[' and ctrl):
                self.mode = 'normal' 
            elif key == 'KEY_BACKSPACE':
                self.todos[self.i].text = self.todos[self.i].text[:-1]
            else: 
                self.todos[self.i].text += key


    def render(self):
        for i, todo in enumerate(self.todos):
            print(self.term.move_xy(0, i), end='')
            if i == self.i:
                if self.mode == 'edit':
                    print(f'[{"x" if todo.done else " "}] {todo.text}', end='')
                    # and cursor
                    print(self.term.on_snow + self.term.black + ' ' + self.term.normal)
                    continue

                print(self.term.on_snow + self.term.black, end='')
            print(f'[{"x" if todo.done else " "}] {todo.text}')
            print(self.term.normal)


    def on_start(self):
        self.todoapp.load()


    def on_exit(self):
        self.todoapp.save()

