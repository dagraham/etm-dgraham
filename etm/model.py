#!/usr/bin/env python

from pprint import pprint
import datetime # for type testing in rrule
import pendulum
from pendulum import parse as pendulum_parse
from pendulum.datetime import Timezone
from pendulum import __version__ as pendulum_version
import locale
import calendar
from copy import deepcopy
import math
from ruamel.yaml import YAML
yaml = YAML(typ='safe', pure=True)

from ruamel.yaml import __version__ as ruamel_version

import dateutil
from dateutil.rrule import *
from dateutil import __version__ as dateutil_version
from dateutil.parser import parse as dateutil_parse
from dateutil.tz import gettz

# for saving timers
import pickle

from warnings import filterwarnings
def parse(s, **kwd):
    # return pendulum_parse(s, strict=False, parserinfo=pi, **kwd)
    pi = dateutil.parser.parserinfo(
            dayfirst=settings['dayfirst'],
            yearfirst=settings['yearfirst']
            )
    dt = pendulum.instance(dateutil_parse(s, parserinfo=pi))
    if 'tzinfo' in kwd:
        tz = kwd['tzinfo']
        dt = dt.replace(tzinfo=tz)
    return dt

import sys
import re

from tinydb import __version__ as tinydb_version
from tinydb.table import Document

from jinja2 import Template
from jinja2 import __version__ as jinja2_version

import textwrap
import os
import platform

import string
# for automatic job ids
LOWERCASE = list(string.ascii_lowercase)

# for compressing backup files
from zipfile import ZipFile, ZIP_DEFLATED

system_platform = platform.platform(terse=True)

python_version = platform.python_version()
developer = "dnlgrhm@gmail.com"
import shutil

from operator import itemgetter
from itertools import groupby, combinations

from prompt_toolkit.styles import Style
from prompt_toolkit import __version__ as prompt_toolkit_version

settings = {'ampm': True}
# These are set in _main_
DBITEM = None
DBARCH = None
ETMDB = None
data = None
# NOTE: view.main() will override ampm using the configuration setting
ampm = True
logger = None

def sortdt(dt):
    # assumes dt is either a date or a datetime
    try:
        # this works if dt is a datetime
        return dt.format("YYYYMMDDHHmm")
    except:
        # this works if dt is a date by providing 00 for HH and mm
        return dt.format("YYYYMMDD0000")



PHONE_REGEX = re.compile(r'[0-9]{10}@.*')
KONNECT_REGEX = re.compile(r'^.+:\s+(\d+)\s*$')

# The style sheet for terminal output
style = Style.from_dict({
    'plain':        '#fffafa',
    'selection':    '#fffafa',
    'inbox':        '#ff00ff',
    'pastdue':      '#87ceeb',
    'begin':        '#ffff00',
    'journal':      '#daa520',
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
UPDATE_CHAR = "𝕦"
INBASKET_CHAR = "𝕚"
KONNECT_CHAR = 'k'
LINK_CHAR = 'g'
PIN_CHAR = 'p'
ELLIPSiS_CHAR = '…'
LINEDOT = ' · '  # ܁ U+00B7 (middle dot)

etmdir = None

ETMFMT = "%Y%m%dT%H%M"
ZERO = pendulum.duration(minutes=0)
ONEMIN = pendulum.duration(minutes=1)
DAY = pendulum.duration(days=1)

# finished_char = u"\u2713"  #  ✓

WKDAYS_DECODE = {"{0}{1}".format(n, d): "{0}({1})".format(d, n) if n else d for d in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'] for n in ['-4', '-3', '-2', '-1', '', '1', '2', '3', '4']}
WKDAYS_ENCODE = {"{0}({1})".format(d, n): "{0}{1}".format(n, d) if n else d for d in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'] for n in ['-4', '-3', '-2', '-1', '+1', '+2', '+3', '+4']}
for wkd in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']:
    WKDAYS_ENCODE[wkd] = wkd

type_keys = {
    "*": "event",
    "-": "task",
    "✓": "finished",
    "%": "journal",
    "!": "inbox",
}

type_prompt = u"item type character:"

item_types = """item type characters:\n    """ + """\n    """.join([f"{k}: {v}" for k, v in type_keys.items()])

allowed = {}
required = {}
common_methods = [x for x in 'cdgiklmnstuxz']
repeating_methods = [x for x in '+-o'] + ['rr', 'rc', 'rm', 'rE', 'rh', 'ri', 'rM', 'rn', 'rs', 'ru', 'rW', 'rw']
datetime_methods = [x for x in 'abe']
task_methods = [x for x in 'efhp'] + ['jj', 'ja', 'jb', 'jd', 'je', 'jf', 'ji', 'jl', 'jm', 'jp', 'js', 'ju']

# event
required['*'] = ['s']
allowed['*'] = common_methods + datetime_methods + repeating_methods


# task
required['-'] = []
allowed['-'] = common_methods + datetime_methods + task_methods + repeating_methods

# journal
required['%'] = []
allowed['%'] = common_methods + ['+']

# inbox
required['!'] = []
allowed['!'] = common_methods + datetime_methods + task_methods + repeating_methods

requires = {
        'a': ['s'],
        'b': ['s'],
        # 'u': ['i'],
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

def subsets(l):
    """
    Return a list of the possible subsets of the list of strings, l, together with the size of the subset. E.g., if l = ('blue', 'green', 'red'), return [(1, 'blue'), (1, 'green'), (1, 'red'), (2, 'blue & green'), (2, 'blue & red'), (2, 'green & red'), (3, 'blue & green & red')]
    """
    l.sort()
    ret = [('1', x) for x in l]
    if len(l) > 1:
        # add an element for the list of all elements of l
        ret.append((str(len(l)), ' & '.join(l)))
    if len(l) > 2:
        for i in range(2, len(l)):
            # add an element for each subset of length i of l
            tmp = list(combinations(l, i))
            for tup in tmp:
                ret.append((str(i), ' & '.join(list(tup))))
    else:
        ret.append(('~', '~'))
    return ret


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
    total_minutes = sum(e - b for (b, e) in busy_minutes + conf_minutes)
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
    xpat = re.compile("@x\s+[a-zA-Z]+\s")
    match = xpat.findall(s)
    if match and settings:
        xparts = match[0].split(' ')
        if xparts[1] in settings['expansions']:
            replacement = settings['expansions'][xparts[1]] + xparts[2]
            s = s.replace(match[0], replacement)


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
    # return the last p, v pair
    return p, v


class Item(dict):
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
                'summary': ["summary", "brief item description. Append an '@' to add an option.", self.do_summary],
                '+': ["include", "list of datetimes to include", self.do_datetimes],
                '-': ["exclude", "list of datetimes to exclude", self.do_datetimes],
                'a': ["alerts", "list of alerts", do_alert],
                'b': ["beginby", "number of days for beginby notices", do_beginby],
                'c': ["calendar", "calendar", do_string],
                'd': ["description", "item details", do_paragraph],
                'e': ["extent", "timeperiod", do_period],
                'f': ["finish", "completion datetime", self.do_datetime],
                'g': ["goto", "url or filepath", do_string],
                'h': ["completions", "list of completion datetimes", self.do_datetimes],
                'i': ["index", "forward slash delimited string", do_string],
                'k': ["konnection", "document id", do_konnection],
                'l': ["location", "location or context, e.g., home, office, errands", do_string],
                'm': ["mask", "string to be masked", do_mask],
                'n': ["attendee", "name <email address>", do_string],
                'o': ["overdue", "character from (r)estart, (s)kip, (k)eep or (p)reserve", do_overdue],
                'p': ["priority", "priority from 0 (none) to 4 (urgent)", do_priority],
                's': ["start", "starting date or datetime", self.do_datetime],
                't': ["tag", "tag", do_string],
                'u': ["used time", "timeperiod: datetime", do_usedtime],
                # 'w': ['who', 'who is responsible for this item', do_string],
                'x': ["expansion", "expansion key", do_string],
                'z': ["timezone", "a timezone entry such as 'US/Eastern' or 'Europe/Paris' or 'float' to specify a naive/floating datetime", self.do_timezone],
                '?': ["@-key", "", self.do_at],

                'rr': ["repetition frequency", "character from (y)ear, (m)onth, (w)eek,  (d)ay, (h)our, mi(n)ute. Append an '&' to add a repetition option.", do_frequency],
                'ri': ["interval", "positive integer", do_interval],
                'rm': ["monthdays", "list of integers 1 ... 31, possibly prepended with a minus sign to count backwards from the end of the month", do_monthdays],
                'rE': ["easterdays", "number of days before (-), on (0) or after (+) Easter", do_easterdays],
                'rh': ["hours", "list of integers in 0 ... 23", do_hours],
                'rM': ["months", "list of integers in 1 ... 12", do_months],
                'rn': ["minutes", "list of integers in 0 ... 59", do_minutes],
                'rw': ["weekdays", "list from SU, MO, ..., SA, possibly prepended with a positive or negative integer", do_weekdays],
                'rW': ["week numbers", "list of integers in 1, ... 53", do_weeknumbers],
                'rc': ["count", "integer number of repetitions", do_count],
                'ru': ["until", "datetime", self.do_until],
                'rs': ["set positions", "integer", do_setpositions],
                'r?': ["repetition &-key", "enter &-key", self.do_ampr],

                'jj': ["summary", "job summary. Append an '&' to add a job option.", do_string],
                'ja': ["alert", "list of timeperiod before task start followed by a colon and a list of command", do_alert],
                'jb': ["beginby", " integer number of days", do_beginby],
                'jd': ["description", " string", do_paragraph],
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

    def __repr__(self):
        return f"""
doc_id:      {self.doc_id}
is_new:      {self.is_new}
is_modified: {self.is_modified}
item_hsh:    {self.item_hsh}
                """

    def set_dbfile(self, dbfile=None):
        self.settings = settings if settings else {}
        if dbfile is None:
            self.db = ETMDB
            self.dbarch = DBARCH
            self.dbitem = DBITEM
            self.dbquery = DBITEM

        else:
            if not os.path.exists(dbfile):
                logger.error(f"{dbfile} does not exist")
                return
            self.db = data.initialize_tinydb(dbfile)
            self.dbarch = self.db.table('archive', cache_size=None)
            self.dbquery = self.db.table('items', cache_size=None)

    def use_archive(self):
        self.query_mode = "archive table"
        self.db = DBARCH

    def use_items(self):
        self.query_mode = "items table"
        self.db = DBITEM

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
            return showing, "not a repeating item"
        relevant = date_to_datetime(item['s'])

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
        item_hsh = self.db.get(doc_id=doc_id)
        # item_hsh = self.dbquery.get(doc_id=doc_id)
        self.init_entry = entry
        if item_hsh:
            self.doc_id = doc_id
            self.is_new = False
            self.item_hsh = deepcopy(item_hsh) # created and modified entries
            self.keyvals = []
            self.text_changed(entry, 0, False)


    def edit_copy(self, doc_id=None, entry=""):
        if not (doc_id and entry):
            return None
        item_hsh = self.db.get(doc_id=doc_id)
        if item_hsh:
            self.doc_id = None
            self.is_new = True
            self.item_hsh = deepcopy(item_hsh) # created and modified entries
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
        try:
            self.db.remove(doc_ids=[doc_id])
            return True
        except:
            return False


    def add_used(self, doc_id, usedtime):
        # usedtime = "period_str: datetime_str"

        self.item_hsh = self.db.get(doc_id=doc_id)
        self.doc_id = doc_id
        self.created = self.item_hsh['created']
        ut = [x.strip() for x in usedtime.split(': ')]
        if len(ut) != 2:
            return False

        per_ok, per = parse_duration(ut[0])
        if not per_ok:
            return False
        dt_ok, dt, z = parse_datetime(ut[1])
        if not dt_ok:
            return False

        used_times = self.item_hsh.get("u", [])
        used_times.append([per, dt])
        self.item_hsh['u'] = used_times
        self.item_hsh['created'] = self.created
        self.item_hsh['modified'] = pendulum.now('local')
        self.db.update(db_replace(self.item_hsh), doc_ids=[self.doc_id])

        return True



    def schedule_new(self, doc_id, new_dt):
        self.item_hsh = self.db.get(doc_id=doc_id)
        self.doc_id = doc_id
        self.created = self.item_hsh['created']
        changed = False
        if 's' not in self.item_hsh:
            self.item_hsh['s'] = new_dt
        elif 'r' in self.item_hsh and '-' in self.item_hsh and new_dt in self.item_hsh['-']:
            self.item_hsh['-'].remove(new_dt)
        else:
            # works both with and without r
            self.item_hsh.setdefault('+', []).append(new_dt)
        changed = True
        if changed:
            self.item_hsh['created'] = self.created
            self.item_hsh['modified'] = pendulum.now('local')
            self.db.update(db_replace(self.item_hsh), doc_ids=[self.doc_id])
        return changed



    def reschedule(self, doc_id, old_dt, new_dt):
        if old_dt == new_dt:
            return

        changed = False
        self.doc_id = doc_id
        self.item_hsh = self.db.get(doc_id=doc_id)
        if 'r' not in self.item_hsh and '+' not in self.item_hsh:
            # not repeating
            self.item_hsh['s'] = new_dt
            self.item_hsh['modified'] = pendulum.now('local')
            self.db.update(db_replace(self.item_hsh), doc_ids=[self.doc_id])
            changed = True
        else:
            # repeating
            removed_old = False
            added_new = self.schedule_new(doc_id, new_dt)
            if added_new:
                removed_old = self.delete_instances(doc_id, old_dt, 0)
            else:
                logger.warning(f"doc_id: {doc_id}; error adding {new_dt}")
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
                    logger.warning(f"could not remove {instance} from {self.item_hsh}")
            if changed:
                self.item_hsh['created'] = self.created
                self.item_hsh['modified'] = pendulum.now('local')

                self.db.update(db_replace(self.item_hsh), doc_ids=[self.doc_id])
        else: # 1
            # all instance - delete item
            changed = self.delete_item(doc_id)

        return changed


    def finish_item(self, item_id, job_id, completed_datetime, due_datetime):
        # item_id and job_id should have come from dataview.hsh ok, maybe_finish and thus be valid
        save_item = False
        self.item_hsh = self.db.get(doc_id=item_id)
        self.doc_id = item_id
        self.created = self.item_hsh['created']
        logger.debug(f"completed: {completed_datetime}; due: {due_datetime}")
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
                    logger.debug(f"nxt: {nxt}")
                    if nxt:
                        if 'r' in self.item_hsh:
                            for i in range(len(self.item_hsh['r'])):
                                if 'c' in self.item_hsh['r'][i] and self.item_hsh['r'][i]['c'] > 0:
                                    logger.debug(f"item_hsh[i]: {self.item_hsh['r'][i]}")
                                    self.item_hsh['r'][i]['c'] -= 1
                                    break
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
                    logger.debug(f"nxt: {nxt}")
                    if nxt:
                        for i in range(len(self.item_hsh['r'])):
                            if 'c' in self.item_hsh['r'][i] and self.item_hsh['r'][i]['c'] > 0:
                                logger.debug(f"item_hsh[i]: {self.item_hsh['r'][i]}")
                                self.item_hsh['r'][i]['c'] -= 1
                                break
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
            num_finished = settings.get('num_finished', 0)
            if 'h' in self.item_hsh and num_finished:
                ok = True
                # only truncate completions for infinitely repeating tasks
                for rr in self.item_hsh.get('r', {}):
                    if 'c' in rr or 'u' in rr:
                        # we have a count or an until: keep all completions
                        ok = False
                if ok:
                    sh = self.item_hsh['h']
                    sh.sort(key=sortdt)
                    self.item_hsh['h'] = sh[-num_finished:]

            self.item_hsh['created'] = self.created
            self.item_hsh['modified'] = pendulum.now('local')
            self.db.update(db_replace(self.item_hsh), doc_ids=[self.doc_id])
            return True
        return False


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
            self.db.update(db_replace(self.item_hsh), doc_ids=[self.doc_id])


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
        TODO: add return status
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

    # def set_item_hsh(self, hsh={}):
    #     self.item_hsh = hsh

    def check_item_hsh(self):
        logger.debug(f"item_hsh: {self.item_hsh}")
        created = self.item_hsh.get('created', None)
        self.item_hsh = {'created': created}
        cur_hsh = {}
        cur_key = None
        msg = []
        for pos, (k, v) in self.pos_hsh.items():
            obj = self.object_hsh.get((k, v))
            if not obj:
                msg.append(f"bad entry for {k}: {v}")
                continue
            elif k in ['a', 'u', 'n', 't', 'k']:
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
        for k in ['k', 't', 'n']:
            # remove duplicates
            # XXX: should 'u' be included?
            if k in self.item_hsh:
                self.item_hsh[k] = list(set(self.item_hsh[k]))
        if cur_key:
            # record the last if necessary
            self.item_hsh.setdefault(cur_key, []).append(cur_hsh)
            cur_key = None
            cur_hsh = {}

        if 'j' in self.item_hsh:
            ok, res, last = jobs(self.item_hsh['j'], self.item_hsh)
            if ok:
                self.item_hsh['j'] = res
                if last:
                    self.item_hsh['f'] = last
            else:
                msg.extend(res)
        if self.item_hsh.get('z', None) not in [None, 'float']:
            del self.item_hsh['z']
        if msg:
            logger.debug(f"{msg}")

        return msg


    def update_item_hsh(self):
        msg = self.check_item_hsh()

        links = self.item_hsh.get('k', [])
        if links:
            # make sure the doc_id refers to an actual document
            self.item_hsh['k'] = [x for x in links if self.db.contains(doc_id=x)]

        if self.is_modified and not msg:
            logger.debug(f"{repr(self)}")
            now = pendulum.now('local')
            if self.is_new:
                # creating a new item or editing a copy of an existing item
                self.item_hsh['created'] = now
                if self.doc_id is None:
                    logger.debug(f"inserting: {self.item_hsh}")
                    self.doc_id = self.db.insert(self.item_hsh)
                else:
                    self.db.update(db_replace(self.item_hsh), doc_ids=[self.doc_id])
            else:
                # editing an existing item
                if 'k' in self.item_hsh and self.doc_id in self.item_hsh['k']:
                    # remove self referential konnections
                    self.item_hsh['k'].remove(self.doc_id)
                self.item_hsh['modified'] = now
                self.db.update(db_replace(self.item_hsh), doc_ids=[self.doc_id])


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
            allow = [f"@{k[0]}_({v[0]})" for k, v in self.keys.items() if (k in avail and k not in already_entered)]
            allow.sort()
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
        if obj:
            self.item_hsh['summary'] = obj

            rep = arg
        elif 'summary' in self.item_hsh:
            del self.item_hsh['summary']

        return obj, rep

    # FIXME: Will this work without considering @z?
    def do_until(self, arg):
        """
        Return a datetime object. This will be an aware datetime in the local timezone.
        >>> until('2019-01-03 10am')
        (True, DateTime(2019, 1, 3, 10, 0, 0, tzinfo=Timezone('America/New_York')))
        >>> until('whenever')
        (False, 'Include repetitions falling on or before this datetime.')
        """
        obj = None
        tz = self.item_hsh.get('z', None)
        ok, res, z = parse_datetime(arg, tz)
        if ok:
            if isinstance(res, pendulum.Date) and not isinstance(res, pendulum.DateTime):
                return obj, "a datetime is required"
            obj = res
            rep = f"local datetime: {format_datetime(obj)[1]}" if ok == 'aware' else format_datetime(obj)[1]
        else:
            rep = "Include repetitions falling on or before this datetime"
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
    period_string_regex = re.compile(r'^\s*(([+-]?\d+[wdhmMy])+\s*$)')

    ampm = settings.get('ampm', True)
    datetime_fmt = "ddd MMM D YYYY h:mmA zz" if ampm else "ddd MMM D YYYY H:mm zz"
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
        if not ok:
            return f"error: could not parse '{x}'"
        dt_x = date_to_datetime(dt_x)
        pmy = f"{pm}{y}"
        if period_string_regex.match(y):
            ok, dur = parse_duration(pmy)
            if not ok:
                return f"error: could not parse '{y}'"
            dt = (dt_x + dur).in_timezone(yz)
            return dt.format(datetime_fmt)
        else:
            ok, dt_y, z = parse_datetime(y, yz)
            if not ok:
                return f"error: could not parse '{y}'"
            dt_y = date_to_datetime(dt_y)
            if pm == '-':
                return (dt_x - dt_y).in_words()
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

    To get a datetime for midnight, schedule for 1 second later - the second will be dropped from the hours and minutes datetime:
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
    >>> dt = parse_datetime("2019-03-24 5:00PM")
    >>> dt
    ('local', DateTime(2019, 3, 24, 17, 0, 0, tzinfo=Timezone('America/New_York')), None)
    """

    filterwarnings("error")
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
        s = s.strip()
        if s == 'now':
            return True, pendulum.now(tz=tzinfo), z

        dt_str = ''
        dur_str = ''
        dt_and_dur_regex = re.compile(r'^(.+)\s+([+-].+)?$')
        days_or_more_regex = re.compile(r'[dwM]')
        g = dt_and_dur_regex.match(s)
        if g:
            # we have dt and dur strings
            dt_str = g.group(1)
            dur_str = g.group(2)
        elif s[0] in ['+', '-']:
            # must be a dur string
            dur_str = s
        else:
            # must be a dt string
            dt_str = s

        if dt_str:
            dt = pendulum.now(tz=tzinfo) if dt_str.strip() == 'now' else parse(dt_str, tzinfo=tzinfo)
        else:
            dt = pendulum.now(tz=tzinfo)
            if dur_str and re.search(r'[dwM]', dur_str):
                dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)

        dur = parse_duration(dur_str)[1] if dur_str else ZERO
        res = dt + dur

    except Exception as e:
        return False, f"'{s}' is incomplete or invalid: {e}", z
    else:
        if tzinfo in ['local', 'float'] and (
            res.hour,
            res.minute,
            res.second,
            res.microsecond,
        ) == (0, 0, 0, 0):
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
    if isinstance(arg, pendulum.DateTime):
        return True, arg
    elif isinstance(arg, pendulum.Date):
        return True, date_to_datetime(arg)
    try:
        # res = parse(arg).strftime(ETMFMT)
        res = parse(arg)
    except:
        return False, 'invalid time-stamp: {}'.format(arg)
    return True, res


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

def fivechar_datetime(obj):
    """
    Return a 5 character representation of datetime obj using
    the format XX<sep>YY. Examples when today is 2020/10/15
    1:15pm today -> 13:15
    today -> 00:00
    2p on Nov 7 of this year -> 11/07
    11a on Jan 17 of 2012 -> 12.01
    """
    if type(obj) != pendulum.DateTime:
        obj = pendulum.instance(obj)
    now = pendulum.now('local')

    if obj.year == now.year:
        if obj.month == now.month:
            if obj.day == now.day:
                return obj.format("HH:mm")
            else:
                return obj.format("MM/DD")
        else:
            return obj.format("MM/DD")
    else:
        return obj.format("YY.MM")


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
    dayfirst = settings.get('dayfirst', False)
    yearfirst = settings.get('yearfirst', False)
    logger.debug(f"model dayfirst: {dayfirst}; yearfirst: {yearfirst}")
    md = "D/M" if dayfirst else "M/D"
    ymd = f"YY/{md}" if yearfirst else f"{md}/YY"

    date_fmt = ymd if short else "ddd MMM D YYYY"
    time_fmt = "h:mmA" if ampm else "H:mm"


    if type(obj) == pendulum.Date:
        return True, obj.format(date_fmt)

    if type(obj) != pendulum.DateTime:
        try:
            obj = pendulum.instance(obj)
        except:
            return False, "a pendulum date or datetime."

    # we want all-day events to display as dates
    if (obj.hour, obj.minute, obj.second, obj.microsecond) == (0, 0, 0, 0):
        # treat as date
        return True, obj.format(date_fmt)

    if obj.format('Z') == '':
        # naive datetime
        if (obj.hour, obj.minute, obj.second, obj.microsecond) == (0, 0, 0, 0):
            # treat as date
            return True, obj.format(date_fmt)
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
    return ", ".join([format_datetime(x)[1] for x in obj_lst])


def plain_datetime_list(obj_lst):
    return ", ".join([plain_datetime(x)[1] for x in obj_lst])

def format_hours_and_tenths(obj):
    """
    Convert a pendulum duration object into hours and tenths of an hour rounding up to the nearest tenth.
    """
    if not isinstance(obj, pendulum.Duration):
        return None
    usedtime_minutes = settings.get('usedtime_minutes', 1)
    try:
        if usedtime_minutes == 1:
            return format_duration(obj, short=True)
        minutes = 0
        if obj.weeks:
            minutes += obj.weeks * 7 * 24 * 60
        if obj.remaining_days:
            minutes += obj.remaining_days * 24 * 60
        if obj.hours:
            minutes += obj.hours * 60
        if obj.minutes:
            minutes += obj.minutes
        if minutes:
            return f"{math.ceil(minutes/usedtime_minutes)/(60/usedtime_minutes)}h"
        else:
            return "0m"

    except Exception as e:
        logger.error(f"error: {e} formatting {obj}")
        return None


def round_minutes(obj):
    """
    if hours, show hours and minutes
    otherwise, minutes and seconds
    """
    seconds = 60 if obj.remaining_seconds >= 30 else obj.remaining_seconds
    return pendulum.duration(weeks=obj.weeks, days=obj.remaining_days, hours=obj.hours, minutes=obj.minutes, seconds=seconds)



def format_duration(obj, short=False):
    """
    if short report only hours and minutes, else include weeks and days
    >>> td = pendulum.duration(weeks=1, days=2, hours=3, minutes=27)
    >>> format_duration(td)
    '1w2d3h27m'
    """
    if not isinstance(obj, pendulum.Duration):
        return None
    obj = round_minutes(obj)
    hours = obj.hours
    try:
        until =[]
        if obj.weeks:
            if short:
                hours += obj.weeks * 7 * 24
            else:
                until.append(f"{obj.weeks}w")

        if obj.remaining_days:
            if short:
                hours += obj.remaining_days * 24
            else:
                until.append(f"{obj.remaining_days}d")
        minutes = obj.minutes

        if hours:
            until.append(f"{hours}h")
        if minutes:
            until.append(f"{minutes}m")
        if not until:
            until.append("0m")
        return "".join(until)
    except Exception as e:
        logger.error(f"{obj}: {e}")
        return None


def format_duration_list(obj_lst):
    try:
        return ", ".join([format_duration(x) for x in obj_lst])
    except Exception as e:
        logger.error(f"{obj_lst}: {e}")


period_regex = re.compile(r'(([+-]?)(\d+)([wdhmMy]))+?')
expanded_period_regex = re.compile(r'(([+-]?)(\d+)\s(week|day|hour|minute|month|year)s?)+?')
relative_regex = re.compile(r'(([+-])(\d+)([wdhmMy]))+?')
threeday_regex = re.compile(r'([+-]?[1234])(MON|TUE|WED|THU|FRI|SAT|SUN)', re.IGNORECASE)
anniversary_regex = re.compile(r'!(\d{4})!')


def parse_duration(s):
    """\
    Take a period string and return a corresponding pendulum.duration.
    Examples:
        parse_duration('-2w3d4h5m')= Duration(weeks=-2,days=3,hours=4,minutes=5)
        parse_duration('1h30m') = Duration(hours=1, minutes=30)
        parse_duration('-10m') = Duration(minutes=10)
    where:
        y: years
        M: months
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

    knms = {
            'y': 'years',
            'M': 'months',
            'month': 'months',
            'months': 'months',
            'w': 'weeks',
            'week': 'weeks',
            'weeks': 'weeks',
            'd': 'days',
            'day': 'days',
            'days': 'days',
            'h': 'hours',
            'hour': 'hours',
            'hours': 'hours',
            'm': 'minutes',
            'minute': 'minutes',
            'minutes': 'minutes',
            }

    kwds = {
            'years': 0,
            'months': 0,
            'weeks': 0,
            'days': 0,
            'hours': 0,
            'minutes': 0
            }

    m = period_regex.findall(str(s))
    if not m:
        m = expanded_period_regex.findall(str(s))
        if not m:
            return False, f"Invalid period string '{s}'"
    for g in m:
        if g[3] not in knms:
            return False, f"invalid period argument: {g[3]}"

        num = -int(g[2]) if g[1] == '-' else int(g[2])
        if num:
            kwds[knms[g[3]]] = num
    td = pendulum.duration(**kwds)

    return True, td


sys_platform = platform.system()
mac = sys.platform == 'darwin'
windoz = sys_platform in ('Windows', 'Microsoft')

from time import perf_counter as timer

# FIXME: is this still used?
class TimeIt(object):
    def __init__(self, loglevel=1, label=""):
        self.loglevel = loglevel
        self.label = label
        msg = "{0} timer started; loglevel: {1}".format(self.label, self.loglevel)
        if self.loglevel in [1, 2]:
            logger.debug(msg)
        elif self.loglevel == 3:
            logger.warning(msg)
        self.start = timer()

    def stop(self, *args):
        self.end = timer()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        msg = "{0} timer stopped; elapsed time: {1} milliseconds".format(self.label, self.msecs)
        if self.loglevel in [1, 2]:
            logger.debug(msg)
        elif self.loglevel == 3:
            logger.warning(msg)


class NDict(dict):
    """
    Constructed from rows of (path, values) tuples. The path will be split using 'split_char' to produce the nodes leading to 'values'. The last element in values is presumed to be the 'id' of the item that generated the row.
    """

    # tab = " " * 2
    tab = 2

    def __init__(self, split_char='/'):
        self.split_char = split_char
        self.width = shutil.get_terminal_size()[0] - 2
        self.row = 0
        self.row2id = {}
        self.output = []
        self.flag_len = 4 # gkptp

    def __missing__(self, key):
        self[key] = NDict()
        return self[key]

    def as_dict(self):
        return self

    def leaf_detail(self, detail, depth):
        dindent = NDict.tab * (depth + 1) * " "
        paragraphs = detail.split('\n')
        ret = []
        for para in paragraphs:
            ret.extend(textwrap.fill(para, initial_indent=dindent, subsequent_indent=dindent, width=self.width-NDict.tab*(depth-1)).split('\n'))
        return ret


    def add(self, tkeys, values=()):
        """
        We want values always to have 4 components:
            0) itemtype
            1) summary
            2) flags3
            3) rhc (a constant length and pre justified)
            4) doc_id

        Leaf output will begin with indent, add a possibly truncated value 1, value 2 and value 3. The lengths of indent, value 2 and value 3 will be subtracted from screen width with the difference the space available for value 1 which will either be truncated or left fill justified accordingly.
        """
        keys = tkeys.split(self.split_char)
        for j in range(len(keys)):
            key = keys[j]
            keys_left = keys[j+1:]
            if not keys_left:
                try:
                    self.setdefault(key, []).append(values)
                except Exception as e:
                    logger.warning(f"error adding key: {key}, values: {values}\n self: {self}; e: {repr(e)}")
            if isinstance(self[key], dict):
                self = self[key]
            elif keys_left:
                self.setdefault("/".join(keys[j:]), []).append(values)
                break

    def as_tree(self, t={}, depth = 0, level=0):
        """ return an indented tree """
        for k in t.keys():
            indent = NDict.tab * depth * " "
            self.output.append(f"{indent}{k}")
            self.row += 1
            depth += 1
            if level and depth > level:
                depth -= 1
                continue

            if type(t[k]) == NDict:
                self.as_tree(t[k], depth, level)
            else:
                # we have a list of leaves
                for leaf in t[k]:
                    indent = NDict.tab * depth * " "
                    l_indent = len(indent)
                    # width - indent - 2 (type and space) - flags - 1 (space) - rhc
                    summary_width = self.width - l_indent - 2 - self.flag_len - 2 - len(leaf[3])
                    if settings['connecting_dots'] and (leaf[2].strip() or leaf[3].strip()):
                        times = leaf[3].rstrip() if leaf[3].strip() else ''
                        details = f" {leaf[2]} {times}".replace('   ', LINEDOT)
                        fill = summary_width - len(leaf[1])
                        if fill < 0:
                            summary = leaf[1][:summary_width - 1] + ELLIPSiS_CHAR
                        elif fill >= 3:
                            pad = ' '*(fill%3) if fill%3 else ''
                            summary = f"{leaf[1][:summary_width - 1]}{pad}{LINEDOT*(fill//3)}"
                        else:
                            summary = leaf[1][:summary_width - 1].ljust(summary_width, ' ')
                        tmp = f"{indent}{leaf[0]} {summary}{details}"
                    else:
                        summary = leaf[1][:summary_width - 1] + ELLIPSiS_CHAR if len(leaf[1]) > summary_width else leaf[1].ljust(summary_width-1, ' ')
                        tmp = f"{indent}{leaf[0]} {summary} {leaf[2]} {leaf[3]}"

                    self.output.append(tmp)
                    self.row2id[self.row] = leaf[4]
                    self.row += 1
                    if len(leaf) > 5:
                        lines = self.leaf_detail(leaf[5], depth)
                        for line in lines:
                            self.output.append(line)
                            self.row += 1
            depth -= 1
        return "\n".join(self.output), self.row2id


class DataView(object):

    def __init__(self, etmdir):
        self.active_item = None
        self.active_view = 'agenda'
        self.prior_view = 'agenda'
        self.current = []
        self.alerts = []
        self.row2id = []
        self.id2relevant = {}
        self.link_list = []
        self.pinned_list = []
        self.current_row = 0
        self.agenda_view = ""
        self.done_view = ""
        self.busy_view = ""
        self.calendar_view = ""
        self.query_view = ""
        self.query_text = ""
        self.query_items = []
        self.query_mode = "items table"
        self.report_view = ""
        self.report_text = ""
        self.report_items = []
        self.cal_locale = None
        self.history_view = ""
        self.cache = {}
        self.itemcache = {}
        self.used_summary = {}
        self.used_details = {}
        self.used_details2id = {}
        self.currMonth()
        self.completions = []
        self.konnections_from = {}
        self.konnections_to = {}
        self.konnected = []
        if os.path.exists(timers_file):
            with open(timers_file, 'rb') as fn:
                self.timers = pickle.load(fn)
            self.active_timer = None
            for x in self.timers:
                if self.timers[x][0] == 'p':
                    self.active_timer = x
                    break
        else:
            self.timers = {}
            self.active_timer = None
        self.saved_timers = deepcopy(self.timers)
        self.archive_after = 0
        self.set_etmdir(etmdir)
        self.views = {
                'a': 'agenda',
                'b': 'busy',
                'c': 'completed',
                'd': 'do next',
                'f': 'forthcoming',
                'h': 'history',
                'i': 'index',
                'k': 'konnected',
                'l': 'location',
                'm': 'timers',
                'p': 'pinned',
                'q': 'query',
                'j': 'journal',
                't': 'tags',
                'u': 'used time',
                'r': 'review',
                'U': 'used summary',
                'y': 'yearly',
                }

        self.completion_keys = ['c', 'g', 'i', 'k', 'l', 'n', 't']
        self.edit_item = None
        self.is_showing_details = False
        self.is_showing_query = False
        self.is_showing_help = False
        self.is_editing = False
        self.is_showing_items = True
        self.get_completions()
        self.refresh_konnections()
        self.refreshRelevant()
        self.activeYrWk = self.currentYrWk
        self.calAdv = pendulum.today().month // 7

        self.refreshAgenda()
        self.refreshCurrent()
        self.currcal()

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
        if 'keep_next' in self.settings and self.settings['keep_next']:
            self.nextfile = os.path.normpath(os.path.join(etmdir, 'next.txt'))
        else:
            self.nextfile = None

        if 'locale' in self.settings:
            locale_str = settings['locale']
            # locale_str should have the format "en_US"
            if locale_str:
                try:
                    locale.setlocale(locale.LC_ALL, f"{locale_str}.UTF-8")
                    self.cal_locale = [locale_str, "UTF-8"]
                except:
                    logger.error(f"could not set python locale to {locale_str}.UTF-8")
                else:
                    logger.info(f"Using python locale: '{locale_str}.UTF-8'")

                tmp = locale_str[:2]
                try:
                    # pendulum needs 2 char abbreviations
                    pendulum.set_locale(tmp)
                except:
                    logger.error(f"could not set locale for pendulum to {tmp}")
                else:
                    logger.info(f"Using pendulum locale: '{tmp}'")

        if 'archive_after' in self.settings:
            try:
                self.archive_after = int(self.settings['archive_after'])
            except Exception as e:
                logger.error(f"An integer is required for archive_after - got {self.settings['archive_after']}. {e}")

        self.db = DBITEM
        self.dbarch = DBARCH
        logger.info(f"items: {len(DBITEM)}; archive: {len(DBARCH)}")
        self.possible_archive()
        self.update_links()

    def use_archive(self):
        self.query_mode = "archive table"
        self.db = DBARCH

    def use_items(self):
        self.query_mode = "items table"
        self.db = DBITEM

    def get_completions(self):
        """
        Get completions from db items
        """
        completions = set([])
        self.completions = list(completions)

        for item in self.db:
            found = {x: v for x, v in item.items() if x in self.completion_keys}

            for x, v in found.items():
                if isinstance(v, list):
                    if x == "k":
                        continue
                    for p in v:
                        completions.add(f"@{x} {p}")
                else:
                    completions.add(f"@{x} {v}")
                    if x == "i":
                        # make a "k" completion for the "i" entry
                        i, t, s, d = (
                            item["i"],
                            item["itemtype"],
                            item["summary"],
                            item.doc_id,
                        )
                        completions.add(f"@k {i} {t} {s}: {d}")
        self.completions = list(completions)
        self.completions.sort()


    def update_konnections(self, item):
        """
        Only change relevant hashes
        """
        # the original @k entries
        orig = self.konnections_from.get(item.doc_id, []) if item.doc_id else []

        # the new and valid @k entries
        # links = [x for x in item.item_hsh.get('k', []) if self.db.contains(doc_id = x)]
        links = item.item_hsh.get('k', [])

        # remove duplicates
        links = list(set(links))

        # upate konnections_from to the new, valid,
        # and non-duplicate @k's
        if links:
            self.konnections_from[item.doc_id] = links
        elif item.doc_id in self.konnections_from:
            del self.konnections_from[item.doc_id]

        # these @k's were added
        added = [x for x in links if x not in orig]
        # these @k's were removed
        removed = [x for x in orig if x not in links]

        for link in links:
            if link in added:
                self.konnections_to.setdefault(link, []).append(item.doc_id)
            elif link in removed:
                self.konnections_to[link].remove(item.doc_id)

        # now update konnected to reflect the changes
        konnected = [x for x in self.konnections_to] + [x for x in self.konnections_from]
        self.konnected = list(set(konnected))



    def refresh_konnections(self):
        """
        to_hsh: ID -> ids of items with @k ID
        from_hsh ID -> ids in @k
        """
        self.konnections_to = {}
        self.konnections_from = {}
        self.konnected = []
        for item in self.db:
            # from item to link by @k entry
            links = [x for x in item.get('k', []) if self.db.contains(doc_id=x)]
            if links:
                self.konnections_from[item.doc_id] = links
                # append the to links
                for link in links:
                    self.konnections_to.setdefault(link, []).append(item.doc_id)

        konnected = [x for x in self.konnections_to] + [x for x in self.konnections_from]
        self.konnected = list(set(konnected))

    # def refresh_konnected(self):
    #     konnected = [x for x in self.konnections_to] + [x for x in self.konnections_from]
    #     self.konnected = list(set(konnected))

    def handle_backups(self):
        removefiles = []
        timestamp = pendulum.now('UTC').format("YYYY-MM-DD")
        filelist = os.listdir(self.backupdir)
        # deal with db.json
        dbmtime = os.path.getctime(self.dbfile)
        zipfiles = [x for x in filelist if x.startswith('db')]
        zipfiles.sort(reverse=True)
        if zipfiles:
            lastdbtime = os.path.getctime(os.path.join(self.backupdir, zipfiles[0]))
        else:
            lastdbtime = None

        if lastdbtime is None or dbmtime > lastdbtime:
            backupfile = os.path.join(self.backupdir, f"db-{timestamp}.json")
            zipfile = os.path.join(self.backupdir, f"db-{timestamp}.zip")
            shutil.copy2(self.dbfile, backupfile)
            with ZipFile(zipfile, 'w', compression=ZIP_DEFLATED, compresslevel=6) as zip:
                zip.write(backupfile, os.path.basename(backupfile))
            os.remove(backupfile)
            logger.info(f"backed up {self.dbfile} to {zipfile}")
            zipfiles.insert(0, f"db-{timestamp}.zip")
            zipfiles.sort(reverse=True)
            removefiles.extend([os.path.join(self.backupdir, x) for x in zipfiles[7:]])
        else:
            logger.info(f"{self.dbfile} unchanged - skipping backup")

        # deal with cfg.yaml
        cfgmtime = os.path.getctime(self.cfgfile)
        cfgfiles = [x for x in filelist if x.startswith('cfg')]
        cfgfiles.sort(reverse=True)
        if cfgfiles:
            lastcfgtime = os.path.getctime(os.path.join(self.backupdir, cfgfiles[0]))
        else:
            lastcfgtime = None
        if lastcfgtime is None or cfgmtime > lastcfgtime:
            backupfile = os.path.join(self.backupdir, f"cfg-{timestamp}.yaml")
            shutil.copy2(self.cfgfile, backupfile)
            logger.info(f"backed up {self.cfgfile} to {backupfile}")
            cfgfiles.insert(0, f"cfg-{timestamp}.yaml")
            cfgfiles.sort(reverse=True)
            removefiles.extend([os.path.join(self.backupdir, x) for x in
                cfgfiles[7:]])
        else:
            logger.info(f"{self.cfgfile} unchanged - skipping backup")

        # maybe delete older backups
        if removefiles:
            logger.info(f"removing old files: {removefiles}")
            for f in removefiles:
                os.remove(f)
        return True

    def save_timers(self):
        timers = deepcopy(self.timers)
        if self.active_timer and self.active_timer in timers:
            state, start, period = timers[self.active_timer]
            if state == 'r':
                now = pendulum.now('local')
                period += now - start
                state = 'p'
                timers[self.active_timer] = [state, now, period]
        if timers:
            if timers != self.saved_timers:
                logger.debug(f"timers changed - dumping to {timers_file}")
                with open(timers_file, 'wb') as fn:
                    pickle.dump(timers, fn)
                self.saved_timers = timers
            else:
                logger.debug(f"timers unchanged - skipping dump to {timers_file}")
        elif os.path.exists(timers_file):
            logger.debug(f"removing {timers_file}")
            os.remove(timers_file)
        # this return is necessary to avoid blocking event_handler
        return


    # bound to tt
    def toggle_active_timer(self, row=None):
        if not self.active_timer:
            return
        now = pendulum.now('local')
        state, start, period = self.timers[self.active_timer]
        if state == 'r':
            period += now - start
            state = 'p'
        else:
            state = 'r'
        self.timers[self.active_timer] = [state, now, period]
        self.save_timers()


    # bound to T
    def next_timer_state(self, doc_id=None):
        """
        states for this reminder's timer
            n: does not exist
            i: inactive
            r: running
            p: paused
        other timers:
            -: none active
            +: one is active

        transitions:
            n- -> r-
            n+ -> i+
            i- -> r-
            i+ -> r-
            r- -> p-
            p- -> r-
        """
        if not doc_id:
            return
        other_timers = deepcopy(self.timers)
        if doc_id in other_timers:
            del other_timers[doc_id]
        active = [x for x, v in other_timers.items() if v[0] in ['r', 'p']]
        if len(active) > 1:
            logger.warning(f"more than one active timer: {active}")
        now = pendulum.now('local')
        if doc_id in self.timers:
            # there is already a timer for this item
            if active:
                # another timer is active - update time if needed and make inactive
                for x in active:
                    active_state, active_start, active_period = self.timers[x]
                    active_period = active_period + now - active_start if active_state == 'r' else active_period
                    self.timers[x] = ['i', now, active_period]
            state, start, period = self.timers[doc_id]
            if state == 'i':
                # the timer for this item is inactive
                # start the timer for this item
                state = 'r'
            else:
                # the timer for this item is active
                # update the period if running
                period = period + now - start if state == 'r' else period
                # toggle the state
                state = 'p' if state == 'r' else 'r'
            self.active_timer = doc_id
            self.timers[doc_id] = state, now, period
        elif doc_id:
            # there is no timer for this item
            # create the timer
            if active:
                state = 'i'
            else:
                # no other timer is active so start this timer
                state = 'r'
                self.active_timer = doc_id
            self.timers[doc_id] = [state, now, ZERO]

        logger.debug(f"next timer state for doc_id {doc_id}: {self.timers[doc_id]}")
        self.save_timers()
        return True, doc_id, active


    # for status bar report
    def timer_report(self):
        if not self.timers:
            return ''
        active = unrecorded = ""
        zero = pendulum.Duration()
        delta = zero
        if self.active_timer:
            status, started, elapsed = self.timers[self.active_timer]
            delta = pendulum.now('local') - started
            if status == 'r': # running
                delta += elapsed
            active = f"{status}:{format_duration(delta, short=True)}"
        if len(self.timers) > 1:
            timers = deepcopy(self.timers)
            if self.active_timer in timers:
                del timers[self.active_timer]
            relevant = [round_minutes(v[2]) for k, v in timers.items() if v[2] > zero]
            if relevant:
                total = zero
                for v in relevant:
                    total += v
                unrecorded = f" + i:{format_duration(total, short=True)}"
        return f"{active}{unrecorded}  "


    def unsaved_timers(self):
        return len(self.timers)


    def timer_clear(self, doc_id=None):
        if not doc_id:
            return
        if doc_id == self.active_timer:
            self.active_timer = None
        if doc_id in self.timers:
            del self.timers[doc_id]
        self.save_timers()
        self.show_active_view()


    def set_now(self):
        self.now = pendulum.now('local')

    def set_active_item(self, id):
        self.active_item = id

    def set_active_view(self, c):
        self.current_row = None
        self.prior_view = self.active_view
        self.active_view = self.views.get(c, 'agenda')
        if self.active_view != 'query':
            self.use_items()


    def show_active_view(self):
        if self.active_view != 'query':
            self.hide_query()
        if self.active_view == 'agenda':
            self.refreshAgenda()
            return self.agenda_view
        if self.active_view == 'completed':
            self.refreshAgenda()
            self.row2id = self.done2id
            return self.done_view
        if self.active_view == 'busy':
            self.refreshAgenda()
            return self.busy_view
        if self.active_view == 'yearly':
            # self.refreshCalendar()
            return self.calendar_view
        if self.active_view == 'history':
            self.history_view, self.row2id = show_history(self.db, True, self.pinned_list, self.link_list, self.konnected, self.timers)
            return self.history_view
        if self.active_view == 'timers':
            self.timers_view, self.row2id = show_timers(self.db, self.pinned_list, self.link_list, self.konnected, self.timers, self.active_timer)
            return self.timers_view
        if self.active_view == 'forthcoming':
            self.forthcoming_view, self.row2id = show_forthcoming(self.db, self.id2relevant, self.pinned_list, self.link_list, self.konnected, self.timers)
            return self.forthcoming_view
        if self.active_view == 'do next':
            self.next_view, self.row2id = show_next(self.db, self.pinned_list, self.link_list, self.konnected, self.timers)
            return self.next_view
        if self.active_view == 'journal':
            self.journal_view, self.row2id = show_journal(self.db, self.id2relevant, self.pinned_list, self.link_list, self.konnected, self.timers)
            return self.journal_view
        if self.active_view == 'tags':
            self.tag_view, self.row2id = show_tags(self.db, self.id2relevant, self.pinned_list, self.link_list, self.konnected, self.timers)
            return self.tag_view
        if self.active_view == 'index':
            self.index_view, self.row2id = show_index(self.db, self.id2relevant, self.pinned_list, self.link_list, self.konnected, self.timers)
            return self.index_view
        if self.active_view == 'location':
            self.index_view, self.row2id = show_location(self.db, self.id2relevant, self.pinned_list, self.link_list, self.konnected, self.timers)
            return self.index_view
        if self.active_view == 'pinned':
            self.pinned_view, self.row2id = show_pinned(self.get_pinned(), self.pinned_list, self.link_list, self.konnected, self.timers)
            return self.pinned_view
        if self.active_view == 'used time':
            used_details = self.used_details.get(self.active_month)
            if not used_details:
                month_format = pendulum.from_format(self.active_month + "-01", "YYYY-MM-DD").format("MMMM YYYY")
                return f"Nothing recorded for {month_format}"
            self.used_view = used_details
            self.row2id = self.used_details2id.get(self.active_month)
            return self.used_view
        if self.active_view == 'used summary':
            self.row2id = {}
            used_summary = self.used_summary.get(self.active_month)
            if not used_summary:
                month_format = pendulum.from_format(self.active_month + "-01", "YYYY-MM-DD").format("MMMM YYYY")
                return f"Nothing recorded for {month_format}"
            self.used_summary_view = used_summary
            return self.used_summary_view
        if self.active_view == 'review':
            self.review_view, self.row2id = show_review(self.db, self.pinned_list, self.link_list, self.konnected, self.timers)
            return self.review_view
        if self.active_view == 'konnected':
            self.konnected_view, self.row2id = show_konnected(self.db, self.pinned_list, self.link_list, self.konnected, self.timers, self.active_item, self.konnections_from, self.konnections_to)
            return self.konnected_view
        if self.active_view == 'query':
            if self.query_text:
                if len(self.query_text) > 1 and self.query_text[1] == ' ' and self.query_text[0] in ['s', 'u', 'm', 'c']:
                    # complex query
                    self.query_view, self.row2id = show_query_results(self.query_text, self.query_grpby, self.query_items)
                else:
                    # standard query
                    self.query_view, self.row2id = show_query_items(self.query_text, self.query_items, self.pinned_list, self.link_list, self.konnected, self.timers)
            else:
                self.query_view = ""
                self.row2id = {}

            return self.query_view

    def set_query(self, text, grpby, items):
        self.query_text = text
        self.query_items = items
        self.query_grpby = grpby

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


    def currMonth(self):
        self.active_month = pendulum.today().format("YYYY-MM")


    def prevMonth(self):
        dt = pendulum.from_format(self.active_month + "-01", "YYYY-MM-DD", 'local') - DAY
        self.active_month = dt.format("YYYY-MM")


    def nextMonth(self):
        dt = pendulum.from_format(self.active_month + "-01", "YYYY-MM-DD", 'local') + 31 * DAY
        self.active_month = dt.format("YYYY-MM")


    def refreshRelevant(self):
        """
        Called to set the relevant items for the current date and to change the currentYrWk and activeYrWk to that containing the current date.
        """
        logger.debug(f"in refreshRelevant")
        self.set_now()
        self.currentYrWk = getWeekNum(self.now)
        dirty = True
        while dirty:
            self.current, self.alerts, self.id2relevant, dirty = relevant(self.db, self.now, self.pinned_list, self.link_list, self.konnected, self.timers)
            if dirty:
                self.refresh_konnections()

        self.refreshCache()


    def refreshAgenda(self):
        if self.activeYrWk not in self.cache:
            self.cache.update(schedule(self.db, yw=self.activeYrWk, current=self.current, now=self.now, pinned_list=self.pinned_list, link_list=self.link_list, konnect_list=self.konnected, timers=self.timers))
        # agenda, done, busy, row2id, done2id
        self.agenda_view, self.done_view, self.busy_view, self.row2id, self.done2id = self.cache[self.activeYrWk]


    def refreshCurrent(self):
        """
        Agenda for the current and following 2 weeks
        """
        if self.currfile is not None:
            weeks = []
            this_week = getWeekNum(self.now)
            for _ in range(self.settings['keep_current']):
                weeks.append(this_week)
                this_week = nextWeek(this_week)
            current = []
            for week in weeks:
                if week not in self.cache:
                    self.cache.update(schedule(self.db, yw=week, current=self.current, now=self.now, pinned_list=self.pinned_list, link_list= self.link_list))
                agenda, done, busy, num2id, row2id = self.cache[week]
                current.append(agenda)
            with open(self.currfile, 'w', encoding='utf-8') as fo:
                fo.write("\n\n".join([re.sub(' {5,}', ' ', x.strip()) for x in current]))
                # fo.write("\n\n".join([x.lstrip() for x in current]))
            logger.info(f"saved current schedule to {self.currfile}")

        if self.nextfile is not None:
            next_view, row2id = show_next(self.db, self.pinned_list, self.link_list, self.konnected, self.timers)
            with open(self.nextfile, 'w', encoding='utf-8') as fo:
                fo.write(re.sub(' {3,}', ' ', next_view))
                # fo.write(next_view)
            logger.info(f"saved do next to {self.nextfile}")


    def show_query(self):
        self.is_showing_query = True

    def hide_query(self):
        self.is_showing_query = False

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


    def get_arch_id(self, row=None, edit=False):
        res = self.get_row_details(row)
        if not (res and res[0]):
            return None, ''
        item_id = res[0]
        item = self.db.get(doc_id=item_id)
        if 'doc_id' in item:
            return item['doc_id']


    def get_details(self, row=None, edit=False):
        res = self.get_row_details(row)
        if not (res and res[0]):
            return None, ''
        item_id = res[0]

        if not edit and item_id in self.itemcache:
            return item_id, self.itemcache[item_id]
        item = self.db.get(doc_id=item_id)
        if item:
            item_hsh = item_details(item, edit)
            return item_id, item_hsh
        return None, ''


    def toggle_pinned(self, row=None):
        res = self.get_row_details(row)
        if not (res and res[0]):
            return None, ''
        item_id = res[0]
        if item_id in self.pinned_list:
            self.pinned_list.remove(item_id)
            act = 'unpinned'
        else:
            self.pinned_list.append(item_id)
            act = 'pinned'
        return f"{act} {item_id}"


    def get_pinned(self):

        return [self.db.get(doc_id=x) for x in self.pinned_list if x]


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

    def touch(self, row):
        res = self.get_row_details(row)
        if not res:
            return False
        doc_id, instance, job_id = res
        now = pendulum.now('local')
        item_hsh = self.db.get(doc_id=doc_id)
        item_hsh['modified'] = pendulum.now('local')
        self.db.update(db_replace(item_hsh), doc_ids=[doc_id])
        return True


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
        if 'j' in item and not job_id:
            return False, 'no job_id but task has jobs', None, None, None

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
        self.cache = schedule(ETMDB, self.currentYrWk, self.current, self.now, 5, 20, self.pinned_list, self.link_list, self.konnected, self.timers)
        self.used_details, self.used_details2id, self.used_summary = get_usedtime(self.db, self.pinned_list, self.link_list, self.konnected, self.timers)

    def update_links(self):
        """
        Look for items with @g entries and add their ids
        to link_list.
        """
        for item in self.db:
            if 'g' in item:
                if item.doc_id not in self.link_list:
                    self.link_list.append(item.doc_id)
            else:
                if item.doc_id in self.link_list:
                    self.link_list.remove(item_id)


    def possible_archive(self):
        """
        Collect old finished tasks, (repeating or not), old non-repeating events,
        and repeating events with old @u entries. Do not collect journal.
        """
        if not self.archive_after:
            logger.info(f"archive_after: {self.archive_after} - skipping archive")
            return
        old = pendulum.now() - pendulum.duration(years=self.archive_after)
        rows = []
        for item in self.db:
            if item['itemtype'] == '%':
                # keep journal
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
                    if 'u' not in rr:
                        toss = False
                        break
                    elif isinstance(rr['u'], pendulum.Date):
                        # could be date or datetime
                        if isinstance(rr['u'], pendulum.DateTime):
                            # datetime
                            if rr['u'].date() >= old.date():
                                toss = False
                                break
                        else:
                            # date
                            if rr['u'] >= old.date():
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
                start = item.get('s', None)
                if isinstance(start, pendulum.DateTime):
                    if start < old:
                        # toss old, non-repeating events
                        rows.append(item)
                        continue
                elif isinstance(start, pendulum.Date):
                    if start < old.date():
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
            add_items.append(item)

        try:
            self.dbarch.insert_multiple(add_items)
        except:
            logger.error(f"archive failed for doc_ids: {rem_ids}")
        else:
            self.db.remove(doc_ids=rem_ids)

        return rows

    def move_item(self, row=None):
        res = self.get_row_details(row)
        if not (res and res[0]):
            return False
        item_id = res[0]
        item = self.db.get(doc_id=item_id)
        try:
            if self.query_mode == "items table":
                # move to archive
                DBARCH.insert(item)
                DBITEM.remove(doc_ids=[item_id])
            else:
                # back to items
                DBITEM.insert(item)
                DBARCH.remove(doc_ids=[item_id])
        except Exception as e:
            logger.error(f"move from {self.query_mode} failed for item_id: {item_id}; exception: {e}")
            return False
        return True

    def send_mail(self, doc_id):
        item = DBITEM.get(doc_id=doc_id)
        attendees = item.get('n', None)
        if not attendees:
            logger.error(f"@n (attendees) are not specified in {item}. send_mail aborted.")
            return
        # attendees can have the form "abbrev: emailaddress". Split on the colon and keep the emailaddress.
        addresses = [x.split(':')[-1].strip() for x in attendees]
        email_addresses = [x for x in addresses if not PHONE_REGEX.match(x)]
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
        from email.mime.text import MIMEText
        from email.utils import COMMASPACE, formatdate
        assert type(email_addresses) == list
        msg = MIMEMultipart()
        msg['From'] = smtp_from
        msg['To'] = COMMASPACE.join(email_addresses)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = item['summary']
        msg.attach(MIMEText(message))
        smtp = smtplib.SMTP_SSL(smtp_server)
        smtp.login(smtp_id, smtp_pw)
        smtp.sendmail(smtp_from, attendees, msg.as_string())
        smtp.close()


    def send_text(self, doc_id):
        item = DBITEM.get(doc_id=doc_id)
        attendees = item.get('n', None)
        if not attendees:
            logger.error(f"@n (attendees) are not specified in {item}. send_text aborted.")
            return
        addresses = [x.split(':')[-1].strip() for x in attendees]
        phone_numbers = [x for x in addresses if PHONE_REGEX.match(x)]

        from email.utils import COMMASPACE


        sms = self.settings['sms']
        sms_from = sms.get('from', None)
        # sms_phone = sms.get('phone', None)
        sms_phone = COMMASPACE.join(phone_numbers)
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
        msg = MIMEText(message)
        msg["From"] = sms_from
        msg["Subject"] = summary
        msg['To'] = sms_phone
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
        y = today.year
        try:

            c = calendar.LocaleTextCalendar(0, self.cal_locale)
        except:
            logger.warning(f"error using locale {self.cal_locale}")
            c = calendar.LocaleTextCalendar(0)
        cal = []
        m = 1
        m += 6 * self.calAdv
        y += m // 12
        m %= 12
        for i in range(6): # months in the half year
            cal.append(c.formatmonth(y, m+i, w=2).split('\n'))
        ret = ['']
        for r in range(0, 6, 2):  # 6 months in columns of 2 months
            l = max(len(cal[r]), len(cal[r + 1]))
            for i in range(2):
                if len(cal[r + i]) < l:
                    for _ in range(len(cal[r + i]), l + 1):
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
        self.calAdv = pendulum.today().month // 7
        self.refreshCalendar()

def nowrap(txt, indent=3, width=shutil.get_terminal_size()[0]-3):
    return txt

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
    para = [x.rstrip() for x in txt.split('\n')]
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


def set_summary(summary='', start=None, relevant=None, freq=''):
    """

    """
    if not ('{XXX}' in summary and
            isinstance(start, pendulum.Date) and
            isinstance(relevant, pendulum.Date) and
            freq in ['y', 'm', 'w', 'd']):
        # return unchanged summary
        return summary
    relevant_date = relevant.date() if isinstance(relevant, pendulum.DateTime) else relevant
    start_date = start.date() if isinstance(start, pendulum.DateTime) else start
    diff = relevant_date - start_date
    replacement = 0
    if freq == 'y':
        replacement = diff.in_years()
    elif freq == 'm':
        replacement = diff.in_months()
    elif freq == 'w':
        replacement = diff.in_weeks()
    elif freq == 'd':
        replacement = diff.in_days()
    replacement = ordinal(replacement) if replacement >= 0 else '???'
    return summary.format(XXX=replacement)

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


# def anniversary_string(startyear, endyear):
#     """
#     Compute the integer difference between startyear and endyear and
#     append the appropriate English suffix.
#     """
#     return ordinal(int(endyear) - int(startyear))


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

def do_paragraph(arg):
    """
    Remove trailing whitespace.
    """
    obj = None
    rep = arg
    para = [x.rstrip() for x in arg.split('\n')]
    if para:
        all_ok = True
        obj_lst = []
        rep_lst = []
        for p in para:
            try:
                res = str(p)
                obj_lst.append(res)
                rep_lst.append(res)
            except:
                all_ok = False
                rep_lst.append(f"~{arg}~")
        obj = "\n".join(obj_lst) if all_ok else None
        rep = "\n".join(rep_lst)
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
{{ nowrap(title) }} \
{% if 'f' in h %}\
{{ "@f {} ".format(dt2str(h['f'])[1]) }} \
{% endif -%}\
{% if 'a' in h %}\
{%- set alerts %}\
{% for x in h['a'] %}{{ "@a {}: {} ".format(inlst2str(x[0]), ", ".join(x[1])) }}{% endfor %}\
{% endset %}\
{{ nowrap(alerts) }} \
{% endif %}\
{% if 'u' in h %}\
{%- set used %}\
{% for x in h['u'] %}{{ "@u {}: {} ".format(in2str(x[0]), dt2str(x[1])[1]) }}{% endfor %}\
{% endset %}
{{ nowrap(used) }} \
{% endif %}\
{%- set is = namespace(found=false) -%}\
{%- set index -%}\
{%- for k in ['c', 'i'] -%}\
{%- if k in h %}@{{ k }} {{ h[k] }}{% set is.found = true %} {% endif %}\
{%- endfor %}\
{%- endset %}\
{% if is.found %}
{{ nowrap(index) }} \
{% endif %}\
{%- if 't' in h %}
{% for x in h['t'] %}{{ "@t {} ".format(x) }}{% endfor %}\
{% endif %}\
{%- if 'k' in h %}
{% for x in h['k'] %}{{ "@k {} ".format(x) }}{% endfor %}\
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
{{ nowrap(location) }} \
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
@r {{ nowrap(rrule) }} \
{% endif -%}\
{%- endfor %}\
{% if 'o' in h %}\
@o {{ h['o'] }}{% endif %} \
{% endif %}\
{% for k in ['+', '-', 'h'] %}\
{% if k in h and h[k] %}
@{{ k }} {{ nowrap(dtlst2str(h[k])) }} \
{%- endif %}\
{%- endfor %}\
{% if 'd' in h %}
@d {{ nowrap(h['d'], 0) }} \
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
{%- set used %}\
{% for u in x['u'] %}{{ "&u {}: {} ".format(in2str(u[0]), dt2str(u[1])[1]) }}{% endfor %}\
{% endset %}
{{ nowrap(used) }} \
{% endif %}\
{% if 'f' in x %}{{ " &f {}".format(dt2str(x['f'])[1]) }}{% endif %}\
{%- endset %}
@j {{ nowrap(job) }} \
{%- endfor %}\
{%- endif %}
"""

# This duplication seems silly but seemed necessary to use nowrap in entry and wrap in display

display_tmpl = """\
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
{%- if 'k' in h %}
{% for x in h['k'] %}{{ "@k {} ".format(x) }}{% endfor %}\
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
{%- set used %}\
{% for u in x['u'] %}{{ "&u {}: {} ".format(in2str(u[0]), dt2str(u[1])[1]) }}{% endfor %}\
{% endset %}\
{{ wrap(used) }} \
{% endif %}\
{% if 'f' in x %}{{ " &f {}".format(dt2str(x['f'])[1]) }}{% endif %}\
{%- endset %}
@j {{ wrap(job) }} \
{%- endfor %}\
{%- endif %}

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
jinja_entry_template.globals['dtlst2str'] = plain_datetime_list
jinja_entry_template.globals['inlst2str'] = format_duration_list
jinja_entry_template.globals['one_or_more'] = one_or_more
jinja_entry_template.globals['isinstance'] = isinstance
jinja_entry_template.globals['nowrap'] = nowrap

jinja_display_template = Template(display_tmpl)
jinja_display_template.globals['dt2str'] = plain_datetime
jinja_display_template.globals['in2str'] = format_duration
jinja_display_template.globals['dtlst2str'] = format_datetime_list
jinja_display_template.globals['inlst2str'] = format_duration_list
jinja_display_template.globals['one_or_more'] = one_or_more
jinja_display_template.globals['isinstance'] = isinstance
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

def do_konnection(arg):
    konnection_str = "an integer document id"
    m = KONNECT_REGEX.match(arg)
    if m:
        arg = m[1]

    if not arg:
        return None, konnection_str
    ok, res = integer(arg, 1, None, False)
    if ok:
        obj = res
        rep = arg
    else:
        obj = None
        rep = f"'{arg}' is incomple or invalid. Konnection requires {konnection_str}."
    return obj, rep


def do_usedtime(arg):
    """
    >>> do_usedtime('75m: 9p 2019-02-01')
    ([Duration(hours=1, minutes=15), DateTime(2019, 2, 1, 21, 0, 0, tzinfo=Timezone('America/New_York'))], '1h15m: 2019-02-01 9:00pm')
    >>> do_usedtime('75m: 2019-02-01 9:00AM')
    ([Duration(hours=1, minutes=15), DateTime(2019, 2, 1, 9, 0, 0, tzinfo=Timezone('America/New_York'))], '1h15m: 2019-02-01 9:00am')
    """
    if not arg:
        return None, ''
    got_period = got_datetime = False
    rep_period = 'period'
    rep_datetime = 'datetime'
    parts = arg.split(': ')
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
    command = parts[0] if parts and parts[0] else None
    commands = [x.strip() for x in command.split(',')] if command else []
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
    ovrstr = "overdue: character from (r)estart, (s)kip, (k)eep or (p)reserve"

    if arg:
        ok = arg in ('k', 'r', 's', 'p')
        if ok:
            return arg, f"overdue: {arg}"
        else:
            return None, f"invalid overdue: '{arg}'. {ovrstr}"
    else:
        return None, ovrstr


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
        return None, wrap(f"repetition frequency: character from {freqstr} Append an '&' to add an option.", 2)


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
        weeknumbersstr = "weeknumbers: a comma separated list of integer week numbers from 1, 2, ..., 53"

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
    'w5zDnMOSwo7CicOnwo_Cl8Ojw5bDicKFw6XDi8Oow5_CisOUw6LDoA=='
    """
    obj = Mask(arg)
    return obj, arg


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
    'r':  'frequency',
    'i':  'interval',
    's':  'setpositions',
    'c':  'count',
    'u':  'until',
    'M':  'months',
    'm':  'monthdays',
    'W':  'weeknumbers',
    'w':  'weekdays',
    'h':  'hours',
    'n':  'minutes',
    'E':  'easterdays',
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
            r_hsh[k] = tmp[0] if len(tmp) == 1 else tmp
    if 'u' in r_hsh and 'c' in r_hsh:
        logger.warning(f"Warning: using both 'c' and 'u' is depreciated in {r_hsh}")
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
    overdue = item.get('o', 'k') # make 'k' the default for 'o'
    dtstart = item['s']
    if overdue == 'k':
        aft = due
        inc = False
    elif overdue == 'r':
        aft = done
        dtstart = done
        inc = False
    else:  # 's' skip
        today = pendulum.today()
        if due < today:
            aft = today
            inc = True
        else:
            aft = due
            inc = False
    using_dates = False
    if isinstance(dtstart, pendulum.Date) and not isinstance(dtstart, pendulum.DateTime):
        using_dates = True
        dtstart = pendulum.datetime(year=dtstart.year, month=dtstart.month, day=dtstart.day, hour=0, minute=0)
        aft = pendulum.datetime(year=aft.year, month=aft.month, day=aft.day, hour=0, minute=0)
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
    if nxt_rset:
        nxt = pendulum.instance(nxt_rset)
        if using_dates:
            nxt = nxt.date()
    else:
        nxt = None
    return nxt

def date_to_datetime(dt):
    if isinstance(dt, pendulum.Date) and not isinstance(dt, pendulum.DateTime):
        dt= pendulum.datetime(year=dt.year, month=dt.month, day=dt.day, hour=0, minute=0, tz='local')
    return dt


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

    if 's' not in item:
        if 'f' in item:
            return [(item['f'], None)]
        else:
            return []
    instances = []
    dtstart = item['s']
    if not (
        isinstance(dtstart, pendulum.DateTime)
        or isinstance(dtstart, pendulum.Date)
    ):
        return []
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

    # all the dateutil instances will be in UTC so these must be as well
    aft_dt = date_to_datetime(aft_dt).replace(tzinfo='UTC')
    bef_dt = bef_dt if isinstance(bef_dt, int) else date_to_datetime(bef_dt).replace(tzinfo='UTC')

    if 'r' in item:
        lofh = item['r']
        rset = rruleset()

        for hsh in lofh:
            freq, kwd = rrule_args(hsh)
            kwd['dtstart'] = dtstart
            try:
                rset.rrule(rrule(freq, **kwd))
            except Exception as e:
                logger.error(f"exception: {e}")
                return []
        if '-' in item:
            for dt in item['-']:
                rset.exdate(date_to_datetime(dt))

        if '+' in item:
            for dt in item['+']:
                rset.rdate(date_to_datetime(dt))
        if isinstance(bef_dt, int):
            tmp = []
            inc = True
            for _ in range(bef_dt):
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
        tmp = [dtstart, *item['+']]
        tmp = [date_to_datetime(x) for x in tmp]
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
            if pairs and settings['limit_skip_display']:
                # only keep the first instance that falls during or after today/now
                break
            if isinstance(instance, pendulum.Date) and not isinstance(instance, pendulum.DateTime) and instance >= pendulum.now().date():
                pairs.append((instance, None))
                logger.debug(f"appended overdue skip date instance: {instance}")
            # elif instance.replace(hour=23, minute=59, second=59) >= pendulum.now(tz=item.get('z', None)):
            elif instance >= pendulum.now(tz=item.get('z', None)):
                pairs.append((instance, None))
                logger.debug(f"appended overdue skip datetime instance: {instance}")
                logger.debug(f"overdue skip datetime pairs: {pairs}")
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
    job_methods = datetime_job_methods if 's' in at_hsh else undated_job_methods
    msg = []
    # rmd = []
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
            count = 0
            # set auto mode True if i is missing from the first job, otherwise set auto mode
            auto = 'i' not in hsh
        if auto: # auto mode
            if count > 25:
                count = 0
                msg.append(
                    "error: at most 26 jobs are allowed in auto mode")
            if 'i' in hsh:
                msg.append(
                    "error: &i should not be specified in auto mode")
            if 'p' in hsh:
                msg.append(
                    "error: &p should not be specified in auto mode")
            # auto generate simple sequence for i: a, b, c, ... and
            # for p: a requires nothing, b requires a, c requires b, ...
            hsh['i'] = LOWERCASE[count]
            hsh['p'] = [LOWERCASE[count - 1]] if count > 0 else []
            count += 1
            req[hsh['i']] = deepcopy(hsh['p'])

        else:    # manual mode
            if 'i' not in hsh:
                msg.append('error: &i is required for each job in manual mode')
            elif hsh['i'] in req:
                msg.append(f"error: '&i {hsh['i']}' has already been used")
            elif 'p' in hsh:
                    if type(hsh['p']) == str:
                        req[hsh['i']] = [x.strip() for x in hsh['p'].split(',') if x]
                    else:
                        req[hsh['i']] = deepcopy(hsh['p'])
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

    # Recursively compute the transitive closure of req so that j in req[i]
    # iff i requires j either directly or indirectly through some chain of
    # requirements
    again = True
    while again:
        # stop after this loop unless we've added a new requirement
        again = False
        for i in ids:
            for j in ids:
                for k in ids:
                    if j in req[i] and k in req[j] and k not in req[i]:
                        # since i requires j and j requires k, i indirectly
                        # requires k so, if not already included, add k to
                        # req[i]
                        # and loop again
                        req[i].append(k)
                        again = True

    # look for circular dependencies when a job indirectly requires itself
    tmp = []
    for i in ids:
        if i in req[i]:
            tmp.append(i)
    if tmp:
        tmp.sort()
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
        logger.warning(f"{msg}")
        return False, msg, None
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
    for _ in range(5):
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
    for _ in range(1, bef + after + 1):
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
    if not (
        isinstance(beg_dt, pendulum.DateTime)
        and isinstance(end_dt, pendulum.DateTime)
    ):
        return "xxx"

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
    >>> beg_ends(parse('2022-12-29 12am'), parse_duration('1d')[1])
    [(DateTime(2018, 3, 2, 9, 0, 0, tzinfo=Timezone('UTC')), DateTime(2018, 3, 2, 17, 20, 0, tzinfo=Timezone('UTC')))]
    """

    pairs = []
    beg = starting_dt
    ending = starting_dt + extent_duration
    while ending.date() > beg.date():
        end = beg.end_of('day')
        pairs.append((beg, end))
        beg = beg.start_of('day').add(days=1)
    if beg == ending:
        # don't include zero-extent "tails"
        pass
    else:
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


def relevant(db, now=pendulum.now(), pinned_list=[], link_list=[], konnect_list=[], timers={}):
    """
    Collect the relevant datetimes, inbox, pastdues, beginbys and alerts. Note that jobs are only relevant for the relevant instance of a task
    Called by dataview.refreshRelevant
    """
    # These need to be local times since all times from the datastore and rrule will be local times
    dirty = False
    width = shutil.get_terminal_size()[0] - 2
    summary_width = width - 7 - 16

    today = pendulum.today()
    tomorrow = today + DAY
    inbox_fmt = today.format("YYYYMMDD24@@")
    pastdue_fmt = today.format("YYYYMMDD24^^")
    begby_fmt = today.format("YYYYMMDD24~~")

    id2relevant = {}
    inbox = []
    pastdue = []
    beginbys = []
    alerts = []
    current = []

    for item in db:
        instance_interval = []
        possible_beginby = None
        possible_alerts = []
        all_tds = []
        id = item.doc_id
        if 'itemtype' not in item:
            logger.warning(f"no itemtype: {item}")
            item['itemtype'] = '?'
            # continue
        if 'g' in item:
            if id not in link_list:
                link_list.append(id)
        else:
            if id in link_list:
                link_list.remove(id)

        summary = item.get('summary', "~")
        flags = get_flags(id, link_list, konnect_list, pinned_list, timers)
        if item['itemtype'] == '!':
            inbox.append([0, summary, item.doc_id, None, None])
            relevant = today

        elif 'f' in item:
            relevant = item['f']
            if isinstance(relevant, pendulum.Date) and not isinstance(relevant, pendulum.DateTime):
                relevant = pendulum.datetime(year=relevant.year, month=relevant.month, day=relevant.day, hour=0, minute=0, tz='local')

        elif 's' in item:
            dtstart = item['s']
            has_a = 'a' in item
            has_b = 'b' in item
            # for daylight savings time changes
            if isinstance(dtstart, pendulum.Date) and not isinstance(dtstart, pendulum.DateTime):
                dtstart = pendulum.datetime(year=dtstart.year, month=dtstart.month, day=dtstart.day, hour=0, minute=0, tz='local')
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
                            dt = pendulum.datetime(year=dt.year, month=dt.month, day=dt.day, hour=0, minute=0, tz='local')
                        rset.exdate(dt)

                if '+' in item:
                    for dt in item['+']:
                        if type(dt) == pendulum.Date:
                            dt = pendulum.datetime(year=dt.year, month=dt.month, day=dt.day, hour=0, minute=0, tz='local')
                        rset.rdate(dt)

                if item['itemtype'] == '-':
                    if item.get('o', 'k') == 's':
                        relevant = rset.after(today, inc=True)
                        if relevant:
                            if item['s'] != pendulum.instance(relevant):
                                item['s'] = pendulum.instance(relevant)
                                update_db(db, item.doc_id, item)
                    elif item.get('o', 'k') == 'p':
                        # this is the first instance after 12am today
                        relevant = rset.after(today, inc=True)
                        # these are the instances to be preserved
                        using_datetimes = isinstance(item['s'], pendulum.DateTime)
                        # make sure we have a starting datetime for between
                        start = item['s'] if using_datetimes else pendulum.datetime(
                                item['s'].year, item['s'].month, item['s'].day)
                        between = rset.between(start, today - ONEMIN, inc=True)
                        if relevant and not between:
                            # shouldn't happen
                            logger.debug(f"relevant, {relevant}, but not between for {item}")
                        summary = item['summary']

                        if relevant and item['s'].format('YYYYMMDD') < today.format('YYYYMMDD'):
                            # the due date for the repeating version of the item needs to be reset
                            # keep a copy with the original @s for the instances to be preserved
                            orig_id = item.doc_id
                            hsh_copy = deepcopy(item)
                            # remove @r and @o from the copy
                            hsh_copy.pop('r')
                            hsh_copy.pop('o')
                            hsh_copy.setdefault('k', []).append(orig_id)
                            hsh_copy['created'] = pendulum.now()
                            if 'modified' in hsh_copy:
                                hsh_copy.pop('modified')

                            # update @s for the repeating item
                            item['s'] = pendulum.instance(relevant)
                            # update the repeating item in the db
                            update_db(db, orig_id, item)

                        for dt in between:
                            pdt = pendulum.instance(dt)
                            hsh_copy['s'] = pdt

                            if using_datetimes:
                                # hsh_copy['summary'] = f"{summary} ({pdt.format('YY/M/D H:mm')})"
                                hsh_copy['summary'] = f"{summary} ({format_datetime(pdt, short=True)[1]})"
                            else:
                                # hsh_copy['summary'] = f"{summary} ({pdt.format('YY/M/D')})"
                                hsh_copy['summary'] = f"{summary} ({format_datetime(pdt, short=True)[1]})"

                            # set the new id to avoid a conflict
                            new_id = db._get_next_id()
                            logger.debug(f"inserting: {new_id}:  {hsh_copy}")
                            db.insert(Document(hsh_copy, doc_id=new_id))
                            dirty = True

                    else:
                        # for a restart or keep task, relevant is dtstart
                        relevant = dtstart
                else:
                    # get the first instance after today
                    try:
                        relevant = rset.after(today, inc=True)
                    except Exception as e:
                        logger.error(f"error processing {item}; {repr(e)}")
                    if not relevant:
                        relevant = rset.before(today, inc=True)
                    if relevant:
                        relevant = pendulum.instance(relevant)

                # rset
                if instance_interval:
                    instances = rset.between(instance_interval[0], instance_interval[1], inc=True)
                    if possible_beginby:
                        for instance in instances:
                            if today + DAY <= instance <= tomorrow + possible_beginby:
                                id = item.doc_id
                                if 'r' in item:
                                    # use the freq from the first recurrence rule
                                    freq = item['r'][0].get('r', 'y')
                                else:
                                    freq = 'y'
                                # relevant = id2relevant[id]
                                # summary = set_summary(item['summary'], item.get('s', None), relevant, freq)
                                summary = set_summary(summary, item.get('s', None), pendulum.instance(instance).date(), freq)
                                beginbys.append([(instance.date() - today.date()).days, summary, item.doc_id, None, instance])
                    if possible_alerts:
                        for instance in instances:
                            for possible_alert in possible_alerts:
                                if today <= instance - possible_alert[0] <= tomorrow:
                                    alerts.append([instance - possible_alert[0], instance, possible_alert[1], item['summary'], item.doc_id])

            elif '+' in item:
                # no @r but @+ => simple repetition
                tmp = [dtstart]
                tmp.extend(item['+'])
                tmp = [date_to_datetime(x) for x in tmp]
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
                            beginbys.append([(instance.date() - today.date()).days, summary, item.doc_id, None, instance])
                if possible_alerts:
                    for instance in aft + bef:
                        for possible_alert in possible_alerts:
                            if today <= instance - possible_alert[0] <= tomorrow:
                                alerts.append([instance - possible_alert[0], instance, possible_alert[1], item['summary'], item.doc_id])

            else:
                # 's' but not 'r' or '+'
                relevant = dtstart
                if (
                    possible_beginby
                    and today + DAY <= dtstart <= tomorrow + possible_beginby
                ):
                    beginbys.append([(relevant.date() - today.date()).days, summary,  item.doc_id, None, None])
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
                job_summary = job.get('summary', '')
                jobstart = relevant - job.get('s', ZERO)
                if jobstart.date() < today.date():
                    pastdue_jobs = True
                    pastdue.append([(jobstart.date() - today.date()).days, job_summary, item.doc_id, job_id, None])
                if 'b' in job:
                    days = int(job['b']) * DAY
                    if today + DAY <= jobstart <= tomorrow + days:
                        beginbys.append([(jobstart.date() - today.date()).days, job_summary, item.doc_id, job_id, None])
                if 'a' in job:
                    for alert in job['a']:
                        for td in alert[0]:
                            if today <= jobstart - td <= tomorrow:
                                alerts.append([dtstart - td, dtstart, alert[1],  job['summary'], item.doc_id, job_id, None])

        id2relevant[item.doc_id] = relevant

        if item['itemtype'] == '-' and 'f' not in item and not pastdue_jobs and relevant.date() < today.date():
            pastdue.append([(relevant.date() - today.date()).days, summary, item.doc_id, None, None])

    inbox.sort()
    pastdue.sort()
    beginbys.sort()
    alerts.sort()
    week = today.isocalendar()[:2]
    day = (today.format("ddd MMM D"), )
    for item in inbox:
        item_0 = ' '
        rhc = item_0.center(15, ' ')
        id = item[2]
        flags = get_flags(id, link_list, konnect_list, pinned_list, timers)
        current.append({'id': item[2], 'job': None, 'instance': None, 'sort': (inbox_fmt, 1), 'week': week, 'day': day, 'columns': ['!', item[1], flags, rhc, id]})

    for item in pastdue:
        item_0 = str(item[0]) if item[0] in item else ""
        rhc = item_0.center(15, ' ')
        id = item[2]
        flags = get_flags(id, link_list, konnect_list, pinned_list, timers)
        try:
            current.append({'id': item[2], 'job': item[3], 'instance': item[4], 'sort': (pastdue_fmt, 2, item[0]), 'week': week, 'day': day, 'columns': ['<', item[1], flags, rhc, id]})
        except Exception as e:
            logger.warning(f"could not append item: {item}; e: {e}")

    for item in beginbys:
        item_0 = str(item[0]) if item[0] in item else ""
        rhc = item_0.center(15, ' ')
        id = item[2]
        flags = get_flags(id, link_list, konnect_list, pinned_list, timers)
        current.append({'id': item[2], 'job': item[3], 'instance': item[4], 'sort': (begby_fmt, 3, item[0]), 'week': week, 'day': day, 'columns': ['>', item[1], flags, rhc, id]})

    return current, alerts, id2relevant, dirty


def db_replace(new):
    """
    Used with update to replace the original doc with new.
    """
    def transform(doc):
        # update doc to include key/values from new
        doc.update(new)
        # remove any key/values from doc that are not in new
        for k in list(doc.keys()):
            if k not in new:
                del doc[k]
    return transform


def update_db(db, id, hsh={}):
    old = db.get(doc_id=id)
    if not old:
        logger.error(f"Could not get document corresponding to id {id}")
        return
    if old == hsh:
        return
    hsh['modified'] = pendulum.now()
    try:
        db.update(db_replace(hsh), doc_ids=[id])
    except Exception as e:
        logger.error(f"Error updating document corresponding to id {id}\nhsh {hsh}\nexception: {repr(e)}")

def write_back(db, docs):
    for doc in docs:
        try:
            doc_id = doc.doc_id
            update_db(db, doc_id, doc)
        except Exception as e:
            logger.error(f"exception: {e}")


def insert_db(db, hsh={}):
    """
    Assume hsh has been vetted.
    """
    if not hsh:

        return
    hsh['created'] = pendulum.now()
    try:
        db.insert(hsh)
    except Exception as e:
        logger.error(f"Error updating database:\nhsh {hsh}\ne {repr(e)}")


def show_forthcoming(db, id2relevant, pinned_list=[], link_list=[], konnect_list=[], timers={}):
    width = shutil.get_terminal_size()[0] - 2
    summary_width = width - 19
    rows = []
    today = pendulum.today()
    for item in db:
        if item.doc_id not in id2relevant:
            continue

        id = item.doc_id
        if 'r' in item:
            # use the freq from the first recurrence rule
            freq = item['r'][0].get('r', 'y')
        else:
            freq = 'y'
        relevant = id2relevant[item.doc_id]
        if relevant < today:
            continue
        year = relevant.format("YYYY")
        monthday = relevant.format("MMM D")
        time = fmt_time(relevant)
        rhc = f"{monthday} {time}".ljust(14, ' ')

        itemtype = FINISHED_CHAR if 'f' in item else item['itemtype']
        summary = set_summary(item['summary'], item.get('s', None), relevant, freq)
        flags = get_flags(id, link_list, konnect_list, pinned_list, timers)

        rows.append(
                {
                    'id': id,
                    'sort': relevant,
                    'path': year,
                    'values': [
                        itemtype,
                        summary,
                        flags,
                        rhc,
                        id
                        ],
                }
                )

    rows.sort(key=itemgetter('sort'))
    rdict = NDict()
    for row in rows:
        path = row['path']
        values = row['values']
        rdict.add(path, values)
    tree, row2id = rdict.as_tree(rdict, level=0)
    return tree, row2id

def get_flags(id, link_list=[], konnect_list=[], pinned_list=[], timers={}):
    """
    Always length = 3, space or character in each slot
    """
    flags = ""
    if id in link_list:
        flags += LINK_CHAR
    if id in konnect_list:
        flags += KONNECT_CHAR
    if id in pinned_list:
        flags += PIN_CHAR
    if id in timers:
        flags += "t"
    return flags.rjust(4, ' ')

def show_query_items(text, items=[], pinned_list=[], link_list=[], konnect_list=[], timers={}):
    rows = []
    if not items or not isinstance(items, list):
        return f"query: {text}\n   none matching", {}
    item_count = f" [{len(items)}]"
    width = shutil.get_terminal_size()[0] - 2
    summary_width = width - len(item_count) - 7
    for item in items:
        mt = item.get('modified', None)
        if mt is not None:
            dt, label = mt, 'm'
        else:
            dt, label = item.get('created', None), 'c'
        id = item.doc_id
        year = dt.format("YYYY")
        itemtype = FINISHED_CHAR if 'f' in item else item['itemtype']
        summary = item['summary']
        flags = get_flags(id, link_list, konnect_list, pinned_list, timers)
        rhc = f"{id: >6}"
        rows.append(
                {
                    'sort': dt,
                    'path': year,
                    'values': [
                        itemtype,
                        summary,
                        flags,
                        rhc,
                        id],
                }
                )
    rdict = NDict()
    path = f"query: {text[:summary_width]}{item_count}"
    for row in rows:
        values = row['values']
        rdict.add(path, values)
    tree, row2id = rdict.as_tree(rdict, level=0)
    return tree, row2id


def show_history(db, reverse=True, pinned_list=[], link_list=[], konnect_list=[], timers={}):
    width = shutil.get_terminal_size()[0] - 2
    rows = []
    summary_width = width - 25
    for item in db:
        mt = item.get('modified', None)
        if mt is not None:
            dt, label = mt, 'm'
        else:
            dt, label = item.get('created', None), 'c'
        if dt is not None:
            id = item.doc_id
            year = dt.format("YYYY")
            monthday = dt.format("MMM D").ljust(6, ' ')
            c5dt = fivechar_datetime(dt)
            # time = fmt_time(dt).rjust(7, ' ')
            rhc = f" {c5dt} {label}"
            itemtype = FINISHED_CHAR if 'f' in item else item.get('itemtype', '?')
            summary = item.get('summary', "~")
            flags = get_flags(id, link_list, konnect_list, pinned_list, timers)
            path = '    m: last modified; c: created; most recent first'
            rows.append(
                    {
                        'sort': dt,
                        'path': path,
                        'values': [
                            itemtype,
                            summary,
                            flags,
                            rhc,
                            id
                            ],
                    }
                    )
    try:
        rows.sort(key=itemgetter('sort'), reverse=reverse)
    except:
        logger.error(f"sort exception: {e}: {[type(x['sort']) for x in rows]}")
    rdict = NDict()
    for row in rows:
        path = row['path']
        values = row['values']
        rdict.add(path, values)
    tree, row2id = rdict.as_tree(rdict, level=0)
    return tree, row2id


def show_review(db, pinned_list=[], link_list=[], konnect_list=[], timers={}):
    """
    Unfinished, undated tasks and jobs
    """
    width = shutil.get_terminal_size()[0] - 2
    rows = []
    locations = set([])
    summary_width = width - 18
    for item in db:
        if item.get('itemtype', None) not in ['-'] or 's' in item or 'f' in item:
            continue
        id = item.doc_id
        rhc = item.get('l', '~')[:10].ljust(10, ' ')
        itemtype = item['itemtype']
        summary = item['summary']
        flags = get_flags(id, link_list, konnect_list, pinned_list, timers)
        modified = item['modified'] if 'modified' in item else item['created']

        weeks = (pendulum.now() - modified).days // 7
        if weeks == 0:
            wkfmt = " This week"
        elif weeks == 1:
            wkfmt = " Last week"
        else:
            wkfmt = f" {weeks} weeks ago"
        rows.append(
                {
                    'path': wkfmt,
                    'sort': modified,
                    'values': [
                        itemtype,
                        summary,
                        flags,
                        rhc, # location
                        id,
                        ]
                }
                )
    try:
        rows.sort(key=itemgetter('sort'), reverse=False)
    except Exception as e:
        logger.error(f"sort exception: {e}: {[type(x['sort']) for x in rows]}")
    rdict = NDict()
    for row in rows:
        path = row['path']
        values = row['values']
        rdict.add(path, values)
    tree, row2id = rdict.as_tree(rdict, level=0)
    return tree, row2id

def show_timers(db, pinned_list=[], link_list=[], konnect_list=[], timers={}, active_timer=None):
    """
    timers
    """
    width = shutil.get_terminal_size()[0] - 2
    rows = []
    locations = set([])
    summary_width = width - 18
    now = pendulum.now('local')
    state2sort = {
            'i': 'inactive',
            'r': 'active',
            'p': 'active'
            }
    total_time = ZERO
    num_timers = 0
    timer_ids = [x for x in timers if x]
    for id in timer_ids:
        item = db.get(doc_id=id)
        if not item:
            continue
        state, start, elapsed = timers[id]
        if state == 'r':
            elapsed += round_minutes(now - start)
        num_timers += 1
        total_time += elapsed
        sort = state2sort[state]
        rhc = f"{format_duration(elapsed, short=True)}  {state}".rjust(10, ' ')
        itemtype = item['itemtype']
        summary = item['summary']
        flags = get_flags(id, link_list, konnect_list, pinned_list, timers)
        rows.append(
                {
                    'sort': (sort, now - start),
                    'values': [
                        itemtype,
                        summary,
                        flags,
                        rhc, # status
                        id,
                        ]
                }
                )
    try:
        rows.sort(key=itemgetter('sort'), reverse=False)
    except Exception as e:
        logger.error(f"sort exception: {e}: {[type(x['sort']) for x in rows]}")
    rdict = NDict()
    timers_fmt = "timers" if num_timers > 1 else "timer"
    path = f"{num_timers} {timers_fmt}: {format_duration(total_time, short=True)}".center(width, ' ')
    for row in rows:
        values = row['values']
        rdict.add(path, values)
    tree, row2id = rdict.as_tree(rdict, level=0)
    return tree, row2id

def show_konnected(db, pinned_list=[], link_list=[], konnect_list=[], timers={}, selected_id=None, from_ids={}, to_ids={}):
    """
    konnected view for selected_id
    """
    if selected_id is None or not db.contains(doc_id=selected_id):
        return [], {}
    selected_item = db.get(doc_id=selected_id)
    if selected_item is None:
        return [], {}

    relevant = []
    relevant.append([' Selection', selected_item])

    for id in from_ids.get(selected_id, []):
        tmp = db.get(doc_id=id)
        if tmp:
            relevant.append([' From the selection', tmp])

    for id in to_ids.get(selected_id, []):
        tmp = db.get(doc_id=id)
        if tmp:
            relevant.append([' To the selection', tmp])

    if len(relevant) < 2:
        # from and to are empty
        return [], {}

    width = shutil.get_terminal_size()[0] - 2
    rows = []
    summary_width = width - 11
    for path, item in relevant:
        id = item.doc_id
        rhc = str(id).rjust(5, ' ')
        itemtype = FINISHED_CHAR if 'f' in item else item.get('itemtype', '?')
        summary = item['summary']
        flags = get_flags(id, link_list, konnect_list, pinned_list, timers)
        rows.append(
                {
                    'path': path,
                    'sort': (path, -id),
                    'values': [
                        itemtype,
                        summary,
                        flags,
                        rhc,
                        id,
                        ]
                }
                )
    try:
        rows.sort(key=itemgetter('sort'), reverse=True)
    except Exception as e:
        logger.error(f"sort exception: {e}: {[type(x['sort']) for x in rows]}")
    rdict = NDict()
    for row in rows:
        path = row['path']
        values = row['values']
        rdict.add(path, values)
    tree, row2id = rdict.as_tree(rdict, level=0)
    return tree, row2id


def show_next(db, pinned_list=[], link_list=[], konnect_list=[], timers={}):
    """
    Unfinished, undated tasks and jobs
    """
    width = shutil.get_terminal_size()[0] - 2
    rows = []
    locations = set([])
    group_names = []
    groups = settings.get('locations', {})
    using_groups = True if groups else False
    if using_groups:
        group_names = groups.keys()
        location2groups = {'~': ['OTHER']}
        for group, locations in groups.items():
            for location in locations:
                location2groups.setdefault(location, []).append(group)

    for item in db:
        if item.get('itemtype', None) not in ['-'] or 's' in item or 'f' in item:
            continue
        id = item.doc_id
        flags = get_flags(id, link_list, konnect_list, pinned_list, timers)
        if 'j' in item:
            task_location = item.get('l', '~')
            priority = int(item.get('p', 0))
            sort_priority = 4 - int(priority)
            show_priority = str(priority) if priority > 0 else ""
            for job in item['j']:
                if job.get('f'):
                    # show completed jobs only in completed view
                    continue
                location = job.get('l', task_location)
                extent = job.get('e', '')
                extent = format_duration(extent) if extent else ''
                status = 0 if job.get('status') == '-' else 1
                # status 1 -> waiting, status 0 -> available
                rhc = " ".join([show_priority, extent]).center(7, ' ')
                summary = job.get('summary')
                job_id = job.get('i', None)
                job_sort = str(job_id)
                rows.append(
                    {
                        'id': item.doc_id,
                        'job': job_id,
                        'instance': None,
                        'sort': (location, status, sort_priority, job_sort, job.get('summary', '')),
                        'location': location,
                        'columns': [
                            job.get('status', ''),
                            summary,
                            flags,
                            rhc,
                            (id, None, job_id)
                            ]
                    }
                )
        else:
            location = item.get('l', '~')
            priority = int(item.get('p', 0))
            extent = item.get('e', '')
            extent = format_duration(extent) if extent else ""
            sort_priority = 4 - int(priority)
            show_priority = str(priority) if priority > 0 else ""
            rhc = " ".join([show_priority, extent]).center(7, ' ')
            summary = item['summary']
            rows.append(
                    {
                        'id': item.doc_id,
                        'job': None,
                        'instance': None,
                        'sort': (location, sort_priority, extent, item['summary']),
                        'location': location,
                        'columns': [
                            item['itemtype'],
                            summary,
                            flags,
                            rhc,
                            (id, None, None)
                            ]
                    }
                    )
    rows.sort(key=itemgetter('sort'))
    rdict = NDict()
    for row in rows:
        if using_groups:
            groups = location2groups.get(row['location'], ['OTHER'])
            for group in groups:
                path = f"{group}/{row['location']}"
                values = row['columns']
                rdict.add(path, values)
        else:
            path = row['location']
            values = row['columns']
            rdict.add(path, values)
    tree, row2id = rdict.as_tree(rdict, level=0)
    return tree, row2id


def show_journal(db, id2relevant, pinned_list=[], link_list=[], konnect_list=[], timers={}):
    """
    journal grouped by index entry
    """
    width = shutil.get_terminal_size()[0] - 2
    rows = []
    summary_width = width - 14
    # indices = set([])
    for item in db:
        id = item.doc_id
        if item['itemtype'] != '%':
            continue
        rhc = str(id).rjust(5, ' ')
        index = item.get('i', '~')
        itemtype = item['itemtype']
        summary = item['summary']
        flags = get_flags(id, link_list, konnect_list, pinned_list, timers)

        rows.append({
                    'sort': (index, item['summary']),
                    'path': index,
                    'values': [
                        itemtype,
                        summary,
                        flags,
                        rhc,
                        id
                        ],
                    })
    rows.sort(key=itemgetter('sort'))
    rdict = NDict()
    for row in rows:
        path = row['path']
        values = row['values']
        rdict.add(path, values)
    tree, row2id = rdict.as_tree(rdict, level=0)
    return tree, row2id


def show_tags(db, id2relevant, pinned_list=[], link_list=[], konnect_list=[], timers={}):
    """
    tagged items grouped by tag
    """
    width = shutil.get_terminal_size()[0] - 2
    rows = []
    for item in db:
        id = item.doc_id
        rhc = str(id).rjust(5, ' ')
        tags = item.get('t', [])
        itemtype = FINISHED_CHAR if 'f' in item else item.get('itemtype', '?')
        summary = item['summary']
        flags = get_flags(id, link_list, konnect_list, pinned_list, timers)

        for tag in subsets(tags):
            rows.append({
                        'sort': (tag, item['itemtype'], item['summary']),
                        'path': tag[1],
                        'values': [
                            itemtype,
                            summary,
                            flags,
                            rhc,
                            id
                            ],
                        })
    rows.sort(key=itemgetter('sort'))
    rdict = NDict()
    for row in rows:
        path = row['path']
        values = row['values']
        rdict.add(path, values)
    tree, row2id = rdict.as_tree(rdict, level=0)
    return tree, row2id


def show_location(db, id2relevant, pinned_list=[], link_list=[], konnect_list=[], timers={}):
    """
    items with location entries grouped by location
    """
    width = shutil.get_terminal_size()[0] - 2
    rows = []
    for item in db:
        id = item.doc_id
        rhc = str(id).rjust(5, ' ')
        location = item.get('l', '~')
        itemtype = FINISHED_CHAR if 'f' in item else item.get('itemtype', '?')
        summary = item['summary']
        flags = get_flags(id, link_list, konnect_list, pinned_list, timers)

        rows.append({
                    'sort': (location, item['itemtype'], item['summary']),
                    'path': location,
                    'values': [
                        itemtype,
                        summary,
                        flags,
                        rhc,
                        id
                        ],
                    })
    rows.sort(key=itemgetter('sort'))
    rdict = NDict()
    for row in rows:
        path = row['path']
        values = row['values']
        rdict.add(path, values)
    tree, row2id = rdict.as_tree(rdict, level=0)
    return tree, row2id


def show_index(db, id2relevant, pinned_list=[], link_list=[], konnect_list=[], timers={}):
    """
    All items grouped by index entry
    """
    rows = []
    for item in db:
        # if item['itemtype'] == '%':
        #     continue
        id = item.doc_id
        rhc = str(id).rjust(5, ' ')
        index = item.get('i', '~')
        itemtype = FINISHED_CHAR if 'f' in item else item.get('itemtype', '?')
        summary = item['summary']
        flags = get_flags(id, link_list, konnect_list, pinned_list, timers)
        rows.append({
                    'sort': (index, item['summary']),
                    'path': index,
                    'values': [
                        itemtype,
                        summary,
                        flags,
                        rhc,
                        id],
                    })
    rows.sort(key=itemgetter('sort'))
    rdict = NDict()
    for row in rows:
        path = row['path']
        values = row['values']
        try:
            rdict.add(path, values)
        except:
            logger.error(f"error adding path: {path}, values: {values}")
    tree, row2id = rdict.as_tree(rdict, level=0)
    return tree, row2id


def show_pinned(items, pinned_list=[], link_list=[], konnect_list=[], timers={}):
    width = shutil.get_terminal_size()[0] - 2
    rows = []
    rhc_width = 8
    for item in items:
        mt = item.get('modified', None)
        if mt is not None:
            dt, label = mt, 'm'
        else:
            dt, label = item.get('created', None), 'c'
        if dt is not None:
            id = item.doc_id
            year = dt.format("YYYY")
            monthday = dt.format("MMM D")
            time = fmt_time(dt)
            rhc = f"{str(id).rjust(6)}"
            itemtype = FINISHED_CHAR if 'f' in item else item.get('itemtype', '?')
            summary = item['summary']
            flags = get_flags(id, link_list, konnect_list, pinned_list, timers)

            rows.append(
                    {
                        'sort': (itemtype, dt),
                        'path': type_keys[itemtype],
                        'values': [
                            itemtype,
                            summary,
                            flags,
                            rhc,
                            id
                            ],
                    }
                    )

    rows.sort(key=itemgetter('sort'), reverse=False)
    rdict = NDict()
    for row in rows:
        path = row['path']
        values = row['values']
        rdict.add(path, values)
    tree, row2id = rdict.as_tree(rdict, level=0)
    return tree, row2id

def get_usedtime(db, pinned_list=[], link_list=[], konnect_list=[], timers={}):
    """
    All items with used entries grouped by month, index entry and day

    """
    UT_MIN = settings.get('usedtime_minutes', 1)

    width = shutil.get_terminal_size()[0] - 2
    summary_width = width - 21

    used_details = {}
    used_details2id = {}
    used_summary = {}

    month_rows = {}
    used_time = {}
    detail_rows = []
    months = set([])
    for item in db:
        used = item.get('u') # this will be a list of 'period, datetime' tuples
        if not used:
            continue
        index = item.get('i', '~')
        id_used = {}
        index_tup = index.split('/')
        id = item.doc_id
        itemtype = item['itemtype']
        summary = item['summary']
        flags = get_flags(id, link_list, konnect_list, pinned_list, timers)

        for period, dt in used:
            if isinstance(dt, pendulum.Date) and not isinstance(dt, pendulum.DateTime):
                dt = pendulum.parse(dt.format("YYYYMMDD"), tz='local')
                dt.set(hour=23, minute=59, second=59)
            # for id2used
            if UT_MIN != 1:
                res = period.minutes % UT_MIN
                if res:
                    period += (UT_MIN - res) * ONEMIN

            monthday = dt.date()
            id_used.setdefault(monthday, ZERO)
            id_used[monthday] += period
            # for used_time
            month = dt.format("YYYY-MM")
            used_time.setdefault(tuple((month,)), ZERO)
            used_time[tuple((month, ))] += period
            for i in range(len(index_tup)):
                used_time.setdefault(tuple((month, *index_tup[:i+1])), ZERO)
                used_time[tuple((month, *index_tup[:i+1]))] += period
        for monthday in id_used:
            month = monthday.format("YYYY-MM")
            rhc = f"{monthday.format('M/DD')}: {format_hours_and_tenths(id_used[monthday])}".ljust(14, ' ')
            detail_rows.append({
                        'sort': (month, index_tup, monthday, itemtype, summary),
                        'month': month,
                        'path': f"{monthday.format('MMMM YYYY')}/{index}",
                        'values': [
                            itemtype,
                            summary,
                            flags,
                            rhc,
                            id],
                        })

    try:
        detail_rows.sort(key=itemgetter('sort'))
    except Exception as e:
        # report the components of sort other than the last, the summary
        logger.error(f"error sorting detail_rows: f{e}\nsort: {[x['sort'][:-1] for x in detail_rows]}")
        return used_details, used_details2id, used_summary


    for month, items in groupby(detail_rows, key=itemgetter('month')):
        months.add(month)
        rdict = NDict()
        for row in items:
            path = row['path']
            values = row['values']
            try:
                rdict.add(path, values)
            except Exception as e:
                logger.error(f"error adding path: {path}, values: {values}: {e}")
        tree, row2id = rdict.as_tree(rdict, level=0)
        used_details[month] = tree
        used_details2id[month] = row2id

    keys = [x for x in used_time]
    keys.sort()
    for key in keys:
        period = used_time[key]
        month_rows.setdefault(key[0], [])
        indent = (len(key) - 1) * 3 * " "
        if len(key) == 1:
            yrmnth = pendulum.from_format(key[0] + "-01", "YYYY-MM-DD").format("MMMM YYYY")
            try:
                rhc = f"{format_hours_and_tenths(period)}"
                summary = f"{indent}{yrmnth}: {rhc}"[:summary_width]
                month_rows[key[0]].append(f"{summary}")
            except Exception as e:
                logger.error(f"e: {repr(e)}")

        else:
            rhc = f"{format_hours_and_tenths(period)}"
            summary = f"{indent}{key[-1]}: {rhc}"[:summary_width].ljust(summary_width, ' ')
            month_rows[key[0]].append(f"{summary}")

    for key, val in month_rows.items():
        used_summary[key] = "\n".join(val)

    return used_details, used_details2id, used_summary


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

    monday = pendulum_parse(f"{week[0]}-W{str(week[1]).zfill(2)}-1")
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

def summary_pin(text, width, id, pinned_list, link_list, konnected_list):
    in_konnected = False
    if id in konnected_list:
        in_konnected = True
        text = (text[:width-3].rstrip() +  KONNECT_CHAR)
    if id in link_list:
        text = (text[:width-3].rstrip() +  LINK_CHAR)
    if id in pinned_list:
        ret = (text[:width-1] + PIN_CHAR).ljust(width-1, ' ')
    else:
        ret = text[:width].ljust(width, ' ')
    return ret


def schedule(db, yw=getWeekNum(), current=[], now=pendulum.now(), weeks_before=0, weeks_after=0, pinned_list=[], link_list=[], konnect_list=[], timers={}):
    ampm = settings['ampm']
    omit = settings['omit_extent']
    UT_MIN = settings.get('usedtime_minutes', 1)
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
    # xx:xxam-xx:xxpm
    rhc_width = 15
    flag_width = 6
    indent_to_summary = 6
    summary_width = width - indent_to_summary - flag_width - rhc_width

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
        if item.get('itemtype', None) == None:
            logger.error(f"itemtype missing from {item}")
            continue
        if item['itemtype'] in "!?":
            continue
        summary = item.get('summary', "~")
        id = item.doc_id
        flags = get_flags(id, link_list, konnect_list, pinned_list, timers)
        if 'u' in item:
            used = item.get('u') # this will be a list of @u entries
            itemtype = item['itemtype']
            dates_to_periods = {}
            for period, dt in used:
                if isinstance(dt, pendulum.Date) and not isinstance(dt, pendulum.DateTime):
                    pass
                else:
                    dt = dt.date()
                if UT_MIN != 1:
                    # round up minutes
                    res = period.minutes % UT_MIN
                    if res:
                        period += (UT_MIN - res) * ONEMIN
                dates_to_periods.setdefault(dt, []).append(period)
            for dt in dates_to_periods:
                total = ZERO
                for p in dates_to_periods[dt]:
                    total += p
                rhc = format_hours_and_tenths(total).center(rhc_width, ' ')
                done.append(
                        {
                            'id': id,
                            'job': None,
                            'instance': None,
                            'sort': (dt.format("YYYYMMDD"), 1),
                            'week': (
                                dt.isocalendar()[:2]
                                ),
                            'day': (
                                dt.format("ddd MMM D"),
                                ),
                            'columns': [itemtype,
                                summary,
                                flags,
                                rhc,
                                (id, None, None)
                                ],
                        }
                        )

        if item['itemtype'] == '-':
            d = []
            if 'f' in item:
                d.append([item['f'], summary, item.doc_id, None])
            if 'h' in item:
                for dt in item['h']:
                    d.append([dt, summary, item.doc_id, None])
            if 'j' in item:
                for job in item['j']:
                    job_summary = job.get('summary', '')
                    if 'f' in job:
                        d.append([job['f'], job_summary, item.doc_id, job['i']])
            if d:
                for row in d:
                    dt = row[0]
                    if isinstance(dt, pendulum.Date) and not isinstance(dt, pendulum.DateTime):
                        dt = pendulum.parse(dt.format("YYYYMMDD"), tz='local')
                        dt.set(hour=23, minute=59, second=59)

                    rhc = ''
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
                                'columns': [FINISHED_CHAR,
                                    row[1],
                                    flags,
                                    rhc,
                                    (row[2], None, row[3])
                                    ],
                            }
                            )

        if 's' not in item or 'f' in item:
            continue

        # get the instances
        for dt, et in item_instances(item, aft_dt, bef_dt):
            start_dt = item['s']
            if 'r' in item:
                freq = item['r'][0].get('r', 'y')
            else:
                freq = 'y'
            instance = dt if '+' in item or 'r' in item else None
            if 'j' in item:
                for job in item['j']:
                    if 'f' in job:
                        continue
                    job_summary = job.get('summary', '')
                    jobstart = dt - job.get('s', ZERO)
                    job_id = job.get('i', None)
                    job_sort = str(job_id)

                    rhc = fmt_time(dt).center(rhc_width, ' ')
                    rows.append(
                        {
                            'id': item.doc_id,
                            'job': job_id,
                            'instance': instance,
                            'sort': (jobstart.format("YYYYMMDDHHmm"), job_sort),
                            'week': (
                                jobstart.isocalendar()[:2]
                                ),
                            'day': (
                                jobstart.format("ddd MMM D"),
                                ),
                            'columns': [job['status'],
                                set_summary(job_summary, start_dt,  jobstart, freq),
                                flags,
                                rhc,
                                (item.doc_id, instance, job_id)
                                ]
                        }
                    )

            else:
                if item['itemtype'] == '-':
                    rhc = fmt_time(dt).center(rhc_width, ' ')
                elif 'e' in item:
                    if omit and 'c' in item and item['c'] in omit:
                        et = None
                        rhc = fmt_time(dt).center(rhc_width, ' ')
                    else:
                        rhc = fmt_extent(dt, et).center(rhc_width, ' ')
                else:
                    rhc = fmt_time(dt).center(rhc_width, ' ')

                sort_dt = dt.format("YYYYMMDDHHmm")
                if sort_dt.endswith('0000'):
                    if item['itemtype'] == '*':
                        sort_dt = sort_dt[:-4] + '$$$$'
                    elif item['itemtype'] in ['-']:
                        sort_dt = sort_dt[:-4] + '24$$'
                    elif item['itemtype'] in ['%']:
                        sort_dt = sort_dt[:-4] + '24%%'

                rows.append(
                        {
                            'id': item.doc_id,
                            'job': None,
                            'instance': instance,
                            'sort': (sort_dt, 0),
                            'week': (
                                dt.isocalendar()[:2]
                                ),
                            'day': (
                                dt.format("ddd MMM D"),
                                ),
                            'columns': [item['itemtype'],
                                set_summary(summary, item['s'], dt, freq),
                                flags,
                                rhc,
                                (item.doc_id, instance, None)
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

        monday = pendulum_parse(f"{week[0]}-W{str(week[1]).zfill(2)}-1")
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

    for week, items in groupby(rows, key=itemgetter('week')):
        weeks.add(week)
        rdict = NDict()
        wk_fmt = fmt_week(week).center(width, ' ')
        today = now.format("ddd MMM D")
        tomorrow = (now + 1*DAY).format("ddd MMM D")
        for row in items:
            day = row['day'][0]
            if day == today:
                day += " (Today)"
            elif day == tomorrow:
                day += " (Tomorrow)"
            path = f"{wk_fmt}/{day}"
            values = row['columns']
            rdict.add(path, values)
        tree, row2id = rdict.as_tree(rdict, level=0)
        agenda_hsh[week] = tree
        row2id_hsh[week] = row2id

    for week, items in groupby(done, key=itemgetter('week')):
        weeks.add(week)
        rdict = NDict()
        wk_fmt = fmt_week(week).center(width, ' ')
        today = now.format("ddd MMM D")
        for row in items:
            day = row['day'][0]
            if day == today:
                day += " (Today)"
            path = f"{wk_fmt}/{day}"
            values = row['columns']
            rdict.add(path, values)
        tree, row2id = rdict.as_tree(rdict, level=0)
        done_hsh[week] = tree
        done2id_hsh[week] = row2id

    cache = {}
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


def import_file(import_file=None):
    if not import_file:
        return False, ""
    import_file = os.path.normpath(os.path.expanduser(import_file))
    if not os.path.exists(import_file):
        return False, f"could not locate: {import_file}"
    filename, extension = os.path.splitext(import_file)
    if extension == '.json':
        return True, import_json(import_file)
    elif extension == '.text':
        return True, import_text(import_file)
    elif extension == '.ics':
        return True, import_ics(import_file)
    else:
        return False, f"Importing a file with the extension '{extension}' is not implemented. Only 'json', 'text' and 'ics' are recognized"


def import_ics(import_file=None):
    """
    open ics file and convert it to text file in tempdir. Then import the text file using
    """
    items = ical.ics_to_items(import_file)
    if not items:
        return
    # check for dups
    exst = []
    new = []
    dups = 0
    for x in ETMDB:
        exst.append({
                    'itemtype': x.get('itemtype'),
                    'summary': x.get('summary'),
                    's': x.get('s'),
                    # 'f': x.get('f')
                    })
    num_docs = len(items.keys())
    for i, x  in items.items():
        y = {
                    'itemtype': x.get('itemtype'),
                    'summary': x.get('summary'),
                    's': x.get('s'),
                    # 'f': x.get('f')
                    }
        if exst and y in exst:
            dups += 1
        else:
            x['created'] = pendulum.now()
            new.append(x)

    ids = []
    if new:
        ids = ETMDB.insert_multiple(new)
    msg = f"imported {len(new)} items"
    if ids:
        msg += f"\n  ids: {ids[0]}-{ids[-1]}."
    if dups:
        msg += f"\n  rejected {dups} items as duplicates"
    return msg


def import_text(import_file=None):
    docs = []
    with open(import_file, 'r') as fo:
        results = []
        good = []
        bad = 0
        reminders = []
        reminder = []
        for line in fo:
            s = line.strip()
            if s and s[0] in ['!', '*', '-', '%']:
                if reminder:
                    # append it to reminders and reset it
                    reminders.append(reminder)
                    reminder = []
                reminder = [s]
            else:
                # append to the existing reminder
                reminder.append(s)
        if reminder:
            reminders.append(reminder)
    for reminder in reminders:
        logger.debug(f"processing {reminder}")
        ok = True
        s = "\n".join(reminder)
        if not s: continue
        item = Item()  # use ETMDB by default
        item.new_item()
        item.text_changed(s, 1)
        if item.item_hsh.get('itemtype', None) is None:
            ok = False

        if item.item_hsh.get('summary', None) is None:
            ok = False

        if not ok:
            bad += 1
            results.append(f"   {s}")
            continue

        # update_item_hsh stores the item in ETMDB
        logger.debug(f"updating {item}")
        item.update_item_hsh()
        good.append(f"{item.doc_id}")

    res = f"imported {len(good)} items"
    if good:
        # ids = ETMDB.insert_multiple(docs)
        res += f"\n  ids: {good[0]} - {good[-1]}"
    if bad:
        res += f"\nrejected {bad} items:\n  "
        res += "\n  ".join(results)
    return res


def import_json(import_file=None):
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
                            logger.error(f"error parsing rul['u']: {rul['u']}. {e}")
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
                    's': x.get('s'),
                    # 'f': x.get('f')
                    })
    i = 0
    for x in docs:
        i += 1
        y = {
                    'itemtype': x.get('itemtype'),
                    'summary': x.get('summary'),
                    's': x.get('s'),
                    # 'f': x.get('f')
                    }
        if exst and y in exst:
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
    return msg


def about(padding=0):
    logo_lines = [
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

    summary = wrap(f"This application provides a format for using plain text entries to create events, tasks and other reminders and a prompt_toolkit based interface for creating and modifying items as well as viewing them.", 0, width)

    ret1 = f"""\
{logo}
{summary}

Discussion:     groups.io/g/etm
Documentation:  dagraham.github.io/etm-dgraham
PyPi:           pypi.org/project/etm-dgraham
GitHub:         github.com/dagraham/etm-dgraham
Developer:      dnlgrhm@gmail.com

{copyright}\
"""

    ret2 = f"""
etm:            {etm_version}
python:         {python_version}
dateutil:       {dateutil_version}
pendulum:       {pendulum_version}
prompt_toolkit: {prompt_toolkit_version}
tinydb:         {tinydb_version}
jinja2:         {jinja2_version}
ruamel.yaml:    {ruamel_version}
platform:       {system_platform}
etm directory:  {etmhome}
"""
    return ret1, ret2



dataview = None
item = None
def main(etmdir="", *args):
    global dataview, item, db, ampm, settings
    # NOTE: DataView called in model.main
    dataview = DataView(etmdir)
    settings = dataview.settings
    db = dataview.db
    item = Item(etmdir)
    dataview.refreshCache()


if __name__ == '__main__':
    sys.exit('model.py should only be imported')

