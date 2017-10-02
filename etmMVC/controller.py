 #! /usr/bin/env python3

import pendulum
pendulum.set_formatter('alternative')

# from dateutil.tz import gettz, tzutc, tzlocal

from model import ONEWEEK, ONEDAY, ONEHOUR, ONEMINUTE 
from model import parse_datetime, parse_period

import re
at_regex = re.compile(r'\s+@', re.MULTILINE)
amp_regex = re.compile(r'\s+&', re.MULTILINE)
week_regex = re.compile(r'[+-]?(\d+)w', flags=re.I)
day_regex = re.compile(r'[+-]?(\d+)d', flags=re.I)
hour_regex = re.compile(r'[+-]?(\d+)h', flags=re.I)
minute_regex = re.compile(r'[+-]?(\d+)m', flags=re.I)
sign_regex = re.compile(r'(^\s*([+-])?)')
int_regex = re.compile(r'^\s*([+-]?\d+)\s*$')
period_string_regex = re.compile(r'^\s*([+-]?(\d+[wWdDhHmM])+\s*$)')
period_parts = re.compile(r'([wWdDhHmM])')

# item_hsh = {} # preserve state

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
    's': "starting date or datetime",
    't': "tags (list of strings)",
    'v': "value (defaults key)",
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
    's': {
        'z': "timezone (string)",
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
undated_methods = 'cdgilmstv'
date_methods = 'b'
datetime_methods = date_methods + 'ea' 
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


def deal_with_at(at_hsh={}):
    """
    When an '@' has been entered but not yet with its key, show required and available keys with descriptions. Note, for example, that until a valid entry for @s has been given, @a, @b and @z are not available.
    """
    pass

deal_with = {}
item_hsh = {}

def deal_with_s(at_hsh = {}, item_hsh={}):
    """
    Check the currents state of at_hsh regarding the 's' and 'z' keys

    """
    s = at_hsh.get('s', None)
    top = "{}?\n".format(at_keys['s'])
    bot = ''
    if s is None:
        return top, bot
    ok, obj = parse_datetime(s)
    if not ok or not obj:
        return top, "considering: '{}'".format(s), None
    item_hsh['s'] = obj
    bot = "starting: {}".format(format_datetime(obj))
    if ok == 'date':
        # 'dateonly'
        bot += '\nWithout a time, this schedules an all-day, floating item for the specified date in whatever happens to be the local timezone.'
    elif ok == 'naive':
        bot += "\nThe datetime entry for @s will be interpreted as a naive datetime in whatever happens to be the local timezone."
    elif ok == 'aware':
        bot += "\nThe datetime entry for @s will be interpreted as an aware datetime in the specified timezone."
    else:
        bot += "\nThe datetime entry for @s will be interpreted as an aware datetime in the current local timezone. Append a comma and then 'float' to make the datetime floating (naive) or a specific timezone, e.g., 'US/Pacific', to use that timezone instead of the local one."

    bot += "\n{}".format(str(at_hsh))
    return top, bot, item_hsh

deal_with['s'] = deal_with_s

def deal_with_e(at_hsh={}, item_hsh={}):
    """
    Check the current state of at_hsh regarding the 'e' key.
    """
    s = at_hsh.get('e', None)
    top = "{}?\n".format(at_keys['e'])
    bot = ''
    if s is None:
        return top, bot
    ok, obj = parse_period(s)
    if not ok:
        return top, "considering: '{}'".format(s)
    item_hsh['e'] = obj
    bot = "extending from {0} until {1}".format(format_datetime(item_hsh['s']), format_datetime(item_hsh['s'] + item_hsh['e']))
    bot += "\n{}".format(str(at_hsh))
    return top, bot, item_hsh

deal_with['e'] = deal_with_e

def str2hsh(s, cursor_pos=0, complete=False):
    """
    Process an item string and return a corresponding hash with no validation or processing of key values.
    >>> pprint(str2hsh("* lunch @s sat 2p @e 2h @a 1h, 30m, 15m @z US/Eastern"))
    {'a': ['1h, 30m, 15m'],
     'e': '2h',
     'itemtype': '*',
     's': 'sat 2p',
     'summary': 'lunch',
     'z': 'US/Eastern'}
    >>> pprint(str2hsh("- group @s mon @a 1d: e @a 1h: m @j job one &i 1 &p '' @j job two &i 2 &p 1"))
    {'a': ['1d: e', '1h: m'],
     'itemtype': '-',
     'j': [{'i': '1', 'j': 'job one'}, {'i': '2', 'j': 'job two', 'p': '1'}],
     's': 'mon',
     'summary': 'group'}
    >>> pprint(str2hsh("- group @s mon @j job A &i a &p b, c @j job B &i b &p '' @j job C &i c &p ''"))
    {'itemtype': '-',
     'j': [{'i': 'a', 'j': 'job A', 'p': 'b, c'},
           {'i': 'b', 'j': 'job B'},
           {'i': 'c', 'j': 'job C'}],
     's': 'mon',
     'summary': 'group'}
    >>> pprint(str2hsh("- repeat @s mon @r d &i 3 &u fri"))
    {'itemtype': '-',
     'r': [{'i': '3', 'r': 'd', 'u': 'fri'}],
     's': 'mon',
     'summary': 'repeat'}
    >>> str2hsh("")
    {}
    >>> pprint(str2hsh("* repeat @s mon @r d &i 3 &u fri"))
    {'itemtype': '*',
     'r': [{'i': '3', 'r': 'd', 'u': 'fri'}],
     's': 'mon',
     'summary': 'repeat'}
    >>> pprint(str2hsh("* repeat @s mon @r d &i 3 &u"))
    {'itemtype': '*', 'r': [{'i': '3', 'r': 'd'}], 's': 'mon', 'summary': 'repeat'}
    >>> pprint(str2hsh("* repeat @s mon @r d &i"))
    {'itemtype': '*', 'r': [{'r': 'd'}], 's': 'mon', 'summary': 'repeat'}
    >>> pprint(str2hsh("* repeat @s mon @r d &"))
    {'itemtype': '*', 'r': [{'r': 'd'}], 's': 'mon', 'summary': 'repeat'}
    >>> pprint(str2hsh("* repeat @s mon @r d "))
    {'itemtype': '*', 'r': [{'r': 'd'}], 's': 'mon', 'summary': 'repeat'}
    >>> pprint(str2hsh("* repeat @s mon @r"))
    {'itemtype': '*', 's': 'mon', 'summary': 'repeat'}
    >>> pprint(str2hsh("* repeat @"))
    {'itemtype': '*', 'summary': 'repeat'}
    >>> pprint(str2hsh("* "))
    {'itemtype': '*', 'summary': ''}
    """
    global item_hsh
    msg = []
    hsh = {}

    if not s:
        return hsh

    at_parts = [x.strip() for x in at_regex.split(s)]
    at_tups = []
    ask = ('say', '')
    reply = ('say', '')
    at_entry = False
    if at_parts:
        # print('at_part0 : "{}"'.format(at_parts[0]))
        place = -1
        tmp = at_parts.pop(0)
        hsh['itemtype'] = tmp[0]
        hsh['summary'] = tmp[1:].strip()
        at_tups.append( (hsh['itemtype'], hsh['summary'], place) )
        place += 2 + len(tmp)

        for part in at_parts:
            if part:
                at_entry = False
                if len(part) < 2:
                    continue
            else:
                at_entry = True
                break
            k = part[0]
            v = part[1:].strip()
            if v in ['', ""]:
                pass
            elif k in ('a', 'j', 'r'):
                # there can be more than one entry for these keys
                hsh.setdefault(k, []).append(v)
            else:
                hsh[k] = v
            at_tups.append( (k, v, place) )
            place += 2 + len(part)

    for key in ['r', 'j']:
        if key not in hsh: continue
        lst = []
        for part in hsh[key]:  # an individual @r or @j entry
            amp_hsh = {}
            amp_parts = [x.strip() for x in amp_regex.split(part)]
            if amp_parts:
                amp_hsh[key] = "".join(amp_parts.pop(0))
                # k = amp_part
                for part in amp_parts:  # the & keys and values for the given entry
                    if len(part) < 2:
                        continue
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
                lst.append(amp_hsh)
        hsh[key] = lst

    if item_hsh:
        for key in item_hsh:
            if key not in hsh:
                del item_hsh[key]

    if at_tups:
        # itemtype, summary, end = at_tups.pop(0)
        itemtype, summary, end = at_tups[0]
        act_key = act_val = ''
        if itemtype in type_keys:
            for tup in at_tups:
                if tup[-1] < cursor_pos:
                    act_key = tup[0]
                    act_val = tup[1]
                else:
                    break

            if at_entry:
                reply_str =  "{} @-keys\n".format(type_keys[itemtype])
                current_required = ["@{}".format(x) for x in required[itemtype] if x not in hsh]
                if current_required:
                    reply_str += "  required: {}\n".format(", ".join(current_required))
                current_allowed = ["@{}".format(x) for x in allowed[itemtype] if x not in hsh or x in 'jr']
                if current_allowed:
                    reply_str += "  allowed: {}\n".format(", ".join(current_allowed))
                reply = ('say', reply_str)
            elif act_key:

                if act_key == itemtype:
                    ask = ('say', "{} summary:\n".format(type_keys[itemtype]))
                    reply = ('say', 'Enter the summary for the {}'.format(type_keys[itemtype]))

                elif act_key in allowed[itemtype]:
                    if act_key in deal_with:
                        top, bot, item_hsh = deal_with[act_key](hsh, item_hsh)
                        ask = ('say', top)
                        reply = ('say', bot)

                    elif act_val:
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
    reply = ('say', reply[1] + "\nat_entry: {}\n".format(at_entry) + ", ".join(["'{}'".format(x) for x in at_parts]))

    if complete:
        return hsh, item_hsh
    else:
        return ask, reply


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
            if part:
                at_entry = False
                if len(part) > 1:
                    at_key = part[0]
                    at_val = part[1:].strip()
                    if at_key in amp_keys:
                        amp_parts = amp_regex.split(at_val)
                        for amp_part in amp_parts:
                            if amp_part:
                                amp_entry = False
                                if len(amp_part) > 1:
                                    amp_key = amp_part[0]
                                    amp_val = amp_part[1:].strip()
                                else:
                                    pass

                            else:
                                # & entered without key
                                amp_entry = True


                    at_hsh[at_key] = at_val

                else:
                    at_hsh[part[0]] = ''
            else:
                # @ entered but without key
                at_entry = True
                break
                # continue
            at_tups.append( (part[0], at_hsh[part[0]], tmp) )
            tmp += 2 + len(part)

    if at_tups:
        itemtype, summary, end = at_tups.pop(0)
        act_key = itemtype
        act_val = summary
        at_hsh['type'] = itemtype
        at_hsh['summary'] = summary
        for tup in at_tups:
            if tup[-1] < pos:
                act_key = tup[0]
                act_val = tup[1]
            else:
                break
        if itemtype in type_keys:

            if at_entry:
                reply_str =  "{} @-keys\n".format(type_keys[itemtype])
                current_required = ["@{}".format(x) for x in required[itemtype] if x not in at_hsh]
                if current_required:
                    reply_str += "  required: {}\n".format(", ".join(current_required))
                current_allowed = ["@{}".format(x) for x in allowed[itemtype] if x not in at_hsh or x in 'jr']
                if current_allowed:
                    reply_str += "  allowed: {}\n".format(", ".join(current_allowed))
                reply = ('say', reply_str)

            elif act_key == itemtype:
                ask = ('say', "{} summary:\n".format(type_keys[itemtype]))
                reply = ('say', 'Enter the summary for the {}'.format(type_keys[itemtype]))

            elif act_key in allowed[itemtype]:
                if act_key in deal_with:
                    top, bot = deal_with[act_key](at_hsh)
                    ask = ('say', top)
                    reply = ('say', bot)

                elif act_val:
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
    # reply = ('say', ", ".join(["'{}'".format(x) for x in at_parts]))
    reply = ('say', reply[1] + "\nat_entry: {}\n".format(at_entry) + ", ".join(["'{}'".format(x) for x in at_parts]))
    return ask, reply

if __name__ == '__main__':
    print('\n\n')
    import doctest
    from pprint import pprint
    doctest.testmod()

