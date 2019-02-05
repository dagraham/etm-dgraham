#!/usr/bin/env python3
from pprint import pprint
import pendulum
from pendulum import parse as pendulum_parse
# from pendulum import  DateTime, Duration
from pendulum.datetime import Timezone
# from bisect import insort

def parse(s, **kwd):
    return pendulum_parse(s, strict=False, **kwd)

# from datetime import datetime

import sys
import re
from re import finditer

from tinydb import TinyDB
# from tinydb.operations import delete
# from tinydb.database import Table
# from tinydb.storages import JSONStorage
from tinydb_serialization import Serializer
from tinydb_serialization import SerializationMiddleware
# from tinydb_smartcache import SmartCacheTable

# from copy import deepcopy
# import calendar as clndr

import dateutil
import dateutil.rrule
from dateutil.rrule import *
# from dateutil.easter import easter
from dateutil import __version__ as dateutil_version

from jinja2 import Template

import textwrap

import os
import platform

import shutil

import logging
import logging.config
logger = logging.getLogger()


from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style
from prompt_toolkit.output import ColorDepth
# print = print_formatted_text

# The style sheet.
style = Style.from_dict({
    'plain':        '#fffafa',
    'selection':    '#fffafa',
    'inbox':        '#ff00ff',
    'pastdue':      '#87ceeb',
    'begin':        '#ffff00',
    'record':       '#daa520',
    'event':        '#90ee90',
    'available':    '#1e90ff',
    'waiting':      '#6495ed',
    'finished':     '#191970',
})

type2style = {
        '!': 'class:inbox',
        '<': 'class:pastdue',
        '>': 'class:begin',
        '%': 'class:record',
        '*': 'class:event',
        '-': 'class:available',
        '+': 'class:waiting',
        '✓': 'class:finished',
        }

etmdir = None

ampm = True

testing = True
# testing = False

ETMFMT = "%Y%m%dT%H%M"
ZERO = pendulum.duration(minutes=0)
DAY = pendulum.duration(days=1)
finished_char = u"\u2713"  #  ✓

WKDAYS_DECODE = {"{0}{1}".format(n, d): "{0}({1})".format(d, n) if n else d for d in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'] for n in ['-4', '-3', '-2', '-1', '', '1', '2', '3', '4']}
WKDAYS_ENCODE = {"{0}({1})".format(d, n): "{0}{1}".format(n, d) if n else d for d in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'] for n in ['-4', '-3', '-2', '-1', '+1', '+2', '+3', '+4']}
for wkd in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']:
    WKDAYS_ENCODE[wkd] = wkd

# # FIXME: display characters 
# datedChar2Type = {
#     '!': "ib",
#     '*': "ev",
#     '~': "ac",
#     '%': "nt",
#     '-': "ta",
#     '+': "tw",
#     finished_char: "tf",
#     '?': "so",
# }

# pastdueTaskChar2Type = {
#     '-': "td",
#     '+': "tw"
# }

# undatedChar2Type = {
#     '-': "ta",
#     '%': "nt",
#     '!': "ib",
#     '?': "so",
#     finished_char: "tf",
# }

type_keys = {
    "*": "event",
    "-": "task",
    "%": "record",
    "!": "inbox",
}

type_prompt = u"item type character:"

item_types = """item type characters:\n    """ + """\n    """.join([f"{k}: {v}" for k, v in type_keys.items()])


at_keys = {
        '+': "include: list of date-times",
        '-': "exclude: list of date-times",
        'a': "alert: list of periods followd by a colon and a command and, optionally, by a list of cmd arguments",
        'b': "beginby: integer number of days",
        'c': "calendar: string",
        'd': "description: string",
        'e': "extent: timeperiod",
        'f': "finish: datetime",
        'g': "goto url or filepath: string",
        'h': "completions history: list of datetimes",
        'i': "index: colon delimited string",
        'j': "job summary: string",
        'l': "location: string",
        'm': "memo: string",  # maybe masked / crypted?
        'n': "attendees: list of 'name <email address>'",
        'o': "overdue: character from (r)estart, (s)kip or (k)eep",
        'p': "priority: integer",
        'r': "repetition frequency: character from (y)ear, (m)onth, (w)eek,"
            " (d)ay, (h)our, mi(n)ute",
        's': "start: date or datetime",
        't': "tags: list of strings",
        'x': "expansion key: string",
        'z': "timezone: string",
        'itemtype': "character from (*)event, (-)task, (%)record or (!)inbox",
        'summary': "string"
}

amp_keys = {
    'r': {
        'c': "count: integer number of repetitions",
        'm': "monthday: list of integers 1 ... 31, possibly prepended with a minus sign to count backwards from the end of the month", 
        'E': "easter: number of days before (-), on (0) or after (+) Easter",
        'h': "hour: list of integers in 0 ... 23",
        'r': "frequency: character in y, m, w, d, h, n",
        'i': "interval: positive integer",
        'M': "month: list of integers in 1 ... 12", 
        'n': "minute: list of integers in 0 ... 59", 
        's': "set position: integer",
        'u': "until: datetime",
        'w': "weekday: list from SU, MO, ..., SA, possibly prepended with a positive or negative integer",
        'W': "week number: list of integers in 1, ... 53"
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

# item_hsh = {} # preserve state

allowed = {}
required = {}
common_methods = [x for x in 'cdegilmnstx']
repeating_methods = [x for x in '+-o'] + ['rr', 'rc', 'rm', 'rE', 'rh', 'ri', 'rM', 'rn', 'rs', 'ru', 'rW', 'rw']
datetime_methods = [x for x in 'abez']
task_methods = [x for x in 'fhp'] + ['jj', 'ja', 'jb', 'jd', 'je', 'jf', 'ji', 'jl', 'jm', 'jp', 'js']

# events
required['*'] = ['s']
allowed['*'] = common_methods + datetime_methods + repeating_methods


# tasks
required['-'] = []
allowed['-'] = common_methods + datetime_methods + task_methods + repeating_methods

# record entries
required['%'] = []
allowed['%'] = common_methods + datetime_methods

# inbox entries
required['!'] = []
allowed['!'] = common_methods + datetime_methods + task_methods + repeating_methods

requires = {
        'a': 's',
        'b': 's',
        '+': 's',
        '-': 'r',
        'o': 'r',
        'rr': 's',
        'js': 's',
        'ja': 's',
        'jb': 's',
        }

# set up 2 character weekday name abbreviations for busy view
# pendulum.set_locale('fr')
WA = {}
today = pendulum.today()
day = today.end_of('week')  # Sunday
for i in range(1, 8):
    # 1 -> Mo, ...,  7 -> Su
    WA[i] = day.add(days=i).format('ddd')[:2]

AMPM = True
LL = {}
for hour in range(24):
    if hour % 6 == 0:
        if AMPM:
            suffix = 'am' if hour < 12 else 'pm'
            if hour == 0:
                hr = 12
            elif hour <= 12:
                hr = hour
            elif hour > 12:
                hr = hour - 12
            LL[hour] = f"{hr}{suffix}".rjust(6, ' ')
        else:
            LL[hour] = f"{hour}h".rjust(6, ' ')
    else:
        LL[hour] = ' '.rjust(6, ' ')


busy_template = """\
{week}
         {WA[1]} {DD[1]}  {WA[2]} {DD[2]}  {WA[3]} {DD[3]}  {WA[4]} {DD[4]}  {WA[5]} {DD[5]}  {WA[6]} {DD[6]}  {WA[7]} {DD[7]} 
         -----------------------------------------------  
{l[0]}   {h[0][1]}  {h[0][2]}  {h[0][3]}  {h[0][4]}  {h[0][5]}  {h[0][6]}  {h[0][7]}
{l[1]}   {h[1][1]}  {h[1][2]}  {h[1][3]}  {h[1][4]}  {h[1][5]}  {h[1][6]}  {h[1][7]}
{l[2]}   {h[2][1]}  {h[2][2]}  {h[2][3]}  {h[2][4]}  {h[2][5]}  {h[2][6]}  {h[2][7]}
{l[3]}   {h[3][1]}  {h[3][2]}  {h[3][3]}  {h[3][4]}  {h[3][5]}  {h[3][6]}  {h[3][7]}
{l[4]}   {h[4][1]}  {h[4][2]}  {h[4][3]}  {h[4][4]}  {h[4][5]}  {h[4][6]}  {h[4][7]}
{l[5]}   {h[5][1]}  {h[5][2]}  {h[5][3]}  {h[5][4]}  {h[5][5]}  {h[5][6]}  {h[5][7]}
{l[6]}   {h[6][1]}  {h[6][2]}  {h[6][3]}  {h[6][4]}  {h[6][5]}  {h[6][6]}  {h[6][7]}
{l[7]}   {h[7][1]}  {h[7][2]}  {h[7][3]}  {h[7][4]}  {h[7][5]}  {h[7][6]}  {h[7][7]}
{l[8]}   {h[8][1]}  {h[8][2]}  {h[8][3]}  {h[8][4]}  {h[8][5]}  {h[8][6]}  {h[8][7]}
{l[9]}   {h[9][1]}  {h[9][2]}  {h[9][3]}  {h[9][4]}  {h[9][5]}  {h[9][6]}  {h[9][7]}
{l[10]}   {h[10][1]}  {h[10][2]}  {h[10][3]}  {h[10][4]}  {h[10][5]}  {h[10][6]}  {h[10][7]}
{l[11]}   {h[11][1]}  {h[11][2]}  {h[11][3]}  {h[11][4]}  {h[11][5]}  {h[11][6]}  {h[11][7]}
{l[12]}   {h[12][1]}  {h[12][2]}  {h[12][3]}  {h[12][4]}  {h[12][5]}  {h[12][6]}  {h[12][7]}
{l[13]}   {h[13][1]}  {h[13][2]}  {h[13][3]}  {h[13][4]}  {h[13][5]}  {h[13][6]}  {h[13][7]}
{l[14]}   {h[14][1]}  {h[14][2]}  {h[14][3]}  {h[14][4]}  {h[14][5]}  {h[14][6]}  {h[14][7]}
{l[15]}   {h[15][1]}  {h[15][2]}  {h[15][3]}  {h[15][4]}  {h[15][5]}  {h[15][6]}  {h[15][7]}
{l[16]}   {h[16][1]}  {h[16][2]}  {h[16][3]}  {h[16][4]}  {h[16][5]}  {h[16][6]}  {h[16][7]}
{l[17]}   {h[17][1]}  {h[17][2]}  {h[17][3]}  {h[17][4]}  {h[17][5]}  {h[17][6]}  {h[17][7]}
{l[18]}   {h[18][1]}  {h[18][2]}  {h[18][3]}  {h[18][4]}  {h[18][5]}  {h[18][6]}  {h[18][7]}
{l[19]}   {h[19][1]}  {h[19][2]}  {h[19][3]}  {h[19][4]}  {h[19][5]}  {h[19][6]}  {h[19][7]}
{l[20]}   {h[20][1]}  {h[20][2]}  {h[20][3]}  {h[20][4]}  {h[20][5]}  {h[20][6]}  {h[20][7]}
{l[21]}   {h[21][1]}  {h[21][2]}  {h[21][3]}  {h[21][4]}  {h[21][5]}  {h[21][6]}  {h[21][7]}
{l[22]}   {h[22][1]}  {h[22][2]}  {h[22][3]}  {h[22][4]}  {h[22][5]}  {h[22][6]}  {h[22][7]}
{l[23]}   {h[23][1]}  {h[23][2]}  {h[23][3]}  {h[23][4]}  {h[23][5]}  {h[23][6]}  {h[23][7]}
         -----------------------------------------------  
{t[0]}   {t[1]}  {t[2]}  {t[3]}  {t[4]}  {t[5]}  {t[6]}  {t[7]}
"""

def busy_conf_minutes(lofp):
    """
    lofp is a list of tuples of (begin_minute, end_minute) busy times, e.g., [(b1, e1) , (b2, e2), ...]. By construction bi < ei. By sort, bi <= bi+1. 
    Return list of busy intervals, list of conflict intervals, busy minutes.
    [(540, 600), (600, 720)]
    >>> busy_conf_minutes([(540, 600)])
    ([(540, 600)], [], 60)
    >>> busy_conf_minutes([(540, 600), (600, 720)])
    ([(540, 600), (600, 720)], [], 180)
    >>> busy_conf_minutes([(540, 620), (600, 720), (660, 700)])
    ([(540, 600), (620, 660), (700, 720)], [(600, 620), (660, 700)], 180)
    """
    lofp.sort()
    busy_minutes = []
    conf_minutes = []
    if not lofp:
        return ([], [], 0)
    (b, e) = lofp.pop(0)
    while lofp:
        (B, E) = lofp.pop(0)
        if e <= B:  # no conflict
            busy_minutes.append((b, e))
            b = B
            e = E
        else:  # B < e
            busy_minutes.append((b, B))
            if e <= E:
                conf_minutes.append((B, e))
                b = e
                e = E
            else:  # E < e
                conf_minutes.append((B, E))
                b = E
                e = e
    busy_minutes.append((b, e))
    total_minutes = 0
    for (b, e) in busy_minutes + conf_minutes:
        total_minutes += e - b
    return busy_minutes, conf_minutes, total_minutes

def busy_conf_day(lofp):
    """
    lofp is a list of tuples of (begin_minute, end_minute) busy times, e.g., [(b1, e1) , (b2, e2), ...]. By construction bi < ei. By sort, bi <= bi+1.
    Return a hash giving total minutes and appropriate symbols for busy hours.
    >>> busy_conf_day([(540, 600), (600, 720)])
    {'total': 180, 9: '  #  ', 10: '  #  ', 11: '  #  '}
    >>> busy_conf_day([(540, 620), (600, 720), (660, 700)])
    {'total': 180, 9: '  #  ', 10: ' ### ', 11: ' ### '}
    >>> busy_conf_day([(540, 620), (620, 720), (700, 720)])
    {'total': 180, 9: '  #  ', 10: '  #  ', 11: ' ### '}
    >>> busy_conf_day([])
    {'total': 0}
    >>> busy_conf_day([(0, 1439)])
    {0: '  #  ', 'total': 1439, 1: '  #  ', 2: '  #  ', 3: '  #  ', 4: '  #  ', 5: '  #  ', 6: '  #  ', 7: '  #  ', 8: '  #  ', 9: '  #  ', 10: '  #  ', 11: '  #  ', 12: '  #  ', 13: '  #  ', 14: '  #  ', 15: '  #  ', 16: '  #  ', 17: '  #  ', 18: '  #  ', 19: '  #  ', 20: '  #  ', 21: '  #  ', 22: '  #  ', 23: '  #  '}
    """

    busy_ranges, conf_ranges, total = busy_conf_minutes(lofp)
    busy_hours = []
    conf_hours = []

    for (b, e) in conf_ranges:
        h_b = b // 60
        h_e = e // 60
        if e % 60: h_e += 1
        for i in range(h_b, h_e):
            if i not in conf_hours:
                conf_hours.append(i)

    for (b, e) in busy_ranges:
        h_b = b // 60
        h_e = e // 60
        if e % 60: h_e += 1
        for i in range(h_b, h_e):
            if i not in conf_hours and i not in busy_hours:
                busy_hours.append(i)
    h = {} 
    for i in range(24):
        if i in busy_hours:
            h[i] = '#'.center(5, ' ')
        elif i in conf_hours:
            h[i] = '###'.center(5, ' ')
        # else:
        #     h[i] = '.'.center(3, ' ')
        h['total'] = total
    return h

def check_requires(key, hsh):
    """
    Check that hsh has the prerequisite entries for key.
    """
    if key in requires and requires[key] not in hsh:
        return False, ('warn', f"{requires[key]} is required for {key}")
    else:
        return True, ('say', '')




deal_with = {}

def deal_with_z(at_hsh={}):
    """
    Check the currents state of at_hsh regarding the 'z' key
    """
    top = "{}?".format(at_keys['z'])
    bot = ''
    tz = at_hsh.get('z', None)
    if tz is None:
        return top, bot, None
    bot = f"timezone: {tz}"
    return top, bot, tz
    # s = at_hsh.get('s', None)
    # if s is None:
    #     return top, bot, None

    # t1, t2, obj = deal_with_s(at_hsh)
    # if obj is None:
    #     return top, bot, None
    # return obj.tzinfo

deal_with['z'] = deal_with_z

def deal_with_s(at_hsh = {}):
    """
    Check the currents state of at_hsh regarding the s and z keys
    """
    s = at_hsh.get('s', None)
    top = "{}?".format(at_keys['s'])
    bot = ''
    if s is None:
        return top, bot
    tz = at_hsh.get('z', None)
    ok, obj, tz = parse_datetime(s, tz)
    if not ok or not obj:
        return top, "considering: '{}'".format(s), None
    # at_hsh['s'] = obj
    # at_hsh['z'] = tz
    if ok == 'date':
        # 'dateonly'
        bot = "starting: {}".format(obj.format("ddd MMM D YYYY"))
        bot += '\nWithout a time, this schedules an all-day, floating item for the specified date in whatever happens to be the local timezone.'
    elif ok == 'float':
        bot = "starting: {}".format(obj.in_tz('Factory').format("ddd MMM D YYYY h:mmA"))
        bot += "\nBecause of the '@z float' entry, the datetime entry for @s will be interpreted as a naive datetime in whatever happens to be the local timezone."
    elif ok == 'aware':
        # bot = "starting: {}".format(obj.format("ddd MMM D h:mmA z"))
        bot = "starting: {}".format(obj.in_tz(tz).format("ddd MMM D YYYY h:mmA zz"))
        # bot = "starting: {}".format(obj.format("ddd MMM D YYYY h:mmA z"))
        bot += "\nWith an entry for '@z', The datetime entry for @s will be interpreted as an aware datetime in the specified timezone."
    else:
        bot = "starting: {}".format(obj.in_tz('local').format("ddd MMM D YYYY h:mmA zz"))
        bot += "\nWithout an entry for '@z', the datetime entry for @s will be interpreted as an aware datetime in the current local timezone. Append a specific timezone, e.g., '@z US/Pacific', to use that timezone or '@z float' to make the datetime floating (naive)."

    return top, bot, obj



deal_with['s'] = deal_with_s


def deal_with_missing(at_hsh, key):

    s = at_hsh.get(key, None)
    top = "{}?".format(at_keys[key])
    bot = ''
    if s is None:
        return top, bot, None

    top = "{}".format(at_keys[key])
    bot = f"{at_keys[key]}: {s}"
    if key in ['t']:
        ok, res = string_list(s)
    else:
        res = s

    return top, bot, res

def deal_with_e(at_hsh={}):
    """
    Check the current state of at_hsh regarding the 'e' key.
    """
    s = at_hsh.get('e', None)
    top = "{}?".format(at_keys['e'])
    bot = ''
    if s is None:
        return top, bot, None
    ok, obj = parse_duration(s)
    if not ok:
        return top, "considering: '{}'".format(s), None
    # item_hsh['e'] = obj
    bot = "extent: {0}".format(obj.in_words())
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

    # item_hsh['i'] = res
    bot = "index: " + ", ".join(['level {0} -> {1}'.format(i, res[i]) for i in range(len(res))])
    return top, bot, res

deal_with['@i'] = deal_with_i


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

# def get_next(at_hsh={}):
#     if not at_hsh or 's' not in at_hsh or 'rrulestr' not in at_hsh:
#         return False, "Both @s and @r are required for repetitions"



def deal_with_r(at_hsh={}):
    """
    Check the current state of at_hsh regarding r and s.
    """
    top = "repeat?"
    bot = "{}".format(at_keys['r'])
    lofh = at_hsh.get('r', [])
    # print('lofh:', at_hsh, lofh)
    ok, res = check_rrule(lofh)
    if ok:
        show = "".join([f"    {x}\n" for x in res])
        bot = f"repetition:\n{show}"
    else:
        bot = f"considering: {lofh}"
    return top, bot, res


deal_with['r'] = deal_with_r

def deal_with_j(at_hsh={}):
    """
    Check the current state of at_hsh regarding j and s.
    """
    # dated = 's' in at_hsh
    top = "job?"
    bot = "{}".format(at_keys['j'])
    lofh = at_hsh.get('j', [])
    ok, res, lastcompletion = jobs(lofh, at_hsh)
    if ok:
        # item_hsh['jobs'] = res
        show = "".join(["    {}\n".format(x) for x in res])
        bot = "jobs:\n{}".format(show)
    else:
        bot = "jobs:\n{}\n".format(res)
    return top, bot, res


deal_with['j'] = deal_with_j


def process_entry(s):
    """
    Return tuples containing key, value and postion tuples for the string s. 
    0         1         2         3         4         5         6 
    0123456789012345678901234567890123456789012345678901234567890123456789
    * evnt @s 2p fri @e 90m @r m &w 2fr &u 6/1 9a @c dag @l home
    >>> s = "* evnt @s 2p fri @e 90m @r m &w 2fr & @c dag"
    >>> process_entry(s)
    ({(0, 1): ('itemtype', '*'), (1, 7): ('summary', 'evnt'), (7, 17): ('s', '2p fri'), (17, 24): ('e', '90m'), (24, 29): ('rr', 'm'), (29, 36): ('rw', '2fr'), (36, 38): ('r?', ''), (38, 45): ('c', 'dag')}, [('itemtype', '*'), ('summary', 'evnt'), ('s', '2p fri'), ('e', '90m'), ('rr', 'm'), ('rw', '2fr'), ('r?', ''), ('c', 'dag')])
    >>> s = "* evnt @s 2p fri @e 90m @r m &w 2fr &u 6/1 9a @ @l home"
    >>> process_entry(s)
    ({(0, 1): ('itemtype', '*'), (1, 7): ('summary', 'evnt'), (7, 17): ('s', '2p fri'), (17, 24): ('e', '90m'), (24, 29): ('rr', 'm'), (29, 36): ('rw', '2fr'), (36, 46): ('ru', '6/1 9a'), (46, 48): ('?', ''), (48, 56): ('l', 'home')}, [('itemtype', '*'), ('summary', 'evnt'), ('s', '2p fri'), ('e', '90m'), ('rr', 'm'), ('rw', '2fr'), ('ru', '6/1 9a'), ('?', ''), ('l', 'home')])
    >>> process_entry('')
    ({(0, 1): ('itemtype', '')}, [('itemtype', '')])
    >>> process_entry("- ")
    ({(0, 1): ('itemtype', '-'), (1, 3): ('summary', '')}, [('itemtype', '-'), ('summary', '')])
    >>> process_entry("- todo @ @t red, green")
    ({(0, 1): ('itemtype', '-'), (1, 7): ('summary', 'todo'), (7, 9): ('?', ''), (9, 23): ('t', 'red, green')}, [('itemtype', '-'), ('summary', 'todo'), ('?', ''), ('t', 'red, green')])
    >>> process_entry("- todo  @s mon 9a @j job 1 &s 2d @j job 2 & @j job 3")
    ({(0, 1): ('itemtype', '-'), (1, 8): ('summary', 'todo'), (8, 18): ('s', 'mon 9a'), (18, 27): ('jj', 'job 1'), (27, 33): ('js', '2d'), (33, 42): ('jj', 'job 2'), (42, 44): ('j?', ''), (44, 53): ('jj', 'job 3')}, [('itemtype', '-'), ('summary', 'todo'), ('s', 'mon 9a'), ('jj', 'job 1'), ('js', '2d'), ('jj', 'job 2'), ('j?', ''), ('jj', 'job 3')])
    >>> process_entry("- todo  @s mon 9a @a 15m, 10m: d @a 15m, 10m: v")
    ({(0, 1): ('itemtype', '-'), (1, 8): ('summary', 'todo'), (8, 18): ('s', 'mon 9a'), (18, 33): ('a', '15m, 10m: d'), (33, 48): ('a', '15m, 10m: v')}, [('itemtype', '-'), ('summary', 'todo'), ('s', 'mon 9a'), ('a', '15m, 10m: d'), ('a', '15m, 10m: v')])
    >>> process_entry('+ bad type character')
    ({(0, 21): ('itemtype', '+')}, [('itemtype', '+')])
    """
    tups = []
    keyvals = []
    pos_hsh = {}  # (tupbeg, tupend) -> [key, value]
    if not s:
        return {(0, 1): ('itemtype', '')}, [('itemtype', '')]
    elif s[0] not in type_keys:
        return {(0, len(s) + 1): ('itemtype', s[0])}, [('itemtype', s[0])]
    pattern = "\s[@&][a-zA-Z+-]"
    parts = []
    for match in finditer(pattern, s):
        parts.append([match.span()[0]+1, match.span()[1], match.group().strip()])
    if not parts:
        tups.append((s[0], s[1:].strip(), 0, len(s)+1))

    lastbeg = 0
    lastend = 1
    lastkey = s[0]
    for beg, end, key in parts:
        tups.append([lastkey, s[lastend:beg].strip(), lastbeg, beg])
        pos_hsh[tuple((tups[-1][2], tups[-1][3]))] = (tups[-1][0], tups[-1][1])
        lastkey = key
        lastbeg = beg
        lastend = end
    tups.append([lastkey, s[lastend:].strip(), lastbeg, len(s)+1])
    pos_hsh[tuple((tups[-1][2], tups[-1][3]))] = (tups[-1][0], tups[-1][1])

    pos_hsh = {}  # (tupbeg, tupend) -> [key, value]

    # add (@?, '') and (&?, '') tups for @ and & entries without keys
    aug_tups = []
    for key, value, beg, end in tups:
        if beg == 0:
            aug_tups.append(('itemtype', key, beg, 1))
            if value.endswith(' @') or value.endswith(' &'):
                aug_key = f"{value[-1]}?"
                end -= 2
                value = value[:-2]
                aug_tups.append(('summary', value, 1, end))
                aug_tups.append((aug_key, '', end, end + 2))
            else:
                aug_tups.append(('summary', value, 1, end))
        elif value.endswith(' @') or value.endswith(' &'):
            aug_key = f"{value[-1]}?"
            end -= 2
            value = value[:-2]
            aug_tups.append((key, value, beg, end))
            aug_tups.append((aug_key, '', end, end + 2))
        else:
            aug_tups.append((key, value, beg, end))

    for key, value, beg, end in aug_tups:
        if key in ['@r', '@j']:
            pos_hsh[tuple([beg, end])] = (f"{key[-1]}{key[-1]}", value)
            adding = key[-1]
        elif key in ['@a']:
            pos_hsh[tuple((beg, end))] = (key[-1], value)
            adding = None
        elif key.startswith('&'):
            if adding:
                pos_hsh[tuple((beg, end))] = (f"{adding}{key[-1]}", value)
            else:
                pass
        elif key in ['itemtype', 'summary']:
            adding = None
            pos_hsh[tuple((beg, end))] = (key, value)
        else:
            adding = None
            pos_hsh[tuple([beg, end])] = (key[-1], value)

    keyvals = [(k, v) for pos, (k, v) in pos_hsh.items()]
    if keyvals[0][0] in type_keys:
        k, v = keyvals.pop(0)
        keyvals.insert(0, ('summary', v))
        keyvals.insert(0, ('itemtype', k))

    return pos_hsh, keyvals

def active_from_pos(pos_hsh, pos):
    """
    >>> s = "* evnt @s 2p fri @e 90m @r w &w 2fr &u 6/1 9a @c dag @l home"
    >>> pos_hsh, hsh = process_entry(s)
    >>> print(pos_hsh)
    {(0, 1): ('itemtype', '*'), (1, 7): ('summary', 'evnt'), (7, 17): ('s', '2p fri'), (17, 24): ('e', '90m'), (24, 29): ('rr', 'w'), (29, 36): ('rw', '2fr'), (36, 46): ('ru', '6/1 9a'), (46, 53): ('c', 'dag'), (53, 61): ('l', 'home')}
    >>> active_from_pos(pos_hsh, 18)
    ((17, 24), ('e', '90m'))
    >>> active_from_pos(pos_hsh, 45)
    ((36, 46), ('ru', '6/1 9a'))
    >>> pos_hsh, hsh = process_entry("- ")
    >>> active_from_pos(pos_hsh, 0)
    ((0, 1), ('itemtype', '-'))
    >>> active_from_pos(pos_hsh, 1)
    ((1, 3), ('summary', ''))
    >>> pos_hsh, hsh = process_entry("")
    >>> active_from_pos(pos_hsh, 1)
    (None, None)
    >>> pos_hsh, hsh = process_entry("+ bad type character")
    >>> active_from_pos(pos_hsh, 3)
    ((0, 21), ('itemtype', '+'))
    """
    for p, v in pos_hsh.items():
        if p[0] <= pos < p[1]:
            return p, v
    return None, None


class Item(object):
    """

    """

    def __init__(self, doc_id=None, s=""):
        """
        """

        self.doc_id = doc_id
        self.entry = s
        self.is_new = doc_id is None
        self.is_modified = False
        self.created = None
        self.modified = None
        self.object_hsh = {}    # key, val -> object version of raw string for tinydb 
        self.askreply= {}       # key, val -> display version raw string
        self.pos_hsh = {}       # (beg, end) -> (key, val)
        self.keyvals = [] 

        self.messages = []
        self.active = ()
        self.interval = ()
        self.item_hsh = {}      # key -> obj
        # Note: datetime(s) require timezone and at requires itemtype
        # all else do not need item_hsh
        self.keys = {
                'itemtype': ["item type", "character from * (event), - (task), % (record) or ! (inbox)", self.do_itemtype],
                'summary': ["summary", "brief item description", self.do_summary],
                '+': ["include", "list of datetimes to include", self.do_datetimes],
                '-': ["exclude", "list of datetimes to exclude", self.do_datetimes],
                'a': ["alerts", "list of alerts", do_alert],
                'b': ["beginby", "number of days for beginby notices", do_beginby],
                'c': ["calendar", "calendar", do_string],
                'd': ["description", "item details", do_string],
                'e': ["extent", "timeperiod", do_period],
                'f': ["finish", "completion datetime", self.do_datetime],
                'g': ["goto", "url or filepath", do_string],
                'h': ["completions", "list of completion datetimes", self.do_datetimes],
                'i': ["index", "colon delimited string", do_string],
                'l': ["location", "location or context", do_string],
                'm': ["memo", "", do_string],
                'n': ["attendees", "list of 'name <email address>'", do_stringlist],
                'o': ["overdue", "character from (r)estart, (s)kip or (k)eep", do_overdue],
                'p': ["priority", "priority from 1 (highest) to 9 (lowest)", do_priority],
                's': ["start", "starting date or datetime", self.do_datetime],
                't': ["tags", "list of tags", do_stringlist],
                'x': ["expansion", "expansion key", do_string],
                'z': ["timezone", "", self.do_timezone],
                '?': ["@-key", "", self.do_at],

                'rr': ["repetition frequency", "character from (y)ear, (m)onth, (w)eek,  (d)ay, (h)our, mi(n)ute", do_frequency],
                'ri': ["interval", "positive integer", do_interval],
                'rm': ["monthdays", "list of integers 1 ... 31, possibly prepended with a minus sign to count backwards from the end of the month", do_monthdays], 
                'rE': ["easterdays", "number of days before (-), on (0) or after (+) Easter", do_easterdays],
                'rh': ["hours", "list of integers in 0 ... 23", do_hours],
                'rM': ["months", "list of integers in 1 ... 12", do_months], 
                'rn': ["minutes", "list of integers in 0 ... 59", do_minutes], 
                'rw': ["weekdays", "list from SU, MO, ..., SA, possibly prepended with a positive or negative integer", do_weekdays],
                'rW': ["week numbers", "list of integers in 1, ... 53", do_weeknumbers],
                'rc': ["count", "integer number of repetitions", do_count],
                'ru': ["until", "datetime", self.do_datetime],
                'rs': ["set positions", "integer", do_setpositions],
                'r?': ["repetition &-key", "enter &-key", self.do_ampr],

                'jj': ["summary", "job summary", do_string],
                'ja': ["alert", "list of timeperiod before task start followed by a colon and a command and, optionally, command arguments", do_alert],
                'jb': ["beginby", " integer number of days", do_beginby],
                'jd': ["description", " string", do_string],
                'je': ["extent", " timeperiod", do_period],
                'jf': ["finished", " datetime", self.do_datetime],
                'ji': ["unique id", " integer or string", do_string],
                'jl': ["location", " string", do_string],
                'jm': ["memo", "string", do_string],
                'jp': ["prerequisite ids", "list of ids of immediate prereqs", do_stringlist],
                'js': ["start", "timeperiod before task start when job is due", do_period],
                'j?': ["job &-key", "enter &-key", self.do_ampj],
                }
        if not self.entry:
            self.text_changed('', 0)
        self.etmdb = TinyDB('db.json', storage=serialization, default_table='items', indent=1, ensure_ascii=False)
        self.etmdb_query = self.etmdb.table('items', cache_size=None)

    def edit_item(self, item_id=None, entry=""):
        if not (item_id and entry):
            logger.info(f"item_id: {item_id}; entry: {entry}")
            return None
        item_hsh = ETMDB_QUERY.get(doc_id=item_id)
        if item_hsh:
            self.item_id = item_id
            self.item_hsh = item_hsh # created and modified entries
            self.entry = entry


    def cursor_changed(self, pos):
        # ((17, 24), ('e', '90m'))
        self.interval, self.active = active_from_pos(self.pos_hsh, pos)
        logger.info(f"interval: {self.interval}; active: {self.active}")


    def text_changed(self, s, pos):
        """

        """
        logger.info(f"s: {s}; pos: {pos}")
        self.entry = s
        self.pos_hsh, keyvals = process_entry(s)
        removed, changed = listdiff(self.keyvals, keyvals)
        # only process changes for kv entries
        update_timezone = False
        for kv in removed + changed:
            if kv[0] == 'z':
                update_timezone = True
                break
        if update_timezone:
            changed += [kv for kv in self.keyvals if kv[0] in ['s', 'ru',  '+', '-']]

        for kv in removed:
            if kv in self.object_hsh:
                del self.object_hsh[kv]
            if kv in self.askreply:
                del self.askreply[kv]
        for kv in changed:
            self.update_keyval(kv)

        self.keyvals = [kv for kv in keyvals]


    def update_keyval(self, kv):
        """
        """
        logger.info(f"updating kv: {kv}")
        key, val = kv

        if key in self.keys:
            a, r, do = self.keys[key]
            ask = a
            msg = self.check_allowed(key)
            if msg:
                obj = None
                reply = msg
            else: # only do this for allowed keys
                msg = self.check_requires(key)
                if msg:
                    obj = None
                    reply = msg
                else:
                    obj, rep = do(val)
                    reply = rep if rep else r
                    if obj:
                        self.object_hsh[kv] = obj
                    else:
                        if kv in self.object_hsh:
                            del self.object_hsh[kv]
            # logger.info(f"kv: {kv}; ask: {ask}; reply: {reply}")
            self.askreply[kv] = (ask, reply)
            if obj:
                logger.info(f"askreply: {self.askreply}")
        else:
            display_key = f"@{key}" if len(key) == 1 else f"&{key[-1]}"
            self.askreply[kv] = ('unrecognized key', f'{display_key} is invalid')

    def update_item_hsh(self):
        self.item_hsh = {}
        cur_hsh = {}
        cur_key = None
        logger.info(f"pos_hsh: {self.pos_hsh.items()}")
        logger.info(f"object_hsh: {self.object_hsh.items()}")
        for pos, (k, v) in self.pos_hsh.items():
            obj = self.object_hsh[(k, v)]
            if k == 'a':
                self.item_hsh.setdefault(k, []).append(obj)
            elif k in ['rr', 'jj']:
                if cur_hsh:
                    # starting new rrule or job - append the old
                    self.item_hsh.setdefault(cur_key, []).append(cur_hsh)
                cur_key = k[0]
                cur_hsh = {k[0]: obj}
            elif k[0] in ['r', 'j']:
                if cur_hsh:
                    cur_hsh[k[1]] = obj
                else:
                    # shouldn't happen
                    pass
            else:
                if cur_key:
                    self.item_hsh.setdefault(cur_key, []).append(cur_hsh)
                    cur_key = None
                    cur_hsh = {}
                self.item_hsh[k] = obj
        if cur_key:
            # record the last if necessary 
            self.item_hsh.setdefault(cur_key, []).append(cur_hsh)
            cur_key = None
            cur_hsh = {}

        now = pendulum.now('UTC')
        # keys = [x for x in self.item_hsh.keys()]
        # keys.sort()
        # hsh = {k: self.item_hsh[k] for k in keys}
        if self.doc_id is None:
            # creating a new item
            self.created = now
            self.item_hsh['created'] = self.created
            self.doc_id = self.etmdb.insert(self.item_hsh)
        else:
            # editing an existing item
            self.item_hsh['created'] = self.created
            self.item_hsh['modified'] = now
            self.etmdb.write_back([self.item_hsh], doc_ids=[self.doc_id])
        logger.info(f"doc_id: {self.doc_id}; item_hsh: {self.item_hsh}")


    def check_requires(self, key):
        """
        Check that key has the prerequisite entries.
        if key in requires, check that each key in requires[k] has a corresponding key, val in keyvals: [(k, v), (k, v), ...]
        """

        missing = []
        if key in requires:
            cur_keys = [k for (k, v) in self.keyvals]
            missing = [f"@{k}" for k in requires[key] if k not in cur_keys]

        if missing:
            display_key = f"@{key[0]}" if len(key) == 1 or key[-1] in 'rj' else f"&{key[-1]}"
            return f"Required for {display_key} but missing: {', '.join(missing)}"
        else:
            return ""

    def check_allowed(self, key):
        """
        Check that key is allowed for the given item type or @-key.
        """
        if key in ['?', 'r?', 'j?', 'itemtype', 'summary']:
            return ""
        if key not in self.keys:
            if len(key) > 1:
                msg = f"&{key[1]} is invalid with @{key[0]}"
            else:
                msg = f"@{key} is invalid"
            return msg
        itemtype = self.item_hsh.get('itemtype', None)
        if itemtype:
            if key not in allowed[itemtype]:
                display_key = f"@{key}" if len(key) == 1 else f"&{key[-1]}"
                return f"{display_key} is not allowed for itemtype {itemtype} ({type_keys[itemtype]})"
            else:
                return ""
        else:
            return "missing itemtype"


    def do_at(self, arg=''):
        """
        Need access to itemtype - hence in Item()
        >>> item = Item()
        >>> item.do_at()
        (None, 'The type character must be entered before any @-keys')
        >>> item.item_hsh['itemtype'] = '*'
        >>> obj, rep = item.do_at()
        >>> print(rep)
        required: @s (start)
        available: @+ (include), @- (exclude), @a (alerts),
          @b (beginby), @c (calendar), @d (description),
          @e (extent), @g (goto), @i (index), @l (location),
          @m (memo), @n (attendees), @o (overdue), @s (start),
          @t (tags), @x (expansion), @z (timezone)
        """
        itemtype = self.item_hsh.get('itemtype', '')
        if itemtype:
            # only @-keys; allow a, rr and jj more than once
            already_entered = [k for (k, v) in self.keyvals if len(k) == 1 and k not in ['a']]
            logger.info(f"already_entered: {already_entered}")
            req = [k for k, v in self.keys.items() if (k in required[itemtype] and k not in already_entered)]
            require = [f"@{k}_({v[0]})" for k, v in self.keys.items() if (k in required[itemtype] and k != '?' and k not in already_entered)] 
            logger.info(f"require: {require}; required: {required[itemtype]}")
            # allow rr to be entered as r and jj as j
            avail = [x[0] for x in allowed[itemtype] if len(x) == 1 or x in ['rr', 'jj'] ]
            allow = [f"@{k}_({v[0]})" for k, v in self.keys.items() if (k in avail and k != '?' and k not in already_entered)] 
            # prompt = f"{type_keys[itemtype]} @-keys:\n"
            prompt = ""
            if require:
                prompt += wrap(f"required: {', '.join(require)}", 2) + "\n"
                # prompt += "required: " +  wrap(, 2, 56) + "\n"
            if allow:
                prompt += wrap(f"available: {', '.join(allow)}", 2)
                # prompt += "allowed: " + wrap(", ".join(allow), 2, 56)
            rep = prompt.replace('_', ' ')
        else:
            rep = "The type character must be entered before any @-keys"

        return None, rep

    def do_ampr(self, arg=''):
        """
        Need access to &-keys and names - hence in Item()
        >>> item = Item()
        >>> obj, rep = item.do_ampr()
        >>> print(rep)
        repetition &-keys: &i (interval), &m (monthdays),
            &E (easterdays), &h (hours), &M (months),
            &n (minutes), &w (weekdays), &W (week numbers),
            &c (count), &u (until), &s (set positions)
        """
        keys = [f"&{k[1]}_({v[0]})" for k, v in self.keys.items() if k.startswith('r') and k[1] not in 'r?'] 
        rep = wrap("repetition &-keys: " + ", ".join(keys), 4, 60).replace('_', ' ')

        return None, rep


    def do_ampj(self, arg=''):
        """
        Need access to &-keys and names - hence in Item()
        >>> item = Item()
        >>> obj, rep = item.do_ampj()
        >>> print(rep)
        job &-keys: &a (alert), &b (beginby), &d (description),
            &e (extent), &f (finished), &i (unique id),
            &l (location), &m (memo), &p (prerequisite ids),
            &s (start)
        """
        keys = [f"&{k[1]}_({v[0]})" for k, v in self.keys.items() if k.startswith('j') and k[1] not in 'j?'] 
        rep = wrap("job &-keys: " + ", ".join(keys), 4, 60).replace('_', ' ')

        return None, rep


    def do_itemtype(self, arg):
        """
        >>> item = Item()
        >>> item.do_itemtype('')
        (None, 'Choose a character from * (event), - (task), % (record) or ! (inbox)')
        >>> item.do_itemtype('+')
        (None, "'+' is invalid. Choose a character from * (event), - (task), % (record) or ! (inbox)")
        >>> item.do_itemtype('*')
        ('*', '* (event)')
        """
        a, r, d = self.keys['itemtype']
        if not arg:
            obj = None
            rep = f"Choose a {r}"
        elif arg in type_keys:
            obj = arg
            rep = f"{arg} ({type_keys[arg]})"
            self.item_hsh['itemtype'] = obj 
        else:
            obj = None
            rep = f"'{arg}' is invalid. Choose a {r}"
            self.item_hsh['itemtype'] = '' 
        return obj, rep

    def do_summary(self, arg):
        if not self.item_hsh['itemtype']:
            return None, "a valid itemtype must be provided"
        obj, rep = do_string(arg)
        # rep = f"{type_keys[self.item_hsh['itemtype']]} sum: {rep}"
        if obj:
            self.item_hsh['summary'] = obj
            rep = arg
        elif 'summary' in self.item_hsh:
            del self.item_hsh['summary']

        return obj, rep


    def do_datetime(self, arg):
        """
        >>> item = Item()
        >>> item.do_datetime('fr')
        (None, "'fr' is incomplete or invalid")
        >>> item.do_datetime('2019-01-25')
        (Date(2019, 1, 25), 'Fri Jan 25 2019')
        >>> item.do_datetime('2019-01-25 2p')
        (DateTime(2019, 1, 25, 14, 0, 0, tzinfo=Timezone('America/New_York')), 'Fri Jan 25 2019 2:00pm EST')
        """
        obj = None
        tz = self.item_hsh.get('z', None)
        logger.info(f"got tz = {tz}")
        ok, res, z = parse_datetime(arg, tz)
        logger.info(f"tz: {tz}; ok: {ok}; res: {res}; z={z}")
        if ok:
            obj = res 
            rep = f"local datetime: {format_datetime(obj)[1]}" if ok == 'aware' else format_datetime(obj)[1]
        else:
            rep = res
        return obj, rep

    def do_datetimes(self, args):
        """
        >>> item = Item()
        >>> item.do_datetimes('2019-1-25 2p, 2019-1-30 4p')
        ([DateTime(2019, 1, 25, 14, 0, 0, tzinfo=Timezone('America/New_York')), DateTime(2019, 1, 30, 16, 0, 0, tzinfo=Timezone('America/New_York'))], 'datetimes: 2019-01-25 2:00pm, 2019-01-30 4:00pm')
        >>> print(item.do_datetimes('2019-1-25 2p, 2019-1-30 4p, 2019-2-29 8a')[1])
        datetimes: 2019-01-25 2:00pm, 2019-01-30 4:00pm
        incomplete or invalid datetimes:  2019-2-29 8a
        """
        rep = args
        obj = None
        tz = self.item_hsh.get('z', None)
        args = [x.strip() for x in args.split(',')]
        obj = []
        rep = []
        bad = []
        all_ok = True
        for arg in args:
            if not arg:
                continue
            ok, res, tz = parse_datetime(arg, tz)
            if ok:
                obj.append(res)
                rep.append(format_datetime(res, True)[1])
            else:
                all_ok = False
                bad.append(arg)
        obj = obj if all_ok else None 
        rep = f"local datetimes: {', '.join(rep)}" if (tz is not None and tz != 'float') else f"datetimes: {', '.join(rep)}" 
        if bad:
            rep += f"\nincomplete or invalid datetimes:  {', '.join(bad)}"
        return obj, rep

    def do_timezone(self, arg=None):
        """
        >>> item = Item()
        >>> item.do_timezone()
        ('local', 'local')
        >>> item.do_timezone('float')
        ('float', 'float')
        >>> item.do_timezone('local')
        ('local', 'local')
        >>> item.do_timezone('UTC')
        ('UTC', 'timezone: UTC')
        >>> item.do_timezone('Europe/Paris')
        ('Europe/Paris', 'timezone: Europe/Paris')
        >>> item.do_timezone('US/Pacifc')
        (None, "incomplete or invalid timezone: 'US/Pacifc'")
        """
        logger.info(f"do_timezone arg: {arg}")
        if arg is None:
            obj = rep = 'local'
            if 'z' in self.item_hsh:
                del self.item_hsh['z']
        elif arg in ['local', 'float']:
            self.item_hsh['z'] = arg 
            obj = rep = arg
        elif not arg.strip():
            obj = None
            rep = ""
        else:
            try:
                Timezone(arg)
                obj = rep = arg
                self.item_hsh['z'] = obj 
                logger.info(f"{obj}")
                logger.info(f"item_hsh: {self.item_hsh}")
                rep = f"timezone: {obj}"
            except:
                obj = None
                rep = f"incomplete or invalid timezone: '{arg}'"
                if 'z' in self.item_hsh:
                    del self.item_hsh['z']
        # if obj:
        #     ud = [kv for kv in self.keyvals if kv[0] in ['s', 'u',  '+', '-']]
        #     logger.info(f"ud: {ud}")
        #     for kv in ud:
        #         self.update_keyval(kv)
        return obj, rep



def listdiff(old_lst, new_lst):
    """
    >>> old_lst = [('s', '2p fri'), ('z', 'US/Eastern')]
    >>> new_lst = [('s', '3p fri'), ('e', '90m'), ('z', 'US/Eastern')] 
    >>> listdiff(old_lst, new_lst)
    ([('s', '2p fri')], [('s', '3p fri'), ('e', '90m')])
    """
    removed = [x for x in old_lst if x not in new_lst]
    changed = [x for x in new_lst if x not in old_lst]
    return removed, changed

def dictdiff(old_hsh, new_hsh):
    """
    >>> old_hsh = {'a': 1, 'b': 2}
    >>> new_hsh = {'b': 3, 'c': 5}
    >>> dictdiff(old_hsh, new_hsh)
    ({'a': 1}, {'b': 3, 'c': 5})
    """
    removed = {}
    changed = {}
    for k, v in old_hsh.items():
        if k not in new_hsh:
            removed[k] = v
    for k, v in new_hsh.items():
        if k not in old_hsh or v != old_hsh[k]:
            changed[k] = v
    return removed, changed

def verify_entry(entry, pos_hsh, ent_hsh, pos):
    """

    """
    state = None
    if not entry or not pos_hsh:
        ask, reply = (('say', type_prompt), ('say', item_types)),
    elif entry[0] not in type_keys:
        ask, reply = (('say', type_prompt), ('warn', f"Item type character '{entry[0]}' is invalid"))

        interval, (k, v) = active_from_pos(pos_hsh, 0)

    ask, reply = ask_reply[what]
    return ask, reply


# item_hsh = {}
# def check_entry(s, cursor_pos=0):
#     # """
#     # Process 's' as the current entry with the cursor at cursor_pos and return the relevant ask and reply prompts.
#     # >>> check_entry('')
#     # (('say', 'item type character:'), ('say', 'item type characters:\\n    *: event\\n    -: task\\n    %: record\\n    !: inbox'), {})
#     # >>> check_entry('^')
#     # (('say', 'item type character:'), ('warn', "invalid item type character: '^'"), {})
#     # >>> check_entry('- todo')
#     # (('say', 'task summary:'), ('say', 'Enter the summary for the task followed, optionally, by @key and value pairs'), {})
#     # >>> check_entry('- todo @s 2019-01-22 4p @', 25)
#     # """
#     global item_hsh
#     pos_hsh, keyvals = process_entry(s)
#     hsh = {}

#     ask = ('say', '')
#     reply = ('say', '')
#     if not s or not pos_hsh:
#         ask = ('say', type_prompt)
#         reply = ('say', item_types)
#         return ask, reply, hsh

#     interval, (key, itemtype) = active_from_pos(pos_hsh, 0)
#     if itemtype not in type_keys:
#         ask = ('say', type_prompt)
#         reply = ('warn', u"invalid item type character: '{0}'".format(itemtype))
#         return ask, reply, hsh

#     interval, res = active_from_pos(pos_hsh, cursor_pos)
#     at_key = amp_key = None
#     act_key = act_val = None
#     if res:
#         at_key = res[0][0]
#         amp_key = res[0][1]
#         act_key = amp_key if amp_key else at_key
#         act_val = res[1]
#     if act_val and act_val[-1] == '@':
#         amp_entry = False
#         at_entry = True
#     elif act_val and act_val[-1] == '&':
#         amp_entry = True
#         at_entry = False
#     else:
#         amp_entry = False
#         at_entry = False


#     if at_entry:
#         ask =  ('say', "{} @keys:".format(type_keys[itemtype]))
#         current_required = ["@{} {}".format(x, at_keys[x]) for x in required[itemtype] if x not in hsh]
#         reply_str = ""
#         if current_required:
#             reply_str += "Required: {}".format(", ".join(current_required))
#         current_allowed = ["@{} {}".format(x, at_keys[x]) for x in allowed[itemtype] if x not in hsh or x in 'ajr']
#         if current_allowed:
#             reply_str += "Allowed: {}".format(", ".join(current_allowed))
#         reply = ('say', reply_str)
#     elif amp_entry:
#         ask = ('say', "&key for @{}?".format(act_key))
#         reply =  ('say', "Allowed: {}".format(", ".join(["&{} {}".format(key, amp_keys[act_key][key]) for key in amp_keys[act_key] if key != 'r'])))
#     elif amp_key:
#         if amp_key in amp_keys[at_key]:
#             ask = ('say', f"{amp_keys[at_key][amp_key]}?")
#         else:
#             ask =  ('say', f"&{amp_key} is not allowed for @{at_key}")

#             reply =  ('say', "Allowed: {}".format(", ".join(["&{} {}".format(key, amp_keys[act_key][key]) for key in amp_keys[act_key] if key != 'r'])))

#     elif at_key:
#         if at_key in at_keys:
#             ask = ('say', "{0}?".format(at_keys[at_key]))

#         else:
#             ask =  ('say', "{} @keys:".format(type_keys[itemtype]))

#         if at_key == itemtype:
#             ask = ('say', "{} summary:".format(type_keys[itemtype]))
#             reply = ('say', 'Enter the summary for the {} followed, optionally, by @key and value pairs'.format(type_keys[itemtype]))

#         else:
#             ok, res = check_requires(act_key, hsh)
#             if not ok:
#                 ask = ('say', '{0}'.format(at_keys[act_key]))
#                 reply = res

#             elif act_key in allowed[itemtype]:

#                 if amp_entry:
#                     ask = ('say', "&key for @{}?".format(act_key))
#                     reply =  ('say', "Allowed: {}".format(", ".join(["&{} {}".format(key, amp_keys[act_key][key]) for key in amp_keys[act_key] if key != 'r'])))
#                 elif act_key in deal_with:
#                     top, bot, obj = deal_with[act_key](hsh)
#                     ask = ('say', top)
#                     reply = ('say', "{}".format(bot))
#                     if obj:
#                         item_hsh[act_key] = obj
#                         # hsh[act_key] = obj
#                 else:
#                     top, bot, obj = deal_with_missing(hsh, act_key)
#                     if obj:
#                         item_hsh[act_key] = obj
#             else:
#                 reply = ('warn', "{0} is not allowed for item type '{1}'".format(act_key, itemtype))
#     else:
#         reply = ('warn', 'no act_key')


#     if 'summary' in hsh:
#         item_hsh['summary'] = hsh['summary']

#     missing = [k for k in item_hsh if k not in hsh]
#     for k in missing:
#         del item_hsh[k]

#     # for testing and debugging:
#     if testing:
#         reply = (reply[0], reply[1]) 
#         # reply = (reply[0], reply[1] + f"\n{item_details(item_hsh, edit=True)}\n\ncursor pos: {cursor_pos}; active entry: '{act_key}' -> {act_val}\nhsh: {hsh}\nitem_hsh: {item_hsh}") # .format(at_entry, act_key, act_val, cursor_pos,  amp_entry, amp_key, at_tups, at_parts, hsh))
#         # reply = (reply[0], reply[1] + f"\n{hsh}\n\ncursor pos: {cursor_pos}; active entry: {res} '{act_key}' -> {act_val}\n{pos_hsh}\nat_key: {at_key}; at_entry: {at_entry}\namp_key: {amp_key}; amp_entry: {amp_entry}") # .format(at_entry, act_key, act_val, cursor_pos,  amp_entry, amp_key, at_tups, at_parts, hsh))

#     return ask, reply, hsh


def parse_datetime(s, z=None):
    """
    's' will have the format 'datetime string' Return a 'date' object if the parsed datetime is exactly midnight. Otherwise return a naive datetime object if 'z == float' or an aware datetime object converting to UTC using tzlocal if z == None and using the timezone specified in z otherwise.
    >>> dt = parse_datetime("2015-10-15 2p")
    >>> dt[1]
    DateTime(2015, 10, 15, 14, 0, 0, tzinfo=Timezone('America/New_York'))
    >>> dt = parse_datetime("2015-10-15")
    >>> dt[1]
    Date(2015, 10, 15)

    To get a datetime for midnight, schedule for 1 second later and note that the second is removed from the datetime:
    >>> dt = parse_datetime("2015-10-15 00:00:01")
    >>> dt[1]
    DateTime(2015, 10, 15, 0, 0, 1, tzinfo=Timezone('America/New_York'))
    >>> dt = parse_datetime("2015-10-15 2p", "float")
    >>> dt[1]
    DateTime(2015, 10, 15, 14, 0, 0)
    >>> dt[1].tzinfo == None
    True
    >>> dt = parse_datetime("2015-10-15 2p", "US/Pacific")
    >>> dt
    ('aware', DateTime(2015, 10, 15, 21, 0, 0, tzinfo=Timezone('UTC')), 'US/Pacific')
    >>> dt[1].tzinfo
    Timezone('UTC')
    >>> dt = parse_datetime("2019-02-01 12:30a", "Europe/Paris")
    >>> dt
    ('aware', DateTime(2019, 1, 31, 23, 30, 0, tzinfo=Timezone('UTC')), 'Europe/Paris')
    """
    if z is None:
        tzinfo = 'local'
        ok = 'local'
    elif z == 'float':
        tzinfo = None
        ok = 'float'
    else:
        tzinfo = z
        ok = 'aware'

    if not s:
        return False, '', z
    try:
        res = parse(s, tz=tzinfo)
    except:
        return False, f"'{s}' is incomplete or invalid", z
    else:
        if (tzinfo is 'local' or tzinfo == 'float') and (res.hour, res.minute, res.second, res.microsecond) == (0, 0, 0, 0):
            return 'date', res.replace(tzinfo='Factory').date(), z
        elif ok == 'aware':
            return ok, res.in_timezone('UTC'), z
        else:
            return ok, res, z

def timestamp(arg):
    """
    Fuzzy parse a datetime string and return the YYYYMMDDTHHMM formatted version.
    >>> timestamp("6/16/16 4p")
    (True, DateTime(2016, 6, 16, 16, 0, 0, tzinfo=Timezone('UTC')))
    >>> timestamp("13/16/16 2p")
    (False, 'invalid time-stamp: 13/16/16 2p')
    """
    if type(arg) is pendulum.DateTime:
        return True, arg
    try:
        # res = parse(arg).strftime(ETMFMT)
        res = parse(arg)
    except:
        return False, 'invalid time-stamp: {}'.format(arg)
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

def plain_datetime(obj):
    return format_datetime(obj, short=True)

def format_datetime(obj, short=False):
    """
    >>> format_datetime(parse_datetime("20160710T1730")[1])
    (True, 'Sun Jul 10 2016 5:30pm EDT')
    >>> format_datetime(parse_datetime("2015-07-10 5:30p", "float")[1])
    (True, 'Fri Jul 10 2015 5:30pm')
    >>> format_datetime(parse_datetime("20160710")[1])
    (True, 'Sun Jul 10 2016')
    >>> format_datetime(parse_datetime("2015-07-10", "float")[1])
    (True, 'Fri Jul 10 2015')
    >>> format_datetime("20160710T1730")
    (False, 'The argument must be a pendulum date or datetime.')
    >>> format_datetime(parse_datetime("2019-02-01 12:30a", "Europe/Paris")[1])
    (True, 'Thu Jan 31 2019 6:30pm EST')
    >>> format_datetime(parse_datetime("2019-01-31 11:30p", "Europe/Paris")[1])
    (True, 'Thu Jan 31 2019 5:30pm EST')
    """

    short_date_fmt = "YYYY-MM-DD"
    long_date_fmt = "ddd MMM D YYYY"

    date_fmt = "YYYY-MM-DD" if short else "ddd MMM D YYYY"
    time_fmt = "h:mmA" if ampm else "H:mm"

    if type(obj) == pendulum.Date:
        return True, obj.format(date_fmt)

    if type(obj) != pendulum.DateTime:
        return False, "The argument must be a pendulum date or datetime."

    if obj.format('Z') == '':
        # naive datetime
        if (obj.hour, obj.minute, obj.second, obj.microsecond) == (0, 0, 0, 0):
            # treat as date
            return True, obj.format(date_fmt)
        res = obj.format(f"{date_fmt} {time_fmt}")
    else:
        # aware datetime
        obj = obj.in_timezone('local')
        if not short: time_fmt += " zz"
        res = obj.format(f"{date_fmt} {time_fmt}")

    if ampm:
        res = res.replace('AM', 'am')
        res = res.replace('PM', 'pm')
    logger.info(f"res: {res}")
    return True, res


def format_datetime_list(obj_lst):
    ret = ", ".join([format_datetime(x)[1] for x in obj_lst])
    return ret

def plain_datetime_list(obj_lst):
    ret = ", ".join([plain_datetime(x)[1] for x in obj_lst])
    return ret

def format_duration(obj):
    """
    >>> td = pendulum.duration(weeks=1, days=2, hours=3, minutes=27)
    >>> format_duration(td)
    '1w2d3h27m'
    """
    if not isinstance(obj, pendulum.Duration):
        return None
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
        print('format_duration', e)
        print(obj)
        return None

def format_duration_list(obj_lst):
    try:
        ret = ", ".join([format_duration(x) for x in obj_lst])
        return ret
    except Exception as e:
        print('format_duration_list', e)
        print(obj_lst)




period_regex = re.compile(r'(([+-]?)(\d+)([wdhm]))+?')
threeday_regex = re.compile(r'(MON|TUE|WED|THU|FRI|SAT|SUN)', re.IGNORECASE)
anniversary_regex = re.compile(r'!(\d{4})!')

period_hsh = dict(
    z=pendulum.duration(seconds=0),
    m=pendulum.duration(minutes=1),
    h=pendulum.duration(hours=1),
    d=pendulum.duration(days=1),
    w=pendulum.duration(weeks=1),
        )

def parse_duration(s):
    """\
    Take a period string and return a corresponding pendulum.duration.
    Examples:
        parse_duration('-2w3d4h5m')= Duration(weeks=-2,days=3,hours=4,minutes=5)
        parse_duration('1h30m') = Duration(hours=1, minutes=30)
        parse_duration('-10m') = Duration(minutes=10)
    where:
        w: weeks
        d: days
        h: hours
        m: minutes

    >>> 3*60*60+5*60
    11100
    >>> parse_duration("2d-3h5m")[1]
    Duration(days=1, hours=21, minutes=5)
    >>> pendulum.datetime(2015, 10, 15, 9, 0, tz='local') + parse_duration("-25m")[1]
    DateTime(2015, 10, 15, 8, 35, 0, tzinfo=Timezone('America/New_York'))
    >>> pendulum.datetime(2015, 10, 15, 9, 0) + parse_duration("1d")[1]
    DateTime(2015, 10, 16, 9, 0, 0, tzinfo=Timezone('UTC'))
    >>> pendulum.datetime(2015, 10, 15, 9, 0) + parse_duration("1w-2d+3h")[1]
    DateTime(2015, 10, 20, 12, 0, 0, tzinfo=Timezone('UTC'))
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

def setup_logging(level, dir=None, file=None):
    """
    Setup logging configuration. Override root:level in
    logging.yaml with default_level.
    """
    # import logging
    # import logging.config
    # logger = logging.getLogger()

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
    if file:
        logger.info(f'logging for file: {file}\n    logging at level: {loglevel}\n    logging to file: {logfile}')
    else:
        logger.info(f'logging at level: {loglevel}\n    logging to file: {logfile}')


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


class DataView(object):

    def __init__(self, loglevel=1, dtstr=None, weeks=1, plain=False):
        self.active_view = 'agenda'  # (other views: history)
        # self.activeYrWk = self.currentYrWk = None
        self.current = []
        self.num2id = []
        self.current_row = 0
        self.plain = plain
        self.weeks = weeks
        self.agenda_view = ""
        self.busy_view = ""
        self.history_view = ""
        self.cache = {}
        self.itemcache = {}
        self.set_now(dtstr) 
        self.views = {
                'a': 'agenda',
                'b': 'busy',
                'h': 'history',
                'i': 'index',
                'n': 'next',
                'r': 'relevant',
                't': 'tags',
                }

        self.edit_item = None
        self.is_showing_details = False
        self.is_showing_help = False
        self.is_editing = False
        self.is_showing_items = True
        self.refreshRelevant()
        self.currYrWk()

    def set_now(self, dtstr=None):
        # self.now = pendulum.now() if dtstr is None else pendulum.parse(dtstr)
        self.now = pendulum.parse(dtstr, tz='local') if dtstr else pendulum.now('local')  

    def set_active_view(self, c):
        self.active_view = self.views.get(c, 'agenda')

    def show_active_view(self):
        if self.active_view == 'agenda':
            return self.agenda_view
        elif self.active_view == 'busy':
            return self.busy_view
        elif self.active_view == 'history':
            self.history_view, self.num2id = show_history()
            return self.history_view

    def toggle_agenda_busy(self):
        if self.active_view == 'agenda':
            self.active_view = 'busy'
            return self.busy_view
        elif self.active_view == 'busy':
            self.active_view = 'agenda'
            return self.agenda_view
        else:
            self.active_view = 'agenda'
            return self.agenda_view

    def nextYrWk(self):
        self.activeYrWk = nextWeek(self.activeYrWk) 
        self.refreshAgenda()

    def prevYrWk(self):
        self.activeYrWk = prevWeek(self.activeYrWk) 
        self.refreshAgenda()

    def currYrWk(self):
        """Set the active week to one containing today."""
        self.currentYrWk = self.activeYrWk = getWeekNum(self.now)
        self.refreshAgenda()

    def dtYrWk(self, dtstr):
        dt = pendulum.parse(dtstr)
        self.activeYrWk = getWeekNum(dt)
        self.refreshAgenda()

    def refreshRelevant(self):
        """
        Called to set the relevant items for the current date and to change the currentYrWk and activeYrWk to that containing the current date.
        """
        # self.now = pendulum.now()
        self.set_now()
        self.currentYrWk = self.activeYrWk = self.now.isocalendar()[:2]
        self.current, self.alerts = relevant(self.now)
        self.refreshCache()

    def refreshAgenda(self):
        if self.activeYrWk not in self.cache:
            self.cache.update(schedule(yw=self.activeYrWk, current=self.current, now=self.now))
        self.agenda_view, self.busy_view, self.num2id = self.cache[self.activeYrWk]

    def show_details(self):
        self.is_showing_details = True 

    def hide_details(self):
        self.is_showing_details = False 

    def get_details(self, num=None, edit=False):
        logger.info(f"num: {num}")
        if num is None:
            return None, ''

        self.current_row = num
        item_id = self.num2id.get(num, None)
        logger.info(f"item_id: {item_id}")
        if item_id is None:
            return None, ''

        if not edit and item_id in self.itemcache:
            logger.info(f"item_id in cache: {item_id}; str: {self.itemcache[item_id]}")
            return item_id, self.itemcache[item_id]
        item = ETMDB_QUERY.get(doc_id=item_id)
        if item:
            self.itemcache[item_id] = item_details(item, edit)
            logger.info(f"item_id not in cache: {item_id}; item: {item}")
            return item_id, self.itemcache[item_id] 
        else:
            logger.info(f"query failed for {item_id}; item: {item}")

        return None, ''

    def clearCache(self):
        self.cache = {}

    def refreshCache(self):
        self.cache = schedule(self.currentYrWk, self.current, self.now, 5, 20)



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


def set_summary(s, dt=pendulum.now()):
    """
    Replace the anniversary string in s with the ordinal represenation of the number of years between the anniversary string and dt.
    >>> set_summary('!1944! birthday', pendulum.date(2017, 11, 19))
    '73rd birthday'
    >>> set_summary('!1978! anniversary', pendulum.date(2017, 11, 19))
    '39th anniversary'
    """
    if not dt:
        dt = pendulum.now()

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


def do_string(arg):
    try:
        obj = str(arg)
        rep = arg
    except:
        obj = None
        rep = f"invalid: {arg}" 
    return obj, rep

def do_stringlist(args):
    """
    >>> do_stringlist('')
    (None, '')
    >>> do_stringlist('red')
    (['red'], 'red')
    >>> do_stringlist('red,  green,blue')
    (['red', 'green', 'blue'], 'red, green, blue')
    """
    obj = None
    rep = args
    if args:
        args = [x.strip() for x in args.split(',')]
        all_ok = True
        obj_lst = []
        rep_lst = []
        for arg in args:
            try:
                res = str(arg)
                obj_lst.append(res)
                rep_lst.append(res)
            except:
                all_ok = False
                rep_lst.append(f"~{arg}~")
        obj = obj_lst if all_ok else None
        rep = ", ".join(rep_lst)
    return obj, rep

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
{%- if 'e' in h %}{{ " @e {}".format(in2str(h['e'])) }}{% endif %}\
{%- if 'z' in h %}{{ " @z {}".format(h['z']) }}{% endif %}\
{%- endset %}\
{{ wrap(title) }}
{% if 'f' in h %}{{ "@f {} ".format(dt2str(h['f'])[1]) }}
{% endif -%}\
{% if 'a' in h %}\
{%- set alerts %}\
{% for x in h['a'] %}{{ "@a {}: {} ".format(inlst2str(x[0]), ", ".join(x[1:])) }}{% endfor %}\
{% endset %}\
{{ wrap(alerts) }}
{% endif %}\
{%- set is = namespace(found=false) -%}\
{%- set index -%}\
{%- for k in ['c', 'i'] -%}\
{%- if k in h %}@{{ k }} {{ h[k] }}{% set is.found = true %} {% endif %}\
{%- endfor %}\
{%- endset %}\
{%- if is.found -%}
{{ wrap(index) }}
{% endif -%}\
{%- if 't' in h %}@t {{ "{}".format(", ".join(h['t'])) }} {% endif %}\
{%- set ls = namespace(found=false) -%}\
{%- set location -%}\
{%- for k in ['l', 'm', 'n', 'g', 'x', 'p'] -%}\
{%- if k in h %}@{{ k }} {{ h[k] }}{% set ls.found = true %} {% endif -%}\
{%- endfor -%}\
{%- endset -%}\
{%- if ls.found -%}\
{{ wrap(location) }}{% endif -%}\
{%- if 'r' in h -%}\
{%- for x in h['r'] -%}\
{%- if 'r' in x and x['r'] -%}\
{%- set rrule -%}\
{{ x['r'] }}\
{%- for k in ['i', 's', 'M', 'm', 'n', 'w', 'h', 'E', 'c'] -%}\
{%- if k in x %} {{ "&{} {}".format(k, one_or_more(x[k])) }}{%- endif %}\
{%- endfor -%}\
{% if isinstance(x, dict) and 'u' in x %}{{ " &u {} ".format(dt2str(x['u'])[1]) }}{% endif %}\
{%- endset -%}
@r {{ wrap(rrule) }}
{% endif -%}\
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
{%- endif %}
"""

display_tmpl = entry_tmpl + """\

{{ '_' * 3 }}
{% if 'created' in h %}\
created: {{ dt2str(h.created)[1] }}\
{% else %}\
created: ~ 
{%- endif %}
{% if 'modified' in h %}\
modified: {{ dt2str(h.modified)[1] }}\
{% else %}\
modified: ~ 
{%- endif %}
{% if h.doc_id %}\
id: {{ h.doc_id }}\
{% else %}\
id: ~ 
{%- endif %}
"""

jinja_entry_template = Template(entry_tmpl)
jinja_entry_template.globals['dt2str'] = plain_datetime
jinja_entry_template.globals['in2str'] = format_duration
jinja_entry_template.globals['dtlst2str'] = format_datetime_list
jinja_entry_template.globals['inlst2str'] = format_duration_list
jinja_entry_template.globals['one_or_more'] = one_or_more
jinja_entry_template.globals['isinstance'] = isinstance
jinja_entry_template.globals['wrap'] = wrap

jinja_display_template = Template(display_tmpl)
jinja_display_template.globals['dt2str'] = plain_datetime
jinja_display_template.globals['in2str'] = format_duration
jinja_display_template.globals['dtlst2str'] = plain_datetime_list
jinja_display_template.globals['inlst2str'] = format_duration_list
jinja_display_template.globals['one_or_more'] = one_or_more
jinja_entry_template.globals['isinstance'] = isinstance
jinja_display_template.globals['wrap'] = wrap

def do_beginby(arg):
    beginby_str = "an integer number of days"
    if not arg:
        return None, beginby_str
    ok, res = integer(arg, 1, None, False, 'beg')
    if ok:
        obj = res
        rep = f"beginby: {arg} day(s)"
    else:
        obj = None
        rep = f"'{arg}' is invalid. Beginby requires {beginby_str}."
    return obj, rep

def do_alert(arg):
    """
    p1, p2, ...: cmd[, arg1, arg2, ...]
    >>> do_alert('')
    (None, '')
    >>> print(do_alert('90m, 45m')[1])
    alert: 1h30m, 45m -> None
    commmand is required but missing
    >>> print(do_alert('90m, 45m, 10: d')[1])
    alert: 1h30m, 45m -> d
    incomplete or invalid periods: 10
    >>> do_alert('90m, 45m, 10m: d')
    ([[Duration(hours=1, minutes=30), Duration(minutes=45), Duration(minutes=10)], 'd'], 'alert: 1h30m, 45m, 10m -> d')
    """
    obj = None
    rep = arg
    parts = arg.split(':')
    periods = parts.pop(0)
    command = parts[0].strip() if parts else None
    if periods:
        all_ok = True
        periods = [x.strip() for x in periods.split(',')]
        obj_periods = []
        good_periods = []
        bad_periods = []
        for period in periods:
            ok, res = parse_duration(period)
            if ok:
                obj_periods.append(res)
                good_periods.append(format_duration(res))
            else:
                all_ok = False
                bad_periods.append(period)
        rep = f"alert: {', '.join(good_periods)} -> {command}"
        if bad_periods:
            obj = None
            rep += f"\nincomplete or invalid periods: {', '.join(bad_periods)}"
        elif command is None:
            obj = None
            rep += f"\ncommmand is required but missing"
        else:
            obj = [obj_periods, command]

    return obj, rep

def do_period(arg):
    """
    >>> do_period('')
    (None, 'time period')
    >>> do_period('90')
    (None, 'incomplete or invalid period: 90')
    >>> do_period('90m')
    (Duration(hours=1, minutes=30), '1h30m')
    """
    if not arg:
        return None, f"time period"
    ok, res = parse_duration(arg)
    if ok:
        obj = res
        rep = f"{format_duration(res)}"
    else:
        obj = None
        rep = f"incomplete or invalid period: {arg}"
    return obj, rep

def do_overdue(arg):
    if arg in ('k', 'r', 's'):
        return arg, arg
    else:
        return None, f"~{arg}~"

def job_datetime(arg):
    # FIXME
    return True, ''

def location(arg):
    return string(arg, 'location')


def uid(arg):
    return string(arg, 'uid')


def description(arg):
    return string(arg, 'description')


def extent(arg):
    return parse_duration(arg)


def history(arg):
    """
    Return a list of properly formatted completions.
    >>> history("4/1/2016 2p")
    (True, [DateTime(2016, 4, 1, 14, 0, 0, tzinfo=Timezone('America/New_York'))])
    >>> history(["4/31 2p", "6/1 7a"])
    (False, "'4/31 2p' is incomplete or invalid")
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

# This won't work since @z needs to be considered
def until(arg):
    """
    Return a datetime object. This will be an aware datetime in the local timezone. 
    >>> until('2019-01-03 10am')
    (True, DateTime(2019, 1, 3, 10, 0, 0, tzinfo=Timezone('America/New_York')))
    >>> until('whenever')
    (False, 'Include repetitions falling on or before this datetime.')
    """
    ok, res, tz = parse_datetime(arg)
    if ok:
        return True, res
    else:
        return False, "Include repetitions falling on or before this datetime."

def do_priority(arg):
    """
    >>> do_priority("0")
    (None, 'invalid priority: 0 is less than the allowed minimum. An integer priority number from 1 (highest), to 9 (lowest) is required')
    >>> do_priority("1")
    (1, 'priority: 1')
    """
    prioritystr = "An integer priority number from 1 (highest), to 9 (lowest)"
    if arg:
        ok, res = integer(arg, 1, 9, False, "")
        if ok:
            obj = res
            rep = f"priority: {arg}"
        else:
            obj = None
            rep = f"invalid priority: {res}. {prioritystr} is required"
    else:
        obj = None
        rep = prioritystr
    return obj, rep

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


def do_easterdays(arg):
    """
    byeaster; integer or sequence of integers numbers of days before, < 0,
    or after, > 0, Easter.
    >>> do_easterdays("0")
    ([0], '0')
    >>> do_easterdays("-364, -30, 0, 45, 260")
    ([-364, -30, 0, 45, 260], '-364, -30, 0, 45, 260')
    """
    easterstr = "easter: a comma separated list of integer numbers of days before, < 0, or after, > 0, Easter."

    if arg == 0:
        arg = [0]
    args = arg.split(',')
    if args:
        ok, res = integer_list(arg, None, None, True, 'easter')
        if ok:
            obj = res
            rep = arg
        else:
            obj = None
            rep = f"invalid easter: {res}. Required for {easterstr}"
    else:
        obj = None
        rep = easterstr
    return obj, rep

def easter(arg):
    """
    byeaster; integer or sequence of integers numbers of days before, < 0,
    or after, > 0, Easter.
    >>> easter(0)
    (True, [0])
    >>> easter([-364, -30, 0, "45", 260])
    (True, [-364, -30, 0, 45, 260])
    """
    easterstr = "easter: a comma separated list of integer numbers of days before, < 0, or after, > 0, Easter."

    if arg == 0:
        arg = [0]

    if arg:
        ok, res = integer_list(arg, None, None, True, 'easter')
        if ok:
            return True, res
        else:
            return False, "invalid easter: {}. Required for {}".format(res, easterstr)
    else:
        return False, easterstr


def do_interval(arg):
    """
    interval (positive integer, default = 1) E.g, with frequency
    w, interval 3 would repeat every three weeks.
    >>> do_interval("two")
    (None, "invalid interval: 'two'. Interval requires a positive integer (default 1) that sets the frequency interval. E.g., with frequency w (weekly), interval 3 would repeat every three weeks.")
    >>> do_interval(27)
    (27, 'interval: 27')
    >>> do_interval("1, 2")
    (None, "invalid interval: '1, 2'. Interval requires a positive integer (default 1) that sets the frequency interval. E.g., with frequency w (weekly), interval 3 would repeat every three weeks.")
    """

    intstr = "Interval requires a positive integer (default 1) that sets the frequency interval. E.g., with frequency w (weekly), interval 3 would repeat every three weeks."

    if arg:
        ok, res = integer(arg, 1, None, False)
        if ok:
            return res, f"interval: {arg}"
        else:
            return None, f"invalid interval: '{res}'. {intstr}"
    else:
        return None, intstr


def do_frequency(arg):
    """
    repetition frequency: character in (y)early, (m)onthly, (w)eekly, (d)aily, (h)ourly
    or mi(n)utely.
    >>> do_frequency('d')
    ('d', 'daily')
    >>> print(do_frequency('z')[1])
    invalid frequency: z not in (y)early, (m)onthly,
      (w)eekly, (d)aily, (h)ourly or mi(n)utely.
    """

    freq = [x for x in freq_names]
    freqstr = "(y)early, (m)onthly, (w)eekly, (d)aily, (h)ourly or mi(n)utely."
    if arg in freq:
        return arg, f"{freq_names[arg]}"
    elif arg:
        return None, wrap(f"invalid frequency: {arg} not in {freqstr}", 2)
    else:
        return None, wrap(f"repetition frequency: character from {freqstr}", 2)

def do_setpositions(arg):
    """
    >>> do_setpositions("1")
    ([1], 'set positions: 1')
    >>> do_setpositions("-1, 0")
    (None, 'invalid set positions: 0 is not allowed. set positions (non-zero integer or sequence of non-zero integers). When multiple dates satisfy the rule, take the dates from this/these positions in the list, e.g, &s 1 would choose the first element and &s -1 the last.')
    """
    setposstr = "set positions (non-zero integer or sequence of non-zero integers). When multiple dates satisfy the rule, take the dates from this/these positions in the list, e.g, &s 1 would choose the first element and &s -1 the last."
    if arg:
        args = arg.split(',')
        ok, res = integer_list(args, None, None, False, "")
        if ok:
            obj = res 
            rep = f"set positions: {arg}"
        else:
            obj = None
            rep = f"invalid set positions: {res}. {setposstr}"
    else:
        obj = None
        rep = setposstr
    return obj, rep


def do_count(arg):
    """
    do_count (positive integer) Include no more than this number of repetitions.
    >>> do_count('three')
    (None, 'invalid count: three. Required for count: a positive integer. Include no more than this number of repetitions.')
    >>> do_count('3')
    (3, 'count: 3')
    >>> do_count([2, 3])
    (None, 'invalid count: [2, 3]. Required for count: a positive integer. Include no more than this number of repetitions.')
    """

    countstr = "count: a positive integer. Include no more than this number of repetitions."

    if arg:
        ok, res = integer(arg, 1, None, False )
        if ok:
            obj = res
            rep = f"count: {arg}"
        else:
            obj = None
            rep = f"invalid count: {res}. Required for {countstr}"
    else:
        obj = None
        rep = countstr
    return obj, rep


# def count(arg):
#     """
#     count (positive integer) Include no more than this number of repetitions.
#     >>> count('three')
#     (False, 'invalid count: three. Required for count: a positive integer. Include no more than this number of repetitions.')
#     >>> count('3')
#     (True, 3)
#     >>> count([2, 3])
#     (False, 'invalid count: [2, 3]. Required for count: a positive integer. Include no more than this number of repetitions.')
#     """

#     countstr = "count: a positive integer. Include no more than this number of repetitions."

#     if arg:
#         ok, res = integer(arg, 1, None, False )
#         if ok:
#             return True, res
#         else:
#             return False, "invalid count: {}. Required for {}".format(res, countstr)
#     else:
#         return False, countstr


def do_weekdays(arg):
    """
    byweekday (English weekday abbreviation SU ... SA or sequence of such).
    Use, e.g., 3WE for the 3rd Wednesday or -1FR, for the last Friday in the
    month.
    >>> do_weekdays("")
    (None, 'weekdays: a comma separated list of English weekday abbreviations from SU, MO, TU, WE, TH, FR, SA. Prepend an integer to specify a particular weekday in the month. E.g., 3WE for the 3rd Wednesday or -1FR, for the last Friday in the month.')
    >>> do_weekdays("-2mo, 3tU")
    ([MO(-2), TU(+3)], '-2MO, 3TU')
    >>> do_weekdays("5Su, 1SA")
    (None, 'incomplete or invalid weekdays: 5SU. weekdays: a comma separated list of English weekday abbreviations from SU, MO, TU, WE, TH, FR, SA. Prepend an integer to specify a particular weekday in the month. E.g., 3WE for the 3rd Wednesday or -1FR, for the last Friday in the month.')
    >>> do_weekdays('3FR, -1M')
    (None, 'incomplete or invalid weekdays: -1M. weekdays: a comma separated list of English weekday abbreviations from SU, MO, TU, WE, TH, FR, SA. Prepend an integer to specify a particular weekday in the month. E.g., 3WE for the 3rd Wednesday or -1FR, for the last Friday in the month.')
    """
    weekdaysstr = "weekdays: a comma separated list of English weekday abbreviations from SU, MO, TU, WE, TH, FR, SA. Prepend an integer to specify a particular weekday in the month. E.g., 3WE for the 3rd Wednesday or -1FR, for the last Friday in the month."
    if arg:
        args = [x.strip().upper() for x in arg.split(',')]
        bad = []
        good = []
        for x in args:
            if x in WKDAYS_DECODE:
                good.append(eval('dateutil.rrule.{}'.format(WKDAYS_DECODE[x])))
            else:
                bad.append(x)
        if bad:
            obj = None
            rep = f"incomplete or invalid weekdays: {', '.join(bad)}. {weekdaysstr}"
        else:
            obj = good
            rep = f"{arg.upper()}"
    else:
        obj = None
        rep = weekdaysstr
    return obj, rep


def do_weeknumbers(arg):
    """
    byweekno (1, 2, ..., 53 or a sequence of such integers)
    >>> do_weeknumbers("0, 1, 5, 54")
    (None, 'invalid weeknumbers: {res}. Required for {weeknumbersstr}')
    """
    weeknumbersstr = "weeknumbers: a comma separated list of integer week numbers from 1, 2, ..., 53"

    if arg:
        args = arg.split(',')
        ok, res = integer_list(args, 0, 53, False)
        if ok:
            obj = res
            rep = f"{arg}"
        else:
            obj = None
            rep = "invalid weeknumbers: {res}. Required for {weeknumbersstr}"
    else:
        obj = None
        rep = weeknumbersstr
    return obj, rep


def do_months(arg):
    """
    bymonth (1, 2, ..., 12 or a sequence of such integers)
    >>> do_months("0, 2, 7, 13")
    (None, 'invalid months: 0 is not allowed; 13 is greater than the allowed maximum. Required for months: a comma separated list of integer month numbers from 1, 2, ..., 12')
    """
    monthsstr = "months: a comma separated list of integer month numbers from 1, 2, ..., 12"

    if arg:
        args = arg.split(',')
        ok, res = integer_list(args, 0, 12, False, "")
        if ok:
            obj = res
            rep = f"{arg}"
        else:
            obj = None
            rep = f"invalid months: {res}. Required for {monthsstr}"
    else:
        obj = None
        rep = monthsstr
    return obj, rep


def do_monthdays(arg):
    """
    >>> do_monthdays("0, 1, 26, -1, -2")
    (None, 'invalid monthdays: 0 is not allowed. Required for monthdays: a comma separated list of integer month days from  (1, 2, ..., 31. Prepend a minus sign to count backwards from the end of the month. E.g., use  -1 for the last day of the month.')
    """

    monthdaysstr = "monthdays: a comma separated list of integer month days from  (1, 2, ..., 31. Prepend a minus sign to count backwards from the end of the month. E.g., use  -1 for the last day of the month."

    args = arg.split(',')
    if arg:
        args = arg.split(',')
        ok, res = integer_list(args, -31, 31, False, "")
        if ok:
            obj = res
            rep = f"{arg}"
        else:
            obj = None
            rep = f"invalid monthdays: {res}. Required for {monthdaysstr}"
    else:
        obj = None
        rep = monthdaysstr
    return obj, rep

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

def do_hours(arg):
    """
    >>> do_hours("0, 6, 12, 18, 24")
    (None, 'invalid hours: hours: 24 is greater than the allowed maximum. Required for hours: a comma separated of integer hour numbers from 0, 1,  ..., 23.')
    >>> do_hours("0, 1")
    ([0, 1], '0, 1')
    """
    hoursstr = "hours: a comma separated of integer hour numbers from 0, 1,  ..., 23."

    args = arg.split(',')

    if args:
        ok, res = integer_list(args, 0, 23, True, "hours")
        if ok:
            obj = res
            rep = arg
        else:
            obj = None
            rep = f"invalid hours: {res}. Required for {hoursstr}"
    else:
        obj = None
        rep = hoursstr
    return obj, rep


def do_minutes(arg):
    """
    byminute (0 ... 59 or a sequence of such integers)
    >>> do_minutes("27")
    ([27], '27')
    >>> do_minutes("0, 60")
    (None, 'invalid minutes: 60 is greater than the allowed maximum. Required for minutes: a comma separated of integer minute numbers from 0 through 59.')
    """
    minutesstr = "minutes: a comma separated of integer minute numbers from 0 through 59."

    args = arg.split(',')
    if args:
        ok, res = integer_list(arg, 0, 59, True, "")
        if ok:
            obj = res
            rep = arg
        else:
            obj = None
            rep = f"invalid minutes: {res}. Required for {minutesstr}"
    else:
        obj = None
        rep = minutesstr
    return obj, rep


rrule_methods = {
    'r':  do_frequency,
    'i':  do_interval,
    's':  do_setpositions,
    'c':  do_count,
    'u':  until,
    'M':  do_months,
    'm':  do_monthdays,
    'W':  do_weeknumbers,
    'w':  do_weekdays,
    'h':  do_hours,
    'n':  do_minutes,
    'E':  do_easterdays,
    }

freq_names = {
    'y': 'yearly',
    'm': 'monthly',
    'w': 'weekly',
    'd': 'daily',
    'h': 'hourly', 
    'n': 'minutely',
    }

rrule_freq = {
    'y': 0,     #'YEARLY',
    'm': 1,     #'MONTHLY',
    'w': 2,     #'WEEKLY',
    'd': 3,     #'DAILY',
    'h': 4,     #'HOURLY',
    'n': 5,     #'MINUTELY',
}

# Note: the values such as MO in the following are dateutil.rrule WEEKDAY methods and not strings. A dict is used to dispatch the relevant method
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
    'w': 'byweekday',  # rrule weekday MO ... SU
    'h': 'byhour',  # positive integer
    'n': 'byminute',  # positive integer
    'E': 'byeaster', # interger number of days before (-) or after (+) Easter Sunday
}

rrule_keys = [x for x in rrule_name]
rrule_keys.sort()

def check_rrule(lofh):
    # """
    # An check_rrule hash or a sequence of such hashes.
    # >>> data = {'r': ''}
    # >>> check_rrule(data)
    # (False, 'repetition frequency: character from (y)early, (m)onthly, (w)eekly, (d)aily, (h)ourly or mi(n)utely.')
    # >>> good_data = {"M": 5, "i": 1, "m": 3, "r": "y", "w": "2SU"}
    # >>> pprint(check_rrule(good_data))
    # (True, [{'M': [5], 'i': 1, 'm': [3], 'r': 'y', 'w': [SU(+2)]}])
    # >>> good_data = {"M": [5, 12], "i": 1, "m": [3, 15], "r": "y", "w": "2SU"}
    # >>> pprint(check_rrule(good_data))
    # (True, [{'M': [5, 12], 'i': 1, 'm': [3, 15], 'r': 'y', 'w': [SU(+2)]}])
    # >>> bad_data = [{"M": 5, "i": 1, "m": 3, "r": "y", "w": "2SE"}, {"M": [11, 12], "i": 4, "m": [2, 3, 4, 5, 6, 7, 8], "r": "z", "w": ["TU", "-1FR"]}]
    # >>> print(check_rrule(bad_data))
    # (False, 'invalid weekdays: 2SE; invalid frequency: z not in (y)early, (m)onthly, (w)eekly, (d)aily, (h)ourly or mi(n)utely.')
    # >>> data = [{"r": "w", "w": "TU", "h": 14}, {"r": "w", "w": "TH", "h": 16}]
    # >>> pprint(check_rrule(data))
    # (True,
    #  [{'h': [14], 'i': 1, 'r': 'w', 'w': [TU]},
    #   {'h': [16], 'i': 1, 'r': 'w', 'w': [TH]}])
    # """
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
            if key in rrule_methods:
                obj, rep = rrule_methods[key](hsh[key])

                if obj:
                    res[key] = obj
                else:
                    msg.append(rep)
            else:
                msg.append("error: {} is not a valid key".format(key))

        if not msg:
            ret.append(res)

    if msg:
        return False, "{}".format("; ".join(msg))
    else:
        return True, ret

def rrule_args(r_hsh):
    """
    Housekeeping: Check for u and c, fix integers and weekdays. Replace etm arg names with dateutil. E.g., frequency 'y' with 0, 'E' with 'byeaster', ... Called by item_instances. 
    >>> item_eg = { "s": parse('2018-03-07 8am').naive(), "r": [ { "r": "w", "u": parse('2018-04-01 8am').naive(), }, ], "itemtype": "*"}
    >>> item_instances(item_eg, parse('2018-03-01 12am').naive(), parse('2018-04-01 12am').naive())
    [(DateTime(2018, 3, 7, 8, 0, 0, tzinfo=Timezone('UTC')), None), (DateTime(2018, 3, 14, 8, 0, 0, tzinfo=Timezone('UTC')), None), (DateTime(2018, 3, 21, 8, 0, 0, tzinfo=Timezone('UTC')), None), (DateTime(2018, 3, 28, 8, 0, 0, tzinfo=Timezone('UTC')), None)]
    >>> r_hsh = item_eg['r'][0]
    >>> r_hsh
    {'r': 'w', 'u': DateTime(2018, 4, 1, 8, 0, 0)}
    >>> rrule_args(r_hsh)
    (2, {'until': DateTime(2018, 4, 1, 8, 0, 0)})
    >>> item_eg = { "s": parse('2016-01-01 8am').naive(), "r": [ { "r": "y", "E": 0, }, ], "itemtype": "*"}
    >>> item_instances(item_eg, parse('2016-03-01 12am').naive(), parse('2019-06-01 12am').naive())
    [(DateTime(2016, 3, 27, 8, 0, 0, tzinfo=Timezone('UTC')), None), (DateTime(2017, 4, 16, 8, 0, 0, tzinfo=Timezone('UTC')), None), (DateTime(2018, 4, 1, 8, 0, 0, tzinfo=Timezone('UTC')), None), (DateTime(2019, 4, 21, 8, 0, 0, tzinfo=Timezone('UTC')), None)]
    >>> r_hsh = item_eg['r'][0]
    >>> r_hsh
    {'r': 'y', 'E': 0}
    >>> rrule_args(r_hsh)
    (0, {'byeaster': 0})
    >>> item_eg = { "s": parse('2018-03-07 8am', tz="US/Eastern"), "e": pendulum.duration(days=1, hours=5), "r": [ { "r": "w", "i": 2, "u": parse('2018-04-01 8am', tz="US/Eastern")}], "z": "US/Eastern", "itemtype": "*" }
    >>> r_hsh = item_eg['r'][0]
    >>> r_hsh
    {'r': 'w', 'i': 2, 'u': DateTime(2018, 4, 1, 8, 0, 0, tzinfo=Timezone('US/Eastern'))}
    >>> rrule_args(r_hsh)
    (2, {'interval': 2, 'until': DateTime(2018, 4, 1, 8, 0, 0, tzinfo=Timezone('US/Eastern'))})
    >>> item_eg = { "s": parse('2018-03-07 8am', tz="US/Eastern"),  "r": [ { "r": "w", "w": MO(+2), "u": parse('2018-06-30 8am', tz="US/Eastern")}], "z": "US/Eastern", "itemtype": "*" }
    >>> r_hsh = item_eg['r'][0]
    >>> r_hsh
    {'r': 'w', 'w': MO(+2), 'u': DateTime(2018, 6, 30, 8, 0, 0, tzinfo=Timezone('US/Eastern'))}
    >>> rrule_args(r_hsh)
    (2, {'byweekday': MO(+2), 'until': DateTime(2018, 6, 30, 8, 0, 0, tzinfo=Timezone('US/Eastern'))})

    """

    # force integers
    for k in "icsMmWhmE":
        if k in r_hsh:
            args = r_hsh[k]
            if not isinstance(args, list):
                args = [args]
            tmp = [int(x) for x in args]
            if len(tmp) == 1:
                r_hsh[k] = tmp[0]
            else:
                r_hsh[k] = tmp
    if 'u' in r_hsh and 'c' in r_hsh:
        logger.warn(f"Warning: using both 'c' and 'u' is depreciated in {r_hsh}")
    freq = rrule_freq[r_hsh['r']]
    kwd = {rrule_name[k]: r_hsh[k] for k in r_hsh if k != 'r'}
    return freq, kwd

def item_instances(item, aft_dt, bef_dt=None):
    """
    Dates and datetimes decoded from the data store will all be aware and in the local timezone. aft_dt and bef_dt must therefore also be aware and in the local timezone.
    In dateutil, the starting datetime (dtstart) is not the first recurrence instance, unless it does fit in the specified rules.  Notice that you can easily get the original behavior by using a rruleset and adding the dtstart as an rdate recurrence.
    Each instance is a tuple (beginning datetime, ending datetime) where ending datetime is None unless the item is an event.

    Get instances from item falling on or after aft_dt and on or before bef_dt or, if bef_dt is None, the first instance after aft_dt. All datetimes will be returned with zero offsets.
    >>> item_eg = { "s": parse('2018-03-07 8am', tz="US/Eastern"), "e": pendulum.duration(days=1, hours=5), "r": [ { "r": "w", "i": 2, "u": parse('2018-04-01 8am', tz="US/Eastern")}], "z": "US/Eastern", "itemtype": "*" }
    >>> item_eg
    {'s': DateTime(2018, 3, 7, 8, 0, 0, tzinfo=Timezone('US/Eastern')), 'e': Duration(days=1, hours=5), 'r': [{'r': 'w', 'i': 2, 'u': DateTime(2018, 4, 1, 8, 0, 0, tzinfo=Timezone('US/Eastern'))}], 'z': 'US/Eastern', 'itemtype': '*'}
    >>> item_instances(item_eg, parse('2018-03-01 12am', tz="US/Eastern"), parse('2018-04-01 12am', tz="US/Eastern"))
    [(DateTime(2018, 3, 7, 8, 0, 0, tzinfo=Timezone('US/Eastern')), DateTime(2018, 3, 7, 23, 59, 59, 999999, tzinfo=Timezone('US/Eastern'))), (DateTime(2018, 3, 8, 0, 0, 0, tzinfo=Timezone('US/Eastern')), DateTime(2018, 3, 8, 13, 0, 0, tzinfo=Timezone('US/Eastern'))), (DateTime(2018, 3, 21, 8, 0, 0, tzinfo=Timezone('US/Eastern')), DateTime(2018, 3, 21, 23, 59, 59, 999999, tzinfo=Timezone('US/Eastern'))), (DateTime(2018, 3, 22, 0, 0, 0, tzinfo=Timezone('US/Eastern')), DateTime(2018, 3, 22, 13, 0, 0, tzinfo=Timezone('US/Eastern')))]
    >>> item_eg['+'] = [parse("20180311T1000", tz="US/Eastern")]
    >>> item_eg['-'] = [parse("20180311T0800", tz="US/Eastern")]
    >>> item_eg['e'] = pendulum.duration(hours=2)
    >>> item_eg
    {'s': DateTime(2018, 3, 7, 8, 0, 0, tzinfo=Timezone('US/Eastern')), 'e': Duration(hours=2), 'r': [{'r': 'w', 'i': 2, 'u': DateTime(2018, 4, 1, 8, 0, 0, tzinfo=Timezone('US/Eastern'))}], 'z': 'US/Eastern', 'itemtype': '*', '+': [DateTime(2018, 3, 11, 10, 0, 0, tzinfo=Timezone('US/Eastern'))], '-': [DateTime(2018, 3, 11, 8, 0, 0, tzinfo=Timezone('US/Eastern'))]}
    >>> item_instances(item_eg, parse('2018-03-01 12am'), parse('2018-04-01 12am'))
    [(DateTime(2018, 3, 7, 8, 0, 0, tzinfo=Timezone('US/Eastern')), DateTime(2018, 3, 7, 10, 0, 0, tzinfo=Timezone('US/Eastern'))), (DateTime(2018, 3, 11, 10, 0, 0, tzinfo=Timezone('US/Eastern')), DateTime(2018, 3, 11, 12, 0, 0, tzinfo=Timezone('US/Eastern'))), (DateTime(2018, 3, 21, 8, 0, 0, tzinfo=Timezone('US/Eastern')), DateTime(2018, 3, 21, 10, 0, 0, tzinfo=Timezone('US/Eastern')))]
    >>> del item_eg['e']
    >>> item_instances(item_eg, parse('2018-03-07 8:01am', tz="US/Eastern"))
    [(DateTime(2018, 3, 11, 10, 0, 0, tzinfo=Timezone('US/Eastern')), None)]
    >>> del item_eg['r']
    >>> del item_eg['-']
    >>> del item_eg['+']
    >>> item_instances(item_eg, parse('2018-03-01 12am'), parse('2018-04-01 12am', tz="US/Eastern"))
    [(DateTime(2018, 3, 7, 8, 0, 0, tzinfo=Timezone('US/Eastern')), None)]
    >>> item_eg = { "s": parse('2018-03-07 8am', tz="US/Eastern"), "r": [ { "r": "w", "w": MO(+2), "u": parse('2018-06-30 8am', tz="US/Eastern")}], "z": "US/Eastern", "itemtype": "*" }
    >>> item_eg
    {'s': DateTime(2018, 3, 7, 8, 0, 0, tzinfo=Timezone('US/Eastern')), 'r': [{'r': 'w', 'w': MO(+2), 'u': DateTime(2018, 6, 30, 8, 0, 0, tzinfo=Timezone('US/Eastern'))}], 'z': 'US/Eastern', 'itemtype': '*'}
    >>> item_instances(item_eg, parse('2018-03-01 12am', tz="US/Eastern"), parse('2018-04-01 12am', tz="US/Eastern"))
    [(DateTime(2018, 3, 12, 8, 0, 0, tzinfo=Timezone('US/Eastern')), None), (DateTime(2018, 3, 19, 8, 0, 0, tzinfo=Timezone('US/Eastern')), None), (DateTime(2018, 3, 26, 8, 0, 0, tzinfo=Timezone('US/Eastern')), None)]

    Simple repetition:
    >>> item_eg = { "itemtype": "*", "s": parse('2018-11-15 8a', tz="US/Eastern"), "+": [parse('2018-11-16 10a', tz="US/Eastern"), parse('2018-11-18 3p', tz="US/Eastern"), parse('2018-11-27 8p', tz="US/Eastern")] }
    >>> item_instances(item_eg, parse('2018-11-17 9am', tz="US/Eastern"))
    [(DateTime(2018, 11, 18, 15, 0, 0, tzinfo=Timezone('US/Eastern')), None), (DateTime(2018, 11, 27, 20, 0, 0, tzinfo=Timezone('US/Eastern')), None)]
    """
    # FIXME 
    # @r given: dateutil behavior @s included only if it fits the repetiton rule
    # @r not given 
    #    @s included
    #    @+ given: @s and each date in @+ added as rdates

    if 's' not in item:
        return []
    instances = []
    dtstart = item['s']
    # print('starting dts:', dtstart)
    # This should not be necessary since the data store decodes dates as datetimes
    if isinstance(dtstart, pendulum.Date) and not isinstance(dtstart, pendulum.DateTime):
        dtstart = pendulum.datetime(year=dtstart.year, month=dtstart.month, day=dtstart.day, hour=0, minute=0)
        startdst = None
    else:
        # for discarding daylight saving time differences in repetitions
        try:
            startdst = dtstart.dst()
        except:
            print('dtstart:', dtstart)
            dtstart = dtstart[0]
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
                print(hsh)
                print(e)
                print(item)
                return []

        if '-' in item:
            for dt in item['-']:
                if type(dt) == pendulum.Date:
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
            nxt = rset.after(aft_dt, inc=True)
            instances = [pendulum.instance(nxt)] if nxt else []
        else:
            instances = [pendulum.instance(x) for x in rset.between(aft_dt, bef_dt, inc=True)]

    elif '+' in item:
        # no @r but @+ => simple repetition
        tmp = [dtstart]
        tmp.extend(item['+'])
        tmp.sort()
        if bef_dt is None:
            instances = [x for x in tmp if (x > aft_dt)]#[:1]
        else:
            instances = [x for x in tmp if (x > aft_dt and x <= bef_dt)]

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
    pairs.sort()

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
    b=do_beginby,
)
datetime_job_methods.update(undated_job_methods)

def task(at_hsh):
    """
    Evaluate task/job completions and update the f and s entries if appropriate 
    >>> item_eg = {"summary": "Task Group",  "s": parse('2018-03-07 8am'), "r": [ { "r": "w", "i": 2, "u": parse('2018-04-01 8am')}], "z": "US/Eastern", "itemtype": "-", 'j': [ {'j': 'Job 1', 'f': parse('2018-03-06 10am')}, {'j': 'Job 2'} ] }
    >>> pprint(task(item_eg))
    {'itemtype': '-',
     'j': [{'f': DateTime(2018, 3, 6, 10, 0, 0, tzinfo=Timezone('UTC')),
            'i': '1',
            'j': 'Job 1',
            'p': [],
            'req': [],
            'status': 'x',
            'summary': 'Task Group 1/0/1: Job 1'},
           {'i': '2',
            'j': 'Job 2',
            'p': ['1'],
            'req': [],
            'status': '-',
            'summary': 'Task Group 1/0/1: Job 2'}],
     'r': [{'i': 2,
            'r': 'w',
            'u': DateTime(2018, 4, 1, 8, 0, 0, tzinfo=Timezone('UTC'))}],
     's': DateTime(2018, 3, 7, 8, 0, 0, tzinfo=Timezone('UTC')),
     'summary': 'Task Group',
     'z': 'US/Eastern'}

    Now finish the last job and note the update for h and s
    >>> item_eg = {"summary": "Task Group",  "s": parse('2018-03-07 8am'), "z": "US/Eastern",  "r": [ { "r": "w", "i": 2, "u": parse('2018-04-01 8am')}], "z": "US/Eastern", "itemtype": "-", 'j': [ {'j': 'Job 1', 'f': parse('2018-03-06 10am')}, {'j': 'Job 2', 'f': parse('2018-03-07 1pm') } ] }
    >>> item_eg
    {'summary': 'Task Group', 's': DateTime(2018, 3, 7, 8, 0, 0, tzinfo=Timezone('UTC')), 'z': 'US/Eastern', 'r': [{'r': 'w', 'i': 2, 'u': DateTime(2018, 4, 1, 8, 0, 0, tzinfo=Timezone('UTC'))}], 'itemtype': '-', 'j': [{'j': 'Job 1', 'f': DateTime(2018, 3, 6, 10, 0, 0, tzinfo=Timezone('UTC'))}, {'j': 'Job 2', 'f': DateTime(2018, 3, 7, 13, 0, 0, tzinfo=Timezone('UTC'))}]}
    >>> pprint(task(item_eg))
    {'h': [DateTime(2018, 3, 7, 13, 0, 0, tzinfo=Timezone('UTC'))],
     'itemtype': '-',
     'j': [{'i': '1',
            'j': 'Job 1',
            'p': [],
            'req': [],
            'status': '-',
            'summary': 'Task Group 1/1/0: Job 1'},
           {'i': '2',
            'j': 'Job 2',
            'p': ['1'],
            'req': ['1'],
            'status': '+',
            'summary': 'Task Group 1/1/0: Job 2'}],
     'r': [{'i': 2,
            'r': 'w',
            'u': DateTime(2018, 4, 1, 8, 0, 0, tzinfo=Timezone('UTC'))}],
     's': DateTime(2018, 3, 7, 8, 0, 0, tzinfo=Timezone('UTC')),
     'summary': 'Task Group',
     'z': 'US/Eastern'}

    Simple repetition:
    default overdue = k
    >>> item_eg = { "itemtype": "-", "s": parse('2018-11-15 8a', tz="US/Eastern"),  "+": [parse('2018-11-16 10a', tz="US/Eastern"), parse('2018-11-18 3p', tz="US/Eastern"), parse('2018-11-27 8p', tz="US/Eastern")], 'f': parse('2018-11-17 9a', tz='US/Eastern') }
    >>> pprint(task(item_eg))
    {'+': [DateTime(2018, 11, 18, 15, 0, 0, tzinfo=Timezone('US/Eastern')),
           DateTime(2018, 11, 27, 20, 0, 0, tzinfo=Timezone('US/Eastern'))],
     'h': [DateTime(2018, 11, 17, 9, 0, 0, tzinfo=Timezone('US/Eastern'))],
     'itemtype': '-',
     's': DateTime(2018, 11, 16, 10, 0, 0, tzinfo=Timezone('US/Eastern'))}

    overdue = r
    >>> item_eg = { "itemtype": "-", "s": parse('2018-11-15 8a', tz="US/Eastern"),  "+": [parse('2018-11-16 10a', tz="US/Eastern"), parse('2018-11-18 3p', tz="US/Eastern"), parse('2018-11-27 8p', tz="US/Eastern")], 'f': parse('2018-11-17 9a', tz='US/Eastern'), 'o': 'r' }
    >>> pprint(task(item_eg))
    {'+': [DateTime(2018, 11, 27, 20, 0, 0, tzinfo=Timezone('US/Eastern'))],
     'h': [DateTime(2018, 11, 17, 9, 0, 0, tzinfo=Timezone('US/Eastern'))],
     'itemtype': '-',
     'o': 'r',
     's': DateTime(2018, 11, 18, 15, 0, 0, tzinfo=Timezone('US/Eastern'))}
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
            # FIXME: is this the right tz setting?
            aft = pendulum.now(tz=at_hsh.get('z', None))
        due = item_instances(at_hsh, aft)
        if due:
            # we have another instance
            at_hsh['s'] = due[0][0]
            if '+' in at_hsh and 'r' not in at_hsh:
                # simple repetition
                at_hsh['+'] = [x for x in at_hsh['+'] if x > at_hsh['s']]
            at_hsh.setdefault('h', []).append(at_hsh['f'])
            del at_hsh['f']
    return(at_hsh)


def jobs(lofh, at_hsh={}):
    """
    Process the job hashes in lofh
    >>> data = [{'j': 'Pick up materials', 'd': 'lumber, nails, paint'}, {'j': 'Cut pieces'}, {'j': 'Assemble'}]
    >>> pprint(jobs(data))
    (True,
     [{'d': 'lumber, nails, paint',
       'i': '1',
       'j': 'Pick up materials',
       'p': [],
       'req': [],
       'status': '-',
       'summary': ' 1/2/0: Pick up materials'},
      {'i': '2',
       'j': 'Cut pieces',
       'p': ['1'],
       'req': ['1'],
       'status': '+',
       'summary': ' 1/2/0: Cut pieces'},
      {'i': '3',
       'j': 'Assemble',
       'p': ['2'],
       'req': ['2', '1'],
       'status': '+',
       'summary': ' 1/2/0: Assemble'}],
     None)
    >>> data = [{'j': 'Job One', 'a': '2d: m', 'b': 2}, {'j': 'Job Two', 'a': '1d: m', 'b': 1}, {'j': 'Job Three', 'a': '6h: m'}]
    >>> pprint(jobs(data))
    (True,
     [{'i': '1',
       'j': 'Job One',
       'p': [],
       'req': [],
       'status': '-',
       'summary': ' 1/2/0: Job One'},
      {'i': '2',
       'j': 'Job Two',
       'p': ['1'],
       'req': ['1'],
       'status': '+',
       'summary': ' 1/2/0: Job Two'},
      {'i': '3',
       'j': 'Job Three',
       'p': ['2'],
       'req': ['2', '1'],
       'status': '+',
       'summary': ' 1/2/0: Job Three'}],
     None)
    >>> data = [{'j': 'Job One', 'a': '2d: m', 'b': 2, 'f': parse('6/20/18 12p')}, {'j': 'Job Two', 'a': '1d: m', 'b': 1}, {'j': 'Job Three', 'a': '6h: m'}]
    >>> pprint(jobs(data))
    (True,
     [{'f': DateTime(2018, 6, 20, 12, 0, 0, tzinfo=Timezone('UTC')),
       'i': '1',
       'j': 'Job One',
       'p': [],
       'req': [],
       'status': 'x',
       'summary': ' 1/1/1: Job One'},
      {'i': '2',
       'j': 'Job Two',
       'p': ['1'],
       'req': [],
       'status': '-',
       'summary': ' 1/1/1: Job Two'},
      {'i': '3',
       'j': 'Job Three',
       'p': ['2'],
       'req': ['2'],
       'status': '+',
       'summary': ' 1/1/1: Job Three'}],
     None)
    >>> data = [{'j': 'Job One', 'a': '2d: m', 'b': 2, 'f': parse('6/20/18 12p')}, {'j': 'Job Two', 'a': '1d: m', 'b': 1, 'f': parse('6/21/18 12p')}, {'j': 'Job Three', 'a': '6h: m'}]
    >>> pprint(jobs(data))
    (True,
     [{'f': DateTime(2018, 6, 20, 12, 0, 0, tzinfo=Timezone('UTC')),
       'i': '1',
       'j': 'Job One',
       'p': [],
       'req': [],
       'status': 'x',
       'summary': ' 1/0/2: Job One'},
      {'f': DateTime(2018, 6, 21, 12, 0, 0, tzinfo=Timezone('UTC')),
       'i': '2',
       'j': 'Job Two',
       'p': ['1'],
       'req': [],
       'status': 'x',
       'summary': ' 1/0/2: Job Two'},
      {'i': '3',
       'j': 'Job Three',
       'p': ['2'],
       'req': [],
       'status': '-',
       'summary': ' 1/0/2: Job Three'}],
     None)
    >>> data = [{'j': 'Job One', 'a': '2d: m', 'b': 2, 'f': parse('6/20/18 12p')}, {'j': 'Job Two', 'a': '1d: m', 'b': 1, 'f': parse('6/21/18 12p')}, {'j': 'Job Three', 'a': '6h: m', 'f': parse('6/22/18 12p')}]
    >>> pprint(jobs(data))
    (True,
     [{'i': '1',
       'j': 'Job One',
       'p': [],
       'req': [],
       'status': '-',
       'summary': ' 1/2/0: Job One'},
      {'i': '2',
       'j': 'Job Two',
       'p': ['1'],
       'req': ['1'],
       'status': '+',
       'summary': ' 1/2/0: Job Two'},
      {'i': '3',
       'j': 'Job Three',
       'p': ['2'],
       'req': ['2', '1'],
       'status': '+',
       'summary': ' 1/2/0: Job Three'}],
     DateTime(2018, 6, 22, 12, 0, 0, tzinfo=Timezone('UTC')))

    Now add an 'r' entry for at_hsh.
    >>> data = [{'j': 'Job One', 'a': '2d: m', 'b': 2, 'f': parse('6/20/18 12p', tz="US/Eastern")}, {'j': 'Job Two', 'a': '1d: m', 'b': 1, 'f': parse('6/21/18 12p', tz="US/Eastern")}, {'j': 'Job Three', 'a': '6h: m', 'f': parse('6/22/18 12p', tz="US/Eastern")}]
    >>> data
    [{'j': 'Job One', 'a': '2d: m', 'b': 2, 'f': DateTime(2018, 6, 20, 12, 0, 0, tzinfo=Timezone('US/Eastern'))}, {'j': 'Job Two', 'a': '1d: m', 'b': 1, 'f': DateTime(2018, 6, 21, 12, 0, 0, tzinfo=Timezone('US/Eastern'))}, {'j': 'Job Three', 'a': '6h: m', 'f': DateTime(2018, 6, 22, 12, 0, 0, tzinfo=Timezone('US/Eastern'))}]
    >>> pprint(jobs(data, {'itemtype': '-', 'r': [{'r': 'd'}], 's': parse('6/22/18 8a', tz="US/Eastern"), 'j': data}))
    (True,
     [{'b': 'beginby: 2 day(s)',
       'i': '1',
       'j': 'Job One',
       'p': [],
       'req': [],
       'status': '-',
       'summary': ' 1/2/0: Job One'},
      {'b': 'beginby: 1 day(s)',
       'i': '2',
       'j': 'Job Two',
       'p': ['1'],
       'req': ['1'],
       'status': '+',
       'summary': ' 1/2/0: Job Two'},
      {'i': '3',
       'j': 'Job Three',
       'p': ['2'],
       'req': ['2', '1'],
       'status': '+',
       'summary': ' 1/2/0: Job Three'}],
     DateTime(2018, 6, 22, 12, 0, 0, tzinfo=Timezone('US/Eastern')))
    """
    if 's' in at_hsh:
        job_methods = datetime_job_methods
        # TODO: deal with &s entries
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
            del id2hsh[i]['f']
            if at_hsh.get('s', None) and ('r' in at_hsh or '+' in at_hsh):
                # repeating
                overdue = at_hsh.get('o', 'k')
                if overdue == 's':
                    dt = pendulum.now(tz=at_hsh.get('z', None))
                elif overdue == 'k':
                    dt = at_hsh['s']
                else: # 'r'
                    dt = last_completion
                n = item_instances(at_hsh, dt, None)
                if n:
                    # n will be a list of beg, end tuples - get the first beg
                    at_hsh['s'] = n[0][0]
                else:
                    at_hsh['f'] = last_completion
        else:
            # remove finished jobs from the requirements
            if id2hsh[i].get('f', None):
                # i is finished so remove it from the requirements for any
                # other jobs
                for j in ids:
                    if i in req[j]:
                        # since i is finished, remove it from j's requirements
                        req[j].remove(i)

    awf = [0, 0, 0]
    # set the job status for each job - f) finished, a) available or w) waiting
    for i in ids:
        if id2hsh[i].get('f', None): # i is finished
            id2hsh[i]['status'] = 'x'
            awf[2] += 1
        elif req[i]: # there are unfinished requirements for i
            id2hsh[i]['status'] = '+'
            awf[1] += 1
        else: # there are no unfinished requirements for i
            id2hsh[i]['status'] = '-'
            awf[0] += 1

    for i in ids:
        id2hsh[i]['summary'] = "{} {}: {}".format(summary, "/".join([str(x) for x in awf]), id2hsh[i]['j'])
        id2hsh[i]['req'] = req[i]
        id2hsh[i]['i'] = i

    if msg:
        return False, "; ".join(msg), None
    else:
        # return the list of job hashes
        # print('id2hsh', id2hsh)
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

# FIXME SmartCacheTable doesn't seem to work with tinydb 3.12
# TinyDB.table_class = SmartCacheTable
TinyDB.DEFAULT_TABLE = 'items'

# Item = Query()

class PendulumDateTimeSerializer(Serializer):
    """
    This class handles both aware and 'factory' pendulum objects.

    Encoding: If obj.tzinfo.abbrev is '-00' (tz=Factory), it is interpreted as naive, serialized without conversion and an 'N' is appended. Otherwise it is interpreted as aware, converted to UTC and an 'A' is appended.
    Decoding: If the serialization ends with 'A', the pendulum object is treated as 'UTC' and converted to localtime. Otherwise, the object is treated as 'Factory' and no conversion is performed.

    This serialization discards both seconds and microseconds but preserves hours and minutes.

    """

    OBJ_CLASS = pendulum.DateTime

    def encode(self, obj):
        """
        Serialize naive objects (Z == '') without conversion but with 'N' for 'Naive' appended. Convert aware datetime objects to UTC and then serialize them with 'A' for 'Aware' appended.
        >>> dts = PendulumDateTimeSerializer()
        >>> dts.encode(pendulum.datetime(2018,7,25,10, 27).naive())
        '20180725T1027N'
        >>> dts.encode(pendulum.datetime(2018,7,25,10, 27, tz='US/Eastern'))
        '20180725T1427A'
        """
        if obj.format('Z') == '':
            return obj.format('YYYYMMDDTHHmm[N]')
        else:
            return obj.in_tz('UTC').format('YYYYMMDDTHHmm[A]')

    def decode(self, s):
        """
        Return the serialization as a datetime object. If the serializaton ends with 'A',  first converting to localtime and returning an aware datetime object in the local timezone. If the serialization ends with 'N', returning without conversion as an aware datetime object in the local timezone.
        >>> dts = PendulumDateTimeSerializer()
        >>> dts.decode('20180725T1027N')
        DateTime(2018, 7, 25, 10, 27, 0, tzinfo=Timezone('America/New_York'))
        >>> dts.decode('20180725T1427A')
        DateTime(2018, 7, 25, 10, 27, 0, tzinfo=Timezone('America/New_York'))
        """
        if s[-1] == 'A':
            return pendulum.from_format(s[:-1], 'YYYYMMDDTHHmm', 'UTC').in_timezone('local')
        else:
            return pendulum.from_format(s[:-1], 'YYYYMMDDTHHmm').naive().in_timezone('local')


class PendulumDateSerializer(Serializer):
    """
    This class handles pendulum date objects. Encode as date string and decode as a midnight datetime without conversion in the local timezone.
    >>> ds = PendulumDateSerializer()
    >>> ds.encode(pendulum.date(2018, 7, 25))
    '20180725'
    >>> ds.decode('20180725')
    Date(2018, 7, 25)
    """
    OBJ_CLASS = pendulum.Date

    def encode(self, obj):
        """
        Serialize the naive date object without conversion.
        """
        return obj.format('YYYYMMDD')

    def decode(self, s):
        """
        Return the serialization as a date object.
        """
        # return pendulum.from_format(s, 'YYYYMMDD').naive().in_timezone('local')
        return pendulum.from_format(s, 'YYYYMMDD').date()


class PendulumDurationSerializer(Serializer):
    """
    This class handles pendulum.duration (timedelta) objects.
    >>> dus = PendulumDurationSerializer()
    >>> dus.encode(pendulum.duration(days=3, hours=5, minutes=15))
    '3d5h15m'
    >>> dus.decode('3d5h15m')
    Duration(days=3, hours=5, minutes=15)
    """
    OBJ_CLASS = pendulum.Duration

    def encode(self, obj):
        """
        Serialize the timedelta object as days.seconds.
        """
        return format_duration(obj)

    def decode(self, s):
        """
        Return the serialization as a timedelta object.
        """
        return parse_duration(s)[1]

class PendulumWeekdaySerializer(Serializer):
    """
    This class handles dateutil.rrule.weeday objects. Note in the following examples that unquoted weekdays, eg. MO(-3), are dateutil.rrule.weekday objects.
    >>> wds = PendulumWeekdaySerializer()
    >>> wds.encode(MO(-3))
    '-3MO'
    >>> wds.encode(SA(+3))
    '3SA'
    >>> wds.encode(WE)
    'WE'
    >>> wds.decode('-3MO')
    MO(-3)
    >>> wds.decode('3SA')
    SA(+3)
    >>> wds.decode('WE')
    WE
    """

    OBJ_CLASS = dateutil.rrule.weekday

    def encode(self, obj):
        """
        Serialize the weekday object.
        """
        s = WKDAYS_ENCODE[obj.__repr__()]
        if s.startswith('+'): 
            # drop the leading + sign
            s = s[1:]
        # print('serializing', obj.__repr__(), type(obj), 'as', s)
        return s

    def decode(self, s):
        """
        Return the serialization as a weekday object.
        """
        # print('deseralizing', s, type(s))
        return eval('dateutil.rrule.{}'.format(WKDAYS_DECODE[s]))



serialization = SerializationMiddleware()
serialization.register_serializer(PendulumDateTimeSerializer(), 'T') # Time
serialization.register_serializer(PendulumDateSerializer(), 'D')     # Date
serialization.register_serializer(PendulumDurationSerializer(), 'I') # Interval
serialization.register_serializer(PendulumWeekdaySerializer(), 'W')  # Wkday 

DBNAME = 'db.json'
ETMDB = TinyDB(DBNAME, storage=serialization, default_table='items', indent=1, ensure_ascii=False)
ETMDB_QUERY = ETMDB.table('items', cache_size=None)

########################
### end TinyDB setup ###
########################


########################
### start week/month ###
########################

# FIXME: Process only one week at a time on demand => no need to store and update extended periods or to limit the weeks that can be displayed.

def get_period(dt=pendulum.now(), weeks_before=3, weeks_after=9):
    """
    Return the begining and ending of the period that includes the weeks in current month plus the weeks in the prior *months_before* and the weeks in the subsequent *months_after*. The period will begin at 0 hours on the relevant Monday and end at 23:59:59 hours on the relevant Sunday.
    >>> get_period(pendulum.datetime(2018, 12, 15, 0, 0, tz='US/Eastern'))
    (DateTime(2018, 11, 19, 0, 0, 0, tzinfo=Timezone('US/Eastern')), DateTime(2019, 2, 17, 23, 59, 59, 999999, tzinfo=Timezone('US/Eastern')))
    """
    beg = dt.start_of('week').subtract(weeks=weeks_before).start_of('week')
    end = dt.start_of('week').add(weeks=weeks_after).end_of('week')
    return (beg, end)


def iso_year_start(iso_year):
    """
    Return the gregorian calendar date of the first day of the given ISO year.
    >>> iso_year_start(2017)
    Date(2017, 1, 2)
    >>> iso_year_start(2018)
    Date(2018, 1, 1)
    """
    fourth_jan = pendulum.date(iso_year, 1, 4)
    delta = pendulum.duration(days=fourth_jan.isoweekday()-1)
    return (fourth_jan - delta)


def iso_to_gregorian(ywd):
    """
    Return the gregorian calendar date for the given year, week and day.
    >>> iso_to_gregorian((2018, 7, 3))
    Date(2018, 2, 14)
    """
    year_start = iso_year_start(ywd[0])
    return year_start + pendulum.duration(days=ywd[2]-1, weeks=ywd[1]-1)


def getWeekNum(dt=pendulum.now()):
    """
    Return the year and week number for the datetime.
    >>> getWeekNum(pendulum.datetime(2018, 2, 14, 10, 30))
    (2018, 7)
    >>> getWeekNum(pendulum.date(2018, 2, 14))
    (2018, 7)
    >>> getWeekNum(pendulum.date(2018, 12, 31))
    (2019, 1)
    """
    return dt.isocalendar()[:2]


def nextWeek(yw):
    """
    >>> nextWeek((2015,53))
    (2016, 1)
    """
    return (iso_to_gregorian((*yw, 7)) + pendulum.duration(days=1)).isocalendar()[:2]


def prevWeek(yw):
    """
    >>> prevWeek((2016,1))
    (2015, 53)
    """
    return (iso_to_gregorian((*yw, 1)) - pendulum.duration(days=1)).isocalendar()[:2]


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

def getWeekNumbers(dt=pendulum.now(), bef=3, after=9):
    """
    >>> dt = pendulum.date(2018, 12, 7)
    >>> getWeekNumbers(dt)
    [(2018, 46), (2018, 47), (2018, 48), (2018, 49), (2018, 50), (2018, 51), (2018, 52), (2019, 1), (2019, 2), (2019, 3), (2019, 4), (2019, 5), (2019, 6)]
    """
    yw = dt.add(days=-bef*7).isocalendar()[:2]
    weeks = [yw]
    for i in range(1, bef + after + 1):
        yw = nextWeek(yw)
        weeks.append(yw)
    return weeks


######################
### end week/month ###
######################

def pen_from_fmt(s, z='local'):
    dt = pendulum.from_format(s, "YYYYMMDDTHHmm", z)
    if z == 'Factory' and dt.hour == dt.minute == 0:
        dt = dt.date()
    return dt

# def timestamp_from_id(doc_id, z='local'):
#     return pendulum.from_format(str(doc_id)[:12], "YYYYMMDDHHmm").in_timezone(z)

def drop_zero_minutes(dt):
    """
    >>> drop_zero_minutes(parse('2018-03-07 10am'))
    '10'
    >>> drop_zero_minutes(parse('2018-03-07 2:45pm'))
    '2:45'
    """
    if dt.minute == 0:
        if ampm:
            return dt.format("h")
        else:
            return dt.format("H")
    else:
        if ampm:
            return dt.format("h:mm")
        else:
            return dt.format("H:mm")

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
        end_suffix = end_dt.format("A").lower()
        if diff:
            beg_suffix = beg_dt.format("A").lower()

    beg_fmt = drop_zero_minutes(beg_dt)
    end_fmt = drop_zero_minutes(end_dt)

    return f"{beg_fmt}{beg_suffix}-{end_fmt}{end_suffix}"

def fmt_time(dt, ignore_midnight=True):
    if ignore_midnight and dt.hour == 0 and dt.minute == 0 and dt.second == 0:
        return ""
    suffix = dt.format("A").lower() if ampm else ""
    dt_fmt = drop_zero_minutes(dt)
    return f"{dt_fmt}{suffix}"


def beg_ends(starting_dt, extent_duration, z=None):
    """
    >>> starting = parse('2018-03-02 9am') 
    >>> beg_ends(starting, parse_duration('2d2h20m')[1])
    [(DateTime(2018, 3, 2, 9, 0, 0, tzinfo=Timezone('UTC')), DateTime(2018, 3, 2, 23, 59, 59, 999999, tzinfo=Timezone('UTC'))), (DateTime(2018, 3, 3, 0, 0, 0, tzinfo=Timezone('UTC')), DateTime(2018, 3, 3, 23, 59, 59, 999999, tzinfo=Timezone('UTC'))), (DateTime(2018, 3, 4, 0, 0, 0, tzinfo=Timezone('UTC')), DateTime(2018, 3, 4, 11, 20, 0, tzinfo=Timezone('UTC')))]
    >>> beg_ends(starting, parse_duration('8h20m')[1])
    [(DateTime(2018, 3, 2, 9, 0, 0, tzinfo=Timezone('UTC')), DateTime(2018, 3, 2, 17, 20, 0, tzinfo=Timezone('UTC')))]
    """

    pairs = []
    beg = starting_dt
    ending = starting_dt + extent_duration
    while ending.date() > beg.date():
        end = beg.end_of('day')
        pairs.append((beg, end))
        beg = beg.start_of('day').add(days=1)
    pairs.append((beg, ending))
    return pairs


def print_json(edit=False):
    for item in ETMDB:
        try:
            print(item.doc_id)
            print(item_details(item, edit))
        except Exception as e:
            print('exception:', e)
            pprint(item)
            print()
        print()

def item_details(item, edit=False):
    """

    """
    try:
        if edit:
            return jinja_entry_template.render(h=item)
        else:
            # return jinja_entry_template.render(h=item)
            return jinja_display_template.render(h=item)

    except Exception as e:
        print('item_details', e)
        print(item)

def fmt_week(yrwk):
    """
    >>> fmt_week((2018, 10))
    '2018 Week 10: Mar 5 - 11'
    >>> fmt_week((2019, 1))
    '2019 Week 1: Dec 31 - Jan 6'
    """
    dt_year, dt_week = yrwk
    # dt_week = dt_obj.week_of_year
    # year_week = f"{dt_year} Week {dt_week}"
    wkbeg = pendulum.parse(f"{dt_year}-W{str(dt_week).rjust(2, '0')}")
    wkend = pendulum.parse(f"{dt_year}-W{str(dt_week).rjust(2, '0')}-7")
    week_begin = wkbeg.format("MMM D")
    if wkbeg.month == wkend.month:
        week_end = wkend.format("D")
    else:
        week_end = wkend.format("MMM D")
    return f"{dt_year} Week {dt_week}: {week_begin} - {week_end}"

def get_item(id):
    """
    Return the hash correponding to id.
    """
    pass


def finish(id, dt):
    """
    Record a completion at dt for the task corresponding to id.  
    """
    pass

def relevant(now=pendulum.now('local')):
    """
    Collect the relevant datetimes, inbox, pastdues, beginbys and alerts. Note that jobs are only relevant for the relevant instance of a task 
    """
    # These need to be local times since all times from the datastore and rrule will be local times
    # now = pendulum.now('local')
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + DAY
    today_fmt = today.format("YYYYMMDD")

    id2relevant = {}
    inbox = []
    done = []
    pastdue = []
    beginbys = []
    alerts = []
    current = []

    for item in ETMDB_QUERY:
        instance_interval = [] 
        possible_beginby = None
        possible_alerts = []
        all_tds = []
        if item['itemtype'] == '!':
            inbox.append([0, item['summary'], item.doc_id])
            id2relevant[item.doc_id] = today
            # no pastdues, beginbys or alerts]
            continue
        if item['itemtype'] == '-' and 'f' in item:
            # no pastdues, beginbys or alerts for finished tasks
            continue

        if 's' in item:
            dtstart = item['s'] 
            has_a = 'a' in item
            has_b = 'b' in item
            # for daylight savings time changes
            if isinstance(dtstart, pendulum.Date) and not isinstance(dtstart, pendulum.DateTime):
                dtstart = pendulum.datetime(year=dtstart.year, month=dtstart.month, day=dtstart.day, hour=0, minute=0)
                startdst = None
            else:
                # for discarding daylight saving time differences in repetitions
                try:
                    startdst = dtstart.dst()
                except:
                    print('dtstart:', dtstart)
                    dtstart = dtstart[0]
                    startdst = dtstart.dst()

            if has_b:
                days = int(item['b']) * DAY
                all_tds.extend([DAY, days])
                possible_beginby = days


            if has_a:
                # alerts
                for alert in  item['a']:
                    tds = alert[0]
                    cmd = alert[1]
                    args = alert[2:]
                    all_tds.extend(tds)

                    for td in tds:
                        # td > 0m => earlier than startdt; dt < 0m => later than startdt
                        possible_alerts.append([td, cmd, args])


            # this catches all alerts and beginbys for the item
            if all_tds:
                instance_interval = [today + min(all_tds), tomorrow + max(all_tds)]

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
                        break

                if '-' in item:
                    for dt in item['-']:
                        if type(dt) == pendulum.Date:
                            pass
                        elif dt.dst() and not startdst:
                            dt = dt + dt.dst()
                        elif startdst and not dt.dst():
                            dt = dt - startdst
                        rset.exdate(dt)

                if '+' in item:
                    for dt in item['+']:
                        rset.rdate(dt)

                if item['itemtype'] == '-': 
                    if item.get('o', 'k') == 's':
                        relevant = rset.after(today, inc=True)
                        if relevant:
                            item['s'] = pendulum.instance(relevant)
                            update_db(item.doc_id, item)
                        else:
                            relevant = dtstart
                    else: 
                        # for a restart or keep task, relevant is dtstart
                        relevant = dtstart
                else:
                    # get the first instance after today
                    relevant = rset.after(today, inc=True)
                    if not relevant:
                        relevant = rset.before(today, inc=True)
                    relevant = pendulum.instance(relevant)

                # rset
                if instance_interval:
                    instances = rset.between(instance_interval[0], instance_interval[1], inc=True)
                    if possible_beginby:
                        for instance in instances:
                            if today + DAY <= instance <= tomorrow + possible_beginby:
                                beginbys.append([(instance.date() - today.date()).days, item['summary'], item.doc_id])
                    if possible_alerts:
                        for instance in instances:
                            for possible_alert in possible_alerts:
                                if today <= instance - possible_alert[0] <= tomorrow:
                                    alerts.append([instance - possible_alert[0], possible_alert[0], possible_alert[1], possible_alert[2], item['summary'], item.doc_id])


            elif '+' in item:
                # no @r but @+ => simple repetition
                tmp = [dtstart]
                for x in item['+']:
                    tmp.insort(x)
                aft = [x for x in tmp if x >= today]
                if aft:
                    relevant = aft[0]
                else:
                    bef = [x for x in tmp if x < today]
                    relevant = bef[-1]

                if possible_beginby:
                    for instance in aft:
                        if today + DAY <= instance <= tomorrow + possible_beginby:
                            beginbys.append([(instance.date() - today.date()).days, item['summary'], item.doc_id])
                if possible_alerts:
                    for instance in aft + bef:
                        for possible_alert in possible_alerts:
                            if today <= instance - possible_alert[0] <= tomorrow:
                                alerts.append([instance - possible_alert[0], possible_alert[0], possible_alert[1], possible_alert[2], item['summary]'], item.doc_id])

            else:
                # 's' but not 'r' or '+'
                relevant = dtstart
                if possible_beginby:
                    if today + DAY <= dtstart <= tomorrow + possible_beginby:
                        beginbys.append([(relevant.date() - today.date()).days, item['summary'],  item.doc_id])
                if possible_alerts:
                    for possible_alert in possible_alerts:
                        if today <= dtstart - possible_alert[0] <= tomorrow:
                            alerts.append([dtstart - possible_alert[0], possible_alert[0], possible_alert[1], possible_alert[2], item['summary'], item.doc_id])
        else:
            # no 's'
            relevant = None


        if not relevant:
            continue
        else:
            try:
                relevant = pendulum.instance(relevant)
            except Exception as e:
                print(repr(e))
                print('relevant:', relevant, startdst)
                continue

        pastdue_jobs = False
        if 'j' in item and 'f' not in item:
            # jobs only for the relevant instance of unfinished tasks
            job_id = 0
            for job in item['j']:
                job_id += 1
                if 'f' in job:
                    continue
                # adjust job starting time if 's' in job
                jobstart = relevant - job.get('s', ZERO)
                if jobstart < today:
                    pastdue_jobs = True
                    pastdue.append([(jobstart.date() - today.date()).days, job['summary'], item.doc_id, job_id])
                if 'b' in job:
                    days = int(job['b'] * DAY)
                    if today + DAY <= jobstart <= tomorrow + days:
                        beginbys.append([(jobstart.date() - today.date()).days, job['summary'], item.item_id, job_id])
                if 'a' in job:
                    for alert in job['a']:
                        for td in alert[0]:
                            if today <= jobstart - td <= tomorrow:
                                alerts.append([dtstart - td, td, alert[1], alert[2], job['summary'], item.doc_id, job_id])

        id2relevant[item.doc_id] = relevant

        if item['itemtype'] == '-' and 'f' not in item and not pastdue_jobs and relevant < today:
            pastdue.append([(relevant.date() - today.date()).days, item['summary'], item.doc_id])


    # print(id2relevant) 
    # print('today:', today, "tomorrow:", tomorrow)
    inbox.sort()
    pastdue.sort()
    beginbys.sort()
    alerts.sort()
    week = today.isocalendar()[:2]
    day = (today.format("ddd MMM D"), )
    for item in inbox:
        current.append({'id': item[2], 'sort': (today_fmt, 0), 'week': week, 'day': day, 'columns': ['!', item[1], '']})

    for item in pastdue:
        # rhc = str(item[0]).center(16, ' ') if item[0] in item else ""
        rhc = str(item[0]) + " "*7 if item[0] in item else ""
        current.append({'id': item[2], 'sort': (today_fmt, 1, item[0]), 'week': week, 'day': day, 'columns': ['<', item[1], rhc]})

    for item in beginbys:
        # rhc = str(item[0]).center(16, ' ') if item[0] in item else ""
        rhc = str(item[0]) + " "*7 if item[0] in item else ""
        # rhc = str(item[0]) if item[0] in item else ""
        current.append({'id': item[2], 'sort': (today_fmt, 2, item[0]), 'week': week, 'day': day, 'columns': ['>', item[1], rhc]})

    return current, alerts 


def update_db(id, hsh={}):
    old = ETMDB.get(doc_id=id)
    if not old:
        logger.error(f"Could not get document corresponding to id {id}")
        return
    if old == hsh:
        logger.info(f"Doument corresponding to id {id} unchanged")
        return
    hsh['modified'] = pendulum.now()
    try:
        ETMDB.update(hsh, doc_ids=[id])
    except Exception as e:
        logger.error(f"Error updating document corresponding to id {id}\nhsh {hsh}\nexception: {repr(e)}")

def insert_db(hsh={}):
    """
    Assume hsh has been vetted. 
    """
    if not hsh:
        logger.warn(f"Empty hash passed to insert_db")
        return
    hsh['created'] = pendulum.now()
    try:
        ETMDB.insert(hsh)
    except Exception as e:
        logger.error(f"Error updating database:\nid {id}\nold {old}\nhsh {hsh}\ne {repr(e)}")




def show_history(reverse=True):
    from operator import itemgetter
    from itertools import groupby
    width = 58
    rows = []
    for item in ETMDB:
        for dt, label in [(item.get('created', None), 'c'), (item.get('modified', None), 'm')]:
            if dt is not None:
                dtfmt = dt.format("YYYY-MM-DD")
                itemtype = finished_char if 'f' in item else item['itemtype']
                rows.append(
                        {
                            'id': item.doc_id,
                            'sort': dtfmt,
                            'week': (
                                dt.isocalendar()[:2]
                                ),
                            'day': (
                                dt.format("ddd MMM D"),
                                ),
                            'columns': [itemtype,
                                item['summary'], 
                                f"{dtfmt} {label}"
                                ]
                        }
                        )
    rows.sort(key=itemgetter('sort'), reverse=reverse)
    out_view = []
    num2id = {}

    summary_width = width - 18 
    num = 0
    for i in rows:
        num2id[num] = i['id']
        num += 1
        view_summary = i['columns'][1][:summary_width].ljust(summary_width, ' ')
        # sel_summary = i['columns'][1][:sel_width].ljust(sel_width, ' ')
        # space = " "*(width - len(str(i['columns'][1])) - len(str(i['columns'][2])) - len(num) - 3 - 2)
        # tmp = f"{i['columns'][0]} [{i['columns'][3]}] {sel_summary}{i['columns'][2]}\n" 
        # out_sel.append(fmt_class(tmp, type2style[i['columns'][0]], plain))
        tmp = f" {i['columns'][0]} {view_summary}  {i['columns'][2]}" 
        # out_view.append(fmt_class(tmp, type2style[i['columns'][0]], plain))
        out_view.append(tmp)
    return "\n".join(out_view), num2id

def show_next():
    """
    Unfinished, undated tasks and jobs
    """
    from operator import itemgetter
    from itertools import groupby
    width = 58
    rows = []
    for item in ETMDB:
        if 's' in item or 'f' in item:
            continue
        location = item.get('l', '~none')
        rows.append(
                {
                    'id': item.doc_id,
                    'sort': (location, item['itemtype'], item['summary']),
                    'location': location,
                    'columns': [item['itemtype'],
                        item['summary'], 
                        ]
                }
                )
    rows.sort(key=itemgetter('sort'))
    out_view = []
    num2id = {}

    view_width = width
    num = 0
    for i in rows:
        num2id[num] = i['id']
        num += 1
        # sel_width = view_width - len(num) - 3
        view_summary = i['columns'][1][:25].ljust(view_width, ' ')
        # sel_summary = i['columns'][1][:sel_width].ljust(sel_width, ' ')
        # space = " "*(width - len(str(i['columns'][1])) - len(str(i['columns'][2])) - len(num) - 3 - 2)
        # tmp = f"{i['columns'][0]} [{i['columns'][3]}] {sel_summary}{i['columns'][2]}\n" 
        # out_sel.append(fmt_class(tmp, type2style[i['columns'][0]], plain))
        tmp = f" {i['columns'][0]} {view_summary}  {i['columns'][2]}" 
        # out_view.append(fmt_class(tmp, type2style[i['columns'][0]], plain))
        out_view.append(tmp)
    return "\n".join(out_view), num2id

def fmt_class(txt, cls=None, plain=False):
    if not plain and cls is not None:
        return cls, txt
    else:
        return txt

def no_busy_periods(week, width):
    monday = parse(f"{week[0]}-W{str(week[1]).zfill(2)}-1")
    DD = {}
    h = {}
    t = {0: 'total'.rjust(6, ' ')}
    for i in range(7):
        DD[i+1] = monday.add(days=i).format("D").ljust(2, ' ')

    for weekday in range(1, 8):
        t[weekday] = '0'.center(5, ' ')

    for hour in range(24):
        h.setdefault(hour, {})
        for weekday in range(1, 8):
            h[hour][weekday] = '  .  '
    return busy_template.format(week=fmt_week(week).center(width, ' '), WA=WA, DD=DD, t=t, h=h, l=LL)


def schedule(yw=getWeekNum(), current=[], now=pendulum.now('local'), weeks_before=0, weeks_after=0):
    width = 58
    summary_width = width - 7 - 16
    # yw will be the active week, but now will be the current moment

    d = iso_to_gregorian((yw[0], yw[1], 1))
    dt = pendulum.datetime(d.year, d.month, d.day, 0, 0, 0, tz='local')
    week_numbers = getWeekNumbers(dt, weeks_before, weeks_after)
    if yw not in week_numbers:
        week_numbers.append(yw)
        week_numbers.sort()
    aft_dt, bef_dt = get_period(dt, weeks_before, weeks_after)

    current_day = ""
    current_week = yw == getWeekNum() 
    if current_week:
        current_day = now.format("ddd MMM D")

    rows = []
    busy = []
    for item in ETMDB_QUERY:
        if item['itemtype'] in "!?":
            continue

        if item['itemtype'] == '-':
            done = []
            if 'f' in item:
                done.append([item['f'], item['summary'], item.doc_id, 0])
            if 'h' in item:
                for dt in item['h']:
                    done.append([dt, item['summary'], item.doc_id, 0])
            if 'j' in item:
                j = 0
                for job in item['j']:
                    j += 1
                    if 'f' in job:
                        done.append([job['f'], job['summary'], item.doc_id, j])
            if done:
                # FIXME: h and f timestamps in datastore may not be UTC times
                for row in done:
                    dt = row[0] 
                    if isinstance(dt, pendulum.Date) and not isinstance(dt, pendulum.DateTime): 
                        dt = pendulum.parse(dt.format("YYYYMMDD"), tz='local')
                        dt.set(hour=23, minute=59, second=59)
                        rhc = ''
                    else:
                        rhc = fmt_time(dt).center(16, ' ') 

                    if dt < aft_dt or dt > bef_dt:
                        continue

                    rows.append(
                            {
                                'id': row[2],
                                'sort': (dt.format("YYYYMMDDHHmm"), 1),
                                'week': (
                                    dt.isocalendar()[:2]
                                    ),
                                'day': (
                                    dt.format("ddd MMM D"),
                                    ),
                                'columns': [finished_char,
                                    row[1], 
                                    rhc
                                    ],
                            }
                            )

        if 's' not in item or 'f' in item:
            continue

        for dt, et in item_instances(item, aft_dt, bef_dt):
            if 'j' in item:
                for job in item['j']:
                    jobstart = dt - job.get('s', ZERO)
                    rhc = fmt_extent(jobstart, et).center(16, ' ') if 'e' in item else fmt_time(dt).center(16, ' ')
                    rows.append(
                        {
                            'id': item.doc_id,
                            'sort': (jobstart.format("YYYYMMDDHHmm"), 0),
                            'week': (
                                jobstart.isocalendar()[:2]
                                ),
                            'day': (
                                jobstart.format("ddd MMM D"),
                                ),
                            'columns': [job['status'],
                                set_summary(job['summary'], jobstart), 
                                rhc
                                ]
                        }
                    )

            else:
                rhc = fmt_extent(dt, et).center(16, ' ') if 'e' in item else fmt_time(dt).center(16, ' ')
                rows.append(
                        {
                            'id': item.doc_id,
                            'sort': (dt.format("YYYYMMDDHHmm"), 0),
                            'week': (
                                dt.isocalendar()[:2]
                                ),
                            'day': (
                                dt.format("ddd MMM D"),
                                ),
                            'columns': [item['itemtype'],
                                set_summary(item['summary'], dt), 
                                rhc
                                ]
                        }
                    )
            if et:
                beg_min = dt.hour * 60 + dt.minute
                end_min = et.hour * 60 + et.minute
                y, w, d = dt.isocalendar()
                #             x[0] x[1]  x[2]     x[3]
                # busy.append([(y,w), d, beg_min, end_min])
                busy.append({'sort': dt.format("YYYYMMDDHHmm"), 'week': (y, w), 'day': d, 'period': (beg_min, end_min)})
    if yw == getWeekNum(now):
        rows.extend(current)
    from operator import itemgetter
    from itertools import groupby
    rows.sort(key=itemgetter('sort'))
    busy.sort(key=itemgetter('sort'))

    # for the individual weeks
    agenda_hsh = {}       # yw -> agenda_view
    busy_hsh = {}       # yw -> busy_view
    row2id_hsh = {}     # yw -> row2id
    weeks = set([])

    for week, items in groupby(busy, key=itemgetter('week')):
        weeks.add(week)
        busy_tups = []
        for day, period in groupby(items, key=itemgetter('day')):
            for p in period:
                busy_tups.append([day, p['period']])
        busy_tups.sort()
        h = {}
        busy = {}
        t = {0: 'total'.rjust(6, ' ')}

        monday = parse(f"{week[0]}-W{str(week[1]).zfill(2)}-1")
        DD = {}
        for i in range(7):
            DD[i+1] = monday.add(days=i).format("D").ljust(2, ' ')

        for weekday in range(1, 8):
            t[weekday] = '0'.center(5, ' ')

        for hour in range(24):
            h.setdefault(hour, {})
            for weekday in range(1, 8):
                h[hour][weekday] = '  .  '

        for tup in busy_tups:
            #                 d             (beg_min, end_min)
            busy.setdefault(tup[0], []).append(tup[1])
        for weekday in range(1, 8):
            lofp = busy.get(weekday, [])
            hours = busy_conf_day(lofp)
            t[weekday] = str(hours['total']).center(5, ' ')
            for hour in range(24):
                if hour in hours:
                    h[hour][weekday] = hours[hour]


        busy_hsh[week] = busy_template.format(week=fmt_week(week).center(width, ' '), WA=WA, DD=DD, t=t, h=h, l=LL)

    row2id = {}
    row_num = -1
    # FIXME: deal with weeks without scheduled items
    cache = {}
    for week, items in groupby(rows, key=itemgetter('week')):
        weeks.add(week)
        agenda = []
        row2id = {}
        row_num = 0
        agenda.append("{}".format(fmt_week(week).center(width, ' '))) 
        for day, columns in groupby(items, key=itemgetter('day')):
            for d in day:
                if current_week and d == current_day:
                    d += " (Today)"
                agenda.append(f"  {d}")
                row_num += 1
                for i in columns:
                    summary = i['columns'][1][:summary_width].ljust(summary_width, ' ')
                    rhc = i['columns'][2].rjust(16, ' ')
                    agenda.append(f"    {i['columns'][0]} {summary}{rhc}") 
                    row_num += 1
                    row2id[row_num] = i['id']
        agenda_hsh[week] = "\n".join(agenda)
        row2id_hsh[week] = row2id

    for week in week_numbers:
        tup = []
        if week in agenda_hsh:
            tup.append(agenda_hsh[week])
        else:
            tup.append("{}\n   Nothing scheduled".format(fmt_week(week).center(width, ' ')))
        if week in busy_hsh:
            tup.append(busy_hsh[week])
        else:
            # tup.append("{}\n\n   No busy periods".format(fmt_week(week).center(width, ' ')))
            tup.append(no_busy_periods(week, width))
        if week in row2id_hsh:
            tup.append(row2id_hsh[week])
        else:
            tup.append({})
        cache[week] = tup

    return cache


def import_json(etmdir=None):
    # FIXME: this purges ETMDB
    import json
    # ETMDB = TinyDB('db.json', storage=serialization, default_table='items', indent=1, ensure_ascii=False)
    if etmdir:
        import_file = os.path.join(etmdir, 'data', 'etm-db.json')
    else:
        import_file = '/Users/dag/.etm/data/etm-db.json'
    with open(import_file, 'r') as fo:
        import_hsh = json.load(fo)
    items = import_hsh['items']
    ETMDB.purge()

    docs = []
    for id in items:
        item_hsh = items[id]
        if item_hsh['itemtype'] not in type_keys:
            continue
        z = item_hsh.get('z', 'Factory')
        bad_keys = [x for x in item_hsh if x not in at_keys]
        for key in bad_keys:
            del item_hsh[key]
        bad_keys = [x for x in item_hsh if not item_hsh[x]]
        for key in bad_keys:
            del item_hsh[key]
        if 's' in item_hsh:
            item_hsh['s'] = pen_from_fmt(item_hsh['s'], z)
        elif 'z' in item_hsh:
            del item_hsh['z']
        if 'f' in item_hsh:
            item_hsh['f'] = pen_from_fmt(item_hsh['f'], z)
        # item_hsh['created'] = timestamp_from_id(id, 'UTC')
        item_hsh['created'] = pendulum.now('UTC')
        # if 'f' in item_hsh and item_hsh['f'] < item_hsh['created']:
        #     item_hsh['created'] = item_hsh['f']
        # if 's' in item_hsh and item_hsh['s'] < item_hsh['created']:
        #     item_hsh['created'] = item_hsh['s']
        if 'h' in item_hsh:
            item_hsh['h'] = [pen_from_fmt(x, z) for x in item_hsh['h']]
        if '+' in item_hsh:
            item_hsh['+'] = [pen_from_fmt(x, z) for x in item_hsh['+'] ]
        if '-' in item_hsh:
            item_hsh['-'] = [pen_from_fmt(x, z) for x in item_hsh['-'] ]
        if 'e' in item_hsh:
            item_hsh['e'] = parse_duration(item_hsh['e'])[1]
        if 'a' in item_hsh:
            alerts = []
            for alert in item_hsh['a']:
                # drop the True from parse_duration
                tds = [parse_duration(x)[1] for x in alert[0]]
                # put the largest duration first
                tds.sort(reverse=True)
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
            else:
                print('using jbs', jbs)
                print("ok:", ok,  " lofh:", lofh, " last_completed:", last_completed)

        if 'r' in item_hsh:
            ruls = []
            for rul in item_hsh['r']:
                if 'r' in rul and rul['r'] == 'l':
                    continue
                elif 'f' in rul:
                    if rul['f'] == 'l':
                        continue
                    else:
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
                if 'w' in rul:
                    if isinstance(rul['w'], list):
                        rul['w'] = ["{0}:{1}".format("{W}", x.upper()) for x in rul['w']]
                    else:
                        rul['w'] = "{0}:{1}".format("{W}", rul['w'].upper())
                bad_keys = []
                for key in rul:
                    if key not in amp_keys['r'] or not rul[key]:
                        bad_keys.append(key)
                if bad_keys:
                    for key in bad_keys:
                        del rul[key]
                if rul:
                    ruls.append(rul)
            if ruls:
                item_hsh['r'] = ruls
            else:
                del item_hsh['r']

        # pprint(item_hsh)
        # db.insert(item_hsh)
        docs.append(item_hsh)
    ETMDB.insert_multiple(docs)


def main():
    pass

if __name__ == '__main__':
    import sys
    import doctest
    etmdir = ''
    if len(sys.argv) > 1:
        etmdir = sys.argv.pop(1)
    setup_logging(1, etmdir, 'main.py')

    if len(sys.argv) > 1:
        if 'i' in sys.argv[1]:
            import_json(etmdir)
        if 'j' in sys.argv[1]:
            print_json()
        if 'c' in sys.argv[1]:
            dataview = DataView()
            dataview.refreshCache()
            print([wk for wk in dataview.cache])
            schedule, busy, row2id = dataview.cache[dataview.activeYrWk] 
            print(schedule)
            print(busy)
            pprint(row2id)
            print([wk for wk in dataview.cache])
        if 'p' in sys.argv[1]:
            dataview = DataView(weeks=1, plain=True)
            print(dataview.agenda_view)
            print(dataview.busy_view)
            pprint(dataview.num2id)
        if 'P' in sys.argv[1]:
            dataview = DataView(weeks=4, plain=True)
            print(dataview.agenda_view)
            dataview.nextYrWk()
            print(dataview.agenda_view)
        if 's' in sys.argv[1]:
            dataview = DataView(weeks=1)
            dataview.dtYrWk('2018/12/31')
            print_formatted_text(dataview.agenda_view, style=style)
        if 'S' in sys.argv[1]:
            dataview = DataView()
            print_formatted_text(dataview.agenda_select, style=style)
            print()
            print(dataview.num2id)
        if 'r' in sys.argv[1]:
            current, alerts = relevant()
            pprint(current)
            pprint(alerts)
        if 'V' in sys.argv[1]:
            dataview = DataView(dtstr="2018/12/18", weeks=2)
            # dataview.prevYrWk()
            # print_formatted_text(dataview.agenda_select, style=style)
            print(dataview.num2id)
            num = 9
            print(f"details for {num}:", dataview.num2id[num])
            print(dataview.get_details(num))
        if 'v' in sys.argv[1]:
            dataview = DataView(dtstr="2018/12/18", weeks=2)
            print_formatted_text(dataview.agenda_view, style=style)
            print()
        if 'h' in sys.argv[1]:
            history_view, num2id = show_history()
            print(history_view)



    doctest.testmod()
