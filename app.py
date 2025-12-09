import json
from dataclasses import dataclass, asdict

import blessed

term = blessed.Terminal()

@dataclass
class Todo:
    text: str
    done: bool


with term.hidden_cursor(), term.cbreak():
    selected_num = 0
    filename = 'todo-list.json'
    running = True
    with open(filename, 'r') as f:
        todos = [Todo(**todo) 
                 for todo in json.load(f)]

    while running:
        print(term.home + term.clear)

        for i, todo in enumerate(todos):
            print(term.move_xy(0, i), end='')
            if i == selected_num:
                print(term.on_snow + term.black, end='')
            print(f'[{"x" if todo.done else " "}] {todo.text}')
            print(term.normal)

        key = term.inkey()

        if key == 'q':
            break

        if key == 'j':
            selected_num = min(selected_num + 1, len(todos) - 1)

        if key == 'k':
            selected_num = max(selected_num - 1, 0)

        if key == ' ':
            todos[selected_num].done = not todos[selected_num].done

print(term.clear, end='')

with open(filename, 'w') as f:
    json.dump([asdict(todo) for todo in todos], f, indent=4)

