from time import monotonic

from textual.app import App, ComposeResult
from textual.layout import Container
from textual.reactive import Reactive
from textual.widgets import Button, Header, Footer, Static


class TimeDisplay(Static):
    """A widget to display elapsed time."""

    start_time = Reactive(monotonic)
    time = Reactive.init(0.0)
    total = Reactive(0.0)

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.update_timer = self.set_interval(1 / 60, self.update_time, pause=True)

    def update_time(self) -> None:
        """Method to update time to current."""
        self.time = self.total + (monotonic() - self.start_time)

    def watch_time(self, time: float) -> None:
        """Called when the time attribute changes."""
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        self.update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")

    def start(self) -> None:
        """Method to start (or resume) time updating."""
        self.start_time = monotonic()
        self.update_timer.resume()

    def stop(self):
        """Method to stop the time display updating."""
        self.update_timer.pause()
        self.total += monotonic() - self.start_time
        self.time = self.total

    def reset(self):
        """Method to reset the time display to zero."""
        self.total = 0
        self.time = 0


class Stopwatch(Static):
    """A stopwatch widget."""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        time_display = self.query_one(TimeDisplay)
        if button_id == "start":
            time_display.start()
            self.add_class("started")
        elif button_id == "stop":
            time_display.stop()
            self.remove_class("started")
        elif button_id == "reset":
            time_display.reset()

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        yield TimeDisplay()


class StopwatchApp(App):
    """Manage the timers."""

    def on_load(self) -> None:
        """Called when the app first loads."""
        self.bind("a", "add_stopwatch", description="Add")
        self.bind("r", "remove_stopwatch", description="Remove")
        self.bind("d", "toggle_dark", description="Dark mode")

    def compose(self) -> ComposeResult:
        """Called to ad widgets to the app."""
        yield Header()
        yield Footer()
        yield Container(Stopwatch(), Stopwatch(), Stopwatch(), id="timers")

    def action_add_stopwatch(self) -> None:
        """An action to add a timer."""
        new_stopwatch = Stopwatch()
        self.query_one("#timers").mount(new_stopwatch)
        new_stopwatch.scroll_visible()

    def action_remove_stopwatch(self) -> None:
        """Called to remove a timer."""
        timers = self.query("#timers Stopwatch")
        if timers:
            timers.last().remove()

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark


app = StopwatchApp(css_path="stopwatch.css")
if __name__ == "__main__":
    app.run()
