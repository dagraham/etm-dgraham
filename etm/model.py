#  standard sort order for usable ASCII characters
# usable = ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_', '`', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~']
# len(usable): 94

from etm.common import (
    VERSION_INFO,
    parse,
    WKDAYS_DECODE,
    WKDAYS_ENCODE,
    ETM_CHAR,
    Period,
)

from tinydb.table import Document
from etm.common import TimeIt
import sys
import re
from pprint import pprint
import tracemalloc

# import datetime  # for type testing in rrule
import locale
import calendar
from copy import deepcopy
import math
import shutil
from operator import itemgetter
from itertools import groupby, combinations

from prompt_toolkit.styles import Style

# from ruamel.yaml import __version__ as ruamel_version
# from dateutil import __version__ as dateutil_version
# from tinydb import __version__ as tinydb_version
# from jinja2 import __version__ as jinja2_version
# from prompt_toolkit import __version__ as prompt_toolkit_version

from dateutil import rrule as dr
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
from dateutil.rrule import MO, TU, WE, TH, FR, SA, SU

# for saving timers
import pickle
from warnings import filterwarnings
from ruamel.yaml import YAML
from jinja2 import Template
import textwrap
import os
import platform
import string as strng
from zipfile import ZipFile, ZIP_DEFLATED

from etm.view import is_showing_konnections

# from etm.report import get_usedtime_cvs

for key, value in ETM_CHAR.items():
    globals()[key] = value

yaml = YAML(typ='safe', pure=True)

LOWERCASE = list(strng.ascii_lowercase)

# for compressing backup files
system_platform = platform.platform(terse=True)
python_version = platform.python_version()
developer = 'dnlgrhm@gmail.com'

# These are set in _main_
DBITEM = None
DBARCH = None
ETMDB = None
data = None
# NOTE: view.main() will override ampm using the configuration setting
ampm = True
logger = None

active_tasks = {}


def sortprd(prd):
    # assumes prd is a Period
    return prd.start.strftime('%Y%m%d%H%M')


PHONE_REGEX = re.compile(r'[0-9]{10}@.*')
KONNECT_REGEX = re.compile(r'^.+:\s+(\d+)\s*$')
YMD_REGEX = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}')  # 4-digit year - 2-digit month - 2-digit month day

# The style sheet for terminal output
style = Style.from_dict(
    {
        'plain': '#fffafa',
        'selection': '#fffafa',
        'inbox': '#ff00ff',
        'pastdue': '#87ceeb',
        'begin': '#ffff00',
        'journal': '#daa520',
        'event': '#90ee90',
        'available': '#1e90ff',
        'waiting': '#6495ed',
        'finished': '#191970',
    }
)

etmdir = None

ETMFMT = '%Y%m%dT%H%M'
ZERO = timedelta(minutes=0)
ONEMIN = timedelta(minutes=1)
ONESEC = timedelta(seconds=1)
DAY = timedelta(days=1)


type_keys = {
    '*': 'event',
    '-': 'task',
    '✓': 'finished',
    '%': 'journal',
    '!': 'inbox',
    '~': 'wrap',
}

wrapbefore = '↱'
wrapafter = '↳'

type_prompt = 'item type character:'

item_types = """item type characters:\n    """ + """\n    """.join(
    [f'{k}: {v}' for k, v in type_keys.items()]
)

common_methods = list('cdgikKlmnstuxz')
repeating_methods = list('+-o') + [
    'rr',
    'rc',
    'rm',
    'rE',
    'rh',
    'ri',
    'rM',
    'rn',
    'rs',
    'ru',
    'rW',
    'rw',
]
datetime_methods = list('abe')
task_methods = list('efhp') + [
    'jj',
    'ja',
    'jb',
    'jd',
    'je',
    'jf',
    'ji',
    'jl',
    'jm',
    'jp',
    'js',
    'ju',
]

wrap_methods = ['w']

required = {'*': ['s'], '-': [], '%': []}
allowed = {
    '*': common_methods + datetime_methods + repeating_methods + wrap_methods,
    '-': common_methods + datetime_methods + task_methods + repeating_methods,
    '%': common_methods + ['+'],
}
# inbox
required['!'] = []
allowed['!'] = (
    common_methods + datetime_methods + task_methods + repeating_methods
)

requires = {
    'a': ['s'],
    'b': ['s'],
    '+': ['s'],
    '-': ['rr'],
    'rr': ['s'],
    'js': ['s'],
    'ja': ['s'],
    'jb': ['s'],
}

def truncate_string(s: str, max_length: int)->str:
    if len(s) > max_length:
        return f"{s[:max_length-2]} {ELLIPSiS_CHAR}"
    else:
        return s

def round_to_minutes(obj: timedelta)->timedelta:
    """
    Round a timedelta object to the nearest minute
    """
    seconds = abs(int(obj.total_seconds()))
    minutes = seconds // 60
    if seconds % 60 >= 30:
        minutes += 1
    return timedelta(minutes=minutes)

# def is_leap_year(year):
#     """Return True if the year is a leap year, False otherwise."""
#     if year % 400 == 0:
#         return True
#     if year % 100 == 0:
#         return False
#     if year % 4 == 0:
#         return True
#     return False

# Example usage
# current_year = 2024  # You can replace this with any year you want to check
# print(is_leap_year(current_year))


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
            ret.extend((str(i), ' & '.join(list(tup))) for tup in tmp)
    if len(l) == 0:
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
        return ([], [])
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
    return busy_minutes, conf_minutes


def get_busy_settings() -> tuple:
    width = shutil.get_terminal_size()[0]

    if width < 70:
        begin_hour = 6
        end_hour = 24
        slot_minutes = 30
        marker_hour_interval = 3
    else:
        begin_hour = 6
        end_hour = 24
        slot_minutes = 20
        marker_hour_interval = 2

    return begin_hour, end_hour, slot_minutes, marker_hour_interval


def day_bar_labels() -> str:

    (
        begin_hour,
        end_hour,
        slot_minutes,
        marker_hour_interval,
    ) = get_busy_settings()

    # label_interval = (marker_hour_interval*60) // slot_minutes

    MIDNIGHT = datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    HOUR = timedelta(hours=1)
    label_length = (marker_hour_interval * 60) // slot_minutes
    ampm = settings.get('ampm', True)
    hour_fmt = '%-I%p' if ampm else '%H'
    dent = ' ' * 7 if ampm else ' ' * 8
    hour_labels = [dent]
    for i in range(begin_hour, end_hour, marker_hour_interval):
        if (i - begin_hour) % marker_hour_interval == 0:
            l = f"{(MIDNIGHT + i*HOUR).strftime(hour_fmt).rstrip('M').lower()}"
            hour_labels.append(f"{l}{' '*(label_length - len(l))}")
        else:
            hour_labels.append(' ' * label_length)
    if end_hour % marker_hour_interval == 0:
        last_label = f"{(MIDNIGHT + end_hour*HOUR).strftime(hour_fmt).rstrip('M').lower()}"
        last_label = last_label if last_label else '24'
        hour_labels.append(last_label)

    return ''.join(hour_labels)


def day_bar(events: list, allday: bool = False) -> str:
    """Takes begin hour, end hour, slot minutes and a list of
    (integer start minutes, integer end minutes) tuples, Return a string
    representing the corresponding free, busy and conflict slots.

    Args:
        events (list): (start minutes, extent minutes)
        allday (bool): At least one all day event is scheduled

    Returns:
        list[in]: free, busy and conflict slots
    """
    VSEP = '⏐'   # U+23D0  this will be a de-emphasized color
    FREE = '─'   # U+2500  this will be a de-emphasized color
    BUSY = '■'   # '■' # U+25A0 this will be busy (event) color
    CONF = '▦'   # '▦' # U+25A6 this will be conflict color
    ADAY = '━'   # U+2501 for all day events ━
    RSKIP = '▶'   # U+25E6 for used time
    LSKIP = '◀'   # U+25E6 for used time
    # RSKIP   =  '⏵' # U+25E6 for used time
    # LSKIP   =  '⏴' # U+25E6 for used time

    # TODO: add ADAY switch and spacing for FREE

    (
        begin_hour,
        end_hour,
        slot_minutes,
        marker_hour_interval,
    ) = get_busy_settings()

    begin_slots = (begin_hour * 60) // slot_minutes
    end_slots = (end_hour * 60) // slot_minutes

    if slot_minutes in [5, 10, 12, 15, 20, 30, 60]:
        marker_slot_interval = (marker_hour_interval * 60) // slot_minutes
    else:
        marker_slot_interval = 0

    all_slots = []

    for i in range(1 + (24 * 60) // slot_minutes):
        if marker_slot_interval and i % marker_slot_interval == 0:
            all_slots.append([VSEP, 0])
        else:
            all_slots.append([None, 0])

    # all_slots = [0 for i in range((24*60)//slot_minutes)] # 24*12/5 5-minute slots + before + after.  All initially free = 0.
    for start, end in events:
        extent = end - start
        start_slot = start // slot_minutes
        num_slots = (
            extent // slot_minutes
            if extent % slot_minutes == 0
            else extent // slot_minutes + 1
        )
        for i in range(
            start_slot, min(start_slot + num_slots, len(all_slots))
        ):
            # free 0 -> busy 1; busy 1 -> confict 2
            all_slots[i][1] = min(all_slots[i][1] + 1, 2)

    # replace slots prior to 'begin' and after 'end' with their
    # respective maximums

    event_slots = []
    if begin_hour > 0:
        event_slots.append(max([x[1] for x in all_slots[:begin_slots]]))
        if all_slots[begin_slots][0] is None:
            event_slots.append(f' {LSKIP} ')
    for x in all_slots[begin_slots:end_slots]:
        # if x[0] is not None:
        #     # append VSEP
        #     event_slots.append(x[0])
        # event_slots.append(x[1])
        if x[1] > 0:
            event_slots.append(x[1])
            # append VSEP
        elif x[0] is not None:
            event_slots.append(x[0])
        else:
            event_slots.append(x[1])   # 0
    if end_hour < 24:
        if all_slots[end_slots][0] is not None:
            event_slots.append(all_slots[end_slots][0])
        else:
            event_slots.append(f' {RSKIP} ')
        event_slots.append(max([x[1] for x in all_slots[end_slots:]]))
    elif marker_slot_interval:
        event_slots.append(VSEP)

    busyfree = []
    for j in range(len(event_slots)):
        if event_slots[j] == 0:
            if allday:
                busyfree.append(ADAY)
            else:
                busyfree.append(HSEP)
        elif event_slots[j] == 1:
            busyfree.append(BUSY)
        elif event_slots[j] == 2:
            busyfree.append(CONF)
        else:
            busyfree.append(event_slots[j])

    return ''.join(busyfree)


def busy_conf_day(lofp, allday=False):
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

    busy_ranges, conf_ranges = busy_conf_minutes(lofp)
    busy_quarters = []
    conf_quarters = []
    first_quarter = beginbusy * 4
    last_quarter = first_quarter + 14 * 4 + 1

    for (b, e) in conf_ranges:
        h_b = b // 15
        h_e = e // 15
        if e % 15:
            h_e += 1
        for i in range(h_b, h_e):
            if i not in conf_quarters:
                conf_quarters.append(i)

    for (b, e) in busy_ranges:
        h_b = b // 15
        h_e = e // 15
        if e % 15:
            h_e += 1
        for i in range(h_b, h_e):
            if i not in conf_quarters and i not in busy_quarters:
                busy_quarters.append(i)
    h = {0: '  ', 58: '  '}
    for i in range(1, 58):
        h[i] = ' ' if (i - 1) % 4 else VSEP
    empty = ''.join([h[i] for i in range(59)])
    for i in range(1, 58):
        if allday:
            h[i] = ADAY   # if (i-1) % 4 else VSEP
        else:
            h[i] = HSEP if (i - 1) % 4 else VSEP

    # quarters: 1 before start + 1 after start + 56 + 1 between = 59 slots 0, ... 58
    conflict = False
    busy = False
    for i in range(first_quarter):
        if i in conf_quarters:
            conflict = True
        if i in busy_quarters:
            busy = True
        h[0] = f'{CONF} ' if conflict else f'{BUSY} ' if busy else '  '
    conflict = False
    busy = False
    for i in range(last_quarter, 24 * 4):
        if i in conf_quarters:
            conflict = True
        elif i in busy_quarters:
            busy = True
        h[58] = f' {CONF}' if conflict else f' {BUSY}' if busy else '  '
    for i in range(first_quarter, last_quarter):
        if i in conf_quarters:
            h[i - first_quarter + 1] = CONF
        elif i in busy_quarters:
            h[i - first_quarter + 1] = BUSY
    res = f"\n{empty}\n{''.join([h[i] for i in range(59)])}"
    full = ''.join([h[i] for i in range(59)])
    # empty: blank busy bar
    # full:  busy bar with busy/conflict markers
    return empty, full


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
    xpat = re.compile(r'@x\s+[a-zA-Z]+\s')
    match = xpat.findall(s)
    if match and settings:
        xparts = match[0].split(' ')
        if xparts[1] in settings['expansions']:
            replacement = settings['expansions'][xparts[1]] + xparts[2]
            s = s.replace(match[0], replacement)

    pattern = re.compile(r'\s[@&][a-zA-Z+-]')
    parts = [
        [match.span()[0] + 1, match.span()[1], match.group().strip()]
        for match in pattern.finditer(s)
    ]
    if not parts:
        tups.append((s[0], s[1:].strip(), 0, len(s) + 1))

    lastbeg = 0
    lastend = 1
    lastkey = s[0]
    for beg, end, key in parts:
        tups.append([lastkey, s[lastend:beg].strip(), lastbeg, beg])
        pos_hsh[tups[-1][2], tups[-1][3]] = (tups[-1][0], tups[-1][1])
        lastkey = key
        lastbeg = beg
        lastend = end
    tups.append([lastkey, s[lastend:].strip(), lastbeg, len(s) + 1])
    pos_hsh[tups[-1][2], tups[-1][3]] = (tups[-1][0], tups[-1][1])

    pos_hsh = {}  # (tupbeg, tupend) -> [key, value]

    # add (@?, '') and (&?, '') tups for @ and & entries without keys
    aug_tups = []
    for key, value, beg, end in tups:
        if beg == 0:
            aug_tups.append(('itemtype', key, beg, 1))
            if value.endswith(' @') or value.endswith(' &'):
                aug_key = f'{value[-1]}?'
                end -= 2
                value = value[:-2]
                aug_tups.extend(
                    (('summary', value, 1, end), (aug_key, '', end, end + 2))
                )
            else:
                aug_tups.append(('summary', value, 1, end))
        elif value.endswith(' @') or value.endswith(' &'):
            aug_key = f'{value[-1]}?'
            end -= 2
            value = value[:-2]
            aug_tups.extend(
                ((key, value, beg, end), (aug_key, '', end, end + 2))
            )
        else:
            aug_tups.append((key, value, beg, end))

    for key, value, beg, end in aug_tups:
        if key in ['@r', '@j']:
            pos_hsh[beg, end] = (f'{key[-1]}{key[-1]}', value)
            adding = key[-1]
        elif key in ['@a', '@u']:
            pos_hsh[beg, end] = (key[-1], value)
            adding = None
        elif key.startswith('&'):
            if adding:
                pos_hsh[beg, end] = (f'{adding}{key[-1]}', value)
        elif key in ['itemtype', 'summary']:
            adding = None
            pos_hsh[beg, end] = (key, value)
        else:
            adding = None
            pos_hsh[beg, end] = (key[-1], value)

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
    """ """
    # def __init__(self, doc_id=None, s=""):
    def __init__(self, dbfile=None, entry=""):
        """ """
        self.doc_id = None
        self.entry = entry
        self.init_entry = ''
        self.is_new = True
        self.is_modified = False
        self.created = None
        self.modified = None
        self.set_dbfile(dbfile)
        self.object_hsh = {}  # key, val -> object version for tinydb
        self.askreply = {}     # key, val -> display version raw string
        self.pos_hsh = {}     # (beg, end) -> (key, val)
        self.keyvals = []

        self.messages = []
        self.active = ()
        self.interval = ()
        self.item_hsh = {}      # key -> obj
        # Note: datetime(s) require timezone and at requires itemtype
        # all else do not need item_hsh
        self.keys = {
            'itemtype': [
                'item type',
                'character from * (event), - (task), % (journal) or ! (inbox)',
                self.do_itemtype,
            ],
            'summary': [
                'summary',
                "brief item description. Append an '@' to add an option.",
                self.do_summary,
            ],
            '+': [
                'include',
                'list of datetimes to include',
                self.do_datetimes,
            ],
            '-': [
                'exclude',
                'list of datetimes to exclude',
                self.do_datetimes,
            ],
            'a': ['alerts', 'list of alerts', do_alert],
            'b': ['beginby', 'number of days for beginby notices', do_beginby],
            'c': ['calendar', 'calendar', do_string],
            'd': ['description', 'item details', do_paragraph],
            'e': ['extent', 'timeperiod', do_duration],
            'w': ['wrap', 'list of two timeperiods', do_two_periods],
            'f': ['finish', 'completion done -> due', self.do_completion],
            'g': ['goto', 'url or filepath', do_string],
            'h': [
                'completions',
                'list of completion datetimes',
                self.do_completions,
            ],
            'i': ['index', 'forward slash delimited string', do_string],
            'k': ['konnection', 'document id', do_konnection],
            'K': ['konnect', 'summary for inbox item', do_konnect],
            'l': [
                'location',
                'location or context, e.g., home, office, errands',
                do_string,
            ],
            'm': ['mask', 'string to be masked', do_mask],
            'n': ['attendee', 'name <email address>', do_string],
            'o': [
                'overdue',
                'character from (r)estart, (s)kip or (k)eep',
                do_overdue,
            ],
            'p': [
                'priority',
                'priority from 0 (none) to 4 (urgent)',
                do_priority,
            ],
            's': ['scheduled', 'starting date or datetime', self.do_datetime],
            't': ['tag', 'tag', do_string],
            'u': ['used time', 'timeperiod: datetime', do_usedtime],
            'x': ['expansion', 'expansion key', do_string],
            'z': [
                'timezone',
                "a timezone entry such as 'US/Eastern' or 'Europe/Paris' or 'float' to specify a naive/floating datetime",
                self.do_timezone,
            ],
            '?': ['@-key', '', self.do_at],
            'rr': [
                'repetition frequency',
                "character from (y)ear, (m)onth, (w)eek,  (d)ay, (h)our, mi(n)ute. Append an '&' to add a repetition option.",
                do_frequency,
            ],
            'ri': ['interval', 'positive integer', do_interval],
            'rm': [
                'monthdays',
                'list of integers 1 ... 31, possibly prepended with a minus sign to count backwards from the end of the month',
                do_monthdays,
            ],
            'rE': [
                'easterdays',
                'number of days before (-), on (0) or after (+) Easter',
                do_easterdays,
            ],
            'rh': ['hours', 'list of integers in 0 ... 23', do_hours],
            'rM': ['months', 'list of integers in 1 ... 12', do_months],
            'rn': ['minutes', 'list of integers in 0 ... 59', do_minutes],
            'rw': [
                'weekdays',
                'list from SU, MO, ..., SA, possibly prepended with a positive or negative integer',
                do_weekdays,
            ],
            'rW': [
                'week numbers',
                'list of integers in 1, ... 53',
                do_weeknumbers,
            ],
            'rc': ['count', 'integer number of repetitions', do_count],
            'ru': ['until', 'datetime', self.do_until],
            'rs': ['set positions', 'integer', do_setpositions],
            'r?': ['repetition &-key', 'enter &-key', self.do_ampr],
            'jj': [
                'summary',
                "job summary. Append an '&' to add a job option.",
                do_string,
            ],
            'ja': [
                'alert',
                'list of timeperiods before job is scheduled followed by a colon and a list of commands',
                do_alert,
            ],
            'jb': ['beginby', ' integer number of days', do_beginby],
            'jd': ['description', ' string', do_paragraph],
            'je': ['extent', ' timeperiod', do_duration],
            'jf': ['finish', ' completion done -> due', self.do_completion],
            'ji': ['unique id', ' integer or string', do_string],
            'jl': ['location', ' string', do_string],
            'jm': ['mask', 'string to be masked', do_mask],
            'jp': [
                'prerequisite ids',
                'list of ids of immediate prereqs',
                do_stringlist,
            ],
            'js': [
                'scheduled',
                'timeperiod before task scheduled when job is scheduled',
                do_duration,
            ],
            'ju': ['used time', 'timeperiod: datetime', do_usedtime],
            'j?': ['job &-key', 'enter &-key', self.do_ampj],
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
                logger.error(f'{dbfile} does not exist')
                return
            logger.debug(f"dbfile is {dbfile}, initializing tinydb")
            self.db = data.initialize_tinydb(dbfile)
            self.dbarch = self.db.table('archive', cache_size=30)
            self.dbquery = self.db.table('items', cache_size=0)

    def use_archive(self):
        self.query_mode = 'archive table'
        self.db = DBARCH

    def use_items(self):
        self.query_mode = 'items table'
        self.db = DBITEM

    def check_goto_link(self, num=5):
        """ """
        logger.debug("calling update_item_hsh from check_goto_link")
        self.update_item_hsh()
        if goto := self.item_hsh.get('g'):
            return True, goto
        else:
            return False, 'does not have an @g goto entry'

    def get_repetitions(self):
        """
        Called with a row, we should have an doc_id and can use relevant
        as aft_dt. Called while editing, we won't have a row or doc_id
        and can use '@s' as aft_dt
        """
        # doc_id, instance, job = dataview.get_row_details(text_area.document.cursor_position_row)

        num = self.settings['num_repetitions']
        self.update_item_hsh()
        item = self.item_hsh
        showing = 'Repetitions'
        if 's' not in item and ('r' not in item or '+' not in item):
            return showing, 'not a repeating item'
        relevant = date_to_datetime(item['s'])
        at_plus = item.get('+', [])
        if at_plus:
            at_plus.sort()
            relevant = min(relevant, date_to_datetime(at_plus[0]))
        logger.debug(f'relevant: {relevant}')

        instances = item_instances(item, relevant, num + 1, False)
        instances.sort()
        pairs = [format_datetime(x[0])[1] for x in instances]
        starting = format_datetime(relevant.date())[1]
        if len(pairs) > num:
            showing = f'Next {num} repetitions'
            pairs = pairs[:num]
        elif pairs:
            showing = 'All repetitions'
        else:
            showing = 'No repetitions'
        return showing, f'from {starting}:\n  ' + '\n  '.join(pairs)

    def do_update(self):
        try:
            self.db.remove(doc_ids=[self.doc_id])
            self.db.insert(Document(self.item_hsh, doc_id=self.doc_id))
        except Exception as e:
            logger.debug(f"exception: {e}")
        return True

    def do_insert(self):
        # timer_insert = TimeIt('***INSERT***')
        if 'created' not in self.item_hsh:
            self.item_hsh['created'] = datetime.now().astimezone()
        doc_id = self.db.insert(self.item_hsh)
        # timer_insert.stop()
        return doc_id

    def edit_item(self, doc_id=None, entry=''):
        if not (doc_id and entry):
            return None
        item_hsh = self.db.get(doc_id=doc_id)
        self.init_entry = entry
        if item_hsh:
            self.doc_id = doc_id
            self.is_new = False
            self.item_hsh = deepcopy(item_hsh)   # created and modified entries
            self.keyvals = []
            self.text_changed(entry, 0, False)

    def edit_copy(self, doc_id=None, entry=''):
        if not (doc_id and entry):
            return None
        if item_hsh := self.db.get(doc_id=doc_id):
            self.doc_id = None
            self.is_new = True
            self.item_hsh = deepcopy(item_hsh)   # created and modified entries
            self.keyvals = []
            self.text_changed(entry, 0, False)

    def new_item(self):
        self.doc_id = None
        self.is_new = True
        self.item_hsh = {}
        self.entry = ''

    def delete_item(self, doc_id=None):
        if not (doc_id):
            return None
        try:
            self.db.remove(doc_ids=[doc_id])
            return True
        except:
            return False

    def add_used(self, doc_id, period, dt):
        self.item_hsh = self.db.get(doc_id=doc_id)
        self.doc_id = doc_id
        self.created = self.item_hsh['created']
        # ut = [x.strip() for x in usedtime.split(': ')]
        # if len(ut) != 2:
        #     return False, f"The entry '{usedtime}' is invalid"

        # per_ok, per = parse_duration(ut[0])
        # if not per_ok:
        #     return False, f"The entry '{ut[0]}' is not a valid period"
        # dt_ok, dt, z = parse_datetime(ut[1])
        # if not dt_ok:
        #     return False, f"The entry '{ut[1]}' is not a valid datetime"

        used_times = self.item_hsh.get('u', [])
        used_times.append([period, dt])
        self.item_hsh['u'] = used_times
        self.item_hsh['created'] = self.created
        self.item_hsh['modified'] = datetime.now().astimezone()
        # self.db.update(db_replace(self.item_hsh), doc_ids=[self.doc_id])
        self.do_update()

        return True, ''

    def schedule_new(self, doc_id, new_dt):
        self.item_hsh = self.db.get(doc_id=doc_id)
        self.doc_id = doc_id
        self.created = self.item_hsh['created']
        changed = False
        if 's' not in self.item_hsh:
            self.item_hsh['s'] = new_dt
        elif (
            'r' in self.item_hsh
            and '-' in self.item_hsh
            and new_dt in self.item_hsh['-']
        ):
            self.item_hsh['-'].remove(new_dt)
        else:
            # works both with and without r
            self.item_hsh.setdefault('+', []).append(new_dt)
        changed = True
        if changed:
            self.item_hsh['created'] = self.created
            self.item_hsh['modified'] = datetime.now().astimezone()
            # self.db.update(db_replace(self.item_hsh), doc_ids=[self.doc_id])
            self.do_update()
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
            self.item_hsh['modified'] = datetime.now().astimezone()
            # self.db.update(db_replace(self.item_hsh), doc_ids=[self.doc_id])
            self.do_update()
            return True
        else:
            # repeating
            removed_old = False
            added_new = self.schedule_new(doc_id, new_dt)
            if added_new:
                removed_old = self.delete_instances(doc_id, old_dt, 0)
            else:
                logger.warning(f'doc_id: {doc_id}; error adding {new_dt}')
            return added_new and removed_old

    def delete_instances(self, doc_id, instance, which):
        """
        which:
        (1, 'this instance'),
        (2, 'this and any subsequent instance'),
        (3, 'the item itself'),
        """
        self.item_hsh = self.db.get(doc_id=doc_id)
        self.doc_id = doc_id
        self.created = self.item_hsh['created']
        changed = False
        if which == '1':
            # this instance
            if '+' in self.item_hsh and instance in self.item_hsh['+']:
                self.item_hsh['+'].remove(instance)
                changed = True
            elif 'r' in self.item_hsh:
                # instances don't include @s
                self.item_hsh.setdefault('-', []).append(instance)
                changed = True
            elif self.item_hsh['s'] == instance:
                if '+' in self.item_hsh and self.item_hsh['+']:
                    self.item_hsh['s'] = self.item_hsh['+'].pop(0)
                else:
                    del self.item_hsh['s']
                changed = True
            else:
                # should not happen
                logger.warning(
                    f'could not remove {instance} from {self.item_hsh}'
                )
            if changed:
                self.item_hsh['created'] = self.created
                self.item_hsh['modified'] = datetime.now().astimezone()

                # self.db.update(db_replace(self.item_hsh), doc_ids=[self.doc_id])
                self.do_update()
        if which == '2':
            # this and any future instances
            delete_item = False
            if '+' in self.item_hsh:
                for dt in self.item_hsh['+']:
                    if dt >= instance:
                        self.item_hsh['+'].remove(instance)
                        changed = True
            if 'r' in self.item_hsh:
                # instances don't necessarily include @s
                # r will contain a list of hashes
                rr_to_keep = []
                for i in range(len(self.item_hsh['r'])):
                    rr = self.item_hsh['r'][i]
                    if 'c' in rr:
                        # error to have a 'u' with this 'c'
                        current_count = rr['c']
                        rset = dr.rruleset()
                        freq, kwd = rrule_args(rr)
                        kwd['dtstart'] = self.item_hsh['s']
                        rset.rrule(dr.rrule(freq, **kwd))
                        new_count = current_count - sum(
                            1
                            for dt in rset
                            if dt.astimezone() >= instance.astimezone()
                        )
                        if new_count > 0 and new_count < current_count:
                            rr['c'] = new_count
                            self.item_hsh['r'][i] = rr
                            changed = True
                        elif new_count == 0:
                            # all gone, remove this rr
                            # del rr['c']
                            # rr['u'] = instance - ONEMIN
                            if '+' in self.item_hsh and self.item_hsh:
                                self.item_hsh['r'][i] = {}
                                changed = True
                            else:
                                # no instances left
                                delete_item = True
                    elif instance > date_to_datetime(self.item_hsh['s']):
                        # no 'c', so we can change/add 'u'
                        rr['u'] = instance - ONESEC
                        self.item_hsh['r'][i] = rr
                        changed = True

                    else:
                        self.item_hsh['r'][i] = {}

                if changed:
                    # anything left of rr's?
                    rr_to_keep = []
                    for i in range(len(self.item_hsh['r'])):
                        rr = self.item_hsh['r'][i]
                        if rr:
                            rr_to_keep.append(rr)
                    if rr_to_keep:
                        self.item_hsh['r'] = rr_to_keep
                    else:
                        del self.item_hsh['r']

            if instance <= self.item_hsh['s']:
                if '+' in self.item_hsh and self.item_hsh['+']:
                    self.item_hsh['s'] = self.item_hsh['+'].pop(0)
                    changed = True
                else:
                    # nothing left
                    delete_item = True

            if changed:
                self.item_hsh['created'] = self.created
                self.item_hsh['modified'] = datetime.now().astimezone()
                # self.db.update(db_replace(self.item_hsh), doc_ids=[self.doc_id])
                self.do_update()
            elif delete_item:
                changed = self.delete_item(doc_id)

        elif which == '3':
            # all instance - delete item
            changed = self.delete_item(doc_id)

        return changed

    def finish_item(
        self,
        item_id: int,
        job_id: any,
        completed_datetime: datetime,
        due_datetime: datetime,
    ) -> bool:
        """Use the completed_datetime and the due_datetime to update the completion history and to remove the due_datetime from the instances that still need to be finished.

        Args:
            item_id (int): The database key for the item
            job_id (any): If this is a job, the key for the job
            completed_datetime (datetime): instance completed
            due_datetime (datetime): instance due

        Returns:
            bool: Success/Failure


        """

        # item_id and job_id should have come from dataview.hsh ok, maybe_finish and thus be valid

        # 23/5/29 FIXME with a repeating item either r or +, finishing an
        # instance other than the oldest requires besides adding the instance to @h either
        # deleting an @+ or adding an @- NOT changing @s!

        # What to do about history? Make history a hash with done keys and
        # lists of (done-due) or ZERO periods as values. Show competed on due
        # date with period.days in right hand column if 2nd component is not
        # ZERO. Why list of period values? done's resolution is one minute so
        # more than one completion might be attributed to the same minute.
        global active_tasks

        save_item = False
        self.item_hsh = self.db.get(doc_id=item_id)
        self.doc_id = item_id
        self.created = self.item_hsh['created']
        completion_entry = (
            Period(completed_datetime, due_datetime)
            if due_datetime
            else Period(completed_datetime, completed_datetime)
        )
        if job_id:
            j = 0
            for job in self.item_hsh['j']:
                if job['i'] == job_id:
                    self.item_hsh['j'][j]['f'] = completion_entry
                    save_item = True
                    break
                else:
                    j += 1
            ok, jbs, last = jobs(self.item_hsh['j'], self.item_hsh)
            if ok:
                self.item_hsh['j'] = jbs
                if last:
                    if nxt := get_next_due(
                        self.item_hsh, last, completion_entry.end
                    ):
                        if 'r' in self.item_hsh:
                            for i in range(len(self.item_hsh['r'])):
                                if (
                                    'c' in self.item_hsh['r'][i]
                                    and self.item_hsh['r'][i]['c'] > 0
                                ):
                                    self.item_hsh['r'][i]['c'] -= 1
                                    break
                        self.item_hsh['s'] = nxt
                        self.item_hsh.setdefault('h', []).append(
                            completion_entry
                        )
                        if self.doc_id in active_tasks:
                            del active_tasks[self.doc_id]

                    else:
                        self.item_hsh['f'] = completion_entry
                    save_item = True
                    # else:
                    #     # FIXME This is the undated task with jobs branch
                    #     save_item = True

        elif 's' in self.item_hsh:
            if '+' in self.item_hsh and due_datetime in self.item_hsh['+']:
                self.item_hsh['+'].remove(due_datetime)
                if not self.item_hsh['+']:
                    del self.item_hsh['+']
                self.item_hsh.setdefault('h', []).append(completion_entry)
                save_item = True
            elif 'r' in self.item_hsh:
                from_rrule = self.item_hsh.get('o', 'k') == 's'
                nxt = get_next_due(
                    self.item_hsh, completed_datetime, completion_entry.end, from_rrule
                )
                if nxt:
                    for i in range(len(self.item_hsh['r'])):
                        if (
                            'c' in self.item_hsh['r'][i]
                            and self.item_hsh['r'][i]['c'] > 0
                        ):
                            self.item_hsh['r'][i]['c'] -= 1
                            break
                    self.item_hsh['s'] = nxt
                    self.item_hsh.setdefault('h', []).append(completion_entry)
                else:
                    self.item_hsh['f'] = completion_entry

            elif '+' in self.item_hsh:
                tmp = [self.item_hsh['s']] + self.item_hsh['+']
                tmp = [date_to_datetime(x) for x in tmp]
                tmp.sort()
                due = tmp.pop(0)
                if tmp:
                    self.item_hsh['s'] = tmp.pop(0)
                if tmp:
                    self.item_hsh['+'] = tmp
                    self.item_hsh.setdefault('h', []).append(completion_entry)
                else:
                    del self.item_hsh['+']
                    self.item_hsh['f'] = completion_entry
            else:
                self.item_hsh['f'] = completion_entry
            save_item = True
        else:
            self.item_hsh['f'] = completion_entry
            save_item = True

        if save_item:
            num_finished = settings.get('num_finished', 0)

            if 'h' in self.item_hsh and num_finished:
                ok = not any(
                    'c' in rr or 'u' in rr for rr in self.item_hsh.get('r', {})
                )
                if ok:
                    sh = self.item_hsh['h']
                    sh.sort(key=sortprd)
                    self.item_hsh['h'] = sh[-num_finished:]

            self.item_hsh['created'] = self.created
            self.item_hsh['modified'] = datetime.now().astimezone()
            # self.db.update(db_replace(self.item_hsh), doc_ids=[self.doc_id])
            self.do_update()
            return True
        return False

    def record_timer(
        self, item_id, job_id=None, completed_datetime=None, elapsed_time=None
    ):
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
                    self.item_hsh['j'][j].setdefault('u', []).append(
                        [elapsed_time, completed_datetime]
                    )
                    save_item = True
                    break
                else:
                    j += 1
                    continue
        else:
            self.item_hsh.setdefault('u', []).append(
                [elapsed_time, completed_datetime]
            )
            save_item = True
        if save_item:
            self.item_hsh['created'] = self.created
            self.item_hsh['modified'] = datetime.now().astimezone()
            # self.db.update(db_replace(self.item_hsh), doc_ids=[self.doc_id])
            self.do_update()

    def cursor_changed(self, pos):
        # ((17, 24), ('e', '90m'))
        self.interval, self.active = active_from_pos(self.pos_hsh, pos)


    def text_changed(self, s, pos, modified=True):
        """ """
        # self.is_modified = modified
        # logger.debug(f"\n### starting text_changed with s: {s} and self.keyvals: {self.keyvals}")
        self.entry = s
        self.pos_hsh, keyvals = process_entry(s, self.settings)
        removed, changed = listdiff(self.keyvals, keyvals)
        # logger.debug(f" pos_hsh: {self.pos_hsh}; keyvals: {keyvals}\nremoved: {removed}; changed: {changed}")
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
            changed += [
                kv for kv in keyvals if kv[0] in ['s', 'ru', '+', '-']
            ]

        for kv in removed:
            if kv in self.object_hsh:
                del self.object_hsh[kv]
            if kv in self.askreply:
                del self.askreply[kv]
            if kv in keyvals:
                keyvals.remove(kv)
        self.keyvals = []
        for kv in [x for x in keyvals if x not in removed]:
            # logger.debug(f"updating kv: {kv}")
            self.update_keyval(kv)
            self.keyvals.append(kv)
        # logger.debug(f"### leaving text_changed with self.keyvals: {self.keyvals}\n")

    def update_keyval(self, kv):
        """
        TODO: add return status
        """
        key, val = kv
        # logger.debug(f"starting update_keyval with self.keyvals: {self.keyvals}")

        condition = 'f' in key

        # logger.debug(f"checking kv: {kv}")
        if key in self.keys:
            # logger.debug(f"found kv: {kv}")
            a, r, do = self.keys[key]
            ask = a
            msg = self.check_allowed(key)
            # logger.debug(f"got msg: {msg} when checking {kv} allowed")
            if msg:
                obj = None
                reply = msg
            else:   # only do this for allowed keys
                msg = self.check_requires(key)
                # logger.debug(f"got msg: {msg} checking required for {key}")
                if msg:
                    # logger.debug(f"failed required, self: {self}")
                    obj = None
                    reply = msg
                else:
                    # call the appropriate do for the key
                    obj, rep = do(val)
                    reply = rep if rep else r
                    # logger.debug(f"got obj: {obj}, rep: {rep} from {val}")
                    if obj is not None:
                        self.object_hsh[kv] = obj
                        # logger.debug(f"added {kv[0]}: {obj} to obj_hsh: {self.object_hsh}")
                        # self.item_hsh[kv[0]] = obj
                    else:
                        if kv in self.object_hsh:
                            del self.object_hsh[kv]
            self.askreply[kv] = (ask, reply)
        else:
            display_key = f'@{key}' if len(key) == 1 else f'&{key[-1]}'
            self.askreply[kv] = (
                'unrecognized key',
                f'{display_key} is invalid',
            )


    def check_item_hsh(self):
        created = self.item_hsh.get('created', None)
        self.item_hsh = {'created': created}
        cur_hsh = {}
        cur_key = None
        msg = []
        for pos, (k, v) in self.pos_hsh.items():
            obj = self.object_hsh.get((k, v))
            if obj is None:
                msg.append(f'bad entry for {k}: {v}')
                return msg
                # continue
            elif k in ['a', 'u', 'n', 't', 'k', 'K']:
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
                    # FIXME
                    self.item_hsh['f'] = last
            else:
                msg.extend(res)
        if self.item_hsh.get('z', None) not in [None, 'float']:
            del self.item_hsh['z']
        if msg:
            msg = '\n'.join(msg)
        return msg

    def update_item_hsh(self, check_links=True):
        msg = self.check_item_hsh()

        if msg:
            logger.error(msg)

        if 'K' in self.item_hsh:
            doc_ids = get_konnections(self.item_hsh)
            konnections = self.item_hsh.get('k', [])
            konnections.extend(doc_ids)
            self.item_hsh['k'] = konnections
            del self.item_hsh['K']

        if check_links:
            # make sure the doc_id refers to an actual document
            links = self.item_hsh.get('k', [])
            self.item_hsh['k'] = [
                x for x in links if self.db.contains(doc_id=x)
            ]


        if self.is_modified and not msg:
            now = datetime.now().astimezone()
            if self.is_new:
                # creating a new item or editing a copy of an existing item
                self.item_hsh['created'] = now
                if self.doc_id is None:
                    self.doc_id = self.do_insert()
                else:
                    self.do_update()
            else:
                # editing an existing item
                if 'k' in self.item_hsh and self.doc_id in self.item_hsh['k']:
                    # remove self referential konnections
                    self.item_hsh['k'].remove(self.doc_id)
                self.item_hsh['modified'] = now
                self.do_update()

    def check_requires(self, key):
        """
        Check that key has the prerequisite entries.
        if key in requires, check that each key in requires[k] has a corresponding key, val in keyvals: [(k, v), (k, v), ...]
        """
        # logger.debug(f"self.keyvals: {self.keyvals}")
        missing = []
        if key in requires:
            cur_keys = [k for (k, v) in self.keyvals]
            # logger.debug(f"checking cur_keys {cur_keys} for required key {key}")
            missing = [f'@{k[0]}' for k in requires[key] if k not in cur_keys]

        if missing:
            display_key = (
                f'@{key[0]}'
                if len(key) == 1 or key in ['rr', 'jj']
                else f'&{key[-1]}'
            )
            return (
                f"Required for {display_key} but missing: {', '.join(missing)}"
            )
        else:
            return ''

    def check_allowed(self, key):
        """
        Check that key is allowed for the given item type or @-key.
        """
        if not self.item_hsh:
            return
        if key in ['?', 'r?', 'j?', 'itemtype', 'summary']:
            return ''
        if key not in self.keys:
            if len(key) > 1:
                msg = f'&{key[1]} is invalid with @{key[0]}'
            else:
                msg = f'@{key} is invalid'
            return msg
        itemtype = self.item_hsh.get('itemtype', None)
        if itemtype:
            if key not in allowed[itemtype]:
                display_key = f'@{key}' if len(key) == 1 else f'&{key[-1]}'
                return f'{display_key} is not allowed for itemtype {itemtype} ({type_keys[itemtype]})'


            numuses = {}
            duplicates = []
            for k, v in self.keyvals:
                numuses.setdefault(k, 0)
                numuses[k] += 1
            duplicates = [
                k for (k, v) in numuses.items() if v > 1 and k not in [
                    'a', 'u', 't', 'k', 'K', 'jj', 'rr', 'ji', 'js', 'jb', 'jp', 'ja', 'jd', 'je', 'jf', 'jl', 'jm', 'ju']
                ]
            if key in duplicates:
                display_key = f'@{key}' if len(key) == 1 else f'&{key[-1]}'
                return f'{display_key} has already been entered'
            else:
                return ''
        else:
            return 'missing itemtype'

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
            already_entered = [
                k
                for (k, v) in self.keyvals
                if len(k) == 1 and k not in ['a', 'u', 't', 'k', 'K']
            ]
            require = [
                f'@{k}_({v[0]})'
                for k, v in self.keys.items()
                if (
                    k in required[itemtype]
                    and k != '?'
                    and k not in already_entered
                )
            ]
            # allow rr to be entered as r and jj as j
            avail = [
                x
                for x in allowed[itemtype]
                if len(x) == 1 or x in ['rr', 'jj']
            ]
            allow = [
                f'@{k[0]}_({v[0]})'
                for k, v in self.keys.items()
                if (k in avail and k not in already_entered)
            ]
            allow.sort()
            prompt = ''
            if require:
                prompt += wrap(f"required: {', '.join(require)}", 2) + '\n'
            if allow:
                prompt += wrap(f"available: {', '.join(allow)}", 2)
            rep = prompt.replace('_', ' ')
        else:
            rep = 'The type character must be entered before any @-keys'

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
        keys = [
            f'&{k[1]}_({v[0]})'
            for k, v in self.keys.items()
            if k.startswith('r') and k[1] not in 'r?'
        ]
        rep = wrap('repetition &-keys: ' + ', '.join(keys), 4, 60).replace(
            '_', ' '
        )

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
        keys = [
            f'&{k[1]}_({v[0]})'
            for k, v in self.keys.items()
            if k.startswith('j') and k[1] not in 'j?'
        ]
        rep = wrap('job &-keys: ' + ', '.join(keys), 4, 60).replace('_', ' ')

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
            rep = f'Choose a {r}'
        elif arg in type_keys:
            obj = arg
            rep = f'{arg} ({type_keys[arg]})'
            self.item_hsh['itemtype'] = obj
        else:
            obj = None
            rep = f"'{arg}' is invalid. Choose a {r}"
            self.item_hsh['itemtype'] = ''
        return obj, rep

    def do_summary(self, arg):
        if not self.item_hsh['itemtype']:
            return None, 'a valid itemtype must be provided'
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
        (True, DateTime(2019, 1, 3, 10, 0, 0, tzinfo=ZoneInfo('America/New_York')))
        >>> until('whenever')
        (False, 'Include repetitions falling on or before this datetime.')
        """
        obj = None
        tz = self.item_hsh.get('z', None)
        ok, res, z = parse_datetime(arg, tz)
        if ok:
            if isinstance(res, date) and not isinstance(res, datetime):
                return obj, 'a datetime is required'
            obj = res
            rep = (
                f'local datetime: {format_datetime(obj)[1]}'
                if ok == 'aware'
                else format_datetime(obj)[1]
            )
        else:
            rep = 'Include repetitions falling on or before this datetime'
        return obj, rep

    def do_datetime(self, arg):
        """
        >>> item = Item("")
        >>> item.do_datetime('fr')
        (None, "'fr' is incomplete or invalid")
        >>> item.do_datetime('2019-01-25')
        (Date(2019, 1, 25), 'Fri Jan 25 2019')
        >>> item.do_datetime('2019-01-25 2p')
        (DateTime(2019, 1, 25, 14, 0, 0, tzinfo=ZoneInfo('America/New_York')), 'Fri Jan 25 2019 2:00pm EST')
        """
        obj = None
        tz = self.item_hsh.get('z', None)
        ok, res, z = parse_datetime(arg, tz)
        if ok:
            obj = res
            rep = (
                f'local datetime: {format_datetime(obj)[1]}'
                if ok == 'aware'
                else format_datetime(obj)[1]
            )
        else:
            rep = res
        return obj, rep

    def do_datetimes(self, args):
        """
        >>> item = Item("")
        >>> item.do_datetimes('2019-1-25 2p, 2019-1-30 4p')
        ([DateTime(2019, 1, 25, 14, 0, 0, tzinfo=ZoneInfo('America/New_York')), DateTime(2019, 1, 30, 16, 0, 0, tzinfo=ZoneInfo('America/New_York'))], 'datetimes: 2019-01-25 2:00pm, 2019-01-30 4:00pm')
        >>> print(item.do_datetimes('2019-1-25 2p, 2019-1-30 4p, 2019-2-29 8a')[1])
        datetimes: 2019-01-25 2:00pm, 2019-01-30 4:00pm
        incomplete or invalid datetimes:  2019-2-29 8a
        """
        rep = args
        obj = None
        tz = self.item_hsh.get('z', None)
        if not isinstance(args, list):
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
        rep = (
            f"local datetimes: {', '.join(rep)}"
            if (tz is not None and tz != 'float')
            else f"datetimes: {', '.join(rep)}"
        )
        if bad:
            rep += f"\nincomplete or invalid datetimes:  {', '.join(bad)}"
        return obj, rep

    def do_completions(self, args):
        tz = self.item_hsh.get('z', None)
        args = [x.strip() for x in args.split(',')]
        all_ok = True
        obj_lst = []
        rep_lst = []
        bad_lst = []
        completions = []
        # arg_lst will be a list of periods
        for arg in args:
            if not arg:
                continue
            obj, rep = self.do_completion(arg)
            if isinstance(obj, Period):
                obj_lst.append(obj)
                rep_lst.append(rep)
            else:
                all_ok = False
                bad_lst.append(arg)

        obj = obj_lst if all_ok else None
        rep = f"periods: {', '.join(rep_lst)}"
        if bad_lst:
            rep += f"\nincomplete or invalid completions: {', '.join(bad_lst)}"

        return obj, rep

    def do_completion(self, arg):
        # obj = None
        tz = self.item_hsh.get('z', None)
        args = [x.strip() for x in arg.split('->')]
        obj, rep = self.do_datetimes(args)
        parts = [date_to_datetime(x) for x in obj] if obj else []
        if len(parts) > 1:
            start_dt, end_dt = parts[:2]
            obj = Period(start_dt, end_dt)
            rep = f'{format_datetime(start_dt, short=True)[1]} -> {format_datetime(end_dt, short=True)[1]}'
        else:
            obj = None
            rep = f'\nincomplete or invalid completion: {arg}'
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
            rep = ''
        else:
            try:
                ZoneInfo(arg)
                obj = rep = arg
                self.item_hsh['z'] = obj
                rep = f'timezone: {obj}'
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


def completion_evaluator(s):
    return f'got {s}'


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
    wkday_fmt = '%a %-d %b' if settings['dayfirst'] else '%a %b %-d'
    datetime_fmt = (
        f'{wkday_fmt} %Y %-I:%M%p %Z' if ampm else f'{wkday_fmt} %Y %H:%M %Z'
    )
    m = date_calc_regex.match(s)
    if not m:
        return f'Could not parse "{s}"'
    x, pm, y = [z.strip() for z in m.groups()]
    xz = ''
    nx = timezone_regex.match(x)
    if nx:
        x, xz = nx.groups()
    yz = ''
    ny = timezone_regex.match(y)
    if ny:
        y, yz = ny.groups()
    try:
        if xz:
            ok, dt_x, z = parse_datetime(x, xz)
        else:
            ok, dt_x, z = parse_datetime(x)
        if not ok:
            return f"error: could not parse '{x}'"
        dt_x = date_to_datetime(dt_x)
        pmy = f'{pm}{y}'
        if period_string_regex.match(y):
            ok, dur = parse_duration(pmy)
            if not ok:
                return f"error: could not parse '{y}'"
            if yz:
                dt = (dt_x + dur).astimezone(ZoneInfo(yz))
            else:
                dt = (dt_x + dur).astimezone()
            return dt.strftime(datetime_fmt)
        else:
            if yz:
                ok, dt_y, z = parse_datetime(y, yz)
            else:
                ok, dt_y, z = parse_datetime(y)
            if not ok:
                return f"error: could not parse '{y}'"
            dt_y = date_to_datetime(dt_y)
            if pm == '-':
                return duration_in_words(dt_x - dt_y)
            else:
                return 'error: datetimes cannot be added'
    except ValueError:
        return f'error parsing "{s}"'


def duration_in_words(obj, short=False):
    """
    Return string representing weeks, days, hours and minutes. Drop any remaining seconds.
    >>> td = timedelta(weeks=1, days=2, hours=3, minutes=27)
    >>> format_duration(td)
    '1 week 2 days 3 hours 27 minutes'
    """
    if not isinstance(obj, timedelta):
        return None
    try:
        until = []
        total_seconds = int(obj.total_seconds())
        weeks = days = hours = minutes = seconds = 0
        if total_seconds:
            sign = '' if total_seconds > 0 else '- '
            total_seconds = abs(total_seconds)
            seconds = total_seconds % 60
            minutes = total_seconds // 60
            if minutes >= 60:
                hours = minutes // 60
                minutes = minutes % 60
            if hours >= 24:
                days = hours // 24
                hours = hours % 24
            if days >= 7:
                weeks = days // 7
                days = days % 7
        if weeks:
            if weeks > 1:
                until.append(f'{sign}{weeks} weeks')
            else:
                until.append(f'{sign}{weeks} week')
        if days:
            if days > 1:
                until.append(f'{sign}{days} days')
            else:
                until.append(f'{sign}{days} day')
        if hours:
            if hours > 1:
                until.append(f'{sign}{hours} hours')
            else:
                until.append(f'{sign}{hours} hour')
        if minutes:
            if minutes > 1:
                until.append(f'{sign}{minutes} minutes')
            else:
                until.append(f'{sign}{minutes} minute')
        if seconds:
            if seconds > 1:
                until.append(f'{sign}{seconds} seconds')
            else:
                until.append(f'{sign}{seconds} second')
        if not until:
            until.append('zero minutes')
        ret = ' '.join(until[:2]) if short else ' '.join(until)
        return ret
    except Exception as e:
        return None


def parse_datetime(s: str, z: str = None):
    """
    's' will have the format 'datetime string' Return a 'date' object if the parsed datetime is exactly midnight. Otherwise return a naive datetime object if 'z == float' or an aware datetime object converting to UTC using the local timezone if z == None and using the timezone specified in z otherwise.
    >>> dt = parse_datetime("2015-10-15 2p")
    >>> dt[1]
    DateTime(2015, 10, 15, 14, 0, 0, tzinfo=ZoneInfo('America/New_York'))
    >>> dt = parse_datetime("2015-10-15")
    >>> dt[1]
    Date(2015, 10, 15)

    To get a datetime for midnight, schedule for 1 second later - the second will be dropped from the hours and minutes datetime:
    >>> dt = parse_datetime("2015-10-15 00:00:01")
    >>> dt[1]
    DateTime(2015, 10, 15, 0, 0, 1, tzinfo=ZoneInfo('America/New_York'))
    >>> dt = parse_datetime("2015-10-15 2p", "float")
    >>> dt[1]
    DateTime(2015, 10, 15, 14, 0, 0)
    >>> dt[1].tzinfo == None
    True
    >>> dt = parse_datetime("2015-10-15 2p", "US/Pacific")
    >>> dt
    ('aware', DateTime(2015, 10, 15, 21, 0, 0, tzinfo=ZoneInfo('UTC')), 'US/Pacific')
    >>> dt[1].tzinfo
    ZoneInfo('UTC')
    >>> dt = parse_datetime("2019-02-01 12:30a", "Europe/Paris")
    >>> dt
    ('aware', DateTime(2019, 1, 31, 23, 30, 0, tzinfo=ZoneInfo('UTC')), 'Europe/Paris')
    >>> dt = parse_datetime("2019-02-01 12:30a", "UTC")
    >>> dt
    ('aware', DateTime(2019, 2, 1, 0, 30, 0, tzinfo=ZoneInfo('UTC')), 'UTC')
    >>> dt = parse_datetime("2019-03-24 5:00PM")
    >>> dt
    ('local', DateTime(2019, 3, 24, 17, 0, 0, tzinfo=ZoneInfo('America/New_York')), None)
    """

    filterwarnings('error')
    if z in ['local', None]:
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
            return True, datetime.now().astimezone(), z

        dt_str = ''
        dur_str = ''
        dt_and_dur_regex = re.compile(r'^(.+)\s+([+-].+)?$')
        days_or_more_regex = re.compile(r'[dwM]')   # FIXME: USED?
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
            dt = (
                datetime.now().astimezone()
                if dt_str.strip() == 'now'
                else parse(dt_str, tzinfo=tzinfo)
            )
        else:
            dt = datetime.now().astimezone()
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
            return 'date', res.astimezone(), z
        elif ok == 'float':
            return ok, res.astimezone(None), z
        else:
            return ok, res.astimezone(), z


def timestamp(arg):
    """
    Fuzzy parse a datetime string and return the YYYYMMDDTHHMM formatted version.
    >>> timestamp("6/16/16 4p")
    (True, DateTime(2016, 6, 16, 16, 0, 0, tzinfo=ZoneInfo('UTC')))
    >>> timestamp("13/16/16 2p")
    (False, 'invalid time-stamp: 13/16/16 2p')
    """
    if isinstance(arg, datetime):
        return True, arg
    elif isinstance(arg, date):
        return True, date_to_datetime(arg)
    elif isinstance(arg, Period):
        return True, arg
    try:
        res = parse(arg)
    except:
        return False, 'invalid time-stamp: {}'.format(arg)
    return True, res


def plain_datetime(obj):
    return format_datetime(obj, short=True)


def format_time(obj: datetime)->str:
    obj = date_to_datetime(obj)
    ampm = settings.get('ampm', True)
    (hours, suffix) = ('%-I:', '%p') if ampm else ('%H:', '')
    seconds = ':%S' if obj.second else ''
    hourminutes = obj.strftime(f"{hours}%M{seconds}{suffix}").rstrip('M').lower()
    return True, hourminutes


def fivechar_datetime(obj):
    """
    Return a 5 character representation of datetime obj using
    the format XX<sep>YY. Examples when today is 2020/10/15
    1:15pm today -> 13:15
    today -> 00:00
    2p on Nov 7 of this year -> 11/07
    11a on Jan 17 of 2012 -> 12.01
    """
    now = datetime.now().astimezone()

    md_fmt = '%d/%m' if settings['dayfirst'] else '%m/%d'
    ym_fmt = '%y.%m' if settings['yearfirst'] else '%m.%y'

    if obj.year == now.year:
        if obj.month == now.month:
            if obj.day == now.day:
                return obj.strftime('%H:%M')
            else:
                return obj.strftime(md_fmt)
        else:
            return obj.strftime(md_fmt)
    else:
        return obj.strftime(ym_fmt)


def format_date(obj, year=True, separator='/', omit_zeros=True):
    dayfirst = settings.get('dayfirst', False)
    yearfirst = settings.get('yearfirst', False)
    # md = ('%-d', '%-m') if dayfirst else ('%-m', '%-d')
    if omit_zeros:
        md = f"%-d{separator}%-m" if dayfirst else f"%-m{separator}%-d"
    else:
        md = f"%d{separator}%m" if dayfirst else f"%m{separator}%d"
    if year:
        # date_fmt = f'%Y/{md}' if yearfirst else f'{md}/%Y'
        # ymd = ('%Y',) + md if yearfirst else md + ('%Y',)
        date_fmt = f"%Y{separator}{md}" if yearfirst else f"{md}{separator}%Y"
    else:
        date_fmt = md


    if type(obj) != date and type(obj) != datetime:
        return False, ''
    else:
        return True, obj.strftime(date_fmt)


def format_statustime(obj):
    width = shutil.get_terminal_size()[0]
    ampm = settings.get('ampm', True)
    dayfirst = settings.get('dayfirst', False)
    yearfirst = settings.get('yearfirst', False)
    month = obj.strftime('%b')
    day = obj.strftime('%-d')
    hourminutes = (
        obj.strftime('%-I:%M%p').rstrip('M').lower()
        if ampm
        else obj.strftime('%H:%M')
    )
    if width < 60:
        weekday = ''
        monthday = ''
    else:
        weekday = f' {obj.strftime("%a")}'
        monthday = f' {day} {month}' if dayfirst else f' {month} {day}'
    return f'{hourminutes}{weekday}{monthday}'


def format_wkday(obj):
    dayfirst = settings.get('dayfirst', False)
    yearfirst = settings.get('yearfirst', False)
    month = obj.strftime('%b')
    day = obj.strftime('%-d')
    weekday = obj.strftime('%a')
    monthday = f'{day} {month}' if dayfirst else f'{month} {day}'
    return f'{weekday} {monthday}'


def format_datetime(obj, short=False):
    """
    >>> format_datetime(parse_datetime("20160710T1730")[1])
    , needs(True, 'Sun Jul 10 2016 5:30pm EDT')
    >>> format_datetime(parse_datetime("2015-07-10 5:30p", "float")[1])
    (True, 'Fri Jul 10 2015 5:30pm')
    >>> format_datetime(parse_datetime("20160710")[1])
    (True, 'Sun Jul 10 2016')
    >>> format_datetime(parse_datetime("2015-07-10", "float")[1])
    (True, 'Fri Jul 10 2015')
    >>> format_datetime("20160710T1730")
    (False, 'The argument must be a date or datetime.')
    >>> format_datetime(parse_datetime("2019-02-01 12:30a", "Europe/Paris")[1])
    (True, 'Thu Jan 31 2019 6:30pm EST')
    >>> format_datetime(parse_datetime("2019-01-31 11:30p", "Europe/Paris")[1])
    (True, 'Thu Jan 31 2019 5:30pm EST')
    """
    ampm = settings.get('ampm', True)
    dayfirst = settings.get('dayfirst', False)
    yearfirst = settings.get('yearfirst', False)
    md = f'%-d/%-m' if dayfirst else f'%-m/%-d'
    if short:
        md = '%-d/%-m' if dayfirst else '%-m/%-d'
        date_fmt = f'%Y/{md}' if yearfirst else f'{md}/%Y'
    else:
        md = '%a %-d %b' if dayfirst else '%a %b %-d'
        date_fmt = f'{md}, %Y' if yearfirst else f'{md} %Y'

    obj = date_to_datetime(obj)

    if obj.second == 0:
        time_fmt = '%-I:%M%p' if ampm else '%H:%M'
    else:
        time_fmt = '%-I:%M:%S%p' if ampm else '%H:%M:%S'

    if type(obj) == date:
        return True, obj.strftime(date_fmt)

    if not isinstance(obj, datetime):
        return False, f'Error: {e}'

    # we want all-day events to display as dates
    if (obj.hour, obj.minute, obj.second, obj.microsecond) == (0, 0, 0, 0):
        # treat as date
        return True, obj.strftime(date_fmt)

    if obj.strftime('Z') == '':
        # naive datetime
        if (obj.hour, obj.minute, obj.second, obj.microsecond) == (0, 0, 0, 0):
            # treat as date
            return True, obj.strftime(date_fmt)
    else:
        # aware datetime
        obj = obj.astimezone()
        if not short:
            time_fmt += ' %Z'
    res = obj.strftime(f'{date_fmt} {time_fmt}')
    if ampm:
        res = res.rstrip('M').lower()
    return True, res


def format_relative_time(obj: datetime)->str:
    now = datetime.now().astimezone()
    if obj.date() != now.date():
        return format_duration(now - obj, short=True)[1:]
    else:
        return format_time(obj)[1]


def format_period(obj):
    if not isinstance(obj, Period):
        logger.error(f'error, expected Period but got: {obj}')
        return obj
    start = obj.start
    end = obj.end
    local_end = end.astimezone()
    if local_end.hour == 0 and local_end.minute == 0:
        # treat end as a date instead of a datetime
        local_end_str = format_date(local_end.date())[1]
    else:
        local_end_str = format_datetime(local_end, short=True)[1]
    return f'{format_datetime(start, short=True)[1]} -> {local_end_str}'


def format_period_list(obj_lst):
    if not isinstance(obj_lst, list):
        obj_lst = [obj_lst]
    return ', '.join([format_period(x) for x in obj_lst])


def format_datetime_list(obj_lst):
    return ', '.join([format_datetime(x)[1] for x in obj_lst])


def plain_datetime_list(obj_lst):
    return ', '.join([plain_datetime(x)[1] for x in obj_lst])


def format_hours_and_tenths(obj):
    """
    Convert a timedelta object into hours and tenths of an hour rounding up to the nearest tenth.
    """
    if not isinstance(obj, timedelta):
        return None
    UT_MIN = settings.get('usedtime_minutes', 1)
    if UT_MIN <= 1:
        # hours, minutes and seconds if not rounded up
        return format_duration(obj, short=True)
    seconds = int(obj.total_seconds())
    minutes = seconds // 60
    if seconds % 60:
        minutes += 1
    if minutes:
        return f'{math.ceil(minutes/UT_MIN)/(60/UT_MIN)}h'
    else:
        return '0.0h'


def dt2minutes(obj):
    return obj.hour * 60 + obj.minute


def datetimes2busy(dta, dtb):
    # a for after, b for before
    ret = []
    beg_dt = dtb
    count = 0
    while beg_dt < dta and count < 5:
        count += 1
        by, bw, begin_day = beg_dt.isocalendar()
        begin_week = (by, bw)
        beg_min = dt2minutes(beg_dt)
        if beg_dt.date() < dta.date():
            # midnight - 1 minute
            end_min = 1439
        else:
            # when dta ends
            end_min = dt2minutes(dta)
        ret.append((begin_week, begin_day, (beg_min, end_min)))
        beg_dt = beg_dt + timedelta(minutes=end_min - beg_min + 1)
    return ret


def round_minutes(obj):

    # round up
    if isinstance(obj, timedelta) and int(obj.total_seconds()) % 60:
        return obj + timedelta(seconds=60 - int(obj.total_seconds()) % 60)
    else:
        return obj


def usedminutes2bar(minutes):
    # leave room for indent and weekday
    # TODO: fix this?
    if not minutes:
        return '', ''
    width = shutil.get_terminal_size()[0] - 3
    chars = width - 8
    # goal in hours to minutes
    used_minutes = int(minutes)
    used_fmt = (
        format_hours_and_tenths(used_minutes * ONEMIN)
        .ljust(6, ' ')
        .lstrip('+')
    )
    if usedtime_hours:
        goal_minutes = int(usedtime_hours) * 60
        numchars = math.ceil((used_minutes / goal_minutes) / (1 / chars))
        if numchars <= chars:
            bar = f'{numchars*BUSY}'
        else:
            bar = f'{(chars-6)*BUSY} {BUSY}'
        return used_fmt, bar
    else:
        return used_fmt, ''


def format_duration(obj, short=False):
    """
    if short report only biggest 2, else all
    >>> td = timedelta(weeks=1, days=2, hours=3, minutes=27)
    >>> format_duration(td)
    '1w2d3h27m'
    """
    # if not (isinstance(obj, Period) or isinstance(obj, timedelta)):
    if not isinstance(obj, timedelta):
        return None
    total_seconds = int(obj.total_seconds())
    if total_seconds == 0:
        return ' 0m'
    sign = '+' if total_seconds > 0 else '-'
    total_seconds = abs(total_seconds)
    try:
        until = []
        weeks = days = hours = minutes = 0
        if total_seconds:
            seconds = total_seconds % 60
            minutes = total_seconds // 60
            if minutes >= 60:
                hours = minutes // 60
                minutes = minutes % 60
            if hours >= 24:
                days = hours // 24
                hours = hours % 24
            if days >= 7:
                weeks = days // 7
                days = days % 7
        if weeks:
            until.append(f'{weeks}w')
        if days:
            until.append(f'{days}d')
        if hours:
            until.append(f'{hours}h')
        if minutes:
            until.append(f'{minutes}m')
        if seconds:
            until.append(f'{seconds}s')
        if not until:
            until.append('0m')
        ret = ''.join(until[:2]) if short else ''.join(until)
        return sign + ret
    except Exception as e:
        logger.error(f'{obj}: {e}')
        return ''

def format_completion(done: date|datetime, due: date|datetime)->str:
    for x in [done, due]:
        if not isinstance(x, datetime) and not isinstance(x, date):
            logger.error(f"in format_completion with {done = } and {due = }.  {x = } is neither a date nor a datetime instance.")
            raise TypeError(f"{x = } is neither a date nor a datetime instance")

    due = date_to_datetime(due).astimezone()
    done = date_to_datetime(done).astimezone()
    if due.hour == 0 and due.minute == 0:
        # allday task - regard it as due at zero hours on the next day
        due = due + timedelta(days=1)
    return format_duration(due - done, short=True)


def status_duration(obj):
    """
    hours, minutes and tenths of minutes for display in the status bar
    """
    if not (isinstance(obj, timedelta) or isinstance(obj, Period)):
        raise ValueError(f"{obj = } is neither a timedelta nor a period instance.")
    td = obj if isinstance(obj, timedelta) else obj.diff
    return format_duration(td)[1:]

    # total_seconds = int(td.total_seconds())
    # if total_seconds < 60:
    #     return '0m'
    # hours = total_seconds // (60 * 60)
    # minutes = (total_seconds % (60 * 60)) // 60
    # seconds = total_seconds - 60 * 60 * hours - 60 * minutes
    # until = []
    # if hours > 0:
    #     until.append(f'{hours}h')
    # # if seconds and refresh_interval == 6:
    # #     until.append(f'{minutes}.{seconds//6}m')
    # if minutes:
    #     until.append(f'{minutes}m')
    #
    # return ''.join(until)


def fmt_dur(obj):
    """
    Return string representing weeks, days, hours and minutes. Drop any remaining seconds.
    >>> td = timedelta(weeks=1, days=2, hours=3, minutes=27)
    >>> format_duration(td)
    '1w2d3h27m'
    """
    if not isinstance(obj, timedelta):
        return None
    try:
        until = []
        seconds = int(obj.total_seconds())
        weeks = days = hours = minutes = 0
        if seconds:
            minutes = seconds // 60
            if minutes >= 60:
                hours = minutes // 60
                minutes = minutes % 60
            if hours >= 24:
                days = hours // 24
                hours = hours % 24
            if days >= 7:
                weeks = days // 7
                days = days % 7
        if weeks:
            until.append(f'{weeks}w')
        if days:
            until.append(f'{days}d')
        if hours:
            until.append(f'{hours}h')
        if minutes:
            until.append(f'{minutes}m')
        if not until:
            until.append('0m')
        ret = ''.join(until)
        return ''.join(until)
    except Exception as e:
        return None


def fmt_period(obj):
    if not isinstance(obj, Period):
        return 'not a period'
    start = obj.start
    end = obj.end
    return format_duration(end-start, short=True)


def format_duration_list(obj_lst):
    try:
        return ', '.join([format_duration(x) for x in obj_lst])
    except Exception as e:
        logger.error(f'{obj_lst}: {e}')


period_regex = re.compile(r'(([+-]?)(\d+)([wdhms]))+?')
expanded_period_regex = re.compile(
    r'(([+-]?)(\d+)\s(week|day|hour|minute|second)s?)+?'
)
relative_regex = re.compile(r'(([+-])(\d+)([wdhmys]))+?')
threeday_regex = re.compile(
    r'([+-]?[1234])(MON|TUE|WED|THU|FRI|SAT|SUN)', re.IGNORECASE
)
anniversary_regex = re.compile(r'!(\d{4})!')


def parse_durations(s):
    periods = [x.strip() for x in s.split('+')]
    total = ZERO
    bad = []
    for d in periods:
        ok, p = parse_duration(d)
        if ok:
            total += p
        else:
            bad.append(d)
    if bad:
        return False, bad
    else:
        return True, total


def parse_duration(s: str)->timedelta:
    """\
    Take a period string and return a corresponding timedelta.
    Examples:
        parse_duration('-2w3d4h5m')= Duration(weeks=-2,days=3,hours=4,minutes=5)
        parse_duration('1h30m') = Duration(hours=1, minutes=30)
        parse_duration('-10m') = Duration(minutes=10)
    where:
        y: years
        w: weeks
        d: days
        h: hours
        m: minutes
        s: seconds

    >>> 3*60*60+5*60
    11100
    >>> parse_duration("2d-3h5m")[1]
    Duration(days=1, hours=21, minutes=5)
    >>> datetime(2015, 10, 15, 9, 0, tz='local') + parse_duration("-25m")[1]
    DateTime(2015, 10, 15, 8, 35, 0, tzinfo=ZoneInfo('America/New_York'))
    >>> datetime(2015, 10, 15, 9, 0) + parse_duration("1d")[1]
    DateTime(2015, 10, 16, 9, 0, 0, tzinfo=ZoneInfo('UTC'))
    >>> datetime(2015, 10, 15, 9, 0) + parse_duration("1w-2d+3h")[1]
    DateTime(2015, 10, 20, 12, 0, 0, tzinfo=ZoneInfo('UTC'))
    """

    knms = {
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
        's': 'seconds',
        'second': 'second',
        'seconds': 'seconds',
    }

    kwds = {
        'weeks': 0,
        'days': 0,
        'hours': 0,
        'minutes': 0,
        'seconds': 0,
    }

    m = period_regex.findall(str(s))
    if not m:
        m = expanded_period_regex.findall(str(s))
        if not m:
            return False, f"Invalid period string '{s}'"
    for g in m:
        if g[3] not in knms:
            return False, f'invalid period argument: {g[3]}'

        num = -int(g[2]) if g[1] == '-' else int(g[2])
        if num:
            kwds[knms[g[3]]] = num
    td = timedelta(**kwds)

    return True, td


class NDict(dict):
    """
    Constructed from rows of (path, values) tuples. The path will be split using 'split_char' to produce the nodes leading to 'values'. The last element in values is presumed to be the 'id' of the item that generated the row.
    """

    tab = 1

    def __init__(self, split_char='/', compact=False, width=None):
        self.compact = compact
        self.width = width if width else shutil.get_terminal_size()[0] - 3
        self.split_char = split_char
        self.row = 0
        self.level = 0
        self.show_leaves = True
        self.row2id = {}
        self.output = []
        self.flag_len = 4   # gkptp

    def __missing__(self, key):
        self[key] = NDict(compact=self.compact, width=self.width)
        return self[key]

    def as_dict(self):
        return self

    def leaf_detail(self, detail, depth):
        if not self.show_details:
            return []
        dindent = NDict.tab * (depth + 1) * ' '
        paragraphs = detail.split('\n')
        ret = []
        for para in paragraphs:
            ret.extend(
                textwrap.fill(
                    para,
                    initial_indent=dindent,
                    subsequent_indent=dindent,
                    width=self.width - NDict.tab * (depth - 1),
                ).split('\n')
            )
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
            keys_left = keys[j + 1 :]
            if not keys_left:
                try:
                    self.setdefault(key, []).append(values)
                except Exception as e:
                    logger.warning(
                        f'error adding key: {key}, values: {values}\n self: {self}; e: {repr(e)}'
                    )
            if isinstance(self[key], dict):
                self = self[key]
            elif keys_left:
                self.setdefault('/'.join(keys[j:]), []).append(values)
                break

    def as_tree(self, t={}, depth=0):
        """return an indented tree"""
        for k in t.keys():
            indent = NDict.tab * depth * ' '
            # replace any newlines in the title with spaces
            K = re.sub(' *\n+ *', ' ', k)
            self.output.append(f'{indent}{K}')
            self.row += 1
            depth += 1
            if self.level and depth > self.level:
                depth -= 1
                continue

            if type(t[k]) == NDict:
                self.as_tree(t[k], depth)
            elif self.show_leaves:
                # we have a list of leaves
                for leaf in t[k]:
                    indent = NDict.tab * depth * ' '
                    l_indent = len(indent)
                    # replace any newlines in the summary with spaces
                    leaf[0] = re.sub(' *\n+ *', ' ', leaf[0])
                    leaf[1] = re.sub(' *\n+ *', ' ', leaf[1])
                    flags = leaf[2].strip()
                    # flags = " ❘" + flags + "❘" if flags else ""
                    flags = ' ' + flags if flags else ''
                    # rhc = leaf[3].strip()
                    rhc = leaf[3].rstrip()
                    rhc = f'{rhc}  ' if rhc else ''
                    summary_width = (
                        self.width - l_indent - 2 - len(flags) - len(rhc)
                    )
                    summary = truncate_string(leaf[1], summary_width)
                    if self.compact:
                        tmp = f'{indent}{leaf[0]} {rhc}{summary}{flags}'
                    else:
                        tmp = f'{indent}{leaf[0]} {rhc}{summary}{flags}'

                    self.output.append(tmp)
                    if leaf[0] not in [wrapbefore, wrapafter]:
                        self.row2id[self.row] = leaf[4]
                    self.row += 1
                    if len(leaf) > 5:
                        lines = self.leaf_detail(leaf[5], depth)
                        for line in lines:
                            self.output.append(line)
                            self.row += 1
            depth -= 1
        # return '\n'.join([x for x in self.output if x]), self.row2id
        return '\n'.join(self.output), self.row2id


class DataView(object):
    def __init__(self, etmdir):
        timer_database = TimeIt('***DATABASE***')
        self.active_item = None
        self.active_view = 'agenda'
        self.prior_view = 'agenda'
        self.current = []
        self.alerts = []
        self.row2id = []
        self.konnections_row2id = {}
        self.konnected_id2row = {}
        self.konnected_row = None
        self.last_id = 0
        self.id2relevant = {}
        self.wkday2busy_details = {}
        self.busy_row = 0
        self.link_list = []
        self.pinned_list = []
        self.repeat_list = []
        self.current_row = 0
        self.agenda_view = ''
        self.done_view = ''
        self.effort_view = ''
        self.busy_view = ''
        self.calendar_view = ''
        self.query_view = ''
        self.query_text = ''
        self.last_query = ''
        self.query_items = []
        self.query_mode = 'items table'
        self.report_view = ''
        self.report_text = ''
        self.active_str = ''
        self.inactive_str = ''
        self.report_items = []
        self.cal_locale = None
        self.history_view = ''
        self.cache = {}
        self.itemcache = {}
        self.current_hsh = {}
        self.used_summary = {}
        self.used_details = {}
        self.used_details2id = {}
        self.effort_details = {}
        self.currMonth()
        self.completions = []
        self.kompletions = {}
        self.konnections_from = {}
        self.konnections_to = {}
        self.konnected = []
        self.calculator_expression = ''

        # for repeating tasks with jobs - only one can be active
        # self.active_tasks = [] # ids of repeating tasks with jobs

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
            'e': 'effort',
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
        # self.is_showing_confirmation = False
        # self.is_showing_choice = False
        self.is_showing_entry = False
        self.hide_choice()
        self.hide_entry()
        self.entry_content = ''
        self.details_key_press = ''
        self.is_showing_query = False
        self.is_showing_help = False
        self.is_editing = False
        self.control_z_active = False
        self.dialog_active = False
        self.is_showing_items = True
        self.is_showing_konnections = False
        if needs_update:
            timer_update = TimeIt('***UPDATE***')
            self.update_datetimes_to_periods()
            timer_update.stop()
        self.get_completions()
        timer_konnections = TimeIt('***KONNECTIONS***')
        self.refreshKonnections()
        timer_konnections.stop()
        self.currYrWk()
        timer_relevant = TimeIt('***RELEVANT***')
        self.refreshRelevant()
        timer_relevant.stop()
        timer_current = TimeIt('***CURRENT***')
        self.refreshCurrent()
        timer_current.stop()
        timer_agenda = TimeIt('***AGENDA***')
        self.refreshAgenda()
        timer_agenda.stop()
        timer_archive = TimeIt('***ARCHIVE***')
        self.possible_archive()
        timer_archive.stop()
        self.currcal()
        timer_database.stop()

    def set_etmdir(self, etmdir):
        self.etmdir = etmdir
        self.backupdir = os.path.join(self.etmdir, 'backups')
        # need these files for backups
        self.dbfile = os.path.normpath(os.path.join(etmdir, 'etm.json'))
        self.cfgfile = os.path.normpath(os.path.join(etmdir, 'cfg.yaml'))
        self.settings = settings
        # if 'keep_current' in self.settings and self.settings['keep_current']:
        if (
            'keep_current' in self.settings
            and self.settings['keep_current'][0]
        ):
            # weeks is not zero
            self.mk_current = True
            self.mk_next = True
            self.currfile = os.path.normpath(
                os.path.join(etmdir, 'current.txt')
            )
            self.nextfile = os.path.normpath(os.path.join(etmdir, 'next.txt'))
        else:
            self.mk_current = False
            self.mk_next = False
            self.currfile = None
            self.nextfile = None

        if 'locale' in self.settings:
            locale_str = settings['locale']
            # locale_str should have the format "en_US"
            if locale_str:
                try:
                    locale.setlocale(locale.LC_ALL, f'{locale_str}.UTF-8')
                    self.cal_locale = [locale_str, 'UTF-8']
                except:
                    logger.error(
                        f'could not set python locale to {locale_str}.UTF-8'
                    )
                else:
                    logger.info(f"Using python locale: '{locale_str}.UTF-8'")

                tmp = locale_str[:2]
                try:
                    # TODO: needs 2 char abbreviations
                    pass
                except:
                    logger.error(f'could not set locale to {tmp}')
                else:
                    logger.info(f"Using locale: '{tmp}'")

        if 'archive_after' in self.settings:
            try:
                self.archive_after = int(self.settings['archive_after'])
            except Exception as e:
                logger.error(
                    f"An integer is required for archive_after - got {self.settings['archive_after']}. {e}"
                )

        self.db = DBITEM
        self.dbarch = DBARCH
        logger.info(f'items: {len(DBITEM)}; archive: {len(DBARCH)}')
        self.update_links()

    def use_archive(self):
        self.query_mode = 'archive table'
        self.db = DBARCH

    def use_items(self):
        self.query_mode = 'items table'
        self.db = DBITEM

    def get_completions(self):
        """
        Get completions from db items
        """
        completions = set([])
        self.completions = list(completions)
        self.kompletions = {}
        # self.occurrences = []
        self.occurrences = {} # hsk with fields such as @i -> hsh instances -> number of occurences

        for item in self.db:
            self.last_id = item.doc_id
            found = {
                x: v for x, v in item.items() if x in self.completion_keys
            }

            for x, v in found.items():
                if isinstance(v, list):
                    if x == 'k':
                        continue
                    self.occurrences.setdefault(x, {})
                    for p in v:
                        completions.add(f'@{x} {p}')
                        self.occurrences[x].setdefault(p, 0)
                        self.occurrences[x][p] += 1
                else:
                    self.occurrences.setdefault(x, {})
                    self.occurrences[x].setdefault(v, 0)
                    self.occurrences[x][v] += 1
                    completions.add(f'@{x} {v}')
                    if x == 'i':
                        # make a "k" completion for the "i" entry
                        i, t, s, d = (
                            item['i'],
                            item['itemtype'],
                            item['summary'],
                            item.doc_id,
                        )
                        completions.add(f'@k {i} {t} {s} | {d}')
                        # self.kompletions[f"@k {i} {t} {s}: {d}"] = d

        self.completions = list(completions)
        self.completions.sort()
        for x in  self.completions:
            if ' | ' not in x:
                continue
            parts = x.split(' | ')
            if len(parts) == 2:
                k, v = parts
                self.kompletions[k.strip()[3:]] = f"@k {v.strip()}"
            else:
                logger.debug(f"bad parts: {parts}")


    def show_occurrences(self):
        width = shutil.get_terminal_size()[0]
        tmp = []
        newline = False
        for k in self.completion_keys:
            if k in self.occurrences:
                if newline:
                    tmp.append('')
                else:
                    newline = True
                tmp.append(f"@{k}")
                instances = [x for x in self.occurrences[k].keys()]
                instances.sort()
                for instance in instances:
                    count = f"{self.occurrences[k][instance]}"
                    w = width - 7 - len(count)
                    tmp.append(f"   {truncate_string(instance, w)}: {count}")
        return "\n".join(tmp)



    def update_konnections(self, item):
        """
        Only change relevant hashes
        """
        # the original @k entries
        orig = (
            self.konnections_from.get(item.doc_id, []) if item.doc_id else []
        )

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
        konnected = [x for x in self.konnections_to] + [
            x for x in self.konnections_from
        ]
        self.konnected = list(set(konnected))

    def refreshKonnections(self):
        """
        to_hsh: ID -> ids of items with @k ID
        from_hsh ID -> ids in @k
        """
        self.konnections_to = {}
        self.konnections_from = {}
        self.konnected = []
        all_ids = [item.doc_id for item in self.db]
        for item in self.db:
            doc_id = item.doc_id
            if 'k' in item and item['k']:
                for id in item['k']:
                    if id in all_ids:
                        self.konnections_from.setdefault(doc_id, []). append(id)
                        self.konnections_to.setdefault(id, []).append(doc_id)
        konnected = [x for x in self.konnections_to] + [
            x for x in self.konnections_from
        ]
        self.konnected = list(set(konnected))
        self.konnected.sort()
        row = 0
        for id in self.konnected:
            row += 1
            self.konnected_id2row[id] = row


    def handle_backups(self):
        removefiles = []
        timestamp = (
            datetime.now().astimezone(ZoneInfo('UTC')).strftime('%Y-%m-%d')
        )
        filelist = os.listdir(self.backupdir)
        # deal with etm.json
        dbmtime = os.path.getctime(self.dbfile)
        zipfiles = [x for x in filelist if x.startswith('etm')]
        zipfiles.sort(reverse=True)
        if zipfiles:
            lastdbtime = os.path.getctime(
                os.path.join(self.backupdir, zipfiles[0])
            )
        else:
            lastdbtime = None

        if lastdbtime is None or dbmtime > lastdbtime:
            backupfile = os.path.join(self.backupdir, f'etm-{timestamp}.json')
            zipfile = os.path.join(self.backupdir, f'etm-{timestamp}.zip')
            shutil.copy2(self.dbfile, backupfile)
            with ZipFile(
                zipfile, 'w', compression=ZIP_DEFLATED, compresslevel=6
            ) as zip:
                zip.write(backupfile, os.path.basename(backupfile))
            os.remove(backupfile)
            logger.info(f'backed up {self.dbfile} to {zipfile}')
            zipfiles.insert(0, f'etm-{timestamp}.zip')
            zipfiles.sort(reverse=True)
        else:
            logger.info(f'{self.dbfile} unchanged - skipping backup')

        removefiles.extend(
            [os.path.join(self.backupdir, x) for x in zipfiles[7:]]
        )

        # deal with cfg.yaml
        cfgmtime = os.path.getctime(self.cfgfile)
        cfgfiles = [x for x in filelist if x.startswith('cfg')]
        cfgfiles.sort(reverse=True)
        if cfgfiles:
            lastcfgtime = os.path.getctime(
                os.path.join(self.backupdir, cfgfiles[0])
            )
        else:
            lastcfgtime = None
        if lastcfgtime is None or cfgmtime > lastcfgtime:
            backupfile = os.path.join(self.backupdir, f'cfg-{timestamp}.yaml')
            shutil.copy2(self.cfgfile, backupfile)
            logger.info(f'backed up {self.cfgfile} to {backupfile}')
            cfgfiles.insert(0, f'cfg-{timestamp}.yaml')
            cfgfiles.sort(reverse=True)
        else:
            logger.info(f'{self.cfgfile} unchanged - skipping backup')

        removefiles.extend(
            [os.path.join(self.backupdir, x) for x in cfgfiles[7:]]
        )

        if self.currfile and os.path.exists(self.currfile):
            currtime = os.path.getctime(self.currfile)
            currfiles = [x for x in filelist if x.startswith('curr')]
            currfiles.sort(reverse=True)
            if currfiles:
                lastcurrtime = os.path.getctime(
                    os.path.join(self.backupdir, currfiles[0])
                )
            else:
                lastcurrtime = None
            if lastcurrtime is None or currtime > lastcfgtime:
                backupfile = os.path.join(
                    self.backupdir, f'curr-{timestamp}.txt'
                )
                shutil.copy2(self.currfile, backupfile)
                logger.info(f'backed up {self.currfile} to {backupfile}')
                currfiles.insert(0, f'curr-{timestamp}.yaml')
                currfiles.sort(reverse=True)
            else:
                logger.info(f'{self.currfile} unchanged - skipping backup')

            removefiles.extend(
                [os.path.join(self.backupdir, x) for x in currfiles[7:]]
            )

        # maybe delete older backups
        if removefiles:
            filelist = '\n    '.join(removefiles)
            logger.info(f'removing old files:\n    {filelist}')
            for f in removefiles:
                os.remove(f)

        return True

    def save_timers(self):
        timers = deepcopy(self.timers)
        if self.active_timer and self.active_timer in timers:
            state, start, period = timers[self.active_timer]
            if state == 'r':
                now = datetime.now().astimezone()
                period += now - start
                state = 'p'
                timers[self.active_timer] = [state, now, period]
        if timers:
            if timers != self.saved_timers:
                with open(timers_file, 'wb') as fn:
                    pickle.dump(timers, fn)
                self.saved_timers = timers

        elif os.path.exists(timers_file):
            os.remove(timers_file)
        # this return is necessary to avoid blocking event_handler
        return

    # bound to tt
    def toggle_active_timer(self, row=None):
        if not self.active_timer:
            return
        now = datetime.now().astimezone()
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
            +: one is active (running or paused)

        transitions:
            n- -> r-   n- -> p-
            n+ -> i+   n+ -> i+
            i- -> r-   i- -> r-
            i+ -> r-   i+ -> r-
            r- -> p-   r- -> p-
            p- -> r-   p- -> r-
        """
        logger.debug("next_timer_state")
        if not doc_id:
            return
        other_timers = deepcopy(self.timers)
        logger.debug(f"{other_timers = }")
        if doc_id in other_timers:
            del other_timers[doc_id]
        active = [x for x, v in other_timers.items() if v[0] in ['r', 'p']]
        if len(active) > 1:
            logger.warning(f'more than one active timer: {active}')
        now = datetime.now().astimezone()
        if doc_id in self.timers:
            # there is already a timer for this item
            if active:
                # another timer is active - update time if needed and make inactive
                for x in active:
                    active_state, active_start, active_period = self.timers[x]
                    active_period = (
                        active_period + now - active_start
                        if active_state == 'r'
                        else active_period
                    )
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
            # create the timer but don't start it
            if active:
                state = 'i'
            else:
                # no other timer is active so make this timer's state paused
                state = 'p'
                self.active_timer = doc_id
            self.timers[doc_id] = [state, now, ZERO]

        self.save_timers()
        return True, doc_id, active

    def get_timers(self):
        """
        timers
        """
        db = self.db
        repeat_list = self.repeat_list
        pinned_list = self.pinned_list
        link_list = self.link_list
        konnected = self.konnected
        timers = self.timers
        active_timer = self.active_timer
        width = shutil.get_terminal_size()[0] - 3
        rows = []
        locations = set([])
        now = datetime.now().astimezone()
        state2sort = {'i': 'inactive', 'r': 'active', 'p': 'active'}
        total_time = inactive_time = ZERO
        num_timers = 0
        timer_ids = [x for x in timers if x]
        active = ""
        for doc_id in timer_ids:
            item = db.get(doc_id=doc_id)
            if not item:
                continue
            num_timers += 1
            itemtype = item['itemtype']
            summary = item['summary']
            state, start, elapsed = timers[doc_id]
            since = f'{format_relative_time(start)}'
            if state == 'r':
                elapsed += now - start
            elapsed = round_to_minutes(elapsed)
            if state in ['r', 'p']:
                # at most one timer can be active
                total = f'{status_duration(elapsed)}'
                this_width = width - len(since) - len(total) - 8
                self.active_str = f"{itemtype} {total} {state}{ELECTRIC}{since}  {truncate_string(summary, this_width)} "
            else:
                # zero or more timers can be inactive
                inactive_time += elapsed
            total_time += elapsed
            sort = state2sort[state]
            rhc = f'{status_duration(elapsed)} {state}{ELECTRIC}{format_relative_time(start)}'
            flags = get_flags(
                doc_id, repeat_list, link_list, konnected, pinned_list, timers
            )
            rows.append(
                {
                    'sort': (sort, now - start),
                    'values': [
                        itemtype,
                        summary,
                        flags,
                        rhc,  # status
                        doc_id,
                    ],
                }
            )
        self.inactive_str = f' {status_duration(inactive_time)}  '
        try:
            rows.sort(key=itemgetter('sort'), reverse=False)
        except Exception as e:
            logger.error(f"sort exception: {e}: {[type(x['sort']) for x in rows]}")
        rdict = NDict()
        timers_fmt = 'timers' if num_timers > 1 else 'timer'
        path = f'{num_timers} {timers_fmt}: {status_duration(total_time)}'.center(
            width, ' '
        )
        for row in rows:
            values = row['values']
            rdict.add(path, values)
        timers_view, row2id = rdict.as_tree(rdict)
        return timers_view, row2id


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
        self.now = datetime.now().astimezone()

    def set_active_item(self, doc_id):
        self.active_item = doc_id

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
        if self.active_view == 'effort':
            self.refreshAgenda()
            self.row2id = self.effort2id
            return self.effort_view
        if self.active_view == 'busy':
            self.refreshAgenda()
            return self.busy_view
        if self.active_view == 'yearly':
            self.refreshCalendar()
            return self.calendar_view
        if self.active_view == 'history':
            self.history_view, self.row2id = show_history(
                self.db,
                True,
                self.repeat_list,
                self.pinned_list,
                self.link_list,
                self.konnected,
                self.timers,
            )
            return self.history_view
        if self.active_view == 'timers':
            self.timers_view, self.row2id = self.get_timers()
            return self.timers_view
        if self.active_view == 'forthcoming':
            self.forthcoming_view, self.row2id = show_forthcoming(
                self.db,
                self.id2relevant,
                self.repeat_list,
                self.pinned_list,
                self.link_list,
                self.konnected,
                self.timers,
            )
            return self.forthcoming_view
        if self.active_view == 'do next':
            self.next_view, self.row2id, self.next_txt = show_next(
                self.db,
                self.repeat_list,
                self.pinned_list,
                self.link_list,
                self.konnected,
                self.timers,
            )
            return self.next_view
        if self.active_view == 'journal':
            self.journal_view, self.row2id = show_journal(
                self.db,
                self.id2relevant,
                self.repeat_list,
                self.pinned_list,
                self.link_list,
                self.konnected,
                self.timers,
            )
            return self.journal_view
        if self.active_view == 'tags':
            self.tag_view, self.row2id = show_tags(
                self.db,
                self.id2relevant,
                self.repeat_list,
                self.pinned_list,
                self.link_list,
                self.konnected,
                self.timers,
            )
            return self.tag_view
        if self.active_view == 'index':
            self.index_view, self.row2id = show_index(
                self.db,
                self.id2relevant,
                self.repeat_list,
                self.pinned_list,
                self.link_list,
                self.konnected,
                self.timers,
            )
            return self.index_view
        if self.active_view == 'location':
            self.index_view, self.row2id = show_location(
                self.db,
                self.id2relevant,
                self.repeat_list,
                self.pinned_list,
                self.link_list,
                self.konnected,
                self.timers,
            )
            return self.index_view
        if self.active_view == 'pinned':
            self.pinned_view, self.row2id = show_pinned(
                self.get_pinned(),  # items for ids in list
                self.repeat_list,
                self.pinned_list,
                self.link_list,
                self.konnected,
                self.timers,
            )
            return self.pinned_view
        if self.active_view == 'used time':
            used_details = self.used_details.get(self.active_month)
            if not used_details:
                month_format = datetime.strptime(
                    self.active_month + '-01', '%Y-%m-%d'
                ).strftime('%B %Y')
                return f'Nothing recorded for {month_format}'
            self.used_view = used_details
            self.row2id = self.used_details2id.get(self.active_month)
            return self.used_view
        if self.active_view == 'used summary':
            self.row2id = {}
            used_summary = self.used_summary.get(self.active_month)
            if not used_summary:
                month_format = datetime.strptime(
                    self.active_month + '-01', '%Y-%m-%d'
                ).strftime('%B %Y')
                return f'Nothing recorded for {month_format}'
            self.used_summary_view = used_summary
            return self.used_summary_view
        if self.active_view == 'review':
            self.review_view, self.row2id = show_review(
                self.db,
                self.repeat_list,
                self.pinned_list,
                self.link_list,
                self.konnected,
                self.timers,
            )
            return self.review_view
        if self.active_view == 'konnected':
            self.konnected_view, self.row2id = show_konnected(
                self.db,
                self.repeat_list,
                self.pinned_list,
                self.link_list,
                self.konnected,
                self.timers,
                self.active_item,
                self.konnections_from,
                self.konnections_to,
            )
            # self.konnected_id2row = {id: row for row, id in self.row2id.items()}
            return self.konnected_view

        if self.active_view == 'query':
            if self.query_text:
                if self.query_text == self.last_query:
                    return self.query_view
                else:
                    self.last_query = self.query_text
                if (
                    len(self.query_text) > 1
                    and self.query_text[1] == ' '
                    and self.query_text[0] in ['s', 'u', 'm', 'c', 'v']
                ):
                    self.query_view, self.row2id = show_query_results(
                        self.query_text, self.query_grpby, self.query_items, self.query_needs
                    )
                else:
                    # standard query
                    self.query_view, self.row2id = show_query_items(
                        self.query_text,
                        self.query_items,
                        self.repeat_list,
                        self.pinned_list,
                        self.link_list,
                        self.konnected,
                        self.timers,
                    )
            else:
                self.query_view = ''
                self.row2id = {}

            return self.query_view

    def set_query(self, text, grpby, items, needs=[]):
        self.query_text = text
        self.query_items = items
        self.query_grpby = grpby
        self.query_needs = needs

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

    def dtYrWk(self, dtstr):
        dt = parse(dtstr, strict=False)
        self.activeYrWk = getWeekNum(dt)
        self.refreshAgenda()

    def currMonth(self):
        self.active_month = date.today().strftime('%Y-%m')

    def prevMonth(self):
        dt = (
            datetime.strptime(
                self.active_month + '-01', '%Y-%m-%d'
            ).astimezone()
            - DAY
        )
        self.active_month = dt.strftime('%Y-%m')

    def nextMonth(self):
        dt = (
            datetime.strptime(
                self.active_month + '-01', '%Y-%m-%d'
            ).astimezone()
            + 31 * DAY
        )
        self.active_month = dt.strftime('%Y-%m')

    def show_konnections(self, selected_id):
        """
        konnected view for selected_id
        """
        if selected_id is None or not self.db.contains(doc_id=selected_id):
            return [], {}
        selected_item = self.db.get(doc_id=selected_id)
        if selected_item is None:
            return [], {}
        relevant = []
        # relevant.append(['Selection', selected_item])
        relevant.append(['   === selection:', selected_item])
        # relevant.append(['   ===', selected_item])

        for doc_id in self.konnections_from.get(selected_id, []):
            tmp = self.db.get(doc_id=doc_id)
            if tmp:
                # relevant.append(['From the selection', tmp])
                relevant.append(['      <<< from the selection:', tmp])
                # relevant.append(['      <<<', tmp])

        for doc_id in self.konnections_to.get(selected_id, []):
            tmp =self.db.get(doc_id=doc_id)
            if tmp:
                # relevant.append(['To the selection', tmp])
                relevant.append([' >>> to the selection:', tmp])
                # relevant.append([' >>>', tmp])

        if len(relevant) < 2:
            # from and to are empty
            return [], {}

        # width = shutil.get_terminal_size()[0] - 3
        rows = []
        # summary_width = width - 11
        for path, item in relevant:
            # rhc = str(doc_id).rjust(5, ' ')
            itemtype = FINISHED_CHAR if 'f' in item else item.get('itemtype', '?')
            if '===' in path:
                itemtype = "  →"
            elif '>>>' in path:
                itemtype = "↓"
            elif '<<<' in path:
                itemtype = "    ↓"
            doc_id = item.doc_id
            summary = item['summary']
            # flags = get_flags(
            #     doc_id, repeat_list, link_list, konnected, pinned_list, timers
            # )
            rows.append(
                {
                    # 'path': path,
                    'path': '',
                    'sort': (path.lstrip(), -doc_id),
                    'values': [
                        itemtype,
                        summary,
                        f"{doc_id}",
                        '',
                        doc_id,
                    ],
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
        tree, row2id = rdict.as_tree(rdict)
        tree = re.sub(r'^\s*\n', f" konnections for #{selected_id}\n", tree, 1)
        return tree, row2id


    def refreshRelevant(self):
        """
        Called to set the relevant items for the current date and to change the currentYrWk and activeYrWk to that containing the current date.
        """
        self.set_now()
        self.currentYrWk = getWeekNum(self.now)
        dirty = True
        while dirty:
            self.current, self.alerts, self.id2relevant, dirty = relevant(
                self.db,
                self.now,
                self.repeat_list,
                self.pinned_list,
                self.link_list,
                self.konnected,
                self.timers,
            )
            if dirty:
                self.refreshKonnections()
        self.refreshCache()

    def refreshAgenda(self):
        if self.activeYrWk not in self.cache:
            self.cache.update(
                schedule(
                    self.db,
                    yw=self.activeYrWk,
                    current=self.current,
                    now=self.now,
                    repeat_list=self.repeat_list,
                    pinned_list=self.pinned_list,
                    link_list=self.link_list,
                    konnected=self.konnected,
                    timers=self.timers,
                )
            )
        # agenda, done, busy, row2id, done2id
        (
            self.agenda_view,
            self.done_view,
            self.effort_view,
            self.busy_view,
            self.row2id,
            self.done2id,
            self.effort2id,
            self.busy_details,
        ) = self.cache[self.activeYrWk]

    def refreshCurrent(self):
        """
        Agenda for the current and following 'keep_current' weeks
        """
        if self.mk_current and self.currfile is not None:
            weeks = []
            self.set_now()
            curr_lines = []
            this_week = getWeekNum(self.now)
            num_weeks = self.settings['keep_current'][0]
            for _ in range(num_weeks):
                # weeks corresponding to 0, ..., num_weeks-1
                weeks.append(this_week)
                this_week = nextWeek(this_week)

            # tmp_cache = self.cache
            for week in weeks:
                if week in current_hsh:
                    # append the agenda component
                    curr_lines.append(current_hsh[week])
                else:
                    logger.debug(f'week {week} missing from cache')
            if curr_lines:
                with open(self.currfile, 'w', encoding='utf-8') as fo:
                    fo.write('\n\n'.join([x.strip() for x in curr_lines]))
                logger.info(
                    f'saved {len(curr_lines)} weeks from current schedule to {self.currfile}'
                )
            else:
                logger.info('current schedule empty - did not save')

        if self.mk_next:
            next_view, row2id, next_txt = show_next(
                self.db,
                self.repeat_list,
                self.pinned_list,
                self.link_list,
                self.konnected,
                self.timers,
            )
            next_view = current_hsh['next'] if 'next' in current_hsh else None
            if next_txt:
                with open(self.nextfile, 'w', encoding='utf-8') as fo:
                    fo.write(re.sub(LINEDOT, '   ', next_txt))
                logger.info(f'saved do next to {self.nextfile}')

    def show_query(self):
        self.is_showing_query = True

    def hide_query(self):
        self.is_showing_query = False


    def show_details(self):
        self.is_showing_details = True

    def hide_details(self):
        self.is_showing_details = False

    # def show_confirmation(self):
    #     self.details_key_press = ""
    #     self.is_showing_confirmation = True

    # def hide_confirmation(self):
    #     self.is_showing_confirmation = False

    # def coroutine():
    #     pass

    # self.got_choice = coroutine

    def show_choice(self):
        self.details_key_press = ''
        self.is_showing_choice = True

    def hide_choice(self):
        self.is_showing_choice = False

        # reset the coroutine used for got_choice
        def coroutine():
            pass

        self.got_choice = coroutine

    def show_entry(self):
        # self.entry_content = ""
        self.is_showing_entry = True

    def hide_entry(self):
        self.is_showing_entry = False

        def coroutine():
            pass

        self.got_entry = coroutine

    def get_row_details(self, row=None):
        if row is None:
            return ()
        self.current_row = row
        if self.is_showing_konnections:
            row2id = self.konnections_row2id
        else:
            row2id = self.row2id
        id_tup = row2id.get(row, None)
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
            logger.debug(f'toggle_pinned no details for {row}')
            return None, ''
        item_id = res[0]
        if item_id in self.pinned_list:
            self.pinned_list.remove(item_id)
            act = 'unpinned'
        else:
            self.pinned_list.append(item_id)
            act = 'pinned'
        logger.debug(f'pinned_list: {self.pinned_list}')
        return f'{act} {item_id}'

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
            return (
                False,
                f"The item\n   {item['itemtype']} {item['summary']}\n does not have an @g goto entry.",
            )

    def get_repetitions(self, row=None):
        """
        Called with a row, we should have an doc_id and can use relevant as aft_dt.
        Called while editing, we won't have a row or doc_id and can use '@s' as aft_dt
        """
        num = self.settings['num_repetitions']
        res = self.get_row_details(row)
        if not res:
            return None, ''
        item_id = res[0]
        instance = res[1]

        if not (item_id and item_id in self.id2relevant):
            logger.debug(f'{item_id} not in id2relevant')
            return ''
        showing = 'Repetitions'
        item = DBITEM.get(doc_id=item_id)
        details = f"{item['itemtype']} {item['summary']}"

        if not ('s' in item and ('r' in item or '+' in item)):
            return showing, 'not a repeating item'

        if instance:
            relevant = instance
        else:
            relevant = date_to_datetime(item['s'])
            at_plus = item.get('+', [])
            if at_plus:
                at_plus.sort()
                relevant = min(relevant, date_to_datetime(at_plus[0]))

        # relevant = instance if instance else self.id2relevant.get(item_id)
        # showing = 'Repetitions'
        if not relevant:
            return 'Repetitons', details + 'none'
        pairs = [
            format_datetime(x[0])[1]
            for x in item_instances(item, relevant, num + 1, False)
        ]
        starting = format_datetime(relevant.date())[1]
        if len(pairs) > num:
            showing = f'Next {num} repetitions'
            pairs = pairs[:num]
        else:
            showing = f'Remaining repetitions'
        return showing, f'from {starting} for\n{details}:\n  ' + '\n  '.join(
            pairs
        )

    def get_history(self, row=None):
        """
        For those with '@o s', additionally show those that were skipped.
        """
        num = self.settings['num_repetitions']
        res = self.get_row_details(row)
        if not res:
            return None, ''
        item_id = res[0]

        if not (item_id and item_id in self.id2relevant):
            return ''
        showing = 'Completion History'
        item = DBITEM.get(doc_id=item_id)

        if 'h' not in item and 'f' not in item:
            return showing, 'there is no history of completions'

        relevant = self.id2relevant.get(item_id)
        res = []
        skip = item.get('o', 'k') == 's'
        if 'f' in item:
            per = item['f']
            res.append((per.end, f' {fmt_period(per)}', FINISHED_CHAR))
        for c in item.get('h', []):
            if skip and c.start == c.end + ONEMIN:
                res.append((c.end, '', SKIPPED_CHAR))
            else:
                # due at 12am, change the effective due date to 12am of the following day
                if c.end.hour == 0 and c.end.minute == 0:
                    per = Period(c.start, c.end + DAY)
                else:
                    per = Period(c.start, c.end)
                res.append((c.end, f' {fmt_period(per)}', FINISHED_CHAR))
        res.sort()   # datetime obj as first component
        if len(res) > num:
            showing = f'Completion History: last {num} of {len(res)}'
            res = res[-num:]
        else:
            showing = f'Completion History'
        relevant = res[-1][0]
        details = f"{item['itemtype']} {item['summary']}"

        pairs = [
            f'{x[2]} {format_datetime(x[0], short=True)[1]:<16}{x[1]:>8}'
            for x in res
        ]
        starting = format_datetime(relevant.date())[1]

        if skip:
            pss = f"""

{FINISHED_CHAR} indicates completed instances.
{SKIPPED_CHAR} indicates skipped instances.
Due datetimes are shown. The length of
time a completion preceded (+) or
followed (-) the due datetime is also
shown when nonzero."""

        else:
            pss = f"""

{FINISHED_CHAR} indicates completed instances.
Due datetimes are shown. The length of
time the completion preceded (+) or
followed (-) the due datetime is also
shown when nonzero."""

        return (
            showing,
            f'through {starting} for\n{details}:\n\n  '
            + '\n  '.join(pairs)
            + pss,
        )

    def touch(self, row):
        res = self.get_row_details(row)
        if not res:
            return False
        doc_id, instance, job_id = res
        now = datetime.now().astimezone()
        item_hsh = self.db.get(doc_id=doc_id)
        item_hsh['modified'] = datetime.now().astimezone()
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
        logger.debug('maybe_finish')
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
        due_str = f'due: {format_datetime(due, short=True)[1]}' if due else ''

        if job_id:
            for job in item.get('j', []):
                if job['i'] != job_id:
                    continue
                elif job['status'] != '-':
                    # the requisite job_id is already finished or waiting
                    return (
                        False,
                        'this job is either finished or waiting',
                        None,
                        None,
                        None,
                    )
                else:
                    # the requisite job_id and available
                    return (
                        True,
                        f"{job['status']} {job['summary']}\n{due_str}",
                        item_id,
                        job_id,
                        due,
                    )
            # couldn't find job_id
            return False, f'bad job_id: {job_id}', None, None, None

        # we have an unfinished task without jobs
        return (
            True,
            f"{item['itemtype']} {item['summary']}\n{due_str}",
            item_id,
            job_id,
            due,
        )

    def clearCache(self):
        self.cache = {}

    def refreshCache(self):
        self.cache = schedule(
            ETMDB,
            self.currentYrWk,
            self.current,
            self.now,
            5,
            20,
            self.repeat_list,
            self.pinned_list,
            self.link_list,
            self.konnected,
            self.timers,
        )
        (
            self.used_details,
            self.used_details2id,
            self.used_summary,
            self.effort_details,
        ) = get_usedtime(
            self.db,
            self.repeat_list,
            self.pinned_list,
            self.link_list,
            self.konnected,
            self.timers,
        )

    def update_links(self):
        """
        Look for items with @g entries and add their ids
        to link_list or items with @+ or @r entries and add
        them to the repeat_list.
        """
        for item in self.db:
            if 'g' in item:
                if item.doc_id not in self.link_list:
                    self.link_list.append(item.doc_id)
            else:
                if item.doc_id in self.link_list:
                    self.link_list.remove(item_id)
            if '+' in item or 'r' in item:
                if item.doc_id not in self.repeat_list:
                    self.repeat_list.append(item.doc_id)
            else:
                if item.doc_id in self.repeat_list:
                    self.repeat_list.remove(item_id)

    def update_datetimes_to_periods(self):
        """
        For items with 'h' and/or 'f' entries, make sure entry is a Period. Also for clones
        created because of @o p, remove @k entries doc_ids that do not exist and remove @h entries.
        if db.json exists and etm.json does not, then copy db.json to etm.json and run this script
        using etm.json.
        """
        items_to_update = []
        old_parent = (
            {}
        )       # doc_id of parent -> parent item for items with @o p entries
        possible_clones = []  # items with @k entries
        doc_ids = []
        for item in self.db:
            doc_ids.append(item.doc_id)
            if item['itemtype'] == '-':
                changed = False
                if 'f' in item:
                    if not isinstance(item['f'], Period):
                        start = date_to_datetime(item['f'])
                        end = date_to_datetime(item.get('s', item['f']))
                        item['f'] = Period(start, end)
                        changed = True

                if 'o' in item:
                    if item['o'] == 'p':
                        item['o'] = 'k'
                        old_parent[item.doc_id] = item
                        changed = True

                if 'k' in item:
                    possible_clones.append(item)

                h_changed = False
                if 'h' in item and not ('r' in item or '+' in item):
                    # not repeating - should not have an @h
                    del item['h']
                    changed = True

                if 'h' in item:
                    # deal with old to new history format
                    curr_hist = item.get('h', [])
                    new_hist = []
                    h_changed = False
                    for x in curr_hist:
                        if isinstance(x, Period):
                            new_hist.append(x)
                        else:
                            x = date_to_datetime(x)
                            new_hist.append(Period(x, x))
                            h_changed = True

                    if h_changed:
                        item['h'] = new_hist
                        changed = True

                if 'j' in item:
                    j_changed = False
                    new_jobs = []
                    for job in item.get('j', []):
                        if 'f' not in job:
                            new_jobs.append(job)
                        elif isinstance(job['f'], Period):
                            new_jobs.append(job)
                        else:
                            dt = date_to_datetime(job['f'])
                            job['f'] = Period(dt, dt)
                            new_jobs.append(job)
                            j_changed = True
                    if j_changed:
                        item['j'] = new_jobs
                        changed = True

                if changed:
                    items_to_update.append(item)

        if items_to_update:
            # backup db
            updated_items = []
            for item in items_to_update:
                update_db(self.db, item.doc_id, item)
                updated_items.append(item.doc_id)
            logger.info(
                f'updated datetimes to periods for {len(updated_items)} items with these doc_ids:\n  {updated_items}'
            )

        items_to_update = []
        items_to_remove = []
        items_with_bad_links = []

        for item in possible_clones:
            for link in item.get('k', []):
                if link in doc_ids:
                    # the item corresponding to the link exists in the database
                    if link in old_parent and item['summary'].startswith(
                        old_parent[link]['summary']
                    ):
                        # we have a clone - the summary of the clone begins with the summary from the possible parent
                        parent = old_parent[link]
                        if 'f' in item:
                            # clone finished - add completion to parent
                            if isinstance(item['f'], Period):
                                completion = item['f']
                            else:
                                start = date_to_datetime(item['f'])
                                end = date_to_datetime(
                                    item.get('s', item['f'])
                                )
                                completion = Period(start, end)
                            parent.setdefault('h', []).append(completion)
                            items_to_update.append(parent)
                        elif 's' in item:
                            # clone unfinished - add datetime to parent
                            parent.setdefault('+', []).append(item['s'])
                            items_to_update.append(parent)
                        # remove the clone
                        items_to_remove.append(item)
                else:
                    # dead link
                    item['k'].remove(link)
                    items_to_update.append(item)
            if 'k' in item and not item['k']:
                del item['k']

        if items_to_update:
            # backup db
            updated_items = []
            for item in items_to_update:
                update_db(self.db, item.doc_id, item)
                updated_items.append(item.doc_id)
            logger.info(
                f'updated parents of clones for {len(updated_items)} items with these doc_ids:\n  {updated_items}'
            )

        if items_to_remove:
            # backup db
            removed_ids = []
            for item in items_to_remove:
                self.db.remove(doc_ids=[item.doc_id])
                removed_ids.append(item.doc_id)
            logger.info(
                f'removed clones for {len(removed_ids)} items with these doc_ids:\n  {removed_ids}'
            )

    def possible_archive(self):
        """
        Collect old finished tasks, (repeating or not), old non-repeating events,
        and repeating events with old @u entries. Do not collect journal.
        """
        if not self.archive_after:
            logger.info(
                f'archive_after: {self.archive_after} - skipping archive'
            )
            return
        now = datetime.now().astimezone()
        # old = now.replace(year=now.year - self.archive_after)
        old = now - timedelta(days=365*self.archive_after)
        rows = []
        for item in self.db:
            if item['itemtype'] == '%' or item.get('k', []):
                # keep journal and konnections
                continue
            elif 'f' in item:
                if isinstance(item['f'], Period):
                    if item['f'].start < old and item['f'].end < old:
                        # toss old finished tasks
                        rows.append(item)
                        continue
            elif '+' in item:
                toss = True
                for dt in item['+']:
                    if isinstance(dt, date):
                        # could be date or datetime
                        if isinstance(dt, datetime):
                            # datetime
                            if dt.date() >= old.date():
                                toss = False
                                break
                        else:
                            # date
                            if dt >= old.date():
                                toss = False
                                break
                    else:
                        prov = dt
                    # FIXME: complicated whether or not to archive other repeating items with 't' so keep them
                if toss:
                    rows.append(item)
                    continue
            elif 'r' in item:
                toss = True
                for rr in item['r']:
                    if 'u' not in rr:
                        toss = False
                        break
                    elif isinstance(rr['u'], date):
                        # could be date or datetime
                        if isinstance(rr['u'], datetime):
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

            elif item['itemtype'] == '*':
                start = item.get('s', None)
                if isinstance(start, datetime):
                    if start < old:
                        # toss old, non-repeating events
                        rows.append(item)
                        continue
                elif isinstance(start, date):
                    if start < old.date():
                        # toss old, non-repeating events
                        rows.append(item)
                        continue
            else:
                continue

        # one at a time
        archive_ids = [item.doc_id for item in rows]
        failed_ids = []
        rem_ids = []
        logger.info(f'items to archive {len(archive_ids)}: {archive_ids}')
        for item in rows:
            try:
                self.dbarch.insert(item)
            except Exception as e:
                failed_ids.append(f'{item.doc_id}; {e}')
            else:
                self.db.remove(doc_ids=[item.doc_id])
                rem_ids.append(item.doc_id)
        if rem_ids:
            logger.info(f'archived doc_ids: {rem_ids}')
        if failed_ids:
            logger.error(f'archive failed for doc_ids: {failed_ids}')
        return rows

    def move_item(self, row=None):
        res = self.get_row_details(row)
        if not (res and res[0]):
            return False
        item_id = res[0]
        item = self.db.get(doc_id=item_id)
        try:
            if self.query_mode == 'items table':
                # move to archive
                DBARCH.insert(item)
                DBITEM.remove(doc_ids=[item_id])
            else:
                # back to items
                DBITEM.insert(item)
                DBARCH.remove(doc_ids=[item_id])
        except Exception as e:
            logger.error(
                f'move from {self.query_mode} failed for item_id: {item_id}; exception: {e}'
            )
            return False
        return True

    def send_mail(self, doc_id):
        item = DBITEM.get(doc_id=doc_id)
        attendees = item.get('n', None)
        if not attendees:
            logger.error(
                f'@n (attendees) are not specified in {item}. send_mail aborted.'
            )
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
        if not (
            smtp_from and smtp_id and smtp_pw and smtp_server and smtp_body
        ):
            logger.error(
                f'Bad or missing stmp settings in the cfg.json smtp entry: {smtp}. send_mail aborted'
            )
            return
        startdt = item.get('s', '')
        if startdt:
            start = format_datetime(startdt)[1]
            startdt = date_to_datetime(startdt)
            alertdt = datetime.now().astimezone()
            if startdt > alertdt:
                when = f'in {duration_in_words(startdt-alertdt, short=True)}'
            elif startdt == alertdt:
                when = 'now'
            else:
                when = f'{duration_in_words(alertdt-startdt, short=True)} ago'
        else:
            start = ''
            when = ''
        summary = item.get('summary', '')
        location = item.get('l', '')
        description = item.get('d', '')
        message = smtp_body.format(
            start=start,
            when=when,
            summary=summary,
            location=location,
            description=description,
        )
        logger.debug(f"message: {message}")
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
            logger.error(
                f'@n (attendees) are not specified in {item}. send_text aborted.'
            )
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
            logger.error(
                f"Bad or missing smx settings in the cfg.json sms entry: {sms}. send_text aborted. sms_from: {sms_from}; sms_phone: {sms_phone}; sms_pw: {sms_pw}; sms_server: {sms_server}; sms_body: {sms_body}"
            )
            return
        startdt = item.get('s', '')
        if startdt:
            start = format_datetime(startdt)[1]
            startdt = date_to_datetime(startdt)
            alertdt = datetime.now().astimezone()
            if startdt > alertdt:
                when = f'in {duration_in_words(startdt-alertdt, short=True)}'
            elif startdt == alertdt:
                when = 'now'
            else:
                when = f'{duration_in_words(alertdt-startdt, short=True)} ago'
        else:
            start = ''
            when = ''
        summary = item.get('summary', '')
        location = item.get('l', '')
        description = item.get('d', '')
        message = sms_body.format(
            start=start,
            when=when,
            summary=summary,
            location=location,
            description=description,
        )

        # All the necessary ingredients are in place
        import smtplib
        from email.mime.text import MIMEText

        sms = smtplib.SMTP(sms_server)
        sms.starttls()
        sms.login(sms_from, sms_pw)
        msg = MIMEText(message)
        msg['From'] = sms_from
        msg['Subject'] = summary
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
        columns = 2 if width < 70 else 3
        today = date.today()
        y = today.year
        try:
            c = calendar.LocaleTextCalendar(0, self.cal_locale)
        except:
            logger.warning(f'error using locale {self.cal_locale}')
            c = calendar.LocaleTextCalendar(0)
        cal = []
        m = 0
        m += 12 * self.calAdv
        y += m // 12
        m %= 12
        for i in range(12):   # months in the year
            cal.append(c.formatmonth(y, 1 + i, w=2).split('\n'))
        ret = ['']
        for r in range(0, 12, columns):  # 12 months in columns months
            if columns == 3:
                l = max(len(cal[r]), len(cal[r + 1]), len(cal[r + 2]))
            else:
                l = max(len(cal[r]), len(cal[r + 1]))

            for i in range(columns):
                if len(cal[r + i]) < l:
                    for _ in range(len(cal[r + i]), l + (columns - 1)):
                        cal[r + i].append('')
            for j in range(l):  # rows from each of the 2 months
                if columns == 3:
                    ret.append(
                        (
                            '%-20s   %-20s   %-20s '
                            % (cal[r][j], cal[r + 1][j], cal[r + 2][j])
                        )
                    )
                else:
                    ret.append(('%-20s   %-20s ' % (cal[r][j], cal[r + 1][j])))
        max_len = max([len(line) for line in ret])
        indent = max(width - max_len, 0) // 2 * ' '
        ret_lines = [f'{indent}{line}' for line in ret]
        ret_str = '\n'.join(ret_lines)
        self.calendar_view = ret_str

    def nextcal(self):
        self.calAdv += 1
        self.refreshCalendar()

    def prevcal(self):
        self.calAdv -= 1
        self.refreshCalendar()

    def currcal(self):
        self.calAdv = date.today().month // 13
        self.refreshCalendar()


def nowrap(txt, indent=3, width=shutil.get_terminal_size()[0] - 3):
    return txt


def wrap(txt, indent=3, width=shutil.get_terminal_size()[0] - 3):
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
            initial_indent = ' ' * indent
        tmp.append(
            textwrap.fill(
                p,
                initial_indent=initial_indent,
                subsequent_indent=' ' * indent,
                width=width - indent - 1,
            )
        )
    return '\n'.join(tmp)


def set_summary(summary='', start=None, relevant=None, freq=''):
    """ """
    if not (
        '{XXX}' in summary
        and isinstance(start, date)
        and isinstance(relevant, date)
        and freq in ['y', 'm', 'w', 'd']
    ):
        return summary
    relevant_date = (
        relevant.date() if isinstance(relevant, datetime) else relevant
    )
    start_date = start.date() if isinstance(start, datetime) else start
    diff = relevant_date - start_date
    replacement = 0
    if freq == 'y':
        replacement = relevant_date.year - start_date.year
    elif freq == 'm':
        years = relevant_date.year - start_date.year
        months = relevant_date.month - start_date.month
        replacement = 12 * years + months
    elif freq == 'w':
        replacement = diff.days // 7
    elif freq == 'd':
        replacement = diff.days
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
    return '{0}{1}'.format(str(num), suffix)


def one_or_more(s):
    def _str(s):
        s = str(s)
        if s in WKDAYS_ENCODE:
            return WKDAYS_ENCODE[s].lstrip('+')
        else:
            return s
    if type(s) is list:
        return ', '.join([_str(x) for x in s])
    else:
        return _str(s)


def do_string(arg):
    try:
        obj = str(arg)
        rep = arg
    except:
        obj = None
        rep = f'invalid: {arg}'
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
                rep_lst.append(f'~{arg}~')
        obj = '\n'.join(obj_lst) if all_ok else None
        rep = '\n'.join(rep_lst)
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
                rep_lst.append(f'~{arg}~')
        obj = obj_lst if all_ok else None
        rep = ', '.join(rep_lst)
    return obj, rep


def string(arg, typ=None):
    try:
        arg = str(arg)
    except:
        if typ:
            return False, '{}: {}'.format(typ, arg)
        else:
            return False, '{}'.format(arg)
    return True, arg


def string_list(arg, typ=None):
    """ """
    if arg == '':
        args = []
    elif type(arg) == str:
        try:
            args = [x.strip() for x in arg.split(',')]
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
            return False, '{}: {}'.format(typ, '; '.join(msg))
        else:
            return False, '{}'.format('; '.join(msg))
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
    msg = ''
    try:
        arg = int(arg)
    except:
        if typ:
            return False, '{}: {}'.format(typ, arg)
        else:
            return False, arg
    if min is not None and arg < min:
        msg = '{} is less than the allowed minimum'.format(arg)
    elif max is not None and arg > max:
        msg = '{} is greater than the allowed maximum'.format(arg)
    elif not zero and arg == 0:
        msg = '0 is not allowed'
    if msg:
        if typ:
            return False, '{}: {}'.format(typ, msg)
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
            args = [int(x) for x in arg.split(',')]
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
            return False, '{}: {}'.format(typ, '; '.join(msg))
        else:
            return False, '; '.join(msg)
    else:
        return True, ret


def title(arg):
    return string(arg, 'title')


entry_tmpl = """\
{%- set title -%}\
{{ h.itemtype }} {{ h.summary }}\
{% if 's' in h %}{{ " @s {}".format(dt2str(h['s'])[1]) }}{% endif %}\
{%- if 'e' in h %}{{ " @e {}".format(in2str(h['e'])) }}{% endif %}\
{%- if 'w' in h %}{{ " @w {}".format(inlst2str(h['w'])) }}{% endif %}\
{%- if 'b' in h %}{{ " @b {}".format(h['b']) }}{% endif %}\
{%- if 'z' in h %}{{ " @z {}".format(h['z']) }}{% endif %}\
{%- endset %}\
{{ nowrap(title) }} \
{% if 'f' in h %}\
{{ "@f {} ".format(prd2str(h['f'])) }} \
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
{%- if 'K' in h %}
{% for x in h['k'] %}{{ "@K {} ".format(x) }}{% endfor %}\
{% endif %}\
{%- if 'n' in h %}
{% for x in h['n'] %}{{ "@n {} ".format(x) }}{% endfor %}\
{% endif %}\
{% if 'h' in h and h['h'] %}
@h {{ nowrap(prdlst2str(h['h'])) }} \
{%- endif %}\
{%- set ls = namespace(found=false) -%}\
{%- set location -%}\
{%- for k in ['l', 'm', 'g', 'x', 'p'] -%}\
{%- if k in h %} @{{ k }} {{ h[k] }}{% set ls.found = true %} {% endif -%}\
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
{%- for k in ['i', 's', 'M', 'm', 'n', 'w', 'E', 'c'] -%}
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
{% for k in ['+', '-'] %} \
{% if k in h and h[k] %}
@{{ k }} {{ nowrap(dtlst2str(h[k])) }} \
{%- endif %} \
{%- endfor %}\
{% if 'd' in h %}\

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
{% if 'f' in x %}{{ " &f {}".format(prd2str(x['f'])) }}{% endif %}\
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
{%- if 'w' in h %}{{ " @w {}".format(inlst2str(h['w'])) }}{% endif %}\
{%- if 'b' in h %}{{ " @b {}".format(h['b']) }}{% endif %}\
{%- if 'z' in h %}{{ " @z {}".format(h['z']) }}{% endif %}\
{%- endset %}\
{{ wrap(title) }} \
{% if 'f' in h %}\
{{ "@f {} ".format(prd2str(h['f'])) }} \
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
{%- if 't' in h %}\
{% for x in h['t'] %}{{ "@t {} ".format(x) }}{% endfor %}\
{% endif %}\
{%- if 'k' in h %}
{% for x in h['k'] %}{{ "@k {} ".format(x) }}{% endfor %}\
{% endif %}\
{%- if 'K' in h %}
{% for x in h['k'] %}{{ "@K {} ".format(x) }}{% endfor %}\
{% endif %}\
{%- if 'n' in h %}
{% for x in h['n'] %}{{ "@n {} ".format(x) }}{% endfor %}\
{% endif %}\
{% if 'h' in h and h['h'] %}
@h {{ prdlst2str(h['h']) }} \
{%- endif %}\
{%- set ls = namespace(found=false) -%}\
{%- set location -%}\
{%- for k in ['l', 'm', 'g', 'x', 'p'] -%}\
{%- if k in h %} @{{ k }} {{ h[k] }}{% set ls.found = true %} {% endif -%}\
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
{%- for k in ['i', 's', 'M', 'm', 'n', 'w', 'E', 'c'] -%}
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
{% for k in ['+', '-'] %} \
{% if k in h and h[k] %}
@{{ k }} {{ wrap(dtlst2str(h[k])) }} \
{%- endif %} \
{%- endfor %}\
{% if 'd' in h %}\
{% set description -%} \
@d {{ h['d'] }} \
{%- endset %}
{{ wrap(description) }} \
{% endif -%}\
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
{% if 'f' in x %}{{ " &f {}".format(prd2str(x['f'])) }}{% endif %}\
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
jinja_entry_template.globals['in2str'] = fmt_dur
jinja_entry_template.globals['dtlst2str'] = plain_datetime_list
jinja_entry_template.globals['inlst2str'] = format_duration_list
jinja_entry_template.globals['prd2str'] = format_period
jinja_entry_template.globals['prdlst2str'] = format_period_list
jinja_entry_template.globals['one_or_more'] = one_or_more
jinja_entry_template.globals['isinstance'] = isinstance
jinja_entry_template.globals['nowrap'] = nowrap

jinja_display_template = Template(display_tmpl)
jinja_display_template.globals['dt2str'] = plain_datetime
jinja_display_template.globals['in2str'] = fmt_dur
jinja_display_template.globals['dtlst2str'] = plain_datetime_list
jinja_display_template.globals['inlst2str'] = format_duration_list
jinja_display_template.globals['prd2str'] = format_period
jinja_display_template.globals['prdlst2str'] = format_period_list
jinja_display_template.globals['one_or_more'] = one_or_more
jinja_display_template.globals['isinstance'] = isinstance
jinja_display_template.globals['wrap'] = wrap


def do_beginby(arg):
    beginby_str = 'an integer number of days'
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


def do_konnection(arg: int):
    konnection_str = 'an integer document id'
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

def do_konnect(arg: str):
    konnect_str = "summary for konnected inbox item"
    ok, res = string(arg)
    if ok:
        return f"! {res} @s {format_date(datetime.today())[1]}", arg
    else:
        return None, f"'{arg}' is missing. Konnect requires {konnect_str}"


def do_usedtime(arg):
    """
    >>> do_usedtime('75m: 9p 2019-02-01')
    ([Duration(hours=1, minutes=15), DateTime(2019, 2, 1, 21, 0, 0, tzinfo=ZoneInfo('America/New_York'))], '1h15m: 2019-02-01 9:00pm')
    >>> do_usedtime('75m: 2019-02-01 9:00AM')
    ([Duration(hours=1, minutes=15), DateTime(2019, 2, 1, 9, 0, 0, tzinfo=ZoneInfo('America/New_York'))], '1h15m: 2019-02-01 9:00am')
    """
    if not arg:
        return None, ''
    got_period = got_datetime = False
    rep_period = 'period'
    rep_datetime = 'datetime'
    parts = arg.split(': ')
    period = parts.pop(0)
    if period:
        ok, res = parse_durations(period)
        if ok:
            obj_period = res
            rep_period = fmt_dur(res)
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
        return obj, f'{rep_period}: {rep_datetime}'
    else:
        return None, f'{rep_period}: {rep_datetime}'


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
            rep += f'\ncommmand is required but missing'
        else:
            obj = [obj_periods, commands]

    return obj, rep


def do_duration(arg):
    """
    >>> do_duration('')
    (None, 'time period')
    >>> do_duration('90')
    (None, 'incomplete or invalid period: 90')
    >>> do_duration('90m')
    (Duration(hours=1, minutes=30), '1h30m')
    """
    if not arg:
        return None, f'time period'
    ok, res = parse_duration(arg)
    if ok:
        obj = res
        rep = f'{format_duration(res)}'
    else:
        obj = None
        rep = f'incomplete or invalid period: {arg}'
    return obj, rep


def do_two_periods(arg):
    if not arg:
        return None, f'two time periods'
    if arg:
        periods = [x.strip() for x in arg.split(',')]
        if len(periods) != 2:
            obj = None
            rep = f'got {len(periods)} but exactly two periods are requred'
        else:
            # we have 2 periods
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
            rep = f"{', '.join(good_periods)}"
            if bad_periods:
                obj = None
                rep += f"\nincomplete or invalid periods: {', '.join(bad_periods)}"
            else:
                # we have 2 good periods since none were bad
                obj = obj_periods
    return obj, rep


def do_overdue(arg):
    ovrstr = 'overdue: character from (r)estart, (s)kip or (k)eep'

    if arg:
        ok = arg in ('k', 'r', 's')
        if ok:
            return arg, f'overdue: {arg}'
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


def do_priority(arg):
    """
    >>> do_priority(6)
    (None, 'invalid priority: 6 is greater than the allowed maximum. An integer priority number from 0 (none), to 4 (urgent) is required')
    >>> do_priority("1")
    ('1', 'priority: 1')
    """
    prioritystr = 'An integer priority number from 0 (none), to 4 (urgent)'
    if arg:
        ok, res = integer(arg, 0, 4, True, '')
        if ok:
            obj = f'{res}'
            rep = f'priority: {arg}'
        else:
            obj = None
            rep = f'invalid priority: {res}. {prioritystr} is required'
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
    easterstr = 'easter: a comma separated list of integer numbers of days before, < 0, or after, > 0, Easter.'

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
            rep = f'invalid easter: {res}. Required for {easterstr}'
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

    intstr = 'Interval requires a positive integer (default 1) that sets the frequency interval. E.g., with frequency w (weekly), interval 3 would repeat every three weeks.'

    if arg:
        ok, res = integer(arg, 1, None, False)
        if ok:
            return res, f'interval: {arg}'
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
    freqstr = '(y)early, (m)onthly, (w)eekly, (d)aily, (h)ourly or mi(n)utely.'
    if arg in freq:
        return arg, f'{freq_names[arg]}'
    elif arg:
        return None, wrap(f'invalid frequency: {arg} not in {freqstr}', 2)
    else:
        return None, wrap(
            f"repetition frequency: character from {freqstr} Append an '&' to add an option.",
            2,
        )


def do_setpositions(arg):
    """
    >>> do_setpositions("1")
    ([1], 'set positions: 1')
    >>> do_setpositions("-1, 0")
    (None, 'invalid set positions: 0 is not allowed. set positions (non-zero integer or sequence of non-zero integers). When multiple dates satisfy the rule, take the dates from this/these positions in the list, e.g, &s 1 would choose the first element and &s -1 the last.')
    """
    setposstr = 'set positions (non-zero integer or sequence of non-zero integers). When multiple dates satisfy the rule, take the dates from this/these positions in the list, e.g, &s 1 would choose the first element and &s -1 the last.'
    if arg:
        args = arg.split(',')
        ok, res = integer_list(args, None, None, False, '')
        if ok:
            obj = res
            rep = f'set positions: {arg}'
        else:
            obj = None
            rep = f'invalid set positions: {res}. {setposstr}'
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

    countstr = 'count: a positive integer. Include no more than this number of repetitions.'

    if arg:
        ok, res = integer(arg, 1, None, False)
        if ok:
            obj = res
            rep = f'count: {arg}'
        else:
            obj = None
            rep = f'invalid count: {res}. Required for {countstr}'
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
    weekdaysstr = 'weekdays: a comma separated list of English weekday abbreviations from SU, MO, TU, WE, TH, FR, SA. Prepend an integer to specify a particular weekday in the month. E.g., 3WE for the 3rd Wednesday or -1FR, for the last Friday in the month.'
    if arg:
        args = [x.strip().upper() for x in arg.split(',')]
        bad = []
        good = []
        rep = []
        for x in args:
            m = threeday_regex.match(x)
            if m:
                # fix 3 char weekdays, e.g., -2FRI -> -2FR
                x = f'{m[1]}{m[2][:2]}'
            if x in WKDAYS_DECODE:
                good.append(eval('dr.{}'.format(WKDAYS_DECODE[x])))
                rep.append(x)
            elif x in WKDAYS_ENCODE:
                try:
                    good.append(eval(x))
                except Exception as e:
                    logger.debug(f"exception: {e} when evaluating '{x}'")

                rep.append(WKDAYS_ENCODE[x].lstrip('+'))
            else:
                bad.append(x)
        if bad:
            obj = None
            rep = f"incomplete or invalid weekdays: {', '.join(bad)}. {weekdaysstr}"
        else:
            obj = good
            rep = ', '.join(rep)
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
            rep = f'{arg}'
        else:
            obj = None
            rep = 'invalid weeknumbers: {res}. Required for {weeknumbersstr}'
    else:
        obj = None
        weeknumbersstr = 'weeknumbers: a comma separated list of integer week numbers from 1, 2, ..., 53'

        rep = weeknumbersstr
    return obj, rep


def do_months(arg):
    """
    bymonth (1, 2, ..., 12 or a sequence of such integers)
    >>> do_months("0, 2, 7, 13")
    (None, 'invalid months: 0 is not allowed; 13 is greater than the allowed maximum. Required for months: a comma separated list of integer month numbers from 1, 2, ..., 12')
    """
    monthsstr = 'months: a comma separated list of integer month numbers from 1, 2, ..., 12'

    if arg:
        args = arg.split(',')
        ok, res = integer_list(args, 0, 12, False, '')
        if ok:
            obj = res
            rep = f'{arg}'
        else:
            obj = None
            rep = f'invalid months: {res}. Required for {monthsstr}'
    else:
        obj = None
        rep = monthsstr
    return obj, rep


def do_monthdays(arg):
    """
    >>> do_monthdays("0, 1, 26, -1, -2")
    (None, 'invalid monthdays: 0 is not allowed. Required for monthdays: a comma separated list of integer month days from  (1, 2, ..., 31. Prepend a minus sign to count backwards from the end of the month. E.g., use  -1 for the last day of the month.')
    """

    monthdaysstr = 'monthdays: a comma separated list of integer month days from  (1, 2, ..., 31. Prepend a minus sign to count backwards from the end of the month. E.g., use  -1 for the last day of the month.'

    args = arg.split(',')
    if arg:
        args = arg.split(',')
        ok, res = integer_list(args, -31, 31, False, '')
        if ok:
            obj = res
            rep = f'{arg}'
        else:
            obj = None
            rep = f'invalid monthdays: {res}. Required for {monthdaysstr}'
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
    hoursstr = (
        'hours: a comma separated of integer hour numbers from 0, 1,  ..., 23.'
    )

    args = arg.split(',')

    if args:
        ok, res = integer_list(args, 0, 23, True, 'hours')
        if ok:
            obj = res
            rep = arg
        else:
            obj = None
            rep = f'invalid hours: {res}. Required for {hoursstr}'
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
    minutesstr = 'minutes: a comma separated of integer minute numbers from 0 through 59.'

    args = arg.split(',')
    if args:
        ok, res = integer_list(arg, 0, 59, True, '')
        if ok:
            obj = res
            rep = arg
        else:
            obj = None
            rep = f'invalid minutes: {res}. Required for {minutesstr}'
    else:
        obj = None
        rep = minutesstr
    return obj, rep


rrule_methods = {
    'r': 'frequency',
    'i': 'interval',
    's': 'setpositions',
    'c': 'count',
    'u': 'until',
    'M': 'months',
    'm': 'monthdays',
    'W': 'weeknumbers',
    'w': 'weekdays',
    'h': 'hours',
    'n': 'minutes',
    'E': 'easterdays',
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
    'y': 0,  #'YEARLY',
    'm': 1,  #'MONTHLY',
    'w': 2,  #'WEEKLY',
    'd': 3,  #'DAILY',
    'h': 4,  #'HOURLY',
    'n': 5,  #'MINUTELY',
}

# Note: the values such as MO in the following are dateutil.rrule WEEKDAY methods and not strings. A dict is used to dispatch the relevant method
rrule_weekdays = dict(
    MO=dr.MO, TU=dr.TU, WE=dr.WE, TH=dr.TH, FR=dr.FR, SA=dr.SA, SU=dr.SU
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
    'E': 'byeaster',  # interger number of days before (-) or after (+) Easter Sunday
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
            msg.append(
                'error: Elements must be hashes. Cannot process: "{}"'.format(
                    hsh
                )
            )
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
                msg.append('error: {} is not a valid key'.format(key))

        if not msg:
            ret.append(res)

    if msg:
        return False, '{}'.format('; '.join(msg))
    else:
        return True, ret


def rrule_args(r_hsh):
    """
    Housekeeping: Check for u and c, fix integers and weekdays. Replace etm arg names with dateutil. E.g., frequency 'y' with 0, 'E' with 'byeaster', ... Called by item_instances.
    >>> item_eg = { "s": parse('2018-03-07 8am').naive(), "r": [ { "r": "w", "u": parse('2018-04-01 8am').naive(), }, ], "itemtype": "*"}
    >>> item_instances(item_eg, parse('2018-03-01 12am').naive(), parse('2018-04-01 12am').naive())
    [(DateTime(2018, 3, 7, 8, 0, 0, tzinfo=ZoneInfo('UTC')), None), (DateTime(2018, 3, 14, 8, 0, 0, tzinfo=ZoneInfo('UTC')), None), (DateTime(2018, 3, 21, 8, 0, 0, tzinfo=ZoneInfo('UTC')), None), (DateTime(2018, 3, 28, 8, 0, 0, tzinfo=ZoneInfo('UTC')), None)]
    >>> r_hsh = item_eg['r'][0]
    >>> r_hsh
    {'r': 'w', 'u': DateTime(2018, 4, 1, 8, 0, 0)}
    >>> rrule_args(r_hsh)
    (2, {'until': DateTime(2018, 4, 1, 8, 0, 0)})
    >>> item_eg = { "s": parse('2016-01-01 8am').naive(), "r": [ { "r": "y", "E": 0, }, ], "itemtype": "*"}
    >>> item_instances(item_eg, parse('2016-03-01 12am').naive(), parse('2019-06-01 12am').naive())
    [(DateTime(2016, 3, 27, 8, 0, 0, tzinfo=ZoneInfo('UTC')), None), (DateTime(2017, 4, 16, 8, 0, 0, tzinfo=ZoneInfo('UTC')), None), (DateTime(2018, 4, 1, 8, 0, 0, tzinfo=ZoneInfo('UTC')), None), (DateTime(2019, 4, 21, 8, 0, 0, tzinfo=ZoneInfo('UTC')), None)]
    >>> r_hsh = item_eg['r'][0]
    >>> r_hsh
    {'r': 'y', 'E': 0}
    >>> rrule_args(r_hsh)
    (0, {'byeaster': 0})
    >>> item_eg = { "s": parse('2018-03-07 8am', tz="US/Eastern"), "e": timedelta(days=1, hours=5), "r": [ { "r": "w", "i": 2, "u": parse('2018-04-01 8am', tz="US/Eastern")}], "z": "US/Eastern", "itemtype": "*" }
    >>> r_hsh = item_eg['r'][0]
    >>> r_hsh
    {'r': 'w', 'i': 2, 'u': DateTime(2018, 4, 1, 8, 0, 0, tzinfo=ZoneInfo('US/Eastern'))}
    >>> rrule_args(r_hsh)
    (2, {'interval': 2, 'until': DateTime(2018, 4, 1, 8, 0, 0, tzinfo=ZoneInfo('US/Eastern'))})
    >>> item_eg = { "s": parse('2018-03-07 8am', tz="US/Eastern"),  "r": [ { "r": "w", "w": MO(+2), "u": parse('2018-06-30 8am', tz="US/Eastern")}], "z": "US/Eastern", "itemtype": "*" }
    >>> r_hsh = item_eg['r'][0]
    >>> r_hsh
    {'r': 'w', 'w': MO(+2), 'u': DateTime(2018, 6, 30, 8, 0, 0, tzinfo=ZoneInfo('US/Eastern'))}
    >>> rrule_args(r_hsh)
    (2, {'byweekday': MO(+2), 'until': DateTime(2018, 6, 30, 8, 0, 0, tzinfo=ZoneInfo('US/Eastern'))})

    """

    # force integers
    for k in 'icsMmWhmE':
        if k in r_hsh:
            args = r_hsh[k]
            if not isinstance(args, list):
                args = [args]
            tmp = [int(x) for x in args]
            r_hsh[k] = tmp[0] if len(tmp) == 1 else tmp
    if 'u' in r_hsh and 'c' in r_hsh:
        logger.warning(
            f"Warning: using both 'c' and 'u' is depreciated in {r_hsh}"
        )
    freq = rrule_freq[r_hsh['r']]
    kwd = {rrule_name[k]: r_hsh[k] for k in r_hsh if k != 'r'}
    return freq, kwd


def get_next_due(item, done, due, from_rrule=False):
    """
    return the next due datetime for an @r and @+ / @- repetition
    """
    lofh = item.get('r')
    if not lofh:
        return ''
    rset = dr.rruleset()
    overdue = item.get('o', 'k')   # make 'k' the default for 'o'
    start = item['s']
    dtstart = date_to_datetime(item['s'])
    if due > dtstart:
        # we've finished a between instance
        return dtstart
    # we're finishing the oldest instance
    h = [x.end for x in item.get('h', [])]
    h.sort()

    due = dtstart if not due else due

    if overdue == 'k':
        aft = due
        inc = False
    elif overdue == 'r':
        aft = done
        dtstart = done
        inc = False
    else:  # 's' skip
        today = date_to_datetime(date.today())
        if due < today:
            aft = today
            inc = True
        else:
            aft = due
            inc = False
    using_dates = False
    if isinstance(start, date) and not isinstance(start, datetime):
        using_dates = True
        aft = date_to_datetime(aft)
    for hsh in lofh:
        freq, kwd = rrule_args(hsh)
        kwd['dtstart'] = dtstart
        try:
            rset.rrule(dr.rrule(freq, **kwd))
        except Exception as e:
            logger.error(f'error processing {hsh}: {e}')
            return []

    plus = item.get('+', [])
    hist = [x.end for x in item.get('h', [])]
    minus = item.get('-', [])
    minus_hist = hist + minus

    plus_not_minus = list(set(plus) - set(minus_hist))
    minus_not_plus = list(set(minus_hist) - set(plus))
    if from_rrule:
        for dt in minus_not_plus:
            rset.exdate(date_to_datetime(dt))
        nxt = rset.after(date_to_datetime(aft), inc)
    else:
        for dt in plus_not_minus:
            rset.rdate(date_to_datetime(dt))
        nxt = rset.after(date_to_datetime(aft), inc)
    if nxt:
        if using_dates:
            nxt = nxt.date()
    else:
        nxt = None
    return nxt


def date_to_datetime(dt, hour=0, minute=0):
    if isinstance(dt, date) and not isinstance(dt, datetime):
        new_dt = datetime(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=hour,
            minute=minute,
            second=0,
            microsecond=0,
        ).astimezone()
        dt = new_dt
    return dt


def item_instances(item, aft_dt, bef_dt=1, honor_skip=True):
    """
    Dates and datetimes decoded from the data store will all be aware and in the local timezone. aft_dt and bef_dt must therefore also be aware and in the local timezone.
    In dateutil, the starting datetime (dtstart) is not the first recurrence instance, unless it does fit in the specified rules.  Notice that you can easily get the original behavior by using a rruleset and adding the dtstart as an rdate recurrence.
    Each instance is a tuple (beginning datetime, ending datetime) where ending datetime is None unless the item is an event.

    Get instances from item falling on or after aft_dt and on or before bef_dt or, if bef_dt is an integer, n, get the first n instances after aft_dt. All datetimes will be returned with zero offsets.
    >>> item_eg = { "s": parse('2018-03-07 8am', tz="US/Eastern"), "e": timedelta(days=1, hours=5), "r": [ { "r": "w", "i": 2, "u": parse('2018-04-01 8am', tz="US/Eastern")}], "z": "US/Eastern", "itemtype": "*" }
    >>> item_eg
    {'s': DateTime(2018, 3, 7, 8, 0, 0, tzinfo=ZoneInfo('US/Eastern')), 'e': Duration(days=1, hours=5), 'r': [{'r': 'w', 'i': 2, 'u': DateTime(2018, 4, 1, 8, 0, 0, tzinfo=ZoneInfo('US/Eastern'))}], 'z': 'US/Eastern', 'itemtype': '*'}
    >>> item_instances(item_eg, parse('2018-03-01 12am', tz="US/Eastern"), parse('2018-04-01 12am', tz="US/Eastern"))
    [(DateTime(2018, 3, 7, 8, 0, 0, tzinfo=ZoneInfo('US/Eastern')), DateTime(2018, 3, 7, 23, 59, 59, 999999, tzinfo=ZoneInfo('US/Eastern'))), (DateTime(2018, 3, 8, 0, 0, 0, tzinfo=ZoneInfo('US/Eastern')), DateTime(2018, 3, 8, 13, 0, 0, tzinfo=ZoneInfo('US/Eastern'))), (DateTime(2018, 3, 21, 8, 0, 0, tzinfo=ZoneInfo('US/Eastern')), DateTime(2018, 3, 21, 23, 59, 59, 999999, tzinfo=ZoneInfo('US/Eastern'))), (DateTime(2018, 3, 22, 0, 0, 0, tzinfo=ZoneInfo('US/Eastern')), DateTime(2018, 3, 22, 13, 0, 0, tzinfo=ZoneInfo('US/Eastern')))]
    >>> item_eg['+'] = [parse("20180311T1000", tz="US/Eastern")]
    >>> item_eg['-'] = [parse("20180311T0800", tz="US/Eastern")]
    >>> item_eg['e'] = timedelta(hours=2)
    >>> item_eg
    {'s': DateTime(2018, 3, 7, 8, 0, 0, tzinfo=ZoneInfo('US/Eastern')), 'e': Duration(hours=2), 'r': [{'r': 'w', 'i': 2, 'u': DateTime(2018, 4, 1, 8, 0, 0, tzinfo=ZoneInfo('US/Eastern'))}], 'z': 'US/Eastern', 'itemtype': '*', '+': [DateTime(2018, 3, 11, 10, 0, 0, tzinfo=ZoneInfo('US/Eastern'))], '-': [DateTime(2018, 3, 11, 8, 0, 0, tzinfo=ZoneInfo('US/Eastern'))]}
    >>> item_instances(item_eg, parse('2018-03-01 12am'), parse('2018-04-01 12am'))
    [(DateTime(2018, 3, 7, 8, 0, 0, tzinfo=ZoneInfo('US/Eastern')), DateTime(2018, 3, 7, 10, 0, 0, tzinfo=ZoneInfo('US/Eastern'))), (DateTime(2018, 3, 11, 10, 0, 0, tzinfo=ZoneInfo('US/Eastern')), DateTime(2018, 3, 11, 12, 0, 0, tzinfo=ZoneInfo('US/Eastern'))), (DateTime(2018, 3, 21, 8, 0, 0, tzinfo=ZoneInfo('US/Eastern')), DateTime(2018, 3, 21, 10, 0, 0, tzinfo=ZoneInfo('US/Eastern')))]
    >>> del item_eg['e']
    >>> item_instances(item_eg, parse('2018-03-07 8:01am', tz="US/Eastern"))
    [(DateTime(2018, 3, 11, 10, 0, 0, tzinfo=ZoneInfo('US/Eastern')), None)]
    >>> del item_eg['r']
    >>> del item_eg['-']
    >>> del item_eg['+']
    >>> item_instances(item_eg, parse('2018-03-01 12am'), parse('2018-04-01 12am', tz="US/Eastern"))
    [(DateTime(2018, 3, 7, 8, 0, 0, tzinfo=ZoneInfo('US/Eastern')), None)]
    >>> item_eg = { "s": parse('2018-03-07 8am', tz="US/Eastern"), "r": [ { "r": "w", "w": MO(+2), "u": parse('2018-06-30 8am', tz="US/Eastern")}], "z": "US/Eastern", "itemtype": "*" }
    >>> item_eg
    {'s': DateTime(2018, 3, 7, 8, 0, 0, tzinfo=ZoneInfo('US/Eastern')), 'r': [{'r': 'w', 'w': MO(+2), 'u': DateTime(2018, 6, 30, 8, 0, 0, tzinfo=ZoneInfo('US/Eastern'))}], 'z': 'US/Eastern', 'itemtype': '*'}
    >>> item_instances(item_eg, parse('2018-03-01 12am', tz="US/Eastern"), parse('2018-04-01 12am', tz="US/Eastern"))
    [(DateTime(2018, 3, 12, 8, 0, 0, tzinfo=ZoneInfo('US/Eastern')), None), (DateTime(2018, 3, 19, 8, 0, 0, tzinfo=ZoneInfo('US/Eastern')), None), (DateTime(2018, 3, 26, 8, 0, 0, tzinfo=ZoneInfo('US/Eastern')), None)]

    Simple repetition:
    >>> item_eg = { "itemtype": "*", "s": parse('2018-11-15 8a', tz="US/Eastern"), "+": [parse('2018-11-16 10a', tz="US/Eastern"), parse('2018-11-18 3p', tz="US/Eastern"), parse('2018-11-27 8p', tz="US/Eastern")] }
    >>> item_instances(item_eg, parse('2018-11-17 9am', tz="US/Eastern"), 3)
    [(DateTime(2018, 11, 18, 15, 0, 0, tzinfo=ZoneInfo('US/Eastern')), None), (DateTime(2018, 11, 27, 20, 0, 0, tzinfo=ZoneInfo('US/Eastern')), None)]
    """

    if 's' not in item:
        if 'f' in item:
            return [(item['f'], None)]
        else:
            return []
    instances = []
    dtstart = item['s']
    if not (isinstance(dtstart, datetime) or isinstance(dtstart, date)):
        return []
    # This should not be necessary since the data store decodes dates as datetimes
    if isinstance(dtstart, date) and not isinstance(dtstart, datetime):
        dtstart = datetime(
            year=dtstart.year,
            month=dtstart.month,
            day=dtstart.day,
            hour=0,
            minute=0,
        ).astimezone()
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
    aft_dt = date_to_datetime(aft_dt).astimezone(ZoneInfo('UTC'))
    bef_dt = (
        bef_dt
        if isinstance(bef_dt, int)
        else date_to_datetime(bef_dt).astimezone(ZoneInfo('UTC'))
    )

    if 'r' in item:
        lofh = item['r']
        rset = dr.rruleset()

        for hsh in lofh:
            freq, kwd = rrule_args(hsh)
            kwd['dtstart'] = dtstart
            try:
                rset.rrule(dr.rrule(freq, **kwd))
            except Exception as e:
                logger.error(f'exception: {e}')
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
                    inc = False   # to get the next one
                else:
                    break
            if using_dates:
                instances = [x.date() for x in tmp if x] if tmp else []
            else:
                instances = [x for x in tmp if x] if tmp else []
        else:
            instances = [x for x in rset.between(aft_dt, bef_dt, inc=True)]

    elif '+' in item:
        # no @r but @+ => simple repetition
        s_hour = dtstart.hour
        s_minute = dtstart.minute
        # use hours and minutes from @s - they will be 0 if it is a date
        tmp = [date_to_datetime(x, s_hour, s_minute) for x in item['+']]
        tmp.append(dtstart)
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
    today = (
        datetime.now()
        .replace(hour=0, minute=0, second=0, microsecond=0)
        .astimezone()
    )
    # today = datetime.today().astimezone() tz=item.get('z', None))
    for instance in instances:
        if item['itemtype'] == '*' and 'e' in item:
            for pair in beg_ends(instance, item['e'], item.get('z', 'local')):
                pairs.append(pair)
        elif item['itemtype'] == '-':
            # handle tasks repeating or not, extent or not and overdue skip or not
            if item.get('o', 'k') == 's':
                if (instance.year, instance.month, instance.day) >= (
                    today.year,
                    today.month,
                    today.day,
                ):
                    if 'e' in item:
                        for pair in beg_ends(
                            instance, item['e'], item.get('z', 'local')
                        ):
                            pairs.append(pair)
                    else:
                        pairs.append((instance, None))
                    if pairs and honor_skip and settings['limit_skip_display']:
                        # only keep the first instance that falls during or after today/now
                        break
            elif 'e' in item:
                for pair in beg_ends(
                    instance, item['e'], item.get('z', 'local')
                ):
                    pairs.append(pair)
            else:
                pairs.append((instance, None))
        else:
            pairs.append((instance, None))
    pairs.sort(key=itemgetter(0))

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
    k=title,
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
       'f': DateTime(2018, 6, 20, 12, 0, 0, tzinfo=ZoneInfo('UTC')),
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
       'f': DateTime(2018, 6, 20, 12, 0, 0, tzinfo=ZoneInfo('UTC')),
       'i': '1',
       'j': 'Job One',
       'p': [],
       'req': [],
       'status': '✓',
       'summary': ' 1/0/2: Job One'},
      {'a': ['1d: d'],
       'f': DateTime(2018, 6, 21, 12, 0, 0, tzinfo=ZoneInfo('UTC')),
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
     DateTime(2018, 6, 22, 12, 0, 0, tzinfo=ZoneInfo('UTC')))

    Now add an 'r' entry for at_hsh.
    >>> data = [{'j': 'Job One', 's': '1d', 'a': '2d: d', 'b': 2, 'f': parse('6/20/18 12p', tz="US/Eastern")}, {'j': 'Job Two', 'a': '1d: d', 'b': 1, 'f': parse('6/21/18 12p', tz="US/Eastern")}, {'j': 'Job Three', 'a': '6h: d', 'f': parse('6/22/18 12p', tz="US/Eastern")}]
    >>> data
    [{'j': 'Job One', 's': '1d', 'a': '2d: d', 'b': 2, 'f': DateTime(2018, 6, 20, 12, 0, 0, tzinfo=ZoneInfo('US/Eastern'))}, {'j': 'Job Two', 'a': '1d: d', 'b': 1, 'f': DateTime(2018, 6, 21, 12, 0, 0, tzinfo=ZoneInfo('US/Eastern'))}, {'j': 'Job Three', 'a': '6h: d', 'f': DateTime(2018, 6, 22, 12, 0, 0, tzinfo=ZoneInfo('US/Eastern'))}]
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
     DateTime(2018, 6, 22, 12, 0, 0, tzinfo=ZoneInfo('US/Eastern')))
    """
    job_methods = (
        datetime_job_methods if 's' in at_hsh else undated_job_methods
    )
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
            msg.append(
                'Elements must be hashes. Cannot process: "{}"'.format(hsh)
            )
            continue
        if 'j' not in hsh:
            msg.append('error: j is required but missing')
        if first:
            # only do this once - for the first job
            first = False
            count = 0
            # set auto mode True if i is missing from the first job, otherwise set auto mode
            auto = 'i' not in hsh
        if auto:   # auto mode
            if count > 25:
                count = 0
                msg.append('error: at most 26 jobs are allowed in auto mode')
            if 'i' in hsh:
                msg.append('error: &i should not be specified in auto mode')
            if 'p' in hsh:
                msg.append('error: &p should not be specified in auto mode')
            # auto generate simple sequence for i: a, b, c, ... and
            # for p: a requires nothing, b requires a, c requires b, ...
            hsh['i'] = LOWERCASE[count]
            hsh['p'] = [LOWERCASE[count - 1]] if count > 0 else []
            count += 1
            req[hsh['i']] = deepcopy(hsh['p'])
            id

        else:    # manual mode
            if 'i' not in hsh:
                msg.append('error: &i is required for each job in manual mode')
            elif hsh['i'] in req:
                msg.append(f"error: '&i {hsh['i']}' has already been used")
            elif 'p' in hsh:
                if type(hsh['p']) == str:
                    req[hsh['i']] = [
                        x.strip() for x in hsh['p'].split(',') if x
                    ]
                else:
                    req[hsh['i']] = deepcopy(hsh['p'])
            else:
                req[hsh['i']] = []

        not_allowed = []
        for key in hsh.keys():
            if key in ['req', 'status', 'summary']:
                pass
            elif key == 'j':
                res['j'] = hsh['j']
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
            msg.append('invalid: {}'.format(', '.join(not_allowed)))

        if 'i' in hsh:
            id2hsh[hsh['i']] = res

    ids = [x for x in req]
    for i in ids:
        for j in req[i]:
            if j not in ids:
                msg.append('invalid id given in &p: {}'.format(j))

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
        msg.append(
            'error: circular dependency for jobs {}'.format(', '.join(tmp))
        )

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
            if id2hsh[i].get('f', None) is not None:
                # i is finished so remove it from the requirements for any
                # other jobs
                for j in ids:
                    if i in req[j]:
                        # since i is finished, remove it from j's requirements
                        req[j].remove(i)

    awf = [0, 0, 0]
    # set the job status for each job - f) finished, a) available or w) waiting
    for i in ids:
        if id2hsh[i].get('f', None) is not None:   # i is finished
            id2hsh[i]['status'] = FINISHED_CHAR
            awf[2] += 1
        elif req[i]:   # there are unfinished requirements for i
            id2hsh[i]['status'] = '+'
            awf[1] += 1
        else:   # there are no unfinished requirements for i
            id2hsh[i]['status'] = '-'
            awf[0] += 1

    for i in ids:
        try:
            id2hsh[i]['summary'] = '{} {}: {}'.format(
                summary, '/'.join([str(x) for x in awf]), id2hsh[i]['j']
            )
            id2hsh[i]['req'] = req[i]
            id2hsh[i]['i'] = i
        except Exception as e:
            logger.debug(f"exception: {e = }")

    if msg:
        logger.warning(f'{msg}')
        return False, msg, None
    return True, [id2hsh[i] for i in ids], last_completion


#######################
### end jobs setup ####
#######################


########################
### start week/month ###
########################

# def get_period(dt=datetime.now(), weeks_before=3, weeks_after=9):
#     """
#     Return the begining and ending of the period that includes the weeks in current month plus the weeks in the prior *months_before* and the weeks in the subsequent *months_after*. The period will begin at 0 hours on the relevant Monday and end at 23:59:59 hours on the relevant Sunday.
#     >>> get_period(datetime(2018, 12, 15, 0, 0, tz='US/Eastern'))
#     (DateTime(2018, 11, 19, 0, 0, 0, tzinfo=ZoneInfo('US/Eastern')), DateTime(2019, 2, 17, 23, 59, 59, 999999, tzinfo=ZoneInfo('US/Eastern')))
#     """
#     beg = dt.start_of('week').subtract(weeks=weeks_before).start_of('week')
#     end = dt.start_of('week').add(weeks=weeks_after).end_of('week')
#     return (beg, end)


def get_period(dt=datetime.now(), weeks_before=3, weeks_after=9):
    """
    Return the begining and ending of the period that includes the weeks in current month plus the weeks in the prior *months_before* and the weeks in the subsequent *months_after*. The period will begin at 0 hours on the relevant Monday and end at 23:59:59 hours on the relevant Sunday.
    >>> get_period(datetime(2018, 12, 15, 0, 0, tz='US/Eastern'))
    (DateTime(2018, 11, 19, 0, 0, 0, tzinfo=ZoneInfo('US/Eastern')), DateTime(2019, 2, 17, 23, 59, 59, 999999, tzinfo=ZoneInfo('US/Eastern')))
    """
    # Find the weekday (0 for Monday, 6 for Sunday)
    weekday = dt.weekday()

    days_to_subtract = weekday + 7 * weeks_before

    days_to_add = 7 - weekday + 7 * weeks_after

    # Subtract the days to get the previous Monday
    beg = dt - timedelta(days=days_to_subtract)
    end = dt + timedelta(days=days_to_add)

    return (beg, end)


def iso_year_start(iso_year):
    """
    Return the gregorian calendar date of the first day of the given ISO year.
    >>> iso_year_start(2017)
    Date(2017, 1, 2)
    >>> iso_year_start(2018)
    Date(2018, 1, 1)
    """
    fourth_jan = date(iso_year, 1, 4)
    delta = timedelta(days=fourth_jan.isoweekday() - 1)
    return fourth_jan - delta


def iso_to_gregorian(ywd):
    """
    Return the gregorian calendar date for the given year, week and day.
    >>> iso_to_gregorian((2018, 7, 3))
    Date(2018, 2, 14)
    """
    year_start = iso_year_start(ywd[0])
    return year_start + timedelta(days=ywd[2] - 1, weeks=ywd[1] - 1)


def getWeekNum(dt=datetime.now()):
    """
    Return the year and week number for the datetime.
    >>> getWeekNum(datetime(2018, 2, 14, 10, 30))
    (2018, 7)
    >>> getWeekNum(date(2018, 2, 14))
    (2018, 7)
    >>> getWeekNum(date(2018, 12, 31))
    (2019, 1)
    """
    return dt.isocalendar()[:2]


def nextWeek(yw):
    """
    >>> nextWeek((2015,53))
    (2016, 1)
    """
    return (iso_to_gregorian((*yw, 7)) + timedelta(days=1)).isocalendar()[:2]


def prevWeek(yw):
    """
    >>> prevWeek((2016,1))
    (2015, 53)
    """
    return (iso_to_gregorian((*yw, 1)) - timedelta(days=1)).isocalendar()[:2]


def getWeeksForMonth(ym):
    """
    Return the month and week numbrers for the week containing the first day of the month and the 5 following weeks.
    >>> getWeeksForMonth((2018, 3))
    [(2018, 9), (2018, 10), (2018, 11), (2018, 12), (2018, 13), (2018, 14)]
    """
    wp = date(ym[0], ym[1], 1).isocalendar()[:2]
    wl = [wp]
    for _ in range(5):
        wn = nextWeek(wp)
        wl.append(wn)
        wp = wn

    return wl


def getWeekNumbers(dt=datetime.now(), bef=3, after=9):
    """
    >>> dt = date(2018, 12, 7)
    >>> getWeekNumbers(dt)
    [(2018, 46), (2018, 47), (2018, 48), (2018, 49), (2018, 50), (2018, 51), (2018, 52), (2019, 1), (2019, 2), (2019, 3), (2019, 4), (2019, 5), (2019, 6)]
    """
    # yw = dt.add(days=-bef*7).isocalendar()[:2]
    yw = (dt - timedelta(days=bef * 7)).isocalendar()[:2]
    weeks = [yw]
    for _ in range(1, bef + after + 1):
        yw = nextWeek(yw)
        weeks.append(yw)
    return weeks


######################
### end week/month ###
######################


def period_from_fmt(s, z='local'):
    """ """
    start, end = [
        datetime.strptime(x.strip(), '%Y%m%dT%H%M', z) for x in s.split('->')
    ]
    return Period(start, end)


def pen_from_fmt(s, z='local'):
    """
    >>> pen_from_fmt("20120622T0000")
    Date(2012, 6, 22)
    """
    dt = datetime.strptime(s, '%Y%m%dT%H%M', z)
    if z in ['local', 'Factory'] and dt.hour == dt.minute == 0:
        dt = dt.date()
    return dt


def drop_zero_minutes(dt):
    """
    >>> drop_zero_minutes(parse('2018-03-07 10am'))
    '10'
    >>> drop_zero_minutes(parse('2018-03-07 2:45pm'))
    '2:45'
    """
    ampm = settings['ampm']
    show_minutes = settings['show_minutes']
    if show_minutes:
        if ampm:
            return dt.strftime('%-I:%M').rstrip('M').lower()
        else:
            return dt.strftime('%H:%M')
    else:
        if dt.minute == 0:
            if ampm:
                return dt.strftime('%-I')
            else:
                return dt.strftime('%H')
        else:
            if ampm:
                return dt.strftime('%-I:%M').rstrip('M').lower()
            else:
                return dt.strftime('%H:%M')


def fmt_extent(beg_dt: datetime, end_dt: datetime):
    """
    Format the beginning to ending times to display for a reminder with an extent (both @s and @e).
    >>> beg_dt = parse('2018-03-07 10am')
    >>> end_dt = parse('2018-03-07 11:30am')
    >>> fmt_extent(beg_dt, end_dt)
    '10-11:30am'
    >>> end_dt = parse('2018-03-07 2pm')
    >>> fmt_extent(beg_dt, end_dt)
    '10am-2pm'
    """
    beg_suffix = end_suffix = ''
    ampm = settings['ampm']
    if not (isinstance(beg_dt, datetime) and isinstance(end_dt, datetime)):
        return 'xxx'

    if ampm:
        diff = beg_dt.hour < 12 and end_dt.hour >= 12
        end_suffix = end_dt.strftime('%p').lower().rstrip('m')
        if diff:
            beg_suffix = beg_dt.strftime('%p').lower().rstrip('m')

    beg_fmt = drop_zero_minutes(beg_dt)
    end_fmt = drop_zero_minutes(end_dt)
    if ampm:
        beg_fmt = beg_fmt.lstrip('0')
        end_fmt = end_fmt.lstrip('0')

    return f'{beg_fmt}{beg_suffix}-{end_fmt}{end_suffix}'


def fmt_time(dt, ignore_midnight=True):
    ampm = settings['ampm']
    show_minutes = settings['show_minutes']
    if ignore_midnight and dt.hour == 0 and dt.minute == 0 and dt.second == 0:
        return ''
    suffix = dt.strftime('%p').lower().rstrip('m') if ampm else ''

    dt_fmt = drop_zero_minutes(dt)
    if ampm:
        dt_fmt = dt_fmt.lstrip('0')
    return f'{dt_fmt}{suffix}'


def beg_ends(starting_dt, extent_duration, z=None):
    """
    >>> starting = parse('2018-03-02 9am')
    >>> beg_ends(starting, parse_duration('2d2h20m')[1])
    [(DateTime(2018, 3, 2, 9, 0, 0, tzinfo=ZoneInfo('UTC')), DateTime(2018, 3, 2, 23, 59, 59, 999999, tzinfo=ZoneInfo('UTC'))), (DateTime(2018, 3, 3, 0, 0, 0, tzinfo=ZoneInfo('UTC')), DateTime(2018, 3, 3, 23, 59, 59, 999999, tzinfo=ZoneInfo('UTC'))), (DateTime(2018, 3, 4, 0, 0, 0, tzinfo=ZoneInfo('UTC')), DateTime(2018, 3, 4, 11, 20, 0, tzinfo=ZoneInfo('UTC')))]
    >>> beg_ends(starting, parse_duration('8h20m')[1])
    [(DateTime(2018, 3, 2, 9, 0, 0, tzinfo=ZoneInfo('UTC')), DateTime(2018, 3, 2, 17, 20, 0, tzinfo=ZoneInfo('UTC')))]
    >>> beg_ends(parse('2022-12-29 12am'), parse_duration('1d')[1])
    [(DateTime(2018, 3, 2, 9, 0, 0, tzinfo=ZoneInfo('UTC')), DateTime(2018, 3, 2, 17, 20, 0, tzinfo=ZoneInfo('UTC')))]
    """

    pairs = []
    beg = starting_dt
    ending = starting_dt + extent_duration
    while ending.date() > beg.date():
        end = beg.replace(hour=23, minute=59)
        pairs.append((beg, end))
        beg = (beg + timedelta(days=1)).replace(hour=0, minute=0)
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
    """ """
    try:
        if edit:
            return jinja_entry_template.render(h=item)
        else:
            return jinja_display_template.render(h=item)

    except Exception as e:
        logger.error(f'item_details: {e} {item}')


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
    wkbeg = datetime.strptime(f'{dt_year} {str(dt_week)} 1', '%Y %W %w').date()
    wkend = datetime.strptime(f'{dt_year} {str(dt_week)} 0', '%Y %W %w').date()
    if settings['dayfirst']:
        week_end = wkend.strftime('%-d %b')
        week_begin = (
            wkbeg.strftime('%-d')
            if wkbeg.month == wkend.month
            else wkbeg.strftime('%-d %b')
        )
    else:
        day_beg = wkbeg.strftime('%-d')
        day_end = wkend.strftime('%-d')
        week_end = (
            day_end
            if wkbeg.month == wkend.month
            else wkend.strftime('%b') + f' {day_end}'
        )
        week_begin = wkbeg.strftime('%b') + f' {day_beg}'

    return f'{week_begin} - {week_end}, {dt_year} #{dt_week}'


def get_item(doc_id):
    """
    Return the hash correponding to doc_id.
    """
    pass


def relevant(
    db,
    now=datetime.now(),
    repeat_list=[],
    pinned_list=[],
    link_list=[],
    konnected=[],
    timers={},
):
    """
    Collect the relevant datetimes, inbox, pastdues, beginbys and alerts. Note that jobs are only relevant for the relevant instance of a task
    Called by dataview.refreshRelevant
    """
    logger.debug(f"### Relevant ###")

    # wkday_fmt = '%a %d %b' if settings['dayfirst'] else '%a %b %d'
    dirty = False
    width = shutil.get_terminal_size()[0] - 3
    summary_width = width - 3
    ampm = settings['ampm']
    rhc_width = 15 if ampm else 11
    num_remaining = ''

    today = (
        datetime.now()
        .replace(hour=0, minute=0, second=0, microsecond=0)
        .astimezone()
    )
    tomorrow = today + DAY
    inbox_fmt = today.strftime('%Y%m%d    ')   # first
    pastdue_fmt = today.strftime('%Y%m%d^^^^')   # after all day and timed
    begby_fmt = today.strftime('%Y%m%d~~~~')   # after past due

    id2relevant = {}
    inbox = []
    pastdue = []
    beginbys = []
    alerts = []
    current = []
    now = datetime.now().astimezone()

    for item in db:
        instance_interval = []
        possible_beginby = None
        possible_alerts = []
        all_tds = []
        relevant = None
        dtstart = None
        doc_id = item.doc_id
        rset = dr.rruleset()
        if 'itemtype' not in item:
            logger.warning(f'no itemtype: {item}')
            item['itemtype'] = '?'
            # continue
        if 'g' in item:
            if doc_id not in link_list:
                link_list.append(doc_id)
        else:
            if doc_id in link_list:
                link_list.remove(doc_id)
        if '+' in item or 'r' in item:
            if doc_id not in repeat_list:
                repeat_list.append(doc_id)
        else:
            if doc_id in repeat_list:
                repeat_list.remove(doc_id)

        summary = item.get('summary', '~')
        flags = get_flags(
            doc_id, repeat_list, link_list, konnected, pinned_list, timers
        )
        if item['itemtype'] == '!':
            inbox.append([0, summary, item.doc_id, None, None])
            relevant = today

        elif 'f' in item:
            relevant = item['f'].end
            if isinstance(relevant, date) and not isinstance(
                relevant, datetime
            ):
                relevant = datetime(
                    year=relevant.year,
                    month=relevant.month,
                    day=relevant.day,
                    hour=23,
                    minute=59,
                ).astimezone()

        elif 's' in item and not item['s']:
            logger.error(f"bad @s in item['s'] for {doc_id}: {item['s']}; item: {item}")

        elif 's' in item and item['s']:
            dtstart = date_to_datetime(item['s'])
            # has_a = 'a' in item
            # has_b = 'b' in item
            if 'b' in item:
                days = int(item['b']) * DAY
                all_tds.extend([DAY, days])
                possible_beginby = days

            if 'a' in item:
                # alerts
                for alert in item['a']:
                    tds = alert[0]
                    cmd = alert[1]
                    all_tds.extend(tds)

                    for td in tds:
                        # td > 0m => earlier than startdt; dt < 0m => later than startdt
                        possible_alerts.append([td, cmd])

            # this catches all alerts and beginbys for the item
            if all_tds:
                instance_interval = [
                    today + min(all_tds),
                    tomorrow + max(all_tds),
                ]

            if 'r' in item or '+' in item:
                lofh = item.get('r', [])
                rset = dr.rruleset()

                for hsh in lofh:
                    freq, kwd = rrule_args(hsh)
                    kwd['dtstart'] = dtstart
                    try:
                        rset.rrule(dr.rrule(freq, **kwd))
                    except Exception as e:
                        print('Error processing:')
                        print('  ', freq, kwd)
                        print(e)
                        print(item)
                        break

                if '-' in item:
                    for dt in item['-']:
                        dt = date_to_datetime(dt)
                        # if type(dt) == date:
                        #     dt = datetime(year=dt.year, month=dt.month, day=dt.day, hour=0, minute=0, tz='local')
                        rset.exdate(dt)

                if '+' in item:
                    for dt in item['+']:
                        dt = date_to_datetime(dt)
                        rset.rdate(dt)

                if item['itemtype'] == '-':
                    switch = item.get('o', 'k')
                    if switch == 's':
                        cur = date_to_datetime(item['s'])
                        # make 'all day' tasks not pastdue until one minute before midnight
                        delta = (
                            timedelta(hours=23, minutes=59) if (cur.hour == 0 and cur.minute == 0) else ZERO
                        )
                        plus_dates = item.get('+', [])
                        if cur + delta < now:
                            # we need to update @s
                            relevant = rset.after(now, inc=True)
                            while relevant in plus_dates:
                                relevant = rset.after(relevant, inc=False)
                            item['s'] = relevant
                            item.setdefault('h', []).append(
                                    Period(cur + ONEMIN, cur))
                            num_finished = settings.get('num_finished', 0)
                            if num_finished and len(item['h']) > num_finished:
                                h = item['h']
                                h.sort(key=sortprd)
                                item['h'] = h[-num_finished:]
                            update_db(db, item.doc_id, item)
                        elif plus_dates:
                            # @s is ok but @+ may need updating
                            changed = False
                            for dt in plus_dates:
                                if dt >= now:
                                    continue
                                delta = (
                                    timedelta(hours=23, minutes=59) if (dt.hour == 0 and dt.minute == 0) else ZERO
                                )
                                if dt + delta < now:
                                    item.setdefault('h', []).append(
                                            Period(dt + ONEMIN, dt))
                                    item['+'].remove(dt)
                                    changed = True
                            if len(item['+']) > 0:
                                if item['+'][0] < cur:
                                    relevant = item['+'][0]
                                else:
                                    relevant = cur
                            else:
                                del item['+']
                                changed = True
                            if changed:
                                update_db(db, item.doc_id, item)
                        else:
                            relevant = cur

                    else:   # k or r
                        try:
                            relevant = rset.after(today, inc=True)
                        except Exception as e:
                            logger.debug(f"Exception: {e}\nissue with today: {today} ({type(today)}) or rset: {rset}\nskipping {item}")
                            continue

                        already_done = [x.end for x in item.get('h', [])]
                        # relevant will be the first instance after 12am today
                        # it will be the @s entry for the updated repeating item
                        # these are @s entries for the instances to be preserved
                        between = rset.between(
                            dtstart, today - ONEMIN, inc=True
                        )
                        # remaining = [x for x in between if x not in already_done and x != dtstart]
                        remaining = [
                            x for x in between if x not in already_done
                        ]
                        # once instances have been created, between will be empty until
                        # the current date falls after item['s'] and relevant is reset
                        num_remaining = (
                            f'({len(remaining)})' if remaining else ''
                        )
                        sum_abbr = item['summary'][:summary_width]
                        summary = f'{sum_abbr} {num_remaining}'
                        if dtstart.date() < today.date() and 'j' not in item:
                            pastdue.append(
                                [
                                    (dtstart.date() - today.date()).days,
                                    summary,
                                    item.doc_id,
                                    None,
                                    None,
                                ]
                            )
                else:
                    # get the first instance after today
                    try:
                        relevant = rset.after(today, inc=True)
                    except Exception as e:
                        logger.error(f'error processing {item}; {repr(e)}')
                    if not relevant:
                        relevant = rset.before(today, inc=True)

                # rset
                if instance_interval:
                    instances = rset.between(
                        instance_interval[0], instance_interval[1], inc=True
                    )
                    if possible_beginby:
                        for instance in instances:
                            if (
                                ZERO
                                < instance.date() - today.date()
                                <= possible_beginby
                            ):
                                doc_id = item.doc_id
                                if 'r' in item:
                                    # use the freq from the first recurrence rule
                                    freq = item['r'][0].get('r', 'y')
                                else:
                                    freq = 'y'
                                summary = set_summary(
                                    summary,
                                    item.get('s', None),
                                    instance.date(),
                                    freq,
                                )
                                beginbys.append(
                                    [
                                        (instance.date() - today.date()).days,
                                        summary,
                                        item.doc_id,
                                        None,
                                        instance,
                                    ]
                                )
                    if possible_alerts:
                        for instance in instances:
                            for possible_alert in possible_alerts:
                                if (
                                    today
                                    <= instance - possible_alert[0]
                                    <= tomorrow
                                ):
                                    alerts.append(
                                        [
                                            instance - possible_alert[0],
                                            instance,
                                            possible_alert[1],
                                            item['itemtype'],
                                            item['summary'],
                                            item.doc_id,
                                        ]
                                    )

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
                        # if today + DAY <= instance <= tomorrow + possible_beginby:
                        if (
                            ZERO
                            < instance.date() - today.date()
                            <= possible_beginby
                        ):
                            beginbys.append(
                                [
                                    (instance.date() - today.date()).days,
                                    summary,
                                    item.doc_id,
                                    None,
                                    instance,
                                ]
                            )
                if possible_alerts:
                    for instance in aft + bef:
                        for possible_alert in possible_alerts:
                            if (
                                today
                                <= instance - possible_alert[0]
                                <= tomorrow
                            ):
                                alerts.append(
                                    [
                                        instance - possible_alert[0],
                                        instance,
                                        possible_alert[1],
                                        item['itemtype'],
                                        item['summary'],
                                        item.doc_id,
                                    ]
                                )

            else:
                # 's' but not 'r' or '+'
                relevant = dtstart
                if (
                    possible_beginby
                    and ZERO
                    < relevant.date() - today.date()
                    <= possible_beginby
                ):
                    beginbys.append(
                        [
                            (relevant.date() - today.date()).days,
                            summary,
                            item.doc_id,
                            None,
                            None,
                        ]
                    )
                if possible_alerts:
                    for possible_alert in possible_alerts:
                        if today <= dtstart - possible_alert[0] <= tomorrow:
                            alerts.append(
                                [
                                    dtstart - possible_alert[0],
                                    dtstart,
                                    possible_alert[1],
                                    item['itemtype'],
                                    item['summary'],
                                    item.doc_id,
                                ]
                            )
        else:
            # no 's', no 'f'
            relevant = None

        if not relevant:
            continue

        pastdue_jobs = False
        if 'j' in item and 'f' not in item:
            # jobs only for the relevant instance of unfinished tasks
            for job in item['j']:
                job_id = job.get('i')
                if 'f' in job:
                    continue
                # adjust job starting time if 's' in job
                job_summary = (
                    f"{job.get('summary', '')[:summary_width]} {num_remaining}"
                )
                jobstart = dtstart - job.get('s', ZERO)
                if (
                    jobstart.date() < today.date()
                    and job.get('status', None) == '-'
                ):
                    pastdue_jobs = True
                    pastdue.append(
                        [
                            (jobstart.date() - today.date()).days,
                            job_summary,
                            item.doc_id,
                            job_id,
                            None,
                        ]
                    )
                if 'b' in job:
                    days = int(job['b']) * DAY
                    if today + DAY <= jobstart <= tomorrow + days:
                        beginbys.append(
                            [
                                (jobstart.date() - today.date()).days,
                                job_summary,
                                item.doc_id,
                                job_id,
                                None,
                            ]
                        )
                if 'a' in job:
                    for alert in job['a']:
                        for td in alert[0]:
                            if today <= jobstart - td <= tomorrow:
                                alerts.append(
                                    [
                                        dtstart - td,
                                        dtstart,
                                        alert[1],
                                        '-',
                                        job['summary'],
                                        item.doc_id,
                                        job_id,
                                        None,
                                    ]
                                )

        id2relevant[item.doc_id] = relevant

        # if item['itemtype'] == '-' and 'f' not in item and relevant.date() < today.date():
        if (
            item['itemtype'] == '-'
            and 'f' not in item
            and 'j' not in item
            and relevant.date() < today.date()
        ):
            pastdue.append(
                [
                    (relevant.date() - today.date()).days,
                    summary,
                    item.doc_id,
                    None,
                    None,
                ]
            )

    inbox.sort()
    pastdue.sort()
    beginbys.sort()
    alerts.sort()
    # alerts: alert datetime, start datetime, commands, summary, doc_id
    week = today.isocalendar()[:2]
    day = (format_wkday(today),)
    for item in inbox:
        item_0 = ' '
        rhc = item_0.center(rhc_width, ' ')
        doc_id = item[2]
        flags = get_flags(
            doc_id, repeat_list, link_list, konnected, pinned_list, timers
        )
        current.append(
            {
                'id': item[2],
                'job': None,
                'instance': None,
                'sort': (inbox_fmt, 1),
                'week': week,
                'day': day,
                'columns': ['!', item[1], flags, rhc, doc_id],
            }
        )

    for item in pastdue:
        item_0 = str(item[0]) if item[0] in item else ''
        rhc = item_0
        doc_id = item[2]
        job_id = item[3] if item[3] else ''
        flags = get_flags(
            doc_id, repeat_list, link_list, konnected, pinned_list, timers
        )
        try:
            current.append(
                {
                    'id': item[2],
                    'job': item[3],
                    'instance': item[4],
                    'sort': (pastdue_fmt, 2, item[0]),
                    'week': week,
                    'day': day,
                    'columns': [
                        '<',
                        f'{rhc + "  " if rhc else ""}{item[1]}',
                        flags,
                        '',
                        (doc_id, item[4], item[3]),
                    ],
                }
            )
        except Exception as e:
            logger.warning(f'could not append item: {item}; e: {e}')

    for item in beginbys:
        if item[0] in item:
            item_0 = str(item[0]) if item[0] <= 0 else f'+{item[0]}'
        else:
            item_0 = ''
        rhc = item_0 + '  ' if item[0] else ''
        doc_id = item[2]
        flags = get_flags(
            doc_id, repeat_list, link_list, konnected, pinned_list, timers
        )
        current.append(
            {
                'id': item[2],
                'job': item[3],
                'instance': item[4],
                'sort': (begby_fmt, 3, item[0]),
                'week': week,
                'day': day,
                'columns': ['>', rhc + item[1], flags, '', doc_id],
            }
        )
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


def update_db(db, doc_id, hsh={}):
    old = db.get(doc_id=doc_id)
    if not old:
        logger.error(
            f'Could not get document corresponding to doc_id {doc_id}'
        )
        return
    if old == hsh:
        return
    hsh['modified'] = datetime.now()
    logger.debug(f"starting db.update")
    try:
        db.update(db_replace(hsh), doc_ids=[doc_id])
    except Exception as e:
        logger.error(
            f'Error updating document corresponding to doc_id {doc_id}\nhsh {hsh}\nexception: {repr(e)}'
        )


def write_back(db, docs):
    logger.debug(f"starting write_back")
    for doc in docs:
        try:
            doc_id = doc.doc_id
            update_db(db, doc_id, doc)
        except Exception as e:
            logger.error(f'write_back exception: {e}')


def insert_db(db, hsh={}):
    """
    Assume hsh has been vetted.
    """
    if not hsh:

        return
    hsh['created'] = datetime.now()
    try:
        db.insert(hsh)
    except Exception as e:
        logger.error(f'Error updating database:\nhsh {hsh}\ne {repr(e)}')


def show_forthcoming(
    db,
    id2relevant,
    repeat_list=[],
    pinned_list=[],
    link_list=[],
    konnected=[],
    timers={},
):
    width = shutil.get_terminal_size()[0] - 3
    summary_width = width - 19
    rows = []
    today = datetime.now().replace(hour=0, minute=0, second=0).astimezone()
    md_fmt = '%d/%m' if settings['dayfirst'] else '%m/%d'
    for item in db:
        if item.doc_id not in id2relevant:
            continue

        # don't show completed tasks in forthcoming?
        if 'f' in item:
            continue

        doc_id = item.doc_id
        if 'r' in item:
            # use the freq from the first recurrence rule
            freq = item['r'][0].get('r', 'y')
        else:
            freq = 'y'
        relevant = id2relevant[item.doc_id]
        if relevant < today:
            continue
        year = relevant.strftime('%b %Y')
        monthday = relevant.strftime('%-d')
        time = fmt_time(relevant)
        # rhc = f"{monthday:>6} {time:^7}".ljust(14, ' ')
        rhc = f'{monthday : >2} {time} ' if time else f'{monthday : >2} '

        itemtype = FINISHED_CHAR if 'f' in item else item['itemtype']
        summary = set_summary(
            item['summary'], item.get('s', None), relevant, freq
        )
        flags = get_flags(
            doc_id, repeat_list, link_list, konnected, pinned_list, timers
        )

        rows.append(
            {
                'id': doc_id,
                'sort': relevant,
                'path': year,
                'values': [itemtype, f'{rhc}{summary}', flags, '', doc_id],
            }
        )

    rows.sort(key=itemgetter('sort'))
    rdict = NDict()
    for row in rows:
        path = row['path']
        values = row['values']
        rdict.add(path, values)
    tree, row2id = rdict.as_tree(rdict)
    return tree, row2id


def get_flags(
    doc_id,
    repeat_list=[],
    link_list=[],
    konnected=[],
    pinned_list=[],
    timers={},
):
    """ """
    flags = ''
    if doc_id in repeat_list:
        flags += REPS
    if doc_id in link_list:
        flags += LINK_CHAR
    if doc_id in konnected:
        flags += KONNECT_CHAR
    if doc_id in pinned_list:
        flags += PIN_CHAR
    if doc_id in timers:
        flags += 't'
    return flags


def show_query_items(
    text,
    items=[],
    repeat_list=[],
    pinned_list=[],
    link_list=[],
    konnected=[],
    timers={},
):
    rows = []
    if not items or not isinstance(items, list):
        return f'query: {text}\n   none matching', {}
    item_count = f' [{len(items)}]'
    width = shutil.get_terminal_size()[0] - 3
    summary_width = width - len(item_count) - 7
    for item in items:
        mt = item.get('modified', None)
        if mt is not None:
            dt, label = mt, 'm'
        else:
            dt, label = item.get('created', None), 'c'
        doc_id = item.doc_id
        year = dt.strftime('%Y')
        itemtype = FINISHED_CHAR if 'f' in item else item['itemtype']
        summary = item['summary']
        flags = get_flags(
            doc_id, repeat_list, link_list, konnected, pinned_list, timers
        )
        rhc = f'{doc_id: >6}'
        rows.append(
            {
                'sort': dt,
                'path': year,
                'values': [itemtype, summary, flags, rhc, doc_id],
            }
        )
    # if len(rows) == 1:
    #     logger.debug(f"rows[0]: {rows[0]}")
    #     res = rows[0]
    #     return item_details(res), {}

    rdict = NDict()
    path = f'query: {text[:summary_width]}{item_count}'
    for row in rows:
        values = row['values']
        rdict.add(path, values)
    tree, row2id = rdict.as_tree(rdict)
    return tree, row2id


def show_history(
    db,
    reverse=True,
    repeat_list=[],
    pinned_list=[],
    link_list=[],
    konnected=[],
    timers={},
):
    md_fmt = '%d/%m' if settings['dayfirst'] else '%m/%d'
    ymd_fmt = f'%Y/{md_fmt}' if settings['yearfirst'] else f'{md_fmt}/%Y'
    width = shutil.get_terminal_size()[0] - 3
    rows = []
    # summary_width = width - 14
    title = 'reverse sorted by m)odified else c)created'
    for item in db:
        mt = item.get('modified', None)
        if mt is not None:
            dt, label = mt, 'm'
        else:
            dt, label = item.get('created', None), 'c'
        if dt is not None:
            doc_id = item.doc_id
            path = dt.strftime('%b %Y')
            d = dt.strftime('%-d')
            rhc = f'{d : >2} {label} '
            itemtype = (
                FINISHED_CHAR if 'f' in item else item.get('itemtype', '?')
            )
            summary = item.get('summary', '~')
            flags = get_flags(
                doc_id, repeat_list, link_list, konnected, pinned_list, timers
            )
            rows.append(
                {
                    'sort': dt,
                    'path': path,
                    'values': [itemtype, rhc + summary, flags, '', doc_id],
                }
            )
    try:
        rows.sort(key=itemgetter('sort'), reverse=reverse)
    except Exception as e:
        logger.error(f"sort exception: {e}: {[type(x['sort']) for x in rows]}")
    rdict = NDict()
    for row in rows:
        path = row['path']
        values = row['values']
        rdict.add(path, values)
    tree, row2id = rdict.as_tree(rdict)

    # return f"{title}\n" + tree, row2id
    return tree, row2id


def show_review(
    db, repeat_list=[], pinned_list=[], link_list=[], konnected=[], timers={}
):
    """
    Unfinished, undated tasks and jobs
    """
    width = shutil.get_terminal_size()[0] - 3
    rows = []
    locations = set([])
    summary_width = width - 18
    for item in db:
        if (
            item.get('itemtype', None) not in ['-']
            or 's' in item
            or 'f' in item
        ):
            continue
        doc_id = item.doc_id
        rhc = item.get('l', '~')[:10].ljust(10, ' ')
        itemtype = item['itemtype']
        summary = item['summary']
        flags = get_flags(
            doc_id, repeat_list, link_list, konnected, pinned_list, timers
        )
        modified = item['modified'] if 'modified' in item else item['created']

        weeks = (
            datetime.now().astimezone(ZoneInfo('UTC')) - modified
        ).days // 7
        if weeks == 0:
            wkfmt = ' This week'
        elif weeks == 1:
            wkfmt = ' Last week'
        else:
            wkfmt = f' {weeks} weeks ago'
        rows.append(
            {
                'path': wkfmt,
                'sort': modified,
                'values': [
                    itemtype,
                    summary,
                    flags,
                    rhc,  # location
                    doc_id,
                ],
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
    tree, row2id = rdict.as_tree(rdict)
    return tree, row2id


def show_konnected(
    db,
    repeat_list=[],
    pinned_list=[],
    link_list=[],
    konnected=[],
    timers={},
    selected_id=None,
    konnections_from={},
    konnections_to={},
):
    """
    Show list of items with konnections
    """
    konnected.sort()
    count = 0
    id2row = {}
    relevant = []
    for id in konnected:
        item = db.get(doc_id=id)
        if not item:
            continue
        count += 1
        id2row[id] = count
        relevant.append([id, item])

    rows = []
    for path, item in relevant:
        itemtype = FINISHED_CHAR if 'f' in item else item.get('itemtype', '?')
        summary = item['summary']
        doc_id = item.doc_id
        # flags = get_flags(
            # doc_id, repeat_list, link_list, konnected, pinned_list, timers
        # )

        rows.append(
            {
                'path': '',
                'sort': (doc_id),
                'values': [
                    itemtype,
                    summary,
                    f"↓{len(konnections_to.get(doc_id,[]))}#{doc_id}↓{len(konnections_from.get(doc_id, []))}",
                    '',
                    doc_id,
                ],
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
    tree, row2id = rdict.as_tree(rdict)
    tree = re.sub(r'^\s*\n', f" konnected items [{len(rows)}]\n", tree, 1)
    return tree, row2id


def show_next(
    db, repeat_list=[], pinned_list=[], link_list=[], konnected=[], timers={}
):
    """
    Unfinished, undated tasks and jobs
    """
    # width = settings['keep_current'][1]
    global current_hsh
    mk_next = settings['keep_current'][0] > 0
    next_width = settings['keep_current'][1] - 1

    width = shutil.get_terminal_size()[0] - 3
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
        if (
            item.get('itemtype', None) not in ['-']
            or 's' in item
            or 'f' in item
        ):
            continue
        doc_id = item.doc_id
        flags = get_flags(
            doc_id, repeat_list, link_list, konnected, pinned_list, timers
        )
        if 'j' in item:
            task_location = item.get('l', '~')
            priority = int(item.get('p', 0))
            sort_priority = 4 - int(priority)
            show_priority = str(priority) if priority > 0 else ''
            for job in item['j']:
                if job.get('f', None) is not None:
                    # show completed jobs only in completed view
                    continue
                location = job.get('l', task_location)
                extent = job.get('e', '')
                extent = format_duration(extent) if extent else ''
                status = 0 if job.get('status') == '-' else 1
                # status 1 -> waiting, status 0 -> available
                rhc = ' '.join([show_priority, extent]).center(7, ' ')
                summary = job.get('summary')
                job_id = job.get('i', None)
                job_sort = str(job_id)
                rows.append(
                    {
                        'id': doc_id,
                        'job': job_id,
                        'instance': None,
                        'sort': (
                            location,
                            status,
                            sort_priority,
                            job_sort,
                            job.get('summary', ''),
                        ),
                        'location': location,
                        'columns': [
                            job.get('status', ''),
                            summary,
                            flags,
                            rhc,
                            (doc_id, None, job_id),
                        ],
                    }
                )
        else:
            location = item.get('l', '~')
            priority = int(item.get('p', 0))
            extent = item.get('e', '')
            extent = format_duration(extent) if extent else ''
            sort_priority = 4 - int(priority)
            show_priority = str(priority) if priority > 0 else ''
            rhc = ' '.join([show_priority, extent]).center(7, ' ')
            summary = item['summary']
            rows.append(
                {
                    'id': doc_id,
                    'job': None,
                    'instance': None,
                    'sort': (location, sort_priority, extent, item['summary']),
                    'location': location,
                    'columns': [
                        item['itemtype'],
                        summary,
                        flags,
                        rhc,
                        (doc_id, None, None),
                    ],
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

    tree, row2id = rdict.as_tree(rdict)

    ctree = None
    if mk_next:
        cdict = NDict(compact=True, width=next_width)
        for row in rows:
            if using_groups:
                groups = location2groups.get(row['location'], ['OTHER'])
                for group in groups:
                    path = f"{group}/{row['location']}"
                    values = row['columns']
                    cdict.add(path, values)
            else:
                path = row['location']
                values = row['columns']
                cdict.add(path, values)
        ctree, crow2id = cdict.as_tree(cdict)
        current_hsh['next'] = ctree

    return tree, row2id, ctree


def show_journal(
    db,
    id2relevant,
    repeat_list=[],
    pinned_list=[],
    link_list=[],
    konnected=[],
    timers={},
):
    """
    journal grouped by index entry
    """
    rows = []
    journal_name = settings.get('journal_name')
    for item in db:
        itemtype = item.get('itemtype')
        if itemtype != '%':
            continue
        doc_id = item.doc_id
        summary = item.get('summary')
        index = item.get('i', '~')

        if YMD_REGEX.match(summary) and index == journal_name:
            DAILY = True
            s = parse_datetime(summary)[1]
        else:
            DAILY = False
            s = item.get('s', None)
        if s:
            ss = date_to_datetime(s).timestamp()
            year = s.strftime("%Y")
            month = s.strftime("%B")
        else:
            ss = 0.0
            year = month = ''

        if s:
            if DAILY:
                # this is a 'daily' entry
                # sort = (index, -int(s.strftime('%Y')), -int(s.strftime('%m')), -int(s.strftime('%d')))
                sort = (index, -ss, summary)
                path = f'{index}/{year}/{month}'
            else:
                sort = (index, ss, summary)
                path = index
        else:
            sort = (index, ss, item['summary'])
            path = index


        itemtype = item['itemtype']
        flags = get_flags(
            doc_id, repeat_list, link_list, konnected, pinned_list, timers
        )
        rows.append(
            {
                'sort': sort,
                'path': path,
                'values': [itemtype, summary, flags, '', doc_id],
            }
        )
    rows.sort(key=itemgetter('sort'))
    rdict = NDict()
    for row in rows:
        path = row['path']
        values = row['values']
        rdict.add(path, values)
    tree, row2id = rdict.as_tree(rdict)
    return tree, row2id


def show_tags(
    db,
    id2relevant,
    repeat_list=[],
    pinned_list=[],
    link_list=[],
    konnected=[],
    timers={},
):
    """
    tagged items grouped by tag
    """
    width = shutil.get_terminal_size()[0] - 3
    rows = []
    for item in db:
        doc_id = item.doc_id
        rhc = ''
        tags = item.get('t', [])
        itemtype = FINISHED_CHAR if 'f' in item else item.get('itemtype', '?')
        summary = item['summary']
        flags = get_flags(
            doc_id, repeat_list, link_list, konnected, pinned_list, timers
        )

        for tag in subsets(tags):
            rows.append(
                {
                    'sort': (tag, item['itemtype'], item['summary']),
                    'path': tag[1],
                    'values': [itemtype, summary, flags, rhc, doc_id],
                }
            )
    rows.sort(key=itemgetter('sort'))
    rdict = NDict()
    for row in rows:
        path = row['path']
        values = row['values']
        rdict.add(path, values)
    tree, row2id = rdict.as_tree(rdict)
    return tree, row2id


def show_location(
    db,
    id2relevant,
    repeat_list=[],
    pinned_list=[],
    link_list=[],
    konnected=[],
    timers={},
):
    """
    items with location entries grouped by location
    """
    width = shutil.get_terminal_size()[0] - 3
    rows = []
    for item in db:
        doc_id = item.doc_id
        rhc = (
            format_date(id2relevant[doc_id])[1]
            if doc_id in id2relevant
            else ' ' * 8
        )
        location = item.get('l', '~')
        itemtype = FINISHED_CHAR if 'f' in item else item.get('itemtype', '?')
        summary = item['summary']
        flags = get_flags(
            doc_id, repeat_list, link_list, konnected, pinned_list, timers
        )

        rows.append(
            {
                'sort': (location, item['itemtype'], item['summary']),
                'path': location,
                'values': [itemtype, summary, flags, rhc, doc_id],
            }
        )
    rows.sort(key=itemgetter('sort'))
    rdict = NDict()
    for row in rows:
        path = row['path']
        values = row['values']
        rdict.add(path, values)
    tree, row2id = rdict.as_tree(rdict)
    return tree, row2id


def show_index(
    db,
    id2relevant,
    repeat_list=[],
    pinned_list=[],
    link_list=[],
    konnected=[],
    timers={},
):
    """
    All items grouped by index entry
    """
    rows = []
    width = shutil.get_terminal_size()[0] - 3
    summary_width = width - 14
    for item in db:
        doc_id = item.doc_id
        index = item.get('i', '~')
        itemtype = FINISHED_CHAR if 'f' in item else item.get('itemtype', '?')
        summary = item['summary'][:summary_width]
        flags = get_flags(
            doc_id, repeat_list, link_list, konnected, pinned_list, timers
        )
        s = item.get('s', None)
        if s:
            ss = date_to_datetime(s).timestamp()
            sort = format_datetime(item['created'])[1]
            year = s.strftime("%Y")
            month = s.strftime("%b")
        else:
            ss = 0.0
            sort = '~'
            year = month = ''
        if s:
            if index == settings['journal_name']:
                # sort = (index, -ss, item['summary'])
                sort = (index, ss, item['summary'])
                path = f'{index}/{year}/{month}'
                # ok, summary = format_date(s,separator='-',omit_zeros=False)
                summary = f"{item['summary']}"
            else:
                sort = (index, ss, item['summary'])
                path = index
                summary = f"{item['summary']}"
        else:
            sort = (index, ss, item['summary'])
            path = index
            summary = f"{item['summary']}"

        itemtype = item['itemtype']
        flags = get_flags(
            doc_id, repeat_list, link_list, konnected, pinned_list, timers
        )
        rows.append(
            {
                'sort': sort,
                'path': path,
                'values': [itemtype, summary, flags, '', doc_id],
            }
        )
    rows.sort(key=itemgetter('sort'))
    rdict = NDict()
    for row in rows:
        path = row['path']
        values = row['values']
        try:
            rdict.add(path, values)
        except:
            logger.error(f'error adding path: {path}, values: {values}')
    tree, row2id = rdict.as_tree(rdict)
    return tree, row2id


def show_pinned(
    items,
    repeat_list=[],
    pinned_list=[],
    link_list=[],
    konnected=[],
    timers={},
):
    width = shutil.get_terminal_size()[0] - 3
    rows = []
    rhc_width = 8
    md_fmt = '%-d %b' if settings['dayfirst'] else '%b %-d'
    logger.debug(f'repeat_list: {repeat_list}; pinned_list: {pinned_list}')

    for item in items:
        mt = item.get('modified', None)
        if mt is not None:
            dt, label = mt, 'm'
        else:
            dt, label = item.get('created', None), 'c'
        if dt is not None:
            doc_id = item.doc_id
            year = dt.strftime('%Y')
            monthday = dt.strftime(md_fmt)
            time = fmt_time(dt)
            rhc = f'{str(doc_id).rjust(6)}'
            itemtype = (
                FINISHED_CHAR if 'f' in item else item.get('itemtype', '?')
            )
            summary = item['summary']
            flags = get_flags(
                doc_id, repeat_list, link_list, konnected, pinned_list, timers
            )

            rows.append(
                {
                    'sort': (itemtype, dt),
                    'path': type_keys[itemtype],
                    'values': [itemtype, summary, flags, rhc, doc_id],
                }
            )

    rows.sort(key=itemgetter('sort'), reverse=False)
    rdict = NDict()
    for row in rows:
        path = row['path']
        values = row['values']
        rdict.add(path, values)
    tree, row2id = rdict.as_tree(rdict)
    return tree, row2id


def get_usedtime(
    db, repeat_list=[], pinned_list=[], link_list=[], konnected=[], timers={}
):
    """
    All items with used entries grouped by month, index entry and day

    """
    UT_MIN = settings.get('usedtime_minutes', 1)

    width = shutil.get_terminal_size()[0] - 3

    used_details = {}
    used_details2id = {}
    used_summary = {}
    effort_details = {}
    month_rows = {}
    used_time = {}
    detail_rows = []
    months = set([])
    for item in db:
        used = item.get(
            'u'
        )   # this will be a list of 'period, datetime' tuples
        if item.get('itemtype', '!') == '!' or not used:
            continue
        index = item.get('i', '~')
        id_used = {}
        index_tup = index.split('/')
        doc_id = item.doc_id
        itemtype = item['itemtype']
        summary = item['summary']
        flags = get_flags(
            doc_id, repeat_list, link_list, konnected, pinned_list, timers
        )
        for period, dt in used:
            if isinstance(dt, date) and not isinstance(dt, datetime):
                dt = datetime(dt.year, dt.month, dt.day).astimezone()
                dt.replace(hour=23, minute=59, second=59)
            if UT_MIN > 0:
                seconds = int(period.total_seconds()) % 60
                if seconds:
                    # round up to the next minute
                    period = period + timedelta(seconds=60 - seconds)

                res = (period.total_seconds() // 60) % UT_MIN
                if res:
                    period += (UT_MIN - res) * ONEMIN
            yr, wk, dayofweek = dt.isocalendar()
            week = (yr, wk)
            row = wkday2row(dayofweek)
            effort_details.setdefault(week, {})
            effort_details[week].setdefault(dayofweek, ZERO)
            effort_details[week][dayofweek] += period
            monthday = dt.date()
            id_used.setdefault(monthday, ZERO)
            id_used[monthday] += period
            month = dt.strftime('%Y-%m')
            used_time.setdefault(tuple((month,)), ZERO)
            used_time[tuple((month,))] += period
            for i in range(len(index_tup)):
                used_time.setdefault(tuple((month, *index_tup[: i + 1])), ZERO)
                used_time[tuple((month, *index_tup[: i + 1]))] += period
        for monthday in id_used:
            month = monthday.strftime('%Y-%m')
            rhc = f"{format_hours_and_tenths(id_used[monthday]).lstrip('+')} {monthday.day}"
            detail_rows.append(
                {
                    'sort': (month, index_tup, monthday, itemtype, summary),
                    'month': month,
                    'path': f"{monthday.strftime('%B %Y')}/{index}",
                    'values': [itemtype, summary, flags, rhc, doc_id],
                }
            )

    try:
        detail_rows.sort(key=itemgetter('sort'))
    except Exception as e:
        # report the components of sort other than the last, the summary
        logger.error(
            f"error sorting detail_rows: f{e}\nsort: {[x['sort'][:-1] for x in detail_rows]}"
        )
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
                logger.error(
                    f'error adding path: {path}, values: {values}: {e}'
                )
        tree, row2id = rdict.as_tree(rdict)
        used_details[month] = tree
        used_details2id[month] = row2id

    keys = [x for x in used_time]
    keys.sort()
    for key in keys:
        period = used_time[key]
        month_rows.setdefault(key[0], [])
        indent = (len(key) - 1) * 2 * ' '
        if len(key) == 1:
            yrmnth = datetime.strptime(f'{key[0]}-01', '%Y-%m-%d').strftime(
                '%B %Y'
            )
            rhc = f": {format_hours_and_tenths(period).lstrip('+')}"
            # summary = indent + f"{indent}{yrmnth}"[:summary_width]
            summary = indent + yrmnth
            month_rows[key[0]].append(f'{summary}{rhc}')

        else:
            rhc = f": {format_hours_and_tenths(period).lstrip('+')}"
            summary = indent + key[-1]
            excess = len(rhc) + len(summary) - width
            summary = summary[:-excess] if excess > 0 else summary
            month_rows[key[0]].append(f'{summary}{rhc}')

    for key, val in month_rows.items():
        used_summary[key] = '\n'.join(val)

    return used_details, used_details2id, used_summary, effort_details


def fmt_class(txt, cls=None, plain=False):
    if not plain and cls is not None:
        return cls, txt
    else:
        return txt


def no_busy_periods(week, width):

    # The weekday 2-char abbreviation and the month day
    width = shutil.get_terminal_size()[0]
    dent = int((width - 69) / 2) * ' '
    monday = datetime.strptime(f'{week[0]} {week[1]} 1', '%Y %W %w')
    DD = {}
    for i in range(1, 8):
        DD[
            i
        ] = f"{WA[i]} {(monday + (i-1)*DAY).strftime('%-d')}".ljust(
            5, ' '
        )

    h = {}
    h[0] = '  '
    h[58] = '  '
    for i in range(1, 58):
        h[i] = ' ' if (i - 1) % 4 else VSEP
    empty = ''.join([h[i] for i in range(59)])
    for i in range(1, 58):
        h[i] = HSEP if (i - 1) % 4 else VSEP
    full = ''.join([h[i] for i in range(59)])
    empty_hsh = {}
    wk_fmt = fmt_week(week).center(width, ' ').rstrip()
    empty_hsh[
        0
    ] = f"""\
{wk_fmt}

{dent}{day_bar_labels()}
"""
    for weekday in range(1, 8):
        empty = day_bar([], False)
        empty_hsh[
            weekday
        ] = f"""\
{dent}{7*' '}{empty}
{dent} {DD[weekday] : <6}{empty}
"""
    return ''.join([empty_hsh[i] for i in range(0, 8)])


def summary_pin(text, width, doc_id, pinned_list, link_list, konnected_list):
    in_konnected = False
    if doc_id in konnected_list:
        in_konnected = True
        text = text[: width - 3].rstrip() + KONNECT_CHAR
    if doc_id in link_list:
        text = text[: width - 3].rstrip() + LINK_CHAR
    if doc_id in pinned_list:
        ret = (text[: width - 1] + PIN_CHAR).ljust(width - 1, ' ')
    else:
        ret = text[:width].ljust(width, ' ')
    return ret


def wkday2row(wkday):
    # week day number in 1, ..., 7 to row number in busy view
    # 1 -> 5, ..., 6 -> 15, 0 -> 17  (pendulum thinks Sunday is first)
    # TODO: fixme
    return 3 + 2 * wkday if wkday else 17


def schedule(
    db,
    yw=getWeekNum(),
    current=[],
    now=datetime.now(),
    weeks_before=0,
    weeks_after=0,
    repeat_list=[],
    pinned_list=[],
    link_list=[],
    konnected=[],
    timers={},
):
    global current_hsh, active_tasks
    logger.debug(f"### Schedule ###")
    timer_schedule = TimeIt('***SCHEDULE***')
    width = shutil.get_terminal_size()[0] - 3
    weeks_after = settings['keep_current'][0]
    mk_current = weeks_after > 0
    current_hsh = {}

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
                LL[hour] = f'{hr}{suffix}'.rjust(6, ' ')
            else:
                LL[hour] = f'{hour}h'.rjust(6, ' ')
        else:
            LL[hour] = ' '.rjust(6, ' ')


    d = iso_to_gregorian((yw[0], yw[1], 1))
    dt = datetime(d.year, d.month, d.day, 0, 0, 0).astimezone()
    week_numbers = getWeekNumbers(dt, weeks_before, weeks_after)
    if yw not in week_numbers:
        week_numbers.append(yw)
        week_numbers.sort()
    aft_dt, bef_dt = get_period(dt, weeks_before, weeks_after)

    # for the individual weeks
    agenda_hsh = {}     # yw -> agenda_view
    done_hsh = {}       # yw -> done_view
    busy_hsh = {}       # yw -> busy_view
    row2id_hsh = {}     # yw -> row2id
    done2id_hsh = {}     # yw -> row2id
    effort_hsh = {}
    effort2id_hsh = {}     # yw -> row2id
    week2day2effort = {}   # year, week -> dayofweek -> period total for day
    week2day2heading = {}
    weeks = set([])
    rows = []
    done = []
    effort = []
    # id2konnected = {} # id -> [(to|from, id)]

    # XXX year, week -> dayofweek -> list of [time interval, summary, period]
    busy_details = {}
    week2day2busy = {}
    week2day2allday = {}

    # XXX main loop begins
    todayYMD = now.strftime('%Y%m%d')
    tomorrowYMD = (now + 1 * DAY).strftime('%Y%m%d')

    for item in db:
        completed = []
        if item.get('itemtype', None) == None:
            logger.error(f'itemtype missing from {item}')
            continue
        if item['itemtype'] in '!?':
            continue

        doc_id = item.doc_id

        itemtype = item['itemtype']
        summary = item.get('summary', '~')
        start = item.get('s', None)
        extent = item.get('e', None)
        wraps = item.get('w', [])
        flags = get_flags(
            doc_id, repeat_list, link_list, konnected, pinned_list, timers
        )
        used = item.get('u', None)
        finished = item.get('f', None)
        history = item.get('h', None)
        jobs = item.get('j', None)

        if itemtype == '*' and start and extent and 'r' not in item:
            dt = date_to_datetime(start)

        if used:
            dates_to_periods = {}
            for period, dt in used:
                if isinstance(dt, date) and not isinstance(dt, datetime):
                    pass
                else:
                    dt = dt.date()
                if UT_MIN > 0:
                    # round up minutes - consistent with used time views
                    # seconds = period.total_seconds()//60
                    seconds = int(period.total_seconds()) % (UT_MIN * 60)
                    if seconds:
                        increment = timedelta(seconds=UT_MIN * 60 - seconds)
                        period += increment

                dates_to_periods.setdefault(dt, []).append(period)

            for dt in dates_to_periods:
                week = dt.isocalendar()[:2]
                weekday = format_wkday(dt)
                week2day2effort.setdefault(week, {})
                week2day2effort[week].setdefault(weekday, ZERO)
                total = ZERO
                for p in dates_to_periods[dt]:
                    total += p
                if total is not None:
                    week2day2effort[week][weekday] += total
                    used = format_hours_and_tenths(total).lstrip(
                        '+'
                    )   # drop the +
                else:
                    used = ''
                effort.append(
                    {
                        'id': doc_id,
                        'job': None,
                        'instance': None,
                        'sort': (dt.strftime('%Y%m%d'), '1'),
                        'week': (week),
                        'day': (weekday,),
                        'columns': [
                            itemtype,
                            f'{used} {summary}' if used else '',
                            flags,
                            '',
                            (doc_id, None, None),
                        ],
                    }
                )

        if itemtype == '-':
            d = []   # d for done
            # c = [] # c for completed
            if isinstance(finished, Period):
                # finished will be false if the period is ZERO
                # we need details of when completed (start and end) for completed view
                d.append(
                    [
                        finished.start,
                        summary,
                        doc_id,
                        format_completion(
                            finished.start, finished.end
                        ),
                    ]
                )
                # to skip completed instances we only need the completed (end) instance
                completed.append(finished.start)
                # ditto below for history
            if history:
                for dt in history:
                    d.append(
                        [
                            dt.start,
                            summary,
                            doc_id,
                            format_completion(dt.start, dt.end),
                        ]
                    )
                    completed.append(dt.end)
            if jobs:
                for job in jobs:
                    job_summary = job.get('summary', '')
                    if 'f' in job:
                        d.append(
                            [
                                job['f'].start,
                                job_summary,
                                doc_id,
                                format_completion(
                                    job['f'].start, job['f'].end
                                ),
                            ]
                        )
            if d:
                for row in d:
                    dt = row[0]
                    finished_char = SKIPPED_CHAR if row[3] == '-1m' else FINISHED_CHAR

                    rhc = str(row[3]) + '  ' if len(row) > 3 else ''
                    if dt < aft_dt or dt > bef_dt:
                        continue

                    done.append(
                        {
                            'id': row[2],
                            'job': row[3],
                            'instance': None,
                            'sort': (dt.strftime('%Y%m%d%H%M'), '1'),
                            'week': (dt.isocalendar()[:2]),
                            'day': (
                                format_wkday(dt),
                            ),
                            'columns': [
                                finished_char,
                                f'{rhc}{row[1]}',
                                flags,
                                '',
                                (row[2], None, row[3]),
                            ],
                        }
                    )

        startdt = date_to_datetime(start)
        if not start or finished is not None or startdt in completed:
            continue

        # XXX INSTANCES

        # keep these for reference for this item
        end_dt = None

        for dt, et in item_instances(item, aft_dt, bef_dt):

            yr, wk, dayofweek = dt.isocalendar()
            week = (yr, wk)
            wk_fmt = fmt_week(week).center(width, ' ').rstrip()
            itemday = dt.strftime('%Y%m%d')
            dayDM = format_wkday(dt)
            if itemday == todayYMD:
                dayDM += ' (Today)'
            elif itemday == tomorrowYMD:
                dayDM += ' (Tomorrow)'
            week2day2busy.setdefault(week, {})
            week2day2busy[week].setdefault(dayofweek, [])
            week2day2allday.setdefault(week, {})
            week2day2allday[week].setdefault(
                dayofweek, [False, [f'{dayDM}', f'All day']]
            )

            if (
                item['itemtype'] == '*'
                and dt.hour == 0
                and dt.minute == 0
                and 'e' not in item
            ):
                week2day2allday[week][dayofweek][0] = True
                if 'r' in item:
                    freq = item['r'][0].get('r', 'y')
                else:
                    freq = 'y'
                tmp_summary = set_summary(item['summary'], item['s'], dt, freq)
                week2day2allday[week][dayofweek][1].append(
                    f" {item['itemtype']} {tmp_summary}"
                )

            if 'r' in item:
                freq = item['r'][0].get('r', 'y')
            else:
                freq = 'y'

            instance = dt if '+' in item or 'r' in item else None

            if instance in completed:
                continue

            if 'j' in item:

                # repeating task with jobs

                if instance:
                    if (
                        doc_id in active_tasks
                        and active_tasks[doc_id] != instance
                    ):
                        continue
                    else:
                        active_tasks[doc_id] = instance

                for job in item['j']:
                    if 'f' in job:
                        continue
                    job_summary = job.get('summary', '')
                    jobstart = dt - job.get('s', ZERO)
                    sort_dt = jobstart.strftime('%Y%m%d%H%M')
                    if sort_dt.endswith('0000'):
                        sort_dt = sort_dt[:-4] + '2359'

                    job_id = job.get('i', None)
                    job_sort = str(job_id)

                    # rhc = fmt_time(dt).center(rhc_width, ' ')
                    rhc = fmt_time(dt)
                    rows.append(
                        {
                            'id': doc_id,
                            'job': job_id,
                            'instance': instance,
                            'sort': (
                                sort_dt,
                                job_sort,
                            ),
                            'week': (jobstart.isocalendar()[:2]),
                            'week_fmt': (wk_fmt),
                            'dayofweek': (dayofweek),
                            'day': (
                                format_wkday(jobstart),
                            ),
                            'columns': [
                                job['status'],
                                set_summary(
                                    f'{rhc}  {job_summary}',
                                    start,
                                    jobstart,
                                    freq,
                                ),
                                flags,
                                '',  # rhc,
                                (doc_id, instance, job_id),
                            ],
                        }
                    )

            else:   # not a task with jobs
                dateonly = False
                sort_dt = dt.strftime('%Y%m%d%H%M')
                if sort_dt.endswith('0000'):
                    dateonly = True
                    if item['itemtype'] in ['-']:
                        sort_dt = sort_dt[:-4] + '2359'
                    elif item['itemtype'] in ['%']:
                        sort_dt = sort_dt[:-4] + '2400'
                # if 'allday' in item['summary']:

                if 'e' in item:
                    if omit and 'c' in item and item['c'] in omit:
                        et = None
                        # rhc = fmt_time(dt).center(rhc_width, ' ')
                        rhc = fmt_time(dt)
                    else:
                        if item['itemtype'] == '-' and dateonly:
                            rhc = fmt_dur(item['e'])
                        else:
                            rhc = fmt_extent(dt, et)
                else:
                    rhc = fmt_time(dt)

                dtb = dt

                dta = et if et else None

                # temp - just for this item
                wrap = []
                before = after = {}
                wrapped = ''
                if 'w' in item and dta and dtb:
                    # adjust for wrap
                    has_w = True
                    if len(item['w']) == 2:
                        b, a = item['w']
                        if b:
                            dtb -= b
                        if a:
                            dta += a
                        wrapped = fmt_extent(dtb, dta)

                        wrap = item['w']
                        wraps = (
                            [format_duration(x) for x in wrap] if wrap else ''
                        )
                        if wraps:
                            wraps[0] = f'{wrapbefore}{wraps[0]}'
                            wraps[1] = f'{wrapafter}{wraps[1]}'
                            wrapper = f"\n{22*' '}+ {', '.join(wraps)}"
                        else:
                            wrapper = ''

                    else:
                        a = b = ZERO
                        logger.error(
                            f"The entry for 'w' in item {item.doc_id} should have 2 arguments but instead has {len(item['w'])}: {item['w']}. The entry has been ignored."
                        )

                    if b and b > ZERO:
                        itemtype = wrapbefore   #  "↱"
                        sort_b = (dt - ONEMIN).strftime('%Y%m%d%H%M')
                        rhb = fmt_time(dtb)
                        before = {
                            'id': doc_id,
                            'job': None,
                            'instance': instance,
                            'sort': (sort_b, '0'),
                            'week': (dtb.isocalendar()[:2]),
                            'dayofweek': (dtb.isocalendar()[-1]),
                            'day': (
                                format_wkday(dtb),
                            ),
                            'columns': [
                                itemtype,
                                set_summary(rhb, item['s'], dtb, freq),
                                ' ' * 4,
                                '',
                                (doc_id, instance, None),
                            ],
                        }

                    if a and a > ZERO:
                        itemtype = wrapafter  # "↳"
                        sort_a = (dt + ONEMIN).strftime('%Y%m%d%H%M')
                        rha = fmt_time(dta)
                        after = {
                            'id': doc_id,
                            'job': None,
                            'instance': instance,
                            'sort': (sort_a, 0),
                            'week': (dta.isocalendar()[:2]),
                            'dayofweek': (dta.isocalendar()[-1]),
                            'day': (
                                format_wkday(dta),
                            ),
                            'columns': [
                                itemtype,
                                set_summary(rha, item['s'], dta, freq),
                                ' ' * 4,
                                '',  # rha,
                                (doc_id, instance, None),
                            ],
                        }
                else:
                    wrapped = rhc

                if before:
                    rows.append(before)

                if omit and 'c' in item and item['c'] in omit:
                    busyperiod = None
                elif dta and dta > dtb:
                    # a for after, b for before
                    busyperiod = None
                    dtad = dta.date()
                    dtbd = dtb.date()
                    if dtad == dtbd:
                        busyperiod = (dt2minutes(dtb), dt2minutes(dta))
                        week2day2busy[week][dayofweek].append(busyperiod)
                    elif dtad > dtbd:
                        busyperiods = datetimes2busy(dta, dtb)
                        for w, wd, periods in busyperiods:
                            if w == week and wd == dayofweek:
                                busyperiod = periods
                                week2day2busy[week][dayofweek].append(
                                    busyperiod
                                )
                                break
                else:
                    busyperiod = None
                tmp_summary = set_summary(summary, item['s'], dt, freq)
                rhc = rhc + ' ' if rhc else ''
                columns = [
                    item['itemtype'],
                    f'{rhc}{tmp_summary}',
                    flags,
                    '',
                    (doc_id, instance, None),
                ]

                path = f'{wk_fmt}/{dayDM}**'

                rows.append(
                    {
                        'id': doc_id,
                        'job': None,
                        'instance': instance,
                        'sort': (sort_dt, '0'),
                        'week': (week),
                        'week_fmt': (wk_fmt),
                        'dayofweek': (dayofweek),
                        'day': (
                            format_wkday(dt),
                        ),
                        'busyperiod': (busyperiod),
                        'wrap': (wrap),
                        'wrapped': wrapped,
                        'columns': columns,
                    }
                )

                if after:
                    rows.append(after)

    if yw == getWeekNum(now):
        rows.extend(current)
    rows.sort(key=itemgetter('sort'))
    done.sort(key=itemgetter('sort'))
    effort.sort(key=itemgetter('sort'))

    busy_details = {}
    allday_details = {}
    # TODO
    dent = int((width - 69) / 2) * ' '

    ### item/agenda loop 2
    today = format_wkday(now)
    tomorrow = format_wkday(now + 1 * DAY)

    for week in week2day2allday:
        week2day2heading.setdefault(week, {})
        weeks.add(week)
        allday_details.setdefault(week, {})
        for dayofweek in week2day2allday[week]:
            allday, lst = week2day2allday[week][dayofweek]
            if allday and lst:
                row = wkday2row(dayofweek)
                week2day2heading[week][row] = lst.pop(0)
                day_ = row
                allday_details[week][row] = f'\n'.join([f'{x}' for x in lst])

    for week, items in groupby(rows, key=itemgetter('week')):
        weeks.add(week)
        week2day2heading.setdefault(week, {})
        rdict = NDict(compact=True)
        busy_details.setdefault(week, {})
        wk_fmt = fmt_week(week).center(width, ' ').rstrip()
        for row in items:
            doc_id = row['id']
            day_ = row['day'][0]
            dayofweek = row.get('dayofweek', 1)
            if day_ == today:
                day_ += ' (Today)'
            elif day_ == tomorrow:
                day_ += ' (Tomorrow)'
            path = f'{wk_fmt}/{day_}'
            values = row['columns']
            if values[0] in ['*', '-']:
                values[1] = re.sub(' *\n+ *', ' ', values[1])
                busyperiod = row.get('busyperiod', '')
                if busyperiod:
                    wrap = row.get('wrap', [])
                    wrapped = f"<{row.get('wrapped', '')}>" if wrap else ''
                    row = wkday2row(dayofweek)
                    week2day2heading[week][row] = day_
                    summary = values[1]
                    busy_row = f' {values[0]} {summary}  {wrapped}'.rstrip()

                    busy_details[week].setdefault(row, [f'Busy']).append(
                        busy_row
                    )
            rdict.add(path, values)
        for d, v in busy_details[week].items():
            busy_details[week][d] = '\n'.join([x.rstrip() for x in v])

        tree, row2id = rdict.as_tree(rdict)
        agenda_hsh[week] = tree
        row2id_hsh[week] = row2id

    if mk_current:
        cweeks = set([])
        for week, items in groupby(rows, key=itemgetter('week')):
            cweeks.add(week)
            week2day2heading.setdefault(week, {})
            cdict = NDict(compact=True, width=settings['keep_current'][1])
            wk_fmt = fmt_week(week).center(width, ' ').rstrip()
            for row in items:
                doc_id = row['id']
                day_ = row['day'][0]
                dayofweek = row.get('dayofweek', 1)
                if day_ == today:
                    day_ += ' (Today)'
                elif day_ == tomorrow:
                    day_ += ' (Tomorrow)'
                path = f'{wk_fmt}/{day_}'
                values = row['columns']
                # heading = f"Busy periods for {day_}"
                if values[0] in ['*', '-']:
                    values[1] = re.sub(' *\n+ *', ' ', values[1])
                cdict.add(path, values)

            ctree, crow2id = cdict.as_tree(cdict)
            current_hsh[week] = ctree

    busyday_details = {}
    for week in allday_details:
        busyday_details.setdefault(week, {})
        for day in allday_details[week]:
            busyday_details[week].setdefault(day, []).append(
                allday_details[week][day]
            )
    for week in busy_details:
        busyday_details.setdefault(week, {})
        for day in busy_details[week]:
            busyday_details[week].setdefault(day, []).append(
                busy_details[week][day].rstrip()
            )

    for week in busyday_details:
        for row in busyday_details[week]:
            lst = [
                week2day2heading[week]
                .get(row, f'{week} {row}')
                .center(width, ' ')
                .rstrip(),
            ]
            lst += [x for x in busyday_details[week][row] if x.strip()]
            busyday_details[week][row] = '\n'.join(lst)

    busy = {}
    for week, dayhsh in week2day2busy.items():
        busy_tuples = []
        for day in range(1, 8):
            periods = dayhsh.get(day, [])
            periods.sort()
            busy_tuples.append([day, periods])

        monday = datetime.strptime(f'{week[0]} {week[1]} 1', '%Y %W %w')

        DD = {}
        for i in range(1, 8):
            DD[
                i
            ] = f"{WA[i]} {(monday + (i-1)*DAY).strftime('%-d')}".ljust(
                5, ' '
            )

        for tup in busy_tuples:
            #                 d             (beg_min, end_min)
            busy[tup[0]] = tup[1]
        wk_fmt = fmt_week(week).center(width, ' ').rstrip()
        busy_hsh[
            0
        ] = f"""\
{wk_fmt}

{dent}{day_bar_labels()}
"""
        empty = day_bar([], False)
        for weekday in range(1, 8):
            lofp = busy.get(weekday, [])
            alldayitems = ''
            allday = False
            if week in week2day2allday and weekday in week2day2allday[week]:
                allday, lst = week2day2allday[week][weekday]

            full = day_bar(lofp, allday)

            busy_hsh[
                weekday
            ] = f"""\
{dent}{7*' '}{empty}
{dent} {DD[weekday] : <6}{full}
"""
        busy_hsh[week] = ''.join([busy_hsh[i] for i in range(0, 8)])

    for week, items in groupby(done, key=itemgetter('week')):
        weeks.add(week)
        rdict = NDict()
        wk_fmt = fmt_week(week).center(width, ' ').rstrip()
        for row in items:
            day_ = row['day'][0]
            if day_ == today:
                day_ += ' (Today)'
            elif day_ == tomorrow:
                day_ += ' (Tomorrow)'
            path = f'{wk_fmt}/{day_}'
            values = row['columns']
            rdict.add(path, values)
        tree, row2id = rdict.as_tree(rdict)
        done_hsh[week] = tree
        done2id_hsh[week] = row2id

    for week, items in groupby(effort, key=itemgetter('week')):
        weeks.add(week)
        rdict = NDict()
        wk_fmt = fmt_week(week).center(width, ' ').rstrip()
        for row in items:
            day_ = row['day'][0]
            total_period = (
                week2day2effort[week][day_]
                if day_ in week2day2effort[week]
                else ZERO
            )
            total = int(total_period.total_seconds()) // 60
            used_fmt = bar_fmt = ''
            if total:
                used, bar = usedminutes2bar(total)
                if usedtime_hours:
                    bar_fmt = f"{bar.ljust(width-12, ' ')}"
                    used_fmt = used.center(6, ' ')
                else:
                    bar_fmt = ' '
                    used_fmt = used
            if day_ == today:
                day_ += ' (Today)'
            elif day_ == tomorrow:
                day_ += ' (Tomorrow)'
            path = f'{wk_fmt}/{day_}/{used_fmt} {bar_fmt}'
            values = row['columns']
            rdict.add(path, values)
        tree, row2id = rdict.as_tree(rdict)
        effort_hsh[week] = tree
        effort2id_hsh[week] = row2id

    cache = {}
    for week in week_numbers:
        tup = []
        # agenda
        if week in agenda_hsh:
            tup.append(agenda_hsh[week])
        else:
            tup.append(
                '{}\n   Nothing scheduled'.format(
                    fmt_week(week).center(width, ' ').rstrip()
                )
            )
        # done
        if week in done_hsh:
            tup.append(done_hsh[week])
        else:
            tup.append(
                '{}\n   Nothing completed'.format(
                    fmt_week(week).center(width, ' ').rstrip()
                )
            )

        # effort
        if week in effort_hsh:
            tup.append(effort_hsh[week])
        else:
            tup.append(
                '{}\n   No used times recorded'.format(
                    fmt_week(week).center(width, ' ').rstrip()
                )
            )

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
        # effort2id
        if week in effort2id_hsh:
            tup.append(effort2id_hsh[week])
        else:
            tup.append({})

        if week in busyday_details:
            tup.append(busyday_details[week])
        else:
            tup.append({})
        # agenda, done, effort, busy, row2id, done2id, effort2id, busy_details
        cache[week] = tup

    timer_schedule.stop()
    return cache


def import_file(import_file=None):
    import_file = import_file.strip()
    if not import_file:
        return False, ''
    if import_file.lower() == 'lorem':
        return True, import_examples()

    if not os.path.isfile(import_file):
        return (
            False,
            f'"{import_file}"\n   either does not exist or is not a regular file',
        )
    filename, extension = os.path.splitext(import_file)
    if extension == '.text':
        return True, import_text(import_file)
    else:
        return (
            False,
            f"Importing a file with the extension '{extension}' is not implemented. Only files with the extension '.text' are recognized",
        )


def get_konnections(hsh: dict)->[int]:
    if 'K' not in hsh:
        return []

    konnect = hsh.get('K', [])
    doc_ids = []
    while len(konnect) > 0:
        # save a inbox item for each and replace @K summary with @k doc_id
        s = konnect.pop(0)
        item = Item()
        item.new_item()
        item.text_changed(s, 1)
        doc_id = item.do_insert()
        doc_ids.append(doc_id)
    return doc_ids

def import_examples():
    docs = []
    examples = make_examples(last_id=last_id)

    results = []
    good = []
    bad = []
    items = []

    logger.debug(f"starting import from last_id: {last_id}")
    count = 0
    for s in examples:
        ok = True
        count += 1
        if not s:
            continue
        item = Item()  # use ETMDB by default
        item.new_item()
        item.text_changed(s, 1)
        if item.item_hsh.get('itemtype', None) is None:
            ok = False

        if item.item_hsh.get('summary', None) is None:
            ok = False


        if ok:
            # don't check links because the ids won't yet exist
            item.update_item_hsh(check_links=False)
            good.append(f'{item.doc_id}')
        else:
            logger.debug(f"bad entry: {s}")
            bad.append(s)

    logger.debug("ending import")
    res = f'imported {len(good)} items'
    if good:
        res += f'\n  ids: {good[0]} - {good[-1]}'
    if bad:
        res += f'\nrejected {bad} items:\n  '
        res += '\n  '.join(results)
    return res


def import_text(import_file=None):
    docs = []
    with open(import_file, 'r') as fo:
        logger.debug(f"opened for reading: '{import_file}'")
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
    count = 0
    for reminder in reminders:
        count += 1
        logger.debug(f"reminder number {count}: {reminder}")
        ok = True
        s = '\n'.join(reminder)
        if not s:
            continue
        logger.debug(f"adding item for {s}")
        item = Item()  # use ETMDB by default
        item.new_item()
        item.text_changed(s, 1)
        if item.item_hsh.get('itemtype', None) is None:
            ok = False

        if item.item_hsh.get('summary', None) is None:
            ok = False

        if ok:
            # don't check links because the ids won't yet exist
            item.update_item_hsh(check_links=False)
            good.append(f'{item.doc_id}')
        else:
            logger.debug(f"bad entry: {s}")
            bad.append(s)

        # if not ok:
        #     bad += 1
        #     results.append(f'   {s}')
        #     continue

        # update_item_hsh stores the item in ETMDB
        # item.update_item_hsh()
        # good.append(f'{item.doc_id}')

    res = f'imported {len(good)} items'
    if good:
        res += f'\n  ids: {good[0]} - {good[-1]}'
    if bad:
        res += f'\nrejected {bad} items:\n  '
        res += '\n  '.join(results)
    logger.debug(f"returning: {res}")
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
        if 's' in item_hsh:
            item_hsh['s'] = pen_from_fmt(item_hsh['s'], z)
        if 'f' in item_hsh:
            item_hsh['f'] = period_from_fmt(item_hsh['f'], z)
        item_hsh['created'] = datetime.now('UTC')
        if 'h' in item_hsh:
            item_hsh['h'] = [period_from_fmt(x, z) for x in item_hsh['h']]
        if '+' in item_hsh:
            item_hsh['+'] = [pen_from_fmt(x, z) for x in item_hsh['+']]
        if '-' in item_hsh:
            item_hsh['-'] = [pen_from_fmt(x, z) for x in item_hsh['-']]
        if 'e' in item_hsh:
            item_hsh['e'] = parse_duration(item_hsh['e'])[1]
        if 'w' in item_hsh:
            wrps = [parse_duration(x)[1] for x in item_hsh['w']]
            item_hsh['w'] = wrps
        if 'a' in item_hsh:
            alerts = []
            for alert in item_hsh['a']:
                # drop the True from parse_duration
                tds = [parse_duration(x)[1] for x in alert[0]]
                # put the largest duration first
                tds.sort(reverse=True)
                cmds = alert[1:2]
                args = ''
                if len(alert) > 2 and alert[2]:
                    args = ', '.join(alert[2])
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
                print(
                    'ok:',
                    ok,
                    ' lofh:',
                    lofh,
                    ' last_completed:',
                    last_completed,
                )

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
                            logger.error(
                                f"error parsing rul['u']: {rul['u']}. {e}"
                            )
                if 'w' in rul:
                    if isinstance(rul['w'], list):
                        rul['w'] = [
                            '{0}:{1}'.format('{W}', x.upper())
                            for x in rul['w']
                        ]
                    else:
                        rul['w'] = '{0}:{1}'.format('{W}', rul['w'].upper())
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
        exst.append(
            {
                'itemtype': x.get('itemtype'),
                'summary': x.get('summary'),
                's': x.get('s'),
            }
        )
    i = 0
    for x in docs:
        i += 1
        y = {
            'itemtype': x.get('itemtype'),
            'summary': x.get('summary'),
            's': x.get('s'),
        }
        if exst and y in exst:
            dups += 1
        else:
            new.append(x)

    ids = []
    if new:
        ids = ETMDB.insert_multiple(new)
        ETMDB.close()
    msg = f'imported {len(new)} items'
    if ids:
        msg += f'\n  ids: {ids[0]}-{ids[-1]}.'
    if dups:
        msg += f'\n  rejected {dups} items as duplicates'
    return msg


def about(padding=0):
    logo_lines = [
        ' █████╗██████╗███╗   ███╗ ',
        ' ██╔══╝╚═██╔═╝████╗ ████║ ',
        ' ███╗    ██║  ██╔████╔██║ ',
        ' ██╔╝    ██║  ██║╚██╔╝██║ ',
        ' █████╗  ██║  ██║ ╚═╝ ██║ ',
        ' ╚════╝  ╚═╝  ╚═╝     ╚═╝ ',
        '  Event and Task Manager  ',
    ]
    width = shutil.get_terminal_size()[0] - 3
    output = []
    for line in logo_lines:
        output.append(line.center(width, ' ') + '\n')
    logo = ''.join(output)

    copyright = wrap(
        f"Copyright 2009-{datetime.today().strftime('%Y')}, Daniel A Graham. All rights reserved. This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version. See www.gnu.org/licenses/gpl.html for details.",
        0,
        width,
    )

    summary = wrap(
        'This application provides a format for using plain text entries to create events, tasks and other reminders and a prompt_toolkit based interface for creating and modifying items as well as viewing them.',
        0,
        width,
    )

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

    ret2 = f"""\
{VERSION_INFO}
 etm directory:      {etmhome}\
"""
    return ret1, ret2


dataview = None
item = None


def main(etmdir='', *args):
    global dataview, item, db, ampm, settings
    # NOTE: DataView called in model.main
    dataview = DataView(etmdir)
    settings = dataview.settings
    db = dataview.db
    item = Item(etmdir)
    dataview.refreshCache()


if __name__ == '__main__':
    sys.exit('model.py should only be imported')
