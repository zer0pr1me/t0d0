from datetime import date
from blessed import Terminal

from model.todo import Todo
from todolist.todolist import TodoList
from screens.screen import Screen
from screens.hotkeys import hotkey, unhandled_key_handler
from screens.dialogs.confirmation_dialog import ConfirmationDialog

class TodoScreen(Screen):
    def __init__(self, term: Terminal, todoapp: TodoList):
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


    @hotkey(key='w')
    def schedule_to_today(self):
        self.todos[self.i].scheduled_at = date.today()

    @hotkey(key='n', ctrl = True)
    def swap_with_next(self):
        if self.i != len(self.todos) - 1:
            self.todos[self.i], self.todos[self.i+1] = self.todos[self.i+1], self.todos[self.i]
            self.i += 1

    @hotkey(key='p', ctrl = True)
    def swap_with_prev(self):
        if self.i != 0:
            self.i -= 1
            self.todos[self.i], self.todos[self.i+1] = self.todos[self.i+1], self.todos[self.i]

    @hotkey(key='t', ctrl = True)
    def move_todo_to_top(self):
        i = self.i
        self.todos = [self.todos[i]] + self.todos[:i] + self.todos[i+1:]
        self.i = 0

    @hotkey(key='b', ctrl = True)
    def move_todo_to_bottom(self):
        i = self.i
        self.todos = self.todos[:i] + self.todos[i+1:] + [self.todos[i]] 
        self.i = len(self.todos) - 1

    @hotkey(key='q', mode='normal')
    def quit(self):
        self.exit()

    @hotkey(key='j', mode='normal')
    def move_down(self):
        self.i = min(self.i + 1, len(self.todos) - 1)

    @hotkey(key='k', mode='normal')
    def move_up(self):
        self.i = max(self.i - 1, 0)

    @hotkey(key='t', mode='normal')
    def move_to_top(self):
        self.i = 0

    @hotkey(key='b', mode='normal')
    def move_to_bottom(self):
        self.i = len(self.todos) - 1

    @hotkey(key=' ', mode='normal')
    def toggle_todo(self):
        self.todos[self.i].done = not self.todos[self.i].done

    @hotkey(key='a', mode='normal')
    def add_todo_to_top(self):
        self.todos = [Todo('', False)] + self.todos
        self.i = 0
        self.mode = 'edit'

    @hotkey(key='e', mode='normal')
    def edit_todo(self):
        self.mode = 'edit'

    @hotkey(key='i', mode='normal')
    def insert_todo(self):
        self.todos = self.todos[:self.i+1] + [Todo('', False)] + self.todos[self.i+1:]
        self.i += 1
        self.mode = 'edit'

    @hotkey(key='d', mode='normal')
    def delete_todo(self):
        def _delete():
            self.todos = self.todos[:self.i] + self.todos[self.i+1:]
            self.i = min(self.i, len(self.todos) - 1)
        dialog = ConfirmationDialog(term=self.term,
                                    msg='Do you want to delete this TODO entry?',
                                    on_confirm=_delete)
        self.show_dialog(dialog)

    @unhandled_key_handler()
    def handle_editing(self, name: str, key: str, ctrl: bool):
        if self.mode == 'edit':
            if name == 'KEY_ENTER' or name == 'KEY_ESCAPE' or (key == '[' and ctrl):
                self.mode = 'normal' 
            elif name == 'KEY_BACKSPACE':
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
            print(f'[{"x" if todo.done else " "}] {todo.text}', end='')
            print(self.term.yellow + f' {todo.scheduled_at.isoformat() if todo.scheduled_at else ""}')
            print(self.term.normal)


    def on_start(self):
        self.todoapp.load()


    def on_exit(self):
        self.todoapp.save()

