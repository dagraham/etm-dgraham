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
import shutil

from prompt_toolkit.layout import Float
from prompt_toolkit.widgets import Dialog, Label, Button

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

import pyperclip
# set in __main__
logger = None

dataview = None
item = None
style = None
etmstyle = None
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

COMMAND_DETAILS = """\
* begins field RGX: return items in which the value of
  field begins with a match for the case insensitve
  regular expression RGX.

* includes field RGX: return items in which the value of
  field includes a match for the case insensitive
  regular expression RGX.

* equals field VAL: return items in which the value of
  field == VAL

* more field VAL: return items in which the value of
  field >= VAL. The value of field and VAL must be
  comparable, i.e., both strings or both numbers

* less field VAL: return items in which the value of
  field <= VAL. The value of field and VAL must be
  comparable, i.e., both strings or both numbers

* exists field: return items in which field exists

* any field LST: return items in which the value of field
  is a list and at least one element of field is an
  element of LST

* all field LST: return items in which the value of field
  is a list and the elements of field contain all the
  elements of LST

* one field LST: return items in which the value of
  field is one of the elements of LST

* info ID: return the details of the item whose
  document id equals the integer ID

* dt field EXP: return items in which the value of field
  is a date if EXP = '? date' or a datetime if EXP = '?
  time'. Else if EXP begins with  '>', '=' or '<' followed
  by a string following the format 'yyyy-mm-dd-HH-MM' then
  return items where the datetime of the field value bears
  the specified relation to the string, with hours and
  minutes ignored when the value of field is a date. E.g.,

        dt s < 2020-1-17

  would return items with @s date/times whose year <=
  2020, month <= 1 and month day <= 17.

  Alternatively,

        dt s ? date and equals itemtype *

  would return events with @s date/times that are dates,
  i.e., all day events or occasions."""


UPDATE_DETAILS = """\
* archive: if the items table is active, move the
  reminders from the items table to the archive table,
  else vice versa

* remove: remove the reminders from the database

* replace field RGX VAL: in the value of 'field', replace
  matches for RGX with VAL. If the value of 'field' is a
  list, do this for each element of the list. Remember to
  replace spaces in in both RGX and VAL with '\s'

* delete field: if the reminder has an entry for 'field',
  delete the entry

* set field VAL: set the value of 'field' to VAL
  overriding the current value if it exists

* provide field VAL: set the value of 'field' to VAL if
  there is no existing entry for 'field'

* attach field VAL: if the value of 'field' is intended to
  be a list and if VAL is not in this list, then add VAL
  to the list, creating the entry if necessary

* detach field VAL: if the value of 'field' is a list and
  this list contains VAL, then remove VAL from the list"""

USAGE = f"""\
Contents:
  Simple queries
  Simple query examples
  Archive queries
  Update queries
  Complex queries
  Command history
  Saved queries

Press '/' or '?' to search incrementally forward or
backward, respectively.

Simple queries
==============
Return a list of items displaying the itemtype, summary
and id, and sorted by id, (order created) using commands
with the format:

    command field [args]

where "field" is either 'itemtype', 'summary' or one of
the '@-keys' such as 'l' or 's', and "command" is one of
those listed below (see Simple Query Examples below for
examples):

{COMMAND_DETAILS}

Enter the command at the 'query:' prompt and press 'enter'
to submit the query and display the results. Press 'q' to
reopen the entry area to submit another query. Use up and
down cursor keys to choose from the command history (see
Command History below), submit '?' or 'help' to show this
display, submit 'l' to see a list of stored queries (see
Saved queries below) or submit 'quit', 'exit' or nothing
at all, '', to close the entry area and return to the
previous display.

Simple query examples
=====================
Find items where the summary includes a match for
"waldo":

    query: includes summary waldo

Precede a command with `~` to negate it. E.g., find
reminders where the summary does not include a match for
"waldo":

    query: ~includes summary waldo

To enter a list of values for "arg", simply separate the
components with spaces. E.g.,

    query: all t blue green

would return items with both blue and green tags or

    query: any t blue green

would return items with either a blue or a green tag. As
a last example

    query: one itemtype - *

would return items in which the item type is either '-'
or '*', i.e., either a task or an event.

Conversely, to enter a regex with a space and avoid its
being interpreted as a list, replace the space with '\s'.
E.g.,

    query: matches i john\sdoe

would return items with '@i' (index) entries such as
"John Doe/...".

Note: in the world of regular expressions '\s' matches
any white space character, including a space.

Components can be joined the using "or" or "and". E.g.,
find reminders where either the summary or the entry for
@d (description) includes "waldo":

    query: includes summary waldo or includes d waldo

Archive queries
===============

Queries, by default, search the items table in the etm
database. You can preceed any query with 'a ' (the letter
'a' followed by a space), to search the archive
table instead. E.g.,

    query: a includes summary waldo or includes d waldo

will search the archive table for reminders with matches
for 'waldo' in the summary or in the description.

Queries beginning with 'a ' are, in fact, the only way
to see archived items from within etm itself.

Update queries
==============

Queries can not only locate reminders but also update
them. The update commands act on items returned by a
query. E.g., this query

    query: includes i john\sdoe | replace i john\sdoe
        Jane\sDoe

can be regarded as taking the reminders whose index entry,
'i', includes a match for 'john doe' and feeding them to
the 'replace' command which then takes the index entry of
each reminder and replaces each match for 'john doe' with
'Jane Doe'.

All of the update commands work the same way: a query that
returns a list of reminders is followed by a pipe symbol
surrounded by spaces, ' | ', and an update command with
its arguments. Here is the complete list of these
update commands:

{UPDATE_DETAILS}

The recommended workflow for updating reminders is first
to perfect the query to be certain that it lists just the
items you want to update. Then press 'q' and the 'up'
cursor key to restore the previous query, add ' | ' and
the update command you want with its arguments.

WARNING: Since the results may not be reversible, consider
backing up your 'db.json' database before using update
commands. This simple command, e.g., would PERMANENTLY
DELETE ALL YOUR REMINDERS:

    query: exists itemtype | remove

Complex queries
===============
Return a formatted, heirarchial display of items. Both the
format and the items displayed are determined by the type
of the query and the arguments provided. Since these
queries can group and sort by date/times, these queries
must begin by specifying which of the possible datetimes
to use. There are four types of datetime specifications:

* u: sort and group by datetimes in '@u' (used time)
  entries. Also report aggregates of times spent in these
  entries. Only items with '@u' entries will be reported.
* s: sort and group by datetimes in '@f' entries in
  finished tasks and otherwise by '@s' entries. Only items
  with '@f' or '@s' entries will be reported.
* c: sort and group by the 'created' datetime. All items
  will be reported.
* m: sort and group by the 'modified' datetime if given
  else by the 'created' datetime. All items will be
  reported.

Complex queries follow the datetime specifier with a
required group/sort specification consisting of a
semicolon separated list with at least one of the
following components:

* index specification such as i, i[1:2] or i[1:]

    E.g. for an item with index entry '@i A/B/C':
        i      = ['A','B','C']
        i[0]   = 'A'
        i[1]   = 'B'
        i[2]   = 'C'
        i[3]   => error, list index out of range
        i[0:]  = ['A','B','C']
        i[:1]  = ['A']
        i[1:]  = ['B','C']
        i[1:2] = ['B']
        i[:2]  = ['A','B']
        i[2:]  = ['C']
        i[3:4] = i[3:] = []

    Note: using slices such as i[1:2] rather than i[1]
    avoids 'list index out of range errors' for index
    entries missing the indicated position and is
    strongly recommended.

    When an index specification returns an empty list,
    '~' is used for the missing entry. Items without an
    '@i' entry are given a default entry of '~' and
    included by default. Include 'exists i' in '-q'
    (discussed below) to overrule this default.

* field specification:
    l: location
    c: calendar

    Note: items without the specified field are given a
    default entry of '~' and included by default. Include
    'exists l' or 'exists c' in '-q' (discussed below)
    to overrule these defaults.

* date specification:
    year:
      YY: 2-digit year
      YYYY: 4-digit year
    month:
      M: month: 1 - 12
      MM: month: 01 - 12
      MMM: locale abbreviated month name: Jan - Dec
      MMMM: locale month name: January - December
    week: (examples based on 2020 iso week number 3):
      W: week number: 3
      WW: month days interval for week: Jan 13 - 19
      WWW: interval and year: Jan 13 - 19, 2020
      WWWW: interval, year and week number: Jan 13 - 19, 2020 #3
    day:
      D: month day: 1 - 31
      DD: month day: 01 - 31
      ddd: locale abbreviated week day: Mon - Sun
      dddd: locale week day: Monday - Sunday

    Note: when a date specification is given, the datetime
    used depends upon the report type.
        u: the value of the datetime component of the @u
           entry. Items without @u entries are omitted.
        s: the value of @f when it exists and, otherwise,
           the value of @s. Items lacking both @f and @s
           entries are omitted.
        c: the created datetime.
        m: the modified datetime if it exists, else the created
           datetime.

  E.g.

        query: u i[:1]; MMM YYYY; i[1:]; ddd D

  would create a usedtime query grouped (and sorted) by
  the first component of the index entry, the month and
  year, the remaining components of the index entry and
  finally the month day.

  Sorting note: Specifications using weeks are all sorted
  and grouped by by (YYYY, W). Specifications involving
  months are all sorted by (YYYY, M). Specifications
  involving days are all sorted by (D).

The group/sort specification can be followed, optionally,
by any of the following:

-b begin date/datetime: omit items with earlier datetimes

-e end date/datetime: omit items with later datetimes

-q query: exclude items not satisfying this simple query.
    Anything that could be used in a simple query
    described above could be used here. E.g., "-q exists
    f" would display only items with an "@f" entry, i.e.,
    finished tasks. Similarly "-q equals itemtype - and
    ~exists f" would limit the display to unfinished
    tasks.

-a append: append the contents of this comma separated
    list of @key characters to the formatted output.
    E.g., "-a d, l" would append the item description and
    location to the display of each item.

Note: -b and -e accept shortcuts:
    daybeg: 12am on the current day
    dayend: 12am on the following day
    weekbeg: 12am on Monday of the current week
    weekend: 12am on Monday of the following week
    monthbeg: 12am on the 1st of the current month
    monthend: 12am on the 1st of the following month
and can be combined with period strings using M (month),
w (week), d (day), h (hour) and m (minute). E.g.:
    weekbeg - 1w (the beginning of the previous week)
    monthend + 1M (the end of the following month)

Command History
===============
Any query entered at the 'query:' prompt and submitted by
pressing 'Enter' is added to the command history. These
queries are kept as long as 'etm' is running and can be
accessed using the up and down cursor keys in the query
field. This means you can enter a query, check the result,
press 'q' to reopen the query prompt, press the up cursor
and you will have your previous query ready to modify and
submit again. It is also possible to keep a permanent list
of queries accessible by shortcuts. See 'Saved Queries'
below.

Saved Queries
=============
Commonly used queries can be specified in the "queries"
section of `cfg.yaml` in your etm home directory along
with shortcuts for their use. E.g. with the default entry

  queries:
    # unfinished tasks by location and modified datetime
    md: m l -q equals itemtype - and ~exists f
    # usedtimes by i[:1], month and i[1:2] with d
    ut: u i[:1]; MMM YYYY; i[1:2] -a d
    # finish/start by i[:1], month and i[1:2] with u and d
    st: s i[:1]; MMM YYYY; i[1:2] -a u, d
    # items with an "@u" but missing the needed "@i"
    mi: exists u and ~exists i

entering

    query: ut

and pressing 'enter' would result in the 'ut' being
replaced by its corresponding value to give

    query: u i[:1]; MMM YYYY; i[1:2] -a d

This query can now be submitted as is or first edited to
add, say, `-b` and `-e` options and then submitted. As
with other queries, the submitted form of the query is
added to the command history.

Enter

    query: l

to display a list of the saved keys and values.
"""

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
                (r'\b(begins|includes|equals|more|less|exists|any|all|one)\b', Keyword),
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
        self.style = etmstyle
        self.Item = Query()

        self.allowed_commands = ", ".join([x for x in self.filters])

        self.usage = USAGE

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
            dataview.db.write_back(changed)
            self.changed = True
        logger.debug(f"a: {a}; rgx: {rgx}; re;: {rep}; changed: {changed}")
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
        logger.debug(f"a: {a}; len(items): {len(items)}")
        changed = []
        for item in items:
            if a in item:
                del item[a]
                item['modified'] = pendulum.now('local')
                changed.append(item)
        if changed:
            dataview.db.write_back(changed)
            self.changed = True
        logger.debug(f"a: {a}; changed: {changed}")
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
            dataview.db.write_back(changed)
            self.changed = True
        logger.debug(f"a: {a}; b: {b}; changed: {changed}")

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
            dataview.db.write_back(changed)
            self.changed = True
        logger.debug(f"a: {a}; b: {b}; changed: {changed}")


    def attach(self, a, b, items):
        """
        Attach 'b' into the item['a'] list if 'b' is not in the list.
        """
        changed = []
        b = re.sub('\\\s', ' ', b)
        for item in items:
            if a not in item:
                logger.debug(f"{a} not in item")
                item.setdefault(a, []).append(b)
                item['modified'] = pendulum.now('local')
                changed.append(item)
            elif isinstance(item[a], list) and b not in item[a]:
                item.setdefault(a, []).append(b)
                item['modified'] = pendulum.now('local')
                changed.append(item)
        if changed:
            dataview.db.write_back(changed)
            self.changed = True
        logger.debug(f"a: {a}; item[{a}]: {item[a]};  b: {b}; changed: {changed}")

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
            dataview.db.write_back(changed)
            self.changed = True
        logger.debug(f"a: {a}; b: {b}; changed: {changed}")


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
        # the value of field 'a' includes the case-insensitive regex 'b'
        return where(a).search(b, flags=re.IGNORECASE)

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
        return  f"{item_details(item, False)}"


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
            logger.debug(f"updt: {updt}")
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
                    return False, wrap(f"""bad command: '{part[0]}'. Only commands in {self.allowed_commands} are allowed.""")

            if len(part) > 3:
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
            return False, self.usage
        try:
            ok, test, updt = self.process_query(query)
            logger.debug(f"query: {query}; ok: {ok}; test: {test}; updt: {updt}")
            if not ok:
                return False, test
            if isinstance(test, str):
                # info
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

    lines = res.split('\n')
    msg = []
    for line in lines:
        if line.lstrip().startswith('etm-dgraham'):
            msg.append('etm-dgraham')
        elif line.lstrip().startswith('INSTALLED'):
            msg.append(line)
        elif line.lstrip().startswith('LATEST'):
            msg.append(line)
    show_message("version information", "\n".join(msg), 2)

update_status = UpdateStatus()

async def auto_check_loop(loop):
    logger.debug("in auto_check_loop")
    res = check_output("pip search etm-dgraham")
    logger.debug(f"res: {res}")
    if not res:
        update_status.set_status("?")
        return

    lines = res.split('\n')
    new = False
    for line in lines:
        if line.lstrip().startswith('LATEST'):
            new = re.split(":\s+", line)[1]
            break
    logger.debug(f"new: {new}")
    # status = f"{FINISHED_CHAR} " if new else f"{FINISHED_CHAR} "
    # status = f"[{new}] " if new else f"{PIN_CHAR}"
    status = "ⓤ " if new else FINISHED_CHAR
    logger.debug(f"updating status: '{status}'")
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
        dialog = ConfirmDialog("unsaved changes", "discard changes and close editor?")

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
    res = ""
    try:
        res = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        return res
    except Exception as res:
        logger.warn(f"Error running {cmd}: {res}")
        return ""

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
    return dataview.active_view in ['agenda', 'completed', 'history', 'index', 'tags', 'records', 'do next', 'used time', 'used time expanded',  'relevant', 'forthcoming', 'query', 'pinned']

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
    return dataview.active_view not in ['yearly']

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

# bggrey = "bg:#437070" # 2 shades lighter darkslategrey
# tagrey = "bg:#264040" # 1 shade darker of darkslategrey

bggrey = "bg:#396060" # 1 shade lighter of darkslategrey for status and menubar background
tagrey = "bg:#1d3030" # 2 shades darker of darkslategrey for textarea background

dark_style = Style.from_dict({
    'dialog':             f"bg:{NAMED_COLORS['DarkSlateGrey']} {NAMED_COLORS['White']}",
    'frame.label':       f"bg:{NAMED_COLORS['DarkSlateGrey']} {NAMED_COLORS['White']}",
    'button.focused':   f"bg:{NAMED_COLORS['DarkGreen']} {NAMED_COLORS['White']}",
    'dialog.body label': f"{NAMED_COLORS['White']}",
    'dialog.body':        f"bg:{NAMED_COLORS['DarkSlateGrey']} {NAMED_COLORS['White']}",
    'dialog shadow':      'bg:#444444',
    'text-area': f"{tagrey} {NAMED_COLORS['Ivory']}",

    'dialog-output':    f"bg:{NAMED_COLORS['DarkSlateGrey']} {NAMED_COLORS['Lime']}",
    'dialog-entry':     f"bg:{NAMED_COLORS['White']} {NAMED_COLORS['Black']}",
    'status':     f"{bggrey} {NAMED_COLORS['White']}",
    'query':      f"{NAMED_COLORS['Ivory']}",
    'details':    f"{NAMED_COLORS['Ivory']}",
    'status.position': '#aaaa00',
    'status.key': '#ffaa00',
    'not-searching': '#222222',
    'entry':      f"{tagrey} {NAMED_COLORS['LightGoldenRodYellow']}",
    'ask':        f"{tagrey} {NAMED_COLORS['Lime']} bold",
    'reply':      f"{tagrey} {NAMED_COLORS['DeepSkyBlue']}",

    'window.border': '#888888',
    'shadow':        'bg:#222222',

    'menu-bar': f"{bggrey} {NAMED_COLORS['White']}",
    'menu-bar.selected-item': 'bg:#ffffff #000000',
    'menu': f"bg:{NAMED_COLORS['DarkSlateGrey']} {NAMED_COLORS['White']}",
    'menu.border': '#aaaaaa',
    'window.border shadow': '#444444',

    })

light_style = Style.from_dict({
    'dialog':             f"bg:{NAMED_COLORS['DimGrey']} {NAMED_COLORS['White']}",
    'frame.label':       f"bg:{NAMED_COLORS['DimGrey']} {NAMED_COLORS['White']}",
    'button.focused':   f"bg:{NAMED_COLORS['DarkGreen']} {NAMED_COLORS['White']}",
    'dialog.body label': f"{NAMED_COLORS['White']}",
    'dialog.body':        f"bg:{NAMED_COLORS['DimGrey']} {NAMED_COLORS['White']}",
    'dialog shadow':      'bg:#444444',
    'text-area': f"bg:{NAMED_COLORS['Cornsilk']} {NAMED_COLORS['Black']}",

    'dialog-entry':     f"bg:{NAMED_COLORS['White']} {NAMED_COLORS['Black']}",
    'status':     f"{bggrey} {NAMED_COLORS['White']}",
    'query':   f"{NAMED_COLORS['Black']}",
    'details': f"{NAMED_COLORS['Black']}",
    'status.position': '#aaaa00',
    'status.key': '#ffaa00',
    'not-searching': '#777777',
    'entry': f"bg:{NAMED_COLORS['Cornsilk']} {NAMED_COLORS['Black']}",
    'ask':   f"bg:{NAMED_COLORS['Cornsilk']} {NAMED_COLORS['DarkGreen']} bold",
    'reply': f"bg:{NAMED_COLORS['Cornsilk']} {NAMED_COLORS['Blue']}",

    'window.border': '#888888',
    'shadow': 'bg:#222222',

    'menu-bar': f"{bggrey} {NAMED_COLORS['White']}",
    'menu-bar.selected-item': 'bg:#ffffff #000000',
    'menu': f"bg:{NAMED_COLORS['DimGrey']} {NAMED_COLORS['White']}",
    'menu.border': '#aaaaaa',
    'window.border shadow': '#444444',
    })


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
        t_fmt = dt.format("h") if ampm else dt.format("H")
    else:
        t_fmt = dt.format("h:mm") if ampm else dt.format("H:mm")
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
    # check for updates every interval minutes

    interval = settings.get('updates_interval', 0)
    minutes = 0
    try:
        while True:
            now = pendulum.now()
            current_today = dataview.now.format("YYYYMMDD")
            asyncio.ensure_future(maybe_alerts(now))
            current_datetime = status_time(now)
            today = now.format("YYYYMMDD")
            logger.debug(f"minutes: {minutes}; interval: {interval}")
            wait = 60 - now.second

            if interval:
                if minutes == 0:
                    minutes = 1
                    logger.debug("calling auto_check_loop")
                    loop = asyncio.get_event_loop()
                    asyncio.ensure_future(auto_check_loop(loop))
                    logger.debug("back from auto_check")
                else:
                    minutes += 1
                    minutes = minutes % interval

            if today != current_today:
                logger.debug(f"calling new_day. current_today: {current_today}; today: {today}")
                loop = asyncio.get_event_loop()
                asyncio.ensure_future(new_day(loop))
                logger.debug(f"back from new_day")
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
    return [ ('class:status',  '                      '), ]


def get_statusbar_right_text():
    return [ ('class:status',  f"{dataview.timer_report()}{dataview.active_view} {update_status.get_status()}"), ]

def openWithDefault(path):
    sys_platform = platform.system()
    windoz = sys_platform in ('Windows', 'Microsoft')
    mac =  sys_platform == 'Darwin'
    if windoz:
        os.startfile(path)
        return()

    cmd = 'open' + f" {path}" if mac else 'xdg-open' + f" {path}"
    check_output(cmd)
    return

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

reply_dimension = 2
entry_dimension = 10
# reply_dimension = Dimension(min=2, weight=2)
# entry_dimension = Dimension(min=3, weight=2)

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

query_bindings = KeyBindings()

@query_bindings.add('enter', filter=is_querying)
def accept(buff):
    logger.debug('accept triggered')
    set_text('processing query ...')
    if query_window.text:
        text = query_window.text
        queries = settings.get('queries')
        if text == 'l' and queries:
            tmp = """\
Stored queries are listed as <key>: <query> below. Enter
<key> at the prompt and press 'enter' to replace <key>
with <query>. Submit this query as is or edit it first
and then submit.

  """ + "\n  ".join([f"{k}: {v}" for k, v in queries.items()])
            set_text(tmp)
            return False
        if queries and text in queries:
            set_text("")
            text = queries[text]
            query_window.text = text
            # don't reset the query area buffer we just set
            return True
        if text.strip() in ['quit', 'exit']:
            # quitting
            dataview.active_view = dataview.prior_view
            application.layout.focus(text_area)
            set_text(dataview.show_active_view())
            return False

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
# query_window = Window(BufferControl(buffer=query_buffer, focusable=True, focus_on_click=True, key_bindings=edit_bindings), height=reply_dimension, wrap_lines=True, style='class:query')



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
    logger.debug(f"text: {text}; updt: {updt}")
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
            logger.debug("calling apply_dates_filter with {len(items)} and {filters}")
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
                   style='class:status', width=20, align=WindowAlign.CENTER),
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

    # date_required = isinstance(instance, pendulum.Date) and not isinstance(instance, pendulum.DateTime)

    date_required = instance.hour == 0 and instance.minute == 0

    instance = pendulum.instance(instance)

    instance = instance.date() if date_required else instance
    logger.debug(f"date_required: {date_required}; instance: {instance}; type: {type(instance)}")
    new = "new date" if date_required else "new datetime"

    def coroutine():
        dialog = TextInputDialog(
            title='reschedule instance',
            label_text=f"selected: {hsh['itemtype']} {hsh['summary']}\ninstance: {format_datetime(instance)[1]}\n\n{new}:")

        new_datetime = yield from show_dialog_as_float(dialog)

        if not new_datetime:
            return
        changed = False
        # ok, dt, z = parse_datetime(new_datetime)
        try:
            dt = pendulum.parse(new_datetime, strict=False, tz='local')
            ok = True
        except:
            ok = False

        if ok:
            dt = dt.date() if date_required else dt
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
    app = get_app()
    app.editing_mode = EditingMode.VI if settings['vi_mode'] else EditingMode.EMACS
    if dataview.is_showing_details:
        application.layout.focus(text_area)
        dataview.hide_details()
    dataview.is_editing = True
    doc_id, entry = dataview.get_details(text_area.document.cursor_position_row, True)
    item.edit_item(doc_id, entry)
    entry_buffer.text = item.entry
    starting_buffer_text = item.entry
    default_buffer_changed(event)
    default_cursor_position_changed(event)
    application.layout.focus(entry_buffer)

def entry_buffer_changed():
    return entry_buffer.text != starting_buffer_text


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
    logger.debug(f"ok: {ok}; show: {show}; item_id: {item_id}; job_id: {job_id}; due: {due}")
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
                done = pendulum.parse(done_str, strict=False, tz='local')
                logger.debug(f"done: {done}; {type(done)}")
                ok = True
            except:
                ok = False
            if ok:
                # valid done
                res = item.finish_item(item_id, job_id, done, due)
                # dataview.itemcache[item.doc_id] = {}
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
    starting_buffer_text = ""
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
    msg = ""
    def coroutine():
        global msg
        dialog = TextInputDialog(
            title='import file',
            completer=PathCompleter(expanduser=True),
            label_text="""\
It is possible to import data from files with
one of the following extensions:
  .json  a json file exported from etm 3.2.x
  .text  a text file with etm entries as lines
  .ics   an iCalendar file
Enter the path of the file to import:""")

        file_path = yield from show_dialog_as_float(dialog)
        if file_path:
            ok, msg = import_file(file_path)
            if ok:
                dataview.refreshRelevant()
                dataview.refreshAgenda()
                dataview.refreshCurrent()
                loop = asyncio.get_event_loop()
                loop.call_later(0, data_changed, loop)
            show_message('import file', msg)

    asyncio.ensure_future(coroutine())


@bindings.add('c-p', filter=is_viewing & is_item_view)
def do_whatever(*event):
    """
    For testing whatever
    """
    dataview.handle_backups()


@bindings.add('c-x', filter=is_viewing & is_item_view)
def toggle_archived_status(*event):
    """
    If using items table move the selected item to the archive table and vice versa.
    """
    # row = text_area.document.cursor_position_row
    # dataview.get_arch_id(text_area.document.cursor_position_row)
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
        logger.debug(f"calling complex query with text: {text}")
        dataview.use_items()
        item.use_items()
        loop.call_later(0, data_changed, loop)
        # loop.call_later(0, do_show_processing, loop)
        loop.call_later(.1, do_complex_query, text, loop)
    return


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
    item.use_items()
    set_text(dataview.show_active_view())

@bindings.add('c', filter=is_viewing)
def completed_view(*event):
    dataview.set_active_view('c')
    item.use_items()
    set_text(dataview.show_active_view())

@bindings.add('b', filter=is_viewing)
def busy_view(*event):
    dataview.set_active_view('b')
    item.use_items()
    set_text(dataview.show_active_view())

@bindings.add('q', filter=is_viewing)
def query_view(*event):
    # ask_buffer.text = "Submit '?' for help or 'l' for a list of stored queries"
    ask_buffer.text = "Submit '?' for help or 'l' for a list of stored queries"
    dataview.set_active_view('q')
    dataview.show_query()
    set_text(dataview.show_active_view())
    application.layout.focus(query_area)

@bindings.add('u', filter=is_viewing)
def used_view(*event):
    dataview.set_active_view('u')
    item.use_items()
    set_text(dataview.show_active_view())

@bindings.add('U', filter=is_viewing)
def used_summary_view(*event):
    dataview.set_active_view('U')
    item.use_items()
    set_text(dataview.show_active_view())

@bindings.add('y', filter=is_viewing)
def yearly_view(*event):
    dataview.set_active_view('y')
    set_text(dataview.show_active_view())

@bindings.add('h', filter=is_viewing)
def history_view(*event):
    dataview.set_active_view('h')
    item.use_items()
    set_text(dataview.show_active_view())

@bindings.add('p', filter=is_viewing)
def pinned_view(*event):
    dataview.set_active_view('p')
    item.use_items()
    set_text(dataview.show_active_view())


@bindings.add('f', filter=is_viewing)
def forthcoming_view(*event):
    dataview.set_active_view('f')
    item.use_items()
    set_text(dataview.show_active_view())

@bindings.add('d', filter=is_viewing)
def next_view(*event):
    dataview.set_active_view('d')
    item.use_items()
    set_text(dataview.show_active_view())

@bindings.add('r', filter=is_viewing)
def records_view(*event):
    dataview.set_active_view('r')
    item.use_items()
    set_text(dataview.show_active_view())

@bindings.add('t', filter=is_viewing)
def tag_view(*event):
    dataview.set_active_view('t')
    item.use_items()
    set_text(dataview.show_active_view())

@bindings.add('i', filter=is_viewing)
def index_view(*event):
    dataview.set_active_view('i')
    item.use_items()
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
    if entry_buffer_changed():
        logger.debug(f"item modified - saving")
        save_before_quit()
    else:
        # item.is_modified = False
        logger.debug(f"item not modified - closing")
        app = get_app()
        app.editing_mode = EditingMode.EMACS
        dataview.is_editing = False
        application.layout.focus(text_area)
        set_text(dataview.show_active_view())

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
        MenuItem('f) forthcoming', handler=forthcoming_view),
        MenuItem('h) history', handler=history_view),
        MenuItem('i) index', handler=index_view),
        MenuItem('p) pinned', handler=pinned_view),
        MenuItem('q) query', handler=query_view),
        MenuItem('r) records', handler=records_view),
        MenuItem('t) tags', handler=tag_view),
        MenuItem('u) used time', handler=used_view),
        MenuItem('U) used time summary', handler=used_summary_view),
        MenuItem('-', disabled=True),
        MenuItem("s) scheduled alerts for today", handler=do_alerts),
        MenuItem('y) half yearly calendar', handler=yearly_view),
        MenuItem('-', disabled=True),
        MenuItem('/) search forward'),
        MenuItem('?) search backward'),
        MenuItem('n) next incrementally in search'),
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
        MenuItem('^z) close editor', handler=close_edit),
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
        MenuItem('^g) open goto', handler=do_goto),
        MenuItem('^r) show repetitions', handler=not_editing_reps),
        MenuItem('^x) toggle archived status', handler=toggle_archived_status),
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


def set_askreply(_):
    # logger.debug(f"item.active: {item.active}; item.askreply: {item.askreply}")
    if item.active:
        ask, reply = item.askreply[item.active]
    elif item.askreply.get(('itemtype', '')):
        logger.debug(f"got ('itemtype', '')")
        ask, reply = item.askreply[('itemtype', '')]
    else:
        ask, reply = ('', '')
    ask_buffer.text = ask
    reply_buffer.text = wrap(reply, 0)


async def main(etmdir=""):
    global item, settings, ampm, style, etmstyle, application
    ampm = settings['ampm']
    terminal_style = settings['style']
    etmstyle = settings['colors']
    if terminal_style == "dark":
        style = dark_style
        # etmstyle = dark_etmstyle
    else:
        style = light_style
        # etmstyle = light_etmstyle
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
    background_task = asyncio.create_task(event_handler())
    try:
        await application.run_async()
    finally:
        background_task.cancel()
        logger.info("Quitting event loop.")


if __name__ == '__main__':
    sys.exit('view.py should only be imported')