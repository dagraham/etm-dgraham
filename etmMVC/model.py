#!/usr/bin/env python3

from pprint import pprint
import pendulum
from pendulum import parse

from datetime import datetime

import sys
import re

from tinydb import TinyDB, Query, Storage
from tinydb.operations import delete
from tinydb.database import Table
from tinydb.storages import JSONStorage
from tinydb_serialization import Serializer
from tinydb_serialization import SerializationMiddleware
from tinydb_smartcache import SmartCacheTable

from copy import deepcopy
import calendar as clndr

import dateutil
from dateutil.rrule import *
from dateutil.easter import easter
from dateutil import __version__ as dateutil_version

from jinja2 import Environment, Template

import textwrap

import os
import platform

import textwrap
import shutil

import logging
import logging.config
logger = logging.getLogger()

etmdir = None

# pendulum.set_formatter('alternative')
# FIXME
ampm = True

ETMFMT = "%Y%m%dT%H%M"
ZERO = pendulum.interval(minutes=0)

# display characters 
datedChar2Type = {
    '!': "ib",
    '*': "ev",
    '~': "ac",
    '%': "nt",
    '-': "ta",
    '+': "tw",
    'x': "tf",
    '?': "so",
}

pastdueTaskChar2Type = {
    '-': "td",
    '+': "tw"
}

undatedChar2Type = {
    '-': "ta",
    '%': "nt",
    '!': "ib",
    '?': "so",
    'x': "tf",
}

# type codes in the order in which they should be sorted
# palette settings will determine display colors for each
types = [
        'ib',  # inbox
        'oc',  # occasion
        'ev',  # event
        'td',  # pastdue task or available job 
        'tw',  # job with unfinished prereqs - scheduled or unscheduled 
        'ta',  # task or job that is not pastdue 
        'by',  # beginby"
        'ac',  # action
        'nt',  # note
        'so',  # someday
        'tf',  # finished task or job
         ]

type_keys = {
    "*": "event",
    "-": "task",
    "~": "action",
    "%": "journal entry",
    "?": "someday entry",
    "!": "inbox entry",
}

at_keys = {
    '+': "include (list of date-times)",
    '-': "exclude (list of date-times)",
    'a': "alert (timeperiod: cmd, optional args*)",
    'b': "beginby (integer number of days)",
    'c': "calendar (string)",
    'd': "description (string)",
    'e': "extent (timeperiod)",
    'f': "finish (datetime)",
    'g': "goto (url or filepath)",
    'h': "completions history (list of done:due datetimes)",
    'i': "index (colon delimited string)",
    'j': "job summary (string)",
    'l': "location (string)",
    'm': "memo (list of 'datetime, timeperiod, datetime')",
    'n': "named delegate (string)",
    'o': "overdue (r)estart, (s)kip or (k)eep)",
    'p': "priority (integer)",
    'r': "repetition frequency (y)early, (m)onthly, (w)eekly,"
         " (d)aily, (h)ourly, mi(n)utely",
    's': "starting date or datetime",
    't': "tags (list of strings)",
    'x': "extracton key (string)",
    'z': "timezone (string)",
    'itemtype': "itemtype (character)",
    'summary': "summary (string)"
}

amp_keys = {
    'r': {
        'c': "count: integer number of repetitions",
        'E': "easter: number of days before (-), on (0) or after (+) Easter",
        'h': "hour: list of integers in 0 ... 23",
        'r': "frequency: character in y, m, w, d, h, n",
        'i': "interval: positive integer",
        'm': "monthday: list of integers 1 ... 31",
        'M': "month: list of integers in 1 ... 12",
        'n': "minute: list of integers in 0 ... 59",
        's': "set position: integer",
        'u': "until: datetime",
        'w': "weekday: list from SU, MO, ..., SA",
    },
    'j': {
        'a': "alert: timeperiod: command, args*",
        'b': "beginby: integer number of days",
        'd': "description: string",
        'e': "extent: timeperiod",
        'f': "finish: datetime",
        'i': "unique id: integer or string",
        'j': "job summary (string)",
        'l': "location: string",
        'm': "memo (list of 'datetime, timeperiod, datetime')",
        'n': "named delegate (string)",
        'p': "prerequisites: comma separated list of ids of immediate prereqs",
        's': "start/due: timeperiod before task start",
    },
}

at_regex = re.compile(r'\s@', re.MULTILINE)
amp_regex = re.compile(r'\s&', re.MULTILINE)
week_regex = re.compile(r'[+-]?(\d+)w', flags=re.I)
day_regex = re.compile(r'[+-]?(\d+)d', flags=re.I)
hour_regex = re.compile(r'[+-]?(\d+)h', flags=re.I)
minute_regex = re.compile(r'[+-]?(\d+)m', flags=re.I)
sign_regex = re.compile(r'(^\s*([+-])?)')
int_regex = re.compile(r'^\s*([+-]?\d+)\s*$')
period_string_regex = re.compile(r'^\s*([+-]?(\d+[wWdDhHmM])+\s*$)')
period_parts = re.compile(r'([wWdDhHmM])')
comma_regex = re.compile(r',\s*')
colon_regex = re.compile(r'\:\s*')
semicolon_regex = re.compile(r'\;\s*')

item_hsh = {} # preserve state

allowed = {}
required = {}
undated_methods = 'cdegilmstx'
date_methods = 'br'
datetime_methods = date_methods + 'ea+-'
task_methods = 'fjp'

# events
required['*'] = 's'
allowed['*'] = undated_methods + datetime_methods


# tasks
required['-'] = ''
allowed['-'] = undated_methods + datetime_methods + task_methods

# journal entries
required['%'] = ''
allowed['%'] = undated_methods + datetime_methods

# someday entries
required['?'] = ''
allowed['?'] = undated_methods + task_methods + datetime_methods

# inbox entries
required['!'] = ''
allowed['!'] = undated_methods + task_methods

# item type t and has s
# allowed['date'] = allowed[t] + 'br'
# allowed['datetime'] = allowed[t] + 'abr'
# allowed['r'] = '+-'

requires = {
        'a': 's',
        'b': 's',
        'r': 's',
        '+': 'r',
        '-': 'r',
        }

def check_requires(key, hsh):
    """
    Check that hsh has the prerequisite entries for key.
    """
    if key in requires and requires[key] not in hsh:
        return False, ('warn', "@{0} is required for @{1}\n".format(requires[key], key))
    else:
        return True, ('say', '')


type_prompt = u"type character for new item:"
item_types = u"item type characters:\n  *: event\n  -: task\n  #: journal entry\n  ?: someday entry\n  !: nbox entry"


def deal_with_at(at_hsh={}):
    """
    When an '@' has been entered but not yet with its key, show required and available keys with descriptions. Note, for example, that until a valid entry for @s has been given, @a, @b and @z are not available.
    """
    pass

deal_with = {}

def deal_with_s(at_hsh = {}):
    """
    Check the currents state of at_hsh regarding the 's' key

    """
    s = at_hsh.get('s', None)
    top = "{}?".format(at_keys['s'])
    bot = ''
    if s is None:
        return top, bot
    ok, obj, tz = parse_datetime(s)
    if not ok or not obj:
        return top, "considering: '{}'".format(s), None
    item_hsh['s'] = obj
    item_hsh['z'] = tz
    if ok == 'date':
        # 'dateonly'
        bot = "starting: {}".format(obj.format("ddd MMM D YYYY"))
        bot += '\nWithout a time, this schedules an all-day, floating item for the specified date in whatever happens to be the local timezone.'
    elif ok == 'naive':
        bot = "starting: {}".format(obj.in_tz('Factory').format("ddd MMM D YYYY h:mmA"))
        bot += "\nThe datetime entry for @s will be interpreted as a naive datetime in whatever happens to be the local timezone."
    elif ok == 'aware':
        # bot = "starting: {}".format(obj.format("ddd MMM D h:mmA z"))
        bot = "starting: {}".format(obj.in_tz('local').format("ddd MMM D YYYY h:mmA z"))
        bot += "\nThe datetime entry for @s will be interpreted as an aware datetime in the specified timezone."
    else:
        bot = "starting: {}".format(obj.in_tz('local').format("ddd MMM D YYYY h:mmA z"))
        bot += "\nThe datetime entry for @s will be interpreted as an aware datetime in the current local timezone. Append a comma and then 'float' to make the datetime floating (naive) or a specific timezone, e.g., 'US/Pacific', to use that timezone."

    # if 'summary' in item_hsh:
    #     summary = set_summary(item_hsh['summary'], obj)
    #     bot += "\n{}".format(summary)
    #     item_hsh['summary'] = summary

    return top, bot, obj

deal_with['s'] = deal_with_s

def deal_with_e(at_hsh={}):
    """
    Check the current state of at_hsh regarding the 'e' key.
    """
    s = at_hsh.get('e', None)
    top = "{}?".format(at_keys['e'])
    bot = ''
    if s is None:
        return top, bot, item_hsh
    ok, obj = parse_interval(s)
    if not ok:
        return top, "considering: '{}'".format(s), None
    item_hsh['e'] = obj
    bot = "extent: {0}".format(item_hsh['e'].in_words())
    # bot += "\n\n{}".format(str(at_hsh))
    return top, bot, obj

deal_with['e'] = deal_with_e

def deal_with_i(at_hsh={}):
    """
    Replaces the old filepath and to provide a heirarchial organization
    view of the data. Entered as a colon delineated string, stored as a
    list.
    >>> deal_with_i({'i': "a:b:c"})[2]
    ['a', 'b', 'c']
    >>> deal_with_i({'i': "plant:tree:oak"})[2]
    ['plant', 'tree', 'oak']
    """
    s = at_hsh.get('i', None)
    top = "{}?".format(at_keys['i'])
    bot = ''
    if s is None:
        return top, bot, None

    try:
        res = [x.strip() for x in s.split(':')]
        ok = True
    except:
        res = None
        ok = False

    if not ok or type(res) != list:
        return top, "considering: '{}'".format(s), None

    if type(res) != list:
        return False, "index {}".format(arg)

    item_hsh['i'] = res
    bot = "index: " + ", ".join(['level {0} -> {1}'.format(i, res[i]) for i in range(len(res))])
    return top, bot, res

deal_with['i'] = deal_with_i


def get_reps(n=3, at_hsh={}):
    """
    Return the first n instances of the repetition rule.
    """
    if not at_hsh or 's' not in at_hsh or 'rrulestr' not in at_hsh:
        return False, "Both @s and @r are required for repetitions"

    tz = at_hsh['s'].tzinfo
    naive = tz.abbrev == '-00'
    if naive:
        start = at_hsh['s']
        zone = 'floating'
    else:
        local = at_hsh['s'].in_timezone('local')
        start = local.replace(tzinfo='Factory')
        zone =  local.format("zz")
    rrs = rrulestr(at_hsh['rrulestr'], dtstart=start)
    out = rrs.xafter(start, n+1, inc=True)
    dtstart = format_datetime(at_hsh['s'])[1]
    # dtstart = format_datetime(start)[1]
    lst = []
    for x in out:
        lst.append(format_datetime(x)[1])
    outstr = "\n    ".join(lst[:n])
    if len(lst) <= n:
        countstr = "Repetitions on or after DTSTART"
    else:
        countstr = "The first {} repetitions on or after DTSTART".format(n)
    res = """\
    DTSTART:{}
{}:
    {}
All times: {}""".format(dtstart, countstr,  outstr, zone)
    return True, res

def get_next(at_hsh={}):
    if not at_hsh or 's' not in at_hsh or 'rrulestr' not in at_hsh:
        return False, "Both @s and @r are required for repetitions"



def deal_with_r(at_hsh={}):
    """
    Check the current state of at_hsh regarding r and s.
    """
    top = "repetition rule?"
    bot = "{}".format(at_keys['r'])
    lofh = at_hsh.get('r', [])
    if not lofh:
        return top, bot, None

    ok, res = rrule(lofh)
    if not ok:
        return top, res, None

    rrulelst = []

    # dtut_format = "YYYYMMDD[T]HHmm[00]"
    dtut_format = ";[TZID=]zz:YYYYMMDD[T]HHmm[00]"
    if 's' in item_hsh:
        if type(item_hsh['s']) == pendulum.pendulum.Date:
            # dtut_format = "YYYYMMDD[T][000000]"
            dtut_format = ";[TZID=]zz:YYYYMMDD[T][000000]"
    else:
        bot = "An entry for @s is required for repetition."
        return top, bot, None
    for hsh in res:
        r = hsh.get('r', None)
        if r:
            keys = ['&{}'.format(x) for x in amp_keys['r'] if x not in hsh]
            for key in hsh:
                if hsh[key] and key in amp_keys['r']:
                    bot = "{}".format(amp_keys['r'][key])
                else:
                    bot = 'Allowed: {}'.format(", ".join(keys))
        else:
            # shouldn't happen
            pass
        rrulelst.append(hsh['rrulestr'])

    if '+' in item_hsh:
        for rdate in item_hsh['+']:
            rrulelst.append("RDATE:{}".format(rdate.format(dtut_format, formatter='alternative')))

    if '-' in item_hsh:
        for exdate in item_hsh['-']:
            rrulelst.append("EXDATE:{}".format(exdate.format(dtut_format, formatter='alternative')))

    res = item_hsh['rrulestr'] = "\n".join(rrulelst)
    bot = "repetition rule:\n    {}\n".format(res)
    ok, res = get_reps()
    bot += res

    return top, bot, res


deal_with['r'] = deal_with_r

def deal_with_j(at_hsh={}):
    """
    Check the current state of at_hsh regarding j and s.
    """
    if 's' in item_hsh:
        # Either a dated task or a naive or aware datetimed task
        dated = True
    else:
        # An undated task
        dated = False
    top = "job?"
    bot = "{}".format(at_keys['j'])
    lofh = at_hsh.get('j', [])
    ok, res, lastcompletion = jobs(lofh, at_hsh)
    if ok:
        item_hsh['jobs'] = res
        show = "".join(["    {}\n".format(x) for x in res])
        bot = "jobs:\n{}".format(show)
    else:
        bot = "jobs:\n{}\n".format(res)
    return top, bot, res


deal_with['j'] = deal_with_j


def str2hsh(s):
    """
    Split s on @ and & keys and return the relevant hash along with at_tups (positions of @keys in s) and at_entry (an @ key has been entered without the corresponding key, True or False) for use by check_entry.
    """
    hsh = {}

    if not s.strip():
        return hsh, [], False, [], [], False, []

    at_parts = [x.strip() for x in at_regex.split(s)]
    at_tups = []
    at_entry = False
    amp_entry = False
    amp_tups = []
    amp_parts = []
    delta = 1
    if at_parts:
        place = -1
        tmp = at_parts.pop(0)
        hsh['itemtype'] = tmp[0]
        hsh['summary'] = tmp[1:].strip()
        at_tups.append( (hsh['itemtype'], hsh['summary'], place) )
        place += delta + len(tmp)

        for part in at_parts:
            if part:
                at_entry = False
            else:
                at_entry = True
                break
            k = part[0]
            v = part[1:].strip()
            if k in ('a', 'j', 'r'):
                # there can be more than one entry for these keys
                hsh.setdefault(k, []).append(v)
            else:
                hsh[k] = v
            at_tups.append( (k, v, place) )
            place += delta + len(part)

    for key in ['r', 'j']:
        if key not in hsh: continue
        lst = []
        amp_tups = []
        amp_entry = False
        for part in hsh[key]:  # an individual @r or @j entry
            amp_hsh = {}
            amp_parts = [x.strip() for x in amp_regex.split(part)]
            if amp_parts:
                amp_hsh[key] = "".join(amp_parts.pop(0))
                # k = amp_part
                for part in amp_parts:  # the & keys and values for the given entry
                    if part:
                        amp_entry = False
                    else:
                        amp_entry = True
                        break
                    # if len(part) < 2:
                    #     continue
                    k = part[0]
                    v = part[1:].strip()
                    if v in ["''", '""']:
                        # don't add if the value was either '' or ""
                        pass
                    elif key == 'r' and k in ['M', 'e', 'm', 'w']:
                        # make these lists
                        amp_hsh[k] = comma_regex.split(v)
                    elif k == 'a':
                        amp_hsh.setdefault(k, []).append(v)
                    else:
                        amp_hsh[k] = v
                    amp_tups.append( (k, v, place) )
                    # place += 2 + len(part)
                lst.append(amp_hsh)
        hsh[key] = lst
        # if 'u' in hsh: 
        #     # delegated
        #     hsh['summary'] = f"[{hsh['u']}] {hsh['summary']}"

    return hsh, at_tups, at_entry, at_parts, amp_tups, amp_entry, amp_parts


def check_entry(s, cursor_pos):
    """
    Process 's' as the current entry with the cursor at cursor_pos and return the relevant ask and reply prompts.
    """
    hsh, at_tups, at_entry, at_parts, amp_tups, amp_entry, amp_parts = str2hsh(s)

    ask = ('say', '')
    reply = ('say', '\n')
    if not at_tups:
        ask = ('say', type_prompt)
        reply = ('say', item_types)
        return ask, reply

    # itemtype, summary, end = at_tups.pop(0)
    itemtype, summary, end = at_tups[0]
    act_key = act_val = amp_key = ''

    if itemtype in type_keys:
        for tup in at_tups:
            if tup[-1] < cursor_pos:
                act_key = tup[0]
                act_val = tup[1]
            else:
                break

        if at_entry:
            ask =  ('say', "{} @keys:".format(type_keys[itemtype]))
            current_required = ["@{} {}".format(x, at_keys[x]) for x in required[itemtype] if x not in hsh]
            reply_str = ""
            if current_required:
                reply_str += "Required: {}\n".format(", ".join(current_required))
            current_allowed = ["@{} {}".format(x, at_keys[x]) for x in allowed[itemtype] if x not in hsh or x in 'ajr']
            if current_allowed:
                reply_str += "Allowed: {}\n".format(", ".join(current_allowed))
            reply = ('say', reply_str)
        elif act_key:
            if act_key in at_keys:
                ask = ('say', "{0}?".format(at_keys[act_key]))

            else:
                ask =  ('say', "{} @keys:".format(type_keys[itemtype]))

            if act_key == itemtype:
                ask = ('say', "{} summary:".format(type_keys[itemtype]))
                reply = ('say', 'Enter the summary for the {} followed, optionally, by @key and value pairs\n'.format(type_keys[itemtype]))

            else:
                ok, res = check_requires(act_key, hsh)
                if not ok:
                    ask = ('say', '{0}'.format(at_keys[act_key]))
                    reply = res


                elif act_key in allowed[itemtype]:

                    if amp_entry:
                        ask = ('say', "&key for @{}?".format(act_key))
                        reply =  ('say', "Allowed: {}\n".format(", ".join(["&{} {}".format(key, amp_keys[act_key][key]) for key in amp_keys[act_key]])))
                    elif act_key in deal_with:
                        top, bot, obj = deal_with[act_key](hsh)
                        ask = ('say', top)
                        reply = ('say', "{}\n".format(bot))
                    else:
                        ask = ('say', "{0}?".format(at_keys[act_key]))
                else:
                    reply = ('warn', "@{0} is not allowed for item type '{1}'\n".format(act_key, itemtype))
        else:
            reply = ('warn', 'no act_key')

    else:
        ask = ('say', type_prompt)
        reply = ('warn', u"invalid item type character: '{0}'\n".format(itemtype))

    if 'summary' in hsh:
        item_hsh['summary'] = hsh['summary']

    # for testing and debugging:1
    if testing:
        reply = (reply[0], reply[1] + "\nat_entry {0} {1}: {2}; pos {3}\namp_entry: {4}: {5}\n{6}\n{7}\n{8}\n{9}".format(at_entry, act_key, act_val, cursor_pos,  amp_entry, amp_key, at_tups, at_parts, hsh, item_hsh))

    return ask, reply


def parse_datetime(s, z=None):
    """
    's' will have the format 'datetime string' Return a 'date' object if the parsed datetime is exactly midnight. Otherwise return a naive datetime object if 'z == float' or an aware datetime object converting to UTC using tzlocal if z == None and using the timezone specified in z otherwise.
    >>> dt = parse_datetime("2015-10-15 2p")
    >>> dt[1]
    <Pendulum [2015-10-15T18:00:00+00:00]>
    >>> dt = parse_datetime("2015-10-15")
    >>> dt[1]
    <Pendulum [2015-10-15T00:00:00+00:00]>

    To get a datetime for midnight, schedule for 1 second later and note that the second is removed from the datetime:
    >>> dt = parse_datetime("2015-10-15 00:00:01")
    >>> dt[1]
    <Pendulum [2015-10-15T04:00:01+00:00]>
    >>> dt = parse_datetime("2015-10-15 2p", "float")
    >>> dt[1]
    <Pendulum [2015-10-15T14:00:00+00:00]>
    >>> dt[1].tzinfo
    <TimezoneInfo [Factory, -00, +00:00:00, STD]>
    >>> dt = parse_datetime("2015-10-15 2p", "US/Pacific")
    >>> dt
    ('aware', <Pendulum [2015-10-15T21:00:00+00:00]>, 'US/Pacific')
    >>> dt[1].tzinfo
    <TimezoneInfo [UTC, GMT, +00:00:00, STD]>
    """
    if z is None:
        tzinfo = 'local'
        ok = 'aware'
    elif z == 'float':
        tzinfo = 'Factory'
        ok = 'naive'
    else:
        tzinfo = z
        ok = 'aware'

    try:
        res = parse(s, tz=tzinfo)
        if ok ==  'aware':
            tz = res.format("zz", formatter='alternative')

    except:
        return False, "Invalid date-time: '{}'".format(s), z
    else:
        if (res.hour, res.minute, res.second, res.microsecond) == (0, 0, 0, 0):
            return 'date', res.replace(tzinfo='Factory'), z
        elif ok == 'aware':
            return ok, res.in_timezone('UTC'), z
        else:
            return ok, res, z

def timestamp(arg):
    """
    Fuzzy parse a datetime string and return the YYYYMMDDTHHMM formatted version.
    >>> timestamp("6/16/16 4p")
    (True, <Pendulum [2016-06-16T16:00:00+00:00]>)
    >>> timestamp("13/16/16 2p")
    (False, 'invalid date-time: 13/16/16 2p')
    """
    if type(arg) is pendulum.Pendulum:
        return True, arg
    try:
        # res = parse(arg).strftime(ETMFMT)
        res = parse(arg)
    except:
        return False, 'invalid date-time: {}'.format(arg)
    return True, res


def timestamp_list(arg, typ=None):
    if type(arg) == str:
        try:
            args = [x.strip() for x in arg.split(",")]
        except:
            return False, '{}'.format(arg)
    elif type(arg) == list:
        try:
            args = [str(x).strip() for x in arg]
        except:
            return False, '{}'.format(arg)
    else:
        return False, '{}'.format(arg)

    tmp = []
    msg = []
    for p in args:
        ok, res = format_datetime(p, typ)
        if ok:
            tmp.append(res)
        else:
            msg.append(res)
    if msg:
        return False, "{}".format(", ".join(msg))
    else:
        return True, tmp

def format_datetime(obj):
    """
    >>> format_datetime(parse_datetime("20160710T1730")[1])
    (True, 'Sun Jul 10 2016 5:30PM EDT')
    >>> format_datetime(parse_datetime("2015-07-10 5:30p", "float")[1])
    (True, 'Fri Jul 10 2015 5:30PM')
    >>> format_datetime(parse_datetime("20160710")[1])
    (True, 'Sun Jul 10 2016')
    >>> format_datetime("20160710T1730")
    (False, 'The argument must be a pendulum date or datetime.')
    """
    if type(obj) == datetime:
        obj = pendulum.instance(obj)
    if type(obj) == pendulum.pendulum.Pendulum: 
        if obj.tzinfo.abbrev == '-00':
            # naive
            if (obj.hour, obj.minute, obj.second, obj.microsecond) == (0, 0, 0, 0):
                # date
                return True, format(obj.format("ddd MMM D YYYY", formatter='alternative'))
            else:
                # naive datetime
                return True, format(obj.format("ddd MMM D YYYY h:mmA", formatter='alternative'))
        else:
            # aware
            return True, format(obj.in_timezone('local').format("ddd MMM D YYYY h:mmA z", formatter='alternative'))

    elif type(obj) == pendulum.pendulum.Date:
        return True, format(obj.format("ddd MMM D YYYY", formatter='alternative'))

    else:
        return False, "The argument must be a pendulum date or datetime."

def format_datetime_list(obj_lst):
    ret = ", ".join([format_datetime(x)[1] for x in obj_lst])
    return ret

def format_interval(obj):
    """
    >>> td = pendulum.interval(weeks=1, days=2, hours=3, minutes=27)
    >>> format_interval(td)
    '1w2d3h27m'
    """
    try:
        until =[]
        if obj.weeks:
            until.append(f"{obj.weeks}w")
        if obj.remaining_days:
            until.append(f"{obj.remaining_days}d")
        if obj.hours:
            until.append(f"{obj.hours}h")
        if obj.minutes:
            until.append(f"{obj.minutes}m")
        if not until:
            until.append("0m")
        ret = "".join(until)
        return "".join(until)
    except Exception as e:
        print('format_interval', e)
        print(obj)

def format_interval_list(obj_lst):
    try:
        ret = ", ".join([format_interval(x) for x in obj_lst])
        return ret
    except Exception as e:
        print('format_interval_list', e)
        print(obj_lst)




period_regex = re.compile(r'(([+-]?)(\d+)([wdhm]))+?')
threeday_regex = re.compile(r'(MON|TUE|WED|THU|FRI|SAT|SUN)', re.IGNORECASE)
anniversary_regex = re.compile(r'!(\d{4})!')

period_hsh = dict(
    z=pendulum.Interval(seconds=0),
    m=pendulum.Interval(minutes=1),
    h=pendulum.Interval(hours=1),
    d=pendulum.Interval(days=1),
    w=pendulum.Interval(weeks=1),
        )

def parse_interval(s):
    """\
    Take a period string and return a corresponding pendulum interval.
    Examples:
        parse_interval('-2w3d4h5m')= Interval(weeks=-2,days=3,hours=4,minutes=5)
        parse_interval('1h30m') = Interval(hours=1, minutes=30)
        parse_interval('-10m') = Interval(minutes=10)
    where:
        w: weeks
        d: days
        h: hours
        m: minutes

    >>> 3*60*60+5*60
    11100
    >>> parse_interval("2d-3h5m")[1]
    <Interval [1 day 21 hours 5 minutes]>
    >>> pendulum.create(2015, 10, 15, 9, 0, tz='local') + parse_interval("-25m")[1]
    <Pendulum [2015-10-15T08:35:00-04:00]>
    >>> pendulum.create(2015, 10, 15, 9, 0) + parse_interval("1d")[1]
    <Pendulum [2015-10-16T09:00:00+00:00]>
    >>> pendulum.create(2015, 10, 15, 9, 0) + parse_interval("1w-2d+3h")[1]
    <Pendulum [2015-10-20T12:00:00+00:00]>
    """
    td = period_hsh['z']

    m = period_regex.findall(s)
    if not m:
        return False, "Invalid period '{0}'".format(s)
    for g in m:
        if g[1] == '-':
            num = -int(g[2])
        else:
            num = int(g[2])
        td += num * period_hsh[g[3]]
    return True, td

def setup_logging(level, dir=None):
    """
    Setup logging configuration. Override root:level in
    logging.yaml with default_level.
    """
    global etmdir
    etmdir = dir
    if etmdir:
        etmdir = os.path.normpath(etmdir)
    else:
        etmdir = os.path.normpath(os.path.join(os.path.expanduser("~/etm-mvc")))


    if not os.path.isdir(etmdir):
        # root_logger = logging.getLogger()
        # root_logger.disabled = True
        return

    log_levels = {
        1: logging.DEBUG,
        2: logging.INFO,
        3: logging.WARN,
        4: logging.ERROR,
        5: logging.CRITICAL
    }

    if level in log_levels:
        loglevel = log_levels[level]
    else:
        loglevel = log_levels[3]

    # if we get here, we have an existing etmdir
    logfile = os.path.normpath(os.path.abspath(os.path.join(etmdir, "etm.log")))

    config = {'disable_existing_loggers': False,
              'formatters': {'simple': {
                  'format': '--- %(asctime)s - %(levelname)s - %(module)s.%(funcName)s\n    %(message)s'}},
              'handlers': {
                    'file': {
                        'backupCount': 5,
                        'class': 'logging.handlers.TimedRotatingFileHandler',
                        'encoding': 'utf8',
                        'filename': logfile,
                        'formatter': 'simple',
                        'level': loglevel,
                        'when': 'midnight',
                        'interval': 1}
              },
              'loggers': {
                  'etmmv': {
                    'handlers': ['file'],
                    'level': loglevel,
                    'propagate': False}
              },
              'root': {
                  'handlers': ['file'],
                  'level': loglevel},
              'version': 1}
    logging.config.dictConfig(config)
    logger.info('logging at level: {0}\n    logging to file: {1}'.format(loglevel, logfile))


sys_platform = platform.system()
mac = sys.platform == 'darwin'
if sys_platform in ('Windows', 'Microsoft'):
    windoz = True
    from time import clock as timer
else:
    windoz = False
    from time import time as timer


class TimeIt(object):
    def __init__(self, loglevel=1, label=""):
        self.loglevel = loglevel
        self.label = label
        msg = "{0} timer started; loglevel: {1}".format(self.label, self.loglevel)
        if self.loglevel == 1:
            logger.debug(msg)
        elif self.loglevel == 2:
            logger.info(msg)
        elif self.loglevel == 3:
            logger.warn(msg)
        self.start = timer()

    def stop(self, *args):
        self.end = timer()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        msg = "{0} timer stopped; elapsed time: {1} milliseconds".format(self.label, self.msecs)
        if self.loglevel == 1:
            logger.debug(msg)
        elif self.loglevel == 2:
            logger.info(msg)
        elif self.loglevel == 3:
            logger.warn(msg)



def wrap(txt, indent=3, width=shutil.get_terminal_size()[0]):
    """
    Wrap text to terminal width using indent spaces before each line.
    >>> txt = "Now is the time for all good men to come to the aid of their country. " * 5
    >>> res = wrap(txt, 4, 60)
    >>> print(res)
    Now is the time for all good men to come to the aid of
        their country. Now is the time for all good men to
        come to the aid of their country. Now is the time
        for all good men to come to the aid of their
        country. Now is the time for all good men to come
        to the aid of their country. Now is the time for
        all good men to come to the aid of their country.
    """
    # width, rows = shutil.get_terminal_size()
    para = [textwrap.dedent(x).strip() for x in txt.split('\n') if x.strip()]
    tmp = []
    first = True
    for p in para:
        if first:
            initial_indent = ''
            first = False
        else:
            initial_indent = ' '*indent
        tmp.append(textwrap.fill(p, initial_indent=initial_indent, subsequent_indent=' '*indent, width=width-indent-1))
    return "\n".join(tmp)


def set_summary(s, dt=pendulum.Pendulum.now()):
    """
    Replace the anniversary string in s with the ordinal represenation of the number of years between the anniversary string and dt.
    >>> set_summary('!1944! birthday', pendulum.Pendulum(2017, 11, 19))
    '73rd birthday'
    >>> set_summary('!1978! anniversary', pendulum.Pendulum(2017, 11, 19))
    '39th anniversary'
    """
    if not dt:
        dt = pendulum.Pendulum.now()

    mtch = anniversary_regex.search(s)
    retval = s
    if mtch:
        startyear = mtch.group(1)
        numyrs = anniversary_string(startyear, dt.year)
        retval = anniversary_regex.sub(numyrs, s)
    return retval


# TODO: an international version for this?
SUFFIXES = {0: 'th', 1: 'st', 2: 'nd', 3: 'rd'}

def ordinal(num):
    """
    Append appropriate suffix to integers for ordinal representation.
    E.g., 1 -> 1st, 2 -> 2nd and so forth.
    >>> ordinal(3)
    '3rd'
    >>> ordinal(21)
    '21st'
    >>> ordinal(40)
    '40th'
    >>> ordinal(82)
    '82nd'
    """
    if num < 4 or (num > 20 and num % 10 < 4):
        suffix = SUFFIXES[num % 10]
    else:
        suffix = SUFFIXES[0]
    return "{0}{1}".format(str(num), suffix)

def anniversary_string(startyear, endyear):
    """
    Compute the integer difference between startyear and endyear and
    append the appropriate English suffix.
    """
    return ordinal(int(endyear) - int(startyear))


def one_or_more(s):
    if type(s) is list:
        return ", ".join([str(x) for x in s])
    else:
        return str(s)


def string(arg, typ=None):
    try:
        arg = str(arg)
    except:
        if typ:
            return False, "{}: {}".format(typ, arg)
        else:
            return False, "{}".format(arg)
    return True, arg

def string_list(arg, typ=None):
    """
    """
    if arg == '':
        args = []
    elif type(arg) == str:
        try:
            args = [x.strip() for x in arg.split(",")]
        except:
            return False, '{}: {}'.format(typ, arg)
    elif type(arg) == list:
        try:
            args = [str(x).strip() for x in arg]
        except:
            return False, '{}: {}'.format(typ, arg)
    else:
        return False, '{}: {}'.format(typ, arg)
    bad = []
    msg = []
    ret = []
    for arg in args:
        ok, res = string(arg, None)
        if ok:
            ret.append(res)
        else:
            msg.append(res)
    if msg:
        if typ:
            return False, "{}: {}".format(typ, "; ".join(msg))
        else:
            return False, "{}".format("; ".join(msg))
    else:
        return True, ret

def integer(arg, min, max, zero, typ=None):
    """
    :param arg: integer
    :param min: minimum allowed or None
    :param max: maximum allowed or None
    :param zero: zero not allowed if False
    :param typ: label for message
    :return: (True, integer) or (False, message)
    >>> integer(-2, -10, 8, False, 'integer_test')
    (True, -2)
    >>> integer(-2, 0, 8, False, 'integer_test')
    (False, 'integer_test: -2 is less than the allowed minimum')
    """
    msg = ""
    try:
        arg = int(arg)
    except:
        if typ:
            return False, "{}: {}".format(typ, arg)
        else:
            return False, arg
    if min is not None and arg < min:
        msg = "{} is less than the allowed minimum".format(arg)
    elif max is not None and arg > max:
        msg = "{} is greater than the allowed maximum".format(arg)
    elif not zero and arg == 0:
        msg = "0 is not allowed"
    if msg:
        if typ:
            return False, "{}: {}".format(typ, msg)
        else:
            return False, msg
    else:
        return True, arg


def integer_list(arg, min, max, zero, typ=None):
    """
    :param arg: integer
    :param min: minimum allowed or None
    :param max: maximum allowed or None
    :param zero: zero not allowed if False
    :param typ: label for message
    :return: (True, list of integers) or (False, messages)
    >>> integer_list([-13, -10, 0, "2", 27], -12, +20, True, 'integer_list test')
    (False, 'integer_list test: -13 is less than the allowed minimum; 27 is greater than the allowed maximum')
    >>> integer_list([0, 1, 2, 3, 4], 1, 3, True, "integer_list test")
    (False, 'integer_list test: 0 is less than the allowed minimum; 4 is greater than the allowed maximum')
    >>> integer_list("-1, 1, two, 3", None, None, True, "integer_list test")
    (False, 'integer_list test: -1, 1, two, 3')
    >>> integer_list([1, "2", 3], None, None, True, "integer_list test")
    (True, [1, 2, 3])
    """
    if type(arg) == str:
        try:
            args = [int(x) for x in arg.split(",")]
        except:
            if typ:
                return False, '{}: {}'.format(typ, arg)
            else:
                return False, arg
    elif type(arg) == list:
        try:
            args = [int(x) for x in arg]
        except:
            if typ:
                return False, '{}: {}'.format(typ, arg)
            else:
                return False, arg
    elif type(arg) == int:
        args = [arg]
    bad = []
    msg = []
    ret = []
    for arg in args:
        ok, res = integer(arg, min, max, zero, None)
        if ok:
            ret.append(res)
        else:
            msg.append(res)
    if msg:
        if typ:
            return False, "{}: {}".format(typ, "; ".join(msg))
        else:
            return False, "; ".join(msg)
    else:
        return True, ret


def title(arg):
    return string(arg, 'title')


entry_tmpl = """\
{%- set title -%}\
{{ h.itemtype }} {{ h.summary }}\
{% if 's' in h %}{{ " @s {}".format(dt2str(h['s'])[1]) }}{% endif %}\
{%- for k in ['e', 'z'] -%}\
{%- if k in h %} @{{ k }} {{ h[k] }}{% endif %}\
{%- endfor %}\
{%- endset %}\
{{ wrap(title) }}
{% if 'a' in h %}\
{%- set alerts %}\
{%- for x in h['a'] %}{{ "@a {}: {} ".format(inlst2str(x[0]), ", ".join(x[1:])) }} {% endfor %}\
{% endset %}\
{{ wrap(alerts) }}
{% endif %}\
{% set index %}\
{% for k in ['c', 'i'] %}\
{% if k in h %} @{{ k }} {{ h[k] }}{% endif %}\
{% endfor -%}\
{% endset -%}
{{ wrap(index) }}\
{%- if 't' in h %}{{ " @t {}".format(", ".join(h['t'])) }} {% endif %}\
{% set ns = namespace(found=false) %}\
{% set location %}\
{%- for k in ['l', 'm', 'n', 'g', 'u', 'x', 'f', 'p'] -%}\
{%- if k in h %}@{{ k }} {{ h[k] }}{% set ns.found = true %} {% endif %}\
{% endfor %}\
{% endset %}\
{% if ns.found %}
{{ wrap(location) }}{% endif -%}\
{%- if 'r' in h %}\
{%- for x in h['r'] -%}\
{%- set rrule -%}\
{{ x['f'] }}\
{%- for k in ['i', 'c', 's', 'u', 'M', 'm', 'n', 'w', 'h', 'E'] -%}\
{%- if k in x %} {{ "&{} {}".format(k, one_or_more(x[k])) }}{%- endif %}\
{%- endfor %}\
{%- endset %}
@r {{ wrap(rrule) }}
{%- endfor %}\
{% if 'o' in h %}
@o {{ h['o'] }}{% endif -%}\
{%- endif -%}\
{% for k in ['+', '-', 'h'] -%}
{%- if k in h and h[k] %}
@{{ k }} {{ wrap(dtlst2str(h[k])) }}
{%- endif -%}\
{%- endfor %}\
{% if 'd' in h %}
@d {{ wrap(h['d']) }} \
{% endif -%}
{%- if 'j' in h %}
{%- for x in h['j'] %}
{%- set job -%}
{{ x['j'] }}\
{%- for k in ['s', 'b', 'd', 'e', 'f', 'l', 'i', 'p'] -%}
{%- if k in x and x[k] %} {{ "&{} {}".format(k, one_or_more(x[k])) }}{% endif %}\
{%- endfor %}
{%- if 'a' in x %}\
{%- for a in x['a'] %} &a {{ "&a {}: {}".format(inlst2str(a[0]), ", ".join(a[1:])) }}{% endfor %}\
{%- endif %}\
{%- endset %}
@j {{ wrap(job) }}\
{%- endfor %}\
{%- endif -%}
"""

jinja_entry_template = Template(entry_tmpl)
jinja_entry_template.globals['dt2str'] = format_datetime
jinja_entry_template.globals['in2str'] = format_interval
jinja_entry_template.globals['dtlst2str'] = format_datetime_list
jinja_entry_template.globals['inlst2str'] = format_interval_list
jinja_entry_template.globals['one_or_more'] = one_or_more
# jinja_entry_template.globals['set_summary'] = set_summary
jinja_entry_template.globals['wrap'] = wrap

def beginby(arg):
    return integer(arg, 1, None, False, 'beginby')


def location(arg):
    return string(arg, 'location')


def uid(arg):
    return string(arg, 'uid')


def description(arg):
    return string(arg, 'description')


def extent(arg):
    return parse_interval(arg)


def history(arg):
    """
    Return a list of properly formatted completions.
    >>> history("4/1/2016 2p")
    (True, [<Pendulum [2016-04-01T18:00:00+00:00]>])
    >>> history(["4/31 2p", "6/1 7a"])
    (False, "Invalid date-time: '4/31 2p'")
    """
    if type(arg) != list:
        arg = [arg]
    msg = []
    tmp = []
    for comp in arg:
        ok, res, tz = parse_datetime(comp)
        if ok:
            tmp.append(res)
        else:
            msg.append(res)
    if msg:
        return False, ', '.join(msg)
    else:
        return True, tmp


def priority(arg):
    """
    >>> priority(0)
    (False, 'priority: an integer priority numbers from 1 (highest), to 9 (lowest)')
    """

    prioritystr = "priority: an integer priority numbers from 1 (highest), to 9 (lowest)"

    if arg:
        ok, res = integer(arg, 1, 9, False, "priority")
        if ok:
            return True, res
        else:
            return False, "invalid priority: {}. Required for {}".format(res, prioritystr)
    else:
        return False, prioritystr


#####################################
### begin rrule setup ###############
#####################################


def easter(arg):
    """
    byeaster; integer or sequence of integers numbers of days before, < 0,
    or after, > 0, Easter.
    >>> easter(0)
    (True, [0])
    >>> easter([-364, -30, "45", 260])
    (True, [-364, -30, 45, 260])
    """
    easterstr = "easter: a comma separated list of integer numbers of days before, < 0, or after, > 0, Easter."

    if arg or arg == 0:
        ok, res = integer_list(arg, None, None, True)
        if ok:
            return True, res
        else:
            return False, "invalid easter: {}. Required for {}".format(res, easterstr)
    else:
        return False, easterstr


def frequency(arg):
    """
    repetition frequency: character in (y)early, (m)onthly, (w)eekly, (d)aily, (h)ourly
    or mi(n)utely.
    >>> frequency('d')[0]
    True
    >>> frequency('z')[0]
    False
    """

    freq = [x for x in rrule_freq]
    freqstr = "(y)early, (m)onthly, (w)eekly, (d)aily, (h)ourly or mi(n)utely."
    if arg in freq:
        return True, arg
    elif arg:
        return False, "invalid frequency: {} not in {}".format(arg, freqstr)
    else:
        return False, "repetition frequency: character from {}".format(freqstr)

def interval(arg):
    """
    interval (positive integer, default = 1) E.g, with frequency
    w, interval 3 would repeat every three weeks.
    >>> interval("two")
    (False, 'invalid interval: two. Required for interval: a positive integer. E.g., with frequency w, interval 3 would repeat every three weeks.')
    >>> interval(27)
    (True, 27)
    >>> interval([1, 2])
    (False, 'invalid interval: [1, 2]. Required for interval: a positive integer. E.g., with frequency w, interval 3 would repeat every three weeks.')
    """

    intstr = "interval: a positive integer. E.g., with frequency w, interval 3 would repeat every three weeks."

    if arg:
        ok, res = integer(arg, 1, None, False)
        if ok:
            return True, res
        else:
            return False, "invalid interval: {}. Required for {}".format(res, intstr)
    else:
        return False, intstr


def setpos(arg):
    """
    bysetpos (non-zero integer or sequence of non-zero integers). When
    multiple dates satisfy the rule, take the dates from this/these positions
    in the list, e.g, &s 1 would choose the first element and &s -1 the last.
    >>> setpos(1)
    (True, [1])
    >>> setpos(["-1", 0])
    (False, 'setpos: 0 is not allowed')
    """
    return integer_list(arg, None, None, False, "setpos")


def count(arg):
    """
    count (positive integer) Include no more than this number of repetitions.
    >>> count('three')
    (False, 'invalid count: three. Required for count: a positive integer. Include no more than this number of repetitions.')
    >>> count('3')
    (True, 3)
    >>> count([2, 3])
    (False, 'invalid count: [2, 3]. Required for count: a positive integer. Include no more than this number of repetitions.')
    """

    countstr = "count: a positive integer. Include no more than this number of repetitions."

    if arg:
        ok, res = integer(arg, 1, None, False )
        if ok:
            return True, res
        else:
            return False, "invalid count: {}. Required for {}".format(res, countstr)
    else:
        return False, countstr


def weekdays(arg):
    """
    byweekday (English weekday abbreviation SU ... SA or sequence of such).
    Use, e.g., 3WE for the 3rd Wednesday or -1FR, for the last Friday in the
    month.
    >>> weekdays(" ")
    (False, 'weekdays: a comma separated list of English weekday abbreviations from SU, MO, TU, WE, TH, FR, SA. Prepend an integer to specify a particular weekday in the month. E.g., 3WE for the 3rd Wednesday or -1FR, for the last Friday in the month.')
    >>> weekdays("-2mo, 3tU")
    (True, ['-2MO', '3TU'])
    >>> weekdays(["5Su", "1SA"])
    (False, 'invalid weekdays: 5SU')
    >>> weekdays('3FR, -1M')
    (False, 'considering weekdays: -1M')
    """
    wkdays = ["{0}{1}".format(n, d) for d in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']
        for n in ['-4', '-3', '-2', '-1', '', '1', '2', '3', '4']]
    if type(arg) == list:
        args = [x.strip().upper() for x in arg if x.strip()]
    elif arg:
        args = [x.strip().upper() for x in arg.split(",") if x.strip()]
    else:
        args = None
    if args:
        bad = [x for x in args]
        for x in args:
            for y in wkdays:
                if x in bad and y.startswith(x):
                    bad.remove(x)
        # bad = [x for x in args if x and x not in wkdays]
        if bad:
            return False, "invalid weekdays: {}".format(", ".join(bad))
        else:
            invalid = [x for x in args if x not in wkdays]
            if invalid:
                return False, "considering weekdays: {}".format(", ".join(invalid))
            else:
                return True, args
    else:
        return False, "weekdays: a comma separated list of English weekday abbreviations from SU, MO, TU, WE, TH, FR, SA. Prepend an integer to specify a particular weekday in the month. E.g., 3WE for the 3rd Wednesday or -1FR, for the last Friday in the month."


def weeks(arg):
    """
    byweekno (1, 2, ..., 53 or a sequence of such integers)
    >>> weeks([0, 1, 5, 54])
    (False, 'invalid weeks: 0 is not allowed; 54 is greater than the allowed maximum. Required for weeks: a comma separated list of integer week numbers from 1, 2, ..., 53')
    """

    weeksstr = "weeks: a comma separated list of integer week numbers from 1, 2, ..., 53"

    if arg:
        ok, res = integer_list(arg, 0, 53, False)
        if ok:
            return True, res
        else:
            return False, "invalid weeks: {}. Required for {}".format(res, weeksstr)
    else:
        return False, weeksstr


def months(arg):
    """
    bymonth (1, 2, ..., 12 or a sequence of such integers)
    >>> months([0, 2, 7, 13])
    (False, 'invalid months: 0 is not allowed; 13 is greater than the allowed maximum. Required for months: a comma separated list of integer month numbers from 1, 2, ..., 12')
    """

    monthsstr = "months: a comma separated list of integer month numbers from 1, 2, ..., 12"

    if arg:
        ok, res = integer_list(arg, 0, 12, False, "")
        if ok:
            return True, res
        else:
            return False, "invalid months: {}. Required for {}".format(res, monthsstr)
    else:
        return False, monthsstr


def monthdays(arg):
    """
    >>> monthdays([0, 1, 26, -1, -2])
    (False, 'invalid monthdays: 0 is not allowed. Required for monthdays: a comma separated list of integer month days from  (1, 2, ..., 31. Prepend a minus sign to count backwards from the end of the month. E.g., use  -1 for the last day of the month.')
    """

    monthdaysstr = "monthdays: a comma separated list of integer month days from  (1, 2, ..., 31. Prepend a minus sign to count backwards from the end of the month. E.g., use  -1 for the last day of the month."

    if arg:
        ok, res = integer_list(arg, -31, 31, False, "")
        if ok:
            return True, res
        else:
            return False, "invalid monthdays: {}. Required for {}".format(res, monthdaysstr)
    else:
        return False, monthdaysstr

def hours(arg):
    """
    >>> hours([0, 6, 12, 18, 24])
    (False, 'invalid hours: [0, 6, 12, 18, 24]. Required for hours: a comma separated of integer hour numbers from 0, 1,  ..., 23.')
    >>> hours([0, "1"])
    (True, [0, 1])
    """

    hoursstr = "hours: a comma separated of integer hour numbers from 0, 1,  ..., 23."

    if arg or arg == 0:
        ok, res = integer_list(arg, 0, 23, True, "")
        if ok:
            return True, res
        else:
            return False, "invalid hours: {}. Required for {}".format(arg, hoursstr)
    else:
        return False, hoursstr


def minutes(arg):
    """
    byminute (0 ... 59 or a sequence of such integers)
    >>> minutes(27)
    (True, [27])
    >>> minutes([0, 60])
    (False, 'invalid minutes: 60 is greater than the allowed maximum. Required for minutes: a comma separated of integer hour numbers from 0, 1, ..., 59.')
    """

    minutesstr = "minutes: a comma separated of integer hour numbers from 0, 1, ..., 59."

    if arg or arg == 0:
        ok, res = integer_list(arg, 0, 59, True, "")
        if ok:
            return True, res
        else:
            return False, "invalid minutes: {}. Required for {}".format(res, minutesstr)
    else:
        return False, minutesstr



rrule_methods = dict(
    r=frequency,
    i=interval,
    f=frequency,
    s=setpos,
    c=count,
    u=format_datetime,
    M=months,
    m=monthdays,
    W=weeks,
    w=weekdays,
    h=hours,
    n=minutes,
    E=easter,
)

rrule_freq = {
    'y': 0,     #'YEARLY',
    'm': 1,     #'MONTHLY',
    'w': 2,     #'WEEKLY',
    'd': 3,     #'DAILY',
    'h': 4,     #'HOURLY',
    'n': 5,     #'MINUTELY',
}

rrule_weekdays = dict(
        MO = MO,
        TU = TU,
        WE = WE,
        TH = TH,
        FR = FR,
        SA = SA,
        SU = SU
        )

# Note: 'r' (FREQ) is not included in the following.
rrule_name = {
    'i': 'interval',  # positive integer
    'c': 'count',  # integer
    's': 'bysetpos',  # integer
    'u': 'until',  # unicode
    'M': 'bymonth',  # integer 1...12
    'm': 'bymonthday',  # positive integer
    'W': 'byweekno',  # positive integer
    'w': 'byweekday',  # integer 0 (SU) ... 6 (SA)
    'h': 'byhour',  # positive integer
    'n': 'byminute',  # positive integer
}

rrule_keys = [x for x in rrule_name]
rrule_keys.sort()

def check_rrule(lofh):
    """
    An check_rrule hash or a sequence of such hashes.
    >>> data = {'r': ''}
    >>> check_rrule(data)
    (False, 'repetition frequency: character from (y)early, (m)onthly, (w)eekly, (d)aily, (h)ourly or mi(n)utely.')
    >>> good_data = {"M": 5, "i": 1, "m": 3, "r": "y", "w": "2SU"}
    >>> pprint(check_rrule(good_data))
    (True, [{'M': [5], 'i': 1, 'm': [3], 'r': 'y', 'w': ['2SU']}])
    >>> good_data = {"M": [5, 12], "i": 1, "m": [3, 15], "r": "y", "w": "2SU"}
    >>> pprint(check_rrule(good_data))
    (True, [{'M': [5, 12], 'i': 1, 'm': [3, 15], 'r': 'y', 'w': ['2SU']}])
    >>> bad_data = [{"M": 5, "i": 1, "m": 3, "r": "y", "w": "2SE"}, {"M": [11, 12], "i": 4, "m": [2, 3, 4, 5, 6, 7, 8], "r": "z", "w": ["TU", "-1FR"]}]
    >>> print(check_rrule(bad_data))
    (False, 'invalid weekdays: 2SE; invalid frequency: z not in (y)early, (m)onthly, (w)eekly, (d)aily, (h)ourly or mi(n)utely.')
    >>> data = [{"r": "w", "w": "TU", "h": 14}, {"r": "w", "w": "TH", "h": 16}]
    >>> pprint(check_rrule(data))
    (True,
     [{'h': [14], 'i': 1, 'r': 'w', 'w': ['TU']},
      {'h': [16], 'i': 1, 'r': 'w', 'w': ['TH']}])
    """
    msg = []
    ret = []
    if type(lofh) == dict:
        lofh = [lofh]
    for hsh in lofh:
        res = {}
        if type(hsh) != dict:
            msg.append('error: Elements must be hashes. Cannot process: "{}"'.format(hsh))
            continue
        if 'r' not in hsh:
            msg.append('error: r is required but missing')
        if 'i' not in hsh:
            res['i'] = 1
        for key in hsh.keys():
            if key not in rrule_methods:
                msg.append("error: {} is not a valid key".format(key))
            else:
                ok, out = rrule_methods[key](hsh[key])
                if ok:
                    res[key] = out
                else:
                    msg.append(out)

        if not msg:
            # l = ["RRULE:FREQ=%s" % rrule_frequency[hsh['r']]]

            # for k in rrule_keys:
            #     if k in hsh and hsh[k]:
            #         v = hsh[k]
            #         if type(v) == list:
            #             v = ",".join(map(str, v))
            #         if k == 'w':
            #             # make weekdays upper case
            #             v = v.upper()
            #             m = threeday_regex.search(v)
            #             while m:
            #                 v = threeday_regex.sub("%s" % m.group(1)[:2], v, count=1)
            #                 m = threeday_regex.search(v)
            #         l.append("%s=%s" % (rrule_names[k], v))
            # res['rrulestr'] = ";".join(l)
            ret.append(res)

    if msg:
        return False, "{}".format("; ".join(msg))
    else:
        return True, ret

def rrule_args(r_hsh):
    """
    >>> item_eg = { "s": parse('2018-03-07 8am'), "r": [ { "r": "w", "u": parse('2018-04-01 8am'), }, ], "itemtype": "*"}
    >>> item_instances(item_eg, parse('2018-03-01 12am'), parse('2018-04-01 12am'))
    [(<Pendulum [2018-03-07T08:00:00+00:00]>, None), (<Pendulum [2018-03-14T08:00:00+00:00]>, None), (<Pendulum [2018-03-21T08:00:00+00:00]>, None), (<Pendulum [2018-03-28T08:00:00+00:00]>, None)]
    >>> r_hsh = item_eg['r'][0]
    >>> rrule_args(r_hsh)
    (2, {'until': <Pendulum [2018-04-01T08:00:00+00:00]>})
    """

    # force integers
    for k in "icsMmWhm":
        if k in r_hsh:
            args = r_hsh[k]
            if not isinstance(args, list):
                args = [args]
            tmp = [int(x) for x in args]
            if len(tmp) == 1:
                r_hsh[k] = tmp[0]
            else:
                r_hsh[k] = tmp
    # fix weekdays
    if 'w' in r_hsh:
        tmp = []
        weekdays = r_hsh['w']
        if not isinstance(weekdays, list):
            weekdays = [weekdays]
        for weekday in weekdays:
            # wpart = weekday[-2:].upper()
            wpart = rrule_weekdays[weekday[-2:].upper()]
            ipart = weekday[:-2]
            if ipart:
                # tmp.append(f"{wpart}({int(ipart)})")
                tmp.append(wpart(int(ipart)))
            else:
                tmp.append(wpart)
        if len(tmp) == 1:
            r_hsh['w'] = tmp[0]
        else:
            r_hsh['w'] = tuple(tmp)
    if 'u' in r_hsh and 'c' in r_hsh:
        logger.warn(f"Warning: using both 'c' and 'u' is depreciated in {r_hsh}")
    # remove easter
    if 'E'in r_hsh:
        del r_hsh['E']
    freq = rrule_freq[r_hsh['r']]
    kwd = {rrule_name[k]: r_hsh[k] for k in r_hsh if k != 'r'}
    return freq, kwd

def item_instances(item, aft_dt, bef_dt=None):
    """
    Get instances from item falling on or after aft_dt and on or before bef_dt or, if bef_dt is None, the first instance after aft_dt. All datetimes will be returned with zero offsets.
    >>> item_eg = { "s": parse('2018-03-07 8am'), "e": pendulum.interval(days=1, hours=5), "r": [ { "r": "w", "i": 2, "u": parse('2018-04-01 8am')}], "z": "US/Eastern", "itemtype": "*" }
    >>> item_instances(item_eg, parse('2018-03-01 12am'), parse('2018-04-01 12am'))
    [(<Pendulum [2018-03-07T08:00:00+00:00]>, <Pendulum [2018-03-07T23:59:59.999999+00:00]>), (<Pendulum [2018-03-08T00:00:00+00:00]>, <Pendulum [2018-03-08T13:00:00+00:00]>), (<Pendulum [2018-03-21T08:00:00+00:00]>, <Pendulum [2018-03-21T23:59:59.999999+00:00]>), (<Pendulum [2018-03-22T00:00:00+00:00]>, <Pendulum [2018-03-22T13:00:00+00:00]>)]
    >>> item_eg['+'] = [parse("20180311T1000")]
    >>> item_eg['-'] = [parse("20180311T0800")]
    >>> item_eg['e'] = pendulum.interval(hours=2)
    >>> item_instances(item_eg, parse('2018-03-01 12am'), parse('2018-04-01 12am'))
    [(<Pendulum [2018-03-07T08:00:00+00:00]>, <Pendulum [2018-03-07T10:00:00+00:00]>), (<Pendulum [2018-03-11T10:00:00+00:00]>, <Pendulum [2018-03-11T12:00:00+00:00]>), (<Pendulum [2018-03-21T08:00:00+00:00]>, <Pendulum [2018-03-21T10:00:00+00:00]>)]
    >>> del item_eg['e']
    >>> item_instances(item_eg, parse('2018-03-07 8am'))
    [(<Pendulum [2018-03-11T10:00:00+00:00]>, None)]
    >>> del item_eg['r']
    >>> del item_eg['-']
    >>> del item_eg['+']
    >>> item_instances(item_eg, parse('2018-03-01 12am'), parse('2018-04-01 12am'))
    [(<Pendulum [2018-03-07T08:00:00+00:00]>, None)]
    """
    # FIXME only for events
    if 's' not in item:
        return []
    instances = []
    dts = item['s']
    if type(dts) == pendulum.pendulum.Date:
        # change to datetime at midnight on the same date
        dtstart = pendulum.create(year=dts.year, month=dts.month, day=dts.day, hour=0, minute=0, tz=None)
    else:
        # dtstart = dts.replace(tzinfo=None)
        dtstart = dts
        startdst = dtstart.dst()
    if 'r' in item:
        lofh = item['r']
        rset = rruleset()

        for hsh in lofh:
            freq, kwd = rrule_args(hsh)
            kwd['dtstart'] = dtstart
            try:
                rset.rrule(rrule(freq, **kwd))
            except Exception as e:
                print('Error processing:')
                print('  ', freq, kwd)
                print(e)
                print(item)
                return []

        if '-' in item:
            for dt in item['-']:
                if type(dt) == pendulum.pendulum.Date:
                    pass
                elif dt.dst() and not startdst:
                    dt = dt + dt.dst()
                elif startdst and not dt.dst():
                    dt = dt - startdst
                rset.exdate(dt)

        if '+' in item:
            for dt in item['+']:
                rset.rdate(dt)
        if bef_dt is None:
            # get the first instance after aft_dt
            instances = [pendulum.instance(rset.after(aft_dt, inc=False))]
        else:
            instances = [pendulum.instance(x) for x in rset.between(aft_dt, bef_dt, inc=True)]

    elif '+' in item:
        tmp = item['+'].append(dtstart)
        if bef_dt is None:
            instances = [x for x in tmp if (x > aft_dt)][:1]
        else:
            instances = [x for x in tmp if (x >= aft_dt and x <= bef_dt)]

    else:
        # dtstart >= aft_dt
        if bef_dt is None:
            instances = [dtstart] if dtstart > aft_dt else []
        else:
            instances = [dtstart] if aft_dt <= dtstart <= bef_dt else []

    pairs = []
    for instance in instances:
        # multidays only for events
        if item['itemtype'] == "*" and 'e' in item:
            for pair in beg_ends(instance, item['e'], item.get('z', 'local')):
                pairs.append(pair)
        elif item['itemtype'] == "-" and item.get('o', 'k') == 's':
            # drop old skip instances
            if instance >= pendulum.now(tz=item.get('z', None)):
                pairs.append((instance, None))
        else:
            pairs.append((instance, None))

    return pairs




########################
### end rrule setup ####
########################

#########################
### begin jobs setup ####
#########################

def prereqs(arg):
    """
    >>> prereqs("B, C, D")
    (True, ['B', 'C', 'D'])
    >>> prereqs("2, 3, 4")
    (True, ['2', '3', '4'])
    >>> prereqs([2, 3, 4])
    (True, ['2', '3', '4'])
    """
    if arg:
        return string_list(arg, 'prereqs')
    else:
        return True, []



undated_job_methods = dict(
    d=description,
    e=extent,
    f=timestamp,
    h=history,
    j=title,
    l=location,
    q=timestamp,
    # The last two require consideration of the whole list of jobs
    # i=id,
    p=prereqs,
)

datetime_job_methods = dict(
    # a=alert,
    b=beginby,
    # s=job_date_time
)
datetime_job_methods.update(undated_job_methods)

def task(at_hsh):
    """
    Evaluate task/job completions and update the f and s entries if appropriate 
    >>> item_eg = {"summary": "Task Group",  "s": parse('2018-03-07 8am'), "r": [ { "r": "w", "i": 2, "u": parse('2018-04-01 8am')}], "z": "US/Eastern", "itemtype": "-", 'j': [ {'j': 'Job 1', 'f': parse('2018-03-06 10am')}, {'j': 'Job 2'} ] }
    >>> pprint(task(item_eg))
    {'itemtype': '-',
     'j': [{'f': <Pendulum [2018-03-06T10:00:00+00:00]>,
            'j': 'Job 1',
            'p': [],
            'req': [],
            'status': 'f',
            'summary': 'Task Group 1/1/0: Job 1'},
           {'j': 'Job 2',
            'p': ['1'],
            'req': [],
            'status': 'a',
            'summary': 'Task Group 1/1/0: Job 2'}],
     'r': [{'i': 2, 'r': 'w', 'u': <Pendulum [2018-04-01T08:00:00+00:00]>}],
     's': <Pendulum [2018-03-07T08:00:00+00:00]>,
     'summary': 'Task Group',
     'z': 'US/Eastern'}



    Now finish the last job and note the update for h and s
    >>> item_eg = {"summary": "Task Group",  "s": parse('2018-03-07 8am'), "r": [ { "r": "w", "i": 2, "u": parse('2018-04-01 8am')}], "z": "US/Eastern", "itemtype": "-", 'j': [ {'j': 'Job 1', 'f': parse('2018-03-06 10am')}, {'j': 'Job 2', 'f': parse('2018-03-07 1pm') } ] }
    >>> pprint(task(item_eg))
    {'h': [<Pendulum [2018-03-07T13:00:00+00:00]>],
     'itemtype': '-',
     'j': [{'j': 'Job 1',
            'p': [],
            'req': [],
            'status': 'a',
            'summary': 'Task Group 0/1/1: Job 1'},
           {'j': 'Job 2',
            'p': ['1'],
            'req': ['1'],
            'status': 'w',
            'summary': 'Task Group 0/1/1: Job 2'}],
     'r': [{'i': 2, 'r': 'w', 'u': <Pendulum [2018-04-01T08:00:00+00:00]>}],
     's': [(<Pendulum [2018-03-21T08:00:00+00:00]>, None)],
     'summary': 'Task Group',
     'z': 'US/Eastern'}
    """
    if not at_hsh or at_hsh.get('itemtype', None) != '-':
        return at_hsh
    if 'j' in at_hsh:
        ok, jbs, finished = jobs(at_hsh['j'], at_hsh)
        if ok: 
            at_hsh['j'] = jbs
            if finished is not None:
                # all jobs were completed
                at_hsh['f'] = finished

    if 's' not in at_hsh:
        return at_hsh

    finished = at_hsh.get('f', None)

    if finished:
        overdue = at_hsh.get('o', 'k') 
        if overdue == 'k':
            # keep
            aft = at_hsh['s']
        elif overdue == 'r':
            # restart
            aft = at_hsh['f']
        elif overdue == 's':
            # skip
            aft = pendulum.now(tz=at_hsh.get('z', None))
        due = item_instances(at_hsh, aft)
        if due:
            # we have another instance
            at_hsh['s'] = due
            at_hsh.setdefault('h', []).append(at_hsh['f'])
            del at_hsh['f']
    return(at_hsh)



def jobs(lofh, at_hsh={}):
    """
    Process the job hashes in lofh
    >>> data = [{'j': 'Job One', 'a': '2d: m', 'b': 2, 'f': parse('6/20/18 12p')}, {'j': 'Job Two', 'a': '1d: m', 'b': 1}, {'j': 'Job Three', 'a': '6h: m'}]
    >>> pprint(jobs(data))
    (True,
     [{'f': <Pendulum [2018-06-20T12:00:00+00:00]>,
       'j': 'Job One',
       'p': [],
       'req': [],
       'status': 'f',
       'summary': ' 1/1/1: Job One'},
      {'j': 'Job Two',
       'p': ['1'],
       'req': [],
       'status': 'a',
       'summary': ' 1/1/1: Job Two'},
      {'j': 'Job Three',
       'p': ['2'],
       'req': ['2'],
       'status': 'w',
       'summary': ' 1/1/1: Job Three'}],
     None)
    >>> data = [{'j': 'Job One', 'a': '2d: m', 'b': 2, 'f': parse('6/20/18 12p')}, {'j': 'Job Two', 'a': '1d: m', 'b': 1, 'f': parse('6/21/18 12p')}, {'j': 'Job Three', 'a': '6h: m'}]
    >>> pprint(jobs(data))
    (True,
     [{'f': <Pendulum [2018-06-20T12:00:00+00:00]>,
       'j': 'Job One',
       'p': [],
       'req': [],
       'status': 'f',
       'summary': ' 2/1/0: Job One'},
      {'f': <Pendulum [2018-06-21T12:00:00+00:00]>,
       'j': 'Job Two',
       'p': ['1'],
       'req': [],
       'status': 'f',
       'summary': ' 2/1/0: Job Two'},
      {'j': 'Job Three',
       'p': ['2'],
       'req': [],
       'status': 'a',
       'summary': ' 2/1/0: Job Three'}],
     None)
    >>> data = [{'j': 'Job One', 'a': '2d: m', 'b': 2, 'f': parse('6/20/18 12p')}, {'j': 'Job Two', 'a': '1d: m', 'b': 1, 'f': parse('6/21/18 12p')}, {'j': 'Job Three', 'a': '6h: m', 'f': parse('6/22/18 12p')}]
    >>> pprint(jobs(data))
    (True,
     [{'f': <Pendulum [2018-06-20T12:00:00+00:00]>,
       'j': 'Job One',
       'p': [],
       'req': [],
       'status': 'f',
       'summary': ' 3/0/0: Job One'},
      {'f': <Pendulum [2018-06-21T12:00:00+00:00]>,
       'j': 'Job Two',
       'p': ['1'],
       'req': ['1'],
       'status': 'f',
       'summary': ' 3/0/0: Job Two'},
      {'f': <Pendulum [2018-06-22T12:00:00+00:00]>,
       'j': 'Job Three',
       'p': ['2'],
       'req': ['2', '1'],
       'status': 'f',
       'summary': ' 3/0/0: Job Three'}],
     <Pendulum [2018-06-22T12:00:00+00:00]>)


    Now add an 'r' entry for at_hsh.
    >>> data = [{'j': 'Job One', 'a': '2d: m', 'b': 2, 'f': parse('6/20/18 12p')}, {'j': 'Job Two', 'a': '1d: m', 'b': 1, 'f': parse('6/21/18 12p')}, {'j': 'Job Three', 'a': '6h: m', 'f': parse('6/22/18 12p')}]
    >>> pprint(jobs(data, {'r': 'd'}))
    (True,
     [{'j': 'Job One',
       'p': [],
       'req': [],
       'status': 'a',
       'summary': ' 0/1/2: Job One'},
      {'j': 'Job Two',
       'p': ['1'],
       'req': ['1'],
       'status': 'w',
       'summary': ' 0/1/2: Job Two'},
      {'j': 'Job Three',
       'p': ['2'],
       'req': ['2', '1'],
       'status': 'w',
       'summary': ' 0/1/2: Job Three'}],
     <Pendulum [2018-06-22T12:00:00+00:00]>)
    """
    if 's' in at_hsh:
        job_methods = datetime_job_methods
    else:
        job_methods = undated_job_methods

    msg = []
    rmd = []
    ret = []
    req = {}
    id2hsh = {}
    first = True
    summary = at_hsh.get('summary', '')
    for hsh in lofh:
        # todo: is defaults needed?
        res = {}
        if type(hsh) != dict:
            msg.append('Elements must be hashes. Cannot process: "{}"'.format(hsh))
            continue
        if 'j' not in hsh:
            msg.append('error: j is required but missing')
        if first:
            # only do this once - for the first job
            first = False
            # set auto mode True if both i and p are missing from the first job,
            # otherwise set auto mode False <=> manual mode
            if  'i' in hsh or 'p' in hsh:
                auto = False
            else:
                auto = True
                count = 0
        if auto: # auto mode
            if 'i' in hsh:
                msg.append(
                    "error: &i should not be specified in auto mode")
            if 'p' in hsh:
                msg.append(
                    "error: &p should not be specified in auto mode")
            # auto generate simple sequence for i: 1, 2, 3, ... and
            # for p: 1 requires nothing, 2 requires 1, 3 requires  2, ...
            count += 1
            hsh['i'] = str(count)
            if count > 1:
                hsh['p'] = [str(count - 1)]
            else:
                hsh['p'] = []
            req[hsh['i']] = hsh['p']

        else: # manual mode
            if 'i' not in hsh:
                # TODO: fix this
                rmd.append('reminder: &i is required for each job in manual mode')
            elif hsh['i'] in req:
                msg.append("error: '&i {}' has already been used".format(hsh['i']))
            elif 'p' in hsh:
                    if type(hsh['p']) == str:
                        req[hsh['i']] = [x.strip() for x in hsh['p'].split(',') if x]
                    else:
                        req[hsh['i']] = hsh['p']
            else:
                req[hsh['i']] = []

        not_allowed = []
        for key in hsh.keys():
            if key in ['req', 'status', 'summary']:
                pass
            elif key in job_methods:
                ok, out = job_methods[key](hsh[key])
                if ok:
                    res[key] = out
                else:
                    msg.append(out)
            # else:
            #     not_allowed.append("'&{}'".format(key))
        if not_allowed:
            not_allowed.sort()
            msg.append("invalid: {}".format(", ".join(not_allowed)))

        if 'i' in hsh:
            id2hsh[hsh['i']] = res

    ids = [x for x in req]
    for i in ids:
        for j in req[i]:
            if j not in ids:
                msg.append("invalid id given in &p: {}".format(j))

    ids.sort()

    # Recursively compute the transitive closure of req so that j in req[i] iff
    # i requires j either directly or indirectly through some chain of requirements
    again = True
    while again:
        # stop after this loop unless we've added a new requirement
        again = False
        for i in ids:
            for j in ids:
                for k in ids:
                    if j in req[i] and k in req[j] and k not in req[i]:
                        # since i requires j and j requires k, i indirectly
                        # requires k so, if not already included, add k to req[i]
                        # and loop again
                        req[i].append(k)
                        again = True

    # look for circular dependencies when a job indirectly requires itself
    tmp = []
    for i in ids:
        if i in req[i]:
            tmp.append(i)
    tmp.sort()
    if tmp:
        msg.append("error: circular dependency for jobs {}".format(", ".join(tmp)))

    # Are all jobs finished:
    last_completion = None
    for i in ids:
        if id2hsh[i].get('f', None) is None:
            last_completion = None
            break
        else:
            this_completion = id2hsh[i]['f']
            if last_completion is None or last_completion < this_completion:
                last_completion = this_completion

    for i in ids:
        if last_completion:
            # remove all completions if repeating
            # last_completion will be returned to set @s for the next instance or @f if there are none
            if 'r' in at_hsh:
                del id2hsh[i]['f']
        else:
            # remove finished jobs from the requirements
            if id2hsh[i].get('f', None):
                # i is finished so remove it from the requirements for any
                # other jobs
                for j in ids:
                    if i in req[j]:
                        # since i is finished, remove it from j's requirements
                        req[j].remove(i)

    faw = [0, 0, 0]
    # set the job status for each job - f) finished, a) available or w) waiting
    for i in ids:
        if id2hsh[i].get('f', None): # i is finished
            id2hsh[i]['status'] = 'f'
            faw[0] += 1
        elif req[i]: # there are unfinished requirements for i
            id2hsh[i]['status'] = 'w'
            faw[2] += 1
        else: # there are no unfinished requirements for i
            id2hsh[i]['status'] = 'a'
            faw[1] += 1

    for i in ids:
        id2hsh[i]['summary'] = "{} {}: {}".format(summary, "/".join([str(x) for x in faw]), id2hsh[i]['j'])
        id2hsh[i]['req'] = req[i]

    if msg:
        return False, "; ".join(msg), None
    else:
        # return the list of job hashes
        return True, [id2hsh[i] for i in ids], last_completion



#######################
### end jobs setup ####
#######################

##########################
### begin TinyDB setup ###
##########################

# class DatetimeCacheTable(SmartCacheTable):
#     def _get_next_id(self):
#         """
#         Use a readable, integer timestamp as the id - unique and stores
#         the creation datetime - instead of consecutive integers. E.g.,
#         the the id for an item created 2016-06-24 08:14:11:601637 would
#         be 20160624081411601637.
#         """
#         # This must be an int even though it will be stored as a str
#         current_id = int(pendulum.now('UTC').format("%Y%m%d%H%M%S%f"))
#         self._last_id = current_id
#         return current_id
# TinyDB.table_class = DatetimeCacheTable

TinyDB.table_class = SmartCacheTable
TinyDB.DEFAULT_TABLE = 'items'
# Item = Query()

class PendulumDateTimeSerializer(Serializer):
    """
    This class handles both aware and 'factory' pendulum objects.

    Encoding: If obj.tzinfo.abbrev is '-00' (tz=Factory), it is interpreted as naive, serialized without conversion and an 'N' is appended. Otherwise it is interpreted as aware, converted to UTC and an 'A' is appended.
    Decoding: If the serialization ends with 'A', the pendulum object is treated as 'UTC' and converted to localtime. Otherwise, the object is treated as 'Factory' and no conversion is performed.

    This serialization discards both seconds and microseconds but preserves hours and minutes.
    """

    OBJ_CLASS = pendulum.pendulum.Pendulum

    def encode(self, obj):
        """
        Serialize '-00' objects without conversion but with 'N' for 'Naive' appended. Convert aware datetime objects to UTC and then serialize them with 'A' for 'Aware' appended.
        """
        if obj.tzinfo.abbrev == '-00':
            return obj.format('YYYYMMDDTHHmm[N]', formatter='alternative')
        else:
            return obj.in_timezone('UTC').format('YYYYMMDDTHHmm[A]', formatter='alternative' )

    def decode(self, s):
        """
        Return the serialization as a datetime object. If the serializaton ends with 'A',  first converting to localtime and returning an aware datetime object. If the serialization ends with 'N', returning without conversion as a naive datetime object.
        """
        if s[-1] == 'A':
            return pendulum.from_format(s[:-1], '%Y%m%dT%H%M', 'UTC').in_timezone('local')
        else:
            return pendulum.from_format(s[:-1], '%Y%m%dT%H%M', 'Factory')


class PendulumDateSerializer(Serializer):
    """
    This class handles pendulum date objects.
    """
    OBJ_CLASS = pendulum.pendulum.Date

    def encode(self, obj):
        """
        Serialize the naive date object without conversion.
        """
        return obj.format('%Y%m%d')

    def decode(self, s):
        """
        Return the serialization as a date object.
        """
        return pendulum.from_format(s, '%Y%m%d').date()


class PendulumIntervalSerializer(Serializer):
    """
    This class handles pendulum interval (timedelta) objects.
    """
    OBJ_CLASS = pendulum.Interval

    def encode(self, obj):
        """
        Serialize the timedelta object as days.seconds.
        """
        return format_interval(obj)

    def decode(self, s):
        """
        Return the serialization as a timedelta object.
        """
        return parse_interval(s)[1]


serialization = SerializationMiddleware()
serialization.register_serializer(PendulumDateTimeSerializer(), 'T')
serialization.register_serializer(PendulumDateSerializer(), 'D')
serialization.register_serializer(PendulumIntervalSerializer(), 'I')

########################
### end TinyDB setup ###
########################


########################
### start week/month ###
########################


def iso_year_start(iso_year):
    """
    Return the gregorian calendar date of the first day of the given ISO year.
    >>> iso_year_start(2017)
    <Date [2017-01-02]>
    >>> iso_year_start(2018)
    <Date [2018-01-01]>
    """
    fourth_jan = pendulum.date(iso_year, 1, 4)
    delta = pendulum.interval(fourth_jan.isoweekday()-1)
    return (fourth_jan - delta)


def iso_to_gregorian(ywd):
    """
    Return the gregorian calendar date for the given year, week and day.
    >>> iso_to_gregorian((2018, 7, 3))
    <Date [2018-02-14]>
    """
    year_start = iso_year_start(ywd[0])
    return year_start + pendulum.interval(days=ywd[2]-1, weeks=ywd[1]-1)


def getWeekNum(dt):
    """
    Return the year and week number for the datetime.
    >>> getWeekNum(pendulum.Pendulum(2018, 2, 14, 10, 30))
    (2018, 7)
    >>> getWeekNum(pendulum.date(2018, 2, 14))
    (2018, 7)
    """
    return dt.isocalendar()[:2]


def nextWeek(yw):
    """
    >>> nextWeek((2015,53))
    (2016, 1)
    """
    return (iso_to_gregorian((*yw, 7)) + pendulum.interval(days=1)).isocalendar()[:2]


def prevWeek(yw):
    """
    >>> prevWeek((2016,1))
    (2015, 53)
    """
    return (iso_to_gregorian((*yw, 1)) - pendulum.interval(days=1)).isocalendar()[:2]


def nextMonthWeeks(yw_lst):
    """
    Weeks for December 2015
    >>> nextMonthWeeks([(2015, 49), (2015, 50), (2015, 51), (2015, 52), (2015, 53)])
    [(2015, 53), (2016, 1), (2016, 2), (2016, 3), (2016, 4)]
    """
    return getMonthWeeks(iso_to_gregorian((*yw_lst[-1], 7)) + pendulum.interval(days=1))


def prevMonthWeeks(yw_lst):
    """
    Weeks for January 2016
    >>> prevMonthWeeks([(2015, 53), (2016, 1), (2016, 2), (2016, 3), (2016, 4)])
    [(2015, 49), (2015, 50), (2015, 51), (2015, 52), (2015, 53)]
    """
    return getMonthWeeks(iso_to_gregorian((*yw_lst[0], 1)) - pendulum.interval(days=1))


def getWeeks(dt, bef=0, aft=0):
    """
    Return (year, week number) tuples for the bef weeks before the week containing dt and the aft weeks after
    >>> getWeeks(datetime(2015, 10, 3), bef=0, aft=4)
    [(2015, 40), (2015, 41), (2015, 42), (2015, 43), (2015, 44)]
    >>> getWeeks(datetime(2015, 10, 3))
    [(2015, 40)]
    """
    beg_dt = dt - bef * pendulum.interval(days=7)
    end_dt = dt + aft * pendulum.interval(days=7)
    beg_yw = beg_dt.isocalendar()[:2]
    end_yw = end_dt.isocalendar()[:2]
    ret = [beg_yw]
    tmp_dt = beg_dt
    tmp_yw = beg_yw
    while tmp_yw < end_yw:
        tmp_dt = tmp_dt + pendulum.interval(days=7)
        tmp_yw = tmp_dt.isocalendar()[:2]
        ret.append(tmp_yw)
    return ret

def getMonthWeeks(dt, bef=0, aft=0):
    """
    Return (year, week number) tuples for the weeks in the months beginning bef months before the month containing dt and ending aft months after the month containing dt.
    >>> getMonthWeeks(pendulum.date(2015, 11, 3))
    [(2015, 44), (2015, 45), (2015, 46), (2015, 47), (2015, 48), (2015, 49)]
    >>> getMonthWeeks(pendulum.date(2015, 12, 15))
    [(2015, 49), (2015, 50), (2015, 51), (2015, 52), (2015, 53)]
    >>> getMonthWeeks(pendulum.date(2016, 1, 17))
    [(2015, 53), (2016, 1), (2016, 2), (2016, 3), (2016, 4)]
    >>> getMonthWeeks(pendulum.date(2016, 2, 23))
    [(2016, 5), (2016, 6), (2016, 7), (2016, 8), (2016, 9)]
    >>> getMonthWeeks(pendulum.date(2016, 1, 17), bef=2, aft=1)
    [(2015, 44), (2015, 45), (2015, 46), (2015, 47), (2015, 48), (2015, 49), (2015, 50), (2015, 51), (2015, 52), (2015, 53), (2016, 1), (2016, 2), (2016, 3), (2016, 4), (2016, 5), (2016, 6), (2016, 7), (2016, 8), (2016, 9)]
    """
    ret = []
    # get the first day of the current month
    tmp = dt.replace(day=1)
    for i in range(bef):
        # get the first day of the previous month
        tmp = (tmp - pendulum.interval(days=1)).replace(day=1)
    firstmonthday = tmp

    # get a date from the next month
    tmp = dt.replace(day=28) + pendulum.interval(days=4)
    for i in range(aft):
        tmp = tmp.replace(day=28) + pendulum.interval(days=4)
    lastmonthday = tmp - pendulum.interval(days=tmp.day)

    by, bw, bd = firstmonthday.isocalendar()
    ey, ew, ed = lastmonthday.isocalendar()
    lastweekday = iso_to_gregorian((ey, ew, 7))
    y = by
    w = bw
    day = firstmonthday
    while day <= lastweekday:
        ret.append((y,w))
        day = day + pendulum.interval(days=7)
        y, w, d = day.isocalendar()
    return ret

def getWeeksForMonth(ym):
    """
    Return the month and week numbrers for the week containing the first day of the month and the 5 following weeks.
    >>> getWeeksForMonth((2018, 3))
    [(2018, 9), (2018, 10), (2018, 11), (2018, 12), (2018, 13), (2018, 14)]
    """
    wp = pendulum.date(ym[0], ym[1], 1).isocalendar()[:2]
    wl = [wp]
    for i in range(5):
        wn = nextWeek(wp)
        wl.append(wn)
        wp = wn

    return wl

######################
### end week/month ###
######################

def pen_from_fmt(s, z='Factory'):
    dt = pendulum.from_format(s, "%Y%m%dT%H%M", z)
    if z == 'Factory' and dt.hour == dt.minute == 0:
        dt = dt.date()
    return dt

def timestamp_from_id(doc_id, z='local'):
    return pendulum.from_format(str(doc_id)[:12], "%Y%m%d%H%M").in_timezone(z)

def drop_zero_minutes(dt):
    """
    >>> drop_zero_minutes(parse('2018-03-07 10am'))
    '10'
    >>> drop_zero_minutes(parse('2018-03-07 2:45pm'))
    '2:45'
    """
    if dt.minute == 0:
        if ampm:
            return dt.format("h", formatter='alternative')
        else:
            return dt.format("H", formatter='alternative')
    else:
        if ampm:
            return dt.format("h:mm", formatter='alternative')
        else:
            return dt.format("H:mm", formatter='alternative')

def fmt_extent(beg_dt, end_dt):
    """
    >>> beg_dt = parse('2018-03-07 10am')
    >>> end_dt = parse('2018-03-07 11:30am')
    >>> fmt_extent(beg_dt, end_dt)
    '10-11:30am'
    >>> end_dt = parse('2018-03-07 2pm')
    >>> fmt_extent(beg_dt, end_dt)
    '10am-2pm'
    """
    beg_suffix = end_suffix = ""

    if ampm:
        diff = beg_dt.hour < 12 and end_dt.hour >= 12
        end_suffix = end_dt.format("A", formatter='alternative').lower()
        if diff:
            beg_suffix = beg_dt.format("A", formatter='alternative').lower()

    beg_fmt = drop_zero_minutes(beg_dt)
    end_fmt = drop_zero_minutes(end_dt)

    return f"{beg_fmt}{beg_suffix}-{end_fmt}{end_suffix}"


def beg_ends(starting_dt, extent_interval, z=None):
    """
    >>> starting = parse('2018-03-02 9am') 
    >>> beg_ends(starting, parse_interval('2d2h20m')[1])
    [(<Pendulum [2018-03-02T09:00:00+00:00]>, <Pendulum [2018-03-02T23:59:59.999999+00:00]>), (<Pendulum [2018-03-03T00:00:00+00:00]>, <Pendulum [2018-03-03T23:59:59.999999+00:00]>), (<Pendulum [2018-03-04T00:00:00+00:00]>, <Pendulum [2018-03-04T11:20:00+00:00]>)]
    >>> beg_ends(starting, parse_interval('8h20m')[1])
    [(<Pendulum [2018-03-02T09:00:00+00:00]>, <Pendulum [2018-03-02T17:20:00+00:00]>)]
    """

    pairs = []
    beg = starting_dt
    ending = starting_dt + extent_interval
    while ending.date() > beg.date():
        end = beg.end_of('day')
        pairs.append((beg, end))
        beg = beg.start_of('day').add(days=1)
    pairs.append((beg, ending))
    return pairs


def load_tinydb():

    return TinyDB('db.json', storage=serialization, default_table='items', indent=1, ensure_ascii=False)

def print_json():
    db = load_tinydb()
    for item in db:
        try:
            print(item.doc_id, item.doc_id, item['itemtype'])
            print(item_details(item))
        except Exception as e:
            print('exception:', e)
            pprint(item)
            print()
        print()

def item_details(item):
    try:
        return jinja_entry_template.render(h=item)
    except Exception as e:
        print('item_details', e)
        print(item)


def fmt_week(dt_obj):
    """
    >>> fmt_week(pendulum.parse('2018-03-06 9:30pm'))
    '2018 Week 10: Mar 5 - 11'
    """
    dt_year = dt_obj.year
    dt_week = dt_obj.week_of_year
    year_week = f"{dt_year} Week {dt_week}"
    wkbeg = pendulum.parse(f"{dt_year}W{str(dt_week).rjust(2, '0')}")
    wkend = pendulum.parse(f"{dt_year}W{str(dt_week).rjust(2, '0')}-7")
    week_begin = wkbeg.format("MMM D", formatter='alternative')
    if wkbeg.month == wkend.month:
        week_end = wkend.format("D", formatter='alternative')
    else:
        week_end = wkend.format("MMM D", formatter='alternative')
    return f"{dt_year} Week {dt_week}: {week_begin} - {week_end}"


def schedule(weeks_bef=1, weeks_aft=2):
    today = pendulum.now('local').replace(hour=0, minute=0, second=0, microsecond=0, tzinfo='Factory')
    week_beg = today.subtract(days=today.day_of_week - 1)
    aft_dt = week_beg.subtract(weeks=weeks_bef)
    bef_dt = week_beg.add(weeks=weeks_aft + 1)

    db = TinyDB('db.json', storage=serialization, default_table='items', indent=1, ensure_ascii=False)
    rows = []
    for item in db:
        if item['itemtype'] in "!?" or 's' not in item:
            continue
        # if type(item['s']) == pendulum.Pendulum and 'e' in item:
        #     rhc = fmt_extent(item['s'], item['s'] + item['e']).center(16, ' ')
        #     # rhc = fmt_extent(beg_ends(item['s'], item['e'])[0]).center(16, ' ')
        #     # rhc = item['s'].format("h:mmA", formatter="alternative")
        # else:
        #     rhc = ""

        # aft_dt = parse('2018-01-01 12am').replace(tzinfo=None)
        # bef_dt = parse('2018-12-31 11:59pm').replace(tzinfo=None)
        for dt, et in item_instances(item, aft_dt, bef_dt):
            rhc = fmt_extent(dt, et).center(16, ' ') if 'e' in item else ""

            rows.append(
                    {
                        'id': item.doc_id,
                        'sort': dt.format("YYYYMMDDHHmm", formatter="alternative"),
                        'week': (
                            dt.year, 
                            dt.week_of_year, 
                            ),
                        'day': (
                            dt.format("ddd MMM D", formatter="alternative"),
                            ),
                        'columns': (
                            f"{item['itemtype']} {item['summary']}", 
                            rhc
                            )
                    }
                    )
    from operator import itemgetter
    from itertools import groupby
    rows.sort(key=itemgetter('sort'))

    for week, items in groupby(rows, key=itemgetter('week')):
        wkbeg = pendulum.parse(f"{week[0]}W{str(week[1]).rjust(2, '0')}").date().format("MMM D", formatter='alternative')
        wkend = pendulum.parse(f"{week[0]}W{str(week[1]).rjust(2, '0')}-7").date().format("MMM D", formatter='alternative')

        print(f"{week[0]} Week {week[1]}: {wkbeg} - {wkend}")
        for day, columns in groupby(items, key=itemgetter('day')):
            for d in day:
                print(" ", d)
                for i in columns:
                    space = " "*(60 - len(i['columns'][0]) - len(i['columns'][1]))
                    print(f"    {i['columns'][0]}{space}{i['columns'][1]}" )


def import_json():
    import json
    # root = '/Users/dag/etm-mvc/tmp'
    # import_file = os.path.join(root, 'import.json')
    import_file = '/Users/dag/.etm/data/etm-db.json'
    with open(import_file, 'r') as fo:
        import_hsh = json.load(fo)
    items = import_hsh['items']
    db = TinyDB('db.json', storage=serialization, default_table='items', indent=1, ensure_ascii=False)
    db.purge()

    docs = []
    for id in items:
        item_hsh = items[id]
        if item_hsh['itemtype'] not in type_keys:
            continue
        z = item_hsh.get('z', 'Factory')
        bad_keys = [x for x in item_hsh if x not in at_keys]
        for key in bad_keys:
            del item_hsh[key]
        item_hsh['created'] = timestamp_from_id(id, 'Factory')
        if 's' in item_hsh:
            item_hsh['s'] = pen_from_fmt(item_hsh['s'], z)
        elif 'z' in item_hsh:
            del item_hsh['z']
        if 'f' in item_hsh:
            item_hsh['f'] = pen_from_fmt(item_hsh['f'], z)
        if 'h' in item_hsh:
            item_hsh['h'] = [pen_from_fmt(x, z) for x in item_hsh['h']]
        if '+' in item_hsh:
            item_hsh['+'] = [pen_from_fmt(x, z) for x in item_hsh['+'] ]
        if '-' in item_hsh:
            item_hsh['-'] = [pen_from_fmt(x, z) for x in item_hsh['-'] ]
        if 'e' in item_hsh:
            item_hsh['e'] = parse_interval(item_hsh['e'])[1]
        if 'a' in item_hsh:
            alerts = []
            for alert in item_hsh['a']:
                # drop the True from parse_interval
                tds = [parse_interval(x)[1] for x in alert[0]]
                cmds = alert[1:2]
                args = ""
                if len(alert) > 2 and alert[2]:
                    args = ", ".join(alert[2])
                for cmd in cmds:
                    if args:
                        row = (tds, cmd, args)
                    else:
                        row = (tds, cmd)
                    alerts.append(row)
            item_hsh['a'] = alerts
        if 'j' in item_hsh:
            jbs = []
            for jb in item_hsh['j']:
                if 'h' in jb:
                    if 'f' not in jb:
                        jb['f'] = jb['h'][-1]
                del jb['h']
                jbs.append(jb)
            ok, lofh, last_completed = jobs(jbs, item_hsh)
            if ok:
                item_hsh['j'] = lofh
            # for job in item_hsh['j']:
            #     bad_keys = []
            #     for key in job:
            #         if key not in amp_keys['j'] or not job[key]:
            #             bad_keys.append(key)
            #     if bad_keys:
            #         for key in bad_keys:
            #             del job[key]
            #     jobs.append(job)
            # item_hsh['j'] = jbs

        if 'r' in item_hsh:
            ruls = []
            for rul in item_hsh['r']:
                if 'f' in rul:
                    rul['r'] = rul['f']
                    del rul['f']
                if 'u' in rul:
                    if 't' in rul:
                        del rul['t']
                    if 'c' in rul:
                        del rul['c']
                elif 't' in rul:
                    rul['c'] = rul['t']
                    del rul['t']
                if 'u' in rul:
                    if type(rul['u']) == str:
                        try:
                            rul['u'] = parse(rul['u'], tz=z)
                        except Exception as e:
                            print(e)
                            print(rul['u'])
                bad_keys = []
                for key in rul:
                    if key not in amp_keys['r'] or not rul[key]:
                        bad_keys.append(key)
                if bad_keys:
                    for key in bad_keys:
                        del rul[key]
                ruls.append(rul)
            item_hsh['r'] = ruls

        docs.append(item_hsh)
    db.insert_multiple(docs)



if __name__ == '__main__':
    import sys
    print('\n\n')
    setup_logging(1)
    import doctest

    if len(sys.argv) > 1:
        if 'i' in sys.argv[1]:
            import_json()
        if 'p' in sys.argv[1]:
            print_json()
        if 's' in sys.argv[1]:
            schedule(0, 3)

    doctest.testmod()

