from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button
from textual.containers import Container

class ColorgenTUI(App):
    """Textual app for colorgen."""

    CSS = """
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            # Add widgets here
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Handle button clicks
        pass

def main() -> None:
    tui = ColorgenTUI()
    tui.run()
