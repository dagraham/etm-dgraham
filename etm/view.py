#!/usr/bin/env python
"""
A user interface based on prompt_toolkit.
"""
from __future__ import unicode_literals

import sys

# from prompt_toolkit import __version__ as prompt_toolkit_version

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

from pygments.lexer import RegexLexer

from prompt_toolkit.lexers import PygmentsLexer
# from prompt_toolkit.layout import FloatContainer
from prompt_toolkit.layout import Float
from prompt_toolkit.widgets import Dialog, Label, Button

# from asyncio import .get_event_loop
# from prompt_toolkit.eventloop import use_asyncio_event_loop
# from prompt_toolkit.eventloop import Future, ensure_future, Return, From
import asyncio

import pendulum
from pendulum import parse as pendulum_parse
def parse(s, **kwd):
    return pendulum_parse(s, strict=False, **kwd)

import re
# from model import wrap, format_time, format_datetime
# from model import wrap

import subprocess # for check_output

# for openWithDefault
import platform
import os

import pyperclip
logger = None

############ begin query ###############################
from tinydb import where
from tinydb import Query
from pygments.lexer import RegexLexer
from pygments.token import Keyword
from pygments.token import Literal
from pygments.token import Operator
from pygments.token import Comment
from prompt_toolkit.styles import Style
from prompt_toolkit.lexers import PygmentsLexer

etm_style = Style.from_dict({
    'pygments.comment':   '#888888 bold',
    'pygments.keyword': '#009900 bold',
    'pygments.literal':   '#0066ff bold',  #blue
    'pygments.operator':  '#e62e00 bold',  #red
    # 'pygments.keyword':   '#e62e00 bold',  #red
})

class TDBLexer(RegexLexer):

    name = 'TDB'
    aliases = ['tdb']
    filenames = '*.*'
    flags = re.MULTILINE | re.DOTALL

    tokens = {
            'root': [
                (r'(matches|search|equals|more|less|exists|any|all|one)\b', Keyword),
                (r'(itemtype|summary)\b', Literal),
                (r'(and|or|info)\b', Operator),
                ],
            }

class ETMQuery(object):

    def __init__(self):
        self.arg = { 'matches': self.matches,
                'search': self.search,
                'equals': self.equals,
                'more': self.more,
                'less': self.less,
                'exists': self.exists,
                'any': self.in_any,
                'all': self.in_all,
                'one': self.one_of,
                'info': self.info,
                'dt' : self.dt,
                }

        self.op = {
                '=': self.maybe_equal,
                '>': self.maybe_later,
                '<': self.maybe_earlier
                }

        self.lexer = PygmentsLexer(TDBLexer)
        self.style = etm_style
        self.Item = Query()

        self.allowed_commands = ", ".join([x for x in self.arg])

        self.command_details = """\
    matches a b: return items in which field[a] begins
        with regex b 
    search a b: return items in which field[a] contains 
        regex b
    equals a b: return items in which field[a] == b
    more a b: return items in which field[a] >= b
    less a b: return items in which field[a] <= b
    exists a: return items in which field[a] exists
    any a b: return items in which at least one 
        element of field[a] is an element of the list b 
    all a b: return items in which the elements of 
        field[a] contain all the elements of the list b 
    one a b: return items in which the value of 
        field[a] is one of the elements of list b
    info a: return the details of the item whose 
        document id equals the integer a
    dt a b: return items in which the value of field[a] 
        is a date if b = '? date' or a datetime if 
        b = '? time'. Else if b begins with  '>', '='
        or '<' followed by a string following the format 
        'yyyy-mm-dd-HH-MM' then return items where the
        date/time in field[a] bears the specified 
        relation to the string. E.g., 
            dt s < 2020-1-17 
        would return items with @s date/times whose 
        year <= 2020, month <= 1 and month day <= 17. 
        Hours and minutes are ignored when field[a] is
        a date."""

        self.usage = f"""\
Query has components in the format: [~]command a [b]
where "a" is one of the etm fields: itemtype, summary,
or one of the @keys and "command" is one of the 
following:
{self.command_details}
E.g., find items where the summary contains "waldo":
    query: search summary waldo
Precede a command with "~" to negate it. E.g., find 
reminders where the summary does not contain "waldo":
    query: ~search summary waldo
To enter a list of values for "b", simply separate the 
components with spaces. Conversely, to enter a regex 
with a space and avoid its being interpreted as a list, 
replace the space with \s. Components can be joined the 
using "or" or "and". E.g., find reminders where either 
the summary or the entry for @d (description) contains 
"waldo":
    query: search summary waldo or search d waldo
Press 'Enter' to submit a query, close the entry area
and display the results. Press 'q' to reopen the entry
area to submit another query. Submit '?' or 'help' 
to show this display or nothing to quit. In the entry
area, the 'up' and 'down' cursor keys scroll through
previously submitted queries.
"""

    def is_datetime(self, val):
        return isinstance(val, pendulum.DateTime)

    def is_date(self, val):
        return isinstance(val, pendulum.Date) and not isinstance(val, pendulum.DateTime)

    def maybe_equal(self, val, args):
        """
        args = year-month-...-minute
        """
        args = args.split("-")
        # args = list(args)
        if not isinstance(val, pendulum.Date):
            # neither a date or a datetime
            return False
        if args and not val.year == int(args.pop(0)):
            return False
        if args and not val.month == int(args.pop(0)):
            return False
        if args and not val.day == int(args.pop(0)):
            return False
        if isinstance(val, pendulum.DateTime):
            # val has hours and minutes
            if args and not val.hour == int(args.pop(0)):
                return False
            if args and not val.minute == int(args.pop(0)):
                return False
        return True

    def maybe_later(self, val, args):
        """
        args = year-month-...-minute
        """
        args = args.split("-")
        # args = list(args)
        if not isinstance(val, pendulum.Date):
            # neither a date or a datetime
            return False
        if args and not val.year >= int(args.pop(0)):
            return False
        if args and not val.month >= int(args.pop(0)):
            return False
        if args and not val.day >= int(args.pop(0)):
            return False
        if isinstance(val, pendulum.DateTime):
            # val has hours and minutes
            if args and not val.hour >= int(args.pop(0)):
                return False
            if args and not val.minute >= int(args.pop(0)):
                return False
        return True

    def maybe_earlier(self, val, args):
        """
        args = year-month-...-minute
        """
        args = args.split("-")
        # args = list(args)
        if not isinstance(val, pendulum.Date):
            # neither a date or a datetime
            return False
        if args and not val.year <= int(args.pop(0)):
            return False
        if args and not val.month <= int(args.pop(0)):
            return False
        if args and not val.day <= int(args.pop(0)):
            return False
        if isinstance(val, pendulum.DateTime):
            # val has hours and minutes
            if args and not val.hour <= int(args.pop(0)):
                return False
            if args and not val.minute <= int(args.pop(0)):
                return False
        return True


    def matches(self, a, b):
        # the value of at least one element of field 'a' begins with the case-insensitive regex 'b'
        return where(a).matches(b, flags=re.IGNORECASE)

    def search(self, a, b):
        # the value of at least one element of field 'a' contains the case-insensitive regex 'b'
        return where(a).search(b, flags=re.IGNORECASE)

    def equals(self, a, b):
        # the value of at least one element of field 'a' equals 'b'
        try:
            b = int(b)
        except:
            pass
        return where(a) == b

    def more(self, a, b):
        # the value of at least one element of field 'a' >= 'b'
        try:
            b = int(b)
        except:
            pass
        return where(a) >= b

    def less(self, a, b):
        # the value of at least one element of field 'a' equals 'b'
        try:
            b = int(b)
        except:
            pass
        return where(a) <= b

    def exists(self, a):
        # field 'a' exists
        return where(a).exists()


    def in_any(self, a, b):
        """
        the value of field 'a' is a list of values and at least 
        one of them is an element from 'b'. Here 'b' should be a list with
        2 or more elements. With only a single element, there is no 
        difference between any and all.

        With egs, "any,  blue, green" returns all three items.
        """

        if not isinstance(b, list):
            b = [b]
        return where(a).any(b)

    def in_all(self, a, b):
        """
        the value of field 'a' is a list of values and among the list 
        are all the elements in 'b'. Here 'b' should be a list with
        2 or more elements. With only a single element, there is no 
        difference between any and all.

        With egs, "all, blue, green" returns just "blue and green"
        """
        if not isinstance(b, list):
            b = [b]
        return where(a).all(b)

    def one_of(self, a, b):
        """
        the value of field 'a' is one of the elements in 'b'. 

        With egs, "one, summary, blue, green" returns both "green" and "blue"
        """
        if not isinstance(b, list):
            b = [b]
        return where(a).one_of(b)

    def info(self, a):
        # field 'a' exists
        item = DBITEM.get(doc_id=int(a))
        return  f"{item_details(item, False)}"


    def dt(self, a, b):
        if b[0]  == '?':
            if b[1] == 'time':
                return self.Item[a].test(self.is_datetime)
            elif b[1] == 'date':
                return self.Item[a].test(self.is_date)

        return self.Item[a].test(self.op[b[0]], b[1])

    def process_query(self, query):

        parts = [x.split() for x in re.split(r' (and|or) ', query)]

        cmnds = []
        for part in parts:
            part = [x.strip() for x in part if x.strip()]
            negation = part[0].startswith('~')
            if part[0] not in ['and', 'or']:
                # we have a command
                if negation:
                    # drop the ~
                    part[0] = part[0][1:]
                if self.arg.get(part[0], None) is None:
                    return False, f"""bad command: '{part[0]}'. Only commands in\n {self.allowed_commands}\nare allowed."""

            if len(part) > 3:
                if negation:
                    cmnds.append(~ self.arg[part[0]](part[1], [x.strip() for x in part[2:]]))
                else:
                    cmnds.append(self.arg[part[0]](part[1], [x.strip() for x in part[2:]]))
            elif len(part) > 2:
                if negation:
                    cmnds.append(~ self.arg[part[0]](part[1], part[2]))
                else:
                    cmnds.append(self.arg[part[0]](part[1], part[2]))
            elif len(part) > 1:
                if negation:
                    cmnds.append(~ self.arg[part[0]](part[1]))
                else:
                    cmnds.append(self.arg[part[0]](part[1]))
            else:
                cmnds.append(part[0])

        test = cmnds[0]
        for i in range(1, len(cmnds)):
            if i % 2:
                if cmnds[i] == 'and' or cmnds[i] == 'or':
                    andor = cmnds[i]
                    continue
            if andor == 'or':
                test = test | cmnds[i]
            else:
                test = test & cmnds[i]
        return True, test

    def do_query(self, query):
        """
        For internal usage
        """
        if query == "?" or query == "help":
            return False, self.usage
        try:
            ok, test = self.process_query(query)
            if not ok:
                return False, test
            if isinstance(test, str): 
                # info
                return False, test
            else:
                items = DBITEM.search(test)
                return True, items 
        except Exception as e:
            return False, f"exception processing '{query}':\n{e}"

############# end query ################################


class InteractiveInputDialog(object):
    def __init__(self, title='', help_text='', evaluator=None, padding=10, completer=None):
        self.future = asyncio.Future()

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
        self.future = asyncio.Future()

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
        self.future = asyncio.Future()

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
        self.future = asyncio.Future()

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
        self.future = asyncio.Future()

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
        yield from show_dialog_as_float(dialog)

    asyncio.ensure_future(coroutine())


def show_dialog_as_float(dialog):
    " Coroutine. "
    float_ = Float(content=dialog)
    root_container.floats.insert(0, float_)

    app = get_app()

    focused_before = app.layout.current_window
    app.layout.focus(dialog)
    result = yield from dialog.future
    app.layout.focus(focused_before)

    if float_ in root_container.floats:
        root_container.floats.remove(float_)

    return result


def show_confirm_as_float(dialog):
    " Coroutine. "
    float_ = Float(content=dialog)
    root_container.floats.insert(0, float_)

    app = get_app()

    focused_before = app.layout.current_window
    app.layout.focus(dialog)
    result = yield from dialog.future
    app.layout.focus(focused_before)

    if float_ in root_container.floats:
        root_container.floats.remove(float_)

    return result


# Key bindings.
bindings = KeyBindings()

@bindings.add('f2')
def do_about(*event):
    show_message('etm information', about(2)[0], 0)

@bindings.add('f4')
def do_check_updates(*event):
    res = check_output("pip search etm-dgraham")

    info =  "".join( chr(x) for x in res)
    lines = info.split('\n')
    msg = []
    for line in lines:
        if line.lstrip().startswith('etm-dgraham'):
            msg.append('etm-dgraham')
        elif line.lstrip().startswith('INSTALLED'):
            msg.append(line)
        elif line.lstrip().startswith('LATEST'):
            msg.append(line)

    show_message("version information", "\n".join(msg), 2)

@bindings.add('f3')
def do_system(*event):
    show_message('system information', about(22)[1], 20)


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
        yield from show_dialog_as_float(dialog)

    asyncio.ensure_future(coroutine())

@bindings.add('f7')
def do_open_config(*event):
    openWithDefault(cfgfile)

@bindings.add('f8')
def do_show_help(*event):
    help_link = "https://dagraham.github.io/etm-dgraham/"
    openWithDefault(help_link)

def save_before_quit(*event):
    def coroutine():
        dialog = ConfirmDialog("unsaved changes", "discard changes and close editor?")

        discard = yield from show_dialog_as_float(dialog)
        if discard:
            # we want to discard changes
            if item.doc_id in dataview.itemcache:
                del dataview.itemcache[item.doc_id]
            dataview.is_editing = False
            application.layout.focus(text_area)
            set_text(dataview.show_active_view())
            # the following is probably not needed
            # item.update_item_hsh()
        else:
            # continue editing
            return

    asyncio.ensure_future(coroutine())

def add_usedtime(*event):

    doc_id, instance, job = dataview.get_row_details(text_area.document.cursor_position_row)

    if not doc_id:
        logger.debug('no doc_id')
        return

    hsh = DBITEM.get(doc_id=doc_id)
    logger.debug(f"doc_id: {doc_id}; instance: {instance}; hsh: {hsh}")


    def coroutine():
        dialog = TextInputDialog(
            title='add usedtime',
            label_text=f"selected: {hsh['itemtype']} {hsh['summary']}\n\n add usedtime using the format:\n    used timeperiod: ending datetime")

        usedtime = yield from show_dialog_as_float(dialog)
        logger.debug(f"usedtime: {usedtime}")

        if not usedtime:
            # None (cancelled) or null string
            return

        changed = item.add_used(doc_id, usedtime)

        if changed:
            if doc_id in dataview.itemcache:
                del dataview.itemcache[doc_id]
            application.layout.focus(text_area)
            set_text(dataview.show_active_view())
            loop = asyncio.get_event_loop()
            loop.call_later(0, data_changed, loop)
        else:
            show_message('add usedtime', f"Cancelled, '{usedtime}' is invalid.\nThe required entry format is:\n   used timeperiod: ending datetime")


    asyncio.ensure_future(coroutine())


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

@Condition
def is_details():
    return get_app().layout.has_focus(details_area) 

@Condition
def is_querying():
    return get_app().layout.has_focus(query_area) 


@bindings.add('f1')
def menu(event=None):
    " Focus menu. "
    if event:
        if event.app.layout.has_focus(root_container.window):
            logger.debug(f"true event.app.layout.has_focus event: {event}")
            focus_previous(event)
        else:
            logger.debug(f"false event.app.layout.has_focus event: {event}")
            event.app.layout.focus(root_container.window)


@Condition
def is_item_view():
    return dataview.active_view in ['agenda', 'completed', 'history', 'index', 'tags', 'records', 'do next', 'used time', 'used time expanded',  'relevant', 'forthcoming', 'query']

@Condition
def is_dated_view():
    return dataview.active_view in ['agenda', 'completed', 'busy'] and get_app().layout.has_focus(text_area) 

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
def is_used_view():
    return dataview.active_view in ['used time', 'used time summary', 'used time expanded']

@Condition
def is_query_view():
    return dataview.active_view in ['query']

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


@bindings.add('s', filter=is_viewing)
def do_alerts(*event):
    show_message("today's scheduled alerts", alerts(), 2)

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

        line_number = yield from show_dialog_as_float(dialog)
        if line_number:
            try:
                line_number = int(line_number)
            except ValueError:
                show_message('go to line', 'Invalid line number')
            else:
                text_area.buffer.cursor_position = \
                    text_area.buffer.document.translate_row_col_to_index(line_number - 1, 0)

    asyncio.ensure_future(coroutine())


@bindings.add('j', filter=is_dated_view)
def do_jump_to_date(*event):
    def coroutine():
        dialog = TextInputDialog(
            title='Jump to date',
            label_text='date:')

        target_date = yield from show_dialog_as_float(dialog)

        if target_date:
            try:
                dataview.dtYrWk(target_date)
            except ValueError:
                show_message('jump to date', 'Invalid date')
            else:
                set_text(dataview.show_active_view())
    asyncio.ensure_future(coroutine())

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
    'pastdue':      'CadetBlue',
    'begin':        'PeachPuff',
    'record':       'GoldenRod',
    'event':        'LimeGreen',
    'available':    'DodgerBlue',
    'waiting':      'SlateGrey',
    'finished':     'DarkGrey',
    'today':        f"{NAMED_COLORS['Ivory']} bold",
}


light_etmstyle = {
    'plain':        'Black',
    'inbox':        'FireBrick',
    'pastdue':      'RebeccaPurple',
    'begin':        'DarkRed',
    'record':       'SaddleBrown',
    'event':        'Green',
    'available':    'DarkBlue',
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

async def new_day(loop):
    logger.info(f"new_day currentYrWk: {dataview.currentYrWk}")
    dataview.refreshRelevant()
    dataview.activeYrWk = dataview.currentYrWk
    dataview.refreshAgenda()
    dataview.refreshCurrent()
    dataview.currcal()
    dataview.set_active_view('a')
    set_text(dataview.show_active_view())
    get_app().invalidate()
    dataview.handle_backups()
    dataview.possible_archive()
    logger.debug(f"leaving new_day")
    return True 

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


async def maybe_alerts(now):
    global current_datetime
    if dataview.alerts and not ('alerts' in settings and settings['alerts']):
        logger.warn("alerts have not been configured")
        return
    bad = []
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
            if startdt > alertdt:
                when = f"in {(startdt-alertdt).in_words()}"
            elif startdt == alertdt:
                when = f"now"
            else:
                when = f"{(alertdt-startdt).in_words()} ago"
            start = format_datetime(startdt)[1]
            summary = alert[3]
            doc_id = alert[4]
            command_list = alert[2]
            item = dataview.db.get(doc_id=doc_id)
            location = item.get('l', '')
            description = item.get('d', '')
            logger.debug(f"command_list: {command_list}")
            if 'e' in command_list:
                logger.debug("e alert")
                command_list.remove('e')
                dataview.send_mail(doc_id)
            if 't' in command_list:
                command_list.remove('t')
                logger.debug("t alert")
                dataview.send_text(doc_id)
            commands = [settings['alerts'][x].format(start=start, when=when, summary=summary, location=location, description=description) for x in command_list if x in settings['alerts']]
            for command in commands:
                if command:
                    logger.debug(f"{command} alert")
                    check_output(command)
            if len(commands) < len(command_list):
                bad.extend([x for x in command_list if x not in settings['alerts']])

    if bad:
        logger.error(f"unrecognized alert commands: {bad}")
        # show_message(f"unrecognized alert commands", f"{bad}", 0)


async def event_handler():
    global current_datetime
    try:
        while True:
            now = pendulum.now()
            current_today = dataview.now.format("YYYYMMDD")
            asyncio.ensure_future(maybe_alerts(now))
            current_datetime = status_time(now)
            today = now.format("YYYYMMDD")
            wait = 60 - now.second
            logger.debug(f"current_datetime: {current_datetime}; wait: {wait}")

            if today != current_today:
                logger.debug(f"calling new_day. current_today: {current_today}; today: {today}")
                loop = asyncio.get_event_loop()
                # python >= 3.6:
                asyncio.ensure_future(new_day(loop))
                # python >= 3.7:
                # asyncio.create_task(new_day(loop))
                logger.debug(f"back from new_day")
            get_app().invalidate()
            await asyncio.sleep(wait)
    except asyncio.CancelledError:
        logger.info(f"Background task cancelled.")


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


# completions will come from prior database entries 
completions = [
        ]

# expansions will come from cfg.yaml
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
            logger.debug(f"get_completions word: {word}")
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
        return


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

query_window = Window(BufferControl(buffer=entry_buffer, focusable=True, focus_on_click=True, key_bindings=edit_bindings), height=entry_dimension, wrap_lines=True, style='class:entry')

edit_area = HSplit([
    ask_window,
    reply_window,
    HorizontalLine(),
    entry_window,
])


details_area = TextArea(
    text="",
    style='class:details', 
    read_only=True,
    search_field=search_field,
    )

query = ETMQuery()
query_area = TextArea(
    height=3, 
    # style=query.style,
    lexer=query.lexer,
    multiline=False,
    prompt='query: ', 
    focusable=True,
    # wrap_lines=True,
    )

def accept(buff):
    if query_area.text:
        ok, items = query.do_query(query_area.text)
        if ok:
            dataview.set_query(query_area.text, items)
            application.layout.focus(text_area)
            set_text(dataview.show_active_view())
        else:
            text_area.text = items
    else:
        # quitting 
        dataview.active_view = dataview.prior_view
        application.layout.focus(text_area)
        set_text(dataview.show_active_view())



query_area.accept_handler = accept


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
        content=query_area,
        filter=is_querying),
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

        new_datetime = yield from show_dialog_as_float(dialog)

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
            loop = asyncio.get_event_loop()
            loop.call_later(0, data_changed, loop)


    asyncio.ensure_future(coroutine())


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

        new_datetime = yield from show_dialog_as_float(dialog)

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
            loop = asyncio.get_event_loop()
            loop.call_later(0, data_changed, loop)


    asyncio.ensure_future(coroutine())


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

            delete = yield from show_dialog_as_float(dialog)
            if delete:
                item.delete_item(doc_id)
                if doc_id in dataview.itemcache:
                    del dataview.itemcache[doc_id]
                application.layout.focus(text_area)
                set_text(dataview.show_active_view())
                loop = asyncio.get_event_loop()
                loop.call_later(0, data_changed, loop)

        asyncio.ensure_future(coroutine())

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

            which = yield from show_dialog_as_float(dialog)
            if which is not None:
                changed = item.delete_instances(doc_id, instance, which)
                if changed:
                    if doc_id in dataview.itemcache:
                        del dataview.itemcache[doc_id]
                    application.layout.focus(text_area)
                    set_text(dataview.show_active_view())
                    loop = asyncio.get_event_loop()
                    loop.call_later(0, data_changed, loop)

        asyncio.ensure_future(coroutine())


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


@bindings.add('E', filter=is_viewing_or_details & is_item_view)
def edit_existing(*event):
    global item
    if dataview.is_showing_details:
        application.layout.focus(text_area)
        dataview.hide_details()
    dataview.is_editing = True
    doc_id, entry = dataview.get_details(text_area.document.cursor_position_row, True)
    item.edit_item(doc_id, entry)
    entry_buffer.text = item.entry
    default_buffer_changed(event)
    default_cursor_position_changed(event)
    application.layout.focus(entry_buffer)


@bindings.add('T', filter=is_viewing_or_details & is_item_view)
def do_timer_toggle(*event):
    dataview.timer_toggle(text_area.document.cursor_position_row)


@bindings.add('c-t', filter=is_viewing_or_details)
def do_maybe_record_timer(*event):
    if not dataview.timer_id:
        add_usedtime() 
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
        title = "Timer"
        text = f"item: {item_info}\nelapsed time: {time_str}\n\nAction?"
        values =[
            (0, 'record time and close timer'),
            (1, 'close timer without recording time'),
        ]

        dialog = RadioListDialog(
            title=title,
            text=text,
            values=values)

        which = yield from show_dialog_as_float(dialog)
        # None: do nothing; 0: record and close; 1: close 
        if which is not None:
            if which == 0:
                item.record_timer(item_id, job_id, completed, time)
                if item_id in dataview.itemcache:
                    del dataview.itemcache[item_id]
                loop = asyncio.get_event_loop()
                loop.call_later(0, data_changed, loop)
            dataview.timer_clear()
            set_text(dataview.show_active_view())
            get_app().invalidate()

    asyncio.ensure_future(coroutine())


@bindings.add('F', filter=is_viewing_or_details & is_item_view)
def do_finish(*event):

    ok, show, item_id, job_id, due = dataview.maybe_finish(text_area.document.cursor_position_row)

    if not ok:
        return

    def coroutine():

        dialog = TextInputDialog(
            title='finish task/job',
            label_text=f"selected: {show}\ndatetime completed:")

        done_str = yield from show_dialog_as_float(dialog)
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
                loop = asyncio.get_event_loop()
                loop.call_later(0, data_changed, loop)

    asyncio.ensure_future(coroutine())

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


@bindings.add('f5')
def do_import_file(*event):
    msg = ""
    def coroutine():
        global msg
        dialog = TextInputDialog(
            title='import file',
            label_text="""\
It is possible to import data from files with 
one of the following extensions:
  .json  a json file exported from etm 3.2.x 
  .text  a text file with etm entries as lines 
  .ics   an iCalendar file
Enter the path of the file to import:""")

        file_path = yield from show_dialog_as_float(dialog)

        if file_path:
            msg = import_file(file_path)
            if msg:
                dataview.refreshRelevant()
                dataview.refreshAgenda()
                dataview.refreshCurrent()
                loop = asyncio.get_event_loop()
                loop.call_later(0, data_changed, loop)
                show_message('import file', msg)
    asyncio.ensure_future(coroutine())


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


@bindings.add('c-c', filter=is_viewing)
def copy_active_view(*event):
    pyperclip.copy(text_area.text)
    show_message("copy", "view copied to system clipboard", 2)

@bindings.add('c-c', filter=is_details | is_editing)
def copy_details(*event):
    details = dataview.get_details(text_area.document.cursor_position_row)[1]
    pyperclip.copy(details)
    show_message("copy", "details copied to system clipboard", 2)

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

@bindings.add('q', filter=is_viewing)
def query_view(*event):
    set_text("")
    dataview.set_active_view('q')
    dataview.show_query()
    application.layout.focus(query_area)

@bindings.add('u', filter=is_viewing)
def used_view(*event):
    dataview.set_active_view('u')
    set_text(dataview.show_active_view())

@bindings.add('x', filter=is_viewing)
def used_description(*event):
    dataview.set_active_view('x')
    set_text(dataview.show_active_view())
    logger.debug(f"dataview.active_view: {dataview.active_view}")

@bindings.add('U', filter=is_viewing)
def used_summary_view(*event):
    dataview.set_active_view('U')
    set_text(dataview.show_active_view())

@bindings.add('y', filter=is_viewing)
def yearly_view(*event):
    dataview.set_active_view('y')
    set_text(dataview.show_active_view())

@bindings.add('h', filter=is_viewing)
def history_view(*event):
    dataview.set_active_view('h')
    set_text(dataview.show_active_view())

@bindings.add('f', filter=is_viewing)
def forthcoming_view(*event):
    dataview.set_active_view('f')
    set_text(dataview.show_active_view())

@bindings.add('d', filter=is_viewing)
def next_view(*event):
    dataview.set_active_view('d')
    set_text(dataview.show_active_view())

@bindings.add('r', filter=is_viewing)
def records_view(*event):
    dataview.set_active_view('r')
    set_text(dataview.show_active_view())

@bindings.add('t', filter=is_viewing)
def tag_view(*event):
    dataview.set_active_view('t')
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

@bindings.add('right', filter=is_used_view & is_viewing)
def nextcal(*event):
    dataview.nextMonth()
    set_text(dataview.show_active_view())

@bindings.add('left', filter=is_used_view & is_viewing)
def prevcal(*event):
    dataview.prevMonth()
    set_text(dataview.show_active_view())

@bindings.add('space', filter=is_used_view & is_viewing)
def currcal(*event):
    dataview.currMonth()
    set_text(dataview.show_active_view())

@bindings.add('enter', filter=is_viewing_or_details & is_item_view)
def show_details(*event):
    logger.debug('processing enter')
    if dataview.is_showing_details:
        application.layout.focus(text_area)
        dataview.hide_details()
    else:
        tmp = dataview.get_details(text_area.document.cursor_position_row)[1]
        if tmp:
            dataview.show_details()
            details_area.text = tmp.rstrip()
            application.layout.focus(details_area)


# @bindings.add('c-c', filter=is_editing, eager=True)
@bindings.add('escape', filter=is_editing, eager=True)
def close_edit(*event):
    if item.is_modified:
        save_before_quit()
    else:
        item.is_modified = False
        dataview.is_editing = False
        application.layout.focus(text_area)
        set_text(dataview.show_active_view())

@edit_bindings.add('c-s', filter=is_editing, eager=True)
def save_changes(*event):
    if item.is_modified:
        maybe_save(item)
    else:
        # no changes to save - close editor
        dataview.is_editing = False
        application.layout.focus(text_area)
        set_text(dataview.show_active_view())


def maybe_save(item):
    # check hsh
    item.update_item_hsh()
    if item.item_hsh.get('itemtype', None) is None:
        show_message('Error', 'An entry for itemtype is required but missing.', 0)
        return 

    if item.item_hsh.get('summary', None) is None:
        show_message('Error', 'A summary is required but missing.', 0)
        return 

    if item.item_hsh['itemtype'] == '*' and 's' not in item.item_hsh: 
        show_message('Error', 'An entry for @s is required for events but missing.', 0)
        # item needs correcting, return to edit
        return 
    # hsh ok, save changes and close editor
    if item.doc_id in dataview.itemcache:
        del dataview.itemcache[item.doc_id]
    dataview.is_editing = False
    application.layout.focus(text_area)
    set_text(dataview.show_active_view())
    loop = asyncio.get_event_loop()
    loop.call_later(0, item_changed, loop)


root_container = MenuContainer(body=body, menu_items=[
    MenuItem('etm', children=[
        MenuItem('F1) activate/close menu', handler=menu),
        MenuItem('F2) about etm', handler=do_about),
        MenuItem('F3) system info', handler=do_system),
        MenuItem('F4) check for updates', handler=do_check_updates),
        MenuItem('F5) import file', handler=do_import_file),
        MenuItem('F6) datetime calculator', handler=datetime_calculator),
        MenuItem('F7) configuration settings', handler=do_open_config),
        MenuItem('F8) help', handler=do_show_help),
        MenuItem('-', disabled=True),
        MenuItem('^q) quit', handler=exit),
    ]),
    MenuItem('view', children=[
        MenuItem('a) agenda', handler=agenda_view),
        MenuItem('b) busy', handler=busy_view),
        MenuItem('c) completed', handler=completed_view),
        MenuItem('d) do next', handler=next_view),
        MenuItem('f) forthcoming', handler=forthcoming_view),
        MenuItem('h) history', handler=history_view),
        MenuItem('i) index', handler=index_view),
        MenuItem('q) query', handler=query_view),
        MenuItem('r) records', handler=records_view),
        MenuItem('t) tags', handler=tag_view),
        MenuItem('u) used time', handler=used_view),
        MenuItem('U) used time summary', handler=used_summary_view),
        MenuItem('x) used time expanded', handler=used_description),
        MenuItem('-', disabled=True),
        MenuItem("s) scheduled alerts for today", handler=do_alerts),
        MenuItem('y) half yearly calendar', handler=yearly_view),
        MenuItem('-', disabled=True),
        MenuItem('/) search forward'),
        MenuItem('?) search backward'),
        MenuItem('l) go to line number', handler=do_go_to_line),
        MenuItem('^c) copy active view to clipboard', handler=copy_active_view),
        MenuItem('-', disabled=True),
        MenuItem('j) jump to date in a), b) and c)', handler=do_jump_to_date),
        MenuItem('right) next in a), b), c), u), U) and y)'),
        MenuItem('left) previous in a), b), c), u), U) and y)'),
        MenuItem('space) current in a), b), c), u), U) and y)'),
    ]),
    MenuItem('editor', children=[
        MenuItem('N) create new item', handler=edit_new),
        MenuItem('-', disabled=True),
        MenuItem('^s) save changes & close', handler=save_changes),
        MenuItem('^r) show repetitions', handler=is_editing_reps),
        MenuItem('escape) close editor', handler=close_edit),
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
        MenuItem('T) begin timer, then toggle paused/running', handler=do_timer_toggle),
        MenuItem("^T) record usedtime", handler=do_maybe_record_timer),
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
async def main(etmdir=""):
    global item, settings, ampm, style, etmstyle, application
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
    background_task = asyncio.create_task(event_handler())
    try:
        await application.run_async()
    finally:
        background_task.cancel()
        logger.info("Quitting event loop.")


if __name__ == '__main__':
    sys.exit('view.py should only be imported')