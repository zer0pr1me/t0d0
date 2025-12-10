import json
from dataclasses import asdict

from blessed import Terminal

from model.todo import Todo

class TodoScreen:
    def __init__(self, term: Terminal):
        self.mode = 'normal'
        self.i = 0
        self.filename = 'todo-list.json'
        self.term = term

    def run(self):
        with self.term.hidden_cursor(), self.term.cbreak():
            self.running = True
            with open(self.filename, 'r') as f:
                self.todos = [Todo(**todo) 
                              for todo in json.load(f)]

            while self.running:
                print(self.term.home + self.term.clear)

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

                key = self.term.inkey()

                if key.is_ctrl('n'):
                    if self.i != len(self.todos) - 1:
                        self.todos[self.i], self.todos[self.i+1] = self.todos[self.i+1], self.todos[self.i]
                        self.i += 1
                    continue

                if key.is_ctrl('p'):
                    if self.i != 0:
                        self.i -= 1
                        self.todos[self.i], self.todos[self.i+1] = self.todos[self.i+1], self.todos[self.i]
                    continue

                if key.is_ctrl('t'):
                    i = self.i
                    self.todos = [self.todos[i]] + self.todos[:i] + self.todos[i+1:]
                    self.i = 0

                if key.is_ctrl('b'):
                    i = self.i
                    self.todos = self.todos[:i] + self.todos[i+1:] + [self.todos[i]] 
                    self.i = len(self.todos) - 1

                if self.mode == 'edit':
                    if key.name == 'KEY_ESCAPE' or key.name == 'KEY_ENTER' or key.is_ctrl('['):
                        self.mode = 'normal'
                        continue

                    if key.name == 'KEY_BACKSPACE':
                        self.todos[self.i].text = self.todos[self.i].text[:-1]
                        continue
                    
                    if not key.is_sequence:
                        self.todos[self.i].text += key
                    continue


                if key == 'q':
                    break

                if key == 'j':
                    self.i = min(self.i + 1, len(self.todos) - 1)

                if key == 'k':
                    self.i = max(self.i - 1, 0)

                if key == 't':
                    self.i = 0

                if key == 'b':
                    self.i = len(self.todos) - 1

                if key == ' ':
                    self.todos[self.i].done = not self.todos[self.i].done

                if key == 'a':
                    self.todos = [Todo('', False)] + self.todos
                    self.i = 0
                    self.mode = 'edit'

                if key == 'i':
                    self.mode = 'edit'

                if key == 'd':
                    # TODO: delete confirmation
                    self.todos = self.todos[:self.i] + self.todos[self.i+1:]
                    self.i = min(self.i, len(self.todos) - 1)

        print(self.term.clear, end='')

        with open(self.filename, 'w') as f:
            json.dump([asdict(todo) for todo in self.todos], f, indent=4)




