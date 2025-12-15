from dataclasses import replace
from datetime import date, timedelta
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
        self.edit_cursor = 0

    @property
    def todos(self):
        return self.todoapp.todos

    @todos.setter
    def todos(self, value):
        self.todoapp.todos = value

    def _start_edit(self):
        self.mode = 'edit'
        self.edit_cursor = len(self.todos[self.i].text)

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

    @hotkey(key='e', ctrl = True)
    def move_todo_to_bottom(self):
        i = self.i
        self.todos = self.todos[:i] + self.todos[i+1:] + [self.todos[i]] 
        self.i = len(self.todos) - 1

    @hotkey(key='w', mode='normal')
    def schedule_to_today(self):
        self.todos[self.i].scheduled_at = date.today()

    @hotkey(key='h', mode='normal')
    def move_schedule_prev(self):
        if self.todos[self.i].scheduled_at is None:
            self.schedule_to_today()
        self.todos[self.i].scheduled_at -= timedelta(days=1)

    @hotkey(key='l', mode='normal')
    def move_schedule_next(self):
        if self.todos[self.i].scheduled_at is None:
            self.schedule_to_today()
        self.todos[self.i].scheduled_at += timedelta(days=1)

    @hotkey(key='c', mode='normal')
    def copy_todo(self):
        copy = replace(self.todos[self.i], 
                       done=False, 
                       created_at=date.today(), 
                       scheduled_at=None)

        self.todos = self.todos[:self.i+1] + [copy] + self.todos[self.i+1:]
        self.i += 1


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
        self._start_edit()

    @hotkey(key='e', mode='normal')
    def edit_todo(self):
        self._start_edit()

    @hotkey(key='i', mode='normal')
    def insert_todo(self):
        self.todos = self.todos[:self.i+1] + [Todo('', False)] + self.todos[self.i+1:]
        self.i += 1
        self._start_edit()

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
            elif key == 'b' and ctrl:
                self.edit_cursor = max(self.edit_cursor - 1, 0)
            elif key == 'f' and ctrl:
                self.edit_cursor = min(self.edit_cursor + 1, len(self.todos[self.i].text))
            else: 
                if self.edit_cursor == len(self.todos[self.i].text):
                    self.todos[self.i].text += key
                else:
                    text = self.todos[self.i].text 
                    self.todos[self.i].text = text[:self.edit_cursor] + key + text[self.edit_cursor:]
                self.edit_cursor += 1


    def render(self):
        for i, todo in enumerate(self.todos):
            print(self.term.move_xy(0, i), end='')
            if i == self.i:
                if self.mode == 'edit':
                    print(f'[{"x" if todo.done else " "}] {todo.text[:self.edit_cursor]}', end='')
                    # and cursor
                    if self.edit_cursor < len(todo.text):
                        print(self.term.on_snow + 
                              self.term.black + 
                              todo.text[self.edit_cursor], end='')
                        print(self.term.normal + todo.text[self.edit_cursor+1:])
                    else:
                        print(self.term.on_snow + self.term.black + ' ' + self.term.normal, end='')
                    continue

                print(self.term.on_snow + self.term.black, end='')
            print(f'[{"x" if todo.done else " "}] {todo.text}', end='')
            print(self.term.yellow + f' {todo.scheduled_at.isoformat() if todo.scheduled_at else ""}')
            print(self.term.normal)


    def on_start(self):
        self.todoapp.load()


    def on_exit(self):
        self.todoapp.save()

