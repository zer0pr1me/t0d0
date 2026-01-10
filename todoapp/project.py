from typing import List
from datetime import date

from model.todo import Todo

class Project:
    def __init__(self, todos: List[Todo]):
        self.todos = todos

    def swap(self, i: int, j: int):
        self.todos[i], self.todos[j] = self.todos[j], self.todos[i]

    def move(self, old_pos: int, new_pos: int):
        item = self.todos[old_pos]
        self.todos = self.todos[:old_pos] + self.todos[old_pos+1:]
        self.todos = self.todos[:new_pos] + [item] + self.todos[new_pos:]

    def sort(self):
        def _key(todo: Todo) -> int:
            score = 0
            if todo.done:
                score -= 1_000_000

            if todo.done:
                if todo.completed_at:
                    score += (todo.completed_at - date.today()).days
                else:
                    score -= 1_000_000
            else:
                score += 1_000_000
                if todo.scheduled_at:
                    score += (todo.scheduled_at - date.today()).days

            return score

        self.todos = sorted(self.todos, key=_key)

    def schedule(self, i: int, date: date):
        # TODO: use separate function for setting completion
        if self.todos[i].done:
            self.todos[i].completed_at = date
        else:
            self.todos[i].scheduled_at = date

