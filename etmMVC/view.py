#!/usr/bin/env python
"""
A user interface based on prompt_toolkit.
"""
from __future__ import unicode_literals

import sys
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign, ConditionalContainer
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.dimension import D
# from prompt_toolkit.buffer import Buffer
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea, SearchToolbar, MenuContainer, MenuItem
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles.named_colors import NAMED_COLORS
from asyncio import get_event_loop
from prompt_toolkit.eventloop import use_asyncio_event_loop
from prompt_toolkit.eventloop import Future, ensure_future, Return, From

from prompt_toolkit.filters import Condition
from prompt_toolkit.application.current import get_app
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.completion import Completion, Completer
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout import Dimension
from prompt_toolkit.widgets import HorizontalLine
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous  
import shutil

from prompt_toolkit.layout import FloatContainer, Float
from prompt_toolkit.widgets import Dialog, Label, Button


import pendulum
import re
from model import wrap, format_time, format_datetime

import logging
import logging.config
logger = logging.getLogger()

from sixmonthcal import sixmonthcal

from model import about

import subprocess # for check_output

class TextInputDialog(object):
    def __init__(self, title='', label_text='', padding=10, completer=None):
        self.future = Future()

        def accept_text(buf):
            get_app().layout.focus(ok_button)
            buf.complete_state = None
            return True

        def accept():
            self.future.set_result(self.text_area.text)

        def cancel():
            self.future.set_result(None)

        self.text_area = TextArea(
            completer=completer,
            multiline=False,
            width=D(preferred=shutil.get_terminal_size()[0]-padding),
            accept_handler=accept_text)

        ok_button = Button(text='OK', handler=accept)
        cancel_button = Button(text='Cancel', handler=cancel)

        self.dialog = Dialog(
            title=title,
            body=HSplit([
                Label(text=label_text),
                self.text_area
            ]),
            buttons=[ok_button, cancel_button],
            width=D(preferred=shutil.get_terminal_size()[0]-10),
            modal=True)

    def __pt_container__(self):
        return self.dialog


class MessageDialog(object):
    def __init__(self, title="", text="", padding=10):
        self.future = Future()

        def set_done():
            self.future.set_result(None)

        ok_button = Button(text='OK', handler=(lambda: set_done()))

        self.dialog = Dialog(
            title=title,
            body=HSplit([
                Label(text=text),
            ]),
            buttons=[ok_button],
            width=D(preferred=shutil.get_terminal_size()[0]-padding),
            modal=True)

    def __pt_container__(self):
        return self.dialog

def show_message(title, text, padding):
    def coroutine():
        dialog = MessageDialog(title, text, padding)
        yield From(show_dialog_as_float(dialog))

    ensure_future(coroutine())


def show_dialog_as_float(dialog):
    " Coroutine. "
    float_ = Float(content=dialog)
    root_container.floats.insert(0, float_)

    app = get_app()

    focused_before = app.layout.current_window
    app.layout.focus(dialog)
    result = yield dialog.future
    app.layout.focus(focused_before)

    if float_ in root_container.floats:
        root_container.floats.remove(float_)

    raise Return(result)

# Key bindings.
bindings = KeyBindings()

@bindings.add('f2')
def do_about(*event):
    show_message('ETM Information', about(2)[0], 0)

@bindings.add('f3')
def do_system(*event):
    show_message('System Information', about(22)[1], 20)

@bindings.add('f5')
def do_alerts(*event):
    show_message("Today's Alerts", alerts(), 2)

@bindings.add('f6')
def do_go_to(*event):
    def coroutine():
        dialog = TextInputDialog(
            title='Go to line',
            label_text='Line number:')

        line_number = yield From(show_dialog_as_float(dialog))
        if line_number:
            try:
                line_number = int(line_number)
            except ValueError:
                show_message('go to line', 'Invalid line number')
            else:
                text_area.buffer.cursor_position = \
                    text_area.buffer.document.translate_row_col_to_index(line_number - 1, 0)

    ensure_future(coroutine())

today = pendulum.today()
calyear = today.year
calmonth = today.month

@bindings.add('f7')
def do_show_calendar(*event):
    # FIXME
    show_message("Six Month Calendar", sixmonthcal(0), 9)
    # def coroutine():
    #     global calyear, calmonth
    #     dialog = TextInputDialog(
    #         title='Show six month calendar',
    #         label_text='year, month:')

    #     yearmonth = yield From(show_dialog_as_float(dialog))

    #     if yearmonth:
    #         try:
    #             y, m = [int(x) for x in yearmonth.split(',')]
    #         except ValueError:
    #             show_message('invalid year, month', 'using current')
    #         else:
    #             calyear = y
    #             calmonth = m

    # ensure_future(coroutine())
    # focus_next()


def check_output(cmd):
    if not cmd:
        return
    try:
        subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as exc:
        logger.error("command: {0}\n    output: {1}".format(cmd, exc.output))

editing = False

@bindings.add('f1')
def menu(event):
    " Focus menu. "
    event.app.layout.focus(root_container.window)

@Condition
def is_editing():
    return dataview.is_editing

@Condition
def is_not_editing():
    return not dataview.is_editing

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
    return dataview.is_showing_details == False

@Condition
def is_showing_details():
    return dataview.is_showing_details

bindings.add('tab', filter=is_not_editing)(focus_next)
bindings.add('s-tab', filter=is_not_editing)(focus_previous)

@bindings.add('g', filter=is_agenda_view & is_not_editing)
def do_go_to_date(*event):
    def coroutine():
        dialog = TextInputDialog(
            title='Go to date',
            label_text='date:')

        target_date = yield From(show_dialog_as_float(dialog))

        try:
            dataview.dtYrWk(target_date)
        except ValueError:
            show_message('go to date', 'Invalid date')
        else:
            set_text(dataview.show_active_view())


    ensure_future(coroutine())

terminal_style = None

dark_style = Style.from_dict({
    'dialog':             f"bg:{NAMED_COLORS['DimGrey']} {NAMED_COLORS['White']}",
    'dialog frame-label': 'bg:#ffffff #000000',
    'dialog.body':        f"bg:{NAMED_COLORS['DimGrey']} {NAMED_COLORS['White']}",
    'dialog shadow':      'bg:#444444',

    'status':     f"bg:{NAMED_COLORS['DimGrey']} {NAMED_COLORS['White']}",
    'details':    f"{NAMED_COLORS['Ivory']}",
    'status.position': '#aaaa00',
    'status.key': '#ffaa00',
    'not-searching': '#888888',
    'entry':      f"{NAMED_COLORS['LightGoldenRodYellow']}",
    'ask':        f"{NAMED_COLORS['Lime']} bold",
    'reply':      f"{NAMED_COLORS['DeepSkyBlue']}",

    'window.border': '#888888',
    'shadow':        'bg:#222222',

    'menu-bar': f"bg:{NAMED_COLORS['DimGrey']} {NAMED_COLORS['White']}",
    'menu-bar.selected-item': 'bg:#ffffff #000000',
    'menu': f"bg:{NAMED_COLORS['DimGrey']} {NAMED_COLORS['White']}",
    'menu.border': '#aaaaaa',
    'window.border shadow': '#444444',

    'focused  button': 'bg:#880000 #ffffff noinherit',
    })

light_style = Style.from_dict({
    'dialog':             f"bg:{NAMED_COLORS['DimGrey']} {NAMED_COLORS['White']}",
    'dialog frame-label': 'bg:#ffffff #000000',
    'dialog.body':        f"bg:{NAMED_COLORS['DimGrey']} {NAMED_COLORS['White']}",
    'dialog shadow':      'bg:#444444',

    'status': f"bg:{NAMED_COLORS['DimGrey']} {NAMED_COLORS['White']}",
    'details': f"{NAMED_COLORS['Black']}",
    'status.position': '#aaaa00',
    'status.key': '#ffaa00',
    'not-searching': '#888888',
    'entry': f"{NAMED_COLORS['Black']}",
    'ask':   f"{NAMED_COLORS['DarkGreen']} bold",
    'reply': f"{NAMED_COLORS['Blue']}",

    'window.border': '#888888',
    'shadow': 'bg:#222222',

    'menu-bar': f"bg:{NAMED_COLORS['DimGrey']} {NAMED_COLORS['White']}",
    'menu-bar.selected-item': 'bg:#ffffff #000000',
    'menu': f"bg:{NAMED_COLORS['DimGrey']} {NAMED_COLORS['White']}",
    'menu.border': '#aaaaaa',
    'window.border shadow': '#444444',

    'focused  button': 'bg:#880000 #ffffff noinherit',
    })


dark_etmstyle = {
    'plain':        'Ivory',
    'inbox':        'LightCoral',
    'pastdue':      'DeepSkyBlue',
    'begin':        'Khaki',
    'record':       'BurlyWood',
    'event':        'LimeGreen',
    'available':    'DodgerBlue',
    'waiting':      'SlateGrey',
    'finished':     'DarkGrey',
    'today':        f"{NAMED_COLORS['Ivory']} bold",
}


light_etmstyle = {
    'plain':        'Black',
    'inbox':        'Crimson',
    'pastdue':      'FireBrick',
    'begin':        'IndianRed',
    'record':       'DarkGoldenRod',
    'event':        'Green',
    'available':    'Blue',
    'waiting':      'DarkSlateBlue',
    'finished':     'LightSlateGrey',
    'today':        f"{NAMED_COLORS['Black']} bold",
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
        return None
    else:
        return None

# Create one text buffer for the main content.
class ETMLexer(Lexer):
    def lex_document(self, document):

        def get_line(lineno):
            tmp = document.lines[lineno]
            typ = first_char(tmp)
            if typ in type2style:
                return [(etmstyle[type2style[typ]], tmp)]
            if tmp.rstrip().endswith("(Today)"):
                return [(etmstyle['today'], f"{tmp} ")]
            return [(etmstyle['plain'], tmp)]
            # return [(etmstyle[type2style.get(typ, 'plain')], tmp)]

        return get_line

def status_time(dt):
    """
    >>> status_time(parse('2018-03-07 10am'))
    '10'
    >>> status_time(parse('2018-03-07 2:45pm'))
    '2:45'
    """
    ampm = settings['ampm']
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

def item_changed(loop):
    item.update_item_hsh()
    data_changed(loop)

def data_changed(loop):
    dataview.refreshRelevant()
    dataview.refreshAgenda()
    set_text(dataview.show_active_view())
    get_app().invalidate()

def new_day(loop):
    dataview.possible_archive()
    dataview.set_active_view('a')
    dataview.refreshRelevant()
    dataview.activeYrWk = dataview.currentYrWk
    dataview.refreshAgenda()
    set_text(dataview.show_active_view())
    get_app().invalidate()
    dataview.handle_backups()

current_datetime = pendulum.now('local')

def alerts():
    alerts = []
    now = pendulum.now('local')
    for alert in dataview.alerts:
        trigger_time = pendulum.instance(alert[0])
        start_time = pendulum.instance(alert[1])
        if start_time.date() == now.date():
            start = format_time(start_time)[1]
        else:
            start = format_datetime(start_time, short=True)[1]
        trigger = format_time(trigger_time)[1]
        command = ", ".join(alert[2])
        summary = alert[3]
        prefix = '<' if trigger_time < now else '>'
        alerts.append(f"{prefix} {trigger} ({command}) {summary} {start}")
    if alerts:
        return "\n".join(alerts)
    else:
        return "There are no alerts for today."


def maybe_alerts(now):
    global current_datetime
    for alert in dataview.alerts:
        logger.debug(f"settings alerts: {settings['alerts']}")
        if alert[0].hour == now.hour and alert[0].minute == now.minute:
            logger.debug(f"{alert}")
            startdt = alert[1]
            if not isinstance(startdt, pendulum.DateTime):
                # rrule produces datetime.datetime objects
                startdt = pendulum.instance(startdt)
            when = startdt.diff_for_humans()
            start = format_datetime(startdt)[1]
            summary = alert[3]
            doc_id = alert[4]
            command_list = alert[2]
            item = dataview.dbquery.get(doc_id=doc_id)
            location = item.get('l', '')
            description = item.get('d', '')
            if 'e' in command_list:
                command_list.remove('e')
                dataview.send_mail(doc_id)
            if 't' in command_list:
                command_list.remove('t')
                dataview.send_text(doc_id)
            commands = [settings['alerts'].get(x, "").format(start=start, when=when, summary=summary, location=location, description=description) for x in command_list]

            logger.info(f"alert now: {now.microsecond}, startdt: {startdt.microsecond}, when: {when}, commands: {commands}, summary: {summary}, doc_id: {doc_id}")
            for command in commands:
                if command:
                    check_output(command)

def event_handler(loop):
    global current_datetime
    current_today = dataview.now.format("YYYYMMDD")
    now = pendulum.now()
    maybe_alerts(now)
    current_datetime = status_time(now)
    today = now.format("YYYYMMDD")
    if today != current_today:
        loop.call_later(0, new_day, loop)
    get_app().invalidate()
    wait = 60 - now.second
    loop.call_later(wait, event_handler, loop)


def get_statusbar_text():
    return [ ('class:status',  f' {current_datetime}'), ]


def get_statusbar_right_text():
    return [ ('class:status',  f'{dataview.active_view} '), ]


search_field = SearchToolbar(text_if_not_searching=[
    ('class:not-searching', "Press '/' to start searching.")], ignore_case=True)

content = ""
text_area = TextArea(
    text="",
    read_only=True,
    scrollbar=True,
    search_field=search_field,
    focus_on_click=True,
    lexer=ETMLexer()
    )

details_area = TextArea(
    text="",
    style='class:details', 
    read_only=True,
    search_field=search_field,
    )


animal_completer = WordCompleter([
    'alligator', 'ant', 'ape', 'bat', 'bear', 'beaver', 'bee', 'bison',
    'butterfly', 'cat', 'chicken', 'crocodile', 'dinosaur', 'dog', 'dolphin',
    'dove', 'duck', 'eagle', 'elephant', 'fish', 'goat', 'gorilla', 'kangaroo',
    'leopard', 'lion', 'mouse', 'rabbit', 'rat', 'snake', 'spider', 'turkey',
    'turtle', '@i personal:exercise:tennis', '_tennis'
    ], ignore_case=True)

# completions will actually come from prior database entries 
completions = [
        ]

# expansions will actually come from cfg.yaml
expansions = {
        }

class AtCompleter(Completer):
    # pat = re.compile(r'@[cgilntxz]\s?\S*')
    pat = re.compile(r'@[cgilntxz]\s?[^@&]*')

    def get_completions(self, document, complete_event):
        cur_line = document.current_line_before_cursor
        logger.info(f"cur_line: {cur_line}")
        matches = re.findall(AtCompleter.pat, cur_line)
        word = matches[-1] if matches else ""
        if word:
            word_len = len(word)
            word = word.rstrip()
            logger.info(f"word: '{word}'")
            for completion in completions:
                if word.startswith('@x') and completion.startswith(word):
                    if completion == word:
                        replacement = expansions.get(word[3:], completion)
                        logger.info(f"== word completion: '{completion}'; replacement: '{replacement}'")
                        yield Completion(
                            replacement,
                            start_position=-word_len)
                    else:
                        logger.info(f"!= word completion: '{completion}'")
                        yield Completion(
                            completion,
                            start_position=-word_len)

                elif completion.startswith(word) and completion != word:
                    logger.info(f"!= word completion: '{completion}'")
                    yield Completion(
                        completion,
                        start_position=-word_len)


at_completer = AtCompleter()

result = ""
def process_input(buf):
    global result
    result = buf.document.text
    return True

edit_bindings = KeyBindings()
ask_buffer = Buffer()
entry_buffer = Buffer(multiline=True, completer=at_completer, complete_while_typing=True, accept_handler=process_input)

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
    """
    item.text_changed(entry_buffer.text, entry_buffer.cursor_position)

def default_cursor_position_changed(_):
    """
    """
    item.cursor_changed(entry_buffer.cursor_position)
    set_askreply('_')

entry_buffer.on_text_changed += default_buffer_changed
entry_buffer.on_cursor_position_changed += default_cursor_position_changed


status_area = VSplit([
            Window(FormattedTextControl(get_statusbar_text), style='class:status'),
            Window(FormattedTextControl(get_statusbar_right_text),
                   style='class:status', width=20, align=WindowAlign.RIGHT),
        ], height=1)


body = HSplit([
    text_area,      # main content
    status_area,    # toolbar
    ConditionalContainer(
        content=details_area,
        filter=is_showing_details & is_not_busy_view),
    ConditionalContainer(
        content=edit_container,
        filter=is_editing),
    search_field,
    ])

item_not_selected = False

@bindings.add('D', filter=is_not_editing)
def delete_item(*event):
    global item
    if dataview.is_showing_details:
        application.layout.focus(text_area)
        dataview.hide_details()
    doc_id, entry = dataview.get_details(text_area.document.cursor_position_row, True)
    logger.info(f"deleting doc_id: {doc_id}")
    item.delete_item(doc_id)
    loop = get_event_loop()
    loop.call_later(0, data_changed, loop)

@bindings.add('N', filter=is_not_editing)
def edit_new(*event):
    global item
    if dataview.is_showing_details:
        application.layout.focus(text_area)
        dataview.hide_details()
    dataview.is_editing = True
    item.new_item()
    entry_buffer.text = item.entry
    default_buffer_changed(_)
    default_cursor_position_changed(_)
    application.layout.focus(entry_buffer)

@bindings.add('E', filter=is_not_editing)
def edit_existing(*event):
    global item
    if dataview.is_showing_details:
        application.layout.focus(text_area)
        dataview.hide_details()
    dataview.is_editing = True
    doc_id, entry = dataview.get_details(text_area.document.cursor_position_row, True)
    logger.debug(f"editing doc_id: {doc_id}; entry: {entry}")
    item.edit_item(doc_id, entry)
    entry_buffer.text = item.entry
    default_buffer_changed(_)
    default_cursor_position_changed(_)
    application.layout.focus(entry_buffer)

@bindings.add('C', filter=is_not_editing)
def edit_copy(*event):
    global item
    if dataview.is_showing_details:
        application.layout.focus(text_area)
        dataview.hide_details()
    dataview.is_editing = True
    doc_id, entry = dataview.get_details(text_area.document.cursor_position_row, True)
    logger.debug(f"editing copy of doc_id: {doc_id}; entry: {entry}")
    item.edit_copy(doc_id, entry)
    entry_buffer.text = item.entry
    default_buffer_changed(_)
    default_cursor_position_changed(_)
    application.layout.focus(entry_buffer)

@bindings.add('B', filter=is_not_editing)
def whatever(*event):
    dataview.handle_backups()

@bindings.add('c-p')
def play_sound(*event):
    check_output(soundcmd)

@bindings.add('c-q')
def exit(*event):
    application.exit()

@bindings.add('f8')
def _(event):
    " Quit. "
    event.app.exit()

def set_text(txt, row=0):
    text_area.text = txt

@bindings.add('a', filter=is_not_searching & not_showing_details & is_not_editing)
def agenda_view(*event):
    dataview.set_active_view('a')
    set_text(dataview.show_active_view())

@bindings.add('b', filter=is_not_searching & not_showing_details & is_not_editing)
def busy_view(*event):
    dataview.set_active_view('b')
    set_text(dataview.show_active_view())

@bindings.add('h', filter=is_not_searching & not_showing_details & is_not_editing)
def history_view(*event):
    dataview.set_active_view('h')
    set_text(dataview.show_active_view())

@bindings.add('n', filter=is_not_searching & not_showing_details & is_not_editing)
def next_view(*event):
    dataview.set_active_view('n')
    set_text(dataview.show_active_view())

@bindings.add('j', filter=is_not_searching & not_showing_details & is_not_editing)
def journal_view(*event):
    dataview.set_active_view('j')
    set_text(dataview.show_active_view())

@bindings.add('i', filter=is_not_searching & not_showing_details & is_not_editing)
def index_view(*event):
    dataview.set_active_view('i')
    set_text(dataview.show_active_view())

@bindings.add('right', filter=is_agenda_view & is_not_searching & not_showing_details & is_not_editing)
def nextweek(*event):
    dataview.nextYrWk()
    set_text(dataview.show_active_view())

@bindings.add('left', filter=is_agenda_view & is_not_searching & not_showing_details & is_not_editing)
def prevweek(*event):
    dataview.prevYrWk()
    set_text(dataview.show_active_view())

@bindings.add('space', filter=is_agenda_view & is_not_searching & not_showing_details & is_not_editing)
def currweek(*event):
    dataview.currYrWk()
    set_text(dataview.show_active_view())

@bindings.add('enter', filter=is_not_searching & is_not_busy_view & is_not_editing)
def show_details(*event):
    if dataview.is_showing_details:
        application.layout.focus(text_area)
        dataview.hide_details()
    else:
        tmp = dataview.get_details(text_area.document.cursor_position_row)[1]
        if tmp:
            dataview.show_details()
            details_area.text = tmp.rstrip()
            application.layout.focus(details_area)


@bindings.add('c-c', filter=is_editing, eager=True)
def close_edit(event):
    # TODO: warn if item.is_modified
    dataview.is_editing = False
    logger.debug(f"is_modified: {item.is_modified}")
    application.layout.focus(text_area)
    set_text(dataview.show_active_view())

@edit_bindings.add('c-s', filter=is_editing, eager=True)
def save_changes(_):
    logger.debug(f"doc_id {item.doc_id} is_modified: {item.is_modified}")
    if item.is_modified:
        if item.doc_id is not None:
            del dataview.itemcache[item.doc_id]
        loop = get_event_loop()
        loop.call_later(0, item_changed, loop)


root_container = MenuContainer(body=body, menu_items=[
    MenuItem('etm', children=[
        MenuItem('F1) activate menu', disabled=True),
        MenuItem('F2) about etm', handler=do_about),
        MenuItem('F3) system info', handler=do_system),
        MenuItem('F4) preferences', disabled=True),
        MenuItem('F5) check for new version', disabled=True),
        MenuItem('-', disabled=True),
        MenuItem('^Q) quit', handler=exit),
    ]),
    MenuItem('edit', children=[
        MenuItem('N) new item', handler=edit_new),
        MenuItem('-', disabled=True),
        MenuItem('selection', children=[
                MenuItem('E) edit', handler=edit_existing),
                MenuItem('C) edit copy', handler=edit_copy),
                MenuItem('F) finish'),
                MenuItem('R) reschedule'),
                MenuItem('S) schedule new'),
                MenuItem('D) delete', handler=delete_item),
                MenuItem('timer', children=[
                    MenuItem('T) start, pause or restart'),
                    MenuItem("^T) stop & add time to @u"),
            ]),
        ]),
        MenuItem('editor', children=[
            MenuItem('^S) save changes'),
            MenuItem('^C) close'),
        ]),
    ]),
    MenuItem('view', children=[
        MenuItem('weekly', children=[
            MenuItem('a) agenda', handler=agenda_view),
            MenuItem('b) busy', handler=busy_view),
            MenuItem('movement', children=[
                MenuItem('left) previous week', handler=prevweek),
                MenuItem('space) current week', handler=currweek),
                MenuItem('right) next week', handler=nextweek),
                MenuItem('g) go to date', handler=do_go_to_date),
            ]),
        ]),
        MenuItem('h) history', handler=history_view),
        MenuItem('i) index', handler=index_view),
        MenuItem('j) journal', handler=journal_view),
        MenuItem('n) next', handler=next_view),
        MenuItem('q) query', disabled=True),
        MenuItem('r) relevant', disabled=True),
        MenuItem('t) tags', disabled=True),
        MenuItem('selection', children=[
            MenuItem('Enter) toggle details', handler=show_details),
            MenuItem('G) goto link', disabled=True),
            MenuItem('X) export ical to clipboard', disabled=True),
        ]),
        MenuItem('-', disabled=True),
        MenuItem('c) copy to clipboard', disabled=True),
        MenuItem('/) search forward'),
        MenuItem('?) search backward'),
    ]),
    MenuItem('tools', children=[
        MenuItem("F5) show today's alerts", handler=do_alerts),
        MenuItem('F6) open date calculator', disabled=True),
        MenuItem('F7) show yearly calendar', handler=do_show_calendar),
    ]),
], floats=[
    Float(xcursor=True,
          ycursor=True,
          content=CompletionsMenu(
              max_height=16,
              scroll_offset=1)),
])


# This is slick - add a call to default_buffer_changed 
entry_buffer.on_text_changed += default_buffer_changed
entry_buffer.on_cursor_position_changed += default_cursor_position_changed

def set_askreply(_):
    logger.debug(f'item.active: {item.active}')
    if item.active:
        ask, reply = item.askreply[item.active]
    else:
        ask, reply = item.askreply[('itemtype', '')]
    ask_buffer.text = ask
    reply_buffer.text = wrap(reply, 0) 


# create application.
# application = Application(
#     layout=Layout(
#         root_container,
#         focused_element=text_area,
#     ),
#     key_bindings=bindings,
#     enable_page_navigation_bindings=True,
#     mouse_support=True,
#     style=style,
#     full_screen=True)

dataview = None
item = None
settings = None
style = None
etmstyle = None
application = None
def main(etmdir=""):
    global dataview, item, settings, ampm, style, etmstyle, application
    import options
    options.etmdir = etmdir
    import model
    from model import DataView
    dataview = DataView(etmdir)
    settings = dataview.settings
    terminal_style = dataview.settings['style']
    logger.info(f"terminal_style: {terminal_style}")
    if terminal_style == "dark": 
        style = dark_style
        etmstyle = dark_etmstyle
    else:
        style = light_style
        etmstyle = light_etmstyle

    # completions = dataview.completions

    # NOTE: we're setting ampm in model here. How cool is this!!!
    model.ampm = settings['ampm']
    from model import Item
    item = Item(etmdir)
    dataview.refreshCache()
    agenda_view()

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

    # Tell prompt_toolkit to use asyncio.
    use_asyncio_event_loop()
    # Run application async.
    loop = get_event_loop()
    loop.call_later(0, event_handler, loop)
    loop.run_until_complete(
        application.run_async().to_asyncio_future())


if __name__ == '__main__':
    sys.exit('view.py should only be imported')