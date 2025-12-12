from dataclasses import asdict
import json
from pathlib import Path

from model.todo import Todo
from todolist.todolist import TodoList

class JsonTodoList(TodoList):
    def __init__(self, name: str, dirname: str):
        super().__init__(name)
        self.dir = Path(dirname)
        self.todo_file = self.dir / 'todo-list.json'

    def save(self):
        self.dir.mkdir(parents=True, exist_ok=True)
        with open(self.todo_file, 'w') as f:
            json.dump([asdict(todo) for todo in self.todos], f, indent=4)

    def load(self):
        if not self.todo_file.exists():
            self.todos = []
            return
        with open(self.todo_file, 'r') as f:
            self.todos = [Todo(**todo) 
                            for todo in json.load(f)]
