#!/usr/bin/env python
"""
A user interface based on prompt_toolkit.
"""
from __future__ import unicode_literals

import sys
import inspect
import tinydb

# from prompt_toolkit import __version__ as prompt_toolkit_version

# import prompt_toolkit.application as pta
import prompt_toolkit.application

# from prompt_toolkit.application import Application
# from prompt_toolkit.application.current import get_app
# from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import Completion, Completer, FuzzyCompleter
from prompt_toolkit.shortcuts import CompleteStyle, prompt
from prompt_toolkit.cursor_shapes import CursorShape
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.filters import Condition
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings


from prompt_toolkit.key_binding.bindings.focus import (
    focus_next,
    focus_previous,
)
from prompt_toolkit.key_binding.vi_state import InputMode
from prompt_toolkit.layout import Dimension
from prompt_toolkit.layout import Float
from prompt_toolkit.layout.containers import (
    HSplit,
    VSplit,
    Window,
    WindowAlign,
    ConditionalContainer,
)
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.selection import SelectionType
from prompt_toolkit.styles import Style
from prompt_toolkit.styles.named_colors import NAMED_COLORS
from prompt_toolkit.widgets import Box, Label, Button
from prompt_toolkit.widgets import HorizontalLine
from prompt_toolkit.widgets import (
    TextArea,
    SearchToolbar,
    MenuContainer,
    MenuItem,
)
from zoneinfo import ZoneInfo

from packaging.version import parse as parse_version

import shutil
from shlex import split as qsplit
import time
from datetime import datetime, date, timedelta

import requests
import asyncio
import textwrap

import re
import subprocess   # for check_output

import platform
import os
from glob import glob
import contextlib, io

import pyperclip
from etm.common import ETM_CHAR
from etm.common import TimeIt

from tinydb import where
from tinydb import Query
from pygments.lexer import RegexLexer
from pygments.token import Keyword
from pygments.token import Literal
from pygments.token import Operator
from pygments.token import Comment

# from etm.model import ETMDB

# from etm.model import ETMDB

pta = prompt_toolkit.application
get_app = prompt_toolkit.application.current.get_app
Buffer = prompt_toolkit.buffer.Buffer

for key, value in ETM_CHAR.items():
    globals()[key] = value

# set in __main__
logger = None

dataview = None
item = None
style = None
application = None

############ begin query ###############################

class UpdateStatus:
    def __init__(self, new=''):
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
            (
                r'\b(begins|includes|in|equals|more|less|exists|any|all|one)\b',
                Keyword,
            ),
            (
                r'\b(replace|remove|archive|delete|set|provide|attach|detach)\b',
                Keyword,
            ),
            (r'\b(itemtype|summary)\b', Literal),
            (r'\b(and|or|info)\b', Keyword),
        ],
    }


def format_week(dt, fmt='WWW'):
    """ """
    wm = re.compile(r'^W{1,5}$')
    if not wm.match(fmt.strip()):
        return f'bad fmt: {fmt}'

    if fmt == 'W':
        return dt.strftime("%-W")

    if len(fmt) < 3:
        year_part = ""
    elif len(fmt) == 3:
        year_part = ", %Y"
    else:
        year_part = ", %Y #%-W"

    dt_year, dt_week = dt.isocalendar()[:2]

    mfmt = '%B %-d' if fmt == 'WWWWW' else '%b %-d'

    wkbeg = datetime.strptime(f'{dt_year} {str(dt_week)} 1', '%Y %W %w').date()
    wkend = datetime.strptime(f'{dt_year} {str(dt_week)} 0', '%Y %W %w').date()
    week_begin = wkbeg.strftime(mfmt)
    if wkbeg.month == wkend.month:
        week_end = wkend.strftime('%-d')
    else:
        week_end = wkend.strftime(mfmt)
    return f'{week_begin} - {week_end}{year_part}'


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
            'dt': self.dt,
        }

        self.op = {
            '=': self.maybe_equal,
            '>': self.maybe_later,
            '<': self.maybe_earlier,
        }

        self.update = {
            'replace': self.replace,  # a, rgx, rep
            'remove': self.remove,  #
            'archive': self.archive,  #
            'delete': self.delete,  # a
            'set': self.set,  # a, b
            'provide': self.provide,  # a, b
            'attach': self.attach,  # a, b
            'detach': self.detach,  # a, b
        }

        self.changed = False

        self.lexer = PygmentsLexer(TDBLexer)
        self.Item = Query()

        self.allowed_commands = ', '.join([x for x in self.filters])

    def replace(self, a, rgx, rep, items):
        """
        Replace matches for rgx with rep in item['a']. If item['a']
        is a list, do this for each element in item['a']
        """
        changed = []
        rep = re.sub(r'\\s', ' ', rep)
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
                    item['modified'] = datetime.now().astimezone()
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
            if dataview.query_mode == 'items table':
                # move to archive
                DBARCH.insert_multiple(items)
                DBITEM.remove(doc_ids=rem_ids)
            else:
                # back to items
                DBITEM.insert_multiple(items)
                DBARCH.remove(doc_ids=rem_ids)
        except Exception as e:
            logger.error(
                f'move from {dataview.query_mode} failed for items: {items}; rem_ids: {rem_ids}; exception: {e}'
            )
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
                item['modified'] = datetime.now().astimezone()
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
        b = re.sub(r'\\\s', ' ', b)
        for item in items:
            item[a] = b
            item['modified'] = datetime.now().astimezone()
            changed.append(item)
        if changed:
            write_back(dataview.db, changed)
            self.changed = True

    def provide(self, a, b, items):
        """
        Provide item['a'] = b for items without an exising entry for 'a'.
        """
        changed = []
        b = re.sub(r'\\\s', ' ', b)
        for item in items:
            item.setdefault(a, b)
            item['modified'] = datetime.now().astimezone()
            changed.append(item)
        if changed:
            write_back(dataview.db, changed)
            self.changed = True

    def attach(self, a, b, items):
        """
        Attach 'b' into the item['a'] list if 'b' is not in the list.
        """
        changed = []
        b = re.sub(r'\\\s', ' ', b)
        for item in items:
            if a not in item:
                item.setdefault(a, []).append(b)
                item['modified'] = datetime.now().astimezone()
                changed.append(item)
            elif isinstance(item[a], list) and b not in item[a]:
                item.setdefault(a, []).append(b)
                item['modified'] = datetime.now().astimezone()
                changed.append(item)
        if changed:
            write_back(dataview.db, changed)
            self.changed = True

    def detach(self, a, b, items):
        """
        Detatch 'b' from the item['a'] list if it belongs to the list.
        """
        changed = []
        b = re.sub(r'\\\s', ' ', b)
        for item in items:
            if a in item and isinstance(item[a], list) and b in item[a]:
                item[a].remove(b)
                item['modified'] = datetime.now().astimezone()
                changed.append(item)
        if changed:
            write_back(dataview.db, changed)
            self.changed = True

    def is_datetime(self, val):
        return isinstance(val, datetime)

    def is_date(self, val):
        return isinstance(val, date) and not isinstance(val, datetime)

    def maybe_equal(self, val, args):
        """
        args = year-month-...-minute
        """
        args = args.split('-')
        # args = list(args)
        if not isinstance(val, date):
            # neither a date or a datetime
            return False
        if args and val.year != int(args.pop(0)):
            return False
        if args and val.month != int(args.pop(0)):
            return False
        if args and val.day != int(args.pop(0)):
            return False
        if isinstance(val, datetime):
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
        args = args.split('-')
        # args = list(args)
        if not isinstance(val, date):
            # neither a date or a datetime
            return False
        if args and not val.year >= int(args.pop(0)):
            return False
        if args and not val.month >= int(args.pop(0)):
            return False
        if args and not val.day >= int(args.pop(0)):
            return False
        if isinstance(val, datetime):
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
        args = args.split('-')
        # args = list(args)
        if not isinstance(val, date):
            # neither a date or a datetime
            return False
        if args and not val.year <= int(args.pop(0)):
            return False
        if args and not val.month <= int(args.pop(0)):
            return False
        if args and not val.day <= int(args.pop(0)):
            return False
        if isinstance(val, datetime):
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
        return item if item else f'doc_id {a} not found'

    def dt(self, a, b):
        if b[0] == '?':
            if b[1] == 'time':
                return self.Item[a].test(self.is_datetime)
            elif b[1] == 'date':
                return self.Item[a].test(self.is_date)

        return self.Item[a].test(self.op[b[0]], b[1])

    def process_query(self, query):
        """ """
        dataview.last_query = []
        [fltr, *updt] = [x.strip() for x in query.split(' | ')]
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
                    return (
                        False,
                        wrap(
                            f"""bad command: '{part[0]}'. Only commands in {self.allowed_commands} are allowed."""
                        ),
                        updt,
                    )

            if len(part) > 3:
                if part[0] in ['in', 'includes']:
                    if negation:
                        cmnds.append(
                            ~self.filters[part[0]](
                                [x.strip() for x in part[1:-1]], part[-1]
                            )
                        )
                    else:
                        cmnds.append(
                            self.filters[part[0]](
                                [x.strip() for x in part[1:-1]], part[-1]
                            )
                        )
                else:
                    if negation:
                        cmnds.append(
                            ~self.filters[part[0]](
                                part[1], [x.strip() for x in part[2:]]
                            )
                        )
                    else:
                        cmnds.append(
                            self.filters[part[0]](
                                part[1], [x.strip() for x in part[2:]]
                            )
                        )
            elif len(part) > 2:
                if negation:
                    cmnds.append(~self.filters[part[0]](part[1], part[2]))
                else:
                    cmnds.append(self.filters[part[0]](part[1], part[2]))
            elif len(part) > 1:
                if negation:
                    cmnds.append(~self.filters[part[0]](part[1]))
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
        """ """
        if query in ['?', 'help']:
            query_help = 'https://dagraham.github.io/etm-dgraham/#query-view'
            openWithDefault(query_help)
            return False, 'opened query help using default browser'
        try:
            ok, res, updt = self.process_query(query)
            if not ok or isinstance(res, str):
                return False, res

            if isinstance(res, tinydb.table.Document):
                return False, item_details(res)
            else:
                items = dataview.db.search(res)
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


def show_work_in_progress(func: str = ''):
    name = inspect.currentframe().f_code.co_name
    show_message('-- Not Yet Implemented', f'"{func}" is a work in progess.')


def show_message(title, text, padding=6):
    if dataview.is_showing_details:
        # close the details window
        application.layout.focus(text_area)
        dataview.hide_details()

    # prep the message window
    width = shutil.get_terminal_size()[0] - 2
    heading = f'-- {title.rstrip()} --'.center(width, ' ')
    prompt = '<enter> closes'.center(width, ' ')
    tmp = f"""\
{heading}
{text}

{prompt}
"""

    dataview.show_details()
    details_area.text = wrap_text(tmp)
    application.layout.focus(details_area)


def get_choice(title, text, options=[]):
    if dataview.is_showing_choice:
        # only one choice at a time
        return

    if dataview.is_showing_details:
        # close the details view
        application.layout.focus(text_area)
        dataview.hide_details()

    width = shutil.get_terminal_size()[0] - 2
    heading = f'-- {title.rstrip()} --'.center(width, ' ')

    opt_choices = ', '.join([x.split(':')[0].strip() for x in options[:-1]])
    opt_choices += f" or {options[-1].split(':')[0].strip()}"
    # opt_choices = ", ".join([str(x) for x in range(1, len(options))])
    text = text.rstrip()
    if options:
        for opt in options:
            text += f"\n{4*' '}{opt.rstrip()}"

    text += f'\n\nPress {opt_choices}.'
    choice_title_buffer.text = heading
    choice_display_area.text = wrap_text(text)
    dataview.show_choice()


starting_entry_text = ''


def get_entry(title: str, text: str, default: str, event) -> any:
    """process a user input string and, when <enter> is pressed store the result in dataview.get_entry_content.  E.g., the name of a file to import, a date to display in a weekly view, the number of a line to show.

    The function that calls this should provide a coroutine stored as dataview.got_entry. Execute this coroutine to process dataview.get_entry_content when this is closed


    Args:
        title (str): title for the input dialog -> ask_buffer
        prompt (str): instructions about the proper input -> reply buffer
        default (str, optional): default/starting entry. Defaults to "" Is this needed?.

    Returns:
        any
    """
    if dataview.is_editing:
        # finish edit first
        return

    if dataview.is_showing_choice:
        # only one dialog at a time
        return

    if dataview.is_showing_details:
        # close details as lower priority
        application.layout.focus(text_area)
        dataview.hide_details()

    global starting_entry_text
    width = shutil.get_terminal_size()[0] - 2
    heading = f'-- {title.rstrip()} --'.center(width, ' ')

    ret = '<return>: to proceed'.center(width, ' ')
    esc = '<escape>: to cancel'.center(width, ' ')

    bp = f"""and press
{ret}
{esc}\
    """
    text = wrap_text(text + bp)

    entry_title_buffer.text = heading
    entry_display_area.text = wrap_text(text)
    entry_buffer.text = ' ' + default
    dataview.show_entry()
    entry_buffer_changed(event)
    # default_cursor_position_changed(event)
    application.layout.focus(entry_buffer)


def wrap_text(text: str, init_indent: int = 0, subs_indent: int = 0):
    # Split the text into paragraphs (separated by newline characters)
    width = shutil.get_terminal_size()[0] - 2
    paragraphs = text.split('\n')

    # Wrap each paragraph separately
    wrapped_text = [
        textwrap.fill(
            paragraph,
            width,
            initial_indent=init_indent * ' ',
            subsequent_indent=subs_indent * ' ',
        )
        for paragraph in paragraphs
    ]

    # Join the wrapped paragraphs with newline characters
    return '\n'.join(wrapped_text)


# Key bindings.
bindings = KeyBindings()


@Condition
def is_showing_entry(*event):
    return dataview.is_showing_entry


@Condition
def is_not_showing_entry(*event):
    return not dataview.is_showing_entry


def is_searching(*event):
    return get_app().current_search_state

def is_not_searching(*event):
    return not get_app().current_search_state


@bindings.add('f2')
def do_about(*event):
    show_message('ETM Information', about(2)[0], 10)


@bindings.add('f4')
def do_check_updates(*event):
    status, res = check_update()
    # '?', None (info unavalable)
    # UPDATE_CHAR, available_version (update to available_version is possible)
    # '', current_version (current_version is the latest available)
    if status in ['?', '']:   # message only
        show_message('Update Information', res, 2)
    else:   # update available
        title = 'Update Available'
        options = [
            '<return>: yes, install update',
            '<escape>: no, do not install now',
        ]
        get_choice(title, res, options)

        def coroutine():
            keypress = dataview.details_key_press
            done = keypress in ['escape', Keys.ControlM]
            if keypress == Keys.ControlM:
                ok, msg = check_output(settings['update_command'])
                tmp = [x.strip() for x in msg.split('\n')]
                lines = [wrap(tmp[0])]
                for line in tmp[1:]:
                    if line and not line.startswith('Requirement already'):
                        lines.append(wrap(line))
                success = wrap(
                    'If the update was sucessful, you will need to restart etm for it to take effect.'
                )
                prompt = '\n'.join(lines)
                # prompt = wrap("\n".join(msg.split('\n')[:1]))

                if ok:
                    show_message('ETM Update', f'{prompt}\n\n{success}', 2)
                    # show_message("etm update", prompt, 2)
                else:
                    show_message('ETM Update', prompt, 2)
            else:
                show_message('ETM Update', 'cancelled')

            return done

        dataview.got_choice = coroutine


def check_update():
    url = 'https://raw.githubusercontent.com/dagraham/etm-dgraham/master/etm/__version__.py'
    try:
        r = requests.get(url)
        t = r.text.strip()
        # t will be something like "version = '4.7.2'"
        url_version = t.split(' ')[-1][1:-1]
        # split(' ')[-1] will give "'4.7.2'" and url_version will then be '4.7.2'
    except:
        url_version = None
    if url_version is None:
        res = 'Update information is currently unavailable. Please check your wifi connection.'
        status_char = '?'
    else:
        # kluge for purely numeric versions
        # if [int(x) for x in url_version.split('.')] > [int(x) for x in etm_version.split('.')]:
        # from packaging.version parse
        if parse_version(url_version) > parse_version(etm_version):
            status_char = UPDATE_CHAR
            res = f"""\
An update is available to {url_version}. Do you want to update now?
If so, a restart will be necessary for the changes to take effect."""
        else:
            status_char = ''
            res = f'The installed version, {etm_version}, is the latest available.'

    return status_char, res


update_status = UpdateStatus()


async def updates_loop(loop):
    logger.debug('XXX update_loop XXX')
    status, res = check_update()
    update_status.set_status(status)


async def refresh_loop(loop):
    logger.debug('XXX refresh_loop XXX')
    dataview.refreshRelevant()
    dataview.refreshAgenda()
    dataview.refreshCurrent()
    set_text(dataview.show_active_view())
    get_app().invalidate()


@bindings.add('f3')
def do_system(*event):
    show_message('System Information', about(22)[1], 20)


@bindings.add('f6')
def dt_calculator(*event):
    # func  = inspect.currentframe().f_code.co_name
    # show_work_in_progress(func)
    # return

    title = 'DateTime Calculator'
    text = """\
Enter an expression of the form:
    x [+-] y
where x is a datetime and y is either
    [+] a timeperiod
    [-] a datetime or a timeperiod
Be sure to surround [+-] with spaces.
Timezones can be appended to x and y.

Enter the expression """
    default = dataview.calculator_expression
    get_entry(title, text, default, event)

    def coroutine():
        expression = dataview.entry_content.rstrip()
        if expression:
            dataview.calculator_expression = expression
            res = datetime_calculator(expression)
            _ = f"""\
  {expression} =>
    {res}
"""
            show_message(title, _)
            # entry_prompt_buffer.text = text + f"\n{wrap_text(res)}"
        else:
            dataview.calculator_expression = ''

            show_message(title, 'cancelled')

    dataview.got_entry = coroutine


@bindings.add('f7')
def do_open_config(*event):
    openWithDefault(cfgfile)


@bindings.add('f8')
def do_show_help(*event):
    help_link = 'https://dagraham.github.io/etm-dgraham/'
    openWithDefault(help_link)


def add_usedtime(*event):

    doc_id, instance, job = dataview.get_row_details(
        text_area.document.cursor_position_row
    )

    if not doc_id:
        return

    hsh = DBITEM.get(doc_id=doc_id)

    state2fmt = {
        'i': 'inactive',
        'r': 'running',
        'p': 'paused',
    }

    now = datetime.now().astimezone()
    if doc_id in dataview.timers:
        state, start, elapsed = dataview.timers[doc_id]
        if state == 'r':
            elapsed += now - start
            start = now
        timer = f'timer:\n  status: {state2fmt[state]}\n  last change: {format_datetime(start, short=True)[1]}\n  elapsed time: {format_duration(elapsed, short=True)}'

        default = f'{format_duration(elapsed, short=True)}: {format_datetime(now, short=True)[1]}'
    else:
        state = None
        timer = 'timer: none'
        default = f'0m: {format_datetime(now, short=True)[1]}'

    title = 'Record Used Time'

    text = f"""\
selected: {hsh['itemtype']} {hsh['summary']}
@i (index): {hsh.get('i', '~')}
{timer}

Enter an expression of the form "period: datetime", e.g., "1h27m: 3:20p", in the entry area below. The default is the current period from the timer ("0m" if there is no timer) and the current datetime. Make any changes you like """

    get_entry(title, text, default, event)

    def coroutine():
        usedtime = dataview.entry_content.strip()

        if usedtime:
            msg = []
            ut = [x.strip() for x in usedtime.split(': ')]
            if len(ut) != 2:
                ok = False
                msg.append(f"The entry '{usedtime}' is invalid")

            else:
                ok, per = model.parse_duration(ut[0])
                if not ok:
                    msg.append(f"The entry '{ut[0]}' is not a valid period")

                ok, dt, z = model.parse_datetime(ut[1])
                if not ok:
                    msg.append(f"The entry '{ut[1]}' is not a valid datetime")
            if msg:
                msg = '\n   '.join(msg)
                show_message(title, f'Cancelled,  {msg}')
                return

            changed, msg = item.add_used(doc_id, per, dt)
            if changed:
                dataview.timer_clear(doc_id)

                if doc_id in dataview.itemcache:
                    del dataview.itemcache[doc_id]
                application.layout.focus(text_area)
                application.output.set_cursor_shape(CursorShape.BLOCK)
                set_text(dataview.show_active_view())
                loop = asyncio.get_event_loop()
                loop.call_later(0, data_changed, loop)
            else:
                show_message('add used time', f'Cancelled, {msg}')

        else:
            show_message(title, 'cancelled')

    dataview.got_entry = coroutine


today = datetime.today()
calyear = today.year
calmonth = today.month


def check_output(cmd):
    if not cmd:
        return
    res = ''
    try:
        res = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT,
            shell=True,
            universal_newlines=True,
            encoding='UTF-8',
        )
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
    return get_app().layout.has_focus(text_area) or get_app().layout.has_focus(
        details_area
    )

@Condition
def is_showing_konnected():
    return dataview.active_view == 'konnected'

@Condition
def timer_active():
    return dataview.active_timer is not None


@Condition
def is_not_showing_konnected():
    return dataview.active_view != 'konnected'

@Condition
def is_showing_konnections():
    return dataview.is_showing_konnections


@Condition
def is_not_showing_konnections():
    return not dataview.is_showing_konnections


@Condition
def is_details():
    return get_app().layout.has_focus(details_area)


@Condition
def is_querying():
    return get_app().layout.has_focus(query_area)

@Condition
def is_not_querying():
    return not get_app().layout.has_focus(query_area)


@Condition
def is_items_table():
    return dataview.query_mode == 'items table'


@bindings.add(',', ',', filter=is_viewing)
def clear_search(*event):
    search_state = get_app().current_search_state
    text = search_state.text
    search_state.text = ''


@bindings.add('f1')
def menu(event=None):
    """Focus menu."""
    if event:
        if event.app.layout.has_focus(root_container.window):
            focus_previous(event)
        else:
            event.app.layout.focus(root_container.window)


@Condition
def is_item_view():
    return dataview.active_view in [
        'agenda',
        'completed',
        'effort',
        'history',
        'index',
        'tags',
        'journal',
        'do next',
        'used time',
        'relevant',
        'forthcoming',
        'query',
        'pinned',
        'review',
        'konnected',
        'timers',
        'location',
    ]


@Condition
def is_dated_view():
    return dataview.active_view in [
        'agenda',
        'completed',
        'busy',
    ] and get_app().layout.has_focus(text_area)


@Condition
def is_editing():
    return dataview.is_editing


@Condition
def is_not_editing():
    return not dataview.is_editing


@Condition
def dialog_active():
    return dataview.dialog_active


@Condition
def dialog_not_active():
    return not dataview.dialog_active


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
    return dataview.active_view in ['agenda', 'busy', 'completed', 'effort']


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
def is_not_showing_details():
    return dataview.is_showing_details == False


@Condition
def is_showing_details():
    return dataview.is_showing_details


# @Condition
# def is_showing_confirmation():
#     return dataview.is_showing_confirmation

# @Condition
# def is_not_showing_confirmation():
#     return dataview.is_showing_confirmation == False


@Condition
def is_showing_choice():
    return dataview.is_showing_choice


@Condition
def is_not_showing_choice():
    return dataview.is_showing_choice == False


@Condition
def is_showing_entry():
    return dataview.is_showing_entry


@Condition
def is_not_showing_entry():
    return dataview.is_showing_entry == False


bindings.add('tab', filter=is_not_editing)(focus_next)
bindings.add('s-tab', filter=is_not_editing)(focus_previous)


@bindings.add('c-s', filter=is_not_editing)
def do_nothing(*event):
    pass


@bindings.add('s', filter=is_viewing)
def do_alerts(*event):
    show_message('scheduled alerts', alerts(), 2)


@bindings.add('o', filter=is_viewing)
def do_occurrences(*event):
    show_message('Occurrences', dataview.show_occurrences(), 2)


@bindings.add('c-l', filter=is_viewing)
def do_go_to_line(*event):
    title = 'Go to line'
    text = 'Enter the line number '
    default = ''
    if dataview.current_row:
        default = dataview.current_row + 1

    get_entry(title, text, default, event)

    def coroutine():
        line_number = dataview.entry_content
        if line_number:
            try:
                line_number = int(line_number)
            except ValueError:
                show_message('go to line', 'Invalid line number')
            else:
                text_area.buffer.cursor_position = (
                    text_area.buffer.document.translate_row_col_to_index(
                        line_number, 0
                    )
                )

    dataview.got_entry = coroutine


@bindings.add('end', filter=is_dated_view)
def do_jump_to_date(*event):
    # func  = inspect.currentframe().f_code.co_name
    # show_work_in_progress(func)
    # return

    title = 'Jump to Date'
    text = """\
Enter the date """

    get_entry(title, text, '', event)

    def coroutine():
        target_date = dataview.entry_content

        if target_date:
            try:
                dataview.dtYrWk(target_date)
            except ValueError:
                show_message('jump to date', 'Invalid date')
            else:
                set_text(dataview.show_active_view())

    dataview.got_entry = coroutine


window_colors = None

grey_colors = {
    'grey1': '#396060',  # 1 shade lighter of darkslategrey for status and menubar background
    'grey2': '#1d3030',  # 2 shades darker of darkslategrey for textarea background
}


def get_colors(bg='', fg='', attr=''):
    if bg and bg in grey_colors:
        bg = f'bg:{grey_colors[bg]}'
    else:
        # background colors from NAMED_COLORS if possible
        bg = f'bg:{NAMED_COLORS.get(bg, bg)}' if bg else ''
    if fg and fg in grey_colors:
        fg = f'{grey_colors[fg]}'
    else:
        # foreground colors from NAMED_COLORS if possible
        fg = f'{NAMED_COLORS.get(fg, fg)}' if fg else ''
    return f'{bg} {fg} {attr}'.rstrip()


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
    '→': 'begin',
    '+': 'waiting',
    '✓': 'finished',
    '✗': 'finished',
    '~': 'missing',
    '◦': 'used',
    '↱': 'wrap',
    '↳': 'wrap',
    '↑': 'event',
    '↓': 'available',
}


def first_char(s):
    """
    Return the first non-whitespace character in s.
    """
    if not s.strip():
        # nothing but whitespace
        return None
    m = re.match(r'(\s+)', s)
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
                    logger.error(f'problem with typ {typ} from {tmp}')
                    logger.error(
                        f'sty: {sty}; type_colors.keys: {type_colors.keys()}'
                    )
            if tmp.rstrip().endswith('(Today)') or tmp.rstrip().endswith(
                '(Tomorrow)'
            ):
                return [(type_colors['today'], f'{tmp} ')]

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
    ampm = settings.get('ampm', True)
    dayfirst = settings.get('dayfirst', False)
    yearfirst = settings.get('yearfirst', False)
    month = dt.strftime('%b')
    day = dt.strftime('%-d')
    weekday = dt.strftime('%a')
    if dt.minute == 0:
        hourminutes = (
            dt.strftime('%-I%p').rstrip('M').lower()
            if ampm
            else dt.strftime('%H')
        )
    else:
        hourminutes = (
            dt.strftime('%-I:%M%p').rstrip('M').lower()
            if ampm
            else dt.strftime('%H:%M')
        )
    monthday = f'{day} {month}' if dayfirst else f'{month} {day}'
    return f'{hourminutes} {weekday} {monthday}'


def item_changed(loop):
    item.update_item_hsh()
    if dataview.active_view == 'timers' and item.doc_id not in dataview.timers:
        if dataview.active_timer:
            state = 'i'
        else:
            state = 'r'
            dataview.active_timer = item.doc_id
        dataview.timers[item.doc_id] = [
            state,
            datetime.now().astimezone(),
            timedelta(),
        ]
    dataview.get_completions()
    dataview.update_konnections(item)
    data_changed(loop)


def data_changed(loop):
    dataview.refreshRelevant()
    dataview.refreshAgenda()
    set_text(dataview.show_active_view())
    dataview.refreshCurrent()
    if dataview.current_row:
        text_area.buffer.cursor_position = (
            text_area.buffer.document.translate_row_col_to_index(
                dataview.current_row, 0
            )
        )
    get_app().invalidate()


async def new_day(loop):
    logger.debug('XXX new day XXX')
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
    logger.info(f'new_day currentYrWk: {dataview.currentYrWk}')
    return True


current_datetime = datetime.now().astimezone()


async def save_timers():
    dataview.save_timers()
    return True


def alerts():
    # alerts = []
    alert_hsh = {}
    now = datetime.now().astimezone()
    #            0            1         2          3         4       5
    # alerts: alert time, start time, commands, itemtype, summary, doc_id
    for alert in dataview.alerts:
        trigger_time = alert[0]
        start_time = alert[1]
        logger.debug(f"{alert[4] = }; {trigger_time = }; {now = }; {(trigger_time.replace(tzinfo=None) < now.replace(tzinfo=None)) = }")
        if start_time.date() == now.date():
            start = format_time(start_time)[1]
        else:
            start = format_datetime(start_time, short=True)[1]
        trigger = format_time(trigger_time)[1]
        command = ', '.join(alert[2])
        itemtype = alert[3]
        summary = alert[4]
        doc_id = alert[5]
        prefix = '✓' if trigger_time.replace(tzinfo=None) < now.replace(tzinfo=None) else '•'   # '⧖'
        alert_hsh.setdefault((alert[5], itemtype, summary), []).append(
            [prefix, trigger, start, command]
        )
    if alerts:
        output = []
        for key, values in alert_hsh.items():
            output.append(f'{key[1]} {key[2]}')
            for value in values:
                output.append(
                    f'  {value[0]} {value[1]:>7} ⭢  {value[2]:>7}:  {value[3]}'
                )
        output.append('')
        output.append('✓ already activated')
        output.append('• not yet activated')
        return '\n'.join(output)

    else:
        return 'There are no alerts for today.'


def get_row_col():
    row_number = text_area.document.cursor_position_row
    col_number = text_area.document.cursor_position_col
    return row_number, col_number


def restore_row_col(row_number, col_number):
    text_area.buffer.cursor_position = (
        text_area.buffer.document.translate_row_col_to_index(
            row_number, col_number
        )
    )


async def maybe_alerts(now):
    # global current_datetime
    row, col = get_row_col()
    set_text(dataview.show_active_view())
    #            0            1         2          3         4       5
    # alerts: alert time, start time, commands, itemtype, summary, doc_id
    restore_row_col(row, col)
    if dataview.alerts and not ('alerts' in settings and settings['alerts']):
        logger.warning('alerts have not been configured')
        return
    bad = []
    for alert in dataview.alerts:
        if alert[0].hour == now.hour and alert[0].minute == now.minute:
            # logger.debug(f"{alert[0].hour = }; {now.hour = }; {alert[0].minute = } {now.minute = }; {alert[0].second = }; {now.second = }")
            # if alert[0].second > 0 and now.second != alert[0].second:
            if now.second != alert[0].second:
                continue
            alertdt = alert[0]
            startdt = alert[1]
            if startdt > alertdt:
                when = f'in {duration_in_words(startdt-alertdt)}'
            elif startdt == alertdt:
                when = f'now'
            else:
                when = f'{duration_in_words(alertdt-startdt)} ago'
            start = format_datetime(startdt)[1]
            time = (
                format_time(startdt)[1]
                if startdt.date() == today.date()
                else format_datetime(startdt, short=True)[1]
            )
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
            commands = [
                settings['alerts'][x].format(
                    start=start,
                    time=time,
                    when=when,
                    now=format_time(now)[1],
                    summary=summary,
                    location=location,
                    description=description,
                )
                for x in command_list
                if x in settings['alerts']
            ]
            for command in commands:
                if command:
                    check_output(command)
            if len(commands) < len(command_list):
                bad.extend(
                    [x for x in command_list if x not in settings['alerts']]
                )

    if bad:
        logger.error(f'unrecognized alert commands: {bad}')


# async def event_handler():
def event_handler(e):
    global current_datetime
    now = datetime.now().astimezone()
    refresh_interval = settings.get(
        'refresh_interval', 6
    )   # seconds to wait between loops
    if now.second % refresh_interval >= 1:
        return
    # check for updates every interval minutes
    updates_interval = settings.get('updates_interval', 0)
    minutes = now.minute
    seconds = now.second

    try:
        current_today = dataview.now.strftime('%Y%m%d')
        asyncio.ensure_future(maybe_alerts(now))
        current_datetime = status_time(now)
        today = now.strftime('%Y%m%d')

        if updates_interval and minutes % updates_interval == 0 and seconds == 0:
            loop = asyncio.get_event_loop()
            asyncio.ensure_future(updates_loop(loop))

        if today != current_today:
            loop = asyncio.get_event_loop()
            asyncio.ensure_future(new_day(loop))

        asyncio.ensure_future(save_timers())
        if dataview.active_view == 'timers':
            row, col = get_row_col()
            set_text(dataview.show_active_view())
            restore_row_col(row, col)

    except asyncio.CancelledError:
        logger.info(f'Background task cancelled.')


def get_edit_mode():
    app = get_app()
    if get_app().layout.has_focus(edit_buffer):
        if app.editing_mode == EditingMode.VI:
            insert_mode = app.vi_state.input_mode in (
                InputMode.INSERT,
                InputMode.INSERT_MULTIPLE,
            )
            replace_mode = app.vi_state.input_mode == InputMode.REPLACE
            sel = edit_buffer.selection_state
            temp_navigation = app.vi_state.temporary_navigation_mode
            visual_line = sel is not None and sel.type == SelectionType.LINES
            visual_block = sel is not None and sel.type == SelectionType.BLOCK
            visual_char = (
                sel is not None and sel.type == SelectionType.CHARACTERS
            )
            mode = 'vi:'
            if insert_mode:
                mode += ' insert'
                application.output.set_cursor_shape(CursorShape.BEAM)
            elif replace_mode:
                mode += ' replace'
                application.output.set_cursor_shape(CursorShape.UNDERLINE)
            elif visual_block:
                mode += ' vblock'
                application.output.set_cursor_shape(CursorShape.BLOCK)
            elif visual_line:
                mode += ' vline'
                application.output.set_cursor_shape(CursorShape.BLOCK)
            elif visual_char:
                mode += 'vchar'
                application.output.set_cursor_shape(CursorShape.BLOCK)
            else:
                mode += ' normal'
                application.output.set_cursor_shape(CursorShape.BLOCK)
        else:
            mode = 'emacs'

        return ''.join(
            [
                mode,
                ' ',
                ('+' if edit_buffer_changed() else ''),
                (' '),
            ]
        )
    else:
        application.output.set_cursor_shape(CursorShape.BLOCK)

    return '        '


def get_statusbar_text():
    return [
        ('class:status', f' {format_statustime(datetime.now().astimezone())}'),
    ]


def get_statusbar_center_text():
    if dataview.is_editing:
        return [
            ('class:status', f' {get_edit_mode()}'),
        ]
    else:
        application.output.set_cursor_shape(CursorShape.BLOCK)
    if dataview.is_showing_query:
        return [
            ('class:status', f' {dataview.query_mode}'),
        ]
    if loglevel == 1:
        # show current row number and associated id in the status bar
        current_row = text_area.document.cursor_position_row
        current_id = dataview.row2id.get(current_row, '~')
        if isinstance(current_id, tuple):
            current_id = current_id[0]
        return [
            ('class:status', f'{current_row}: {current_id}'),
        ]

    return [
        ('class:status', 12 * ' '),
    ]


def get_statusbar_right_text():
    inbasket = INBASKET_CHAR if (glob(text_pattern)) else ''
    inactive_part = ('class:status', '')
    if dataview.timers:
        dataview.get_timers()
        inactive = dataview.inactive_str
        if inactive:
            inactive_part = (
                (type_colors['inactive'], inactive)
            )
    return [
        inactive_part,
        (
            'class:status',
            f'{dataview.active_view} {inbasket}{update_status.get_status()}',
        ),
    ]

def get_timer_text():
    if not dataview.timers:
        return []
    active = dataview.active_str
    if active:
        active_part = (
                (type_colors['running'], f' {active}') if f'r{ELECTRIC}' in active
            else (type_colors['paused'], f' {active}')
        )
        # inactive_part = ('class:status', f'{inactive}  ')
    else:
        active_part = ('class:status', '')
    return [active_part]

def openWithDefault(path):
    if ' ' in path:
        parts = qsplit(path)
        if parts:
            # wrapper to catch 'Exception Ignored' messages
            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                # the pid business is evidently needed to avoid waiting
                pid = subprocess.Popen(
                    parts,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                ).pid
                res = output.getvalue()
                if res:
                    logger.error(f"caught by contextlib:\n'{res}'")

    else:
        path = os.path.normpath(os.path.expanduser(path))
        sys_platform = platform.system()
        if platform.system() == 'Darwin':       # macOS
            subprocess.run(
                ('open', path),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        elif platform.system() == 'Windows':    # Windows
            os.startfile(path)
        else:                                   # linux
            subprocess.run(
                ('xdg-open', path),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    return


search_field = SearchToolbar(
    text_if_not_searching=[
        ('class:not-searching', "Press '/' to start searching.")
    ],
    ignore_case=True,
)

content = ''
etmlexer = ETMLexer()

# this is the main display area
text_area = TextArea(
    text='',
    read_only=True,
    scrollbar=True,
    search_field=search_field,
    focus_on_click=True,
    lexer=etmlexer,
)

konnected_area = TextArea(
    text='',
    read_only=True,
    scrollbar=True,
    search_field=search_field,
    focus_on_click=True,
    lexer=etmlexer,
)

# expansions will come from cfg.yaml
expansions = {}


class AtCompleter(Completer):
    # pat = re.compile(r'@[cgilntxz]\s?\S*')
    pat = re.compile(r'@[cgiklntxz]\s?[^@&]*')

    def __init__(self):
        super().__init__()
        self.continue_completion = True


    def get_completions(self, document, complete_event):
        cur_line = document.current_line_before_cursor
        matches = re.findall(AtCompleter.pat, cur_line)
        word = matches[-1] if matches else ''
        if self.continue_completion and word:
            word_len = len(word)
            word = word.rstrip()
            for completion in dataview.completions:
                if word.startswith('@x') and completion.find(word)>=0:
                    if completion == word:
                        replacement = expansions.get(word[3:], completion)
                        yield Completion(replacement, start_position=-word_len)
                    else:
                        yield Completion(completion, start_position=-word_len)

                elif word.startswith('@k') and completion.find(word)>=0:
                    if completion == word:
                        tmp = completion.split(' | ')
                        replacement = f"@k {tmp[1].strip()}"
                        yield Completion(replacement, start_position=-word_len)
                    else:
                        # yield Completion(completion, start_position=-word_len)
                        yield Completion(completion, start_position=-word_len)

                elif completion.startswith(word) and completion != word:
                    yield Completion(completion, start_position=-word_len)
        return

    def cancel(self):
        self.continue_completion = False


at_completer = FuzzyCompleter(AtCompleter())

result = ''


def process_input(buf):
    global result
    result = buf.document.text
    return True


def process_entry(buf):
    dataview.entry_content = buf.document.text


edit_bindings = KeyBindings()
ask_buffer = Buffer()
reply_buffer = Buffer(multiline=True)

entry_title_buffer = Buffer()
entry_prompt_buffer = Buffer(multiline=True)

choice_title_buffer = Buffer()
# choice_prompt_buffer = Buffer(multiline=True)

edit_buffer = Buffer(
    multiline=True,
    completer=at_completer,
    complete_while_typing=True,
    accept_handler=process_input,
)
entry_buffer = Buffer(multiline=False, accept_handler=process_entry)


reply_dimension = Dimension(min=1, weight=1)
prompt_dimension = Dimension(min=2, weight=3)
edit_dimension = Dimension(min=2, weight=3)
entry_dimension = Dimension(min=2, weight=2)

edit_window = Window(
    BufferControl(
        buffer=edit_buffer,
        focusable=True,
        focus_on_click=True,
        key_bindings=edit_bindings,
    ),
    height=edit_dimension,
    wrap_lines=True,
    style='class:edit',
)
entry_window = Window(
    BufferControl(
        buffer=entry_buffer,
        focusable=True,
        focus_on_click=True,
        key_bindings=edit_bindings,
    ),
    height=entry_dimension,
    wrap_lines=True,
    style='class:entry',
)
ask_window = Window(
    BufferControl(buffer=ask_buffer, focusable=False),
    height=1,
    style='class:ask',
)
entry_title_window = Window(
    BufferControl(buffer=entry_title_buffer, focusable=False),
    height=1,
    style='class:ask',
)
choice_title_window = Window(
    BufferControl(buffer=choice_title_buffer, focusable=False),
    height=1,
    style='class:ask',
)
reply_window = Window(
    BufferControl(buffer=reply_buffer, focusable=False),
    height=reply_dimension,
    wrap_lines=True,
    style='class:reply',
)
entry_prompt_window = Window(
    BufferControl(buffer=entry_prompt_buffer, focusable=False),
    height=reply_dimension,
    wrap_lines=True,
    style='class:edit',
)
# choice_prompt_window = Window(
#     BufferControl(buffer=choice_prompt_buffer, focusable=False), height=reply_dimension, wrap_lines=True, style='class:edit')

edit_area = HSplit(
    [
        ask_window,
        reply_window,
        HorizontalLine(),
        edit_window,
    ],
    style='class:edit',
)

entry_display_area = TextArea(
    text='',
    style='class:edit',
    read_only=True,
    scrollbar=True,
)


entry_area = HSplit(
    [
        entry_title_window,
        entry_display_area,
        HorizontalLine(),
        entry_window,
    ],
    style='class:edit',
)


choice_display_area = TextArea(
    text='',
    style='class:edit',
    read_only=True,
    scrollbar=True,
)

choice_area = HSplit(
    [
        choice_title_window,
        choice_display_area,
    ],
    style='class:edit',
)


details_area = TextArea(
    text='',
    style='class:details',
    read_only=True,
    scrollbar=True,
    focus_on_click=True,
    search_field=search_field,
)


busy_area = TextArea(
    text='',
    style='class:details',
    read_only=True,
    search_field=None,
)


width = shutil.get_terminal_size()[0] - 4


def get_busy_text():
    return get_busy_text_and_keys(0)


def get_busy_keys():
    return get_busy_text_and_keys(1)


def get_busy_text_and_keys(n):

    weekdays = {
        5: f'1→{WA[1]}',
        7: f'2→{WA[2]}',
        9: f'3→{WA[3]}',
        11: f'4→{WA[4]}',
        13: f'5→{WA[5]}',
        15: f'6→{WA[6]}',
        17: f'7→{WA[7]}',
    }
    busy_details = dataview.busy_details
    active_days = '  '.join(
        [v for k, v in weekdays.items() if k in busy_details.keys()]
    )
    no_busy_times = 'There are no days with busy periods this week.'.center(
        width, ' '
    )
    busy_times = wrap_text(
        f"""\
Press the number of a weekday,
    {weekdays[5]}, ..., {weekdays[17]}
to show the details of the busy periods from that day or press the ▼ (down) or ▲ (up) cursor keys to show the details of the next or previous day with busy periods.""",
        init_indent=0,
        subs_indent=0,
    )
    active_keys = f'{active_days}  ▼→next  ▲→previous'.center(width, ' ')

    if n == 0:   # text
        return busy_times if dataview.busy_details else ''
    else:   # n=1, keys
        return active_keys if dataview.busy_details else no_busy_times


busy_container = HSplit(
    [
        busy_area,
        Window(
            FormattedTextControl(get_busy_keys), style='class:status', height=1
        ),
    ],
    style='class:edit',
)

query_bindings = KeyBindings()


@query_bindings.add('enter', filter=is_querying)
def accept(buff):
    set_text('processing query ...')
    if query_window.text:
        text = query_window.text
        queries = settings.get('queries')
        if text == 'l':
            if queries:
                query_str = '\n  '.join(
                    [f'{k}: {v}' for k, v in queries.items()]
                )
            else:
                query_str = 'None listed'
            tmp = (
                """\
Stored queries are listed as <key>: <query> below.
Enter <key> at the prompt and press 'enter' to
replace <key> with <query>. Submit this query as
is or edit it first and then submit.

  """
                + query_str
            )

            show_message('query information', tmp)
            return False
        if text.strip() in ['quit', 'exit']:
            # quitting
            dataview.active_view = dataview.prior_view
            application.layout.focus(text_area)
            application.output.set_cursor_shape(CursorShape.BLOCK)
            set_text(dataview.show_active_view())
            return False
        parts = [x.strip() for x in text.split(' ')]
        if queries and parts[0] in queries:
            set_text('')
            text = queries[parts.pop(0)]
            m = re.search(r'{\d*}', text)
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
        loop.call_later(0.1, do_complex_query, text, loop)

    else:
        # quitting
        dataview.active_view = dataview.prior_view
        application.layout.focus(text_area)
        application.output.set_cursor_shape(CursorShape.BLOCK)
        set_text(dataview.show_active_view())

    return False


query = ETMQuery()

# query_buffer = Buffer(multiline=False, completer=None, complete_while_typing=False, accept_handler=accept)


query_window = TextArea(
    style='class:query',
    lexer=query.lexer,
    multiline=False,
    focusable=True,
    height=3,
    wrap_lines=True,
    prompt='query: ',
)

query_window.accept_handler = accept

query_area = HSplit(
    [
        ask_window,
        query_window,
    ],
    style='class:edit',
)


def do_complex_query(text, loop):
    text, *updt = [x.strip() for x in text.split(' | ')]
    updt = f' | {updt[0]}' if updt else ''
    if text.startswith('a '):
        text = text[2:]
        dataview.use_archive()
        item.use_archive()
    else:
        dataview.use_items()
        item.use_items()

    if len(text) > 1 and text[1] == ' ' and text[0] in ['s', 'u', 'm', 'c', 'v']:
        grpby, filters, needs = report.get_grpby_and_filters(text)
        ok, items = query.do_query(filters.get('query') + updt)
        if ok:
            items = report.apply_dates_filter(items, grpby, filters)
            dataview.set_query(text, grpby, items, needs)
            application.layout.focus(text_area)
            set_text(dataview.show_active_view())
        else:
            set_text(items)
    else:
        ok, items = query.do_query(text + updt)
        if ok:
            dataview.set_query(f'{text + updt}', {}, items)
            application.layout.focus(text_area)
            set_text(dataview.show_active_view())
        else:
            set_text(items)


def do_show_processing(loop):
    set_text('processing query ...')
    application.layout.focus(text_area)
    get_app().invalidate()


edit_container = HSplit(
    [
        edit_area,
    ]
)

entry_container = HSplit(
    [
        entry_area,
    ]
)

choice_container = HSplit(
    [
        choice_area,
    ]
)


def default_buffer_changed(_):
    """ """
    dataview.control_z_active = False
    item.text_changed(edit_buffer.text, edit_buffer.cursor_position)


def default_cursor_position_changed(_):
    """ """
    item.cursor_changed(edit_buffer.cursor_position)
    set_askreply('_')


# This is slick - add a call to default_buffer_changed
edit_buffer.on_text_changed += default_buffer_changed
edit_buffer.on_cursor_position_changed += default_cursor_position_changed

status_area = VSplit(
    [
        Window(FormattedTextControl(get_statusbar_text), style='class:status'),
        Window(
            FormattedTextControl(get_statusbar_center_text),
            style='class:status',
            width=12,
            align=WindowAlign.CENTER,
        ),
        Window(
            FormattedTextControl(get_statusbar_right_text),
            style='class:status',
            width=20,
            align=WindowAlign.RIGHT,
        ),
    ],
    height=1,
)

timer_area = VSplit(
    [
        Window(FormattedTextControl(get_timer_text), style='class:status')
    ],
    height=1,
)


body = HSplit(
    [
        text_area,  # main content
        ConditionalContainer(
            content=HorizontalLine(), filter=is_showing_konnections
        ),
        ConditionalContainer(
            content=konnected_area, filter=is_showing_konnected
        ),
        status_area,  # toolbar
        ConditionalContainer(
            content=timer_area, filter=timer_active
        ),
        ConditionalContainer(
            content=details_area, filter=is_showing_details & is_not_busy_view
        ),
        ConditionalContainer(content=busy_container, filter=is_busy_view),
        ConditionalContainer(content=query_area, filter=is_querying),
        ConditionalContainer(content=edit_container, filter=is_editing),
        ConditionalContainer(content=choice_area, filter=is_showing_choice),
        ConditionalContainer(content=entry_container, filter=is_showing_entry),
        ConditionalContainer(content=search_field, filter=is_not_editing),
        # search_field,
    ]
)

item_not_selected = False


@bindings.add('S', filter=is_viewing_or_details & is_items_table)
def do_schedule_new(*event):
    doc_id, instance, job = dataview.get_row_details(
        text_area.document.cursor_position_row
    )

    if not doc_id:
        return

    hsh = DBITEM.get(doc_id=doc_id)

    title = 'Schedule New Instance'
    text = f"""\
selected: {hsh['itemtype']} {hsh['summary']}

To schedule an additional datetime for this reminder enter the new datetime """

    get_entry(title, text, '', event)

    def coroutine():
        new_datetime = dataview.entry_content.strip()

        if new_datetime:
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
        else:
            show_message(title, 'cancelled')

    dataview.got_entry = coroutine


@bindings.add('R', filter=is_viewing_or_details & is_items_table)
def do_reschedule(*event):
    doc_id, instance, job = dataview.get_row_details(
        text_area.document.cursor_position_row
    )

    if not doc_id:
        return

    hsh = DBITEM.get(doc_id=doc_id)
    if instance is None and 's' in hsh:
        instance = hsh['s']

    is_date = isinstance(instance, date) and not isinstance(instance, datetime)

    date_required = is_date or (instance.hour == 0 and instance.minute == 0)

    instance = instance.date() if date_required and not is_date else instance
    new = 'new date' if date_required else 'new datetime'

    title = 'Reschedule Instance'
    text = f"""\
selected: {hsh['itemtype']} {hsh['summary']}
instance: {format_datetime(instance)[1]}

To reschedule enter the {new} """

    get_entry(title, text, '', event)

    def coroutine():
        new_datetime = dataview.entry_content.strip()

        if new_datetime:
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

        else:
            show_message(title, 'cancelled')

    dataview.got_entry = coroutine


@bindings.add('D', filter=is_viewing_or_details & is_item_view)
def do_maybe_delete(*event):
    doc_id, instance, job = dataview.get_row_details(
        text_area.document.cursor_position_row
    )

    if not doc_id:
        return

    hsh = DBITEM.get(doc_id=doc_id)
    has_timer = doc_id in dataview.timers
    timer_warning = ' and\nits associated timer' if has_timer else ''

    if not instance:
        # not repeating
        title = 'Delete'

        options = [
            '<return>: yes, delete this reminder',
            '<escape>: no, cancel',
        ]

        text = f"""\
{hsh['itemtype']} {hsh['summary']}

Are you sure that you want to delete this reminder?
"""
        get_choice(title, text, options)

        def coroutine():
            keypress = dataview.details_key_press
            done = keypress in ['escape', Keys.ControlM]
            if keypress == Keys.ControlM:
                if has_timer:
                    dataview.timer_clear(doc_id)
                item.delete_item(doc_id)
                if doc_id in dataview.itemcache:
                    del dataview.itemcache[doc_id]
                loop = asyncio.get_event_loop()
                loop.call_later(0, data_changed, loop)

            return done

        dataview.got_choice = coroutine

        return

    if instance:
        # repeating
        title = 'Delete'

        options = [
            '  <1>: just this instance',
            '  <2>: this and all subsequent instances',
            '  <3>: the reminder itself',
            '<escape>: delete nothing, cancel',
        ]

        text = f"""\
{hsh['itemtype']} {hsh['summary']}
    {format_datetime(instance)[1]}

This is one instance of a repeating item. What do you want to delete?
"""
        get_choice(title, text, options)

        def coroutine():
            keypress = dataview.details_key_press

            done = keypress in ['escape', '1', '2', '3']
            if done:
                changed = item.delete_instances(doc_id, instance, keypress)
                if changed:
                    if doc_id in dataview.itemcache:
                        del dataview.itemcache[doc_id]
                    # application.layout.focus(text_area)
                    # set_text(dataview.show_active_view())
                    loop = asyncio.get_event_loop()
                    loop.call_later(0, data_changed, loop)

                return done

        dataview.got_choice = coroutine


starting_buffer_text = ''


@bindings.add('N', filter=is_viewing & is_items_table & is_not_searching)
@bindings.add('+', filter=is_viewing & is_items_table)
def edit_new(*event):
    global item
    global starting_buffer_text
    app = get_app()
    app.editing_mode = (
        EditingMode.VI if settings['vi_mode'] else EditingMode.EMACS
    )
    starting_buffer_text = ''
    if dataview.is_showing_details:
        application.layout.focus(text_area)
        dataview.hide_details()
    # to restore the current cursor row after completed
    dataview.current_row = text_area.document.cursor_position_row
    dataview.is_editing = True
    dataview.control_z_active = False
    item.new_item()
    edit_buffer.text = item.entry
    default_buffer_changed(event)
    default_cursor_position_changed(event)
    application.layout.focus(edit_buffer)

def ordinal_day_and_weekday(d: datetime)->str:
    md, wd = d.split(', ')
    return f"{model.ordinal(int(md))}, {wd}"

@bindings.add('J', filter=is_viewing & is_items_table)
def edit_or_add_journal(*event):
    global item
    global starting_buffer_text
    now = datetime.now()
    app = get_app()
    app.editing_mode = (
        EditingMode.VI if settings['vi_mode'] else EditingMode.EMACS
    )

    if dataview.is_showing_details:
        application.layout.focus(text_area)
        dataview.hide_details()

    # to restore the current cursor row after completed
    dataview.current_row = text_area.document.cursor_position_row
    dataview.is_editing = True
    dataview.control_z_active = False
    # summary_fmt = settings['journal_summary']

    journal_name = settings.get('journal_name')
    doc_id, entry = dataview.get_details(
        text_area.document.cursor_position_row, True
    )
    # summary = model.format_date(datetime.today(), separator='-', omit_zeros=False)[1]
    summary = now.strftime("%Y-%m-%d")
    relevant = None
    for it in ETMDB:
        if it.get('itemtype') != '%':
            continue
        if it.get('i') != journal_name:
            continue
        if it.get('summary') == summary:
            relevant = it
            break
    if relevant:
        doc_id = relevant.doc_id
        entry = item_details(relevant, True)
        item.edit_item(doc_id, entry)
        edit_buffer.text = item.entry
        starting_buffer_text = item.entry
        default_buffer_changed(event)
        default_cursor_position_changed(event)
        application.layout.focus(edit_buffer)
    else:
        starting_buffer_text = ""
        template = f"""\
% {summary}
@i {journal_name}
@d {now.strftime('%A, %B %-d, %Y')}\
"""
        item.new_item()
        default_buffer_changed(event)
        default_cursor_position_changed(event)
        application.layout.focus(edit_buffer)
        edit_buffer.text = template
    # cursor_right below will move over just to the end of '\n   - '
    edit_buffer.text = f"{edit_buffer.text}\n\n* {now.strftime('%H:%M')}\n  - "
    starting_buffer_text = edit_buffer.text
    lines_in_buffer = len(edit_buffer.text.split('\n'))
    position = edit_buffer.document.get_end_of_document_position()
    for i in range(lines_in_buffer):
        edit_buffer.cursor_down()
    for i in range(4):
        edit_buffer.cursor_right()

    # edit_buffer.cursor_position = position



@bindings.add('E', filter=is_viewing_or_details & is_item_view)
def edit_existing(*event):
    global item
    global starting_buffer_text
    global text_area
    app = get_app()
    app.editing_mode = (
        EditingMode.VI if settings['vi_mode'] else EditingMode.EMACS
    )
    if dataview.is_showing_details:
        application.layout.focus(text_area)
        dataview.hide_details()
    dataview.is_editing = True
    doc_id, entry = dataview.get_details(
        text_area.document.cursor_position_row, True
    )
    item.edit_item(doc_id, entry)
    edit_buffer.text = item.entry
    starting_buffer_text = item.entry
    default_buffer_changed(event)
    default_cursor_position_changed(event)
    application.layout.focus(edit_buffer)


def edit_buffer_changed():
    return edit_buffer.text != starting_buffer_text


def entry_buffer_changed(_):
    changed = entry_buffer.text != starting_buffer_text
    if changed:
        dataview.entry_content = entry_buffer.text
    return changed


entry_buffer.on_text_changed += entry_buffer_changed


@bindings.add('T', filter=is_viewing_or_details & is_item_view)
def next_timer_state(*event):
    row = text_area.document.cursor_position_row
    res = dataview.get_row_details(row)   # item_id, instance, job_id
    doc_id = res[0]
    if not doc_id:
        return
    dataview.next_timer_state(doc_id)
    row = text_area.document.cursor_position_row
    dataview.refreshRelevant()
    set_text(dataview.show_active_view())
    text_area.buffer.cursor_position = (
        text_area.buffer.document.translate_row_col_to_index(row, 0)
    )


@bindings.add('T', 'D', filter=is_viewing_or_details & is_item_view)
def maybe_delete_timer(*event):
    row = text_area.document.cursor_position_row
    res = dataview.get_row_details(row)   # item_id, instance, job_id
    doc_id = res[0]
    if not doc_id or doc_id not in dataview.timers:
        return
    hsh = DBITEM.get(doc_id=doc_id)
    state2fmt = {
        'i': 'inactive',
        'r': 'running',
        'p': 'paused',
    }

    state, start, elapsed = dataview.timers[doc_id]
    if state == 'r':
        now = datetime.now().astimezone()
        elapsed += now - start
        start = now
    timer = f"\ntimer:\n  status: {state2fmt[state]}\n  last change: {format_datetime(start, short=True)[1]}\n  elapsed time: {format_duration(elapsed, short=True)}\n\nWARNING: The timer's data will be lost.\nAre you sure you want to delete this timer?"

    title = 'Delete Timer'
    text = f"""\
selected: {hsh['itemtype']} {hsh['summary']}{timer}
"""

    options = [
        '  <return>: yes, delete the timer',
        '  <escape>: no, do not delete the timer',
    ]
    get_choice(title, text, options)

    def coroutine():
        keypress = dataview.details_key_press
        done = keypress in ['escape', Keys.ControlM]
        if keypress == Keys.ControlM:
            dataview.timer_clear(doc_id)
            dataview.refreshRelevant()
            set_text(dataview.show_active_view())
            get_app().invalidate()

        return done

    dataview.got_choice = coroutine


@bindings.add('T', 'T', filter=is_viewing_or_details & is_item_view)
def toggle_active_timer(*event):
    dataview.toggle_active_timer(text_area.document.cursor_position_row)
    row = text_area.document.cursor_position_row
    dataview.refreshRelevant()
    set_text(dataview.show_active_view())
    text_area.buffer.cursor_position = (
        text_area.buffer.document.translate_row_col_to_index(row, 0)
    )


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
    res = dataview.get_row_details(row)   # item_id, instance, job_id
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
        show_message('Update last-modified', 'Update last-modified failed')


@bindings.add('F', filter=is_viewing_or_details & is_item_view)
def do_finish(*event):
    """
    If itemtype is '<', there is at least one pastdue instance. The completion will be for the oldest, if more than one with a warning that others are past due and to finish one other than the oldest to cancel and select the desired instance. Otherwise, the completion will apply to the selection.

    For the completion coroutine
    If the selection corresponds to a
    - non repeating item: add an @f entry
    - repeating [in @+ or @r instances perhaps including @s]
        - if an @+ element: delete it
        - elif == @s
            - if there is a next instance in @r, set @s = next
            - elif there is an instance in @+, set @s = oldest
            - else add an @f entry
        - else add it to @-

    """
    row = text_area.document.cursor_position_row
    doc_id, instance, job = dataview.get_row_details(row)
    if not doc_id:
        return

    hsh = DBITEM.get(doc_id=doc_id)
    msg = ''
    if hsh['itemtype'] != '-' or 'f' in hsh:
        show_message('Finish', 'Only an unfinished task can be finished.')
        return

    # has_timer = doc_id in dataview.timers
    # timer_warning = " and\nits associated timer" if has_timer else ""
    repeating = 's' in hsh and ('r' in hsh or '+' in hsh)
    if repeating:
        due = hsh['s']
        at_plus = hsh.get('+', [])
        if at_plus:
            at_plus.sort()
            due = min(due, model.date_to_datetime(at_plus[0]))
    else:
        due = hsh.get('s', None)

    between = []

    title = 'Finish'

    now = format_datetime(datetime.now().astimezone(), short=True)[1]
    default = now

    if job:
        # only a completion date needed - either undated or finishing the oldest instance
        need = 1
        between = [hsh.get('s', None)]
        # due = hsh.get('s', "")
        start = f'\nDue: {format_datetime(due)[1]}' if due else ''

        text = f"""\
{hsh['itemtype']} {hsh['summary']}
    {job}{start}

If necessary, edit the completion datetime for this task\
"""
        default = now

    elif instance and instance == model.date_to_datetime(due):
        # the oldest instance is selected
        need = 1
        between = [due]
        entry = is_not_yearly_view
        # due = hsh.get('s', "")
        start = f'\n    {format_datetime(due)[1]}' if due else ''

        text = f"""\
{hsh['itemtype']} {hsh['summary']}{start}

The default entered below is to use the current moment as the "completion datetime". Edit this entry if you wish\
"""

    elif instance:
        # either the selected instance or the oldest
        need = 2
        between = [due, instance]
        # if instance != hsh['s']:
        values = [
            f'{format_datetime(due)[1]} (oldest)',
            f'{format_datetime(instance)[1]} (selected)',
        ]

        values_list = []
        count = -1
        for x in values:
            count += 1
            values_list.append(f'    {count}: {x}')

        values_str = '\n'.join(values_list)

        text = f"""\
{hsh['itemtype']} {hsh['summary']}

At least one unfinished instance of this task is older than the one selected:
{values_str}
The default entered below is to use the current moment and the number of the selected instance. Edit this "completion datetime : instance number" entry if you wish\
        """
        default = f'{now} : 1'

    elif repeating:
        # must be selected from today's pastdue or beginby
        already_done = [x.end for x in hsh.get('h', [])]
        between = [
            x[0]
            for x in model.item_instances(
                hsh,
                model.date_to_datetime(due),
                datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0
                ),
            )
            if x[0] not in already_done
        ]
        if between:
            # show_message('Finish', "There is nothing to complete.")
            need = 2
            values_list = []
            # values.append( (0, format_datetime(between[0][0])[1]) )
            count = -1
            for x in between:
                count += 1
                values_list.append(f'   {count}: {format_datetime(x)[1]}')
                # values_list.append(f"   {format_datetime(x)[1]}")

            values_str = '\n'.join(values_list)

            text = f"""\
{hsh['itemtype']} {hsh['summary']}

More than one instance of this task is past due:
{values_str}
The default entered below is to use the current moment and the number of the oldest instance. Edit this "completion datetime : instance number" entry if you wish\
            """

            default = f'{now} : 0'
            due = ''
        else:
            # beginby

            need = 1
            between = [hsh.get('s', None)]
            entry = 'now'
            # due = hsh.get('s', "")
            start = (
                f"\nDue: {format_datetime(hsh['s'])[1]}" if 's' in hsh else ''
            )

            text = f"""\
{hsh['itemtype']} {hsh['summary']}{start}

There are no pastdue instances for this task.  If necessary, edit the completion datetime for this task below\
        """

    else:
        need = 1
        between = [due]
        entry = 'now'
        # due = hsh.get('s', "")
        start = f'\nDue: {format_datetime(due)[1]}' if due in hsh else ''

        text = f"""\
{hsh['itemtype']} {hsh['summary']}{start}

The default entered below is to use the current moment as the "completion datetime". Edit this entry if you wish """

    get_entry(title, text, default, event)

    ###################
    #### coroutine ####
    ###################
    def coroutine(need=need):
        global hsh

        done_str = dataview.entry_content

        if not done_str:
            show_message('Finish', 'Cancelled')
            close_entry(*event)
            return None

        done_parts = [x.strip() for x in done_str.split(' : ')]

        msg = ''
        num_parts = len(done_parts)
        if num_parts != need:
            ok = False
            msg = f'Cancelled, the entry, {done_str}, does not have the required format'

        elif num_parts == 2:
            num = int(done_parts[1])
            # only return due for instance other than the oldest
            # due = between[num] if num else ""
            if num in range(len(between)):
                due = between[num]
            else:
                msg = f"Cancelled, '{num}' is not in [{', '.join([str(x) for x in range(len(between))])}]"
            ok, res, z = parse_datetime(done_parts[0])
            if ok:
                done = res
            else:
                msg = f"Cancelled, '{done_parts[0]}' is not a valid datetime"

        elif num_parts == 1:
            ok, res, z = parse_datetime(done_str)
            if ok:
                done = res
            else:
                msg = f"Cancelled, '{done_str}' is not a valid datetime"
            due = between[0] if between[0] else done

        if msg:
            show_message('Finish', msg)
            return
        done = model.date_to_datetime(done)
        due = model.date_to_datetime(due)

        changed = item.finish_item(doc_id, job, done, due)

        if not msg and changed:
            if doc_id in dataview.itemcache:
                del dataview.itemcache[doc_id]
            application.layout.focus(text_area)
            set_text(dataview.show_active_view())
            loop = asyncio.get_event_loop()
            loop.call_later(0, data_changed, loop)
        else:
            show_message('finish', f"Cancelled, '{done_str}' is invalid.")
            return

    dataview.got_entry = coroutine


@bindings.add(
    'C', filter=is_viewing_or_details & is_item_view & is_items_table
)
def edit_copy(*event):
    global item
    global starting_buffer_text
    app = get_app()
    app.editing_mode = (
        EditingMode.VI if settings['vi_mode'] else EditingMode.EMACS
    )
    if dataview.is_showing_details:
        application.layout.focus(text_area)
        dataview.hide_details()
    dataview.is_editing = True
    doc_id, entry = dataview.get_details(
        text_area.document.cursor_position_row, True
    )
    item.edit_copy(doc_id, entry)
    edit_buffer.text = item.entry
    starting_buffer_text = item.entry
    default_buffer_changed(event)
    default_cursor_position_changed(event)
    application.layout.focus(edit_buffer)


@bindings.add('g', filter=is_viewing & is_not_editing)
def do_goto(*event):
    row = text_area.document.cursor_position_row
    if not row:
        logger.error(
            f'do_goto failed to return a row for cursor position {text_area.document.cursor_position_row}'
        )
        return
    res = dataview.get_row_details(row)   # item_id, instance, job_id
    if not res:
        return
    doc_id = res[0]
    # we have a row and a doc_id
    ok, goto = dataview.get_goto(row)
    if ok and goto:
        res = openWithDefault(goto)
        if res:
            show_message('goto', res, 8)
    else:
        show_message('goto', goto, 8)


@bindings.add('c-g', filter=is_editing)
def check_goto(*event):
    ok, goto = item.check_goto_link()
    if ok:
        res = openWithDefault(goto)
        if res:
            show_message('goto', res, 8)
    else:
        show_message('goto', goto, 8)


@bindings.add('c-r', filter=is_viewing_or_details & is_item_view)
def not_editing_reps(*event):
    # doc_id, instance, job = dataview.get_row_details(text_area.document.cursor_position_row)
    row = text_area.document.cursor_position_row
    res = dataview.get_repetitions(row)
    if not res:
        return
    showing, reps = res
    show_message(showing, reps, 24)


@bindings.add('c-h', filter=is_viewing_or_details & is_item_view)
def not_editing_history(*event):
    row = text_area.document.cursor_position_row
    res = dataview.get_history(row)
    if not res:
        return
    showing, reps = res
    show_message(showing, reps, 24)


@bindings.add('c-r', filter=is_editing)
def is_editing_reps(*event):
    res = item.get_repetitions()
    if not res:
        return
    showing, reps = res
    show_message(showing, reps, 24)


@bindings.add(
    'P', filter=is_viewing_or_details & is_item_view & is_items_table
)
def toggle_pinned(*event):
    row = text_area.document.cursor_position_row
    res = dataview.toggle_pinned(row)
    dataview.refreshRelevant()
    set_text(dataview.show_active_view())
    text_area.buffer.cursor_position = (
        text_area.buffer.document.translate_row_col_to_index(row, 0)
    )


@bindings.add('f5')
def do_import_file(*event):

    # # begin not yet implemented block
    # func  = inspect.currentframe().f_code.co_name
    # show_work_in_progress(func)
    # return
    # # end not yet implemented block

    possible_imports = glob(text_pattern)
    possible_imports.sort()
    count = 0
    options = ["    <0>: lorem"]
    values = {}
    for x in possible_imports:
        count += 1
        options.append(f"    <{count}>: {os.path.relpath(x, start=os.path.expanduser(etmhome))}")
        values[str(count)] = x
    options.append("  <escape>: cancel")
    # values_str = '\n'.join(values)

    # default = (
    #     inbasket if os.path.exists(os.path.expanduser(inbasket)) else etmhome
    # )
    msg = ''

    title = 'Import File'

    text = f"""\
It is possible to import data from a collection of illustrative, 'lorem', reminders or from from a file in the etm home directory, {etmhome}, with the extension '.text'.  (This file will subsequently be deleted). The current options:
"""

    get_choice(title, text, options)

    def coroutine():
        keypress = dataview.details_key_press
        done = keypress in (['escape', '0'] + [x for x in values.keys()])
        if done:
            if keypress == '0':
                ok, msg = import_file('lorem')
                if ok:
                    dataview.refreshRelevant()
                    dataview.refreshAgenda()
                    if dataview.mk_current:
                        dataview.refreshCurrent()
                    dataview.refreshKonnections()
                    loop = asyncio.get_event_loop()
                    loop.call_later(0, data_changed, loop)
                show_message('Import File', msg)

            elif keypress in values.keys():
                filepath = values[keypress]
                set_text(dataview.show_active_view())
                ok, msg = import_file(filepath)
                if ok:
                    # file_base, file_extension = os.path.splitext(filepath)
                    # new_filepath = file_base + '.txt'
                    # os.rename(filepath, new_filepath)
                    os.remove(filepath)
                    msg += f'\n and removed {filepath}'
                    dataview.refreshRelevant()
                    dataview.refreshAgenda()
                    if dataview.mk_current:
                        dataview.refreshCurrent()
                    dataview.refreshKonnections()
                    loop = asyncio.get_event_loop()
                    loop.call_later(0, data_changed, loop)
                show_message('Import File', msg)
            else:
                show_message('Import File', 'cancelled - nothing submitted')
            return done

    dataview.got_choice = coroutine


@bindings.add('c-t', 'c-t', filter=is_viewing & is_item_view)
def do_whatever(*event):
    """
    For testing whatever
    """
    dataview.handle_backups()
    set_text(dataview.show_active_view())


@bindings.add('v', filter=is_viewing)
def refresh_views(*event):
    """
    Refresh all views to fit current window dimensions and redraw the active view
    """
    dataview.refreshCache()
    set_text(dataview.show_active_view())
    return True


@bindings.add('c-t', filter=is_viewing & is_item_view, eager=True)
def quick_timer(*event):

    title = 'Quick Timer'
    text = 'Enter the summary for the quick timer '
    default = format_datetime(datetime.now(), short=True)[1]

    get_entry(title, text, default, event)

    def coroutine():
        summary = dataview.entry_content
        if summary:
            item_hsh = {
                'itemtype': '!',
                'summary': summary,
                'created': datetime.now().astimezone(ZoneInfo('UTC')),
            }

            doc_id = ETMDB.insert(item_hsh)
            if doc_id:
                dataview.next_timer_state(doc_id)
                dataview.next_timer_state(doc_id)
                dataview.refreshRelevant()
                dataview.refreshAgenda()
                dataview.refreshCurrent()
                dataview.refreshKonnections()
                loop = asyncio.get_event_loop()
                loop.call_later(0, data_changed, loop)

    dataview.got_entry = coroutine


@bindings.add('c-t', filter=is_viewing & is_item_view)
def quick_capture(*event):
    """
    Like quick_timer but does not prompt for summary modification
    """
    now = datetime.now().astimezone()
    item_hsh = {
        'itemtype': '!',
        'summary': format_datetime(now, short=True)[1],
        'created': now.astimezone(ZoneInfo('UTC')),
    }
    doc_id = ETMDB.insert(item_hsh)
    if doc_id:
        dataview.next_timer_state(doc_id)
        dataview.next_timer_state(doc_id)
        dataview.refreshRelevant()
        dataview.refreshAgenda()
        dataview.refreshCurrent()
        dataview.refreshKonnections()
        loop = asyncio.get_event_loop()
        loop.call_later(0, data_changed, loop)


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
    if dataview.query_mode == 'items table':
        set_text(dataview.show_active_view())
        loop.call_later(0, data_changed, loop)
    else:
        set_text(
            'The reminder has been moved to items table.\nRun the previous query again to update the display'
        )
        text = f'a { dataview.query_text }'
        dataview.use_items()
        item.use_items()
        loop.call_later(0, data_changed, loop)
        loop.call_later(0.1, do_complex_query, text, loop)
    return


@bindings.add('c-q', filter=is_not_editing)
def exit(*event):
    application.exit()


@query_bindings.add('c-c', filter=is_querying)
def copy_details(*event):
    selection = query_window.buffer.copy_selection().text
    if selection:
        pyperclip.copy(selection)
        show_message('copy', 'selection copied to system clipboard', 2)
    else:
        pyperclip.copy(query_window.text)
        show_message('copy', 'query copied to system clipboard', 2)

@bindings.add('c-c', filter=is_viewing)
def copy_active_view(*event):
    selection = text_area.buffer.copy_selection().text
    if selection:
        pyperclip.copy(selection)
        show_message('copy', 'selection copied to system clipboard', 2)
    else:
        pyperclip.copy(text_area.text)
        show_message('copy', 'view copied to system clipboard', 2)


@bindings.add('c-c', filter=is_editing)
def copy_details(*event):
    selection = edit_buffer.copy_selection().text
    if selection:
        pyperclip.copy(selection)
        show_message('copy', 'selection copied to system clipboard', 2)
    else:
        pyperclip.copy(edit_buffer.text)
        show_message('copy', 'entry text copied to system clipboard', 2)

@bindings.add('c-c', filter=is_details)
def copy_details(*event):
    selection = details_area.buffer.copy_selection().text
    if selection:
        pyperclip.copy(selection)
        show_message('copy', 'selection copied to system clipboard', 2)
    else:
        # get_app().clipboard.set_data(data)
        details = details_area.text
        # details = dataview.get_details(text_area.document.cursor_position_row)[1]
        pyperclip.copy(details)
        show_message('copy', 'details copied to system clipboard', 2)


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
        text_area.buffer.cursor_position = (
            text_area.buffer.document.translate_row_col_to_index(
                dataview.busy_row - 1, 0
            )
        )
    else:
        busy_area.text = get_busy_text()


@bindings.add('c', filter=is_viewing)
def completed_view(*event):
    set_view('c')


@bindings.add('q', filter=is_viewing & is_not_showing_details)
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
    # show_message('History View', 'Reverse sorted (most recent first) using the last modified datetime if modified or the created datetime otherwise.')


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
def effort_view(*event):
    set_view('e')


@bindings.add('j', filter=is_viewing)
def journal_view(*event):
    set_view('j')


@bindings.add('r', filter=is_viewing)
def review_view(*event):
    set_view('r')



@bindings.add('k', filter=is_viewing & is_not_showing_konnected & is_not_editing)
def konnected_view(*event):
    doc_id, entry = dataview.get_details(
        text_area.document.cursor_position_row, True
    )
    # id2row = {id: row for row, id in dataview.konnections_row2id.items()}
    konnected_row = dataview.konnected_id2row.get(doc_id, None)
    set_view('k')
    if konnected_row:
        text_area.buffer.cursor_position = (
            text_area.buffer.document.translate_row_col_to_index(
                konnected_row, 0)
            )

@bindings.add('k', filter=is_showing_konnected & is_not_showing_konnections & is_not_editing)
def get_konnections(*event):
    if not dataview.active_view == 'konnected':
        return

    selected_id = dataview.get_details(text_area.document.cursor_position_row)[
        0
    ]
    tree, row2id = dataview.show_konnections(selected_id)
    dataview.konnections_row2id = row2id
    if tree:
        konnected_area.text = tree
    else:
        konnected_area.text = f"""
        Problem showing konnections for {selected_id}
        """
    application.layout.focus(konnected_area)
    dataview.is_showing_konnections = True


@bindings.add('k', filter=is_showing_konnected & is_showing_konnections)
def hide_konnections(*event):
    doc_id, entry = dataview.get_details(
        konnected_area.document.cursor_position_row, True
    )
    konnected_row = dataview.konnected_id2row.get(doc_id, None)
    application.layout.focus(text_area)
    if konnected_row:
        text_area.buffer.cursor_position = (
            text_area.buffer.document.translate_row_col_to_index(
                konnected_row, 0)
            )
    konnected_area.text = ""
    dataview.is_showing_konnections = False

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
    r = 5 + 2 * (d - 1)
    if not r in busy_details.keys():
        return
    text_area.buffer.cursor_position = (
        text_area.buffer.document.translate_row_col_to_index(r - 1, 0)
    )
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


@bindings.add(' ', filter=is_busy_view & is_viewing & is_not_querying)
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
    text_area.buffer.cursor_position = (
        text_area.buffer.document.translate_row_col_to_index(next_row - 1, 0)
    )
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
    text_area.buffer.cursor_position = (
        text_area.buffer.document.translate_row_col_to_index(next_row - 1, 0)
    )
    busy_area.text = busy_details.get(next_row, '')
    dataview.busy_row = next_row


@bindings.add(
    'down', filter=is_not_busy_view & is_not_yearly_view & is_viewing
)
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
        next_id = (
            row2id[next_row][0]
            if isinstance(row2id[next_row], tuple)
            else row2id[next_row]
        )
    else:
        next_id = '?'
    text_area.buffer.cursor_position = (
        text_area.buffer.document.translate_row_col_to_index(next_row, 0)
    )
    if is_showing_details():
        tmp = dataview.get_details(text_area.document.cursor_position_row)[1]
        if tmp:
            dataview.show_details()
            details_area.text = tmp.rstrip()
            application.layout.focus(text_area)


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
        next_id = (
            row2id[next_row][0]
            if isinstance(row2id[next_row], tuple)
            else row2id[next_row]
        )
    else:
        next_id = '?'
    text_area.buffer.cursor_position = (
        text_area.buffer.document.translate_row_col_to_index(next_row, 0)
    )
    if is_showing_details():
        tmp = dataview.get_details(text_area.document.cursor_position_row)[1]
        if tmp:
            dataview.show_details()
            details_area.text = tmp.rstrip()
            application.layout.focus(text_area)


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
    text_area.buffer.cursor_position = (
        text_area.buffer.document.translate_row_col_to_index(nxt, 0)
    )


@bindings.add('Z', filter=is_viewing)
def toggle_goto_id(*event):
    """
    If goto id is set, remove it. Else set it to the id of the selected item.
    """
    dataview.goto_id = (
        None
        if dataview.goto_id
        else dataview.get_details(text_area.document.cursor_position_row)[0]
    )


@bindings.add('right', filter=is_agenda_view & is_viewing)
def nextweek(*event):
    dataview.nextYrWk()
    dataview.busy_row = 0
    busy_details = dataview.busy_details
    busy_area.text = ''   # get_busy_text()
    set_text(dataview.show_active_view())


@bindings.add('left', filter=is_agenda_view & is_viewing)
def prevweek(*event):
    dataview.prevYrWk()
    dataview.busy_row = 0
    busy_details = dataview.busy_details
    busy_area.text = ''   # get_busy_text()
    set_text(dataview.show_active_view())


@bindings.add('home', filter=is_agenda_view & is_viewing)
@bindings.add('space', filter=is_agenda_view & is_viewing)
def currweek(*event):
    dataview.currYrWk()
    dataview.busy_row = 0
    busy_details = dataview.busy_details
    busy_area.text = ''
    set_text(dataview.show_active_view())


@bindings.add('right', filter=is_yearly_view & is_viewing)
def nextcal(*event):
    dataview.nextcal()
    set_text(dataview.show_active_view())


@bindings.add('left', filter=is_yearly_view & is_viewing)
def prevcal(*event):
    dataview.prevcal()
    set_text(dataview.show_active_view())


@bindings.add('home', filter=is_yearly_view & is_viewing)
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


@bindings.add('home', filter=is_used_view & is_viewing)
@bindings.add('space', filter=is_used_view & is_viewing)
def currcal(*event):
    dataview.currMonth()
    set_text(dataview.show_active_view())


@bindings.add('escape', filter=is_showing_choice, eager=True)
@bindings.add('enter', filter=is_showing_choice)
@bindings.add('<any>', filter=is_showing_choice)
def handle_choice(*event):
    """
    Handle any key presses. The coroutine used as dataview.got_input will determine which presses are acted upon and which are ignored.
    """
    keypressed = event[0].key_sequence[0].key
    dataview.details_key_press = keypressed
    done = dataview.got_choice()
    if done:
        dataview.hide_choice()
        application.layout.focus(text_area)


@bindings.add(
    'enter',
    filter=is_viewing_or_details & is_not_showing_choice & is_item_view & is_not_querying,
)
def show_details(*event):
    if dataview.is_showing_details:
        application.layout.focus(text_area)
        dataview.hide_details()
    else:
        tmp = dataview.get_details(text_area.document.cursor_position_row)[1]
        if tmp:
            dataview.show_details()
            details_area.text = tmp.rstrip()
            application.layout.focus(text_area)


@bindings.add(
    'enter',
    filter=is_showing_konnections & is_not_querying)
def show_details(*event):
    if dataview.is_showing_details:
        application.layout.focus(konnected_area)
        dataview.hide_details()
    else:
        tmp = dataview.get_details(konnected_area.document.cursor_position_row)[1]
        if tmp:
            dataview.show_details()
            details_area.text = tmp.rstrip()
            application.layout.focus(details_area)


@bindings.add('c-q', filter=is_editing, eager=True)
@bindings.add('c-z', filter=is_editing, eager=True)
def close_edit(*event):
    global text_area
    if (
        is_editing()
        and edit_buffer_changed()
        and not dataview.control_z_active
    ):
        dataview.control_z_active = True
        ask_buffer.text = 'There are unsaved changes'
        reply_buffer.text = wrap(
            'To discard them and close the editor press Control-Z again.', 0
        )
        return
    row, col = get_row_col()
    app = get_app()
    app.editing_mode = EditingMode.EMACS
    dataview.is_editing = False
    dataview.control_z_active = False
    application.layout.focus(text_area)
    application.output.set_cursor_shape(CursorShape.BLOCK)
    set_text(dataview.show_active_view())
    restore_row_col(row, col)


@bindings.add('enter', filter=is_showing_entry, eager=True)
def process_entry(*event):
    global text_area
    dataview.got_entry()

    def corountine():
        pass

    dataview.got_entry = corountine
    row, col = get_row_col()
    dataview.hide_entry()
    application.layout.focus(text_area)
    set_text(dataview.show_active_view())
    restore_row_col(row, col)


@bindings.add('escape', filter=is_showing_details, eager=True)
def close_details(*event):
    global text_area
    application.layout.focus(text_area)
    dataview.hide_details()


@bindings.add('escape', filter=is_showing_choice, eager=True)
def close_choice(*event):
    global text_area
    row, col = get_row_col()
    dataview.hide_choice()
    application.layout.focus(text_area)
    set_text(dataview.show_active_view())
    restore_row_col(row, col)


@bindings.add('escape', filter=is_showing_entry, eager=True)
def close_entry(*event):
    global text_area
    row, col = get_row_col()
    dataview.hide_entry()
    application.layout.focus(text_area)
    set_text(dataview.show_active_view())
    restore_row_col(row, col)


@edit_bindings.add('c-s', filter=is_editing, eager=True)
def save_changes(*event):
    if edit_buffer_changed():
        try:
            timer_save = TimeIt('***SAVE***')
            maybe_save(item)
            timer_save.stop()
        except Exception as e:
            logger.debug(f'exception: {e}')

    else:
        # no changes to save - close editor
        dataview.is_editing = False
        application.layout.focus(text_area)
        application.output.set_cursor_shape(CursorShape.BLOCK)
        set_text(dataview.show_active_view())
        app = get_app()
        app.editing_mode = EditingMode.EMACS


def maybe_save(item):
    # check hsh
    global text_area
    msg = item.check_item_hsh()
    if msg:
        show_message('Error', ', '.join(msg))
        return
    if item.item_hsh.get('itemtype', None) is None:
        show_message(
            'Error', 'An entry for itemtype is required but missing.', 0
        )
        return

    if item.item_hsh.get('summary', None) is None:
        show_message('Error', 'A summary is required but missing.', 0)
        return

    if item.item_hsh['itemtype'] == '*' and 's' not in item.item_hsh:
        show_message(
            'Error', 'An entry for @s is required for events but missing.', 0
        )
        # item needs correcting, return to edit
        return
    # hsh ok, save changes and close editor
    if item.doc_id in dataview.itemcache:
        try:
            del dataview.itemcache[item.doc_id]
        except Exception as e:
            logger.debug(f'exception: {e}')

    row, col = get_row_col()
    app = get_app()
    app.editing_mode = EditingMode.EMACS
    dataview.is_editing = False
    application.layout.focus(text_area)
    application.output.set_cursor_shape(CursorShape.BLOCK)
    set_text(dataview.show_active_view())
    loop = asyncio.get_event_loop()
    loop.call_later(0, item_changed, loop)


root_container = MenuContainer(
    body=body,
    menu_items=[
        MenuItem(
            'etm',
            children=[
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
            ],
        ),
        MenuItem(
            'view',
            children=[
                MenuItem('a) agenda', handler=agenda_view),
                MenuItem('b) busy', handler=busy_view),
                MenuItem('c) completed', handler=completed_view),
                MenuItem('d) do next', handler=next_view),
                MenuItem('e) effort', handler=effort_view),
                MenuItem('f) forthcoming', handler=forthcoming_view),
                MenuItem('h) history', handler=history_view),
                MenuItem('i) index', handler=index_view),
                MenuItem('j) journal', handler=journal_view),
                MenuItem('k) konnected', handler=konnected_view),
                MenuItem('l) location', handler=location_view),
                MenuItem('m) timers', handler=timers_view),
                MenuItem('o) occurrences', handler=do_occurrences),
                MenuItem('p) pinned', handler=pinned_view),
                MenuItem('q) query', handler=query_view),
                MenuItem('r) review', handler=review_view),
                MenuItem('s) scheduled alerts for today', handler=do_alerts),
                MenuItem('t) tags', handler=tag_view),
                MenuItem('u) used time', handler=used_view),
                MenuItem('U) used summary', handler=used_summary_view),
                MenuItem(
                    'v) refresh views to fit terminal',
                    handler=refresh_views,
                ),
                MenuItem('y) yearly calendar', handler=yearly_view),
                MenuItem(
                    '^c) copy active view to clipboard',
                    handler=copy_active_view,
                ),
                MenuItem('__ konnected view __', disabled=True),
                MenuItem('k) toggle showing konnections', handler=get_konnections),
            ]
        ),
        MenuItem(
            'move',
            children=[
                # MenuItem('-', disabled=True),
                # MenuItem('-', disabled=True),
                MenuItem('space|home) go to today in a, b, c, u, U and y', handler=currweek),
                MenuItem(
                    'end) prompt for and go to date in a, b and c', handler=do_jump_to_date
                ),
                MenuItem('right) next in a, b, c, u, U and y', disabled=True),
                MenuItem('left) previous in a, b, c, u, U and y', disabled=True),
                MenuItem('-', disabled=True),
                MenuItem('/|?) initiate forward|backward search', disabled=True),
                MenuItem('n|N) search next|previous incrementally', disabled=True),
                MenuItem(',,) clear search', handler=clear_search),
                MenuItem(
                    '^l) prompt for and go to line number',
                    handler=do_go_to_line,
                ),
                MenuItem('^p) go to next pinned item', handler=next_pinned),
            ],
        ),
        MenuItem(
            'edit',
            children=[
                MenuItem('+|N) add new item', handler=edit_new),
                MenuItem('J) jot it down', handler=edit_or_add_journal),
                MenuItem('-', disabled=True),
                MenuItem('^g) test goto link', handler=do_goto),
                MenuItem('^r) show repetitions', handler=is_editing_reps),
                MenuItem('^s) save changes & close', handler=save_changes),
                MenuItem('^z) discard changes & close', handler=close_edit),
            ],
        ),
        MenuItem(
            'selected',
            children=[
                MenuItem('enter) toggle showing details', handler=show_details),
                MenuItem('E) edit', handler=edit_existing),
                MenuItem('C) edit copy', handler=edit_copy),
                MenuItem('D) delete', handler=do_maybe_delete),
                MenuItem('F) finish', handler=do_finish),
                MenuItem('P) toggle pin', handler=toggle_pinned),
                MenuItem('R) reschedule', handler=do_reschedule),
                MenuItem('S) schedule new', handler=do_schedule_new),
                MenuItem('g) open goto link', handler=do_goto),
                MenuItem('^h) show completion history', handler=not_editing_history),
                MenuItem('^r) show repetitions', handler=not_editing_reps),
                MenuItem('^u) update last modified', handler=do_touch),
                MenuItem('^x) toggle archived status', handler=toggle_archived_status,),
                MenuItem('__ konnected view __', disabled=True),
                MenuItem('k) toggle showing konnections', handler=get_konnections),
            ],
        ),
        MenuItem(
            'timers',
            children=[
                MenuItem('m) show timer view', handler=timers_view),
                MenuItem('__ for the selected reminder __', disabled=True),
                MenuItem(
                    'T) create timer then toggle paused/running',
                    handler=next_timer_state,
                ),
                MenuItem(
                    'TR) add | record usedtime and delete timer',
                    handler=record_time,
                ),
                MenuItem(
                    'TD) delete timer without recording',
                    handler=maybe_delete_timer,
                ),
                MenuItem('__ ignores selection __', disabled=True),
                MenuItem(
                    'TT) toggle paused/running for active timer',
                    handler=toggle_active_timer,
                ),
                MenuItem('^t) start quick timer', handler=quick_timer),
                MenuItem('__ views showing recorded times __', disabled=True),
                MenuItem('e) effort', handler=effort_view),
                MenuItem('u) used time', handler=used_view),
                MenuItem('U) used summary', handler=used_summary_view),
            ],
        ),
    ],
    floats=[
        Float(
            xcursor=True,
            ycursor=True,
            content=CompletionsMenu(max_height=16, scroll_offset=1),
        ),
    ],
)


def set_askreply(_):
    if item.active:
        ask, reply = item.askreply[item.active]
    elif item.askreply.get(('itemtype', '')):
        ask, reply = item.askreply[('itemtype', '')]
    else:
        ask, reply = ('', '')
    ask_buffer.text = ask
    reply_buffer.text = wrap(reply, 0)


async def main(etmdir=''):
    global item, settings, ampm, style, type_colors, application, busy_colors
    timer_view = TimeIt('***VIEW***')
    ampm = settings['ampm']
    window_colors = settings['window_colors']
    type_colors = settings['type_colors']
    window_colors = settings['window_colors']
    busy_colors = {
        VSEP: type_colors['wrap'],
        HSEP: type_colors['wrap'],
        BUSY: type_colors['event'],
        CONF: type_colors['inbox'],
        ADAY: type_colors['wrap'],
        FREE: type_colors['wrap'],
    }
    # query = ETMQuery()
    style = get_style(window_colors)
    agenda_view()

    application = pta.Application(
        layout=Layout(
            root_container,
            focused_element=text_area,
        ),
        # set editing_mode in the entry buffer, use default elsewhere
        key_bindings=bindings,
        enable_page_navigation_bindings=True,
        mouse_support=True,
        style=style,
        full_screen=True,
        refresh_interval=1.0,
        on_invalidate=event_handler,
    )
    logger.debug('XX starting event_handler XX')
    timer_view.stop()
    try:
        result = await application.run_async()

    finally:
        # background_task.cancel()
        logger.info('Quitting event loop.')


if __name__ == '__main__':
    sys.exit('view.py should only be imported')
