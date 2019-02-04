#!/usr/bin/env python
"""
A user interface based on prompt_toolkit.
"""
from __future__ import unicode_literals

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window, ConditionalContainer
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
# from prompt_toolkit.buffer import Buffer
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea, SearchToolbar 
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles.named_colors import NAMED_COLORS
from asyncio import get_event_loop
from prompt_toolkit.eventloop import use_asyncio_event_loop
from prompt_toolkit.filters import Condition
from prompt_toolkit.application.current import get_app
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout import Dimension
from prompt_toolkit.widgets import HorizontalLine

import pendulum
import re
from model import DataView, Item, at_keys, amp_keys, wrap
import logging
import logging.config
logger = logging.getLogger()
from model import setup_logging


from help import show_help

ampm = True
showing_help = False
editing = False

@Condition
def is_editing():
    return editing

@Condition
def is_not_editing():
    return not editing

@Condition
def is_not_searching():
    return not application.layout.is_searching

@Condition
def is_not_busy_view():
    return dataview.active_view != 'busy'

@Condition
def is_agenda_view():
    return dataview.active_view in ['agenda', 'busy']

@Condition
def not_showing_details():
    return dataview.details == False

@Condition
def is_showing_details():
    return dataview.details

@Condition
def is_showing_help():
    return showing_help

@Condition
def not_showing_help():
    return not showing_help

at_completions = [f"@{k}" for k in at_keys]
r_completions = [f"&{k}" for k in amp_keys['r']] 
j_completions = [f"&{k}" for k in amp_keys['j']] 


item_completer = WordCompleter(at_completions + r_completions + j_completions, ignore_case=False)

etmstyle = {
    'plain':        'Ivory',
    'inbox':        'LightCoral',
    'pastdue':      'DeepSkyBlue',
    'begin':        'Khaki',
    'record':       'BurlyWood',
    'event':        'LimeGreen',
    'available':    'DodgerBlue',
    'waiting':      'RoyalBlue',
    'finished':     'DarkGrey',
}

type2style = {
        '!': 'inbox',
        '<': 'pastdue',
        '>': 'begin',
        '%': 'record',
        '*': 'event',
        '-': 'available',
        '+': 'waiting',
        '✓': 'finished',
        }

def first_char(s):
    """
    Return the first non-whitespace character in s.
    """
    m = re.match('(\s+)', s)
    if m:
        return s[len(m.group(0))]
    elif len(s):
        # no leading spaces
        # return s[0]
        return None
    else:
        return None

# Create one text buffer for the main content.
class ETMLexer(Lexer):
    def lex_document(self, document):

        def get_line(lineno):
            tmp = document.lines[lineno]
            typ = first_char(tmp)
            return [(etmstyle[type2style.get(typ, 'plain')], tmp)]

        return get_line

dataview = DataView()
dataview.refreshCache()
content = dataview.agenda_view

def status_time(dt):
    """
    >>> status_time(parse('2018-03-07 10am'))
    '10'
    >>> status_time(parse('2018-03-07 2:45pm'))
    '2:45'
    """
    d_fmt = dt.format("ddd MMM D")
    suffix = dt.format("A").lower() if ampm else ""
    if dt.minute == 0:
        if ampm:
            t_fmt = dt.format("h")
        else:
            t_fmt = dt.format("H")
    else:
        if ampm:
            t_fmt = dt.format("h:mm")
        else:
            t_fmt = dt.format("H:mm")
    return f"{t_fmt}{suffix} {d_fmt}"


def new_day(loop):
    dataview.set_active_view('a')
    dataview.now = pendulum.now()
    dataview.refreshRelevant()
    dataview.refreshAgenda()
    set_text(dataview.show_active_view())
    get_app().invalidate()

current_datetime = status_time(dataview.now)

def event_handler(loop):
    global current_datetime
    current_today = dataview.now.format("YYYYMMDD")
    now = pendulum.now()
    current_datetime = status_time(now)
    today = now.format("YYYYMMDD")
    if today != current_today:
        loop.call_later(0, new_day, loop)
    get_app().invalidate()
    wait = 60 - now.second
    loop.call_later(wait, event_handler, loop)

def get_statusbar_text():
    space = ' ' * (58 - 7 - len(current_datetime))
    return [
            ('class:status', f' {current_datetime}{space}F1:help'),
    ]

# def get_details_text():
#     tmp = dataview.get_details(text_area.document.cursor_position_row)[1]
#     return [('class:details', tmp),]


search_field = SearchToolbar(text_if_not_searching=[
    ('class:not-searching', "Press '/' to start searching.")], ignore_case=True)

text_area = TextArea(
    text=content,
    read_only=True,
    scrollbar=True,
    search_field=search_field,
    focus_on_click=True,
    lexer=ETMLexer()
    )

details_area = TextArea(
    text=dataview.get_details(text_area.document.cursor_position_row)[1],
    style='class:details', 
    read_only=True,
    search_field=search_field,
    )

# edit_area = TextArea(
#     text=dataview.get_details(text_area.document.cursor_position_row),
#     style='class:details', 
#     read_only=False,
#     )

# edit_buff = Buffer(completer=item_completer, complete_while_typing=True, accept_handler=process_input)

edit_bindings = KeyBindings()
item = Item()
ask_buffer = Buffer()
entry_buffer = Buffer(multiline=True)
reply_buffer = Buffer(multiline=True)

reply_dimension = Dimension(min=2, weight=2)
entry_dimension = Dimension(min=3, weight=2)

entry_window = Window(BufferControl(buffer=entry_buffer, focusable=True, focus_on_click=True, key_bindings=edit_bindings), height=entry_dimension, wrap_lines=True, style='class:entry')
ask_window = Window(BufferControl(buffer=ask_buffer, focusable=False), height=1, style='class:ask')
reply_window = Window(BufferControl(buffer=reply_buffer, focusable=False), height=reply_dimension, wrap_lines=True, style='class:reply')

edit_area = HSplit([
    ask_window,
    reply_window,
    HorizontalLine(),
    entry_window,
])

edit_container = HSplit([
    edit_area,
])

def default_buffer_changed(_):
    """
    When the buffer on the left changes, update the buffer on
    the right. We just reverse the text.
    """
    # reply_buffer.text = entry_buffer.text[::-1]
    item.text_changed(entry_buffer.text, entry_buffer.cursor_position)
    # ask, say, hsh = check_entry(entry_buffer.text, entry_buffer.cursor_position)
    # reply_buffer.text = ask[1] + "\n" + say[1] 
    # reply_buffer.text = check_entry(entry_buffer.text, entry_buffer.cursor_position)[1][1]

def default_cursor_position_changed(_):
    """
    When the cursor position in the top changes, update the cursor position in the bottom.
    """
    item.cursor_changed(entry_buffer.cursor_position)
    # ask, say, hsh = check_entry(entry_buffer.text, entry_buffer.cursor_position)
    # reply_buffer.text = ask[1] + "\n" + say[1] 
    # reply_buffer.text = entry_buffer.text + f" ({entry_buffer.cursor_position})"
    set_askreply('_')

entry_buffer.on_text_changed += default_buffer_changed
entry_buffer.on_cursor_position_changed += default_cursor_position_changed

help_area = TextArea(
    text=show_help(),
    style='class:details', 
    read_only=True,
    search_field=search_field,
    )

status_area = Window(content=FormattedTextControl(
        get_statusbar_text),
        height=1,
        style='class:status')

root_container = HSplit([
    text_area,      # main content
    status_area,    # toolbar
    ConditionalContainer(
        content=details_area,
        filter=is_showing_details & is_not_busy_view),
    ConditionalContainer(
        content=help_area,
        filter=not_showing_details & is_showing_help),
    ConditionalContainer(
        content=edit_container,
        filter=is_editing),
    search_field,
])

# Key bindings.
bindings = KeyBindings()

@bindings.add('c-q')
@bindings.add('f8')
def _(event):
    " Quit. "
    event.app.exit()

def set_text(txt, row=0):
    text_area.text = txt

@bindings.add('f1')
def toggle_help(event):
    global showing_help
    showing_help = not showing_help
    if showing_help:
        if not dataview.details:
            dataview.show_details()
        details_area.text = show_help()
        application.layout.focus(details_area)
    else:
        application.layout.focus(text_area)
        dataview.hide_details()

# @bindings.add('backspace', filter=is_showing_help, eager=True)
# def cancel_help(event):
#     global showing_help
#     if showing_help:
#         if dataview.details:
#             dataview.hide_details()
#         showing_help = False
#         application.layout.focus(text_area)

@bindings.add('a', filter=is_not_searching & not_showing_details)
def toggle_agenda_busy(event):
    set_text(dataview.toggle_agenda_busy())

@bindings.add('h', filter=is_not_searching & not_showing_details)
def agenda_view(event):
    dataview.set_active_view('h')
    set_text(dataview.show_active_view())

@bindings.add('l', filter=is_agenda_view & is_not_searching & not_showing_details)
@bindings.add('right', filter=is_agenda_view & is_not_searching & not_showing_details)
def nextweek(event):
    dataview.nextYrWk()
    set_text(dataview.show_active_view())


@bindings.add('j', filter=is_agenda_view & is_not_searching & not_showing_details)
@bindings.add('left', filter=is_agenda_view & is_not_searching & not_showing_details)
def prevweek(event):
    dataview.prevYrWk()
    set_text(dataview.show_active_view())

@bindings.add('k', filter=is_agenda_view & is_not_searching & not_showing_details)
@bindings.add('space', filter=is_agenda_view & is_not_searching & not_showing_details & is_not_editing)
def currweek(event):
    dataview.currYrWk()
    set_text(dataview.show_active_view())

@bindings.add('enter', filter=is_not_searching & is_not_busy_view & not_showing_help)
def show_details(event):
    if dataview.details:
        application.layout.focus(text_area)
        dataview.hide_details()
    else:
        tmp = dataview.get_details(text_area.document.cursor_position_row)[1]
        if tmp:
            dataview.show_details()
            details_area.text = tmp.rstrip()
            application.layout.focus(details_area)

@bindings.add('N', filter=is_not_editing)
def edit(event):
    global editing
    editing = True
    application.layout.focus(entry_buffer)

@bindings.add('E', filter=is_not_editing)
def edit(event):
    global editing
    editing = True
    item_id, entry = dataview.get_details(text_area.document.cursor_position_row)
    item.edit_item(item_id, entry)
    application.layout.focus(entry_buffer)


@edit_bindings.add('c-s', eager=True)
def save_item(_):
    item.update_item_hsh()

# Now we add an event handler that captures change events to the buffer on the
# left. If the text changes over there, we'll update the buffer on the right.

def default_buffer_changed(_):
    """
    When the buffer on the left changes, update the buffer on
    the right. We just reverse the text.
    """
    # reply_buffer.text = entry_buffer.text[::-1]
    item.text_changed(entry_buffer.text, entry_buffer.cursor_position)
    # ask, say, hsh = check_entry(entry_buffer.text, entry_buffer.cursor_position)
    # reply_buffer.text = ask[1] + "\n" + say[1] 
    # reply_buffer.text = check_entry(entry_buffer.text, entry_buffer.cursor_position)[1][1]

def default_cursor_position_changed(_):
    """
    When the cursor position in the top changes, update the cursor position in the bottom.
    """
    item.cursor_changed(entry_buffer.cursor_position)
    # ask, say, hsh = check_entry(entry_buffer.text, entry_buffer.cursor_position)
    # reply_buffer.text = ask[1] + "\n" + say[1] 
    # reply_buffer.text = entry_buffer.text + f" ({entry_buffer.cursor_position})"
    set_askreply('_')


# This is slick - add a call to default_buffer_changed 
entry_buffer.on_text_changed += default_buffer_changed
entry_buffer.on_cursor_position_changed += default_cursor_position_changed

def set_askreply(_):
    logger.info(f'item.active: {item.active}')
    if item.active:
        ask, reply = item.askreply[item.active]
    else:
        ask, reply = item.askreply[('itemtype', '')]
    ask_buffer.text = ask
    reply_buffer.text = wrap(reply, 0) 
    # reply_buffer.text = ('class:status', reply)

# set this first for an empty entry
set_askreply('_')


style = Style.from_dict({
    'status': '{} bg:{}'.format(NAMED_COLORS['White'], NAMED_COLORS['DimGrey']),
    'details': '{}'.format(NAMED_COLORS['Ivory']),
    'status.position': '#aaaa00',
    'status.key': '#ffaa00',
    'not-searching': '#888888',
    'entry': f"{NAMED_COLORS['LightGoldenRodYellow']}",
    'ask':   f"{NAMED_COLORS['Lime']} bold",
    'reply': f"{NAMED_COLORS['DeepSkyBlue']}",
})


# create application.
application = Application(
    layout=Layout(
        root_container,
        focused_element=text_area,
    ),
    key_bindings=bindings,
    enable_page_navigation_bindings=True,
    mouse_support=True,
    style=style,
    full_screen=True)


def run():
    application.run()

def main():
    # Tell prompt_toolkit to use asyncio.
    use_asyncio_event_loop()

    # Run application async.
    loop = get_event_loop()
    loop.call_later(0, event_handler, loop)
    loop.run_until_complete(
        application.run_async().to_asyncio_future())


if __name__ == '__main__':
    import sys
    etmdir = ''
    if len(sys.argv) > 1:
        etmdir = sys.argv.pop(1)
    setup_logging(1, etmdir, 'view_pt.py')
    main()