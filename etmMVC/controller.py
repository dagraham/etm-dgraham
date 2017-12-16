 #! /usr/bin/env python3

import pendulum
pendulum.set_formatter('alternative')

# from dateutil.tz import gettz, tzutc, tzlocal

# from model import ONEWEEK, ONEDAY, ONEHOUR, ONEMINUTE 
from model import parse_datetime, parse_period, rrule, format_datetime, set_summary
from dateutil.rrule import rrulestr

testing = True
# testing = False

import re
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
    'r': "repetition frequency y)early, m)onthly, w)eekly, d)aily, h)ourly, min)utely",
    's': "starting date or datetime",
    't': "tags (list of strings)",
    'v': "value (defaults key)",
}

amp_keys = {
    'r': {
        'c': "count: integer number of repetitions",
        'E': "easter: number of days before (-), on (0) or after (+) Easter",
        'h': "hour: list of integers in 0 ... 23",
        'i': "interval: positive integer",
        'm': "monthday: list of integers 1 ... 31",
        'M': "month: list of integers in 1 ... 12",
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
undated_methods = 'cdegilmstv'
date_methods = 'br'
datetime_methods = date_methods + 'ea+-' 
task_methods = 'fjp'

# events
required['*'] = 's'
allowed['*'] = undated_methods + datetime_methods


# tasks
required['-'] = ''
allowed['-'] = undated_methods + datetime_methods + task_methods

# journal entries
required['#'] = ''
allowed['#'] = undated_methods + datetime_methods

# someday entries
required['?'] = ''
allowed['?'] = undated_methods + task_methods + datetime_methods

# inbox entries
required['!'] = ''
allowed['!'] = undated_methods + task_methods

# item type t and has s 
# allowed['date'] = allowed[t] + 'br'
# allowed['datetime'] = allowed[t] + 'abr'
# allowed['r'] = '+-'

requires = {
        'a': 's', 
        'b': 's',
        'r': 's',
        '+': 'r',
        '-': 'r',
        }

def check_requires(key, hsh):
    """
    Check that hsh has the prerequisite entries for key.
    """
    if key in requires and requires[key] not in hsh:
        return False, ('warn', "@{0} is required for @{1}\n".format(requires[key], key))
    else:
        return True, ('say', '')


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
    Check the currents state of at_hsh regarding the 's' key

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
        bot = "starting: {}".format(obj.format("ddd MMM D YYYY"))
        bot += '\nWithout a time, this schedules an all-day, floating item for the specified date in whatever happens to be the local timezone.'
    elif ok == 'naive':
        bot = "starting: {}".format(obj.in_tz('Factory').format("ddd MMM D YYYY h:mmA"))
        bot += "\nThe datetime entry for @s will be interpreted as a naive datetime in whatever happens to be the local timezone."
    elif ok == 'aware':
        # bot = "starting: {}".format(obj.format("ddd MMM D h:mmA z"))
        bot = "starting: {}".format(obj.in_tz('local').format("ddd MMM D YYYY h:mmA z"))
        bot += "\nThe datetime entry for @s will be interpreted as an aware datetime in the specified timezone."
    else:
        bot = "starting: {}".format(obj.in_tz('local').format("ddd MMM D YYYY h:mmA z"))
        bot += "\nThe datetime entry for @s will be interpreted as an aware datetime in the current local timezone. Append a comma and then 'float' to make the datetime floating (naive) or a specific timezone, e.g., 'US/Pacific', to use that timezone."

    # if 'summary' in item_hsh:
    #     summary = set_summary(item_hsh['summary'], obj)
    #     bot += "\n{}".format(summary)
    #     item_hsh['summary'] = summary

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
    bot = "extent: {0}".format(item_hsh['e'].in_words())
    # bot += "\n\n{}".format(str(at_hsh))
    return top, bot, obj

deal_with['e'] = deal_with_e

def deal_with_i(at_hsh={}):
    """
    Replaces the old filepath and to provide a heirarchial organization
    view of the data. Entered as a colon delineated string, stored as a
    list. 
    >>> deal_with_i({'i': "a:b:c"})
    (True, ['a', 'b', 'c'])
    >>> deal_with_i({'i': "plant:tree:oak"})
    (True, ['plant', 'tree', 'oak'])
    """
    s = at_hsh.get('i', None)
    top = "{}?\n".format(at_keys['i'])
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

    item_hsh['i'] = res
    bot = "index: " + ", ".join(['level {0} -> {1}'.format(i, res[i]) for i in range(len(res))])
    return top, bot, res

deal_with['i'] = deal_with_i


def get_reps(n=3):
    """
    Return the first n instances of the repetition rule.
    """
    if 's' not in item_hsh or 'rrulestr' not in item_hsh:
        return False, "Both @s and @r are required for repetitions"
    rrs = rrulestr(item_hsh['rrulestr'], dtstart=item_hsh['s'])
    out = rrs.xafter(item_hsh['s'], n)
    dtstart = format_datetime(item_hsh['s'])[1]
    lst = [format_datetime(x)[1] for x in out]
    outstr = "\n    ".join(lst[:n]) 
    res = """\
The first {} repetitions on or after {}:
    {}""".format(n, dtstart,  outstr)
    return True, res 


def deal_with_r(at_hsh={}):
    """
    Check the current state of at_hsh regarding r and s.
    """
    top = "repetition rule?\n"
    bot = "{}".format(at_keys['r'])
    lofh = at_hsh.get('r', [])
    if not lofh:
        return top, bot, None

    ok, res = rrule(lofh)
    if not ok:
        return top, res, None

    rrulelst = []

    # dtut_format = "YYYYMMDD[T]HHmm[00]"
    dtut_format = ";[TZID=]zz:YYYYMMDD[T]HHmm[00]"
    if 's' in item_hsh:
        if type(item_hsh['s']) == pendulum.pendulum.Date:
            # dtut_format = "YYYYMMDD[T][000000]"
            dtut_format = ";[TZID=]zz:YYYYMMDD[T][000000]"
    else:
        bot = "An entry for @s is required for repetition."
        return top, bot, None
    for hsh in res:
        r = hsh.get('r', None)
        if r:
            keys = ['&{}'.format(x) for x in amp_keys['r'] if x not in hsh]
            for key in hsh:
                if hsh[key] and key in amp_keys['r']: 
                    bot = "{}".format(amp_keys['r'][key])
                else:
                    bot = 'Allowed: {}'.format(", ".join(keys))
        else:
            # shouldn't happen
            pass
        rrulelst.append(hsh['rrulestr'])

    if '+' in item_hsh:
        for rdate in item_hsh['+']:
            rrulelst.append("RDATE:{}".format(rdate.format(dtut_format, formatter='alternative')))

    if '-' in item_hsh:
        for exdate in item_hsh['-']:
            rrulelst.append("EXDATE:{}".format(exdate.format(dtut_format, formatter='alternative')))

    res = item_hsh['rrulestr'] = "\n".join(rrulelst)
    bot = "repetition rule:\n    {}\n".format(res)
    ok, res = get_reps()
    bot += res

    return top, bot, res


deal_with['r'] = deal_with_r

def deal_with_j(at_hsh={}):
    """
    Check the current state of at_hsh regarding j and s.
    """
    if 's' in item_hsh:
        # Either a dated task or a naive or aware datetimed task 
        methods = dated_job_methods
    else:
        # An undated task
        methods = undated_job_methods
    lofh = at_hsh.get('j', [])

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
        if ret_lc:
            return False, "; ".join(msg), None
        else:
            return False, "; ".join(msg)
    else:
        # return the list of job hashes
        if ret_lc:
            return True, [id2hsh[i] for i in ids], last_completion
        else:
            return True, [id2hsh[i] for i in ids]




def str2hsh(s):
    """
    Split s on @ and & keys and return the relevant hash along with at_tups (positions of @keys in s) and at_entry (an 2 key has been entered without the corresponding key, True or False) for use by check_entry. 
    """
    hsh = {}

    if not s:
        return hsh, [], False, [], [], False, []

    at_parts = [x.strip() for x in at_regex.split(s)]
    at_tups = []
    at_entry = False
    amp_entry = False
    amp_tups = []
    amp_parts = []
    delta = 1
    if at_parts:
        place = -1
        tmp = at_parts.pop(0)
        hsh['itemtype'] = tmp[0]
        hsh['summary'] = tmp[1:].strip()
        at_tups.append( (hsh['itemtype'], hsh['summary'], place) )
        place += delta + len(tmp)

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
            place += delta + len(part)

    for key in ['r', 'j']:
        if key not in hsh: continue
        lst = []
        amp_tups = []
        amp_entry = False
        for part in hsh[key]:  # an individual @r or @j entry
            amp_hsh = {}
            amp_parts = [x.strip() for x in amp_regex.split(part)]
            if amp_parts:
                amp_hsh[key] = "".join(amp_parts.pop(0))
                # k = amp_part
                for part in amp_parts:  # the & keys and values for the given entry
                    if part:
                        amp_entry = False
                    else:
                        amp_entry = True
                        break
                    # if len(part) < 2:
                    #     continue
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
                    amp_tups.append( (k, v, place) )
                    # place += 2 + len(part)
                lst.append(amp_hsh)
        hsh[key] = lst

    return hsh, at_tups, at_entry, at_parts, amp_tups, amp_entry, amp_parts


def check_entry(s, cursor_pos):
    """
    Process 's' as the current entry with the cursor at cursor_pos and return the relevant ask and reply prompts.
    """
    hsh, at_tups, at_entry, at_parts, amp_tups, amp_entry, amp_parts = str2hsh(s)

    ask = ('say', '')
    reply = ('say', '\n')
    if not at_tups:
        ask = ('say', type_prompt)
        reply = ('say', item_types)
        return ask, reply 

    # itemtype, summary, end = at_tups.pop(0)
    itemtype, summary, end = at_tups[0]
    act_key = act_val = amp_key = ''

    if itemtype in type_keys:
        for tup in at_tups:
            if tup[-1] < cursor_pos:
                act_key = tup[0]
                act_val = tup[1]
            else:
                break

        if at_entry:
            ask =  ('say', "{} @keys:\n".format(type_keys[itemtype]))
            current_required = ["@{} {}".format(x, at_keys[x]) for x in required[itemtype] if x not in hsh]
            reply_str = ""
            if current_required:
                reply_str += "Required: {}\n".format(", ".join(current_required))
            current_allowed = ["@{} {}".format(x, at_keys[x]) for x in allowed[itemtype] if x not in hsh or x in 'ajr']
            if current_allowed:
                reply_str += "Allowed: {}\n".format(", ".join(current_allowed))
            reply = ('say', reply_str)
        elif act_key:
            if act_key in at_keys:
                ask = ('say', "{0}?\n".format(at_keys[act_key]))

            else:
                ask =  ('say', "{} @keys:\n".format(type_keys[itemtype]))

            if act_key == itemtype:
                ask = ('say', "{} summary:\n".format(type_keys[itemtype]))
                reply = ('say', 'Enter the summary for the {} followed, optionally, by @key and value pairs\n'.format(type_keys[itemtype]))

            else:
                ok, res = check_requires(act_key, hsh)
                if not ok:
                    ask = ('say', '{0}\n'.format(at_keys[act_key]))
                    reply = res


                elif act_key in allowed[itemtype]:

                    if amp_entry:
                        ask = ('say', "&key for @{}?\n".format(act_key))
                        reply =  ('say', "Allowed: {}\n".format(", ".join(["&{} {}".format(key, amp_keys[act_key][key]) for key in amp_keys[act_key]])))
                    elif act_key in deal_with:
                        top, bot, obj = deal_with[act_key](hsh)
                        ask = ('say', top)
                        reply = ('say', "{}\n".format(bot))
                    else:
                        ask = ('say', "{0}?\n".format(at_keys[act_key]))
                else:
                    reply = ('warn', "@{0} is not allowed for item type '{1}'\n".format(act_key, itemtype))
        else:
            reply = ('warn', 'no act_key')

    else:
        ask = ('say', type_prompt)
        reply = ('warn', u"invalid item type character: '{0}'\n".format(itemtype))

    if 'summary' in hsh:
        item_hsh['summary'] = hsh['summary']

    # for testing and debugging:1
    if testing:
        reply = (reply[0], reply[1] + "\nat_entry {0} {1}: {2}; pos {3}\namp_entry: {4}: {5}\n{6}\n{7}\n{8}\n{9}".format(at_entry, act_key, act_val, cursor_pos,  amp_entry, amp_key, at_tups, at_parts, hsh, item_hsh))

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

