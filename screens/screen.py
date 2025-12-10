from blessed import Terminal

from collections import defaultdict
from typing import Optional 

def hotkey(name: str = '', key: str = '', mode: Optional[str] = None, ctrl: bool = False):
    def decorator(func):
        if key and name or (not key and not name):
            raise Error('either key or name should be specified')
        func.__hotkey__ = {
            'key': key if key else name,
            'mode': mode,
            'ctrl': ctrl
        }

        return func

    return decorator


class ScreenMeta(type):
    def __new__(cls, name, bases, attrs):
        keymap = defaultdict(dict)
        ctrl_keymap = defaultdict(dict)

        for base in bases:
            keymap.update(base.keymap)

        for attr_name, value in attrs.items():
            hotkey = getattr(value, "__hotkey__", None)
            if hotkey is not None:
                if hotkey['ctrl']:
                    ctrl_keymap[hotkey['mode']][hotkey['key']] = value
                else:
                    keymap[hotkey['mode']][hotkey['key']] = value

        attrs['keymap'] = keymap
        attrs['ctrl_keymap'] = ctrl_keymap
        return super().__new__(cls, name, bases, attrs)


class Screen(metaclass=ScreenMeta):
    def __init__(self, term: Terminal):
        self.term = term
        self.mode = None
        self._dbg_msg = ""
        self._transition_to = None

    def handle_key(self, name: str, key: str, ctrl: bool) -> bool:
        keymap = self.ctrl_keymap if ctrl else self.keymap
        handler = keymap[self.mode].get(key)
        if handler:
            handler(self)
            return True
        elif handler := keymap[self.mode].get(name):
            handler(self)
            return True
        elif handler := keymap[None].get(key):
            handler(self)
            return True
        elif handler := keymap[None].get(name):
            handler(self)
            return True

        return False

    def on_start(self):
        pass

    def render(self):
        pass

    def on_exit(self):
        pass

    def debug_msg(self, msg: str):
        self._dbg_msg = msg

    def run(self):
        with self.term.hidden_cursor(), self.term.cbreak():
            self.on_start()
            self.running = True

            while self.running and not self._transition_to:
                print(self.term.home + self.term.clear)

                if self._dbg_msg != "":
                    print(self._dbg_msg)
                    self.term.inkey()
                    self._dbg_msg = ""
                    continue

                self.render()
                key = self.term.inkey()
                self.handle_key(key.name, key.value, key._ctrl)

            if not self._transition_to:
                print(self.term.clear, end='')
                self.on_exit()

        if self._transition_to:
            self._transition_to.run()

        if self.running:
            self._transition_to = None
            self.run()

    def exit(self):
        self.running = False

    def to_screen(self, screen: 'Screen'):
        self._transition_to = screen
