#! /usr/bin/env python3

import datetime
from dateutil.parser import parse

import re
at_regex = re.compile(r'\s@', re.MULTILINE)
amp_regex = re.compile(r'\s&', re.MULTILINE)


type_keys = {
    "*": "event",
    "-": "task",
    "#": "journal entry",
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
    'i': "index (colon delimited string)",
    'j': "job summary (string)",
    'l': "location (string)",
    'm': "memo (string)",
    'o': "overdue (r)estart, s)kip or k)eep)",
    'p': "priority (integer)",
    'r': "repetition frequency (y)ear, m)onth, w)eek, d)ay, h)our, M)inute",
    's': "start (date or date-time)",
    't': "tags (list of strings)",
    'v': "value (defaults key)",
    'z': "timezone (string)",
}

amp_keys = {
    'r': {
        'E': "easter: number of days before (-), on (0)  or after (+) Easter",
        'h': "hour: list of integers in 0 ... 23",
        'i': "interval: positive integer",
        'M': "month: list of integers in 1 ... 12",
        'm': "monthday: list of integers 1 ... 31",
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
        'l': "location: string",
        'p': "prerequisites: comma separated list of uids of immediate prereqs",
        's': "start/due: timeperiod before task start",
        'u': "uid: unique identifier: integer or string",
    },
}

allowed = {}
required = {}
rruleset_methods = '+-r'
item_methods = 'degclmitv'
task_methods = 'fjp'
date_methods = 'sb'
datetime_methods = date_methods + 'eaz' 


allowed['*'] = item_methods + datetime_methods + rruleset_methods 
required['*'] = 's'

allowed['-'] = item_methods + task_methods + datetime_methods
required['-'] = []

type_prompt = u"type character for new item:\n"
item_types = u"item type characters:\n  *: event\n  -: task\n  #: journal entry\n  ?: someday entry\n  !: nbox entry"

def etm_parse(s):
    """
    Return a date object if the parsed time is exactly midnight. Otherwise return a datetime object. 
    >>> dt = etm_parse("2015-10-15 2p")
    >>> dt
    datetime.datetime(2015, 10, 15, 14, 0)

    >>> dt = etm_parse("2015-10-15 0h")
    >>> dt
    datetime.date(2015, 10, 15)

    >>> dt = etm_parse("2015-10-15")
    >>> dt
    datetime.date(2015, 10, 15)

    To get a datetime object for midnight use one second past midnight:
    >>> dt = etm_parse("2015-10-15 12:00:01a")
    >>> dt
    datetime.datetime(2015, 10, 15, 0, 0)
    """

    res = parse(s)
    if (res.hour, res.minute, res.second, res.microsecond) == (0, 0, 0, 0):
        return res.date()
    else:
        return res.replace(second=0, microsecond=0)



def check_entry(s, p):
    """
    Check the entry string s with the cursor at position o and return 'ask' and 'reply' tuples in the format (palette_key, display_string).
    """
