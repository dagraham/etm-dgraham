from dateutil.parser import parse as dateutil_parse
from dateutil.parser import parserinfo
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
import platform
import sys
import os
import sys

# import logging
# import logging.config

import etm.__version__ as version
from ruamel.yaml import __version__ as ruamel_version
from dateutil import __version__ as dateutil_version
from tinydb import __version__ as tinydb_version
from jinja2 import __version__ as jinja2_version
from prompt_toolkit import __version__ as prompt_toolkit_version

from time import perf_counter as timer


def is_aware(dt):
    return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None


class TimeIt(object):
    def __init__(self, label='', loglevel=1):
        self.loglevel = loglevel
        self.label = label
        if self.loglevel == 1:
            msg = 'timer {0} started; loglevel: {1}'.format(
                self.label, self.loglevel
            )
            logger.debug(msg)
            self.start = timer()

    def stop(self, *args):
        if self.loglevel == 1:
            self.end = timer()
            self.secs = self.end - self.start
            self.msecs = self.secs * 1000  # millisecs
            msg = 'timer {0} stopped; elapsed time: {1} milliseconds'.format(
                self.label, self.msecs
            )
            logger.debug(msg)


# from etm.__main__ import ETMHOME

python_version = platform.python_version()
system_platform = platform.platform(terse=True)
etm_version = version.version
sys_platform = platform.system()
mac = sys.platform == 'darwin'
windoz = sys_platform in ('Windows', 'Microsoft')

VERSION_INFO = f"""\
 etm version:        {etm_version}
 python:             {python_version}
 dateutil:           {dateutil_version}
 prompt_toolkit:     {prompt_toolkit_version}
 tinydb:             {tinydb_version}
 jinja2:             {jinja2_version}
 ruamel.yaml:        {ruamel_version}
 platform:           {system_platform}\
"""


def parse(s, **kwd):
    # enable pi when read by main and settings is available
    pi = parserinfo(
        dayfirst=settings['dayfirst'], yearfirst=settings['yearfirst']
    )
    dt = dateutil_parse(s, parserinfo=pi)
    if 'tzinfo' in kwd:
        tzinfo = kwd['tzinfo']
        if tzinfo == 'float':
            return dt.replace(tzinfo=None)
        elif tzinfo == 'local':
            return dt.astimezone()
        else:
            return dt.replace(tzinfo=ZoneInfo(tzinfo))
    else:
        return dt.astimezone()


# in __main__ placed in model and view
ETM_CHAR = dict(
    VSEP='⏐',  # U+23D0  this will be a de-emphasized color
    FREE='─',  # U+2500  this will be a de-emphasized color
    HSEP='┈',  #
    BUSY='■',  # U+25A0 this will be busy (event) color
    CONF='▦',  # U+25A6 this will be conflict color
    TASK='▩',  # U+25A9 this will be busy (task) color
    ADAY='━',  # U+2501 for all day events ━
    USED='◦',  # U+25E6 for used time
    REPS='↻',  # Flag for repeating items
    FINISHED_CHAR='✓',
    SKIPPED_CHAR='✗',
    UPDATE_CHAR='𝕦',
    INBASKET_CHAR='𝕚',
    KONNECT_CHAR='k',
    LINK_CHAR='g',
    PIN_CHAR='p',
    ELLIPSiS_CHAR='…',
    LINEDOT=' · ',  # ܁ U+00B7 (middle dot),
    ELECTRIC='⌁',
)
#  model, data and ical
#  with integer prefixes
WKDAYS_DECODE = {
    '{0}{1}'.format(n, d): '{0}({1})'.format(d, n) if n else d
    for d in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']
    for n in ['-4', '-3', '-2', '-1', '', '1', '2', '3', '4']
}

WKDAYS_ENCODE = {
    '{0}({1})'.format(d, n): '{0}{1}'.format(n, d) if n else d
    for d in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']
    for n in ['-4', '-3', '-2', '-1', '+1', '+2', '+3', '+4']
}

# without integer prefixes
for wkd in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']:
    WKDAYS_ENCODE[wkd] = wkd

# print(f'WKDAYS_DECODE:\n{WKDAYS_DECODE}')
# print(f'WKDAYS_ENCODE:\n{WKDAYS_ENCODE}')
# WKDAYS_DECODE:
# {'-4MO': 'MO(-4)', '-3MO': 'MO(-3)', '-2MO': 'MO(-2)', '-1MO': 'MO(-1)', 'MO': 'MO', '1MO': 'MO(1)', '2MO': 'MO(2)', '3MO': 'MO(3)', '4MO': 'MO(4)', '-4TU': 'TU(-4)', '-3TU': 'TU(-3)', '-2TU': 'TU(-2)', '-1TU': 'TU(-1)', 'TU': 'TU', '1TU': 'TU(1)', '2TU': 'TU(2)', '3TU': 'TU(3)', '4TU': 'TU(4)', '-4WE': 'WE(-4)', '-3WE': 'WE(-3)', '-2WE': 'WE(-2)', '-1WE': 'WE(-1)', 'WE': 'WE', '1WE': 'WE(1)', '2WE': 'WE(2)', '3WE': 'WE(3)', '4WE': 'WE(4)', '-4TH': 'TH(-4)', '-3TH': 'TH(-3)', '-2TH': 'TH(-2)', '-1TH': 'TH(-1)', 'TH': 'TH', '1TH': 'TH(1)', '2TH': 'TH(2)', '3TH': 'TH(3)', '4TH': 'TH(4)', '-4FR': 'FR(-4)', '-3FR': 'FR(-3)', '-2FR': 'FR(-2)', '-1FR': 'FR(-1)', 'FR': 'FR', '1FR': 'FR(1)', '2FR': 'FR(2)', '3FR': 'FR(3)', '4FR': 'FR(4)', '-4SA': 'SA(-4)', '-3SA': 'SA(-3)', '-2SA': 'SA(-2)', '-1SA': 'SA(-1)', 'SA': 'SA', '1SA': 'SA(1)', '2SA': 'SA(2)', '3SA': 'SA(3)', '4SA': 'SA(4)', '-4SU': 'SU(-4)', '-3SU': 'SU(-3)', '-2SU': 'SU(-2)', '-1SU': 'SU(-1)', 'SU': 'SU', '1SU': 'SU(1)', '2SU': 'SU(2)', '3SU': 'SU(3)', '4SU': 'SU(4)'}
# WKDAYS_ENCODE:
# {'MO(-4)': '-4MO', 'MO(-3)': '-3MO', 'MO(-2)': '-2MO', 'MO(-1)': '-1MO', 'MO(+1)': '+1MO', 'MO(+2)': '+2MO', 'MO(+3)': '+3MO', 'MO(+4)': '+4MO', 'TU(-4)': '-4TU', 'TU(-3)': '-3TU', 'TU(-2)': '-2TU', 'TU(-1)': '-1TU', 'TU(+1)': '+1TU', 'TU(+2)': '+2TU', 'TU(+3)': '+3TU', 'TU(+4)': '+4TU', 'WE(-4)': '-4WE', 'WE(-3)': '-3WE', 'WE(-2)': '-2WE', 'WE(-1)': '-1WE', 'WE(+1)': '+1WE', 'WE(+2)': '+2WE', 'WE(+3)': '+3WE', 'WE(+4)': '+4WE', 'TH(-4)': '-4TH', 'TH(-3)': '-3TH', 'TH(-2)': '-2TH', 'TH(-1)': '-1TH', 'TH(+1)': '+1TH', 'TH(+2)': '+2TH', 'TH(+3)': '+3TH', 'TH(+4)': '+4TH', 'FR(-4)': '-4FR', 'FR(-3)': '-3FR', 'FR(-2)': '-2FR', 'FR(-1)': '-1FR', 'FR(+1)': '+1FR', 'FR(+2)': '+2FR', 'FR(+3)': '+3FR', 'FR(+4)': '+4FR', 'SA(-4)': '-4SA', 'SA(-3)': '-3SA', 'SA(-2)': '-2SA', 'SA(-1)': '-1SA', 'SA(+1)': '+1SA', 'SA(+2)': '+2SA', 'SA(+3)': '+3SA', 'SA(+4)': '+4SA', 'SU(-4)': '-4SU', 'SU(-3)': '-3SU', 'SU(-2)': '-2SU', 'SU(-1)': '-1SU', 'SU(+1)': '+1SU', 'SU(+2)': '+2SU', 'SU(+3)': '+3SU', 'SU(+4)': '+4SU', 'MO': 'MO', 'TU': 'TU', 'WE': 'WE', 'TH': 'TH', 'FR': 'FR', 'SA': 'SA', 'SU': 'SU'}


AWARE_FMT = '%Y%m%dT%H%MA'
NAIVE_FMT = '%Y%m%dT%H%MN'
DATE_FMT = '%Y%m%d'


def normalize_timedelta(delta):
    total_seconds = delta.total_seconds()
    sign = '-' if total_seconds < 0 else ''
    minutes, remainder = divmod(abs(int(total_seconds)), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)

    until = []
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

    return sign + ''.join(until)


# Test
td = timedelta(days=-1, hours=2, minutes=30)
normalized_td = normalize_timedelta(td)

td = timedelta(days=1, hours=-2, minutes=-30)
normalized_td = normalize_timedelta(td)


def encode_datetime(obj):
    if not isinstance(obj, datetime):
        raise ValueError(f'{obj} is not a datetime instance')
    if is_aware(obj):
        return obj.astimezone(ZoneInfo('UTC')).strftime(AWARE_FMT)
    else:
        return obj.strftime(NAIVE_FMT)


def decode_datetime(s):
    if s[-1] not in 'AN' or len(s) != 14:
        raise ValueError(f'{s} is not a datetime string')
    if s[-1] == 'A':
        return (
            datetime.strptime(s, AWARE_FMT)
            .replace(tzinfo=ZoneInfo('UTC'))
            .astimezone()
        )
    else:
        return datetime.strptime(s, NAIVE_FMT).astimezone(None)


class Period:
    def __init__(self, datetime1, datetime2):
        # datetime1: done/start; datetime2: due/end. On time => period positive
        # Ensure both inputs are datetime.datetime instances
        if not isinstance(datetime1, datetime) or not isinstance(
            datetime2, datetime
        ):
            raise ValueError('Both inputs must be datetime instances')

        aware1 = is_aware(datetime1)
        aware2 = is_aware(datetime2)

        if aware1 != aware2:
            raise ValueError(
                f'start: {datetime1.tzinfo}, end: {datetime2.tzinfo}. Both datetimes must either be naive or both must be aware.'
            )

        if aware1:
            self.start = datetime1.astimezone(ZoneInfo('UTC'))
            self.end = datetime2.astimezone(ZoneInfo('UTC'))
        else:
            self.start = datetime1.replace(tzinfo=None)
            self.end = datetime2.replace(tzinfo=None)

        self.diff = self.end - self.start

    def __repr__(self):
        return f'Period({encode_datetime(self.start)} -> {encode_datetime(self.end)}, {normalize_timedelta(self.diff)})'

    def __eq__(self, other):
        if isinstance(other, Period):
            return self.start == other.start
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Period):
            return self.start < other.start
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Period):
            return self.start > other.start
        return NotImplemented

    # Optionally, define __le__ and __ge__
    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    def start(self):
        return self.start

    def end(self):
        return self.end

    def diff(self):
        return self.diff
