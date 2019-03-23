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
from prompt_toolkit.widgets import TextArea, Frame, RadioList, SearchToolbar, MenuContainer, MenuItem
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles.named_colors import NAMED_COLORS
from asyncio import get_event_loop
from prompt_toolkit.eventloop import use_asyncio_event_loop
from prompt_toolkit.eventloop import Future, ensure_future, Return, From

from prompt_toolkit.filters import Condition
from prompt_toolkit.application.current import get_app
# from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.completion import Completion, Completer
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout import Dimension
from prompt_toolkit.widgets import HorizontalLine
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous  
import shutil

# from prompt_toolkit.layout import FloatContainer
from prompt_toolkit.layout import Float
from prompt_toolkit.widgets import Dialog, Label, Button


import pendulum
from pendulum import parse as pendulum_parse
def parse(s, **kwd):
    return pendulum_parse(s, strict=False, **kwd)

import re
# from model import wrap, format_time, format_datetime
# from model import wrap

import logging
# import logging.config
logger = logging.getLogger()

import subprocess # for check_output

# for openWithDefault
import platform
import os

cfgfile = '' # override this

class InteractiveInputDialog(object):
    def __init__(self, title='', help_text='', evaluator=None, padding=10, completer=None):
        self.future = Future()

        def cancel():
            self.future.set_result(None)

        self.output_field = TextArea(
                text='',
                focusable=False,
                )
        self.input_field = TextArea(
            height=1, prompt='>>> ', multiline=False,
            focusable=True,
            wrap_lines=False)

        def accept(buff):
            # Evaluate "calculator" expression.
            try:
                output = 'In:  {}\nOut: {}\n\n'.format(
                    self.input_field.text,
                    evaluator(self.input_field.text))  
            except BaseException as e:
                output = '\n\n{}'.format(e)
            new_text = self.output_field.text + output

            # Add text to output buffer.
            self.output_field.buffer.text = new_text

        self.input_field.accept_handler = accept

        cancel_button = Button(text='Cancel', handler=cancel)

        self.dialog = Dialog(
            title=title,
            body=HSplit([
                Label(text=help_text),
                self.output_field,
                HorizontalLine(),
                self.input_field,
            ]),
            buttons=[cancel_button],
            width=D(preferred=shutil.get_terminal_size()[0]-padding),
            modal=True)

    def __pt_container__(self):
        return self.dialog


class TextInputDialog(object):
    def __init__(self, title='', label_text='', default='', padding=10, completer=None):
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
            text=default,
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
            # buttons=[ok_button],
            width=D(preferred=shutil.get_terminal_size()[0]-10),
            modal=True)

    def __pt_container__(self):
        return self.dialog

class RadioListDialog(object):
    def __init__(self, title='', text='', label='', values=[], padding=4, completer=None):
        self.future = Future()

        self.radios = RadioList(values=values)
        # radios.current_value will contain the first component of the selected tuple 
        # title = "Delete"
        # values =[
        #     (0, 'this instance'),
        #     (1, 'this and all subsequent instances'),
        #     (2, 'this and all previous instances'),
        #     (3, 'all instances - the item itself'),
        # ]

        def accept():
            self.future.set_result(self.radios.current_value)

        def cancel():
            self.future.set_result(None)


        ok_button = Button(text='OK', handler=accept)
        cancel_button = Button(text='Cancel', handler=cancel)

        self.dialog = Dialog(
            title=title,
            body=HSplit([
                Label(text=text),
                Frame(title=label, body=self.radios)
            ]),
            # body= Frame(title=label, body=self.radios),
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


class ConfirmDialog(object):
    def __init__(self, title="", text="", padding=10):
        self.future = Future()

        def set_yes():
            self.future.set_result(True)
        def set_no():
            self.future.set_result(False)

        yes_button = Button(text='Yes', handler=(lambda: set_yes()))
        no_button = Button(text='No', handler=(lambda: set_no()))

        self.dialog = Dialog(
            title=title,
            body=HSplit([
                Label(text=text),
            ]),
            buttons=[yes_button, no_button],
            width=D(preferred=shutil.get_terminal_size()[0]-padding),
            modal=True)

    def __pt_container__(self):
        return self.dialog

def show_message(title, text, padding=6):
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


def show_confirm_as_float(dialog):
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
    show_message('etm information', about(2)[0], 0)

@bindings.add('f3')
def do_check_updates(*event):
    res = check_output("pip search etm-dgraham")
    info =  "".join( chr(x) for x in res)
    show_message("version information", info, 2)

@bindings.add('f4')
def do_system(*event):
    show_message('system information', about(22)[1], 20)

@bindings.add('f5')
def do_alerts(*event):
    show_message("today's alerts", alerts(), 2)


@bindings.add('f6')
def datetime_calculator(*event):
    def coroutine():
        prompt = """\
Enter an expression of the form:
    x [+-] y
where x is a datetime and y is either
    [+] a timeperiod
    [-] a datetime or a timeperiod
Be sure to surround [+-] with spaces.
Timezones can be appended to x and y.
        """
        dialog = InteractiveInputDialog(
            title='datetime calculator',
            help_text=prompt,
            evaluator=datetime_calculator,
            padding=4,
            )
        yield From(show_dialog_as_float(dialog))

    ensure_future(coroutine())

# @bindings.add('f6')
# def do_open_config(*event):
#     openWithDefault(cfgfile)

def save_before_quit(*event):
    def coroutine():
        dialog = ConfirmDialog("unsaved changes", "Save them before closing?")

        save_changes = yield From(show_dialog_as_float(dialog))
        if save_changes:
            if item.doc_id is not None:
                # del dataview.itemcache[item.doc_id]
                dataview.itemcache[item.doc_id] = {}
            dataview.is_editing = False
            application.layout.focus(text_area)
            set_text(dataview.show_active_view())
            loop = get_event_loop()
            loop.call_later(0, item_changed, loop)

    ensure_future(coroutine())

today = pendulum.today()
calyear = today.year
calmonth = today.month

def check_output(cmd):
    if not cmd:
        return
    try:
        res = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as exc:
        res = "".join( chr(x) for x in exc.output)
        logger.error("command: {0}\n    output: {1}".format(cmd, res))
    finally:
        return res

editing = False

@Condition
def is_viewing():
    return get_app().layout.has_focus(text_area) 

@Condition
def is_viewing_or_details():
    return get_app().layout.has_focus(text_area) or get_app().layout.has_focus(details_area) 


@bindings.add('f1')
def menu(event):
    " Focus menu. "
    if not event.app.layout.has_focus(root_container.window):
        event.app.layout.focus(root_container.window)
    else:
        focus_previous(event)


@Condition
def is_item_view():
    return dataview.active_view in ['agenda', 'completed', 'history', 'index', 'journal', 'do next', 'relevant']

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
    return dataview.active_view in ['agenda', 'busy', 'completed']

@Condition
def is_yearly_view():
    return dataview.active_view in ['yearly']

@Condition
def is_not_yearly_view():
    return not dataview.active_view in ['yearly']

@Condition
def not_showing_details():
    return dataview.is_showing_details == False

@Condition
def is_showing_details():
    return dataview.is_showing_details

bindings.add('tab', filter=is_not_editing)(focus_next)
bindings.add('s-tab', filter=is_not_editing)(focus_previous)


@bindings.add('l', filter=is_viewing)
def do_go_to_line(*event):
    def coroutine():
        default = ''
        if dataview.current_row:
            default = dataview.current_row + 1 
        dialog = TextInputDialog(
            title='Go to line',
            label_text='Line number:',
            default=str(default))

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


@bindings.add('g', filter=is_viewing_or_details)
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
    'not-searching': '#222222',
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
    'not-searching': '#777777',
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
    if not s.strip():
        # nothing but whitespace
        return None
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
    '10am Wed Mar 7'
    >>> status_time(parse('2018-03-07 2:45pm'))
    '2:45pm Wed Mar 7'
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
    dataview.refreshCurrent()
    if dataview.current_row:
        text_area.buffer.cursor_position = text_area.buffer.document.translate_row_col_to_index(dataview.current_row, 0)
    get_app().invalidate()

def new_day(loop):
    logger.info(f"new_day currentYrWk: {dataview.currentYrWk}")
    dataview.refreshRelevant()
    dataview.activeYrWk = dataview.currentYrWk
    dataview.refreshAgenda()
    dataview.set_active_view('a')
    set_text(dataview.show_active_view())
    get_app().invalidate()
    dataview.handle_backups()
    dataview.possible_archive()

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
        prefix = '#' if trigger_time < now else ' '
        alerts.append(f"{prefix} {trigger} ({command}) {summary} {start}")
    if alerts:
        return "\n".join(alerts)
    else:
        return "There are no alerts for today."


def maybe_alerts(now):
    global current_datetime
    if dataview.alerts and not ('alerts' in settings and settings['alerts']):
        logger.warn("alerts have not been configured")
        return
    for alert in dataview.alerts:
        if alert[0].hour == now.hour and alert[0].minute == now.minute:
            alertdt = alert[0] 
            if not isinstance(alertdt, pendulum.DateTime):
                # rrule produces datetime.datetime objects
                alertdt = pendulum.instance(alertdt)
            startdt = alert[1]
            if not isinstance(startdt, pendulum.DateTime):
                # rrule produces datetime.datetime objects
                startdt = pendulum.instance(startdt)
            # when = startdt.diff_for_humans()
            if startdt >= alertdt:
                when = f"in {(startdt-alertdt).in_words()}"
            else:
                when = f"{(alertdt-startdt).in_words()} ago"
            start = format_datetime(startdt)[1]
            summary = alert[3]
            doc_id = alert[4]
            command_list = alert[2]
            item = dataview.db.get(doc_id=doc_id)
            location = item.get('l', '')
            description = item.get('d', '')
            if 'e' in command_list:
                command_list.remove('e')
                dataview.send_mail(doc_id)
            if 't' in command_list:
                command_list.remove('t')
                dataview.send_text(doc_id)
            commands = [settings['alerts'].get(x).format(start=start, when=when, summary=summary, location=location, description=description) for x in command_list]

            for command in commands:
                if command:
                    check_output(command)

def event_handler(loop):
    global current_datetime
    now = pendulum.now()
    current_today = dataview.now.format("YYYYMMDD")
    maybe_alerts(now)
    current_datetime = status_time(now)
    today = now.format("YYYYMMDD")
    if today != current_today:
        logger.debug(f"calling new_day. current_today: {current_today}; today: {today}")
        loop.call_later(0, new_day, loop)
    get_app().invalidate()
    wait = 60 - now.second
    loop.call_later(wait, event_handler, loop)


def get_statusbar_text():
    return [ ('class:status',  f' {current_datetime}'), ]


def get_statusbar_right_text():
    return [ ('class:status',  f"{dataview.timer_report()}{dataview.active_view} "), ]

def openWithDefault(path):
    sys_platform = platform.system()
    windoz = sys_platform in ('Windows', 'Microsoft')
    mac =  sys_platform == 'Darwin'
    if windoz:
        os.startfile(path)
        return()

    if mac:
        cmd = 'open' + f" {path}"
    else:
        cmd = 'xdg-open' + f" {path}"
    res = check_output(cmd)
    return res

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


# completions will come from prior database entries 
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
        matches = re.findall(AtCompleter.pat, cur_line)
        word = matches[-1] if matches else ""
        if word:
            word_len = len(word)
            word = word.rstrip()
            for completion in completions:
                if word.startswith('@x') and completion.startswith(word):
                    if completion == word:
                        replacement = expansions.get(word[3:], completion)
                        yield Completion(
                            replacement,
                            start_position=-word_len)
                    else:
                        yield Completion(
                            completion,
                            start_position=-word_len)

                elif completion.startswith(word) and completion != word:
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

@bindings.add('S', filter=is_viewing_or_details)
def do_schedule_new(*event):
    doc_id, instance, job = dataview.get_row_details(text_area.document.cursor_position_row)

    if not doc_id:
        return

    hsh = DBITEM.get(doc_id=doc_id)

    def coroutine():
        dialog = TextInputDialog(
            title='schedule new instance',
            label_text=f"selected: {hsh['itemtype']} {hsh['summary']}\n\nnew datetime:")

        new_datetime = yield From(show_dialog_as_float(dialog))

        if not new_datetime:
            return 
        changed = False
        ok, dt, z = parse_datetime(new_datetime)

        if ok:
            changed = item.schedule_new(doc_id, dt)
        else:
            show_message('new instance', f"'{new_datetime}' is invalid")

        if changed:
            if doc_id in dataview.itemcache:
                del dataview.itemcache[doc_id]
            application.layout.focus(text_area)
            set_text(dataview.show_active_view())
            loop = get_event_loop()
            loop.call_later(0, data_changed, loop)


    ensure_future(coroutine())


@bindings.add('R', filter=is_viewing_or_details)
def do_reschedule(*event):
    doc_id, instance, job = dataview.get_row_details(text_area.document.cursor_position_row)

    if not doc_id:
        return

    hsh = DBITEM.get(doc_id=doc_id)

    def coroutine():
        dialog = TextInputDialog(
            title='reschedule instance',
            label_text=f"selected: {hsh['itemtype']} {hsh['summary']}\ninstance: {format_datetime(instance)[1]}\n\nnew datetime:")

        new_datetime = yield From(show_dialog_as_float(dialog))

        if not new_datetime:
            return 
        changed = False
        ok, dt, z = parse_datetime(new_datetime)

        if ok:
            changed = item.reschedule(doc_id, instance, dt)
        else:
            show_message('new instance', f"'{new_datetime}' is invalid")

        if changed:
            if doc_id in dataview.itemcache:
                del dataview.itemcache[doc_id]
            application.layout.focus(text_area)
            set_text(dataview.show_active_view())
            loop = get_event_loop()
            loop.call_later(0, data_changed, loop)


    ensure_future(coroutine())


@bindings.add('D', filter=is_viewing_or_details & is_item_view)
def do_maybe_delete(*event):
    doc_id, instance, job = dataview.get_row_details(text_area.document.cursor_position_row)

    if not doc_id:
        return

    hsh = DBITEM.get(doc_id=doc_id)

    if not instance:
        # not repeating
        def coroutine():
            dialog = ConfirmDialog("Delete", 
                    f"Selected: {hsh['itemtype']} {hsh['summary']}\n\nAre you sure you want to delete this item?\nThis would remove the item from the database\nand cannot be undone.")

            delete = yield From(show_dialog_as_float(dialog))
            if delete:
                item.delete_item(doc_id)
                if doc_id in dataview.itemcache:
                    del dataview.itemcache[doc_id]
                application.layout.focus(text_area)
                set_text(dataview.show_active_view())
                loop = get_event_loop()
                loop.call_later(0, data_changed, loop)

        ensure_future(coroutine())

    if instance:
        # repeating
        def coroutine():

            # radios.current_value will contain the first component of the selected tuple 
            title = "Delete"
            text = f"Selected: {hsh['itemtype']} {hsh['summary']}\nInstance: {format_datetime(instance)[1]}\n\nDelete what?"
            values =[
                (0, 'just this instance'),
                (1, 'the item itself'),
            ]

            dialog = RadioListDialog(
                title=title,
                text=text,
                values=values)

            which = yield From(show_dialog_as_float(dialog))
            if which is not None:
                changed = item.delete_instances(doc_id, instance, which)
                if changed:
                    if doc_id in dataview.itemcache:
                        del dataview.itemcache[doc_id]
                    application.layout.focus(text_area)
                    set_text(dataview.show_active_view())
                    loop = get_event_loop()
                    loop.call_later(0, data_changed, loop)

        ensure_future(coroutine())


@bindings.add('N', filter=is_viewing)
def edit_new(*event):
    global item
    if dataview.is_showing_details:
        application.layout.focus(text_area)
        dataview.hide_details()
    dataview.is_editing = True
    item.new_item()
    entry_buffer.text = item.entry
    default_buffer_changed(event)
    default_cursor_position_changed(event)
    application.layout.focus(entry_buffer)


# @bindings.add('E', filter=is_not_editing)
@bindings.add('E', filter=is_viewing_or_details & is_item_view)
def edit_existing(*event):
    global item
    if dataview.is_showing_details:
        application.layout.focus(text_area)
        dataview.hide_details()
    dataview.is_editing = True
    doc_id, entry = dataview.get_details(text_area.document.cursor_position_row, True)
    logger.info(f"doc_id: {doc_id}; entry: {entry}")
    item.edit_item(doc_id, entry)
    entry_buffer.text = item.entry
    default_buffer_changed(event)
    default_cursor_position_changed(event)
    application.layout.focus(entry_buffer)

@bindings.add('t', filter=is_viewing_or_details & is_item_view)
def do_timer_toggle(*event):
    dataview.timer_toggle(text_area.document.cursor_position_row)


@bindings.add('T', filter=is_viewing_or_details)
def do_maybe_record_timer(*event):
    if not dataview.timer_id:
        return
    item_id = dataview.timer_id
    job_id = dataview.timer_job
    hsh = DBITEM.get(doc_id=item_id)
    item_info = f"{hsh['itemtype']} {hsh['summary']}"

    now = pendulum.now()
    if dataview.timer_status == 1: #running
        time = dataview.timer_time + (now - dataview.timer_start)
    else:
        time = dataview.timer_time
    completed = pendulum.now()
    completed_str = format_datetime(completed)
    time_str = format_duration(time)

    def coroutine():
        dialog = ConfirmDialog("record time", f"item: {item_info}\nelapsed time: {time_str}\n\nrecord time and close timer?")
        record_close = yield From(show_dialog_as_float(dialog))
        if record_close:
            item.record_timer(item_id, job_id, completed, time)
            set_text(dataview.show_active_view())
            dataview.timer_clear()
            if item_id in dataview.itemcache:
                del dataview.itemcache[item_id]
            loop = get_event_loop()
            loop.call_later(0, data_changed, loop)

    ensure_future(coroutine())

@bindings.add('c-t', filter=is_viewing_or_details)
def do_maybe_cancel_timer(*event):
    if not dataview.timer_id:
        return
    item_id = dataview.timer_id
    job_id = dataview.timer_job
    hsh = DBITEM.get(doc_id=item_id)
    item_info = f"{hsh['itemtype']} {hsh['summary']}"

    stopped_timer = False
    now = pendulum.now()
    if dataview.timer_status == 1: #running
        time = dataview.timer_time + (now - dataview.timer_start)
    else:
        time = dataview.timer_time
    completed = pendulum.now()
    completed_str = format_datetime(completed)
    time_str = format_duration(time)

    def coroutine():
        dialog = ConfirmDialog("cancel timer", f"item: {item_info}\nelapsed time: {time_str}\n\nclose timer without recording?")
        record_cancel = yield From(show_dialog_as_float(dialog))
        if record_cancel:
            dataview.timer_clear()
            set_text(dataview.show_active_view())
            get_app().invalidate()

    ensure_future(coroutine())


@bindings.add('F', filter=is_viewing_or_details & is_item_view)
def do_finish(*event):

    ok, show, item_id, job_id, due = dataview.maybe_finish(text_area.document.cursor_position_row)

    if not ok:
        return

    def coroutine():

        dialog = TextInputDialog(
            title='finish task/job',
            label_text=f"selected: {show}\ndatetime completed:")

        done_str = yield From(show_dialog_as_float(dialog))
        if done_str:
            try:
                done = parse_datetime(done_str)[1]
            except ValueError:
                show_message('Finish task/job?', 'Invalid finished datetime')
            else:
                # valid done
                item.finish_item(item_id, job_id, done, due)
                # dataview.itemcache[item.doc_id] = {}
                if item_id in dataview.itemcache:
                    del dataview.itemcache[item_id]
                loop = get_event_loop()
                loop.call_later(0, data_changed, loop)

    ensure_future(coroutine())

@bindings.add('C', filter=is_viewing_or_details & is_item_view)
def edit_copy(*event):
    global item
    if dataview.is_showing_details:
        application.layout.focus(text_area)
        dataview.hide_details()
    dataview.is_editing = True
    doc_id, entry = dataview.get_details(text_area.document.cursor_position_row, True)
    item.edit_copy(doc_id, entry)
    entry_buffer.text = item.entry
    default_buffer_changed(event)
    default_cursor_position_changed(event)
    application.layout.focus(entry_buffer)

@bindings.add('c-g', filter=is_viewing_or_details & is_item_view)
def do_goto(*event):
    row = text_area.document.cursor_position_row
    ok, goto = dataview.get_goto(row)
    if ok:
        res = openWithDefault(goto)
        logger.debug(f"res: {res}")
        if res:
            show_message("goto", res, 8)
    else:
        show_message("goto", goto, 8)

@bindings.add('c-g', filter=is_editing)
def check_goto(*event):
    ok, goto = item.check_goto_link()
    if ok:
        res = openWithDefault(goto)
        if res:
            show_message("goto", res, 8)
    else:
        show_message('goto', goto, 8)

@bindings.add('c-r', filter=is_viewing_or_details & is_item_view)
def not_editing_reps(*event):
    row = text_area.document.cursor_position_row
    res = dataview.get_repetitions(row, 5)
    if not res:
        return
    showing, reps = res 
    show_message(showing, reps, 24)

@bindings.add('c-r', filter=is_editing)
def is_editing_reps(*event):
    res = item.get_repetitions(5)
    if not res:
        return
    showing, reps = res 
    show_message(showing, reps, 24)


@bindings.add('f7')
def do_import_text(*event):
    # TODO: add dialog
    msg = ""
    def coroutine():
        global msg
        dialog = TextInputDialog(
            title='import text',
            label_text='Enter the path of the text file to import:')

        text_file = yield From(show_dialog_as_float(dialog))
        logger.info(f"got {text_file}")

        if text_file:
            logger.info(f"importing from {text_file}")
            msg = import_text(text_file)
            if msg:
                dataview.refreshRelevant()
                dataview.refreshAgenda()
                dataview.refreshCurrent()
                loop = get_event_loop()
                loop.call_later(0, data_changed, loop)
                show_message('import text', msg)
    ensure_future(coroutine())



@bindings.add('f8')
def do_import_json(*event):
    # TODO: add dialog
    msg = ""
    def coroutine():
        global msg
        dialog = TextInputDialog(
            title='import json',
            label_text='Enter the path of the json file to import:')

        json_file = yield From(show_dialog_as_float(dialog))

        if json_file:
            logger.info(f"importing from {json_file}")
            msg = import_json(json_file)
            if msg:
                dataview.refreshRelevant()
                dataview.refreshAgenda()
                dataview.refreshCurrent()
                loop = get_event_loop()
                loop.call_later(0, data_changed, loop)
                show_message('import json', msg)
    ensure_future(coroutine())


@bindings.add('c-p')
def do_whatever(*event):
    """
    For testing whatever
    """
    # row = text_area.document.cursor_position_row
    # dataview.get_row_details(row)
    dataview.possible_archive()

@bindings.add('c-q')
def exit(*event):
    application.exit()

# @bindings.add('f8')
# def _(event):
#     " Quit. "
#     event.app.exit()

def set_text(txt, row=0):
    text_area.text = txt

@bindings.add('a', filter=is_viewing)
def agenda_view(*event):
    dataview.set_active_view('a')
    set_text(dataview.show_active_view())

@bindings.add('c', filter=is_viewing)
def completed_view(*event):
    dataview.set_active_view('c')
    set_text(dataview.show_active_view())

@bindings.add('b', filter=is_viewing)
def busy_view(*event):
    dataview.set_active_view('b')
    set_text(dataview.show_active_view())

@bindings.add('y', filter=is_viewing)
def yearly_view(*event):
    dataview.set_active_view('y')
    set_text(dataview.show_active_view())

@bindings.add('h', filter=is_viewing)
def history_view(*event):
    dataview.set_active_view('h')
    set_text(dataview.show_active_view())

@bindings.add('r', filter=is_viewing)
def relevant_view(*event):
    dataview.set_active_view('r')
    set_text(dataview.show_active_view())

@bindings.add('d', filter=is_viewing)
def next_view(*event):
    dataview.set_active_view('d')
    set_text(dataview.show_active_view())

@bindings.add('j', filter=is_viewing)
def journal_view(*event):
    dataview.set_active_view('j')
    set_text(dataview.show_active_view())

@bindings.add('i', filter=is_viewing)
def index_view(*event):
    dataview.set_active_view('i')
    set_text(dataview.show_active_view())

@bindings.add('right', filter=is_agenda_view & is_viewing)
def nextweek(*event):
    dataview.nextYrWk()
    set_text(dataview.show_active_view())

@bindings.add('left', filter=is_agenda_view & is_viewing)
def prevweek(*event):
    dataview.prevYrWk()
    set_text(dataview.show_active_view())

@bindings.add('space', filter=is_agenda_view & is_viewing)
def currweek(*event):
    dataview.currYrWk()
    set_text(dataview.show_active_view())

@bindings.add('right', filter=is_yearly_view & is_viewing)
def nextcal(*event):
    dataview.nextcal()
    set_text(dataview.show_active_view())

@bindings.add('left', filter=is_yearly_view & is_viewing)
def prevcal(*event):
    dataview.prevcal()
    set_text(dataview.show_active_view())

@bindings.add('space', filter=is_yearly_view & is_viewing)
def currcal(*event):
    dataview.currcal()
    set_text(dataview.show_active_view())

@bindings.add('enter', filter=is_viewing_or_details & is_not_yearly_view & is_not_busy_view)
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
def close_edit(*event):
    if item.is_modified:
        save_before_quit()
    item.is_modified = False
    dataview.is_editing = False
    application.layout.focus(text_area)
    set_text(dataview.show_active_view())

@edit_bindings.add('c-s', filter=is_editing, eager=True)
def save_changes(*event):
    if item.is_modified:
        if item.doc_id in dataview.itemcache:
            del dataview.itemcache[item.doc_id]
        dataview.is_editing = False
        application.layout.focus(text_area)
        set_text(dataview.show_active_view())
        loop = get_event_loop()
        loop.call_later(0, item_changed, loop)
    else:
        dataview.is_editing = False
        application.layout.focus(text_area)
        set_text(dataview.show_active_view())


root_container = MenuContainer(body=body, menu_items=[
    MenuItem('etm', children=[
        MenuItem('F1) activate/close menu', handler=menu),
        MenuItem('F2) about etm', handler=do_about),
        MenuItem('F3) check for updates', handler=do_check_updates),
        MenuItem('F4) system info', handler=do_system),
        MenuItem("F5) show today's alerts", handler=do_alerts),
        MenuItem('F6) datetime calculator', handler=datetime_calculator),
        MenuItem('F7) import text file', handler=do_import_text),
        MenuItem('F8) import json file', handler=do_import_json),
        MenuItem('-', disabled=True),
        MenuItem('^q) quit', handler=exit),
    ]),
    MenuItem('view', children=[
        MenuItem('a) agenda', handler=agenda_view),
        MenuItem('b) busy', handler=busy_view),
        MenuItem('c) completed', handler=completed_view),
        MenuItem('d) do next', handler=next_view),
        MenuItem('h) history', handler=history_view),
        MenuItem('i) index', handler=index_view),
        MenuItem('j) journal', handler=journal_view),
        # MenuItem('q) query', disabled=True),
        MenuItem('r) relevant', handler=relevant_view),
        MenuItem('y) yearly', handler=yearly_view),
        MenuItem('-', disabled=True),
        MenuItem('/) search forward'),
        MenuItem('?) search backward'),
        MenuItem('l) go to line number', handler=do_go_to_line),
        MenuItem('-', disabled=True),
        MenuItem('g) goto date in a), b) and c)', handler=do_go_to_date),
        MenuItem('right) next in a), b), c) and m)'),
        MenuItem('left) previous in a), b), c) and m)'),
        MenuItem('space) current in a), b), c) and m)'),
    ]),
    MenuItem('editor', children=[
        MenuItem('N) create new item', handler=edit_new),
        MenuItem('-', disabled=True),
        MenuItem('^s) save changes & close', handler=save_changes),
        MenuItem('^r) show repetitions', handler=is_editing_reps),
        MenuItem('^c) close editor', handler=close_edit),
    ]),
    MenuItem('selected', children=[
        MenuItem('Enter) toggle showing details', handler=show_details),
        MenuItem('E) edit', handler=edit_existing),
        MenuItem('C) edit copy', handler=edit_copy),
        MenuItem('D) delete', handler=do_maybe_delete),
        MenuItem('F) finish', handler=do_finish),
        MenuItem('R) reschedule',  handler=do_reschedule),
        MenuItem('S) schedule new', handler=do_schedule_new),
        MenuItem('^g) open goto', handler=do_goto),
        MenuItem('^r) show repetitions', handler=not_editing_reps),
        MenuItem('-', disabled=True),
        MenuItem('t) timer start, then toggle running/paused', handler=do_timer_toggle),
        MenuItem("^t) cancel timer", handler=do_maybe_cancel_timer),
        MenuItem("T) record time and close timer", handler=do_maybe_record_timer),
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
    if item.active:
        ask, reply = item.askreply[item.active]
    else:
        ask, reply = item.askreply[('itemtype', '')]
    ask_buffer.text = ask
    reply_buffer.text = wrap(reply, 0) 


dataview = None
item = None
style = None
etmstyle = None
application = None
def main(etmdir=""):
    global item, settings, ampm, style, etmstyle, application
    # logger.info(f"archive_after: {settings['archive_after']}")
    ampm = settings['ampm']
    terminal_style = settings['style']
    if terminal_style == "dark": 
        style = dark_style
        etmstyle = dark_etmstyle
    else:
        style = light_style
        etmstyle = light_etmstyle
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