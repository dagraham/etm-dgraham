#!/usr/bin/env python
"""
A simple application that shows a Pager application.
"""
from __future__ import unicode_literals

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window, ConditionalContainer
from prompt_toolkit.layout.controls import FormattedTextControl, BufferControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea, SearchToolbar 
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles.named_colors import NAMED_COLORS
from asyncio import get_event_loop
from prompt_toolkit.eventloop import use_asyncio_event_loop
from prompt_toolkit.filters import Condition
from prompt_toolkit.application.current import get_app

import pendulum
import re
from model import DataView, drop_zero_minutes
from help import show_help

ampm = True
showing_help = False

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



current_datetime = status_time(dataview.now)

def event_handler(loop):
    global current_datetime
    current_today = dataview.now.format("YYYYMMDD")
    now = pendulum.now()
    current_datetime = status_time(now)
    today = now.format("YYYYMMDD")
    if today != current_today:
        dataview.refreshRelevant()
        dataview.refreshAgenda()
    get_app().invalidate()
    wait = 60 - now.second
    loop.call_later(wait, event_handler, loop)

def get_statusbar_text():
    space = ' ' * (58 - 7 - len(current_datetime))
    return [
            ('class:status', f' {current_datetime}{space}F1:help'),
    ]

def get_details_text():
    tmp = dataview.get_details(text_area.document.cursor_position_row)
    return [('class:details', tmp),]
    return tmp


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

# help_area = TextArea(
#     text=show_help(),
#     style='class:details', multiline=True,
#     wrap_lines=True, focus_on_click=True, 
#     )

# details_area = Window(content=FormattedTextControl(
#         get_details_text),
#         style='class:details')

details_area = TextArea(
    text=dataview.get_details(text_area.document.cursor_position_row),
    style='class:details', 
    read_only=True,
    scrollbar=True,
    search_field=search_field,
    # focus_on_click=True, 
    )

help_area = TextArea(
    text=show_help(),
    style='class:details', 
    read_only=True,
    scrollbar=True,
    search_field=search_field,
    # focus_on_click=True, 
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
    search_field,
])

# Key bindings.
bindings = KeyBindings()


@bindings.add('Q')
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


# @bindings.add('d')
# def toggle_details(event):
#     dataview.hide_details() if dataview.details else dataview.show_details()

@bindings.add('a', filter=is_not_searching & not_showing_details)
def toggle_agenda_busy(event):
    set_text(dataview.toggle_agenda_busy())

@bindings.add('h', filter=is_not_searching & not_showing_details)
def agenda_view(event):
    dataview.set_active_view('h')
    # text_area.text = dataview.show_active_view()
    set_text(dataview.show_active_view())

@bindings.add('right', filter=is_agenda_view & is_not_searching & not_showing_details)
def nextweek(event):
    dataview.nextYrWk()
    # text_area.text = dataview.show_active_view()
    set_text(dataview.show_active_view())


@bindings.add('left', filter=is_agenda_view & is_not_searching & not_showing_details)
def prevweek(event):
    dataview.prevYrWk()
    # text_area.text = dataview.show_active_view()
    set_text(dataview.show_active_view())

@bindings.add('space', filter=is_agenda_view & is_not_searching & not_showing_details)
def currweek(event):
    dataview.currYrWk()
    # text_area.text = dataview.show_active_view()
    set_text(dataview.show_active_view())

@bindings.add('enter', filter=is_not_searching & is_not_busy_view & not_showing_help)
def show_details(event):
    if dataview.details:
        application.layout.focus(text_area)
        dataview.hide_details()
    else:
        tmp = dataview.get_details(text_area.document.cursor_position_row)
        if tmp:
            dataview.show_details()
            details_area.text = tmp.rstrip()
            application.layout.focus(details_area)


style = Style.from_dict({
    'status': '{} bg:{}'.format(NAMED_COLORS['White'], NAMED_COLORS['DimGrey']),
    'details': '{}'.format(NAMED_COLORS['Ivory']),
    'status.position': '#aaaa00',
    'status.key': '#ffaa00',
    'not-searching': '#888888',
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
    # run()
    main()