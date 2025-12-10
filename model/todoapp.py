from dataclasses import asdict
import json
from pathlib import Path

from model.todo import Todo

class TodoApp:
    def __init__(self, dirname: str):
        self.todos = []
        self.dir = Path(dirname)

    def save(self):
        with open(self.dir / 'todo-list.json', 'w') as f:
            json.dump([asdict(todo) for todo in self.todos], f, indent=4)

    def load(self):
        with open(self.dir / 'todo-list.json', 'r') as f:
            self.todos = [Todo(**todo) 
                            for todo in json.load(f)]
