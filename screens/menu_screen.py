from dataclasses import asdict
import json

from screens.screen import Screen
from screens.hotkeys import hotkey
from screens.todo_screen import TodoScreen
from model.config import Config, TodolistConfig
from todolist.todolist import TodoList
from todolist.json_todolist import JsonTodoList
from todolist.config_todolist import ConfigTodoList
from globals import CONFIG_FILE

from blessed import Terminal
from dacite import from_dict


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
            print(self.term.orangered + f'[{todolist.storage_type}] ' + self.term.normal, end='')
            if i == self.i:
                print(self.term.on_snow + self.term.black, end='')
            print(f'{todolist.name}', end='')
            if todolist.storage_type == 'json':
                print(f'=> {todolist.args["dir"]}', end='')
            print()
            print(self.term.normal)

    def on_start(self):
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                self.config = from_dict(data_class=Config, data=json.load(f))

        else:
            self.config = Config(todolists = [TodolistConfig(storage_type='json',
                                                             name='cwd', 
                                                             args={
                                                                'dir': '.',
                                                             })])


    def on_exit(self):
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(asdict(self.config), f, indent=4)

    @hotkey(key='q')
    def quit(self):
        self.exit()

    @hotkey(name='KEY_ENTER')
    @hotkey(key='o')
    def open_todolist(self):
        tl_data = self.config.todolists[self.i]
        if tl_data.storage_type == 'json':
            todolist = JsonTodoList(tl_data.name, tl_data.args['dir'])
        elif tl_data.storage_type == 'config':
            todolist = ConfigTodoList(tl_data.name)
        else:
            raise Exception(f'Unknown todo list storage type: {tl_data.storage_type}')
        self.to_screen(TodoScreen(self.term, todolist))

