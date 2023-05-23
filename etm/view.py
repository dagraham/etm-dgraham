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
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea, Frame, RadioList, SearchToolbar, MenuContainer, MenuItem
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles.named_colors import NAMED_COLORS
from prompt_toolkit.filters import Condition

from prompt_toolkit.selection import SelectionType
from prompt_toolkit.key_binding.vi_state import InputMode
from prompt_toolkit.filters import vi_mode, vi_navigation_mode, vi_insert_mode, vi_replace_mode, vi_selection_mode, emacs_mode, emacs_selection_mode, emacs_insert_mode
from prompt_toolkit.application.current import get_app
from prompt_toolkit.completion import Completion, Completer, PathCompleter
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout import Dimension
from prompt_toolkit.widgets import HorizontalLine
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout import Float
from prompt_toolkit.widgets import Dialog, Label, Button
from packaging.version import parse as parse_version

import shutil
from shlex import split as qsplit
import time

import requests
import asyncio

import pendulum
from pendulum import parse as pendulum_parse
def parse(s, **kwd):
    return pendulum_parse(s, strict=False, **kwd)

import re
import subprocess # for check_output

# for openWithDefault
import platform
import os
import contextlib, io

import pyperclip
# set in __main__
logger = None

dataview = None
item = None
style = None
application = None

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


class UpdateStatus():
    def __init__(self, new=""):
        self.status = new

    def set_status(self, new):
        self.status = new

    def get_status(self):
        return self.status


class TDBLexer(RegexLexer):

    name = 'TDB'
    aliases = ['tdb']
    filenames = '*.*'
    flags = re.MULTILINE | re.DOTALL

    tokens = {
            'root': [
                (r'\b(begins|includes|in|equals|more|less|exists|any|all|one)\b', Keyword),
                (r'\b(replace|remove|archive|delete|set|provide|attach|detach)\b', Keyword),
                (r'\b(itemtype|summary)\b', Literal),
                (r'\b(and|or|info)\b', Keyword),
                ],
            }


def format_week(dt, fmt="WWW"):
    """
    """
    if fmt == "W":
        return dt.week_of_year
    if fmt == "WW":
        return dt.strftime("%W")

    dt_year, dt_week = dt.isocalendar()[:2]

    mfmt = "MMMM D" if fmt == "WWWW" else "MMM D"

    wkbeg = pendulum.parse(f"{dt_year}-W{str(dt_week).rjust(2, '0')}")
    wkend = pendulum.parse(f"{dt_year}-W{str(dt_week).rjust(2, '0')}-7")
    week_begin = wkbeg.format(mfmt)
    if wkbeg.month == wkend.month:
        week_end = wkend.format("D")
    else:
        week_end = wkend.format(mfmt)
    return f"{week_begin} - {week_end}"


class ETMQuery(object):

    def __init__(self):
        self.filters = {
                'begins': self.begins,
                'includes': self.includes,
                'in': self.includes,
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

        self.update = {
                'replace': self.replace,    # a, rgx, rep
                'remove': self.remove,      #
                'archive': self.archive,    #
                'delete': self.delete,      # a
                'set': self.set,            # a, b
                'provide': self.provide,   # a, b
                'attach': self.attach,      # a, b
                'detach': self.detach,      # a, b
                }

        self.changed = False

        self.lexer = PygmentsLexer(TDBLexer)
        # self.style = type_colors
        self.Item = Query()

        self.allowed_commands = ", ".join([x for x in self.filters])


    def replace(self, a, rgx, rep, items):
        """
        Replace matches for rgx with rep in item['a']. If item['a']
        is a list, do this for each element in item['a']
        """
        changed = []
        rep = re.sub('\\\s', ' ', rep)
        for item in items:
            if a in item:
                if isinstance(item[a], list):
                    res = []
                    # apply to each component
                    for item in item[a]:
                        res.append(re.sub(rgx, rep, item, flags=re.IGNORECASE))
                else:
                    res = re.sub(rgx, rep, item[a], flags=re.IGNORECASE)
                if res != item[a]:
                    item[a] = res
                    item['modified'] = pendulum.now('local')
                    changed.append(item)
        if changed:
            write_back(dataview.db, changed)
        return changed


    def remove(self, items):
        """
        Remove items.
        """
        rem_ids = [item.doc_id for item in items]
        # warn
        if rem_ids:
            dataview.db.remove(doc_ids=rem_ids)
            self.changed = True

    def archive(self, items):
        """
        When querying the items table, move items to the archive table and vice versa.
        """
        rem_ids = [item.doc_id for item in items]

        try:
            if dataview.query_mode == "items table":
                # move to archive
                DBARCH.insert_multiple(items)
                DBITEM.remove(doc_ids=rem_ids)
            else:
                # back to items
                DBITEM.insert_multiple(items)
                DBARCH.remove(doc_ids=rem_ids)
        except Exception as e:
            logger.error(f"move from {dataview.query_mode} failed for items: {items}; rem_ids: {rem_ids}; exception: {e}")
            return False
        else:
            self.changed = True


    def delete(self, a, items):
        """
        For items having key 'a', remove the key and value from the item.
        """
        changed = []
        for item in items:
            if a in item:
                del item[a]
                item['modified'] = pendulum.now('local')
                changed.append(item)
        if changed:
            write_back(dataview.db, changed)
            self.changed = True
        return changed

    def set(self, a, b, items):
        """
        Set the value of item[a] = b for items
        """
        changed = []
        b = re.sub('\\\s', ' ', b)
        for item in items:
            item[a] = b
            item['modified'] = pendulum.now('local')
            changed.append(item)
        if changed:
            write_back(dataview.db, changed)
            self.changed = True

    def provide(self, a, b, items):
        """
        Provide item['a'] = b for items without an exising entry for 'a'.
        """
        changed = []
        b = re.sub('\\\s', ' ', b)
        for item in items:
            item.setdefault(a, b)
            item['modified'] = pendulum.now('local')
            changed.append(item)
        if changed:
            write_back(dataview.db, changed)
            self.changed = True


    def attach(self, a, b, items):
        """
        Attach 'b' into the item['a'] list if 'b' is not in the list.
        """
        changed = []
        b = re.sub('\\\s', ' ', b)
        for item in items:
            if a not in item:
                item.setdefault(a, []).append(b)
                item['modified'] = pendulum.now('local')
                changed.append(item)
            elif isinstance(item[a], list) and b not in item[a]:
                item.setdefault(a, []).append(b)
                item['modified'] = pendulum.now('local')
                changed.append(item)
        if changed:
            write_back(dataview.db, changed)
            self.changed = True

    def detach(self, a, b, items):
        """
        Detatch 'b' from the item['a'] list if it belongs to the list.
        """
        changed = []
        b = re.sub('\\\s', ' ', b)
        for item in items:
            if a in item and isinstance(item[a], list) and b in item[a]:
                item[a].remove(b)
                item['modified'] = pendulum.now('local')
                changed.append(item)
        if changed:
            write_back(dataview.db, changed)
            self.changed = True


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
        if args and val.year != int(args.pop(0)):
            return False
        if args and val.month != int(args.pop(0)):
            return False
        if args and val.day != int(args.pop(0)):
            return False
        if isinstance(val, pendulum.DateTime):
            # val has hours and minutes
            if args and val.hour != int(args.pop(0)):
                return False
            if args and val.minute != int(args.pop(0)):
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


    def begins(self, a, b):
        # the value of field 'a' begins with the case-insensitive regex 'b'
        return where(a).matches(b, flags=re.IGNORECASE)

    def includes(self, a, b):
        # the value of one of the fields in 'a' includes the case-insensitive regex 'b'
        if not isinstance(a, list):
            a = [a]
        results = [where(field).search(b, flags=re.IGNORECASE) for field in a]
        test = results.pop(0)
        for res in results:
            test = test | res
        return test

    def equals(self, a, b):
        # the value of field 'a' equals 'b'
        try:
            b = int(b)
        except:
            pass
        return where(a) == b

    def more(self, a, b):
        # the value of field 'a' >= 'b'
        try:
            b = int(b)
        except:
            pass
        return where(a) >= b

    def less(self, a, b):
        # the value of field 'a' equals 'b'
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
        item = dataview.db.get(doc_id=int(a))
        return  item if item else f"doc_id {a} not found"


    def dt(self, a, b):
        if b[0]  == '?':
            if b[1] == 'time':
                return self.Item[a].test(self.is_datetime)
            elif b[1] == 'date':
                return self.Item[a].test(self.is_date)

        return self.Item[a].test(self.op[b[0]], b[1])


    def process_query(self, query):
        """

        """
        [fltr, *updt] = [x.strip() for x in query.split(" | ")]
        if len(updt) == 1:
            # get a list with the update command and arguments
            updt = [x.strip() for x in updt[0].split(' ')]
        else:
            updt = []

        parts = [x.split() for x in re.split(r' (and|or) ', fltr)]

        cmnds = []
        for part in parts:
            part = [x.strip() for x in part if x.strip()]
            negation = part[0].startswith('~')
            if part[0] not in ['and', 'or']:
                # we have a command
                if negation:
                    # drop the ~
                    part[0] = part[0][1:]
                if self.filters.get(part[0], None) is None:
                    return False, wrap(f"""bad command: '{part[0]}'. Only commands in {self.allowed_commands} are allowed."""), updt

            if len(part) > 3:
                if part[0] in ['in', 'includes']:
                    if negation:
                        cmnds.append(~ self.filters[part[0]]([x.strip() for x in part[1:-1]], part[-1]))
                    else:
                        cmnds.append(self.filters[part[0]]([x.strip() for x in part[1:-1]], part[-1]))
                else:
                    if negation:
                        cmnds.append(~ self.filters[part[0]](part[1], [x.strip() for x in part[2:]]))
                    else:
                        cmnds.append(self.filters[part[0]](part[1], [x.strip() for x in part[2:]]))
            elif len(part) > 2:
                if negation:
                    cmnds.append(~ self.filters[part[0]](part[1], part[2]))
                else:
                    cmnds.append(self.filters[part[0]](part[1], part[2]))
            elif len(part) > 1:
                if negation:
                    cmnds.append(~ self.filters[part[0]](part[1]))
                else:
                    cmnds.append(self.filters[part[0]](part[1]))
            else:
                cmnds.append(part[0])

        test = cmnds[0]
        for i in range(1, len(cmnds)):
            if i % 2 and cmnds[i] in ['and', 'or']:
                andor = cmnds[i]
                continue
            test = test | cmnds[i] if andor == 'or' else test & cmnds[i]
        return True, test, updt


    def do_query(self, query):
        """
        """
        if query in ["?", "help"]:
            query_help = "https://dagraham.github.io/etm-dgraham/#query-view"
            openWithDefault(query_help)
            return False, "opened query help using default browser"
        try:
            ok, test, updt = self.process_query(query)
            if not ok:
                return False, test
            if isinstance(test, str):
                return False, test
            else:
                items = dataview.db.search(test)
                if updt:
                    self.update[updt[0]](*updt[1:], items)
                    if self.changed:
                        loop = asyncio.get_event_loop()
                        loop.call_later(0, data_changed, loop)
                        self.changed = False
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
                style='class:dialog-output',
                focusable=False,
                height=3,
                )
        self.input_field = TextArea(
            height=1,
            # prompt='',
            multiline=False,
            style='class:dialog-entry',
            focusable=True,
            wrap_lines=False)

        def accept(buff):
            # Evaluate "calculator" expression.
            try:
                output = f"In:  {self.input_field.text}\nOut: {evaluator(self.input_field.text)}\n"
            except BaseException as e:
                output = f"\n{e}"
            # new_text = self.output_field.text + output
            new_text = output
            # Add text to output buffer.
            self.output_field.buffer.text = new_text

        self.input_field.accept_handler = accept

        cancel_button = Button(text='Cancel', handler=cancel)

        self.dialog = Dialog(
            title=title,
            body=HSplit([
                Label(text=help_text),
                self.output_field,
                # HorizontalLine(),
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
            self.set_label('\nworking ...\n')
            get_app().invalidate()
            time.sleep(.1)
            self.future.set_result(self.text_area.text)

        def cancel():
            self.future.set_result(None)

        self.text_area = TextArea(
            completer=completer,
            text=default,
            style='class:dialog-entry',
            multiline=False,
            width=D(preferred=shutil.get_terminal_size()[0]-padding),
            accept_handler=accept_text)

        self.label = Label(
                text=label_text
                )

        ok_button = Button(text='OK', handler=accept)
        cancel_button = Button(text='Cancel', handler=cancel)

        self.dialog = Dialog(
            title=title,
            body=HSplit([
                self.label,
                self.text_area
            ]),
            buttons=[ok_button, cancel_button],
            # buttons=[ok_button],
            width=D(preferred=shutil.get_terminal_size()[0]-10),
            modal=True)

    def set_label(self, txt):
        self.label.text = txt

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
    status, res = check_update()
    msg = wrap(res)
    show_message("version information", msg, 2)


def check_update():
    url = "https://raw.githubusercontent.com/dagraham/etm-dgraham/master/etm/__version__.py"
    try:
        r = requests.get(url)
        t = r.text.strip()
        # t will be something like "version = '4.7.2'"
        url_version = t.split(' ')[-1][1:-1]
        # split(' ')[-1] will give "'4.7.2'" and url_version will then be '4.7.2'
    except:
        url_version = None
    if url_version is None:
        res = "update information is unavailable"
        status_char = "?"
    else:
        # kluge for purely numeric versions
        # if [int(x) for x in url_version.split('.')] > [int(x) for x in etm_version.split('.')]:
        # from packaging.version parse
        if parse_version(url_version) > parse_version(etm_version):
            status_char = UPDATE_CHAR
            res = f"an update is available to {url_version}"
        else:
            status_char = ''
            res = f"the installed version, {etm_version}, is the latest available"

    return status_char, res


update_status = UpdateStatus()

async def auto_check_loop(loop):
    status, res = check_update()
    update_status.set_status(status)

@bindings.add('f3')
def do_system(*event):
    show_message('system information', about(22)[1], 20)


@bindings.add('f6')
def dt_calculator(*event):
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
        dialog = ConfirmDialog("unsaved changes", "discard changes and close the editor?")

        discard = yield from show_dialog_as_float(dialog)
        if discard:
            app = get_app()
            app.editing_mode = EditingMode.EMACS
            dataview.is_editing = False
            application.layout.focus(text_area)
            set_text(dataview.show_active_view())
        else:
            return

    asyncio.ensure_future(coroutine())

def discard_changes(event, prompt=''):
    def coroutine(prompt):
        dialog = ConfirmDialog("unsaved information", prompt)

        discard = yield from show_dialog_as_float(dialog)
        if discard:
            application.exit()
        else:
            return

    asyncio.ensure_future(coroutine(prompt))

def add_usedtime(*event):

    doc_id, instance, job = dataview.get_row_details(text_area.document.cursor_position_row)

    if not doc_id:
        return

    hsh = DBITEM.get(doc_id=doc_id)

    state2fmt = {
            'i': "inactive",
            'r': "running",
            'p': "paused",
            }

    now = pendulum.now('local')
    if doc_id in dataview.timers:
        title = 'active timer - record used time and end timer'
        state, start, elapsed = dataview.timers[doc_id]
        if state == 'r':
            elapsed += now - start
            start = now
        timer = f"\ntimer:\n  status: {state2fmt[state]}\n  last change: {format_datetime(start, short=True)[1]}\n  elapsed time: {format_duration(elapsed, short=True)}"
        entry = f"{format_duration(elapsed, short=True)}: {format_datetime(start, short=True)[1]}"
    else:
        title = 'no active timer - add used time entry'
        state = None
        timer = "\ntimer: None"
        entry = " : now"

    def coroutine():
        dialog = TextInputDialog(
            title=title,
            label_text=f"selected:\n  {hsh['itemtype']} {hsh['summary']}\n  @i {hsh.get('i', '~')}{timer}\n\nused time format:\n    period: datetime\n",
            default=entry,
            )
        usedtime = yield from show_dialog_as_float(dialog)

        if not usedtime:
            # None (cancelled) or null string
            return

        changed = item.add_used(doc_id, usedtime)

        if changed:
            dataview.timer_clear(doc_id)

            if doc_id in dataview.itemcache:
                del dataview.itemcache[doc_id]
            application.layout.focus(text_area)
            set_text(dataview.show_active_view())
            loop = asyncio.get_event_loop()
            loop.call_later(0, data_changed, loop)
        else:
            show_message('add used time', f"Cancelled, '{usedtime}' is invalid.\nThe required entry format is:\n   period: datetime")


    asyncio.ensure_future(coroutine())


today = pendulum.today()
calyear = today.year
calmonth = today.month

def check_output(cmd):
    if not cmd:
        return
    res = ""
    try:
        res = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True, universal_newlines=True, encoding='UTF-8')
        return True, res
    except subprocess.CalledProcessError as e:
        logger.warning(f"Error running {cmd}\n'{e.output}'")
        lines = e.output.strip().split('\n')
        msg = lines[-1]
        return False, msg

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

@Condition
def is_items_table():
    return dataview.query_mode == "items table"

@bindings.add(',', ',', filter=is_viewing)
def _(event):
    search_state = get_app().current_search_state
    text = search_state.text
    search_state.text = ''

@bindings.add('f1')
def menu(event=None):
    " Focus menu. "
    if event:
        if event.app.layout.has_focus(root_container.window):
            focus_previous(event)
        else:
            event.app.layout.focus(root_container.window)


@Condition
def is_item_view():
    return dataview.active_view in ['agenda', 'completed', 'engaged', 'history', 'index', 'tags', 'journal', 'do next', 'used time', 'relevant', 'forthcoming', 'query', 'pinned', 'review', 'konnected', 'timers', 'location']

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
def is_busy_view():
    return dataview.active_view == 'busy'

@Condition
def is_not_busy_view():
    return dataview.active_view != 'busy'

@Condition
def is_agenda_view():
    return dataview.active_view in ['agenda', 'busy', 'completed', 'engaged']

@Condition
def is_used_view():
    return dataview.active_view in ['used time', 'used summary']

@Condition
def is_query_view():
    return dataview.active_view in ['query']

@Condition
def is_yearly_view():
    return dataview.active_view in ['yearly']

@Condition
def is_not_yearly_view():
    return dataview.active_view not in ['yearly']

@Condition
def not_showing_details():
    return dataview.is_showing_details == False

@Condition
def is_showing_details():
    return dataview.is_showing_details

bindings.add('tab', filter=is_not_editing)(focus_next)
bindings.add('s-tab', filter=is_not_editing)(focus_previous)

@bindings.add('c-s', filter=is_not_editing)
def do_nothing(*event):
    pass

@bindings.add('s', filter=is_viewing)
def do_alerts(*event):
    show_message("today's scheduled alerts", alerts(), 2)

@bindings.add('c-l', filter=is_viewing)
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


@bindings.add('J', filter=is_dated_view)
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


window_colors = None

grey_colors = {
        'grey1': '#396060', # 1 shade lighter of darkslategrey for status and menubar background
        'grey2': '#1d3030', # 2 shades darker of darkslategrey for textarea background
    }

def get_colors(bg='', fg='', attr=''):
    if bg and bg in grey_colors:
        bg = f"bg:{grey_colors[bg]}"
    else:
        # background colors from NAMED_COLORS if possible
        bg = f"bg:{NAMED_COLORS.get(bg, bg)}" if bg else ""
    if fg and fg in grey_colors:
        fg = f"{grey_colors[fg]}"
    else:
        # foreground colors from NAMED_COLORS if possible
        fg = f"{NAMED_COLORS.get(fg, fg)}" if fg else ""
    return f"{bg} {fg} {attr}".rstrip()


def get_style(style_dict):
    window_colors = {k: get_colors(*v) for k, v in style_dict.items()}
    return Style.from_dict(window_colors)

type2style = {
        '!': 'inbox',
        '<': 'pastdue',
        '>': 'begin',
        '%': 'journal',
        '*': 'event',
        '-': 'available',
        '+': 'waiting',
        '✓': 'finished',
        '~': 'missing',
        '◦': 'used',
        '↱': 'wrap',
        '↳': 'wrap',
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
    else:
        # no leading spaces
        return None

# Create one text buffer for the main content.
class ETMLexer(Lexer):

    def lex_document(self, document):

        def get_line(lineno):
            tmp = document.lines[lineno]
            typ = first_char(tmp)
            if typ in type2style:
                sty = type2style[typ]
                if sty in type_colors:
                    return [(type_colors[sty], tmp)]
                else:
                    logger.debug(f"problem with typ {typ} from {tmp}")
                    logger.debug(f"sty: {sty}; type_colors.keys: {type_colors.keys()}")
            if tmp.rstrip().endswith("(Today)") or tmp.rstrip().endswith("(Tomorrow)"):
                return [(type_colors['today'], f"{tmp} ")]

            return [
                (busy_colors.get(c, type_colors['plain']), c)
                for i, c in enumerate(document.lines[lineno])
            ]


        return get_line


def status_time(dt):
    """
    >>> status_time(parse('2018-03-07 10am'))
    '10am Wed Mar 7'
    >>> status_time(parse('2018-03-07 2:45pm'))
    '2:45pm Wed Mar 7'
    """
    ampm = settings['ampm']
    if settings['dayfirst']:
        d_fmt = dt.format("ddd D MMM")
    else:
        d_fmt = dt.format("ddd MMM D")
    suffix = dt.format("A").lower() if ampm else ""
    if dt.minute == 0:
        t_fmt = dt.format("h") if ampm else dt.format("H")
    else:
        t_fmt = dt.format("h:mm") if ampm else dt.format("H:mm")
    return f"{t_fmt}{suffix} {d_fmt}"

def item_changed(loop):
    item.update_item_hsh()
    if (dataview.active_view == 'timers'
            and item.doc_id not in dataview.timers):
        if dataview.active_timer:
            state = 'i'
        else:
            state = 'r'
            dataview.active_timer = item.doc_id
        dataview.timers[item.doc_id] = [state, pendulum.now('local'), pendulum.Duration()]
    dataview.get_completions()
    dataview.update_konnections(item)
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
    logger.debug("XXX new day XXX")
    dataview.currYrWk()
    dataview.refreshRelevant()  # sets now, currentYrWk, current
    dataview.refreshAgenda()
    dataview.refreshCurrent()
    dataview.set_active_view('a')
    set_text(dataview.show_active_view())
    dataview.currcal()
    get_app().invalidate()
    dataview.handle_backups()
    dataview.possible_archive()
    logger.info(f"new_day currentYrWk: {dataview.currentYrWk}")
    return True

current_datetime = pendulum.now('local')

async def save_timers():
    dataview.save_timers()
    return True

def alerts():
    # alerts = []
    alert_hsh = {}
    now = pendulum.now('local')
    #            0            1         2          3         4       5
    # alerts: alert time, start time, commands, itemtype, summary, doc_id
    for alert in dataview.alerts:
        trigger_time = pendulum.instance(alert[0])
        start_time = pendulum.instance(alert[1])
        if start_time.date() == now.date():
            start = format_time(start_time)[1]
        else:
            start = format_datetime(start_time, short=True)[1]
        trigger = format_time(trigger_time)[1]
        command = ", ".join(alert[2])
        itemtype = alert[3]
        summary = alert[4]
        doc_id = alert[5]
        prefix = '✓' if trigger_time < now else '•' # '⧖'
        alert_hsh.setdefault((alert[5], itemtype, summary), []).append([prefix, trigger, start, command])
    if alerts:
        output = []
        for key, values in alert_hsh.items():
            output.append(f"{key[1]} {key[2]}")
            for value in values:
                output.append(f"  {value[0]} {value[1]:>7} ⭢  {value[2]:>7}:  {value[3]}")
        output.append('')
        output.append('✓ already activated')
        output.append('• not yet activated')
        return "\n".join(output)

    else:
        return "There are no alerts for today."

def get_row_col():
    row_number = text_area.document.cursor_position_row
    col_number = text_area.document.cursor_position_col
    return row_number, col_number

def restore_row_col(row_number, col_number):
    text_area.buffer.cursor_position = \
                    text_area.buffer.document.translate_row_col_to_index(row_number, col_number)



async def maybe_alerts(now):
    global current_datetime
    row, col = get_row_col()
    set_text(dataview.show_active_view())
    #            0            1         2          3         4       5
    # alerts: alert time, start time, commands, itemtype, summary, doc_id
    restore_row_col(row, col)
    if dataview.alerts and not ('alerts' in settings and settings['alerts']):
        logger.warning("alerts have not been configured")
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
            time = format_time(startdt)[1] if startdt.date() == today.date() else format_datetime(startdt, short=True)[1]
            summary = alert[4]
            doc_id = alert[5]
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
            commands = [settings['alerts'][x].format(start=start, time=time, when=when, now=format_time(now)[1], summary=summary, location=location, description=description) for x in command_list if x in settings['alerts']]
            for command in commands:
                if command:
                    check_output(command)
            if len(commands) < len(command_list):
                bad.extend([x for x in command_list if x not in settings['alerts']])

    if bad:
        logger.error(f"unrecognized alert commands: {bad}")


async def event_handler():
    global current_datetime
    # check for updates every interval minutes
    interval = settings.get('updates_interval', 0)
    refresh_interval = settings.get('refresh_interval', 60)
    minutes = 0
    try:
        while True:
            now = pendulum.now()
            current_datetime = status_time(now)
            wait = refresh_interval - now.second % refresh_interval # residual
            logger.debug(f"refresh_interval: {refresh_interval}; wait: {wait}")
            if now.second < 6:
                current_today = dataview.now.format("YYYYMMDD")
                asyncio.ensure_future(maybe_alerts(now))
                current_datetime = status_time(now)
                today = now.format("YYYYMMDD")

                if interval:
                    if minutes == 0:
                        minutes = 1
                        loop = asyncio.get_event_loop()
                        asyncio.ensure_future(auto_check_loop(loop))
                    else:
                        minutes += 1
                        minutes = minutes % interval

                if today != current_today:
                    loop = asyncio.get_event_loop()
                    asyncio.ensure_future(new_day(loop))

            asyncio.ensure_future(save_timers())
            if dataview.active_view == 'timers':
                row, col = get_row_col()
                set_text(dataview.show_active_view())
                restore_row_col(row, col)
            get_app().invalidate()
            await asyncio.sleep(wait)
    except asyncio.CancelledError:
        logger.info(f"Background task cancelled.")


def get_edit_mode():
    app = get_app()
    if get_app().layout.has_focus(entry_buffer):
        if app.editing_mode == EditingMode.VI:
            insert_mode = app.vi_state.input_mode in (InputMode.INSERT, InputMode.INSERT_MULTIPLE)
            replace_mode = app.vi_state.input_mode == InputMode.REPLACE
            sel = entry_buffer.selection_state
            temp_navigation = app.vi_state.temporary_navigation_mode
            visual_line = sel is not None and sel.type == SelectionType.LINES
            visual_block = sel is not None and sel.type == SelectionType.BLOCK
            visual_char = sel is not None and sel.type == SelectionType.CHARACTERS
            mode = 'vi:'
            if insert_mode:
                mode += ' insert'
            elif replace_mode:
                mode += ' replace'
            elif visual_block:
                mode += ' vblock'
            elif visual_line:
                mode += ' vline'
            elif visual_char:
                mode += 'vchar'
            else:
                mode += ' normal'
        else:
            mode = 'emacs'

        return ''.join([
            mode,
            ' ',
            ('+' if entry_buffer_changed() else ''),
            (' '),
        ])

    return '        '


def get_statusbar_text():
    return [ ('class:status',  f' {current_datetime}'), ]

def get_statusbar_center_text():
    if dataview.is_editing:
        return [ ('class:status',  f' {get_edit_mode()}'), ]
    if dataview.is_showing_query:
        return [ ('class:status',  f' {dataview.query_mode}'), ]
    if loglevel == 1:
        # show current row number and associated id in the status bar
        current_row = text_area.document.cursor_position_row
        current_id = dataview.row2id.get(current_row, '~')
        if isinstance(current_id, tuple):
            current_id = current_id[0]
        return [ ('class:status',  f'{current_row}: {current_id}'), ]

    return [ ('class:status',  14 * ' '), ]


def get_statusbar_right_text():
    inbasket = INBASKET_CHAR if os.path.exists(inbasket_file) else ""
    active, inactive = dataview.timer_report()
    if active:
        active_part = (type_colors['running'], active) if active.startswith('r') else (type_colors['paused'], active)
        inactive_part = ('class:status', f"{inactive}  ")
    else:
        active_part = inactive_part = ('class:status', "")

    return [ active_part, inactive_part,  ('class:status',  f"{dataview.active_view} {inbasket}{update_status.get_status()}"), ]

def openWithDefault(path):
    if " " in path:
        parts = qsplit(path)
        logger.debug(f"path: {path}\n    Popen args: {parts}")
        if parts:
            # wrapper to catch 'Exception Ignored' messages
            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                # the pid business is evidently needed to avoid waiting
                pid = subprocess.Popen(parts, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).pid
                res = output.getvalue()
                if res:
                    logger.error(f"caught by contextlib:\n'{res}'")


    else:
        path = os.path.normpath(os.path.expanduser(path))
        logger.debug(f"path: {path}")
        sys_platform = platform.system()
        if platform.system() == 'Darwin':       # macOS
            subprocess.run(('open', path), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif platform.system() == 'Windows':    # Windows
            os.startfile(path)
        else:                                   # linux
            subprocess.run(('xdg-open', path), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return

search_field = SearchToolbar(text_if_not_searching=[
    ('class:not-searching', "Press '/' to start searching.")], ignore_case=True)

content = ""
etmlexer = ETMLexer()
text_area = TextArea(
    text="",
    read_only=True,
    scrollbar=True,
    search_field=search_field,
    focus_on_click=True,
    lexer=etmlexer,
    )

# expansions will come from cfg.yaml
expansions = {
        }


class AtCompleter(Completer):
    # pat = re.compile(r'@[cgilntxz]\s?\S*')
    pat = re.compile(r'@[cgiklntxz]\s?[^@&]*')

    def get_completions(self, document, complete_event):
        cur_line = document.current_line_before_cursor
        matches = re.findall(AtCompleter.pat, cur_line)
        word = matches[-1] if matches else ""
        if word:
            word_len = len(word)
            word = word.rstrip()
            for completion in dataview.completions:
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

reply_dimension = Dimension(min=1, weight=1)
entry_dimension = Dimension(min=2, weight=3)

entry_window = Window(BufferControl(buffer=entry_buffer, focusable=True, focus_on_click=True, key_bindings=edit_bindings), height=entry_dimension, wrap_lines=True, style='class:entry')
ask_window = Window(BufferControl(buffer=ask_buffer, focusable=False), height=1, style='class:ask')
reply_window = Window(BufferControl(buffer=reply_buffer, focusable=False), height=reply_dimension, wrap_lines=True, style='class:reply')

edit_area = HSplit([
    ask_window,
    reply_window,
    HorizontalLine(),
    entry_window,
    ], style='class:entry')


details_area = TextArea(
    text="",
    style='class:details',
    read_only=True,
    search_field=search_field,
    )


busy_area = TextArea(
    text="",
    style='class:details',
    read_only=True,
    search_field=search_field,
    )


width = shutil.get_terminal_size()[0] - 4

def get_busy_text():
    return get_busy_text_and_keys(0)

def get_busy_keys():
    return get_busy_text_and_keys(1)

def get_busy_text_and_keys(n):

    weekdays = {
            5:  f"1→{WA[1]}",
            7:  f"2→{WA[2]}",
            9:  f"3→{WA[3]}",
            11: f"4→{WA[4]}",
            13: f"5→{WA[5]}",
            15: f"6→{WA[6]}",
            17: f"7→{WA[7]}",
            }
    busy_details = dataview.busy_details
    active_days = "  ".join([v for k, v in weekdays.items() if k in busy_details.keys()])
    no_busy_times = "There are no days with busy periods this week.".center(width, ' ')
    busy_times = wrap(f"Press the number of a weekday, [{weekdays[5]}, ..., {weekdays[17]}], to show the details of the busy periods from that day or press the ▼ (down) or ▲ (up) cursor keys to show the details of the next or previous day with busy periods.", indent=0)
    active_keys = f"{active_days}  ▼→next  ▲→previous".center(width, ' ')

    if n == 0: # text
        return busy_times if dataview.busy_details else ""
    else: # n=1, keys
        return active_keys if dataview.busy_details else no_busy_times


busy_container = HSplit([
    busy_area,
    Window(FormattedTextControl(get_busy_keys), style='class:status', height=1),
    ], style='class:entry')

query_bindings = KeyBindings()

@query_bindings.add('enter', filter=is_querying)
def accept(buff):
    set_text('processing query ...')
    if query_window.text:
        text = query_window.text
        queries = settings.get('queries')
        if text == 'l':
            if queries:
                query_str = "\n  ".join([f"{k}: {v}" for k, v in queries.items()])
            else:
                query_str = "None listed"
            tmp = """\
Stored queries are listed as <key>: <query> below.
Enter <key> at the prompt and press 'enter' to
replace <key> with <query>. Submit this query as
is or edit it first and then submit.

  """ + query_str

            show_message('query information', tmp)
            return False
        if text.strip() in ['quit', 'exit']:
            # quitting
            dataview.active_view = dataview.prior_view
            application.layout.focus(text_area)
            set_text(dataview.show_active_view())
            return False
        parts = [x.strip() for x in text.split(' ')]
        if queries and parts[0] in queries:
            set_text("")
            text = queries[parts.pop(0)]
            m =  re.search('{\d*}', text)
            if m:
                # make the substitutions
                num_needed = text.count('{}')
                num_given = len(parts)
                if num_needed and num_given != num_needed:
                    tmp = f"""\
The query
    {text}
needs {num_needed} argument(s) to replace the '{{}}' but
{num_given} were actually provided:
    {", ".join(parts)}
Please correct and resubmit.
                            """
                    show_message('query error', tmp)
                    return False
                try:
                    text = text.format(*parts)
                    query_window.text = text
                except IndexError as e:
                    tmp = f"""\
Error processing {text}:
{e}
"""
                    show_message('query error', tmp)
                    return True
            else:
                query_window.text = text
                # don't reset the query area buffer we just set
                return True

        loop = asyncio.get_event_loop()
        loop.call_later(0, do_show_processing, loop)
        loop.call_later(.1, do_complex_query, text, loop)

    else:
        # quitting
        dataview.active_view = dataview.prior_view
        application.layout.focus(text_area)
        set_text(dataview.show_active_view())

    return False


query = ETMQuery()

query_buffer = Buffer(multiline=False, completer=None, complete_while_typing=False, accept_handler=accept)


query_window = TextArea(
    style='class:query',
    lexer=query.lexer,
    multiline=False,
    focusable=True,
    # height=3,
    wrap_lines=True,
    prompt='query: ',
    )

query_window.accept_handler = accept

query_area = HSplit([
    ask_window,
    query_window,
    ], style='class:entry')


def do_complex_query(text, loop):
    text, *updt = [x.strip() for x in text.split(' | ')]
    updt = f" | {updt[0]}" if updt else ""
    if text.startswith('a '):
        text = text[2:]
        dataview.use_archive()
        item.use_archive()
    else:
        dataview.use_items()
        item.use_items()

    if len(text) > 1 and text[1] == ' ' and text[0] in ['s', 'u', 'm', 'c']:
        grpby, filters = report.get_grpby_and_filters(text)
        ok, items = query.do_query(filters.get('query') + updt)
        if ok:
            items = report.apply_dates_filter(items, grpby, filters)
            dataview.set_query(text, grpby, items)
            application.layout.focus(text_area)
            set_text(dataview.show_active_view())
        else:
            set_text(items)
    else:
        ok, items = query.do_query(text + updt)
        if ok:
            dataview.set_query(f"{text + updt}", {}, items)
            application.layout.focus(text_area)
            set_text(dataview.show_active_view())
        else:
            set_text(items)

def do_show_processing(loop):
    set_text("processing query ...")
    application.layout.focus(text_area)
    get_app().invalidate()



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


# This is slick - add a call to default_buffer_changed
entry_buffer.on_text_changed += default_buffer_changed
entry_buffer.on_cursor_position_changed += default_cursor_position_changed

status_area = VSplit([
            Window(FormattedTextControl(get_statusbar_text), style='class:status'),
            Window(FormattedTextControl(get_statusbar_center_text),
                   style='class:status', width=14, align=WindowAlign.CENTER),
            Window(FormattedTextControl(get_statusbar_right_text),
                   style='class:status', width=26, align=WindowAlign.RIGHT),
        ], height=1)


body = HSplit([
    text_area,      # main content
    status_area,    # toolbar
    ConditionalContainer(
        content=details_area,
        filter=is_showing_details & is_not_busy_view),
    ConditionalContainer(
        content=busy_container,
        filter=is_busy_view),
    ConditionalContainer(
        content=query_area,
        filter=is_querying),
    ConditionalContainer(
        content=edit_container,
        filter=is_editing),
    search_field,
    ])

item_not_selected = False

@bindings.add('S', filter=is_viewing_or_details & is_items_table)
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


@bindings.add('R', filter=is_viewing_or_details & is_items_table)
def do_reschedule(*event):
    doc_id, instance, job = dataview.get_row_details(text_area.document.cursor_position_row)

    if not doc_id:
        return

    hsh = DBITEM.get(doc_id=doc_id)
    if instance is None and 's' in hsh:
        instance = hsh['s']

    is_date = (isinstance(instance, pendulum.Date) and not isinstance(instance, pendulum.DateTime))

    date_required = is_date or (instance.hour == 0 and instance.minute == 0)

    instance = instance.date() if date_required and not is_date else instance
    new = "new date" if date_required else "new datetime"

    def coroutine():
        dialog = TextInputDialog(
            title='reschedule instance',
            label_text=f"selected: {hsh['itemtype']} {hsh['summary']}\ninstance: {format_datetime(instance)[1]}\n\n{new}:")

        new_datetime = yield from show_dialog_as_float(dialog)

        if not new_datetime:
            return
        changed = False
        try:
            dt = parse_datetime(new_datetime, z='local')[1]
            ok = True
        except:
            ok = False

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
    has_timer = doc_id in dataview.timers
    timer_warning = " and\nits associated timer" if has_timer else ""

    if not instance:
        # not repeating
        def coroutine():
            dialog = ConfirmDialog("Delete",
                    f"Selected: {hsh['itemtype']} {hsh['summary']}\n\nAre you sure you want to delete this item{timer_warning}?\nThis action cannot be undone.")

            delete = yield from show_dialog_as_float(dialog)
            if delete:
                if has_timer:
                    dataview.timer_clear(doc_id)
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

starting_buffer_text = ""

@bindings.add('N', filter=is_viewing & is_items_table)
def edit_new(*event):
    global item
    global starting_buffer_text
    app = get_app()
    app.editing_mode = EditingMode.VI if settings['vi_mode'] else EditingMode.EMACS
    starting_buffer_text = ""
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
    global starting_buffer_text
    global text_area
    app = get_app()
    app.editing_mode = EditingMode.VI if settings['vi_mode'] else EditingMode.EMACS
    if dataview.is_showing_details:
        application.layout.focus(text_area)
        dataview.hide_details()
    dataview.is_editing = True
    doc_id, entry = dataview.get_details(text_area.document.cursor_position_row, True)
    row, col = get_row_col()
    item.edit_item(doc_id, entry)
    entry_buffer.text = item.entry
    starting_buffer_text = item.entry
    default_buffer_changed(event)
    default_cursor_position_changed(event)
    application.layout.focus(entry_buffer)

def entry_buffer_changed():
    return entry_buffer.text != starting_buffer_text


@bindings.add('T', filter=is_viewing_or_details & is_item_view)
def next_timer_state(*event):
    row = text_area.document.cursor_position_row
    res = dataview.get_row_details(row) # item_id, instance, job_id
    doc_id = res[0]
    if not doc_id:
        return
    dataview.next_timer_state(doc_id)
    row = text_area.document.cursor_position_row
    dataview.refreshRelevant()
    set_text(dataview.show_active_view())
    text_area.buffer.cursor_position = \
                    text_area.buffer.document.translate_row_col_to_index(row, 0)


@bindings.add('T', 'D', filter=is_viewing_or_details & is_item_view)
def maybe_delete_timer(*event):
    row = text_area.document.cursor_position_row
    res = dataview.get_row_details(row) # item_id, instance, job_id
    doc_id = res[0]
    if not doc_id or doc_id not in dataview.timers:
        return
    hsh = DBITEM.get(doc_id=doc_id)
    state2fmt = {
            'i': "inactive",
            'r': "running",
            'p': "paused",
            }


    state, start, elapsed = dataview.timers[doc_id]
    if state == 'r':
        now = pendulum.now('local')
        elapsed += now - start
        start = now
    timer = f"\ntimer:\n  status: {state2fmt[state]}\n  last change: {format_datetime(start, short=True)[1]}\n  elapsed time: {format_duration(elapsed, short=True)}\n\nWARNING: The timer's data will be lost.\nAre you sure you want to delete this timer?"

    def coroutine():

        dialog = ConfirmDialog(
            title='delete timer',
            text=f"selected: {hsh['itemtype']} {hsh['summary']}{timer}",
            )

        discard = yield from show_dialog_as_float(dialog)
        if discard:
            dataview.timer_clear(doc_id)
            dataview.refreshRelevant()
            set_text(dataview.show_active_view())
            get_app().invalidate()
        else:
            return

    asyncio.ensure_future(coroutine())



@bindings.add('T', 'T', filter=is_viewing_or_details & is_item_view)
def toggle_active_timer(*event):
    dataview.toggle_active_timer(text_area.document.cursor_position_row)
    row = text_area.document.cursor_position_row
    dataview.refreshRelevant()
    set_text(dataview.show_active_view())
    text_area.buffer.cursor_position = \
                    text_area.buffer.document.translate_row_col_to_index(row, 0)

@bindings.add('T', 'R', filter=is_viewing_or_details)
def record_time(*event):
    """
    doc_id?
        timer?
            prompt for period and ending time with timer period
                and now as the defaults
        else
            prompt for period and ending time w/o defaults
    """
    row = text_area.document.cursor_position_row
    res = dataview.get_row_details(row) # item_id, instance, job_id
    doc_id = res[0]
    if not doc_id:
        return

    add_usedtime(*event)
    return


@bindings.add('c-u', filter=is_viewing_or_details & is_item_view)
def do_touch(*event):
    ok = dataview.touch(text_area.document.cursor_position_row)
    if ok:
        set_text(dataview.show_active_view())
        loop = asyncio.get_event_loop()
        loop.call_later(0, item_changed, loop)
    else:
        show_message('Update last-modified', "Update last-modified failed")


@bindings.add('F', filter=is_viewing_or_details & is_item_view)
def do_finish(*event):

    ok, show, item_id, job_id, due = dataview.maybe_finish(text_area.document.cursor_position_row)
    ampm = settings['ampm']
    fmt = "ddd M/D h:mmA" if ampm else "ddd M/D H:mm"

    if not ok:
        return

    def coroutine():

        dialog = TextInputDialog(
            title='finish task/job',
            label_text=f"selected: {show}\ndatetime completed:",
            default='now'
            )

        done_str = yield from show_dialog_as_float(dialog)
        if done_str:
            try:
                done = parse_datetime(done_str, z='local')[1]

                ok = True
            except:
                ok = False
            if ok:
                # valid done
                res = item.finish_item(item_id, job_id, done, due)
                if res:
                    if item_id in dataview.itemcache:
                        del dataview.itemcache[item_id]
                    loop = asyncio.get_event_loop()
                    loop.call_later(0, data_changed, loop)
            else:
                show_message('Finish task/job?', f"Invalid finished datetime: {done_str}")

    asyncio.ensure_future(coroutine())

@bindings.add('C', filter=is_viewing_or_details & is_item_view & is_items_table)
def edit_copy(*event):
    global item
    global starting_buffer_text
    app = get_app()
    app.editing_mode = EditingMode.VI if settings['vi_mode'] else EditingMode.EMACS
    if dataview.is_showing_details:
        application.layout.focus(text_area)
        dataview.hide_details()
    dataview.is_editing = True
    doc_id, entry = dataview.get_details(text_area.document.cursor_position_row, True)
    item.edit_copy(doc_id, entry)
    entry_buffer.text = item.entry
    starting_buffer_text = item.entry
    default_buffer_changed(event)
    default_cursor_position_changed(event)
    application.layout.focus(entry_buffer)

@bindings.add('g', filter=is_viewing & is_not_editing)
def do_goto(*event):
    row = text_area.document.cursor_position_row
    if not row:
        logger.debug(f"do_goto failed to return a row for cursor position {cursor_position_row}")
        return
    res = dataview.get_row_details(row) # item_id, instance, job_id
    if res:
        logger.debug(f"get_row_details for row {row} returned {res} ")
    else:
        return
    doc_id = res[0]
    # we have a row and a doc_id
    ok, goto = dataview.get_goto(row)
    logger.debug(f"calling get_goto on row {row} with doc_id {res[0]} - returned: {ok}, {goto}")
    if ok and goto:
        res = openWithDefault(goto)
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

@bindings.add('P', filter=is_viewing_or_details & is_item_view & is_items_table)
def toggle_pinned(*event):
    row = text_area.document.cursor_position_row
    res = dataview.toggle_pinned(row)
    dataview.refreshRelevant()
    set_text(dataview.show_active_view())
    text_area.buffer.cursor_position = \
                    text_area.buffer.document.translate_row_col_to_index(row, 0)

@bindings.add('f5')
def do_import_file(*event):
    inbasket = os.path.join(etmhome, "inbasket.text")
    default = inbasket if os.path.exists(os.path.expanduser(inbasket)) else etmhome
    msg = ""
    def coroutine():
        global msg
        dialog = TextInputDialog(
            title='import file',
            completer=PathCompleter(expanduser=True),
            default=default,
            label_text=f"""\
It is possible to import data from files with one
of the following extensions:
  .json  a json file exported from etm 3.2.x
  .text  a text file with etm entries as lines
  .ics   an iCalendar file
or a collection of internally generated examples
by entering the single word:
   lorem
Each of the examples is tagged 'lorem' and thus
can easily be removed with a single query:
   any t lorem | remove

Files imported from the etm home directory
   {etmhome}
will be removed after importing to avoid possible
duplications.

Enter the full path of the file to import or
'lorem':
""")

        file_path = yield from show_dialog_as_float(dialog)
        if not file_path:
           return
        if file_path.strip().lower() == 'lorem':
            logger.debug(f"calling import_file")
            ok, msg = import_file('lorem')
            if ok:
                dataview.refreshRelevant()
                dataview.refreshAgenda()
                dataview.refreshCurrent()
                dataview.refresh_konnections()
                loop = asyncio.get_event_loop()
                loop.call_later(0, data_changed, loop)
            show_message('import lorem', msg)

        else:
            if file_path:
                file_path = os.path.normpath(os.path.expanduser(file_path))
                ok, msg = import_file(file_path)
                if ok:
                    etm_dir = os.path.normpath(os.path.expanduser(etmdir))

                    if os.path.dirname(file_path) == etm_dir:
                        os.remove(file_path)
                        filehome = os.path.join("~", os.path.split(file_path)[1])
                        msg += f"\n and removed {filehome}"
                    dataview.refreshRelevant()
                    dataview.refreshAgenda()
                    dataview.refreshCurrent()
                    dataview.refresh_konnections()
                    loop = asyncio.get_event_loop()
                    loop.call_later(0, data_changed, loop)
                show_message('import file', msg)

    asyncio.ensure_future(coroutine())


@bindings.add('c-t', 'c-t', filter=is_viewing & is_item_view)
def do_whatever(*event):
    """
    For testing whatever
    """
    dataview.refreshCurrent()

@bindings.add('c-t', filter=is_viewing & is_item_view)
def quick_timer(*event):
    now = format_datetime(pendulum.now(), short=True)[1]
    def coroutine():
        dialog = TextInputDialog(
            title='Quick timer summary',
            label_text='summary:',
            default=now)

        summary = yield from show_dialog_as_float(dialog)

        if summary:
            item_hsh = {
                    'itemtype': '!',
                    'summary': summary,
                    'created': pendulum.now('UTC')
                    }

            doc_id = ETMDB.insert(item_hsh)
            if doc_id:
                dataview.next_timer_state(doc_id)
                dataview.next_timer_state(doc_id)
                dataview.refreshRelevant()
                dataview.refreshAgenda()
                dataview.refreshCurrent()
                dataview.refresh_konnections()
                loop = asyncio.get_event_loop()
                loop.call_later(0, data_changed, loop)
    asyncio.ensure_future(coroutine())


@bindings.add('c-x', filter=is_viewing & is_item_view)
def toggle_archived_status(*event):
    """
    If using items table move the selected item to the archive table and vice versa.
    """
    res = dataview.move_item(text_area.document.cursor_position_row)
    if not res:
        return
    application.layout.focus(text_area)
    loop = asyncio.get_event_loop()
    if dataview.query_mode == "items table":
        set_text(dataview.show_active_view())
        loop.call_later(0, data_changed, loop)
    else:
        set_text("The reminder has been moved to items table.\nRun the previous query again to update the display")
        text = f"a { dataview.query_text }"
        dataview.use_items()
        item.use_items()
        loop.call_later(0, data_changed, loop)
        loop.call_later(.1, do_complex_query, text, loop)
    return


@bindings.add('c-q')
def exit(*event):
    tmp = []
    if is_editing() and entry_buffer_changed():
        tmp.append('unsaved edits')
    if dataview.unsaved_timers():
        tmp.append('unrecorded timers')
    if tmp:
        prompt = f"There are {' and '.join(tmp)}.\nClose etm anyway?"
        discard_changes(event, prompt)
    else:
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
    set_view('a')

@bindings.add('b', filter=is_viewing)
def busy_view(*event):
    set_view('b')
    busy_details = dataview.busy_details
    if dataview.busy_row:
        text_area.buffer.cursor_position = \
            text_area.buffer.document.translate_row_col_to_index(dataview.busy_row-1, 0)
    else:
        busy_area.text = get_busy_text()

@bindings.add('c', filter=is_viewing)
def completed_view(*event):
    set_view('c')

@bindings.add('q', filter=is_viewing)
def query_view(*event):
    ask_buffer.text = "Submit '?' for help or 'l' for a list of stored queries"
    set_view('q')
    dataview.show_query()
    application.layout.focus(query_area)

@bindings.add('u', filter=is_viewing)
def used_view(*event):
    set_view('u')

@bindings.add('U', filter=is_viewing)
def used_summary_view(*event):
    set_view('U')

@bindings.add('y', filter=is_viewing)
def yearly_view(*event):
    dataview.set_active_view('y')
    set_text(dataview.show_active_view())

@bindings.add('h', filter=is_viewing)
def history_view(*event):
    set_view('h')

@bindings.add('m', filter=is_viewing)
def timers_view(*event):
    set_view('m')

@bindings.add('p', filter=is_viewing)
def pinned_view(*event):
    set_view('p')

@bindings.add('f', filter=is_viewing)
def forthcoming_view(*event):
    set_view('f')

@bindings.add('d', filter=is_viewing)
def next_view(*event):
    set_view('d')

@bindings.add('e', filter=is_viewing)
def engaged_view(*event):
    set_view('e')

@bindings.add('j', filter=is_viewing)
def journal_view(*event):
    set_view('j')

@bindings.add('r', filter=is_viewing)
def review_view(*event):
    set_view('r')

@bindings.add('k', filter=is_viewing)
def show_konnections(*event):
    selected_id = dataview.get_details(text_area.document.cursor_position_row)[0]
    if selected_id in dataview.konnected:
        dataview.set_active_item(selected_id)
        set_view('k')

@bindings.add('t', filter=is_viewing)
def tag_view(*event):
    set_view('t')

@bindings.add('i', filter=is_viewing)
def index_view(*event):
    set_view('i')

@bindings.add('l', filter=is_viewing)
def location_view(*event):
    set_view('l')

def set_view(view):
    dataview.set_active_view(view)
    item.use_items()
    set_text(dataview.show_active_view())

def get_busy_day(d):
    busy_details = dataview.busy_details
    r = 5 + 2*(d-1)
    if not r in busy_details.keys():
        return
    text_area.buffer.cursor_position = \
        text_area.buffer.document.translate_row_col_to_index(r-1, 0)
    busy_area.text = busy_details.get(r, get_busy_text())
    dataview.busy_row = r


@bindings.add('1', filter=is_busy_view & is_viewing)
def get_busy_1(*event):
    get_busy_day(1)


@bindings.add('2', filter=is_busy_view & is_viewing)
def get_busy_1(*event):
    get_busy_day(2)


@bindings.add('3', filter=is_busy_view & is_viewing)
def get_busy_1(*event):
    get_busy_day(3)


@bindings.add('4', filter=is_busy_view & is_viewing)
def get_busy_1(*event):
    get_busy_day(4)


@bindings.add('5', filter=is_busy_view & is_viewing)
def get_busy_1(*event):
    get_busy_day(5)


@bindings.add('6', filter=is_busy_view & is_viewing)
def get_busy_1(*event):
    get_busy_day(6)


@bindings.add('7', filter=is_busy_view & is_viewing)
def get_busy_1(*event):
    get_busy_day(7)



@bindings.add('enter', filter=is_busy_view & is_viewing)
def curr_busy(*event):
    busy_details = dataview.busy_details
    if not busy_details:
        return
    current_row = text_area.document.cursor_position_row + 1
    busy_area.text = busy_details.get(current_row, get_busy_text())


@bindings.add('down', filter=is_busy_view & is_viewing)
def next_busy(*event):
    busy_details = dataview.busy_details
    if not busy_details:
        return
    rows = [x for x in busy_details.keys()]
    rows.sort()
    current_row = text_area.document.cursor_position_row + 1
    next_row = rows[-1]
    for r in rows:
        if r > current_row:
            next_row = r
            break
    text_area.buffer.cursor_position = \
        text_area.buffer.document.translate_row_col_to_index(next_row-1, 0)
    busy_area.text = busy_details.get(next_row, get_busy_text())
    dataview.busy_row = next_row


@bindings.add('up', filter=is_busy_view & is_viewing)
def previous_busy(*event):
    busy_details = dataview.busy_details
    if not busy_details:
        return
    rows = [x for x in busy_details.keys()]
    rows.sort(reverse=True)
    current_row = text_area.document.cursor_position_row + 1
    next_row = 1
    for r in rows:
        if r < current_row:
            next_row = r
            break
    text_area.buffer.cursor_position = \
        text_area.buffer.document.translate_row_col_to_index(next_row-1, 0)
    busy_area.text = busy_details.get(next_row, "")
    dataview.busy_row = next_row


@bindings.add('down', filter=is_not_busy_view & is_not_yearly_view & is_viewing)
def next_id(*event):
    row2id = dataview.row2id
    if not row2id:
        return
    rows = [x for x in row2id.keys()]
    rows.sort()
    current_row = text_area.document.cursor_position_row
    next_row = rows[-1]
    for r in rows:
        if r > current_row:
            next_row = r
            break
    if next_row in rows:
        next_id = row2id[next_row][0] if isinstance(row2id[next_row], tuple) else row2id[next_row]
    else:
        next_id = "?"
    text_area.buffer.cursor_position = \
        text_area.buffer.document.translate_row_col_to_index(next_row, 0)



@bindings.add('up', filter=is_not_busy_view & is_not_yearly_view & is_viewing)
def previous_id(*event):
    row2id = dataview.row2id
    if not row2id:
        return
    rows = [x for x in row2id.keys()]
    rows.sort(reverse=True)
    current_row = text_area.document.cursor_position_row
    next_row = 1
    for r in rows:
        if r < current_row:
            next_row = r
            break
    if next_row in rows:
        next_id = row2id[next_row][0] if isinstance(row2id[next_row], tuple) else row2id[next_row]
    else:
        next_id = "?"
    text_area.buffer.cursor_position = \
        text_area.buffer.document.translate_row_col_to_index(next_row, 0)


@bindings.add('c-p', filter=is_viewing)
def next_pinned(*event):
    """
    Move the cursor to the next row corresponding to a pinned id if there is such a row and to row 0 otherwise.
    """
    pinned = dataview.pinned_list
    if not pinned:
        return
    rows = [(k, v) for k, v in dataview.row2id.items() if v in pinned]
    if not rows:
        return
    rows.sort()
    cur_row = text_area.document.cursor_position_row
    nxt = 0
    for k, v in rows:
        if k > cur_row:
            nxt = k
            break
    text_area.buffer.cursor_position = \
        text_area.buffer.document.translate_row_col_to_index(nxt, 0)


@bindings.add('Z', filter=is_viewing)
def toggle_goto_id(*event):
    """
    If goto id is set, remove it. Else set it to the id of the selected item.
    """
    dataview.goto_id = None if dataview.goto_id else dataview.get_details(text_area.document.cursor_position_row)[0]



@bindings.add('right', filter=is_agenda_view & is_viewing)
def nextweek(*event):
    dataview.nextYrWk()
    dataview.busy_row = 0
    busy_details = dataview.busy_details
    busy_area.text = '' # get_busy_text()
    set_text(dataview.show_active_view())


@bindings.add('left', filter=is_agenda_view & is_viewing)
def prevweek(*event):
    dataview.prevYrWk()
    dataview.busy_row = 0
    busy_details = dataview.busy_details
    busy_area.text = '' # get_busy_text()
    set_text(dataview.show_active_view())

@bindings.add('space', filter=is_agenda_view & is_viewing)
def currweek(*event):
    dataview.currYrWk()
    dataview.busy_row = 0
    busy_details = dataview.busy_details
    busy_area.text = ""
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
def prevcal(*event):
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
    if dataview.is_showing_details:
        application.layout.focus(text_area)
        dataview.hide_details()
    else:
        tmp = dataview.get_details(text_area.document.cursor_position_row)[1]
        if tmp:
            dataview.show_details()
            details_area.text = tmp.rstrip()
            application.layout.focus(details_area)


@bindings.add('c-z', filter=is_editing, eager=True)
def close_edit(*event):
    global text_area
    row, col = get_row_col()
    if entry_buffer_changed():
        save_before_quit()
    else:
        app = get_app()
        app.editing_mode = EditingMode.EMACS
        dataview.is_editing = False
        application.layout.focus(text_area)
        set_text(dataview.show_active_view())
    restore_row_col(row, col)

@edit_bindings.add('c-s', filter=is_editing, eager=True)
def save_changes(*event):
    if entry_buffer_changed():
        maybe_save(item)
    else:
        # no changes to save - close editor
        dataview.is_editing = False
        application.layout.focus(text_area)
        set_text(dataview.show_active_view())
        app = get_app()
        app.editing_mode = EditingMode.EMACS


def maybe_save(item):
    # check hsh
    global text_area
    msg = item.check_item_hsh()
    if msg:
        show_message('Error', ", ".join(msg))
        return
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

    row, col = get_row_col()
    app = get_app()
    app.editing_mode = EditingMode.EMACS
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
        MenuItem('F6) datetime calculator', handler=dt_calculator),
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
        MenuItem('e) engaged', handler=engaged_view),
        MenuItem('f) forthcoming', handler=forthcoming_view),
        MenuItem('h) history', handler=history_view),
        MenuItem('i) index', handler=index_view),
        MenuItem('j) journal', handler=journal_view),
        MenuItem('l) location', handler=location_view),
        MenuItem('m) timers', handler=timers_view),
        MenuItem('p) pinned', handler=pinned_view),
        MenuItem('q) query', handler=query_view),
        MenuItem('r) review', handler=review_view),
        MenuItem('t) tags', handler=tag_view),
        MenuItem('u) used time', handler=used_view),
        MenuItem('U) used summary', handler=used_summary_view),
        MenuItem('-', disabled=True),
        MenuItem("s) scheduled alerts for today", handler=do_alerts),
        MenuItem('y) yearly calendar', handler=yearly_view),
        MenuItem('-', disabled=True),
        MenuItem('/|?|,,) search forward|backward|clear search'),
        MenuItem('n) next incrementally in search'),
        MenuItem('^l) prompt for and jump to line number', handler=do_go_to_line),
        MenuItem('^p) jump to next pinned item', handler=next_pinned),
        MenuItem('^c) copy active view to clipboard', handler=copy_active_view),
        MenuItem('^t) start quick timer', handler=quick_timer),
        MenuItem('-', disabled=True),
        MenuItem('J) jump to date in a), b) and c)', handler=do_jump_to_date),
        MenuItem('right) next in a), b), c), u), U) and y)'),
        MenuItem('left) previous in a), b), c), u), U) and y)'),
        MenuItem('space) current in a), b), c), u), U) and y)'),
    ]),
    MenuItem('editor', children=[
        MenuItem('N) create new item', handler=edit_new),
        MenuItem('-', disabled=True),
        MenuItem('^s) save changes & close', handler=save_changes),
        MenuItem('^g) test goto link', handler=do_goto),
        MenuItem('^r) show repetitions', handler=is_editing_reps),
        MenuItem('^z) discard changes & close', handler=close_edit),
    ]),
    MenuItem('selected', children=[
        MenuItem('Enter) toggle showing details', handler=show_details),
        MenuItem('E) edit', handler=edit_existing),
        MenuItem('C) edit copy', handler=edit_copy),
        MenuItem('D) delete', handler=do_maybe_delete),
        MenuItem('F) finish', handler=do_finish),
        MenuItem('P) toggle pin', handler=toggle_pinned),
        MenuItem('R) reschedule',  handler=do_reschedule),
        MenuItem('S) schedule new', handler=do_schedule_new),
        MenuItem('g) open goto link', handler=do_goto),
        MenuItem('k) show konnections', handler=show_konnections),
        MenuItem('^r) show repetitions', handler=not_editing_reps),
        MenuItem('^u) update last modified', handler=do_touch),
        MenuItem('^x) toggle archived status', handler=toggle_archived_status),
        MenuItem('-', disabled=True),
        MenuItem('T) activate timer if none active ', handler=next_timer_state),
        MenuItem("TR) add usedtime / record usedtime and end timer", handler=record_time),
        MenuItem('TD) delete timer', handler=maybe_delete_timer),
        MenuItem('TT) toggle paused/running for the active timer', handler=toggle_active_timer),
    ]),
], floats=[
    Float(xcursor=True,
          ycursor=True,
          content=CompletionsMenu(
              max_height=16,
              scroll_offset=1)),
])


def set_askreply(_):
    if item.active:
        ask, reply = item.askreply[item.active]
    elif item.askreply.get(('itemtype', '')):
        ask, reply = item.askreply[('itemtype', '')]
    else:
        ask, reply = ('', '')
    ask_buffer.text = ask
    reply_buffer.text = wrap(reply, 0)


async def main(etmdir=""):
    global item, settings, ampm, style, type_colors, application, busy_colors
    ampm = settings['ampm']
    window_colors = settings['window_colors']
    type_colors = settings['type_colors']
    window_colors = settings['window_colors']
    busy_colors = {
            VSEP    : type_colors['wrap'],
            HSEP    : type_colors['wrap'],
            BUSY    : type_colors['event'],
            CONF    : type_colors['inbox'],
            ADAY    : type_colors['wrap'],
            }
    # query = ETMQuery()
    style = get_style(window_colors)
    agenda_view()

    application = Application(
        layout=Layout(
            root_container,
            focused_element=text_area,
        ),
        # set editing_mode in the entry buffer, use default elsewhere
        key_bindings=bindings,
        enable_page_navigation_bindings=True,
        mouse_support=True,
        style=style,
        full_screen=True)
    logger.debug("XX starting event_handler")
    background_task = asyncio.create_task(event_handler())
    try:
        await application.run_async()
    finally:
        background_task.cancel()
        logger.info("Quitting event loop.")


if __name__ == '__main__':
    sys.exit('view.py should only be imported')
