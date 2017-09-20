#! /usr/bin/env python3

import datetime
from dateutil.parser import parse
from dateutil.tz import gettz, tzutc, tzlocal

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
undated_methods = 'cdgilmtv'
date_methods = 'sb'
datetime_methods = date_methods + 'eaz' 
task_methods = 'fjp'

# events
allowed['*'] = undated_methods + datetime_methods + rruleset_methods 
required['*'] = 's'

# tasks
allowed['-'] = undated_methods + task_methods + datetime_methods + rruleset_methods
required['-'] = []

# journal entries
allowed['#'] = undated_methods + task_methods + datetime_methods
required['#'] = ''

# someday entries
allowed['?'] = undated_methods + task_methods + datetime_methods
required['?'] = ''

# inbox entries
allowed['!'] = undated_methods + task_methods + datetime_methods + rruleset_methods
required['!'] = ''


type_prompt = u"type character for new item:\n"
item_types = u"item type characters:\n  *: event\n  -: task\n  #: journal entry\n  ?: someday entry\n  !: nbox entry"

def etm_parse(s):
    """
    Return a date object if the parsed time is exactly midnight. Otherwise return a datetime object. 
    >>> dt = etm_parse("2015-10-15 2p")[1]
    >>> dt
    datetime.datetime(2015, 10, 15, 14, 0)

    >>> dt = etm_parse("2015-10-15 0h")[1]
    >>> dt
    datetime.date(2015, 10, 15)

    >>> dt = etm_parse("2015-10-15")[1]
    >>> dt
    datetime.date(2015, 10, 15)

    To get a datetime object for midnight use one second past midnight:
    >>> dt = etm_parse("2015-10-15 12:00:01a")[1]
    >>> dt
    datetime.datetime(2015, 10, 15, 0, 0)
    """

    try:
        res = parse(s)
    except:
        return False, "Could not parse {}".format(s)

    if (res.hour, res.minute, res.second, res.microsecond) == (0, 0, 0, 0):
        return 'date', res.date()
    else:
        return 'datetime', res.replace(second=0, microsecond=0)


def format_datetime(obj, tz=None):
    pass


def get_datetime_state(at_hsh = {}):
    """
    Check the currents state of at_hsh regarding the 's' and 'z' keys

    """

    s = at_hsh.get('s', None)
    z = at_hsh.get('z', None)
    msg = ''
    if s is not None:
        ok, S = etm_parse(s)
        if not ok:
            return 
        if ok == 'date':
            state = 'dateonly'
            if z is not None:
                msg = 'An entry for @z is not allowed with a date-only entry for @s'
        elif ok == 'datetime':
            if z == 'float':
                state = 'naive'
                msg = "@s {} will be interpreted as naive".format
            else:
                state = 'aware'
                if z is None:
                    msg = "The datetime entry for @s will be interpreted as an aware datetime in the current local timezone"
                else:
                    msg = "The datetime entry for @s will be interpreted as an aware datetime in the timezone {}".format(z)



def check_entry(entry_text, pos):
    """
    Check the entry string s with the cursor at position o and return appropriate 'ask' and 'reply' tuples in the format (palette_key, display_string). 
    """
    at_parts = at_regex.split(entry_text)
    at_tups = []
    at_hsh = {}
    ask = ('say', '')
    reply = ('say', '')
    if at_parts:
        tmp = -1
        for part in at_parts:
            if not part:
                # @ entered but without key
                break
            if len(part) > 1:
                at_hsh[part[0]] = part[1:].strip()
            else:
                at_hsh[part[0]] = ''
            at_tups.append( (part[0], at_hsh[part[0]], tmp) )
            tmp += 2 + len(part)

    if at_tups:
        itemtype, summary, end = at_tups.pop(0)
        act_key = itemtype
        act_val = summary
        for tup in at_tups:
            if tup[-1] < pos:
                act_key = tup[0]
                act_val = tup[1]
            else:
                break
        if itemtype in type_keys:
            ask = ('say', "summary for {}:\n".format(type_keys[itemtype]))
            if act_key == itemtype:
                reply = ('say', "{0}\n  required: {1}\n  allowed: {2}\n  default: {3}".format(type_keys[itemtype], 
                        ", ".join(["@%s" % x for x in required[itemtype]]), 
                        ", ".join(["@%s" % x for x in allowed[itemtype] if x not in required[itemtype]]),
                            ""
                             ))

            elif act_key in allowed[itemtype]:
                if act_val:
                    ask = ('say', "{0}: {1}\n".format(at_keys[act_key], act_val))
                else:
                    ask = ('say', "{0}:\n".format(at_keys[act_key]))
            else:
                ask = ('warn', "invalid @-key: '@{0}'\n".format(act_key))

        else:
            ask = ('warn', u"invalid item type character: '{0}'\n".format(itemtype))
            summary = "{0}{1}".format(itemtype, summary)
    else:
        ask = ('say', type_prompt)
        reply = ('say', item_types)
    reply = ('say', ", ".join(["'{}'".format(x) for x in at_parts]))
    return ask, reply

if __name__ == '__main__':
    print('\n\n')
    import doctest
    doctest.testmod()

