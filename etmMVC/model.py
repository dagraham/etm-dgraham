#!/usr/bin/env python3

import pendulum
from pendulum import parse, timezone

from datetime import datetime

import sys
import re

from tinydb_serialization import Serializer
from tinydb import TinyDB, Query, Storage
from tinydb.operations import delete
from tinydb.database import Table
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_smartcache import SmartCacheTable

from copy import deepcopy
import calendar as clndr

from dateutil.easter import easter
import dateutil.rrule as dtutrrule
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

def parse_datetime(s):
    """
    's' will have the format 'datetime string' followed, optionally by a comma and a tz specification. Return a 'date' object if the parsed datetime is exactly midnight. Otherwise return a naive datetime object if tz == 'float' or an aware datetime object using tzlocal if tz is None (missing) and using the provided tz otherwise.  
    >>> dt = parse_datetime("2015-10-15 2p")
    >>> dt[1]
    <Pendulum [2015-10-15T14:00:00-04:00]>
    >>> dt = parse_datetime("2015-10-15")
    >>> dt[1]
    <Pendulum [2015-10-15T00:00:00+00:00]>

    To get a datetime for midnight, schedule for 1 second later and note
    that the second is removed from the datetime:
    >>> dt = parse_datetime("2015-10-15 00:00:01")
    >>> dt[1]
    <Pendulum [2015-10-15T00:00:01-04:00]>
    >>> dt = parse_datetime("2015-10-15 2p, float")
    >>> dt[1]
    <Pendulum [2015-10-15T14:00:00+00:00]>
    >>> dt[1].tzinfo
    <TimezoneInfo [Factory, -00, +00:00:00, STD]>
    >>> dt = parse_datetime("2015-10-15 2p, US/Pacific")
    >>> dt[1]
    <Pendulum [2015-10-15T21:00:00+00:00]>
    >>> dt[1]
    <TimezoneInfo [UTC, GMT, +00:00:00, STD]>
    """
    parts = s.split(", ")
    if len(parts) < 2:
        tz = tzinfo = None
        ok = 'none'
    else:
        tz = parts[1].strip()
        if tz == 'float':
            tzinfo = 'Factory'
            ok = 'naive'
        else:
            tzfino = tz
            ok = 'aware'
    s = parts[0]

    try:
        res = parse(s, tz=tzinfo)
    except:
        return False, "Could not process '{}'".format(s), tz
    else:
        if (res.hour, res.minute, res.second, res.microsecond) == (0, 0, 0, 0):
            return 'date', res.replace(tzinfo='Factory'), tz
        elif ok == 'aware':
            return ok, res.in_timezone('UTC'), tz
        else:
            return ok, res, tz

def format_datetime(obj):
    """
    >>> format_datetime(parse_datetime("20160710T1730")[1])
    (True, 'Sun Jul 10 2016 5:30PM EDT')
    >>> format_datetime(parse_datetime("2015-07-10 5:30p, float")[1])
    (True, 'Fri Jul 10 2015 5:30PM')
    >>> format_datetime(parse_datetime("20160710")[1])
    (True, 'Sun Jul 10 2016')
    >>> format_datetime("20160710T1730")
    (False, 'The argument must be a pendulum date or datetime.')
    """
    if type(obj) == datetime:
        obj = pendulum.instance(obj)
    if type(obj) != pendulum.pendulum.Pendulum:
        return False, "The argument must be a pendulum date or datetime."

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



period_regex = re.compile(r'(([+-]?)(\d+)([wdhm]))+?')
threeday_regex = re.compile(r'(MON|TUE|WED|THU|FRI|SAT|SUN)',
                        re.IGNORECASE)
anniversary_regex = re.compile(r'!(\d{4})!')

period_hsh = dict(
    z=pendulum.Interval(seconds=0),
    m=pendulum.Interval(minutes=1),
    h=pendulum.Interval(hours=1),
    d=pendulum.Interval(days=1),
    w=pendulum.Interval(weeks=1),
        )

def parse_period(s):
    """\
    Take a period string and return a corresponding pendulum interval.
    Examples:
        parse_period('-2w3d4h5m')= Interval(weeks=-2,days=3,hours=4,minutes=5)
        parse_period('1h30m') = Interval(hours=1, minutes=30)
        parse_period('-10m') = Interval(minutes=10)
    where:
        w: weeks
        d: days
        h: hours
        m: minutes

    >>> 3*60*60+5*60
    11100
    >>> parse_period("2d-3h5m")[1]
    <Interval [1 day 21 hours 5 minutes]>
    >>> pendulum.create(2015, 10, 15, 9, 0, tz='local') + parse_period("-25m")[1]
    <Pendulum [2015-10-15T08:35:00-04:00]>
    >>> pendulum.create(2015, 10, 15, 9, 0) + parse_period("1d")[1]
    <Pendulum [2015-10-16T09:00:00+00:00]>
    >>> pendulum.create(2015, 10, 15, 9, 0) + parse_period("1w-2d+3h")[1]
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
        etmdir = os.path.normpath(os.path.join(os.path.expanduser("~/.etm-lite")))


    if not os.path.isdir(etmdir):
        # root_logger = logging.getLogger()
        # root_logger.disabled = True
        return

    log_levels = {
        '1': logging.DEBUG,
        '2': logging.INFO,
        '3': logging.WARN,
        '4': logging.ERROR,
        '5': logging.CRITICAL
    }

    if level in log_levels:
        loglevel = log_levels[level]
    else:
        loglevel = log_levels['3']

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
        msg = "{0} timer started".format(self.label)
        if self.loglevel == 1:
            logger.debug(msg)
        elif self.loglevel == 2:
            logger.info(msg)
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



def wrap(txt, indent=5, width=shutil.get_terminal_size()[0]):
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
    para = [textwrap.dedent(x).strip() for x in txt.split('\n')]
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
    >>> set_summary('!1944! birthday')
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
{{ h.itemtype }} {{ h.summary }}\
{% if 's' in h %}{{ " @s {}".format(dt2str(h['s'])[1]) }}{% endif %} \
{% for k in ['e', 'b', 'l', 'c', 'n', 'm', 'g', 'u', 'i', 'v', 'f', 'h', 'p', 'q'] -%}\
{%- if k in h %}@{{ k }} {{ h[k] }} {% endif %}\
{%- endfor %}\
{% if 't' in h %}{{ "@t {}".format(", ".join(h['t'])) }} {% endif %}\
{% if 'a' in h %}\
{%- for x in h['a'] %}{{ "@a {}: {}".format(x[0], ", ".join(x[1:])) }} {% endfor %}\
{% endif %}\
{%- if 'z' in h %}@z {{ h['z'] }}{% endif -%} \
{%- if 'r' in h %}
    {%- for x in h['r'] %}
    {%- set rrule -%}
        {{ x['r'] }}\
        {%- for k in ['i', 's', 'u', 'M', 'm', 'w', 'h', 'u', 'E'] -%}
            {%- if k in x %} {{ "&{} {}".format(k, one_or_more(x[k])) }} {%- endif %}
        {%- endfor %}
    {%- endset %}
  @r {{ wrap(rrule) }}\
    {%- endfor %}
{%- endif -%}
{% for k in ['+', '-', 'h'] -%}
    {%- if k in h and h[k] %}
  @{{ k }} {{ wrap(", ".join(h[k])) }}
    {%- endif -%}\
{%- endfor %}\
{% if 'd' in h %}
  @d {{ wrap(h['d']) }}\
{% endif -%}
{%- if 'j' in h %}
    {%- for x in h['j'] %}
    {%- set job -%}
        {{ x['j'] }}\
        {%- for k in ['s', 'b', 'd', 'e', 'f', 'l', 'i', 'p'] -%}
            {%- if k in x and x[k] %} {{ "&{} {}".format(k, one_or_more(x[k])) }}{% endif %}\
        {%- endfor %}
        {%- if 'a' in x %}\
            {%- for a in x['a'] %} &a {{ "{}: {}".format(a[0], ", ".join(a[1:])) }}{% endfor %}\
        {%- endif %}\
    {%- endset %}
  @j {{ wrap(job) }}\
    {%- endfor %}\
{%- endif -%}
"""

jinja_entry_template = Template(entry_tmpl)
jinja_entry_template.globals['dt2str'] = format_datetime
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
    return parse_period(arg)


def history(arg):
    """
    Return a list of properly formatted completions.
    >>> history("4/1 2p")
    (True, ['20160401T1400'])
    >>> history(["4/31 2p", "6/1 7a"])
    (False, 'invalid date-time: 4/31 2p')
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

    freq = [x for x in rrule_frequency]
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

rrule_names = {
    # 'r': 'FREQUENCY',  # unicode
    'i': 'INTERVAL',  # positive integer
    'c': 'COUNT',  # integer
    's': 'BYSETPOS',  # integer
    'u': 'UNTIL',  # unicode
    'M': 'BYMONTH',  # integer 1...12
    'm': 'BYMONTHDAY',  # positive integer
    'W': 'BYWEEKNO',  # positive integer
    'w': 'BYWEEKDAY',  # integer 0 (SU) ... 6 (SA)
    'h': 'BYHOUR',  # positive integer
    'n': 'BYMINUTE',  # positive integer
    'E': 'BYEASTER',  # non-negative integer number of days after easter
}

# rrule_keys = [x for x in "iMmWwhnEus"]
rrule_keys = [x for x in rrule_names]
rrule_keys.sort()

rrule_frequency = {
    'y': 'YEARLY',
    'm': 'MONTHLY',
    'w': 'WEEKLY',
    'd': 'DAILY',
    'h': 'HOURLY',
    'n': 'MINUTELY',
    'E': 'EASTERLY',
}


def rrule(lofh):
    """
    An rrule hash or a sequence of such hashes.
    >>> data = {'r': ''}
    >>> rrule(data)
    (False, 'repetition frequency: character from (y)early, (m)onthly, (w)eekly, (d)aily, (h)ourly or mi(n)utely.')
    >>> good_data = {"M": 5, "i": 1, "m": 3, "r": "y", "w": "2SU"}
    >>> pprint(rrule(good_data))
    (True,
     [{'M': [5],
       'i': 1,
       'm': [3],
       'r': 'y',
       'rrulestr': 'RRULE:FREQ=YEARLY;BYMONTH=5;INTERVAL=1;BYMONTHDAY=3;BYWEEKDAY=2SU',
       'w': ['2SU']}])
    >>> good_data = {"M": [5, 12], "i": 1, "m": [3, 15], "r": "y", "w": "2SU"}
    >>> pprint(rrule(good_data))
    (True,
     [{'M': [5, 12],
       'i': 1,
       'm': [3, 15],
       'r': 'y',
       'rrulestr': 'RRULE:FREQ=YEARLY;BYMONTH=5,12;INTERVAL=1;BYMONTHDAY=3,15;BYWEEKDAY=2SU',
       'w': ['2SU']}])
    >>> bad_data = [{"M": 5, "i": 1, "m": 3, "r": "y", "w": "2SE"}, {"M": [11, 12], "i": 4, "m": [2, 3, 4, 5, 6, 7, 8], "r": "z", "w": ["TU", "-1FR"]}]
    >>> print(rrule(bad_data))
    (False, 'invalid weekdays: 2SE; invalid frequency: z not in (y)early, (m)onthly, (w)eekly, (d)aily, (h)ourly or mi(n)utely.')
    >>> data = [{"r": "w", "w": "TU", "h": 14}, {"r": "w", "w": "TH", "h": 16}]
    >>> pprint(rrule(data))
    (True,
     [{'h': [14],
       'i': 1,
       'r': 'w',
       'rrulestr': 'RRULE:FREQ=WEEKLY;BYHOUR=14;BYWEEKDAY=TU',
       'w': ['TU']},
      {'h': [16],
       'i': 1,
       'r': 'w',
       'rrulestr': 'RRULE:FREQ=WEEKLY;BYHOUR=16;BYWEEKDAY=TH',
       'w': ['TH']}])
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
            l = ["RRULE:FREQ=%s" % rrule_frequency[hsh['r']]]

            for k in rrule_keys:
                if k in hsh and hsh[k]:
                    v = hsh[k]
                    if type(v) == list:
                        v = ",".join(map(str, v))
                    if k == 'w':
                        # make weekdays upper case
                        v = v.upper()
                        m = threeday_regex.search(v)
                        while m:
                            v = threeday_regex.sub("%s" % m.group(1)[:2], v, count=1)
                            m = threeday_regex.search(v)
                    l.append("%s=%s" % (rrule_names[k], v))
            res['rrulestr'] = ";".join(l)
            ret.append(res)

    if msg:
        return False, "{}".format("; ".join(msg))
    else:
        return True, ret

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
    # f=date_time,
    h=history,
    j=title,
    l=location,
    # q=date_time,
    # The last two require consideration of the whole list of jobs
    i=id,
    p=prereqs,
)

datetime_job_methods = dict(
    # a=alert,
    b=beginby,
    # s=job_date_time
)
datetime_job_methods.update(undated_job_methods)

def jobs(lofh, dated=False):
    """
    Process the job hashes in lofh
    >>> data = [{'j': 'Job One', 'a': '2d: m', 'b': 2, 'f': '6/20 12p'}, {'j': 'Job Two', 'a': '1d: m', 'b': 1}, {'j': 'Job Three', 'a': '6h: m'}]
    >>> pprint(jobs(data))

    """
    if dated:
        job_methods = datetime_job_methods
    else:
        job_methods = undated_job_methods

    msg = []
    rmd = []
    ret = []
    req = {}
    id2hsh = {}
    first = True
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
            elif key not in job_methods:
                not_allowed.append("'&{}'".format(key))
            else:
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
        if id2hsh[i].get('f', None):
            this_completion = id2hsh[i]['f']
            if last_completion is None or last_completion < this_completion:
                last_completion = this_completion
                # print('last_completion', last_completion)
        else:
            last_completion = None
            break

    for i in ids:
        if last_completion:
            # remove all completions
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
        id2hsh[i]['summary'] = "{}: {}".format("/".join([str(x) for x in faw]), id2hsh[i]['j'])
        id2hsh[i]['req'] = req[i]

    if msg:
        # print('msg', msg)
        # return False, msg
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

class DatetimeCacheTable(SmartCacheTable):

    def _get_next_id(self):
        """
        Use a readable, integer timestamp as the id - unique and stores
        the creation datetime - instead of consecutive integers. E.g.,
        the the id for an item created 2016-06-24 08:14:11:601637 would
        be 20160624081411601637.
        """
        # This must be an int even though it will be stored as a str
        current_id = int(pendulum.now('UTC').format("%Y%m%d%H%M%S%f"))
        self._last_id = current_id

        return current_id


TinyDB.table_class = DatetimeCacheTable

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
        return "{0}.{1}".format(obj.days, obj.seconds)

    def decode(self, s):
        """
        Return the serialization as a timedelta object.
        """
        days_seconds = (int(x) for x in s.split('.')) 
        return pendulum.Interval(*days_seconds)


serialization = SerializationMiddleware()
serialization.register_serializer(PendulumDateTimeSerializer(), 'TinyPendulumDateTime')
serialization.register_serializer(PendulumDateSerializer(), 'TinyPendulumDate')
serialization.register_serializer(PendulumIntervalSerializer(), 'TinyPendulumInterval')

########################
### end TinyDB setup ###
########################


if __name__ == '__main__':
    print('\n\n')
    import doctest
    from pprint import pprint
    doctest.testmod()

    db = TinyDB('db.json', storage=serialization)
    db.purge()
    db.insert({'naive pendulum': pendulum.Pendulum(2017, 9, 7, 14, 0, 0, tzinfo='Factory')})

    db.insert({'pacific pendulum': pendulum.Pendulum(2017, 9, 7, 14, 0, 0, tzinfo='US/Pacific') })
    db.insert({'local pendulum': pendulum.Pendulum(2017, 9, 7, 14, 0, 0, tzinfo='local') })
    db.insert({'pendulum list': [pendulum.Pendulum(2017, 9, 7, 12, 0, 0), pendulum.Pendulum(2017, 9, 7, 12, 0, 0, tzinfo='Factory'), pendulum.Pendulum(2017, 9, 7, 12, 0, 0, tzinfo='US/Pacific')]})
    # Absent tzinfo, the first item will be interpreted as noon UTC and will display as 8am Eastern. For the second where Factory is given explicitly, the item will be interpreted as noon in whatever the local timezone, i.e., an offset of 0, and thus noon Eastern. The third will be interpreted as noon Pacific and will display as 3pm Eastern.
    db.insert({'pendulum date': pendulum.Pendulum(2017, 9, 7, tzinfo='Factory').date() })
    db.insert({'pendulum interval': pendulum.Interval(weeks=1, days=3, hours=7, minutes=15)})
    # hsh = {'type': '*', 'summary': 'my event', 's':  datetime(2017, 9, 7, 12, 0, 0, tzinfo=gettz('US/Pacific')), 'e': timedelta(hours=1, minutes=15)}
    # db.insert(hsh)
    for item in db:
        print(item.eid, item)

