import json
from dataclasses import dataclass, asdict

from textual.app import App, ComposeResult
from textual import events
from textual.widgets import Checkbox

@dataclass
class Todo:
    text: str
    done: bool

class MyApp(App):
    filename = 'todo-list.json'
    selected_index = 0

    def compose(self) -> ComposeResult:
        with open(self.filename, 'r') as f:
            self.todos = [Todo(**todo) 
                          for todo in json.load(f)]

        for i, todo in enumerate(self.todos):
            yield Checkbox(todo.text, 
                           todo.done, 
                           id=f'todo{i}')

    def on_key(self, event: events.Event) -> None:
        if event.key == 'space':
            todo = self.todos[self.selected_index]
            todo.done = not todo.done
            checkbox = self.query_one(f'#todo{self.selected_index}') 
            todo.value = todo.done
        else:
            new_selected_index = self.selected_index
            if event.key == 'j':
                new_selected_index += 1
            elif event.key == 'k':
                new_selected_index -= 1


            if new_selected_index < 0 or new_selected_index >= len(self.todos):
                return

            selected = self.query_one(f'#todo{new_selected_index}')
            self.selected_index = new_selected_index
            selected.focus()

        with open(self.filename, 'w') as f:
            json.dump([asdict(todo) for todo in self.todos], f, indent=4)

if __name__ == '__main__':
    app = MyApp()
    app.run()
