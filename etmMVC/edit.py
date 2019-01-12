#!/usr/bin/env python
"""
Simple example of a full screen application with a vertical split.

This will show a window on the left for user input. When the user types, the
reversed input is shown on the right. Pressing Ctrl-Q will quit the application.
"""
from __future__ import unicode_literals

from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import  HSplit, Window
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import HorizontalLine, TextArea

from model import check_entry

# 3. Create the buffers
#    ------------------

ask_buffer = Buffer()
entry_buffer = Buffer(multiline=True)
reply_buffer = Buffer()

# 1. First we create the layout
#    --------------------------

ask_window = Window(BufferControl(buffer=ask_buffer), height=1)
entry_window = Window(BufferControl(buffer=entry_buffer), wrap_lines=True,)
reply_window = Window(BufferControl(buffer=reply_buffer), wrap_lines=True,)


body = HSplit([
    ask_window,
    entry_window,
    HorizontalLine(),
    reply_window,
])

root_container = HSplit([
    body,
])


# 2. Adding key bindings
#   --------------------

# As a demonstration, we will add just a ControlQ key binding to exit the
# application.  Key bindings are registered in a
# `prompt_toolkit.key_bindings.registry.Registry` instance. We use the
# `load_default_key_bindings` utility function to create a registry that
# already contains the default key bindings.

kb = KeyBindings()

# Now add the Ctrl-Q binding. We have to pass `eager=True` here. The reason is
# that there is another key *sequence* that starts with Ctrl-Q as well. Yes, a
# key binding is linked to a sequence of keys, not necessarily one key. So,
# what happens if there is a key binding for the letter 'a' and a key binding
# for 'ab'. When 'a' has been pressed, nothing will happen yet. Because the
# next key could be a 'b', but it could as well be anything else. If it's a 'c'
# for instance, we'll handle the key binding for 'a' and then look for a key
# binding for 'c'. So, when there's a common prefix in a key binding sequence,
# prompt-toolkit will wait calling a handler, until we have enough information.

# Now, There is an Emacs key binding for the [Ctrl-Q Any] sequence by default.
# Pressing Ctrl-Q followed by any other key will do a quoted insert. So to be
# sure that we won't wait for that key binding to match, but instead execute
# Ctrl-Q immediately, we can pass eager=True. (Don't make a habit of adding
# `eager=True` to all key bindings, but do it when it conflicts with another
# existing key binding, and you definitely want to override that behaviour.


@kb.add('c-q', eager=True)
def _(event):
    """
    Pressing Ctrl-Q or Ctrl-C will exit the user interface.

    Setting a return value means: quit the event loop that drives the user
    interface and return this value from the `Application.run()` call.

    Note that Ctrl-Q does not work on all terminals. Sometimes it requires
    executing `stty -ixon`.
    """
    event.app.exit()


# Now we add an event handler that captures change events to the buffer on the
# left. If the text changes over there, we'll update the buffer on the right.


def default_buffer_changed(_):
    """
    When the buffer on the left changes, update the buffer on
    the right. We just reverse the text.
    """
    # reply_buffer.text = entry_buffer.text[::-1]
    set_askreply(_)
    # ask, say = check_entry(entry_buffer.text, entry_buffer.cursor_position)
    # reply_buffer.text = ask[1] + "\n" + say[1] 
    # reply_buffer.text = check_entry(entry_buffer.text, entry_buffer.cursor_position)[1][1]

def default_cursor_position_changed(_):
    """
    When the cursor position in the top changes, update the cursor position in the bottom.
    """
    set_askreply(_)
    # ask, say = check_entry(entry_buffer.text, entry_buffer.cursor_position)
    # reply_buffer.text = ask[1] + "\n" + say[1] 
    # reply_buffer.text = entry_buffer.text + f" ({entry_buffer.cursor_position})"


# This is slick - add a call to default_buffer_changed 
entry_buffer.on_text_changed += default_buffer_changed
entry_buffer.on_cursor_position_changed += default_cursor_position_changed

def set_askreply(_):
    ask, say, hsh = check_entry(entry_buffer.text, entry_buffer.cursor_position)
    ask_buffer.text = ask[1]
    reply_buffer.text = say[1] 

set_askreply('_')

# 3. Creating an `Application` instance
#    ----------------------------------

# This glues everything together.

application = Application(
    layout=Layout(root_container, focused_element=entry_window),
    key_bindings=kb,

    # Let's add mouse support!
    mouse_support=True,

    # Using an alternate screen buffer means as much as: "run full screen".
    # It switches the terminal to an alternate screen.
    full_screen=True)


# 4. Run the application
#    -------------------


def run():
    # Run the interface. (This runs the event loop until Ctrl-Q is pressed.)
    application.run()


if __name__ == '__main__':
    run()