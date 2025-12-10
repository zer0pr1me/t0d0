from dataclasses import asdict
from pathlib import Path
import json

from platformdirs import user_config_dir
from screens.screen import Screen, hotkey
from screens.todo_screen import TodoScreen
from model.config import Config, TodolistConfig
from model.todoapp import TodoApp

from blessed import Terminal
from dacite import from_dict

APP_NAME = 't0d0'
CONFIG_FILE = Path(user_config_dir(APP_NAME)) / 'config.json'

class MenuScreen(Screen):
    def __init__(self, term: Terminal):
        super().__init__(term)
        self.i = 0

    def render(self):
        print("TODOLISTS")
        print("==========================")
        print()
        for i, todolist in enumerate(self.config.todolists):
            if i == self.i:
                print(self.term.on_snow + self.term.black, end='')
            print(self.term.move_xy(0, i+3), end='')
            print(f'{todolist.name}: {todolist.dir}')
            print(self.term.normal)

    def on_start(self):
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                self.config = from_dict(data_class=Config, data=json.load(f))

        else:
            self.config = Config(todolists = [TodolistConfig(name='default', dir='.')])


    def on_exit(self):
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(asdict(self.config), f, indent=4)

    @hotkey(key='q')
    def quit(self):
        self.exit()

    @hotkey(key='o')
    def open_todolist(self):
        self.to_screen(TodoScreen(self.term, TodoApp(self.config.todolists[self.i].dir)))

