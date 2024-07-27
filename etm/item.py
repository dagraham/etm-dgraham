import re, shutil
from dateutil import rrule
from dateutil.rrule import rruleset, rrulestr
from datetime import date, datetime, timedelta
from dateutil.tz import gettz
import pytz

from collections import defaultdict
from math import ceil

from typing import Union, Tuple, Optional
from typing import List, Dict, Any, Callable, Mapping
from common import wrap

type_keys = {
    '*': 'event',
    '-': 'task',
    '%': 'journal',
    '!': 'inbox',
    '~': 'goal',
    '+': 'track',
    # '✓': 'finished',  # more a property of a task than an item type
}
common_methods = list('cdgilmnstuxz')

repeating_methods = list('+-o') + [ 'rr', 'rc', 'rm', 'rE', 'rh', 'ri', 'rM', 'rn', 'rs', 'ru', 'rW', 'rw', ]

datetime_methods = list('abe')

job_methods = list('efhp') + [ 'jj', 'ja', 'jb', 'jd', 'je', 'jf', 'ji', 'jl', 'jm', 'jp', 'js', 'ju' ]

multiple_allowed = [
    'a', 'u', 't', 'jj', 'ji', 'js', 'jb', 'jp', 'ja', 'jd', 'je', 'jf', 'jl', 'jm', 'ju'
    ]

wrap_methods = ['w']

required = {'*': ['s'], '-': [], '%': [], '~': ['s'], '+': ['s']}

allowed = {
    '*': common_methods + datetime_methods + repeating_methods + wrap_methods,
    '-': common_methods + datetime_methods + job_methods + repeating_methods,
    '%': common_methods + ['+'],
    '~': common_methods + ['q', 'h'],
    '+': common_methods + ['h'],
}

# inbox
required['!'] = []
allowed['!'] = (
    common_methods + datetime_methods + job_methods + repeating_methods
)

requires = {
    'a': ['s'],
    'b': ['s'],
    '+': ['s'],
    'q': ['s'],
    '-': ['rr'],
    'rr': ['s'],
    'js': ['s'],
    'ja': ['s'],
    'jb': ['s'],
}

# NOTE: experiment for replacing jinja2
def itemhsh_to_details(item: dict[str, str])->str:
    format_dict = {
        'itemtype': "",
        'summary': " ",
        's': f"\n@s ",
        'e': f" @e ",
        'r': f"\n@r ",
    }

    formatted_string = ""
    for key in format_dict.keys():
        if key in item:
            formatted_string += f"{format_dict[key]}{item[key]}"
    return formatted_string

def ruleset_to_rulehsh(rrset: rruleset)->dict[str, str]:
    # FIXME: fixme
    raise NotImplementedError

def ruleset_to_rulestr(rrset: rruleset)->str:
    print(f"rrset: {rrset}; {type(rrset) = }; {rrset.__dict__}")
    print(f"{list(rrset) = }")
    parts = []
    # parts.append("rrules:")
    for rule in rrset._rrule:
        # parts.append(f"{textwrap.fill(str(rule))}")
        parts.append(f"{'\\n'.join(str(rule).split('\n'))}")
    # parts.append("exdates:")
    for exdate in rrset._exdate:
        parts.append(f"EXDATE:{exdate}")
    # parts.append("rdates:")
    for rdate in rrset._rdate:
        parts.append(f"RDATE:{rdate}")
    return "\n".join(parts)

class Instances:
    """_summary_
    Thinking: This will be called by/from Item instances.

    If the instance is created from the tinydb, then it will have an 'r' attribute that contains a rruleset object.

    If the instance is being created from user input, then it will have an 'r' attribute that contains an entry string that needs to be converted to a rruleset object.

    To display or edit the rruleset, a method will be needed to convert the rruleset to an entry string.

    methods needed:
        - entry_to_rruleset
        - rruleset_to_entry
        - rruleset_to_details

    rruleset methods needed:
        - after(dt, inc=False)
            Returns the first recurrence after the given datetime instance. The inc keyword defines what happens if dt is an occurrence. With inc=True, if dt itself is an occurrence, it will be returned.

        - before(dt, inc=False)
            Returns the last recurrence before the given datetime instance. The inc keyword defines what happens if dt is an occurrence. With inc=True, if dt itself is an occurrence, it will be returned.

        - between(after, before, inc=False, count=1)
            Returns all the occurrences of the rrule between after and before. The inc keyword defines what happens if after and/or before are themselves occurrences. With inc=True, they will be included in the list, if they are found in the recurrence set.

        - count()
            Returns the number of recurrences in this set. It will have go through the whole recurrence, if this hasn’t been done before.
    """
    dt_format = '%Y%m%dT%H%M%S'
    wkd_list = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']
    wkd_str = ', '.join(wkd_list)
    wkd_regex = re.compile(r'(?<![\w-])([+-][1-4])?(MO|TU|WE|TH|FR|SA|SU)(?!\w)')
    frequency = dict(
        y='YEARLY', m='MONTHLY', w='WEEKLY', d='DAILY', h='HOURLY', n='MINUTELY')
    entry_to_param = dict(
        i='INTERVAL', c='COUNT', s='BYSETPOS', u='UNTIL', M='BYMONTH', m='BYMONTHDAY', W='BYWEEKNO', w='BYDAY', h='BYHOUR', n='BYMINUTE', E='BYEASTER'
        )
    param_to_entry = dict(
        INTERVAL='i', COUNT='c', BYSETPOS='s', UNTIL='u', BYMONTH='M', BYMONTHDAY='m', BYWEEKNO='W', BYDAY='w', BYHOUR='h', BYMINUTE='n', BYEASTER='E'
    )

    @classmethod
    def split_int_str(cls, s):
        match = re.match(r'^([+-]?\d*)(.*)$', s)
        if match:
            integer_part = match.group(1)
            string_part = match.group(2)
            # Convert integer_part to an integer if it's not empty, otherwise None
            integer_part = integer_part if integer_part else None
            return integer_part, string_part
        return None, s  # Default case if no match is found

    @classmethod
    def wkdays_to_rrule(cls, wkd_str: str):
        """
        Converts a string representation of weekdays into a list of rrule objects.

        Args:
            wkd_str (str): The string representation of weekdays.

        Returns:
            Tuple[List[rrule], List[str]]: A tuple containing two lists. The first list contains the rrule objects corresponding to the valid weekdays in the input string. The second list contains the invalid weekdays in the input string.
        """
        if isinstance(wkd_str, list):
            return ','.join(wkd_str), []
        wkd_str = wkd_str.upper()
        matches = re.findall(cls.wkd_regex, wkd_str)
        _ = [f"{x[0]}{x[1]}" for x in matches]
        all = [x.strip() for x in wkd_str.split(',')]
        bad = [x for x in all if x not in _]
        problem_str = ""
        problems = []
        for x in bad:
            probs = []
            print(f"spliting {x}")
            i, w = cls.split_int_str(x)
            if i is not None:
                abs_i = abs(int(i))
                if abs_i > 4 or abs_i == 0:
                    probs.append(f"{i} must be between -4 and -1 or between +1 and +4")
                elif not (i.startswith('+') or i.startswith('-')):
                    probs.append(f"{i} must begin with '+' or '-'")
            if w not in cls.wkd_list:
                probs.append(f"{w} must be a weekday abbreviation from {cls.wkd_str}")
            if probs:
                problems.append(f"In '{x}': {', '.join(probs)}")
            else:
                # undiagnosed problem
                problems.append(f"{x} is invalid")
        if problems:
            problem_str = wrap(f"Problem entries: {', '.join(bad)}\n{'\n'.join(problems)}")
        good = []
        for x in matches:
            s = f"{x[0]}{x[1]}" if x[0] else f"{x[1]}"
            good.append(s)\
        # good_str will be '' if good is an empty list
        good_str = ','.join(good)
        return good_str, problem_str

    @classmethod
    def dt_to_naive(cls, dt: datetime)->str:
        """Convert an 'aware' datetime to localtime and then remove the timezone information to make it 'naive'.

        Args:
            dt (datetime): an aware datetime.datetime object

        Returns:
            datetime: a naive datetime.datetime object
        """
        _ = dt if (
            dt.tzinfo is None or
            dt.tzinfo.utcoffset(dt) is None
            ) else dt.astimezone().replace(tzinfo=None)
        return _.strftime(cls.dt_format)

    def __init__(self, obj: Any = None):
        """
        This will be initialized by Item when the instance of Item has been initiallized with a json dictionary from tinydb with an 'r' attribute containing an rruleset object. In that case the attribute will be an rruleset.

        Alternatively, if an instance of Item makes a call to process_entry which contains a token in [r, +, -], then obj will


        Args:
            obj (Any, optional): _description_. Defaults to None.
        """
        self.ruleset = rruleset(cache=True)
        self.rulestr = ''
        self.startdt = None
        print(f"obj = {obj}")
        if isinstance(obj, rrule.rruleset):
            print('rruleset object',  obj)
            self.ruleset = obj
        # if isinstance(obj, dict) and 'r' in obj:
        #     print(f"processing {obj = } as dict")
        #     print('dict object', obj)
        #     self.ruleset = self._from_dict(obj)
        elif isinstance(obj, str):
            print('str object:', obj)
            self.ruleset = self._from_string(obj)

    def _from_string(self, obj):
        return rrulestr(obj)

    def _from_dict(self, obj: Dict[str, Any]):
        """_summary_

        Args:
            obj (Dict[str, Any]): _description_

        Raises:
            NotImplementedError: _description_
        """
        if 'r' in obj:
            for rule in obj['r']:
                self.add_rule(rule)

    def to_string(self):
        parts = []
        for rule in self.ruleset._rrule:
            parts.append(f"{'\\n'.join(str(rule).split('\n'))}")
        for exdate in self.ruleset._exdate:
            parts.append(f"EXDATE:{exdate}")
        for rdate in self.ruleset._rdate:
            parts.append(f"RDATE:{rdate}")
        return "\n".join(parts)

    def set_startdt(self, dt: datetime) -> None:
        self.startdt = Instances.dt_to_naive(dt)

    def add_dates(self, dates: List[datetime]) -> None:
        for dt in dates:
            self.ruleset.rdate(Instances.dt_to_naive(dt))

    def rem_dates(self, dates: List[datetime]) -> None:
        for dt in dates:
            self.ruleset.exdate(Instances.dt_to_naive(dt))

    def add_rule(self, dtstart: datetime = None, rule: Union[dict, str] = None) -> None:
        if isinstance(rule, dict):
            if 'r' not in rule:
                raise ValueError("Missing 'r' in rule")
            if rule['r'] not in Instances.frequency:
                raise ValueError(f"{rule['r']} is not a valid frequency")

            rulelst = [f"DTSTART=self.startdt.strftime(Instances.dt_format)"] if self.startdt else []
            rulelst.append(f"FREQ={Instances.frequency[rule['r']]}")
            for k, v in Instances.entry_to_param.items():
                if k in rule:
                    if k == 'w':
                        _, bad = Instances.wkdays_to_rrule(rule[k])
                        rulelst.append(f"BYDAY={_}")
                        if bad:
                            raise ValueError(f"Invalid weekdays: {bad}")
                    else:
                        if isinstance(rule[k], list):
                            val = ','.join([str(x) for x in rule[k]])
                        else:
                            val = rule[k]
                        rulelst.append(f"{v}={val}")
            print("rulelst:", rulelst)
            self.rulestr = f"RRULE:{';'.join(rulelst)}"
            print("self.rulestr:", self.rulestr)
            print(f"{rrulestr(self.rulestr) = }")
            self.ruleset = rrulestr(self.rulestr)

    def parse_input(self, input_string):
        for rule in rrulestr(input_string):
            self.ruleset.rrule(rule)

# rstr ="""DTSTART:20241028T133000\nRRULE:FREQ=DAILY;COUNT=14
# DTSTART:20241028T133000\nRRULE:FREQ=DAILY;INTERVAL=2;COUNT=7
# EXDATE:2024-11-04 13:30:00
# RDATE:2024-11-04 13:45:00
# RDATE:2024-11-05 15:15:00"""

# rr = Repeat()

# print(f"{rr}\n{rr.to_string()}")

class Item:
    # class variables
    token_keys = { # TODO: provide do_... as class methods
        'itemtype': [
            'item type',
            'character from * (event), - (task), % (journal), ~ (goal), + (track) or ! (inbox)',
            'do_itemtype',
        ],
        'summary': [
            'summary',
            "brief item description. Append an '@' to add an option.",
            'do_summary',
        ],
        's': ['scheduled', 'starting date or datetime', 'do_datetime'],
        '+': [
            'include',
            'list of datetimes to include',
            'do_datetimes',
        ],
        '-': [
            'exclude',
            'list of datetimes to exclude',
            'do_datetimes',
        ],
        'a': ['alerts', 'list of alerts', 'do_alert'],
        'b': ['beginby', 'number of days for beginby notices', 'do_beginby'],
        'c': ['calendar', 'calendar', 'do_string'],
        'd': ['description', 'item details', 'do_paragraph'],
        'e': ['extent', 'timeperiod', 'do_duration'],
        'w': ['wrap', 'list of two timeperiods', 'do_two_periods'],
        'f': ['finish', 'completion done -> due', 'do_completion'],
        'g': ['goto', 'url or filepath', 'do_string'],
        'h': [
            'completions',
            'list of completion datetimes',
            'do_completions',
        ],
        'i': ['index', 'forward slash delimited string', 'do_string'],
        'k': ['konnection', 'document id', 'do_konnection'],
        'K': ['konnect', 'summary for inbox item', 'do_konnect'],
        'l': [
            'location',
            'location or context, e.g., home, office, errands',
            'do_string',
        ],
        'm': ['mask', 'string to be masked', 'do_mask'],
        'n': ['attendee', 'name <email address>', 'do_string'],
        'o': [
            'overdue',
            'character from (r)estart, (s)kip or (k)eep',
            'do_overdue',
        ],
        'p': [
            'priority',
            'priority from 0 (none) to 4 (urgent)',
            'do_priority',
        ],
        'q': ['quota', 'number of instances to be done', 'do_quota'],
        't': ['tag', 'tag', 'do_string'],
        'u': ['used time', 'timeperiod: datetime', 'do_usedtime'],
        'x': ['expansion', 'expansion key', 'do_string'],
        'z': [
            'timezone',
            "a timezone entry such as 'US/Eastern' or 'Europe/Paris' or 'float' to specify a naive/floating datetime",
            'do_timezone',
        ],
        '?': ['@-key', '', 'do_at'],
        'rr': [
            'repetition frequency',
            "character from (y)ear, (m)onth, (w)eek,  (d)ay, (h)our, mi(n)ute. Append an '&' to add a repetition option.",
            'do_frequency',
        ],
        'ri': ['interval', 'positive integer', 'do_interval'],
        'rm': [
            'monthdays',
            'list of integers 1 ... 31, possibly prepended with a minus sign to count backwards from the end of the month',
            'do_monthdays',
        ],
        'rE': [
            'easterdays',
            'number of days before (-), on (0) or after (+) Easter',
            'do_easterdays',
        ],
        'rh': ['hours', 'list of integers in 0 ... 23', 'do_hours'],
        'rM': ['months', 'list of integers in 1 ... 12', 'do_months'],
        'rn': ['minutes', 'list of integers in 0 ... 59', 'do_minutes'],
        'rw': [
            'weekdays',
            'list from SU, MO, ..., SA, possibly prepended with a positive or negative integer',
            'do_weekdays',
        ],
        'rW': [
            'week numbers',
            'list of integers in 1, ... 53',
            'do_weeknumbers',
        ],
        'rc': ['count', 'integer number of repetitions', 'do_count'],
        'ru': ['until', 'datetime', 'do_until'],
        'rs': ['set positions', 'integer', 'do_setpositions'],
        'r?': ['repetition &-key', 'enter &-key', 'do_ampr'],
        'jj': [
            'summary',
            "job summary. Append an '&' to add a job option.",
            'do_string',
        ],
        'ja': [
            'alert',
            'list of timeperiods before job is scheduled followed by a colon and a list of commands',
            'do_alert',
        ],
        'jb': ['beginby', ' integer number of days', 'do_beginby'],
        'jd': ['description', ' string', 'do_paragraph'],
        'je': ['extent', ' timeperiod', 'do_duration'],
        'jf': ['finish', ' completion done -> due', 'do_completion'],
        'ji': ['unique id', ' integer or string', 'do_string'],
        'jl': ['location', ' string', 'do_string'],
        'jm': ['mask', 'string to be masked', 'do_mask'],
        'jp': [
            'prerequisite ids',
            'list of ids of immediate prereqs',
            'do_stringlist',
        ],
        'js': [
            'scheduled',
            'timeperiod before task scheduled when job is scheduled',
            'do_duration',
        ],
        'ju': ['used time', 'timeperiod: datetime', 'do_usedtime'],
        'j?': ['job &-key', 'enter &-key', 'do_ampj'],
    }

    def __init__(self, obj: Union[dict, str] = None):
        # print(f"obj = {obj}")
        self.created = None
        self.modified = None
        self.entry = ""
        self.previous_entry = ""
        self.tokens = None
        self.previous_tokens = []
        self.instances = None
        self.details = "" # add doc_id, created, modified
        self.item = {} # however initialized, this dictionary has all the attributes

        self.start = None
        if isinstance(obj, dict):
            # dict object from tinydb
            self._init_from_dict(obj)
        elif isinstance(obj, str):
            # handle user input string
            # print(f"initializing from string: {obj}")
            self.parse_input(obj)

    def get_token_at_cursor(self, cursor_pos):
        for token, start_pos, end_pos in self.tokens:
            if start_pos <= cursor_pos < end_pos:
                return token, start_pos, end_pos
        return None, None, None  # No token found at the cursor position

    def _get_current_timestamp(self):
        return datetime.now(pytz.utc).strftime("%Y%m%dT%H%MA")

    def _init_from_dict(self, obj):
        self.created = obj.get("created", self.created)
        self.modified = obj.get("modified", None)

    def parse_input(self, entry: str):
        """
        Parses the input string to extract tokens, then processes and validate the tokens.
        """
        digits = '1234567890' * ceil(len(entry) / 10)
        self._tokenize(entry)
        print(f'entry to tokens:\n   |{digits[:len(entry)]}|\n   |{entry}|\n   {self.tokens}')
        self._parse_tokens(entry)
        self._validate()
        self.previous_entry = entry

    def _tokenize(self, entry: str):
        self.entry = entry
        pattern = r'(@\w+ [^@&]+)|(&\w+ \S+)|(^\S+)|(\S[^@&]*)'
        matches = re.finditer(pattern, self.entry)
        tokens_with_positions = []
        for match in matches:
            # Get the matched token
            token = match.group(0)
            # Get the start and end positions
            start_pos = match.start()
            end_pos = match.end()
            # Append the token and its positions as a tuple
            tokens_with_positions.append((token, start_pos, end_pos))
        self.tokens = tokens_with_positions

    def _find_changes(self, previous: str, current: str):
        print(f"{previous = }; {len(previous) = };  {current = }; {len(current) = }")
        # Find the range of changes between the previous and current strings
        start = 0
        while start < len(previous) and start < len(current) and previous[start] == current[start]:
            start += 1
        print(f"ending start = {start}; {previous[start-1] = }; {current[start-1] = }")

        end_prev = len(previous)
        end_curr = len(current)

        while end_prev > start and end_curr > start and previous[end_prev - 1] == current[end_curr - 1]:
            end_prev -= 1
            end_curr -= 1
        print(f"start = {start}, end_prev = {end_prev}, end_curr = {end_curr}")
        return start, end_curr

    def _identify_affected_tokens(self, changes):
        start, end = changes
        affected_tokens = []
        for token_info in self.tokens:
            token, start_pos, end_pos = token_info
            if start <= end_pos and end >= start_pos:
                affected_tokens.append(token_info)
        return affected_tokens

    def _token_has_changed(self, token_info):
        token, start_pos, end_pos = token_info
        for prev_token, prev_start, prev_end in self.previous_tokens:
            if token == prev_token and start_pos == prev_start and end_pos == prev_end:
                return False
        return True


    def _parse_tokens(self, entry: str):
        if not self.previous_entry:
            # If there is no previous entry, parse all tokens
            self._parse_all_tokens()
            return

        # Identify the affected tokens based on the change
        changes = self._find_changes(self.previous_entry, entry)
        affected_tokens = self._identify_affected_tokens(changes)

        # Parse only the affected tokens
        for token_info in affected_tokens:
            token, start_pos, end_pos = token_info
            if self._token_has_changed(token_info):
                if start_pos == 0:
                    self._dispatch_token(token, start_pos, end_pos, 'itemtype')
                elif start_pos == 2:
                    self._dispatch_token(token, start_pos, end_pos, 'summary')
                elif token == "@":
                    self.do_at()
                    # self._dispatch_token(token, start_pos, end_pos, 'do_at')
                elif token == "&":
                    self.do_amp()
                    # self._dispatch_token(token, start_pos, end_pos, 'do_amp')
                else:
                    token_type = token.split()[0][1:]  # Extract token type (e.g., 's' from '@s')
                    self._dispatch_token(token, start_pos, end_pos, token_type)

                # Add your token parsing logic here

    def _parse_all_tokens(self):
        for i, token_info in enumerate(self.tokens):
            token, start_pos, end_pos = token_info
            if i == 0:
                self._dispatch_token(token, start_pos, end_pos, 'itemtype')
            elif i == 1:
                self._dispatch_token(token, start_pos, end_pos, 'summary')
            elif token == "@":
                self.do_at()
                # self._dispatch_token(token, start_pos, end_pos, 'do_at')
            elif token == "&":
                self.do_amp()
                # self._dispatch_token(token, start_pos, end_pos, 'do_amp')
            else:
                token_type = token.split()[0][1:]  # Extract token type (e.g., 's' from '@s')
                self._dispatch_token(token, start_pos, end_pos, token_type)

    def _dispatch_token(self, token, start_pos, end_pos, token_type=None):
        if token_type is None:
            token_type = token.split()[0][1:] if token.startswith(('@', '&')) else token
        if token_type in self.token_keys:
            print(f"Dispatching token: {token} as {token_type}")
            method_name = self.token_keys[token_type][2]
            try:
                method = getattr(self, method_name)
                is_valid, result = method(token)
            except:
                is_valid = False
                result = None
                print(f"Unrecognized method_name: {method_name}")
            if is_valid:
                self.item[token_type] = result
            else:
                print(f"Error processing token '{token_type}': {result}")
        else:
            print(f"No handler for token: {token}")

        # return
        # # TODO: put tokens in a dictionary?
        # self.itemtype = self.tokens[0][0]
        # summary_tokens = []
        # recurrence_attributes = {}
        # processing_r = False
        # job_attributes = {}
        # processing_j = False
        # for token, start, end in self.tokens[1:]:
        #     if token.startswith('@') or token.startswith('&'):
        #         break
        #     summary_tokens.append(token)
        # self.summary = (' '.join(summary_tokens)).strip()
        # for token, start, end in self.tokens[len(summary_tokens) + 1:]:
        #     print(f"{processing_r = }; {token = }")
        #     if token.startswith('&'):
        #         attribute, value = self._parse_attribute(token)
        #         print(f"{attribute = }; {value = }")
        #         if processing_r:
        #             if attribute and value:
        #                 recurrence_attributes[attribute] = value
        #                 print(f"recurrence_attributes: {recurrence_attributes}")
        #         elif processing_j:
        #             job_attributes[attribute] = value
        #     elif token.startswith('@'):
        #         if recurrence_attributes:
        #             print(f"{recurrence_attributes = }")
        #             self.instances.add_rule(recurrence_attributes)
        #             recurrence_attributes = {}
        #         if job_attributes:
        #             self.jobs.append(job_attributes)
        #             job_attributes = {}
        #         if token.startswith('@s'):
        #             processing_r = processing_j = False
        #             self.start = self._parse_datetime(token[3:].strip())
        #         elif token.startswith('@e'):
        #             self.end = self._parse_duration(token[3:].strip())
        #         elif token.startswith('@r'):
        #             processing_r = True
        #             recurrence_attributes['r'] = token[3:].strip()
        #             print(f"{recurrence_attributes = }")
        #         elif token.startswith('@j'):
        #             processing_j = True
        #             job_attributes['r'] = token[3:].strip()
        #             print(f"job_attributes: {job_attributes}")
        # if recurrence_attributes:
        #     self.instances = Instances(recurrence_attributes)
        #     print(f"{recurrence_attributes = }")
        #     self.instances.add_rule(recurrence_attributes)
        #     # self.recurrence.rulestr = self.recurrence.to_string()
        #     print(f"{self.instances = }")

    def do_at(self):
        print(f"Show available @ tokens")

    def do_amp(self):
        print(f"Show available & tokens")

    @classmethod
    def do_itemtype(cls, token):
        # Process item type token
        print(f"Processing item type token: {token}")
        valid_itemtypes = {'*', '-', '%', '~', '+', '!'}
        itemtype = token[0]
        if itemtype in valid_itemtypes:
            return True, itemtype
        else:
            return False, f"Invalid item type: {itemtype}"

    @classmethod
    def do_summary(cls, token):
        # Process summary token
        print(f"Processing summary token: {token}")
        if len(token) > 1:
            return True, token
        else:
            return False, "Summary cannot be empty"

    @classmethod
    def do_datetime(cls, token):
        # Process datetime token
        print(f"Processing datetime token: {token}")
        # Simplified example; you might want to use dateutil.parser for more complex parsing
        try:
            datetime_str = token.split()[1]
            datetime_obj = datetime.strptime(datetime_str, '%Y/%m/%d')
            return True, datetime_obj
        except ValueError as e:
            return False, f"Invalid datetime: {datetime_str}. Error: {e}"

    @classmethod
    def _parse_duration(cls, duration_str):
        match = re.match(r'(\d+)([dwmy])', duration_str)
        if not match:
            raise ValueError(f"Invalid duration format: {duration_str}")
        value, unit = match.groups()
        if unit == 'd':
            return timedelta(days=int(value))
        elif unit == 'w':
            return timedelta(weeks=int(value))
        elif unit == 'm':
            return timedelta(days=int(value) * 30)
        elif unit == 'y':
            return timedelta(days=int(value) * 365)

    # @classmethod
    # def _parse_recurrence(cls, recurrence_str):
    #     return {"r": cls.instances.parse_input(recurrence_str)}

    # @classmethod
    # def _parse_attribute(cls, attribute_str):
    #     print(f"{attribute_str = }")
    #     if len(attribute_str) < 2:
    #         return None, None
    #     if len(attribute_str) == 2:
    #         return attribute_str[1], 0
    #     key, value = attribute_str[1:].split()
    #     if key == "M":
    #         value = [int(value)]
    #     elif key == "w":
    #         value = [f"{value[:1]}TH"]
    #     return key, value

    @classmethod
    def _validate(self):
        # TODO
        return
        # if self.itemtype == '*' and not self.start:
        #     raise ValueError("Events must have a start datetime (@s)")
        # if self.instances and not self.start:
        #     raise ValueError("Items with recurrence (@r) must have a start datetime (@s)")

    # def to_dict(self):
    #     data = {
    #         "created": self.created,
    #         "itemtype": self.itemtype,
    #         "summary": self.summary,
    #     }
    #     # if self.startdt:
    #     #     data["s"] = "{T}:" + self.start.strftime("%Y%m%dT%H%M%S")
    #     # if self.end:
    #     #     data["e"] = "{T}:" + (self.start + self.end).strftime("%Y%m%dT%H%M%S")
    #     if self.recurrence:
    #         data["r"] = self.recurrence
    #     return data

    # def __repr__(self):
    #     return str(self.to_dict())

class ItemManager:
    def __init__(self):
        self.doc_view_data = {}  # Primary structure: dict[doc_id, dict[view, list[row]]]
        self.view_doc_data = defaultdict(lambda: defaultdict(list))  # Secondary index: dict[view, dict[doc_id, list[row]])
        self.view_cache = {}  # Cache for views
        self.doc_view_contribution = defaultdict(set)  # Tracks views each doc_id contributes to

    def add_or_update_reminder(self, item):
        doc_id = item.doc_id
        new_views_and_rows = item.get_views_and_rows()

        # Invalidate cache for views that will be affected by this doc_id
        self.invalidate_cache_for_doc(doc_id)

        # Update the primary structure
        self.doc_view_data[doc_id] = new_views_and_rows

        # Update the secondary index
        for view, rows in new_views_and_rows.items():
            self.view_doc_data[view][doc_id] = rows
            self.doc_view_contribution[doc_id].add(view)

    def get_view_data(self, view):
        # Check if the view is in the cache
        if view in self.view_cache:
            return self.view_cache[view]

        # Retrieve data for a specific view
        view_data = dict(self.view_doc_data[view])

        # Cache the view data
        self.view_cache[view] = view_data
        return view_data

    def get_reminder_data(self, doc_id):
        # Retrieve data for a specific reminder
        return self.doc_view_data.get(doc_id, {})

    def remove_reminder(self, doc_id):
        # Invalidate cache for views that will be affected by this doc_id
        self.invalidate_cache_for_doc(doc_id)

        # Remove reminder from primary structure
        if doc_id in self.doc_view_data:
            views_and_rows = self.doc_view_data.pop(doc_id)
            # Remove from secondary index
            for view in views_and_rows:
                if doc_id in self.view_doc_data[view]:
                    del self.view_doc_data[view][doc_id]

            # Remove doc_id from contribution tracking
            if doc_id in self.doc_view_contribution:
                del self.doc_view_contribution[doc_id]

    def invalidate_cache_for_doc(self, doc_id):
        # Invalidate cache entries for views affected by this doc_id
        if doc_id in self.doc_view_contribution:
            for view in self.doc_view_contribution[doc_id]:
                if view in self.view_cache:
                    del self.view_cache[view]
