from abc import ABC, abstractmethod

class TodoList(ABC):
    def __init__(self, name: str):
        self.todos = []
        self.name = name

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def load(self):
        pass


