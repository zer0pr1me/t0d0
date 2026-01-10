from dataclasses import replace
from datetime import date, timedelta
from blessed import Terminal

from model.todo import Todo, human_date
from screens.screen import Screen
from screens.hotkeys import hotkey, unhandled_key_handler
from screens.dialogs.confirmation_dialog import ConfirmationDialog
from storage.storage import Storage
from todoapp.project import Project

class TodoScreen(Screen):
    def __init__(self, term: Terminal, storage: Storage, project: Project):
        super().__init__(term)
        self.project = project
        self.storage = storage
        self.mode = 'normal'
        self.start_i = 0
        self.i = 0
        self.edit_cursor = 0

    @property
    def visible_row_count(self) -> int:
        max_visible = self.term.height
        if self.start_i != 0:
            max_visible -= 1
        if len(self.todos) - self.start_i >= max_visible:
            max_visible -= 1

        return min(len(self.todos) - self.start_i, max_visible) - 1

    @property
    def todos(self):
        return self.project.todos

    def _start_edit(self):
        self.mode = 'edit'
        self.edit_cursor = len(self.todos[self.i].text)

    @hotkey(key='n', ctrl = True)
    def swap_with_next(self):
        if self.project.swap_with_next(self.i):
            self.i += 1

    @hotkey(key='p', ctrl = True)
    def swap_with_prev(self):
        if self.project.swap_with_prev(self.i):
            self.i -= 1

    @hotkey(key='t', ctrl = True)
    def move_todo_to_top(self):
        self.project.move(old_pos=self.i, new_pos=0)
        self.i = 0

    @hotkey(key='e', ctrl = True)
    def move_todo_to_bottom(self):
        self.project.move(old_pos=self.i, new_pos=len(self.project.todos))
        self.i = len(self.project.todos) - 1

    @hotkey(key='s', alt = True)
    def sort_todo_list(self):
        self.project.sort()

    @hotkey(key='w', mode='normal')
    def schedule_to_today(self):
        self.project.schedule(self.i, date=date.today())

    @hotkey(key='h', mode='normal')
    def move_schedule_prev(self):
        if self.todos[self.i].done:
            if self.todos[self.i].completed_at is None:
                self.todos[self.i].completed_at = date.today()
            self.todos[self.i].completed_at -= timedelta(days=1)
        else:
            if self.todos[self.i].scheduled_at is None:
                self.schedule_to_today()
            self.todos[self.i].scheduled_at -= timedelta(days=1)

    @hotkey(key='l', mode='normal')
    def move_schedule_next(self):
        if self.todos[self.i].done:
            if self.todos[self.i].completed_at is None:
                self.todos[self.i].completed_at = date.today()
            self.todos[self.i].completed_at += timedelta(days=1)
        else:
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
        if self.visible_row_count - 1 <= self.i - self.start_i:
            self.start_i += 1

    @hotkey(key='k', mode='normal')
    def move_up(self):
        self.i = max(self.i - 1, 0)
        if self.i < self.start_i:
            self.start_i -= 1

    @hotkey(key='t', mode='normal')
    def move_to_top(self):
        self.i = 0

    @hotkey(key='b', mode='normal')
    def move_to_bottom(self):
        self.i = len(self.todos) - 1

    @hotkey(key=' ', mode='normal')
    def toggle_todo(self):
        self.todos[self.i].done = not self.todos[self.i].done
        self.todos[self.i].completed_at = date.today()

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
        if len(self.todos) != 1:
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
    def handle_editing(self, name: str, key: str, ctrl: bool, alt: bool):
        if self.mode == 'edit':
            if name == 'KEY_ENTER' or name == 'KEY_ESCAPE' or (key == '[' and ctrl):
                self.mode = 'normal' 
            elif name == 'KEY_BACKSPACE':
                text = self.todos[self.i].text
                self.todos[self.i].text = text[:self.edit_cursor-1] + text[self.edit_cursor:]
                self.edit_cursor = max(0, self.edit_cursor - 1)
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
        start_i = self.start_i
        if start_i != 0:
            print(" ... ")

        end_i = start_i + self.visible_row_count

        for i, todo in enumerate(self.todos[start_i:end_i], start_i):
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
                        print(self.term.on_snow + self.term.black + ' ' + self.term.normal)
                    continue

                print(self.term.on_snow + self.term.black, end='')
            print(f'[{"x" if todo.done else " "}] {todo.text}', end='')

            if todo.done:
                todo_date = todo.completed_at
                date_color = self.term.green
            else:
                todo_date = todo.scheduled_at
                date_color = self.term.yellow
                if todo_date and todo_date < date.today():
                    date_color = self.term.orange
            if todo_date:
                print(date_color + f' {human_date(todo_date)}', end='')
            print(self.term.normal)

        if len(self.todos) > end_i: 
            print(" ... ")


    def on_start(self):
        self.project = self.storage.load()


    def on_exit(self):
        self.storage.save(self.project)

