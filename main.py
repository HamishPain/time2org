from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.application import get_app
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
import datetime
import time

kb = KeyBindings()

@kb.add('c-i')
def focusNext_(event: KeyPressEvent):
    """
    Pressing Ctrl-Q will exit the user interface.

    Setting a return value means: quit the event loop that drives the user
    interface and return this value from the `Application.run()` call.
    """
    event.app.layout.focus_next()
    # event.app.
    # event.app.exit()

@kb.add('c-\\','t','i','m','e')
def time_(event: KeyPressEvent):
    now = datetime.datetime.now()
    event.app.layout.current_buffer.insert_text(now.strftime("DATE_NOW:%m/%d/%Y,%H:%M:%S"))

@kb.add('c-c','q','u','i','t')
def exit_(event):
    event.app.exit()

buffer1 = Buffer()
buffer2 = Buffer()
root_container = VSplit([
    # One window that holds the BufferControl with the default buffer on
    # the left.
    Window(content=BufferControl(buffer=buffer1)),

    # A vertical line in the middle. We explicitly specify the width, to
    # make sure that the layout engine will not try to divide the whole
    # width by three for all these windows. The window will simply fill its
    # content by repeating this character.
    Window(width=1, char='|'),

    # Display the text 'Hello world' on the right.
    Window(content=BufferControl(buffer=buffer2)),
],)

layout = Layout(root_container,)

app = Application(key_bindings=kb, full_screen=True, layout=layout)
app.run()