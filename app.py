from textual.app import App, ComposeResult
from textual import events
from textual.widgets import Checkbox

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield Checkbox('Add test TODO items', True)
        yield Checkbox('Implement focusing items', False)
        yield Checkbox('Implement checking unchecking items', False)

if __name__ == '__main__':
    app = MyApp()
    app.run()
