#!/usr/bin/env python3
from pprint import pprint
import datetime # for type testing in rrule
import pendulum
from pendulum import parse as pendulum_parse
from pendulum.datetime import Timezone
from pendulum import __version__ as pendulum_version
import calendar
from copy import deepcopy

from ruamel.yaml import YAML
yaml = YAML(typ='safe', pure=True) 

from ruamel.yaml import __version__ as ruamel_version

def parse(s, **kwd):
    return pendulum_parse(s, strict=False, **kwd)

import sys
import re
from re import finditer

from tinydb import __version__ as tinydb_version
from tinydb import Query

import dateutil
import dateutil.rrule
from dateutil.rrule import *
from dateutil import __version__ as dateutil_version

from jinja2 import Template
from jinja2 import __version__ as jinja2_version

import textwrap

import os
import platform

# for compressing backup files
from zipfile import ZipFile, ZIP_DEFLATED

system_platform = platform.platform(terse=True)

python_version = platform.python_version()
developer = "dnlgrhm@gmail.com"
import shutil

import logging
# import logging.config
logger = logging.getLogger()

from operator import itemgetter
from itertools import groupby

from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style
from prompt_toolkit.output import ColorDepth
from prompt_toolkit import __version__ as prompt_toolkit_version

# from __version__ import version as etm_version

# import options

settings = {'ampm': True}
DBITEM = None
DBARCH = None
# NOTE: view.main() will override ampm using the configuration setting
ampm = True


# import pwd
# user_name = pwd.getpwuid(os.getuid()).pw_name

# The style sheet for terminal output
style = Style.from_dict({
    'plain':        '#fffafa',
    'selection':    '#fffafa',
    'inbox':        '#ff00ff',
    'pastdue':      '#87ceeb',
    'begin':        '#ffff00',
    'journal':       '#daa520',
    'event':        '#90ee90',
    'available':    '#1e90ff',
    'waiting':      '#6495ed',
    'finished':     '#191970',
})

type2style = {
        '!': 'class:inbox',
        '<': 'class:pastdue',
        '>': 'class:begin',
        '%': 'class:journal',
        '*': 'class:event',
        '-': 'class:available',
        '+': 'class:waiting',
        '✓': 'class:finished',
        }

FINISHED_CHAR = '✓'

etmdir = None


ETMFMT = "%Y%m%dT%H%M"
ZERO = pendulum.duration(minutes=0)
DAY = pendulum.duration(days=1)
finished_char = u"\u2713"  #  ✓

WKDAYS_DECODE = {"{0}{1}".format(n, d): "{0}({1})".format(d, n) if n else d for d in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'] for n in ['-4', '-3', '-2', '-1', '', '1', '2', '3', '4']}
WKDAYS_ENCODE = {"{0}({1})".format(d, n): "{0}{1}".format(n, d) if n else d for d in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'] for n in ['-4', '-3', '-2', '-1', '+1', '+2', '+3', '+4']}
for wkd in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']:
    WKDAYS_ENCODE[wkd] = wkd

type_keys = {
    "*": "event",
    "-": "task",
    "%": "journal",
    "!": "inbox",
}

type_prompt = u"item type character:"

item_types = """item type characters:\n    """ + """\n    """.join([f"{k}: {v}" for k, v in type_keys.items()])

allowed = {}
required = {}
common_methods = [x for x in 'cdegilmnstux']
repeating_methods = [x for x in '+-o'] + ['rr', 'rc', 'rm', 'rE', 'rh', 'ri', 'rM', 'rn', 'rs', 'ru', 'rW', 'rw']
datetime_methods = [x for x in 'abez']
task_methods = [x for x in 'fhp'] + ['jj', 'ja', 'jb', 'jd', 'je', 'jf', 'ji', 'jl', 'jm', 'jp', 'js', 'ju']

# event
required['*'] = ['s']
allowed['*'] = common_methods + datetime_methods + repeating_methods


# task
required['-'] = []
allowed['-'] = common_methods + datetime_methods + task_methods + repeating_methods

# journal
required['%'] = []
allowed['%'] = common_methods + datetime_methods

# inbox
required['!'] = []
allowed['!'] = common_methods + datetime_methods + task_methods + repeating_methods

requires = {
        'a': ['s'],
        'b': ['s'],
        '+': ['s'],
        '-': ['rr'],
        'o': ['rr'],
        'rr': ['s'],
        'js': ['s'],
        'ja': ['s'],
        'jb': ['s'],
        }

busy_template = """{week}
         {WA[1]} {DD[1]}  {WA[2]} {DD[2]}  {WA[3]} {DD[3]}  {WA[4]} {DD[4]}  {WA[5]} {DD[5]}  {WA[6]} {DD[6]}  {WA[7]} {DD[7]} 
         _____  _____  _____  _____  _____  _____  _____
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
         _____  _____  _____  _____  _____  _____  _____
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

def process_entry(s, settings={}):
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
    >>> process_entry('- has expansion key @x tennis')
    ({(0, 1): ('itemtype', '-'), (1, 20): ('summary', 'has expansion key'), (20, 30): ('x', 'tennis')}, [('itemtype', '-'), ('summary', 'has expansion key'), ('x', 'tennis')])
    >>> process_entry('@e 90m @a 30m, 15m: d @i personal:tennis')
    ({(0, 41): ('itemtype', '@')}, [('itemtype', '@')])
    """
    tups = []
    keyvals = []
    pos_hsh = {}  # (tupbeg, tupend) -> [key, value]
    if not s:
        return {(0, 1): ('itemtype', '')}, [('itemtype', '')]
    elif s[0] not in type_keys:
        return {(0, len(s) + 1): ('itemtype', s[0])}, [('itemtype', s[0])]
    # look for expansions
    xpat = re.compile("\s_[a-zA-Z]+\s")
    matches = xpat.findall(s)
    if settings:
        for x in matches:
            x = x.strip()
            if x in settings['expansions']:
                replacement = settings['expansions'][x]
                s = s.replace(x, replacement)

    pattern = re.compile("\s[@&][a-zA-Z+-]")
    parts = []
    for match in pattern.finditer(s):
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
        elif key in ['@a', '@u']:
            # pos_hsh[tuple((beg, end))] = (key[-1], value)
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

    # def __init__(self, doc_id=None, s=""):
    def __init__(self, dbfile=None):
        """
        """

        self.doc_id = None
        self.entry = ""
        self.init_entry = ""
        self.is_new = True
        self.is_modified = False
        self.created = None
        self.modified = None
        self.set_dbfile(dbfile)
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
                'itemtype': ["item type", "character from * (event), - (task), % (journal) or ! (inbox)", self.do_itemtype],
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
                'm': ["mask", "string to be masked", do_mask],
                'n': ["attendee", "name <email address>", do_string],
                'o': ["overdue", "character from (r)estart, (s)kip or (k)eep", do_overdue],
                'p': ["priority", "priority from 0 (none) to 4 (urgent)", do_priority],
                's': ["start", "starting date or datetime", self.do_datetime],
                't': ["tag", "tag", do_string],
                'u': ["used time", "timeperiod: datetime", do_usedtime],
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
                'ja': ["alert", "list of timeperiod before task start followed by a colon and a list of command", do_alert],
                'jb': ["beginby", " integer number of days", do_beginby],
                'jd': ["description", " string", do_string],
                'je': ["extent", " timeperiod", do_period],
                'jf': ["finished", " datetime", self.do_datetime],
                'ji': ["unique id", " integer or string", do_string],
                'jl': ["location", " string", do_string],
                'jm': ["mask", "string to be masked", do_mask],
                'jp': ["prerequisite ids", "list of ids of immediate prereqs", do_stringlist],
                'js': ["start", "timeperiod before task start when job is due", do_period],
                'ju': ["used time", "timeperiod: datetime", do_usedtime],
                'j?': ["job &-key", "enter &-key", self.do_ampj],
                }
        if not self.entry:
            self.text_changed('', 0, False)


    def set_dbfile(self, dbfile=None):
        # FIXME: this should be based on the etmdir or, better, the json file
        self.settings = settings if settings else {}
        if dbfile is None:
            logger.info(f"dbfile is None")
            self.db = ETMDB
            self.dbarch = DBARCH
            self.dbitem = DBITEM
        else: 
            if not os.path.exists(dbfile):
                logger.error(f"{dbfile} does not exist")
                return
            self.db = data.initialize_tinydb(dbfile)
            self.dbarch = self.db.table('archive', cache_size=None)
            self.dbquery = self.db.table('items', cache_size=None) 

        # # self.settings = settings
        # if 'keep_current' in self.settings and self.settings['keep_current']:
        #     self.currfile = os.path.normpath(os.path.join(etmdir, 'current.txt'))
        # else:
        #     self.currfile = None

    def check_goto_link(self, num=5):
        """
        """
        self.update_item_hsh()
        goto = self.item_hsh.get('g')
        if goto:
            return True, goto
        else:
            return False, "does not have an @g goto entry"

    def get_repetitions(self, num=5):
        """
        Called with a row, we should have an doc_id and can use relevant
        as aft_dt.
        Called while editing, we won't have a row or doc_id and can use '@s'
        as aft_dt
        """
        self.update_item_hsh()
        item = self.item_hsh
        showing =  "Repetitions"
        if not ('s' in item and ('r' in item or '+' in item)):
            logger.debug(f"item: {item}")
            return showing, "not a repeating item"
        relevant = item['s'] 
        starting = format_datetime(relevant)
        pairs = [format_datetime(x[0])[1] for x in item_instances(item, relevant, num+1)]
        starting = format_datetime(relevant.date())[1]
        if len(pairs) > num:
            showing = f"First {num} repetitions"
            pairs = pairs[:num]
        elif pairs:
            showing = "All repetitions"
        else:
            showing = "No repetitions"
        return  showing, f"from {starting}:\n  " + "\n  ".join(pairs)


    def edit_item(self, doc_id=None, entry=""):
        if not (doc_id and entry):
            return None
        item_hsh = self.dbquery.get(doc_id=doc_id)
        self.init_entry = entry
        if item_hsh:
            self.doc_id = doc_id
            self.is_new = False
            self.item_hsh = deepcopy(item_hsh) # created and modified entries
            # self.entry = entry
            self.keyvals = []
            self.text_changed(entry, 0, False)


    def edit_copy(self, doc_id=None, entry=""):
        if not (doc_id and entry):
            return None
        item_hsh = self.db.get(doc_id=doc_id)
        if item_hsh:
            self.doc_id = None
            self.is_new = True
            self.item_hsh = item_hsh # created and modified entries
            # self.entry = entry
            self.keyvals = []
            self.text_changed(entry, 0, False)

    def new_item(self):
        self.doc_id = None
        self.is_new = True
        self.item_hsh = {}
        self.entry = ""


    def delete_item(self, doc_id=None):
        if not (doc_id):
            return None
        if self.db.contains(doc_ids=[doc_id]):
            self.db.remove(doc_ids=[doc_id])
            return True
        else:
            return False


    def schedule_new(self, doc_id, new_dt):
        self.item_hsh = self.db.get(doc_id=doc_id)
        self.doc_id = doc_id
        self.created = self.item_hsh['created']
        changed = False
        if 's' not in self.item_hsh:
            self.item_hsh['s'] = new_dt
            changed = True
        elif 'r' in self.item_hsh and '-' in self.item_hsh and new_dt in self.item_hsh['-']:
            self.item_hsh['-'].remove(new_dt)
            changed = True
        else:
            # works both with and without r
            self.item_hsh.setdefault('+', []).append(new_dt)
            changed = True
        if changed:
            self.item_hsh['created'] = self.created
            self.item_hsh['modified'] = pendulum.now('local')
            self.db.write_back([self.item_hsh], doc_ids=[self.doc_id])
        return changed


    def reschedule(self, doc_id, old_dt, new_dt):
        if old_dt == new_dt:
            return

        changed = False
        self.doc_id = doc_id
        self.item_hsh = self.db.get(doc_id=doc_id)
        if not ('r' in self.item_hsh or '+' in self.item_hsh):
            # not repeating
            self.item_hsh['s'] = new_dt
            self.item_hsh['modified'] = pendulum.now('local')
            self.db.write_back([self.item_hsh], doc_ids=[self.doc_id])
            changed = True
        else:
            # repeating
            removed_old = False
            added_new = self.schedule_new(doc_id, new_dt)
            if added_new:
                removed_old = self.delete_instances(doc_id, old_dt, 0)
            else:
                logger.warn(f"doc_id: {doc_id}; error adding {new_dt}")
            changed = added_new and removed_old
        return changed


    def delete_instances(self, doc_id, instance, which):
        """
        which:
        (0, 'this instance'),
        (1, 'all instances - delete the item itself'),
        """
        self.item_hsh = self.db.get(doc_id=doc_id)
        self.doc_id = doc_id
        self.created = self.item_hsh['created']
        changed = False
        if which == 0:
            # this instance
            if '+' in self.item_hsh and instance in self.item_hsh['+']:
                self.item_hsh['+'].remove(instance)
                changed = True
            elif 'r' in self.item_hsh:
                # instances don't include @s
                self.item_hsh.setdefault('-', []).append(instance)
                changed = True
            else:
                # instance should be @s
                if self.item_hsh['s'] == instance:
                    self.item_hsh['s'] = self.item_hsh['+'].pop(0)
                    changed = True
                else:
                    # should not happen
                    logger.warn(f"could not remove {instance} from {self.item_hsh}")
            if changed:
                self.item_hsh['created'] = self.created
                self.item_hsh['modified'] = pendulum.now('local')
                self.db.write_back([self.item_hsh], doc_ids=[self.doc_id])
            return changed

        else: # 1
            # all instance - delete item
            changed = self.delete_item(doc_id)
            return changed


    def finish_item(self, item_id, job_id, completed_datetime, due_datetime):
        # item_id and job_id should have come from dataview.maybe_finish and thus be valid
        save_item = False
        self.item_hsh = self.db.get(doc_id=item_id)
        self.doc_id = item_id
        self.created = self.item_hsh['created']
        if job_id:
            j = 0
            for job in self.item_hsh['j']:
                if job['i'] == job_id:
                    self.item_hsh['j'][j]['f'] = completed_datetime
                    save_item = True
                    break
                else:
                    j += 1
                    continue
            ok, jbs, last = jobs(self.item_hsh['j'], self.item_hsh)
            if ok:
                self.item_hsh['j'] = jbs
                if last:
                    nxt = get_next_due(self.item_hsh, last, due_datetime)
                    if nxt:
                        self.item_hsh['s'] = nxt
                        self.item_hsh.setdefault('h', []).append(completed_datetime)
                        save_item = True
                    else:  # finished last instance
                        self.item_hsh['f'] = completed_datetime
                        save_item = True

        else:
            # no jobs
            if 's' in self.item_hsh:
                if 'r' in self.item_hsh:
                    nxt = get_next_due(self.item_hsh, completed_datetime, due_datetime)
                    if nxt:
                        self.item_hsh['s'] = nxt
                        self.item_hsh.setdefault('h', []).append(completed_datetime)
                        save_item = True
                    else:  # finished last instance
                        self.item_hsh['f'] = completed_datetime
                        save_item = True

                elif '+' in self.item_hsh:
                    # simple repetition
                    tmp = [self.item_hsh['s']] + self.item_hsh['+']
                    tmp.sort()
                    due = tmp.pop(0)
                    if tmp:
                        self.item_hsh['s'] = tmp.pop(0)
                    if tmp:
                        self.item_hsh['+'] = tmp
                        self.item_hsh.setdefault('h', []).append(completed_datetime)
                        save_item = True
                    else:
                        del self.item_hsh['+']
                        self.item_hsh['f'] = completed_datetime
                        save_item = True
                else:
                    self.item_hsh['f'] = completed_datetime
                    save_item = True
            else:
                self.item_hsh['f'] = completed_datetime
                save_item = True

        if save_item:
            self.item_hsh['created'] = self.created
            self.item_hsh['modified'] = pendulum.now('local')
            self.db.write_back([self.item_hsh], doc_ids=[self.doc_id])


    def record_timer(self, item_id, job_id=None, completed_datetime=None, elapsed_time=None):
        if not (item_id and completed_datetime and elapsed_time):
            return 
        save_item = False
        self.item_hsh = self.db.get(doc_id=item_id)
        self.doc_id = item_id
        self.created = self.item_hsh['created']
        if job_id:
            j = 0
            for job in self.item_hsh['j']:
                if job['i'] == job_id:
                    self.item_hsh['j'][j].setdefault('u', []).append([elapsed_time, completed_datetime])
                    save_item = True
                    break
                else:
                    j += 1
                    continue
        else:
            self.item_hsh.setdefault('u', []).append([elapsed_time, completed_datetime]) 
            save_item = True
        if save_item:
            self.item_hsh['created'] = self.created
            self.item_hsh['modified'] = pendulum.now('local')
            self.db.write_back([self.item_hsh], doc_ids=[self.doc_id])


    def cursor_changed(self, pos):
        # ((17, 24), ('e', '90m'))
        self.interval, self.active = active_from_pos(self.pos_hsh, pos)


    def text_changed(self, s, pos, modified=True):
        """

        """
        # self.is_modified = modified
        self.entry = s
        self.pos_hsh, keyvals = process_entry(s, self.settings)
        removed, changed = listdiff(self.keyvals, keyvals)

        # if removed + changed != []:
        if self.init_entry != self.entry:
            self.is_modified = True
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
        self.keyvals = [kv for kv in keyvals]
        for kv in changed:
            self.update_keyval(kv)


    def update_keyval(self, kv):
        """
        """
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
                    # call the appropriate do for the key 
                    obj, rep = do(val)
                    reply = rep if rep else r
                    if obj:
                        self.object_hsh[kv] = obj
                    else:
                        if kv in self.object_hsh:
                            del self.object_hsh[kv]
            self.askreply[kv] = (ask, reply)
        else:
            display_key = f"@{key}" if len(key) == 1 else f"&{key[-1]}"
            self.askreply[kv] = ('unrecognized key', f'{display_key} is invalid')


    def update_item_hsh(self):
        self.created = self.item_hsh.get('created', None)
        self.item_hsh = {}
        cur_hsh = {}
        cur_key = None
        for pos, (k, v) in self.pos_hsh.items():
            obj = self.object_hsh.get((k, v))
            if not obj:
                continue
            if k in ['a', 'u', 'n', 't']:
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
            # journal the last if necessary 
            self.item_hsh.setdefault(cur_key, []).append(cur_hsh)
            cur_key = None
            cur_hsh = {}

        if 'j' in self.item_hsh:
            ok, res, last = jobs(self.item_hsh['j'], self.item_hsh)
            if ok:
                self.item_hsh['j'] = res
                if last:
                    self.item_hsh['f'] = last
        now = pendulum.now('local')
        if self.is_new:
            # creating a new item or editing a copy of an existing item
            self.created = now
            self.item_hsh['created'] = now
            if self.doc_id is None:
                self.doc_id = self.db.insert(self.item_hsh)
                logger.debug(f"new item {self.doc_id} -> {self.item_hsh}")
            else:
                logger.debug("This shouldn't happen")
                self.db.write_back([self.item_hsh], doc_ids=[self.doc_id])
        else:
            # editing an existing item
            self.item_hsh['created'] = self.created
            self.item_hsh['modified'] = now
            self.db.write_back([self.item_hsh], doc_ids=[self.doc_id])


    def check_requires(self, key):
        """
        Check that key has the prerequisite entries.
        if key in requires, check that each key in requires[k] has a corresponding key, val in keyvals: [(k, v), (k, v), ...]
        """

        missing = []
        if key in requires:
            cur_keys = [k for (k, v) in self.keyvals]
            missing = [f"@{k[0]}" for k in requires[key] if k not in cur_keys]

        if missing:
            display_key = f"@{key[0]}" if len(key) == 1 or key in ['rr', 'jj'] else f"&{key[-1]}"
            return f"Required for {display_key} but missing: {', '.join(missing)}"
        else:
            return ""

    def check_allowed(self, key):
        """
        Check that key is allowed for the given item type or @-key.
        """
        if not self.item_hsh:
            return
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
        >>> item = Item("")
        >>> item.do_at()
        (None, 'The type character must be entered before any @-keys')
        >>> item.item_hsh['itemtype'] = '*'
        >>> obj, rep = item.do_at()
        >>> print(rep) # doctest: +NORMALIZE_WHITESPACE
        required: @s (start)
        available: @+ (include), @- (exclude), @a (alerts), @b (beginby),
          @c (calendar), @d (description), @e (extent), @g (goto), @i (index),
          @l (location), @m (mask), @n (attendee), @o (overdue), @r (repetition
          frequency), @s (start), @t (tag), @u (used time), @x (expansion),
          @z (timezone)
        """
        itemtype = self.item_hsh.get('itemtype', '')
        if itemtype:
            # only @-keys; allow a, u, rr and jj more than once
            already_entered = [k for (k, v) in self.keyvals if len(k) == 1 and k not in ['a', 'u']]
            require = [f"@{k}_({v[0]})" for k, v in self.keys.items() if (k in required[itemtype] and k != '?' and k not in already_entered)] 
            # allow rr to be entered as r and jj as j
            avail = [x for x in allowed[itemtype] if len(x) == 1 or x in ['rr', 'jj'] ]
            logger.debug(f"avail: {avail}")
            allow = [f"@{k[0]}_({v[0]})" for k, v in self.keys.items() if (k in avail and k not in already_entered)] 
            allow.sort()
            logger.debug(f"allow: {allow}")
            prompt = ""
            if require:
                prompt += wrap(f"required: {', '.join(require)}", 2) + "\n"
            if allow:
                prompt += wrap(f"available: {', '.join(allow)}", 2)
            rep = prompt.replace('_', ' ')
        else:
            rep = "The type character must be entered before any @-keys"

        return None, rep

    def do_ampr(self, arg=''):
        """
        Need access to &-keys and names - hence in Item()
        >>> item = Item("")
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
        >>> item = Item("")
        >>> obj, rep = item.do_ampj()
        >>> print(rep)
        job &-keys: &a (alert), &b (beginby), &d (description),
            &e (extent), &f (finished), &i (unique id),
            &l (location), &m (mask), &p (prerequisite ids),
            &s (start), &u (used time)
        """
        keys = [f"&{k[1]}_({v[0]})" for k, v in self.keys.items() if k.startswith('j') and k[1] not in 'j?'] 
        rep = wrap("job &-keys: " + ", ".join(keys), 4, 60).replace('_', ' ')

        return None, rep


    def do_itemtype(self, arg):
        """
        >>> item = Item("")
        >>> item.do_itemtype('')
        (None, 'Choose a character from * (event), - (task), % (journal) or ! (inbox)')
        >>> item.do_itemtype('+')
        (None, "'+' is invalid. Choose a character from * (event), - (task), % (journal) or ! (inbox)")
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
        >>> item = Item("")
        >>> item.do_datetime('fr')
        (None, "'fr' is incomplete or invalid")
        >>> item.do_datetime('2019-01-25')
        (Date(2019, 1, 25), 'Fri Jan 25 2019')
        >>> item.do_datetime('2019-01-25 2p')
        (DateTime(2019, 1, 25, 14, 0, 0, tzinfo=Timezone('America/New_York')), 'Fri Jan 25 2019 2:00pm EST')
        """
        obj = None
        tz = self.item_hsh.get('z', None)
        ok, res, z = parse_datetime(arg, tz)
        if ok:
            obj = res 
            rep = f"local datetime: {format_datetime(obj)[1]}" if ok == 'aware' else format_datetime(obj)[1]
        else:
            rep = res
        return obj, rep

    def do_datetimes(self, args):
        """
        >>> item = Item("")
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
        >>> item = Item("")
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
                rep = f"timezone: {obj}"
            except:
                obj = None
                rep = f"incomplete or invalid timezone: '{arg}'"
                if 'z' in self.item_hsh:
                    del self.item_hsh['z']
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

def is_duplicate(import_hsh, existing_hsh, ignore=[]):
    """
    >>> import_hsh = {'a': 1, 'b': 2}
    >>> existing_hsh = {'b': 2, 'a': 5}
    >>> is_duplicate(import_hsh, existing_hsh)
    False
    >>> is_duplicate(import_hsh, existing_hsh, ['a'])
    True
    """
    mpr = deepcopy(import_hsh)
    xst = deepcopy(existing_hsh)
    for x in ignore:
        if x in mpr:
            del mpr[x]
        if x in xst:
            del xst[x]
    return mpr == xst

# def dictdiff(old_hsh, new_hsh):
#     """
#     >>> old_hsh = {'a': 1, 'b': 2}
#     >>> new_hsh = {'b': 3, 'c': 5}
#     >>> dictdiff(old_hsh, new_hsh)
#     ({'a': 1}, {'b': 3, 'c': 5})
#     """
#     removed = {}
#     changed = {}
#     for k, v in old_hsh.items():
#         if k not in new_hsh:
#             removed[k] = v
#     for k, v in new_hsh.items():
#         if k not in old_hsh or v != old_hsh[k]:
#             changed[k] = v
#     return removed, changed

def datetime_calculator(s):
    """
    s has the format:

        x [+-] y

    where x is a datetime and y is either a datetime or a timeperiod.
    >>> datetime_calculator("2015-03-17 4p + 1d3h15m")
    'Wed Mar 18 2015 7:15PM EDT'
    >>> datetime_calculator("2015-03-17 4p - 1w")
    'Tue Mar 10 2015 4:00PM EDT'
    >>> datetime_calculator("2019-04-14 11:50am Europe/Paris + 9h3m US/Eastern")
    'Sun Apr 14 2019 2:53PM EDT'
    >>> datetime_calculator("2019-04-14 2:53pm US/Eastern - 2019-04-14 11:50am Europe/Paris")
    '9 hours 3 minutes'
    >>> datetime_calculator("2019-04-07 7:45am Europe/Paris - 2019-04-06 5:30pm US/Eastern")
    '8 hours 15 minutes'
    >>> datetime_calculator("2019-04-06 5:30pm US/Eastern + 8h15m Europe/Paris")
    'Sun Apr 7 2019 7:45AM CEST'
    """
    date_calc_regex = re.compile(r'^\s*(.+)\s+([+-])\s+(.+)\s*$')
    timezone_regex = re.compile(r'^(.+)\s+([A-Za-z]+/[A-Za-z]+)$')
    period_string_regex = re.compile(r'^\s*([+-]?(\d+[wWdDhHmM])+\s*$)')

    ampm = settings.get('ampm', True)
    if ampm:
        datetime_fmt = "ddd MMM D YYYY h:mmA zz"
    else:
        datetime_fmt = "ddd MMM D YYYY H:mm zz"

    m = date_calc_regex.match(s)
    if not m:
        return f'Could not parse "{s}"'
    x, pm, y = [z.strip() for z in m.groups()]
    xz = 'local'
    nx = timezone_regex.match(x)
    if nx:
        x, xz = nx.groups()
    yz = 'local'
    ny = timezone_regex.match(y)
    if ny:
        y, yz = ny.groups()
    try:
        ok, dt_x, z = parse_datetime(x, xz)
        pmy = f"{pm}{y}"
        if period_string_regex.match(pmy):
            dur = parse_duration(pmy)[1]
            dt = (dt_x + dur).in_timezone(yz)
            return dt.format(datetime_fmt)
        else:
            ok, dt_y, z = parse_datetime(y, yz)
            if pm == '-':
                res = (dt_x - dt_y).in_words()
                return res
            else:
                return 'error: datetimes cannot be added'
    except ValueError:
        return f'error parsing "{s}"'


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
    >>> dt = parse_datetime("2019-02-01 12:30a", "UTC")
    >>> dt
    ('aware', DateTime(2019, 2, 1, 0, 30, 0, tzinfo=Timezone('UTC')), 'UTC')
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

def format_time(obj):
    if type(obj) != pendulum.DateTime:
        obj = pendulum.instance(obj)
    ampm = settings.get('ampm', True)
    time_fmt = "h:mmA" if ampm else "H:mm"
    res = obj.format(time_fmt)
    if ampm:
        res = res.replace('AM', 'am')
        res = res.replace('PM', 'pm')
    return True, res

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
    ampm = settings.get('ampm', True)
    date_fmt = "YYYY-MM-DD" if short else "ddd MMM D YYYY"
    time_fmt = "h:mmA" if ampm else "H:mm"


    if type(obj) == pendulum.Date:
        return True, obj.format(date_fmt)

    if type(obj) != pendulum.DateTime:
        try:
            obj = pendulum.instance(obj)
        except:
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
threeday_regex = re.compile(r'([+-]?[1234])(MON|TUE|WED|THU|FRI|SAT|SUN)', re.IGNORECASE)
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
            logger.debug(msg)
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
            logger.debug(msg)
        elif self.loglevel == 3:
            logger.warn(msg)

class RDict(dict):
    """
    Constructed from rows of (path, values) tuples. The path will be split using 'split_char' to produce the nodes leading to 'values'. The last element in values is presumed to be the 'id' of the item that generated the row. 
    """

    tab = " " * 2

    def __init__(self, split_char=':'):
        self.split_char = split_char
        self.row = 0
        self.row2id = {}
        self.output = []

    def __missing__(self, key):
        self[key] = RDict()
        return self[key]

    def as_dict(self):
        return self


    def add(self, tkeys, values=()):
        keys = tkeys.split(self.split_char)
        for j in range(len(keys)):
            key = keys[j]
            keys_left = keys[j+1:]
            if not keys_left:
                try:
                    self.setdefault(key, []).append(values)
                except Exception as e:
                    logger.warn(f"error adding key: {key}, values: {values}\n self: {self}; e: {repr(e)}")
            if isinstance(self[key], dict):
                self = self[key]
            elif keys_left:
                self.setdefault(":".join(keys[j:]), []).append(values)
                break

    def as_tree(self, t={}, depth = 0, level=0):
        """ return an indented tree """
        for k in t.keys():
            self.output.append("%s%s" % (depth * RDict.tab,  k))
            self.row += 1 
            depth += 1
            if level and depth > level:
                depth -= 1
                continue

            if type(t[k]) == RDict:
                self.as_tree(t[k], depth, level)
            else:
                for leaf in t[k]:
                    self.output.append("%s%s" % (depth * RDict.tab, leaf[0]))
                    self.row2id[self.row] = leaf[1]
                    self.row += 1 
            depth -= 1
        return "\n".join(self.output), self.row2id


class DataView(object):

    # def __init__(self, loglevel=1, dtstr=None, weeks=1, plain=False):
    def __init__(self, etmdir):
        self.active_view = 'agenda'  
        self.current = []
        self.alerts = []
        self.row2id = []
        self.id2relevant = {}
        self.current_row = 0
        self.agenda_view = ""
        self.done_view = ""
        self.busy_view = ""
        self.calendar_view = ""
        self.cal_locale = None
        self.history_view = ""
        self.cache = {}
        self.itemcache = {}
        self.completions = []
        self.timer_status = 0  # 0: stopped, 1: running, 2: paused
        self.timer_time = ZERO
        self.timer_start = None
        self.timer_id = None
        self.timer_job = None
        self.set_etmdir(etmdir)
        self.views = {
                'a': 'agenda',
                'b': 'busy',
                'c': 'completed',
                'd': 'do next',
                'h': 'history',
                'i': 'index',
                'j': 'journal',
                'r': 'relevant',
                't': 'tags',
                'y': 'yearly',
                }

        self.edit_item = None
        self.is_showing_details = False
        self.is_showing_help = False
        self.is_editing = False
        self.is_showing_items = True
        self.archive_after = 0
        self.get_completions()
        self.refreshRelevant()
        self.activeYrWk = self.currentYrWk
        self.calAdv = pendulum.today().month // 7

        self.refreshAgenda()
        self.refreshCurrent()

    def set_etmdir(self, etmdir):
        self.etmdir = etmdir
        self.backupdir = os.path.join(self.etmdir, 'backups')
        # need these files for backups
        self.dbfile = os.path.normpath(os.path.join(etmdir, 'db.json'))
        self.cfgfile = os.path.normpath(os.path.join(etmdir, 'cfg.yaml'))
        self.settings = settings
        if 'keep_current' in self.settings and self.settings['keep_current']:
            self.currfile = os.path.normpath(os.path.join(etmdir, 'current.txt'))
        else:
            self.currfile = None

        if 'locale' in self.settings:
            locale_str = settings['locale']
            if locale_str:
                pendulum.set_locale(locale_str)
                if locale_str == "en":
                    self.cal_locale = ["en_US", "UTF-8"]
                else:
                    self.cal_locale = [f"{locale_str}_{locale_str.upper()}", "UTF-8"]

        if 'archive_after' in self.settings:
            try:
                self.archive_after = int(self.settings['archive_after'])
            except Exception as e:
                logger.error(f"An integer is required for archive_after - got {self.settings['archive_after']}. {e}")

        self.db = DBITEM
        self.dbarch = DBARCH
        logger.info(f"items: {len(DBITEM)}; archive: {len(DBARCH)}")
        self.possible_archive()


    def get_completions(self):
        """
        Get completions from db items
        """
        completion_keys = ['c', 'g', 'l', 'n',  't', 'i', 'z']
        completions = set([])
        for item in self.db:
            found = {x: v for x, v in item.items() if x in completion_keys}
            for x, v in found.items():
                if isinstance(v, list):
                    for p in v:
                        completions.add(f"@{x} {p}")
                else:
                    completions.add(f"@{x} {v}")
        self.completions = list(completions)
        self.completions.sort()


    def handle_backups(self):
        removefiles = []
        timestamp = pendulum.now('UTC').format("YYYY-MM-DD")
        filelist = os.listdir(self.backupdir)
        # deal with db.json
        dbmtime = os.path.getctime(self.dbfile)
        zipfiles = [x for x in filelist if x.endswith('db.zip')] 
        zipfiles.sort(reverse=True)
        if zipfiles:
            lastdbtime = os.path.getctime(os.path.join(self.backupdir, zipfiles[0]))
        else:
            lastdbtime = None

        if lastdbtime is None or dbmtime > lastdbtime:
            backupfile = os.path.join(self.backupdir, f"{timestamp}-db.json")
            zipfile = os.path.join(self.backupdir, f"{timestamp}-db.zip")
            shutil.copy2(self.dbfile, backupfile)
            with ZipFile(zipfile, 'w', compression=ZIP_DEFLATED, compresslevel=6) as zip:
                zip.write(backupfile, os.path.basename(backupfile))
            os.remove(backupfile)
            logger.info(f"backed up {self.dbfile} to {zipfile}")
            zipfiles.insert(0, f"{timestamp}-db.zip")
            zipfiles.sort(reverse=True)
            removefiles.extend([os.path.join(self.backupdir, x) for x in zipfiles[5:]])
        else:
            logger.info(f"{self.dbfile} unchanged - skipping backup")

        # deal with cfg.yaml
        cfgmtime = os.path.getctime(self.cfgfile)
        cfgfiles = [x for x in filelist if x.endswith('cfg.yaml')] 
        cfgfiles.sort(reverse=True)
        if cfgfiles:
            lastcfgtime = os.path.getctime(os.path.join(self.backupdir, cfgfiles[0]))
        else:
            lastcfgtime = None
        if lastcfgtime is None or cfgmtime > lastcfgtime:
            logger.info(f"lastcfgtime: {lastcfgtime}; cfgmtime: {cfgmtime}; last cfgfile: {cfgfiles[0]}")
            backupfile = os.path.join(self.backupdir, f"{timestamp}-cfg.yaml")
            shutil.copy2(self.cfgfile, backupfile)
            logger.info(f"backed up {self.cfgfile} to {backupfile}")
            cfgfiles.insert(0, f"{timestamp}-cfg.yaml")
            cfgfiles.sort(reverse=True)
            removefiles.extend([os.path.join(self.backupdir, x) for x in 
                cfgfiles[5:]])
        else:
            logger.info(f"{self.cfgfile} unchanged - skipping backup")

        # maybe delete older backups
        if removefiles:
            logger.info(f"removing old files: {removefiles}")
            for f in removefiles:
                os.remove(f)

    def timer_toggle(self, row=None):
        if self.timer_status == 0: # stopped
            # we better have a row corresponding to an item
            res = self.get_row_details(row)
            if not res[0]:
                return None, ''
            self.timer_id = res[0]
            self.timer_job = res[2]
            self.timer_status = 1  # running
            self.timer_start = pendulum.now('local')
        elif self.timer_status == 1: # running
            self.timer_status = 2  # paused
            self.timer_time += pendulum.now() - self.timer_start
        elif self.timer_status == 2: # paused
            self.timer_status = 1 # running
            self.timer_start = pendulum.now()

    def timer_report(self):
        if not self.timer_id or self.timer_status == 0:
            return ''
        status = ['#', '*', '!'][self.timer_status]
        if self.timer_status == 1: # running
            elapsed = self.timer_time + (pendulum.now() - self.timer_start)
        if self.timer_status == 2:  # paused
            elapsed = self.timer_time
        return f"{format_duration(elapsed)} {status}   "



    def timer_clear(self):
        if not self.timer_id:
            return None, ''
        self.timer_status = 0  # 0: stopped, 1: running, 2: paused
        self.timer_time = ZERO
        self.timer_start = None
        self.timer_id = None
        self.timer_job = None

    def set_now(self):
        self.now = pendulum.now('local')  

    def set_active_view(self, c):
        self.current_row = None
        self.active_view = self.views.get(c, 'agenda')

    def show_active_view(self):
        if self.active_view == 'agenda':
            self.refreshAgenda()
            return self.agenda_view
        if self.active_view == 'completed':
            self.refreshAgenda()
            self.row2id = self.done2id 
            return self.done_view
        elif self.active_view == 'busy':
            self.refreshAgenda()
            return self.busy_view
        elif self.active_view == 'yearly':
            self.refreshCalendar()
            return self.calendar_view
        elif self.active_view == 'history':
            self.history_view, self.row2id = show_history(self.db)
            return self.history_view
        elif self.active_view == 'relevant':
            self.relevant_view, self.row2id = show_relevant(self.db, self.id2relevant)
            return self.relevant_view
        elif self.active_view == 'do next':
            self.next_view, self.row2id = show_next(self.db)
            return self.next_view
        elif self.active_view == 'journal':
            self.journal_view, self.row2id = show_journal(self.db, self.id2relevant)
            return self.journal_view
        elif self.active_view == 'index':
            self.index_view, self.row2id = show_index(self.db, self.id2relevant)
            return self.index_view

    def nextYrWk(self):
        self.activeYrWk = nextWeek(self.activeYrWk) 
        self.refreshAgenda()

    def prevYrWk(self):
        self.activeYrWk = prevWeek(self.activeYrWk) 
        self.refreshAgenda()

    def currYrWk(self):
        """Set the active week to one containing today."""
        self.set_now()
        self.currentYrWk = self.activeYrWk = getWeekNum(self.now)
        self.refreshAgenda()

    def dtYrWk(self, dtstr):
        dt = pendulum.parse(dtstr, strict=False)
        self.activeYrWk = getWeekNum(dt)
        self.refreshAgenda()

    def refreshRelevant(self):
        """
        Called to set the relevant items for the current date and to change the currentYrWk and activeYrWk to that containing the current date.
        """
        self.set_now()
        self.currentYrWk = getWeekNum(self.now)
        self.current, self.alerts, self.id2relevant = relevant(self.db, self.now)
        self.refreshCache()

    def refreshAgenda(self):
        if self.activeYrWk not in self.cache:
            self.cache.update(schedule(self.db, yw=self.activeYrWk, current=self.current, now=self.now))
        # agenda, done, busy, row2id, done2id
        self.agenda_view, self.done_view, self.busy_view, self.row2id, self.done2id = self.cache[self.activeYrWk]

    def refreshCurrent(self):
        """
        Agenda for the current and following week
        """
        if self.currfile is None:
            return

        thisYrWk = getWeekNum(self.now)
        nextYrWk = nextWeek(thisYrWk)
        current = []
        for week in [thisYrWk, nextYrWk]:
            if week not in self.cache:
                self.cache.update(schedule(self.db, yw=week, current=self.current, now=self.now))
            agenda, done, busy, num2id, row2id = self.cache[week]
            current.append(agenda)
        with open(self.currfile, 'w') as fo:
            fo.write("\n\n".join(current))
        logger.info(f"saved current schedule to {self.currfile}")

    def show_details(self):
        self.is_showing_details = True 

    def hide_details(self):
        self.is_showing_details = False 

    def get_row_details(self, row=None):
        if row is None:
            return ()
        self.current_row = row
        id_tup = self.row2id.get(row, None)
        if isinstance(id_tup, tuple):
            item_id, instance, job = id_tup
        else:
            item_id = id_tup
            instance = None
            job = None
        return (item_id, instance, job)

    def get_details(self, row=None, edit=False):
        res = self.get_row_details(row)
        if not res:
            return None, ''
        item_id = res[0]

        if not edit and item_id in self.itemcache:
            return item_id, self.itemcache[item_id]
        item = DBITEM.get(doc_id=item_id)
        if item:
            self.itemcache[item_id] = item_details(item, edit)
            return item_id, self.itemcache[item_id] 

        return None, ''

    def get_goto(self, row=None):
        res = self.get_row_details(row)
        if not res:
            return None, ''
        item_id = res[0]
        item = DBITEM.get(doc_id=item_id)
        goto = item.get('g')
        if goto:
            return True, goto
        else:
            return False, f"The item\n   {item['itemtype']} {item['summary']}\n does not have an @g goto entry."

    def get_repetitions(self, row=None, num=5):
        """
        Called with a row, we should have an doc_id and can use relevant
        as aft_dt.
        Called while editing, we won't have a row or doc_id and can use '@s'
        as aft_dt
        """
        res = self.get_row_details(row)
        if not res:
            return None, ''
        item_id = res[0]

        if not (item_id and item_id in self.id2relevant):
            return ''
        showing = "Repetitions"
        item = DBITEM.get(doc_id=item_id)
        if not ('s' in item and ('r' in item or '+' in item)):
            return showing, "not a repeating item"
        relevant = self.id2relevant.get(item_id)
        showing =  "Repetitions"
        details = f"{item['itemtype']} {item['summary']}"
        if not relevant:
            return "Repetitons", details + "none" 
        pairs = [format_datetime(x[0])[1] for x in item_instances(item, relevant, num+1)]
        starting = format_datetime(relevant.date())[1]
        if len(pairs) > num:
            showing = f"First {num} repetitions"
            pairs = pairs[:num]
        else:
            showing = f"All repetitions"
        return  showing, f"from {starting} for\n{details}:\n  " + "\n  ".join(pairs)

    def maybe_finish(self, row):
        """
        For tasks, '-', not already finished.
        No reps and no jobs add @f
        Jobs and no reps
            Which job? add &f
        Reps and no jobs
            Add dt to @h
            Update @s to next instance

        Jobs? Which job?
        Reps? Which instance?

        """ 
        res = self.get_row_details(row)
        if not res:
            return None, ''
        item_id, instance, job_id = res

        item = DBITEM.get(doc_id=item_id)
        if item['itemtype'] != '-':
            return False, 'only tasks can be finished', None, None, None
        if 'f' in item:
            return False, 'task is already finished', None, None, None

        due = self.id2relevant.get(item_id)
        due_str = f"due: {format_datetime(due, short=True)[1]}" if due else ""

        if job_id: 
            for job in item.get('j', []):
                if job['i'] != job_id:
                    continue
                elif job['status'] != '-': 
                    # the requisite job_id is already finished or waiting
                    return False, 'this job is either finished or waiting', None, None, None
                else: 
                    # the requisite job_id and available
                    return True, f"{job['status']} {job['summary']}\n{due_str}", item_id, job_id, due
            # couldn't find job_id
            return False, f"bad job_id: {job_id}", None, None, None

        # we have an unfinished task without jobs
        return True, f"{item['itemtype']} {item['summary']}\n{due_str}", item_id, job_id, due

    def clearCache(self):
        self.cache = {}

    def refreshCache(self):
        self.cache = schedule(ETMDB, self.currentYrWk, self.current, self.now, 5, 20)

    def possible_archive(self):
        """
        Collect old finished tasks, (repeating or not), old non-repeating events,
        and repeating events with old @u entries. Do not collect records.
        """
        if not self.archive_after:
            logger.info(f"archive_after: {self.archive_after} - skipping archive")
            return
        old = pendulum.now() - pendulum.duration(years=self.archive_after)
        rows = []
        for item in self.db:
            if item['itemtype'] == '%':
                # keep records
                continue
            elif 'f' in item:
                if isinstance(item['f'], pendulum.DateTime):
                    if item['f'] < old:
                        # toss old finished tasks including repeating ones
                        rows.append(item)
                        continue
                elif isinstance(item['f'], pendulum.Date):
                    if item['f'] < old.date():
                        # toss old finished tasks including repeating ones
                        rows.append(item)
                        continue
            elif 'r' in item:
                toss = True
                for rr in item['r']:
                    if 'u' not in rr or rr['u'] >= old:
                        toss = False
                        break
                    else:
                        prov = rr['u']
                    # FIXME: complicated whether or not to archive other repeating items with 't' so keep them
                # got here so 'u' item with u < datetime
                if toss:
                    rows.append(item)
                    continue
            elif item['itemtype'] == '*':
                if isinstance(item['s'], pendulum.DateTime):
                    if item['s'] < old:
                        # toss old, non-repeating events
                        rows.append(item)
                        continue
                elif isinstance(item['s'], pendulum.Date):
                    if item['s'] < old.date():
                        # toss old, non-repeating events
                        rows.append(item)
                        continue
            else:
                continue
        logger.info(f"items to archive {len(rows)}: {[item.doc_id for item in rows]}")
        add_items = []
        rem_ids = []
        for item in rows:
            rem_ids.append(item.doc_id)
            item['doc_id'] = item.doc_id
            add_items.append(item)

        try: 
            self.dbarch.insert_multiple(add_items)
        except:
            logger.error(f"archive failed for doc_ids: {rem_ids}")
        else:
            self.db.remove(doc_ids=rem_ids)

        return rows


    def send_mail(self, doc_id):
        item = self.dbquery.get(doc_id=doc_id)
        attendees = item.get('n', None)
        if not attendees:
            logger.error(f"@n (attendees) are not specified in {item}. send_mail aborted.")
            return

        smtp = self.settings['smtp']
        smtp_from = smtp.get('from', None)
        smtp_id = smtp.get('id', None)
        smtp_pw = smtp.get('pw', None)
        smtp_server = smtp.get('server', None)
        smtp_body = smtp.get('body', None)
        if not (smtp_from and smtp_id and smtp_pw and smtp_server and smtp_body):
            logger.error(f"Bad or missing stmp settings in the cfg.json smtp entry: {smtp}. send_mail aborted")
            return
        startdt = item.get('s', "")
        when = startdt.diff_for_humans() if startdt else ""
        start = format_datetime(startdt)[1] if startdt else ""
        summary = item.get('summary', "")
        location = item.get('l', "")
        description = item.get('d', "")
        message = smtp_body.format(start=start, when=when, summary=summary, location=location, description=description)

        # All the necessary ingredients are in place
        import smtplib
        from email.mime.multipart import MIMEMultipart
        # from email.mime.base import MIMEBase
        from email.mime.text import MIMEText
        from email.utils import COMMASPACE, formatdate
        # from email import encoders as Encoders
        assert type(attendees) == list
        msg = MIMEMultipart()
        msg['From'] = smtp_from
        msg['To'] = COMMASPACE.join(attendees)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = item['summary']
        msg.attach(MIMEText(message))
        smtp = smtplib.SMTP_SSL(smtp_server)
        smtp.login(smtp_id, smtp_pw)
        smtp.sendmail(smtp_from, attendees, msg.as_string())
        smtp.close()


    def send_text(self, doc_id):
        item = self.dbquery.get(doc_id=doc_id)
        sms = self.settings['sms']
        sms_from = sms.get('from', None)
        sms_phone = sms.get('phone', None)
        sms_pw = sms.get('pw', None)
        sms_server = sms.get('server', None)
        sms_body = sms.get('body', None)
        if not (sms_from and sms_phone and sms_pw and sms_server and sms_body):
            logger.error(f"Bad or missing smx settings in the cfg.json sms entry: {sms}. send_text aborted.")
            return
        startdt = item.get('s', "")
        when = startdt.diff_for_humans() if startdt else ""
        start = format_datetime(startdt)[1] if startdt else ""
        summary = item.get('summary', "")
        location = item.get('l', "")
        description = item.get('d', "")
        message = sms_body.format(start=start, when=when, summary=summary, location=location, description=description)

        # All the necessary ingredients are in place
        import smtplib
        from email.mime.text import MIMEText
        sms = smtplib.SMTP(sms_server)
        sms.starttls()
        sms.login(sms_from, sms_pw)
        for num in sms_phone.split(','):
            msg = MIMEText(message)
            msg["From"] = sms_from
            msg["Subject"] = summary
            msg['To'] = num
            sms.sendmail(sms_from, sms_phone, msg.as_string())
        sms.quit()



    def refreshCalendar(self):
        """
        Advance = 0 shows the half year containing the current month. Advance 
        = n shows the half year containing the month that is 6 x n months in 
        the future if n > 0 or the past if n < 0.  
        """
        width = shutil.get_terminal_size()[0]
        indent = int((width - 45)/2) * " "
        today = pendulum.today()
        try:

            c = calendar.LocaleTextCalendar(0, self.cal_locale)
            # c = calendar.LocaleTextCalendar(0, locale=self.cal_locale)
        except:
            logger.warn(f"error using locale {self.cal_locale}")
            c = calendar.LocaleTextCalendar(0)
        cal = []
        # make advance = 0 show the half year containing the current month
        y = today.year
        adv = self.calAdv 
        m = 1
        m += 6 * adv
        y += m // 12
        m = m % 12
        for i in range(6): # months in the half year
            cal.append(c.formatmonth(y, m+i, w=2).split('\n'))
        ret = ['']
        for r in range(0, 6, 2):  # 6 months in columns of 2 months
            l = max(len(cal[r]), len(cal[r + 1]))
            for i in range(2):
                if len(cal[r + i]) < l:
                    for j in range(len(cal[r + i]), l + 1):
                        cal[r + i].append('')
            for j in range(l):  # rows from each of the 2 months
                ret.append((u'%-20s     %-20s ' % (cal[r][j], cal[r + 
                    1][j])))

        ret_lines = [f"{indent}{line}" for line in ret]
        ret_str = "\n".join(ret_lines)
        self.calendar_view = ret_str

    def nextcal(self):
        self.calAdv += 1
        self.refreshCalendar()

    def prevcal(self):
        self.calAdv -= 1
        self.refreshCalendar()

    def currcal(self):
        self.calAdv = 0
        self.refreshCalendar()



def wrap(txt, indent=3, width=shutil.get_terminal_size()[0]-3):
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
    # TODO: an international version for this?
    SUFFIXES = {0: 'th', 1: 'st', 2: 'nd', 3: 'rd'}
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
    >>> do_stringlist('red,  green, blue')
    (['red', 'green', 'blue'], 'red, green, blue')
    >>> do_stringlist('Joe Smith <js2@whatever.com>')
    (['Joe Smith <js2@whatever.com>'], 'Joe Smith <js2@whatever.com>')
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
{%- if 'b' in h %}{{ " @b {}".format(h['b']) }}{% endif %}\
{%- if 'z' in h %}{{ " @z {}".format(h['z']) }}{% endif %}\
{%- endset %}\
{{ wrap(title) }} \
{% if 'f' in h %}\
{{ "@f {} ".format(dt2str(h['f'])[1]) }} \
{% endif -%}\
{% if 'a' in h %}\
{%- set alerts %}\
{% for x in h['a'] %}{{ "@a {}: {} ".format(inlst2str(x[0]), ", ".join(x[1])) }}{% endfor %}\
{% endset %}\
{{ wrap(alerts) }} \
{% endif %}\
{% if 'u' in h %}\
{%- set used %}\
{% for x in h['u'] %}{{ "@u {}: {} ".format(in2str(x[0]), dt2str(x[1])[1]) }}{% endfor %}\
{% endset %}
{{ wrap(used) }} \
{% endif %}\
{%- set is = namespace(found=false) -%}\
{%- set index -%}\
{%- for k in ['c', 'i'] -%}\
{%- if k in h %}@{{ k }} {{ h[k] }}{% set is.found = true %} {% endif %}\
{%- endfor %}\
{%- endset %}\
{% if is.found %}
{{ wrap(index) }} \
{% endif %}\
{%- if 't' in h %}
{% for x in h['t'] %}{{ "@t {} ".format(x) }}{% endfor %}\
{% endif %}\
{%- if 'n' in h %}
{% for x in h['n'] %}{{ "@n {} ".format(x) }}{% endfor %}\
{% endif %}\
{%- set ls = namespace(found=false) -%}\
{%- set location -%}\
{%- for k in ['l', 'm', 'g', 'x', 'p'] -%}\
{%- if k in h %}@{{ k }} {{ h[k] }}{% set ls.found = true %} {% endif -%}\
{%- endfor -%}\
{%- endset -%}\
{%- if ls.found -%}\
{{ wrap(location) }} \
{% endif -%}\
{%- if 'r' in h -%}\
{%- for x in h['r'] -%}\
{%- if 'r' in x and x['r'] -%}\
{%- set rrule %}\
{{ x['r'] }}\
{%- for k in ['i', 's', 'M', 'm', 'n', 'w', 'h', 'E', 'c'] -%}
{%- if k in x %} {{ "&{} {}".format(k, one_or_more(x[k])) }}{%- endif %}\
{%- endfor %}
{% if isinstance(x, dict) and 'u' in x %}{{ " &u {} ".format(dt2str(x['u'])[1]) }}{% endif %}\
{%- endset %}
@r {{ wrap(rrule) }} \
{% endif -%}\
{%- endfor %}\
{% if 'o' in h %}\
@o {{ h['o'] }}{% endif %} \
{% endif %}\
{% for k in ['+', '-', 'h'] %}\
{% if k in h and h[k] %}
@{{ k }} {{ wrap(dtlst2str(h[k])) }} \
{%- endif %}\
{%- endfor %}\
{% if 'd' in h %}
@d {{ wrap(h['d'], 0) }} \
{% endif -%}
{%- if 'j' in h %}\
{%- for x in h['j'] %}\
{%- set job -%}\
{{ x['j'] }}\
{%- for k in ['s', 'e'] -%}
{%- if k in x and x[k] %} {{ "&{} {}".format(k, in2str(x[k])) }}{% endif %}\
{%- endfor %}
{%- for k in ['b', 'd', 'l', 'i', 'p'] %}
{%- if k in x and x[k] %} {{ "&{} {}".format(k, one_or_more(x[k])) }}{% endif %}\
{%- endfor %}
{%- if 'a' in x %}\
{%- for a in x['a'] %} {{ "&a {}: {}".format( inlst2str(a[0]), one_or_more(a[1]) ) }}{% endfor %}\
{%- endif %}\
{% if 'u' in x %}\
{%- set used %}
{% for u in x['u'] %}{{ "&u {}: {} ".format(in2str(u[0]), dt2str(u[1])[1]) }}{% endfor %}\
{% endset %}
{{ wrap(used) }} \
{% endif %}\
{% if 'f' in x %}{{ " &f {}".format(dt2str(x['f'])[1]) }}{% endif %}\
{%- endset %}
@j {{ wrap(job) }} \
{%- endfor %}\
{%- endif %}
"""

display_tmpl = entry_tmpl + """\

{% if h.doc_id %}\
{{ h.doc_id }}: \
{% endif %}\
{% if 'created' in h %}\
{{ dt2str(h.created)[1] }}\
{%- endif %}\
{% if 'modified' in h %}\
; {{ dt2str(h.modified)[1] }}\
{%- endif %}\
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
    ok, res = integer(arg, 1, None, False)
    if ok:
        obj = res
        rep = arg
    else:
        obj = None
        rep = f"'{arg}' is invalid. Beginby requires {beginby_str}."
    return obj, rep


def do_usedtime(arg):
    """
    >>> do_usedtime('75m: 9p 2019-02-01')
    ([Duration(hours=1, minutes=15), DateTime(2019, 2, 1, 21, 0, 0, tzinfo=Timezone('America/New_York'))], '1h15m: 2019-02-01 9:00pm')
    """
    if not arg:
        return None, ''
    got_period = got_datetime = False
    rep_period = 'period' 
    rep_datetime = 'datetime'
    parts = arg.split(':')
    period = parts.pop(0)
    if period:
        ok, res = parse_duration(period)
        if ok:
            obj_period = res
            rep_period = format_duration(res)
            got_period = True
        else:
            rep_period = res
    if parts:
        dt = parts.pop(0)
        ok, res, z = parse_datetime(dt)
        if ok:
            obj_datetime = res
            rep_datetime = format_datetime(res, short=True)[1]
            got_datetime = True
        else:
            rep_datetime = res

    if got_period and got_datetime:
        obj = [obj_period, obj_datetime]
        return obj, f"{rep_period}: {rep_datetime}"
    else:
        return None, f"{rep_period}: {rep_datetime}"


def do_alert(arg):
    """
    p1, p2, ...: cmd
    >>> do_alert('')
    (None, '')
    >>> print(do_alert('90m, 45m')[1])  # doctest: +NORMALIZE_WHITESPACE 
    1h30m, 45m:
    commmand is required but missing
    >>> print(do_alert('90m, 45m, 10: d')[1])
    1h30m, 45m: d
    incomplete or invalid periods: 10

    >>> do_alert('90m, 45m, 10m: d')
    ([[Duration(hours=1, minutes=30), Duration(minutes=45), Duration(minutes=10)], ['d']], '1h30m, 45m, 10m: d')
    >>> do_alert('90m, 45m, 10m: d, v')
    ([[Duration(hours=1, minutes=30), Duration(minutes=45), Duration(minutes=10)], ['d', 'v']], '1h30m, 45m, 10m: d, v')

    """
    obj = None
    rep = arg
    parts = arg.split(':')
    periods = parts.pop(0)
    command = parts[0] if parts else None
    if command:
        commands = [x.strip() for x in command.split(',')]
    else:
        commands = []
    if periods:
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
                bad_periods.append(period)
        rep = f"{', '.join(good_periods)}: {', '.join(commands)}"
        if bad_periods:
            obj = None
            rep += f"\nincomplete or invalid periods: {', '.join(bad_periods)}"
        elif command is None:
            obj = None
            rep += f"\ncommmand is required but missing"
        else:
            obj = [obj_periods, commands]

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

# FIXME: Will this work without considering @z?
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
    >>> do_priority(6)
    (None, 'invalid priority: 6 is greater than the allowed maximum. An integer priority number from 0 (none), to 4 (urgent) is required')
    >>> do_priority("1")
    ('1', 'priority: 1')
    """
    prioritystr = "An integer priority number from 0 (none), to 4 (urgent)"
    if arg:
        ok, res = integer(arg, 0, 4, True, "")
        if ok:
            obj = f"{res}"
            rep = f"priority: {arg}"
        else:
            obj = None
            rep = f"invalid priority: {res}. {prioritystr} is required"
    else:
        obj = None
        rep = prioritystr
    return obj, rep


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


# def easter(arg):
#     """
#     byeaster; integer or sequence of integers numbers of days before, < 0,
#     or after, > 0, Easter.
#     >>> easter(0)
#     (True, [0])
#     >>> easter([-364, -30, 0, "45", 260])
#     (True, [-364, -30, 0, 45, 260])
#     """
#     easterstr = "easter: a comma separated list of integer numbers of days before, < 0, or after, > 0, Easter."

#     if arg == 0:
#         arg = [0]

#     if arg:
#         ok, res = integer_list(arg, None, None, True, 'easter')
#         if ok:
#             return True, res
#         else:
#             return False, "invalid easter: {}. Required for {}".format(res, easterstr)
#     else:
#         return False, easterstr


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
    >>> print(do_frequency('z')[1]) # doctest: +NORMALIZE_WHITESPACE 
    invalid frequency: z not in (y)early, (m)onthly, (w)eekly, (d)aily, (h)ourly or mi(n)utely.
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
    >>> do_weekdays('FR(+3), MO(-1)')
    ([FR(+3), MO(-1)], '+3FR, -1MO')
    """
    weekdaysstr = "weekdays: a comma separated list of English weekday abbreviations from SU, MO, TU, WE, TH, FR, SA. Prepend an integer to specify a particular weekday in the month. E.g., 3WE for the 3rd Wednesday or -1FR, for the last Friday in the month."
    if arg:
        args = [x.strip().upper() for x in arg.split(',')]
        bad = []
        good = []
        rep = []
        for x in args:
            m = threeday_regex.match(x)
            if m:
                # fix 3 char weekdays, e.g., -2FRI -> -2FR
                x = f"{m[1]}{m[2][:2]}"
            if x in WKDAYS_DECODE:
                good.append(eval('dateutil.rrule.{}'.format(WKDAYS_DECODE[x])))
                rep.append(x)
            elif x in WKDAYS_ENCODE:
                good.append(eval(x))
                rep.append( WKDAYS_ENCODE[x] )
            else:
                bad.append(x)
        if bad:
            obj = None
            rep = f"incomplete or invalid weekdays: {', '.join(bad)}. {weekdaysstr}"
        else:
            obj = good
            rep = ", ".join(rep)
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


# def monthdays(arg):
#     """
#     >>> monthdays([0, 1, 26, -1, -2])
#     (False, 'invalid monthdays: 0 is not allowed. Required for monthdays: a comma separated list of integer month days from  (1, 2, ..., 31. Prepend a minus sign to count backwards from the end of the month. E.g., use  -1 for the last day of the month.')
#     """

#     monthdaysstr = "monthdays: a comma separated list of integer month days from  (1, 2, ..., 31. Prepend a minus sign to count backwards from the end of the month. E.g., use  -1 for the last day of the month."

#     if arg:
#         ok, res = integer_list(arg, -31, 31, False, "")
#         if ok:
#             return True, res
#         else:
#             return False, "invalid monthdays: {}. Required for {}".format(res, monthdaysstr)
#     else:
#         return False, monthdaysstr


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


def do_mask(arg):
    """
    >>> do_mask('when to the sessions')[0].encoded
    'w5zDnMOSwo7CicOnwo_Ch8Omw43DhsKUwpTDisOnw6DCicOYw6HCkw=='
    """
    return Mask(arg), arg


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

def get_next_due(item, done, due):
    """
    return the next due datetime for an @r repetition 
    """
    lofh = item.get('r')
    if not lofh:
        return ''
    rset = rruleset()
    overdue = item.get('o', 'k')
    if overdue == 'k':
        aft = due
        inc = False
    elif overdue == 'r':
        aft = done
        inc = False
    else:  # 's'
        today = pendulum.today()
        if due < today:
            aft = today
            inc = True
        else:
            aft = due
            inc = False

    using_dates = False
    dtstart = item['s']
    if isinstance(dtstart, pendulum.Date) and not isinstance(dtstart, pendulum.DateTime):
        using_dates = True
        dtstart = pendulum.datetime(year=dtstart.year, month=dtstart.month, day=dtstart.day, hour=0, minute=0)
    for hsh in lofh:
        freq, kwd = rrule_args(hsh)
        kwd['dtstart'] = dtstart
        try:
            rset.rrule(rrule(freq, **kwd))
        except Exception as e:
            logger.error(f"error processing {hsh}: {e}")
            return []

    if '-' in item:
        for dt in item['-']:
            rset.exdate(dt)

    if '+' in item:
        for dt in item['+']:
            rset.rdate(dt)
    nxt_rset = rset.after(aft, inc)
    nxt = pendulum.instance(nxt_rset)
    if using_dates:
        nxt = nxt.date()
    return nxt


def item_instances(item, aft_dt, bef_dt=1):
    """
    Dates and datetimes decoded from the data store will all be aware and in the local timezone. aft_dt and bef_dt must therefore also be aware and in the local timezone.
    In dateutil, the starting datetime (dtstart) is not the first recurrence instance, unless it does fit in the specified rules.  Notice that you can easily get the original behavior by using a rruleset and adding the dtstart as an rdate recurrence.
    Each instance is a tuple (beginning datetime, ending datetime) where ending datetime is None unless the item is an event.

    Get instances from item falling on or after aft_dt and on or before bef_dt or, if bef_dt is an integer, n, get the first n instances after aft_dt. All datetimes will be returned with zero offsets.
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
    >>> item_instances(item_eg, parse('2018-11-17 9am', tz="US/Eastern"), 3)
    [(DateTime(2018, 11, 18, 15, 0, 0, tzinfo=Timezone('US/Eastern')), None), (DateTime(2018, 11, 27, 20, 0, 0, tzinfo=Timezone('US/Eastern')), None)]
    """
    # FIXME 
    # @r given: dateutil behavior @s included only if it fits the repetiton rule
    # @r not given 
    #    @s included
    #    @+ given: @s and each date in @+ added as rdates

    if 's' not in item:
        if 'f' in item:
            return [(item['f'], None)]
        else:
            return []
    instances = []
    dtstart = item['s']
    # print('starting dts:', dtstart)
    # This should not be necessary since the data store decodes dates as datetimes
    if isinstance(dtstart, pendulum.Date) and not isinstance(dtstart, pendulum.DateTime):
        dtstart = pendulum.datetime(year=dtstart.year, month=dtstart.month, day=dtstart.day, hour=0, minute=0)
        startdst = None
        using_dates = True
    else:
        using_dates = False
        # for discarding daylight saving time differences in repetitions
        try:
            startdst = dtstart.dst()
        except:
            print('dtstart:', dtstart)
            dtstart = dtstart[0]

    if isinstance(aft_dt, pendulum.Date) and not isinstance(aft_dt, pendulum.DateTime):
        aft_dt = pendulum.datetime(year=aft_dt.year, month=aft_dt.month, day=aft_dt.day, hour=0, minute=0)
    if isinstance(bef_dt, pendulum.Date) and not isinstance(bef_dt, pendulum.DateTime):
        bef_dt = pendulum.datetime(year=bef_dt.year, month=bef_dt.month, day=bef_dt.day, hour=0, minute=0)

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
                rset.exdate(dt)

        if '+' in item:
            for dt in item['+']:
                rset.rdate(dt)
        if isinstance(bef_dt, int):
            tmp = []
            inc = True
            for i in range(bef_dt):
                aft_dt = rset.after(aft_dt, inc=inc)
                if aft_dt:
                    tmp.append(aft_dt)
                    inc = False # to get the next one
                else:
                    break
            if using_dates:
                instances = [pendulum.instance(x).date() for x in tmp if x] if tmp else []
            else:
                instances = [pendulum.instance(x) for x in tmp if x] if tmp else []
        else:
            instances = [pendulum.instance(x) for x in rset.between(aft_dt, bef_dt, inc=True)]

    elif '+' in item:
        # no @r but @+ => simple repetition
        tmp = [dtstart]
        tmp.extend(item['+'])
        tmp.sort()
        if isinstance(bef_dt, int):
            instances = [x for x in tmp if (x >= aft_dt)][:bef_dt]
        else:
            instances = [x for x in tmp if (x >= aft_dt and x <= bef_dt)]

    else:
        # dtstart >= aft_dt
        if isinstance(bef_dt, int):
            instances = [dtstart] if dtstart >= aft_dt else []
        else:
            instances = [dtstart] if aft_dt <= dtstart <= bef_dt else []

    pairs = []
    for instance in instances: # FIXME: task don't get item['e']
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

# NOTE: job_methods, datetime or undated, are dispatched in jobs() according to whether or not the task has an 's' entry

undated_job_methods = dict(
    d=description,
    e=extent,
    f=timestamp,
    h=history,
    j=title,
    l=location,
    q=timestamp,
    # The last requires consideration of the whole list of jobs
    p=prereqs,
)

datetime_job_methods = dict(
    b=do_beginby,
)
datetime_job_methods.update(undated_job_methods)

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
    >>> data = [{'j': 'Job One', 'a': '2d: d', 'b': 2}, {'j': 'Job Two', 'a': '1d: d', 'b': 1}, {'j': 'Job Three', 'a': '6h: d'}]
    >>> pprint(jobs(data))
    (True,
     [{'a': ['2d: d'],
       'i': '1',
       'j': 'Job One',
       'p': [],
       'req': [],
       'status': '-',
       'summary': ' 1/2/0: Job One'},
      {'a': ['1d: d'],
       'i': '2',
       'j': 'Job Two',
       'p': ['1'],
       'req': ['1'],
       'status': '+',
       'summary': ' 1/2/0: Job Two'},
      {'a': ['6h: d'],
       'i': '3',
       'j': 'Job Three',
       'p': ['2'],
       'req': ['2', '1'],
       'status': '+',
       'summary': ' 1/2/0: Job Three'}],
     None)
    >>> data = [{'j': 'Job One', 'a': '2d: d', 'b': 2, 'f': parse('6/20/18 12p')}, {'j': 'Job Two', 'a': '1d: d', 'b': 1}, {'j': 'Job Three', 'a': '6h: d'}]
    >>> pprint(jobs(data))
    (True,
     [{'a': ['2d: d'],
       'f': DateTime(2018, 6, 20, 12, 0, 0, tzinfo=Timezone('UTC')),
       'i': '1',
       'j': 'Job One',
       'p': [],
       'req': [],
       'status': '✓',
       'summary': ' 1/1/1: Job One'},
      {'a': ['1d: d'],
       'i': '2',
       'j': 'Job Two',
       'p': ['1'],
       'req': [],
       'status': '-',
       'summary': ' 1/1/1: Job Two'},
      {'a': ['6h: d'],
       'i': '3',
       'j': 'Job Three',
       'p': ['2'],
       'req': ['2'],
       'status': '+',
       'summary': ' 1/1/1: Job Three'}],
     None)

    >>> data = [{'j': 'Job One', 'a': '2d: d', 'b': 2, 'f': parse('6/20/18 12p')}, {'j': 'Job Two', 'a': '1d: d', 'b': 1, 'f': parse('6/21/18 12p')}, {'j': 'Job Three', 'a': '6h: d'}]
    >>> pprint(jobs(data))
    (True,
     [{'a': ['2d: d'],
       'f': DateTime(2018, 6, 20, 12, 0, 0, tzinfo=Timezone('UTC')),
       'i': '1',
       'j': 'Job One',
       'p': [],
       'req': [],
       'status': '✓',
       'summary': ' 1/0/2: Job One'},
      {'a': ['1d: d'],
       'f': DateTime(2018, 6, 21, 12, 0, 0, tzinfo=Timezone('UTC')),
       'i': '2',
       'j': 'Job Two',
       'p': ['1'],
       'req': [],
       'status': '✓',
       'summary': ' 1/0/2: Job Two'},
      {'a': ['6h: d'],
       'i': '3',
       'j': 'Job Three',
       'p': ['2'],
       'req': [],
       'status': '-',
       'summary': ' 1/0/2: Job Three'}],
     None)
    >>> data = [{'j': 'Job One', 'a': '2d: d', 'b': 2, 'f': parse('6/20/18 12p')}, {'j': 'Job Two', 'a': '1d: d', 'b': 1, 'f': parse('6/21/18 12p')}, {'j': 'Job Three', 'a': '6h: d', 'f': parse('6/22/18 12p')}]
    >>> pprint(jobs(data))
    (True,
     [{'a': ['2d: d'],
       'i': '1',
       'j': 'Job One',
       'p': [],
       'req': [],
       'status': '-',
       'summary': ' 1/2/0: Job One'},
      {'a': ['1d: d'],
       'i': '2',
       'j': 'Job Two',
       'p': ['1'],
       'req': ['1'],
       'status': '+',
       'summary': ' 1/2/0: Job Two'},
      {'a': ['6h: d'],
       'i': '3',
       'j': 'Job Three',
       'p': ['2'],
       'req': ['2', '1'],
       'status': '+',
       'summary': ' 1/2/0: Job Three'}],
     DateTime(2018, 6, 22, 12, 0, 0, tzinfo=Timezone('UTC')))

    Now add an 'r' entry for at_hsh.
    >>> data = [{'j': 'Job One', 's': '1d', 'a': '2d: d', 'b': 2, 'f': parse('6/20/18 12p', tz="US/Eastern")}, {'j': 'Job Two', 'a': '1d: d', 'b': 1, 'f': parse('6/21/18 12p', tz="US/Eastern")}, {'j': 'Job Three', 'a': '6h: d', 'f': parse('6/22/18 12p', tz="US/Eastern")}]
    >>> data
    [{'j': 'Job One', 's': '1d', 'a': '2d: d', 'b': 2, 'f': DateTime(2018, 6, 20, 12, 0, 0, tzinfo=Timezone('US/Eastern'))}, {'j': 'Job Two', 'a': '1d: d', 'b': 1, 'f': DateTime(2018, 6, 21, 12, 0, 0, tzinfo=Timezone('US/Eastern'))}, {'j': 'Job Three', 'a': '6h: d', 'f': DateTime(2018, 6, 22, 12, 0, 0, tzinfo=Timezone('US/Eastern'))}]
    >>> pprint(jobs(data, {'itemtype': '-', 'r': [{'r': 'd'}], 's': parse('6/22/18 8a', tz="US/Eastern"), 'a': parse('6/22/18 7a', tz="US/Eastern"), 'j': data}))
    (True,
     [{'a': ['2d: d'],
       'b': 2,
       'i': '1',
       'j': 'Job One',
       'p': [],
       'req': [],
       's': '1d',
       'status': '-',
       'summary': ' 1/2/0: Job One'},
      {'a': ['1d: d'],
       'b': 1,
       'i': '2',
       'j': 'Job Two',
       'p': ['1'],
       'req': ['1'],
       'status': '+',
       'summary': ' 1/2/0: Job Two'},
      {'a': ['6h: d'],
       'i': '3',
       'j': 'Job Three',
       'p': ['2'],
       'req': ['2', '1'],
       'status': '+',
       'summary': ' 1/2/0: Job Three'}],
     DateTime(2018, 6, 22, 12, 0, 0, tzinfo=Timezone('US/Eastern')))
    """
    if 's' in at_hsh:
        job_methods = datetime_job_methods
    else:
        job_methods = undated_job_methods

    msg = []
    rmd = []
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
            elif key == 'a':
                res.setdefault('a', []).append(hsh['a'])
            elif key == 'u':
                res.setdefault('u', []).append(hsh['u'])
            elif key == 's':
                res[key] = hsh[key]
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
            id2hsh[i]['status'] = FINISHED_CHAR
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


########################
### start week/month ###
########################

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
    """
    >>> pen_from_fmt("20120622T0000")
    Date(2012, 6, 22)
    """
    dt = pendulum.from_format(s, "YYYYMMDDTHHmm", z)
    if z in ['local', 'Factory'] and dt.hour == dt.minute == 0:
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
    ampm = settings['ampm']
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
    ampm = settings['ampm']

    if ampm:
        diff = beg_dt.hour < 12 and end_dt.hour >= 12
        end_suffix = end_dt.format("A").lower()
        if diff:
            beg_suffix = beg_dt.format("A").lower()

    beg_fmt = drop_zero_minutes(beg_dt)
    end_fmt = drop_zero_minutes(end_dt)

    return f"{beg_fmt}{beg_suffix}-{end_fmt}{end_suffix}"


def fmt_time(dt, ignore_midnight=True):
    ampm = settings['ampm']
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


def print_json(etmdb, edit=False):
    for item in etmdb:
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
    'Mar 5 - 11, 2018 #10'
    >>> fmt_week((2019, 1))
    'Dec 31 - Jan 6, 2019 #1'
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
    # return f"{dt_year} Week {dt_week}: {week_begin} - {week_end}"
    return f"{week_begin} - {week_end}, {dt_year} #{dt_week}"


def get_item(id):
    """
    Return the hash correponding to id.
    """
    pass


# def finish(id, dt):
#     """
#     journal a completion at dt for the task corresponding to id.  
#     """
#     pass


def relevant(db, now=pendulum.now()):
    """
    Collect the relevant datetimes, inbox, pastdues, beginbys and alerts. Note that jobs are only relevant for the relevant instance of a task 
    """
    # These need to be local times since all times from the datastore and rrule will be local times
    # today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today = pendulum.today()
    tomorrow = today + DAY
    today_fmt = today.format("YYYYMMDD")

    id2relevant = {}
    inbox = []
    # done = []
    pastdue = []
    beginbys = []
    alerts = []
    current = []

    for item in db:
        instance_interval = [] 
        possible_beginby = None
        possible_alerts = []
        all_tds = []
        if 'itemtype' not in item:
            logger.warn(f"no itemtype: {item}")
            continue
        if item['itemtype'] == '!':
            inbox.append([0, item['summary'], item.doc_id, None, None])
            id2relevant[item.doc_id] = today

        elif 'f' in item:
            relevant = item['f']
            if isinstance(relevant, pendulum.Date) and not isinstance(relevant, pendulum.DateTime):
                relevant = pendulum.datetime(year=relevant.year, month=relevant.month, day=relevant.day, hour=0, minute=0)


        elif 's' in item:
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
                    all_tds.extend(tds)

                    for td in tds:
                        # td > 0m => earlier than startdt; dt < 0m => later than startdt
                        possible_alerts.append([td, cmd])


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
                        rset.exdate(dt)

                if '+' in item:
                    for dt in item['+']:
                        rset.rdate(dt)

                if item['itemtype'] == '-': 
                    if item.get('o', 'k') == 's':
                        relevant = rset.after(today, inc=True)
                        if relevant: 
                            if item['s'] != pendulum.instance(relevant):
                                item['s'] = pendulum.instance(relevant)
                                update_db(db, item.doc_id, item)
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
                    if instances:
                        logger.info(f"instances for {item['summary']}: {instances}")
                    if possible_beginby:
                        for instance in instances:
                            if today + DAY <= instance <= tomorrow + possible_beginby:
                                beginbys.append([(instance.date() - today.date()).days, item['summary'], item.doc_id, None, instance])
                    if possible_alerts:
                        for instance in instances:
                            for possible_alert in possible_alerts:
                                if today <= instance - possible_alert[0] <= tomorrow:
                                    alerts.append([instance - possible_alert[0], instance, possible_alert[1], item['summary'], item.doc_id])


            elif '+' in item:
                # no @r but @+ => simple repetition
                tmp = [dtstart]
                tmp.extend(item['+'])
                tmp.sort()
                aft = [x for x in tmp if x >= today]
                bef = [x for x in tmp if x < today]
                if aft:
                    relevant = aft[0]
                else:
                    relevant = bef[-1]

                if possible_beginby:
                    for instance in aft:
                        if today + DAY <= instance <= tomorrow + possible_beginby:
                            beginbys.append([(instance.date() - today.date()).days, item['summary'], item.doc_id, None, instance])
                if possible_alerts:
                    for instance in aft + bef:
                        for possible_alert in possible_alerts:
                            if today <= instance - possible_alert[0] <= tomorrow:
                                alerts.append([instance - possible_alert[0], instance, possible_alert[1], item['summary'], item.doc_id])

            else:
                # 's' but not 'r' or '+'
                relevant = dtstart
                if possible_beginby:
                    if today + DAY <= dtstart <= tomorrow + possible_beginby:
                        beginbys.append([(relevant.date() - today.date()).days, item['summary'],  item.doc_id, None, None])
                if possible_alerts:
                    for possible_alert in possible_alerts:
                        if today <= dtstart - possible_alert[0] <= tomorrow:
                            alerts.append([dtstart - possible_alert[0], dtstart, possible_alert[1], item['summary'], item.doc_id])
        else:
            # no 's', no 'f'
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
            for job in item['j']:
                job_id = job.get('i') 
                if 'f' in job:
                    continue
                # adjust job starting time if 's' in job
                jobstart = relevant - job.get('s', ZERO)
                if jobstart.date() < today.date():
                    pastdue_jobs = True
                    pastdue.append([(jobstart.date() - today.date()).days, job['summary'], item.doc_id, job_id, None])
                if 'b' in job:
                    days = int(job['b']) * DAY
                    if today + DAY <= jobstart <= tomorrow + days:
                        beginbys.append([(jobstart.date() - today.date()).days, job['summary'], item.item_id, job_id, None])
                if 'a' in job:
                    for alert in job['a']:
                        for td in alert[0]:
                            if today <= jobstart - td <= tomorrow:
                                alerts.append([dtstart - td, dtstart, alert[1],  job['summary'], item.doc_id, job_id, None])

        id2relevant[item.doc_id] = relevant

        if item['itemtype'] == '-' and 'f' not in item and not pastdue_jobs and relevant.date() < today.date():
            pastdue.append([(relevant.date() - today.date()).days, item['summary'], item.doc_id, None, None])


    # print(id2relevant) 
    # print('today:', today, "tomorrow:", tomorrow)
    inbox.sort()
    pastdue.sort()
    beginbys.sort()
    alerts.sort()
    week = today.isocalendar()[:2]
    day = (today.format("ddd MMM D"), )
    for item in inbox:
        current.append({'id': item[2], 'job': None, 'instance': None, 'sort': (today_fmt, 0), 'week': week, 'day': day, 'columns': ['!', item[1], '']})

    for item in pastdue:
        # rhc = str(item[0]).center(16, ' ') if item[0] in item else ""
        rhc = str(item[0]) + " "*7 if item[0] in item else ""
        try:
            current.append({'id': item[2], 'job': item[3], 'instance': item[4], 'sort': (today_fmt, 1, item[0]), 'week': week, 'day': day, 'columns': ['<', item[1], rhc]})
        except Exception as e:
            logger.warn(f"could not append item: {item}; e: {e}")

    for item in beginbys:
        # rhc = str(item[0]).center(16, ' ') if item[0] in item else ""
        rhc = str(item[0]) + " "*7 if item[0] in item else ""
        # rhc = str(item[0]) if item[0] in item else ""
        current.append({'id': item[2], 'job': item[3], 'instance': item[4], 'sort': (today_fmt, 2, item[0]), 'week': week, 'day': day, 'columns': ['>', item[1], rhc]})

    return current, alerts, id2relevant


def update_db(db, id, hsh={}):
    old = db.get(doc_id=id)
    if not old:
        logger.error(f"Could not get document corresponding to id {id}")
        return
    if old == hsh:
        return
    hsh['modified'] = pendulum.now()
    try:
        db.update(hsh, doc_ids=[id])
    except Exception as e:
        logger.error(f"Error updating document corresponding to id {id}\nhsh {hsh}\nexception: {repr(e)}")


def insert_db(db, hsh={}):
    """
    Assume hsh has been vetted. 
    """
    if not hsh:
        logger.warn(f"Empty hash passed to insert_db")
        return
    hsh['created'] = pendulum.now()
    try:
        db.insert(hsh)
    except Exception as e:
        logger.error(f"Error updating database:\nid {id}\nold {old}\nhsh {hsh}\ne {repr(e)}")


def show_relevant(db, id2relevant):
    width = shutil.get_terminal_size()[0] - 2 
    summary_width = width - 23 
    rows = []
    for item in db:
        if item.doc_id not in id2relevant:
            continue
        id = item.doc_id
        relevant = id2relevant[item.doc_id]
        dtfmt = format_datetime(relevant, short=True)[1]
        itemtype = finished_char if 'f' in item else item['itemtype']
        rows.append(
                {
                    'id': id,
                    'sort': relevant,
                    # 'week': (
                    #     relevant.isocalendar()[:2]
                    #     ),
                    # 'day': (
                    #     relevant.format("ddd MMM D"),
                    #     ),
                    'columns': [itemtype,
                        item['summary'], 
                        dtfmt
                        ]
                }
                )

    rows.sort(key=itemgetter('sort'), reverse=True)
    out_view = []
    num2id = {}
    num = 0
    for i in rows:
        num2id[num] = i['id']
        num += 1
        view_summary = i['columns'][1][:summary_width].ljust(summary_width, ' ')
        tmp = f" {i['columns'][0]} {view_summary}  {i['columns'][2]}" 
        out_view.append(tmp)
    return "\n".join(out_view), num2id


def show_history(db, reverse=True):
    # from itertools import groupby
    # * summary yyyy-mm-dd hh:mmam
    width = shutil.get_terminal_size()[0] - 2 
    rows = []
    for item in db:
        mt = item.get('modified', None)
        if mt is not None:
            dt, label = mt, 'm'
        else:
            dt, label = item.get('created', None), 'c'
        if dt is not None:
            dtfmt = dt.in_timezone('local').format("YYYYMMDD HH:mm")
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

    summary_width = width - 21 
    num = 0
    for i in rows:
        num2id[num] = i['id']
        num += 1
        view_summary = i['columns'][1][:summary_width].ljust(summary_width, ' ')
        tmp = f" {i['columns'][0]} {view_summary}  {i['columns'][2]}" 
        out_view.append(tmp)
    return "\n".join(out_view), num2id


def show_next(db):
    """
    Unfinished, undated tasks and jobs
    """
    width = shutil.get_terminal_size()[0] - 2
    rows = []
    locations = set([])
    for item in db:
        if item['itemtype'] not in ['-'] or 's' in item or 'f' in item:
            continue
        if 'j' in item:
            task_location = item.get('l', '~')
            priority = int(item.get('p', 0))
            sort_priority = 4 - int(priority)
            show_priority = str(priority) if priority > 0 else ""
            for job in item['j']:
                location = job.get('l', task_location)
                status = 0 if job.get('status') == '-' else 1
                rows.append(
                    {
                        'id': item.doc_id,
                        'job': job['i'],
                        'instance': None,
                        'sort': (location, sort_priority, status, job['summary']),
                        'location': location,
                        'columns': [job['status'],
                            job['summary'], 
                            show_priority,
                            ]
                    }
                )
        else:
            location = item.get('l', '~')
            priority = int(item.get('p', 0))
            sort_priority = 4 - int(priority)
            show_priority = str(priority) if priority > 0 else ""
            rows.append(
                    {
                        'id': item.doc_id,
                        'job': None,
                        'instance': None,
                        'sort': (location, sort_priority, 0, item['summary']),
                        'location': location,
                        'columns': [item['itemtype'],
                            item['summary'], 
                            show_priority,
                            ]
                    }
                    )
    rows.sort(key=itemgetter('sort'))

    row2id = {}
    next_view = []
    num = 0
    for location, items in groupby(rows, key=itemgetter('location')):
        locations.add(location)
        num += 1
        next_view.append(f"{location}")
        for i in items:
            row2id[num] = (i['id'], i['instance'], i['job'])
            num += 1
            next_view.append(f"  {i['columns'][0]} {i['columns'][1][:width - 8].ljust(width - 8, ' ')}  {i['columns'][2]}")
    return "\n".join(next_view), row2id

def show_journal(db, id2relevant):
    """
    Undated journals grouped by index entry
    """
    width = shutil.get_terminal_size()[0] - 2
    rows = []
    indices = set([])
    for item in db:
        if item['itemtype'] != '%': #  or 's' in item:
            continue
        # if 'i' not in item:
        #     continue
        index = item.get('i', '~')
        rows.append({
                    'sort': (index, item['summary'], id2relevant.get(item.doc_id)),
                    # 'sort': (index, item['summary']),
                    'index': index,
                    'columns': [item['itemtype'],
                        item['summary'], 
                        item.doc_id],
                    })
    rows.sort(key=itemgetter('sort'))
    rdict = RDict()
    for row in rows:
        path = row['index']
        # values = row['columns']
        values = (
                f"{row['columns'][0]} {row['columns'][1]}", row['columns'][2]
                ) 
        rdict.add(path, values)
    tree, row2id = rdict.as_tree(rdict, level=0)
    return tree, row2id


def show_index(db, id2relevant):
    """
    All items grouped by index entry
    """
    width = shutil.get_terminal_size()[0] - 2
    rows = []
    indices = set([])
    for item in db:
        # if 'i' not in item:
        #     continue
        index = item.get('i', '~')
        rows.append({
                    'sort': (index, item['summary'], id2relevant.get(item.doc_id)),
                    # 'sort': (index, item['summary']),
                    'index': index,
                    'columns': [item['itemtype'][:width - 15],
                        item['summary'], 
                        item.doc_id],
                    })
    rows.sort(key=itemgetter('sort'))
    rdict = RDict()
    for row in rows:
        path = row['index']
        # values = row['columns']
        values = (
                f"{row['columns'][0]} {row['columns'][1]}", row['columns'][2]
                ) 
        try:
            rdict.add(path, values)
        except:
            logger.error(f"error adding path: {path}, values: {values}")
    tree, row2id = rdict.as_tree(rdict, level=0)
    return tree, row2id


def fmt_class(txt, cls=None, plain=False):
    if not plain and cls is not None:
        return cls, txt
    else:
        return txt


def no_busy_periods(week, width):
    ampm = settings['ampm']
    LL = {}
    for hour in range(24):
        if hour % 6 == 0:
            if ampm:
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
    return busy_template.format(week = 8 * ' ' + fmt_week(week).center(47, ' '), WA=WA, DD=DD, t=t, h=h, l=LL)


def schedule(db, yw=getWeekNum(), current=[], now=pendulum.now(), weeks_before=0, weeks_after=0):
    ampm = settings['ampm']
    # yw will be the active week, but now will be the current moment
    LL = {}
    for hour in range(24):
        if hour % 6 == 0:
            if ampm:
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

    width = shutil.get_terminal_size()[0] - 2
    summary_width = width - 7 - 16

    d = iso_to_gregorian((yw[0], yw[1], 1))
    dt = pendulum.datetime(d.year, d.month, d.day, 0, 0, 0, tz='local')
    week_numbers = getWeekNumbers(dt, weeks_before, weeks_after)
    if yw not in week_numbers:
        week_numbers.append(yw)
        week_numbers.sort()
    aft_dt, bef_dt = get_period(dt, weeks_before, weeks_after)


    rows = []
    done = []
    busy = []

    for item in db:
        if item['itemtype'] in "!?":
            continue

        if item['itemtype'] == '-':
            d = []
            if 'f' in item:
                d.append([item['f'], item['summary'], item.doc_id, None])
            if 'h' in item:
                for dt in item['h']:
                    d.append([dt, item['summary'], item.doc_id, None])
            if 'j' in item:
                for job in item['j']:
                    if 'f' in job:
                        d.append([job['f'], job['summary'], item.doc_id, job['i']])
            if d:
                for row in d:
                    dt = row[0] 
                    if isinstance(dt, pendulum.Date) and not isinstance(dt, pendulum.DateTime): 
                        dt = pendulum.parse(dt.format("YYYYMMDD"), tz='local')
                        dt.set(hour=23, minute=59, second=59)
                        rhc = ''
                    else:
                        rhc = fmt_time(dt).center(16, ' ') 

                    if dt < aft_dt or dt > bef_dt:
                        continue

                    done.append(
                            {
                                'id': row[2],
                                'job': row[3],
                                'instance': None,
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

        # get the instances
        for dt, et in item_instances(item, aft_dt, bef_dt):

            instance = dt if '+' in item or 'r' in item else None
            if 'j' in item:
                for job in item['j']:
                    if 'f' in job:
                        continue
                    jobstart = dt - job.get('s', ZERO)
                    job_id = job.get('i', None)
                    rhc = fmt_time(dt).center(16, ' ')
                    rows.append(
                        {
                            'id': item.doc_id,
                            'job': job_id,
                            'instance': instance, 
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
                if 'e' not in item or item['itemtype'] == '-': 
                    rhc = fmt_time(dt).center(16, ' ')
                else:
                    rhc = fmt_extent(dt, et).center(16, ' ') if 'e' in item  else fmt_time(dt).center(16, ' ') 
                rows.append(
                        {
                            'id': item.doc_id,
                            'job': None,
                            'instance': instance,
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
                busy.append({'sort': dt.format("YYYYMMDDHHmm"), 'week': (y, w), 'day': d, 'period': (beg_min, end_min)})
    if yw == getWeekNum(now):
        logger.info(f"current week: {yw}. extending current rows")
        rows.extend(current)
    rows.sort(key=itemgetter('sort'))
    done.sort(key=itemgetter('sort'))
    busy.sort(key=itemgetter('sort'))

    # for the individual weeks
    agenda_hsh = {}     # yw -> agenda_view
    done_hsh = {}       # yw -> done_view
    busy_hsh = {}       # yw -> busy_view
    row2id_hsh = {}     # yw -> row2id
    done2id_hsh = {}     # yw -> row2id
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


        busy_hsh[week] = busy_template.format(week = 8 * ' ' + fmt_week(week).center(47, ' '), WA=WA, DD=DD, t=t, h=h, l=LL)

    row2id = {}
    # done2id = {}
    row_num = -1
    cache = {}
    for week, items in groupby(rows, key=itemgetter('week')):
        weeks.add(week)
        agenda = []
        row2id = {}
        row_num = 0
        agenda.append("{}".format(fmt_week(week).center(width, ' '))) 
        for day, columns in groupby(items, key=itemgetter('day')):
            for d in day:
                if week == yw:
                    current_day = now.format("ddd MMM D")
                    logger.info(f"current week, {yw}. day/today: {d}/{current_day}. day == today: {d == current_day}")
                    if d == current_day:
                        d += " (Today)"
                agenda.append(f"  {d}")
                row_num += 1
                for i in columns:
                    summary = i['columns'][1][:summary_width].ljust(summary_width, ' ')
                    rhc = i['columns'][2].rjust(16, ' ')
                    agenda.append(f"    {i['columns'][0]} {summary}{rhc}") 
                    row_num += 1
                    row2id[row_num] = (i['id'], i['instance'], i['job'])
        agenda_hsh[week] = "\n".join(agenda)
        row2id_hsh[week] = row2id

    for week, items in groupby(done, key=itemgetter('week')):
        weeks.add(week)
        done = []
        done2id = {}
        row_num = 0
        done.append("{}".format(fmt_week(week).center(width, ' '))) 
        for day, columns in groupby(items, key=itemgetter('day')):
            for d in day:
                if week == yw:
                    current_day = now.format("ddd MMM D")
                    logger.info(f"current week, {yw}. day/today: {d}/{current_day}. day == today: {d == current_day}")
                    if d == current_day:
                        d += " (Today)"
                done.append(f"  {d}")
                row_num += 1
                for i in columns:
                    summary = i['columns'][1][:summary_width].ljust(summary_width, ' ')
                    rhc = i['columns'][2].rjust(16, ' ')
                    done.append(f"    {i['columns'][0]} {summary}{rhc}") 
                    row_num += 1
                    done2id[row_num] = (i['id'], i['instance'], i['job'])
        done_hsh[week] = "\n".join(done)
        done2id_hsh[week] = done2id

    for week in week_numbers:
        tup = []
        # agenda
        if week in agenda_hsh:
            tup.append(agenda_hsh[week])
        else:
            tup.append("{}\n   Nothing scheduled".format(fmt_week(week).center(width, ' ')))
        # done
        if week in done_hsh:
            tup.append(done_hsh[week])
        else:
            tup.append("{}\n   Nothing completed".format(fmt_week(week).center(width, ' ')))
        # busy
        if week in busy_hsh:
            tup.append(busy_hsh[week])
        else:
            tup.append(no_busy_periods(week, width))
        # row2id
        if week in row2id_hsh:
            tup.append(row2id_hsh[week])
        else:
            tup.append({})
        # done2id
        if week in done2id_hsh:
            tup.append(done2id_hsh[week])
        else:
            tup.append({})
        # agenda, done, busy, row2id, done2id
        cache[week] = tup

    return cache

def temp_to_items(etmdir=None):
    temp_dbfile = os.path.join(etmdir, 'temp.json')
    TEMPDB = data.initialize_tinydb(temp_dbfile)


def import_text(import_file=None):
    if not import_file:
        return ""
    import_file = os.path.normpath(os.path.expanduser(import_file))
    if not os.path.exists(import_file):
        return f"could not locate: {import_file}"
    import tempfile
    docs = []
    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_dbfile = os.path.join(tmpdirname, 'temp.json')
        TEMPDB = data.initialize_tinydb(temp_dbfile)
        TEMPDB.purge()
        with open(import_file, 'r') as fo:
            for line in fo:
                try:
                    s = line.strip()
                    item = Item(temp_dbfile)
                    item.new_item()
                    item.text_changed(s, 1)
                    item.update_item_hsh()
                    docs.append(item.item_hsh)
                except Exception as e:
                    logger.error(f"error processing line: '{s}'; {repr(e)}")

    # TEMPDB.insert_multiple(docs)
    # temp_items = TEMPDB.table('items', cache_size=None)

    exst = []
    new = []
    dups = []
    for x in ETMDB:
        if 'modified' in x:
            del x['modified']
        if 'created' in x:
            del x['created']
        exst.append(x)
    for x in docs:
        created = x.get('created')
        if created:
            del x['created']
        if 'modified' in x:
            del x['modified']
        if x in exst:
            x['created'] = created
            dups.append(x)
        else:
            x['created'] = created
            new.append(x)

    ids = []
    if new:
        ids = ETMDB.insert_multiple(new)
    msg = f"imported {len(new)} items"
    if ids:
        msg += f"\n  ids: {ids[0]}-{ids[-1]}."
    if dups:
        msg += f"\n  rejected {len(dups)} items as duplicates"
    logger.info(msg)
    return msg


def import_json(import_file=None):
    if not import_file:
        return ""
    import_file = os.path.normpath(os.path.expanduser(import_file))
    if not os.path.exists(import_file):
        return f"could not locate: {import_file}"
    import json
    with open(import_file, 'r') as fo:
        import_hsh = json.load(fo)
    items = import_hsh['items']
    docs = []
    dups = 0
    add = 0
    for id in items:
        item_hsh = items[id]
        itemtype = item_hsh.get('itemtype')
        if not itemtype:
            continue
        summary = item_hsh.get('summary')
        if not summary:
            continue
        z = item_hsh.get('z', 'Factory')
        bad_keys = [x for x in item_hsh if not item_hsh[x]]
        for key in bad_keys:
            del item_hsh[key]
        # z = item_hsh.get('z')
        if 's' in item_hsh:
            item_hsh['s'] = pen_from_fmt(item_hsh['s'], z)
        if 'f' in item_hsh:
            item_hsh['f'] = pen_from_fmt(item_hsh['f'], z)
        item_hsh['created'] = pendulum.now('UTC')
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
                    if not rul[key]:
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

        docs.append(item_hsh)
    # now check for duplicates. If an item to be imported has the same type, summary and starting time as an existing item, regard it as a duplicate and do not import it.
    exst = []
    new = []
    dups = 0
    for x in ETMDB:
        exst.append({
                    'itemtype': x.get('itemtype'),
                    'summary': x.get('summary'),
                    's': x.get('s')
                    })
    for x in docs:
        y = {
                    'itemtype': x.get('itemtype'),
                    'summary': x.get('summary'),
                    's': x.get('s')
                    }
        if y in exst:
            dups += 1
        else:
            new.append(x)

    ids = []
    if new:
        ids = ETMDB.insert_multiple(new)
    msg = f"imported {len(new)} items"
    if ids:
        msg += f"\n  ids: {ids[0]}-{ids[-1]}."
    if dups:
        msg += f"\n  rejected {dups} items as duplicates"
    logger.info(msg)
    return msg


def about(padding=0):
    logo_lines = [
        "                          ",
        " █████╗██████╗███╗   ███╗ ",
        " ██╔══╝╚═██╔═╝████╗ ████║ ",
        " ███╗    ██║  ██╔████╔██║ ",
        " ██╔╝    ██║  ██║╚██╔╝██║ ",
        " █████╗  ██║  ██║ ╚═╝ ██║ ",
        " ╚════╝  ╚═╝  ╚═╝     ╚═╝ ",
        "  Event and Task Manager  ",
    ]
    width=shutil.get_terminal_size()[0]-2-padding
    output = []
    for line in logo_lines:
        output.append(line.center(width, ' ') + "\n")
    logo = "".join(output)

    copyright = wrap(f"Copyright 2009-{pendulum.today().format('YYYY')}, Daniel A Graham. All rights reserved. This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version. See www.gnu.org/licenses/gpl.html for details.", 0, width)

    summary = wrap(f"This application provides a format for using plain text entries to create events, tasks and other items and a prompt_toolkit based interface for creating and modifying items as well as viewing them.", 0, width)

    ret1 = f"""\
{logo}
{summary}

etm-dgraham: {etm_version}
Developer:   dnlgrhm@gmail.com
GitHub:      github.com/dagraham/etm-mv
Discussion:  groups.google.com/group/eventandtaskmanager

{copyright}\
"""

    ret2 = f"""
python:           {python_version}
dateutil:         {dateutil_version}
pendulum:         {pendulum_version}
prompt_toolkit:   {prompt_toolkit_version}
tinydb:           {tinydb_version}
jinja2:           {jinja2_version}
ruamel.yaml:      {ruamel_version}
platform:         {system_platform}
"""
    return ret1, ret2


dataview = None
item = None
def main(etmdir="", *args):
    global dataview, item, db, ampm, settings
    logdir = os.path.join(etmdir, "logs")
    setup_logging(2, logdir)
    # NOTE: DataView called in model.main
    dataview = DataView(etmdir)
    settings = dataview.settings
    # ampm = settings['ampm'] 
    # print('ampm', ampm)
    db = dataview.db
    item = Item(etmdir)
    dataview.refreshCache()


if __name__ == '__main__':
    sys.exit('model.py should only be imported')

    # import doctest
    # doctest.testmod()

    # etmdir = ''
    # if len(sys.argv) > 1:
    #     etmdir = sys.argv.pop(1)
    # setup_logging(2, etmdir)

    # if len(sys.argv) > 1:
    #     if 'a' in sys.argv[1]:
    #         print(about())
    #     if 'i' in sys.argv[1]:
    #         import_json(etmdir)
    #     if 'j' in sys.argv[1]:
    #         print_json()
    #     if 'c' in sys.argv[1]:
    #         dataview = DataView()
    #         dataview.refreshCache()
    #         print([wk for wk in dataview.cache])
    #         schedule, busy, row2id = dataview.cache[dataview.activeYrWk] 
    #         print(schedule)
    #         print(busy)
    #         pprint(row2id)
    #         print([wk for wk in dataview.cache])
    #     if 'p' in sys.argv[1]:
    #         dataview = DataView(weeks=2, plain=True)
    #         print(dataview.agenda_view)
    #         # print(dataview.busy_view)
    #         # pprint(dataview.num2id)
    #     if 'P' in sys.argv[1]:
    #         dataview = DataView(weeks=4, plain=True)
    #         print(dataview.agenda_view)
    #         dataview.nextYrWk()
    #         print(dataview.agenda_view)
    #     if 's' in sys.argv[1]:
    #         dataview = DataView(weeks=1)
    #         dataview.dtYrWk('2018/12/31')
    #         print_formatted_text(dataview.agenda_view, style=style)
    #     if 'S' in sys.argv[1]:
    #         dataview = DataView()
    #         print_formatted_text(dataview.agenda_select, style=style)
    #         print()
    #         print(dataview.num2id)
    #     if 'r' in sys.argv[1]:
    #         current, alerts, id2relevant = relevant()
    #         pprint(current)
    #         pprint(alerts)
    #     if 'h' in sys.argv[1]:
    #         history_view, num2id = show_history()
    #         print(history_view)

