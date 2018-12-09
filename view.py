#!/usr/bin/env python
"""
A simple application that shows a Pager application.
"""
from __future__ import unicode_literals

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import LayoutDimension as D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea, SearchToolbar
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles.named_colors import NAMED_COLORS
from asyncio import get_event_loop
from prompt_toolkit.eventloop import use_asyncio_event_loop
from prompt_toolkit.output import Output

import pendulum
import re
from etmMVC.model import WeekView


etmstyle = {
    'plain':        'Beige',
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
        return s[0]
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

# file = "./test/schedule.txt"
# with open(file, 'rb') as f:
#     content = f.read().decode('utf-8')

weekview = WeekView(plain=True)
content = "".join(weekview.agenda_view)

current_datetime = pendulum.now().format("YYYYMMDD")
def event_handler(loop):
    global current_datetime
    now = pendulum.now()
    tmp = now.format("YYYYMMDD")
    if tmp != current_datetime:
        current_datetime = tmp
        weekview.refreshRelevant()
    wait = 60 - now.second
    # text_area.text = now.format("h:mmA ddd MMM D").center(58, ' ') + "\n" + content
    # text_area.text = content
    # Output.set_title(t, 'left')
    loop.call_later(wait, event_handler, loop)

def get_statusbar_text():
    return [
        # ('class:status',"line: "),
        ('class:status', '[{}]'.format(
            text_area.document.cursor_position_row)),
        ('class:status', ' Press '),
        ('class:status.key', 'F1'),
        ('class:status', ' for help, '),
        ('class:status.key', '/'),
        ('class:status', ' to search or '),
        ('class:status.key', 'q'),
        ('class:status', ' to exit'),
    ]


search_field = SearchToolbar(text_if_not_searching=[
    ('class:not-searching', "Press '/' to start searching.")])

def get_line_prefix(linenum, wrap=2):
    return(str(linenum).rjust(2, ' ') + " ") # if not linenum % 5 else "    "

text_area = TextArea(
    text=content,
    read_only=True,
    scrollbar=True,
    # get_line_prefix=get_line_prefix,
    # line_numbers=True,
    search_field=search_field,
    lexer=ETMLexer()
    )


root_container = HSplit([
    # The main content.
    text_area,
    # The top toolbar.
    Window(content=FormattedTextControl(
        get_statusbar_text),
        height=D.exact(1),
        style='class:status'),

    search_field,
])


# Key bindings.
bindings = KeyBindings()


@bindings.add('q')
@bindings.add('f8')
def _(event):
    " Quit. "
    event.app.exit()

@bindings.add('n')
def nextweek(event):
    weekview.nextYrWk()
    text_area.text = "".join(weekview.agenda_view)


@bindings.add('p')
def prevweek(event):
    weekview.prevYrWk()
    text_area.text = "".join(weekview.agenda_view)

@bindings.add('space')
def currweek(event):
    weekview.currYrWk()
    text_area.text = "".join(weekview.agenda_view)

style = Style.from_dict({
    'status': '{} bg:{}'.format(NAMED_COLORS['White'], NAMED_COLORS['DimGrey']),
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