import json
from dataclasses import dataclass, asdict

import blessed

term = blessed.Terminal()

@dataclass
class Todo:
    text: str
    done: bool

with term.hidden_cursor(), term.cbreak():
    mode = 'normal' # can be also 'edit'
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
                if mode == 'edit':
                    print(f'[{"x" if todo.done else " "}] {todo.text}', end='')
                    # and cursor
                    print(term.on_snow + term.black + ' ' + term.normal)
                    continue

                print(term.on_snow + term.black, end='')
            print(f'[{"x" if todo.done else " "}] {todo.text}')
            print(term.normal)

        key = term.inkey()

        if key.is_ctrl('n'):
            if selected_num != len(todos) - 1:
                todos[selected_num], todos[selected_num+1] = todos[selected_num+1], todos[selected_num]
                selected_num += 1
            continue

        if key.is_ctrl('p'):
            if selected_num != 0:
                selected_num -= 1
                todos[selected_num], todos[selected_num+1] = todos[selected_num+1], todos[selected_num]
            continue

        if mode == 'edit':
            if key.name == 'KEY_ESCAPE' or key.name == 'KEY_ENTER' or key.is_ctrl('['):
                mode = 'normal'
                continue

            if key.name == 'KEY_BACKSPACE':
                todos[selected_num].text = todos[selected_num].text[:-1]
                continue
            
            if not key.is_sequence:
                todos[selected_num].text += key
            continue


        if key == 'q':
            break

        if key == 'j':
            selected_num = min(selected_num + 1, len(todos) - 1)

        if key == 'k':
            selected_num = max(selected_num - 1, 0)

        if key == ' ':
            todos[selected_num].done = not todos[selected_num].done

        if key == 'a':
            todos = [Todo('', False)] + todos
            selected_num = 0
            mode = 'edit'

        if key == 'd':
            # TODO: delete confirmation
            todos = todos[:selected_num] + todos[selected_num+1:]
            selected_num = min(selected_num, len(todos) - 1)


print(term.clear, end='')

with open(filename, 'w') as f:
    json.dump([asdict(todo) for todo in todos], f, indent=4)

