 #! /usr/bin/env python3

import pendulum
pendulum.set_formatter('alternative')

# from dateutil.tz import gettz, tzutc, tzlocal

# from model import ONEWEEK, ONEDAY, ONEHOUR, ONEMINUTE 
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
comma_regex = re.compile(r',\s*')
colon_regex = re.compile(r'\:\s*')
semicolon_regex = re.compile(r'\;\s*')

item_hsh = {} # preserve state

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
required['*'] = 's'
allowed['*'] = undated_methods


# tasks
required['-'] = ''
allowed['-'] = undated_methods + task_methods

# journal entries
required['#'] = ''
allowed['#'] = undated_methods

# someday entries
required['?'] = ''
allowed['?'] = undated_methods + task_methods

# inbox entries
required['!'] = ''
allowed['!'] = undated_methods + task_methods

# item type t and has s 
# allowed['date'] = allowed[t] + 'br'
# allowed['datetime'] = allowed[t] + 'abr'
# allowed['r'] = '+-'


type_prompt = u"type character for new item:\n"
item_types = u"item type characters:\n  *: event\n  -: task\n  #: journal entry\n  ?: someday entry\n  !: nbox entry"


def deal_with_at(at_hsh={}):
    """
    When an '@' has been entered but not yet with its key, show required and available keys with descriptions. Note, for example, that until a valid entry for @s has been given, @a, @b and @z are not available.
    """
    pass

deal_with = {}

def deal_with_s(at_hsh = {}):
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
    if ok == 'date':
        # 'dateonly'
        bot = "starting: {}".format(obj.format("ddd MMM D"))
        bot += '\nWithout a time, this schedules an all-day, floating item for the specified date in whatever happens to be the local timezone.'
    elif ok == 'naive':
        bot = "starting: {}".format(obj.format("ddd MMM D h:mmA"))
        bot += "\nThe datetime entry for @s will be interpreted as a naive datetime in whatever happens to be the local timezone."
    elif ok == 'aware':
        bot = "starting: {}".format(obj.format("ddd MMM D h:mmA z"))
        bot += "\nThe datetime entry for @s will be interpreted as an aware datetime in the specified timezone."
    else:
        bot = "starting: {}".format(obj.format("ddd MMM D h:mmA z"))
        bot += "\nThe datetime entry for @s will be interpreted as an aware datetime in the current local timezone. Append a comma and then 'float' to make the datetime floating (naive) or a specific timezone, e.g., 'US/Pacific', to use that timezone instead of the local one."

    return top, bot, obj

deal_with['s'] = deal_with_s

def deal_with_e(at_hsh={}):
    """
    Check the current state of at_hsh regarding the 'e' key.
    """
    s = at_hsh.get('e', None)
    top = "{}?\n".format(at_keys['e'])
    bot = ''
    if s is None:
        return top, bot, item_hsh
    ok, obj = parse_period(s)
    if not ok:
        return top, "considering: '{}'".format(s), None
    item_hsh['e'] = obj
    bot = "extending from {0} until {1}".format(item_hsh['s'].format("ddd MMM D h:mmA"), (item_hsh['s'] + item_hsh['e']).format("ddd MMM D h:mmA"))
    # bot += "\n\n{}".format(str(at_hsh))
    return top, bot, obj

deal_with['e'] = deal_with_e


def str2hsh(s):
    """
    Split s on @ and & keys and return the relevant hash along with at_tups (positions of @keys in s) and at_entry (an 2 key has been entered without the corresponding key, True or False) for use by check_entry. 
    """
    hsh = {}

    if not s:
        return hsh, [], False, []

    at_parts = [x.strip() for x in at_regex.split(s)]
    at_tups = []
    at_entry = False
    if at_parts:
        place = -1
        tmp = at_parts.pop(0)
        hsh['itemtype'] = tmp[0]
        hsh['summary'] = tmp[1:].strip()
        at_tups.append( (hsh['itemtype'], hsh['summary'], place) )
        place += 2 + len(tmp)

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

    return hsh, at_tups, at_entry, at_parts


def check_entry(s, cursor_pos):
    """
    Process 's' as the current entry with the cursor at cursor_pos and return the relevant ask and reply prompts.
    """
    hsh, at_tups, at_entry, at_parts = str2hsh(s)

    ask = ('say', '')
    reply = ('say', '')
    if not at_tups:
        ask = ('say', type_prompt)
        reply = ('say', item_types)
        return ask, reply 

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
            ask =  ('say', "{} @keys:\n".format(type_keys[itemtype]))
            current_required = ["@{}".format(x) for x in required[itemtype] if x not in hsh]
            reply_str = ""
            if current_required:
                reply_str += "Required: {}\n".format(", ".join(current_required))
            current_allowed = ["@{}".format(x) for x in allowed[itemtype] if x not in hsh or x in 'jr']
            if current_allowed:
                reply_str += "Allowed: {}\n".format(", ".join(current_allowed))
            reply = ('say', reply_str)
        elif act_key:
            if act_key in at_keys:
                ask = ('say', "{0}: {1}\n".format(at_keys[act_key], act_val))

            else:
                ask =  ('say', "{} @keys:\n".format(type_keys[itemtype]))

            if act_key == itemtype:
                ask = ('say', "{} summary:\n".format(type_keys[itemtype]))
                reply = ('say', 'Enter the summary for the {} followed, optionally, by @key and value pairs\n'.format(type_keys[itemtype]))

            elif act_key in allowed[itemtype]:
                if act_key in deal_with:
                    top, bot, obj = deal_with[act_key](hsh)
                    ask = ('say', top)
                    reply = ('say', bot + '\n')

                elif act_val:
                    ask = ('say', "{0}: {1}\n".format(at_keys[act_key], act_val))
                else:
                    ask = ('say', "{0}:\n".format(at_keys[act_key]))
            else:
                reply = ('warn', "'@{0}' is not allowed\n".format(act_key))
        else:
            reply = ('warn', 'no act_key')

    else:
        ask = ('say', type_prompt)
        reply = ('warn', u"invalid item type character: '{0}'\n".format(itemtype))

    # for testing and debugging:1
    reply = (reply[0], reply[1] + "\nat_entry {0} {1}: {2}; pos {3}\n{4}\n{5}".format(at_entry, act_key, act_val, cursor_pos, at_tups, at_parts))

    return ask, reply


class Item:
    """

    """
    def __init__(self, s=''):
        self.cur_pos = 0
        self.act_key = ''
        self.act_val = ''
        self.entry_
        self.ask = ''
        self.reply = ''
        self.msg = []
        self.temp_hsh = {}
        self.item_hsh = {}




if __name__ == '__main__':
    print('\n\n')
    import doctest
    from pprint import pprint
    doctest.testmod()

