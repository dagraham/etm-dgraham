import re, shutil
from dateutil import rrule
from dateutil.rrule import rruleset, rrulestr
from datetime import datetime, timedelta
from dateutil.tz import gettz
import pytz

from typing import Union, Tuple, Optional
from typing import List, Dict, Any, Callable, Mapping
from common import wrap

type_keys = {
    '*': 'event',
    '-': 'task',
    '✓': 'finished',
    '%': 'journal',
    '~': 'goal',
    '!': 'inbox',
}
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

multiple_allowed = [
    'a', 'u', 't', 'k', 'K', 'jj', 'ji', 'js', 'jb', 'jp', 'ja', 'jd', 'je', 'jf', 'jl', 'jm', 'ju'
    ]

wrap_methods = ['w']

required = {'*': ['s'], '-': [], '%': [], '~': ['s']}

allowed = {
    '*': common_methods + datetime_methods + repeating_methods + wrap_methods,
    '-': common_methods + datetime_methods + task_methods + repeating_methods,
    '%': common_methods + ['+'],
    '~': common_methods + ['q', 'h'],
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

class Repeat:
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
        i='INTERVAL', c='COUNT', s='BYSETPOS', u='UNTIL', M='BYMONTH', m='BYMONTHDAY', W='bYWEEKNO', w='BYDAY', h='BYHOUR', n='BYMINUTE', E='BYEASTER'
        )
    param_to_entry = dict(
        INTERVAL='i', COUNT='c', BYSETPOS='s', UNTIL='u', BYMONTH='M', BYMONTHDAY='m', BYWEEKNO='W', BYDAY='w', BYHOUR='h', BYMINUTE='n', BYEASTER='E'
    )
    def split_int_str(s):
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
        This will be initialized by Item and, if the instance of Item has an 'r' attribute

        Thinking: if Item is initialized with an entry_string that has an 'r' token, then we need to convert that string into a rulestr

        Args:
            obj (Any, optional): _description_. Defaults to None.
        """
        self.ruleset = rruleset(cache=True)
        self.rulestr = ''
        self.startdt = None
        print(f"obj = {obj}")
        if isinstance(obj, rrule.rruleset):
            print('ruleset object',  obj)
            self.ruleset = obj
        if isinstance(obj, dict) and 'r' in obj:
            print('dict object', obj)
            self.ruleset = self._from_dict(obj)
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
        self.startdt = Repeat.dt_to_naive(dt)

    def add_dates(self, dates: List[datetime]) -> None:
        for dt in dates:
            self.ruleset.rdate(Repeat.dt_to_naive(dt))

    def rem_dates(self, dates: List[datetime]) -> None:
        for dt in dates:
            self.ruleset.exdate(Repeat.dt_to_naive(dt))

    def add_rule(self, dtstart: datetime = None, rule: Union[dict, str] = None) -> None:
        if isinstance(rule, dict):
            if 'r' not in rule:
                raise ValueError("Missing 'r' in rule")
            if rule['r'] not in Repeat.frequency:
                raise ValueError(f"{rule['r']} is not a valid frequency")

            rulelst = [f"{DTSTART}=self.startdt.strftime(Repeat.dt_format)"] if self.startdt else []
            rulelst.append(f"FREQ={Repeat.frequency[rule['r']]}")
            for k, v in Repeat.entry_to_param.items():
                if k in rule:
                    if k == 'w':
                        _, bad = Repeat.wkdays_to_rrule(rule[k])
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
    def __init__(self, obj: Union[dict, str] = None):
        print(f"obj = {obj}")
        self.created = self._get_current_timestamp()
        # self.itemtype = None
        # self.summary = None
        # self.start = None
        # self.end = None
        # self.recurrence = Repeat()
        # self.rruleset = None
        if isinstance(obj, dict):
            self._init_from_dict(obj)
        elif isinstance(obj, str):
            # handle user input string
            print(f"obj = {obj}")
            self.parse_input(obj)

    def _get_current_timestamp(self):
        return datetime.now(pytz.utc).strftime("%Y%m%dT%H%MA")

    def _init_from_dict(self, obj):
        self.created = obj.get("created", self.created)
        # self.itemtype = obj.get("itemtype")
        # self.summary = obj.get("summary")
        self.entry = None
        self.tokens = None

        # if "r" in obj:
        #     self.recurrence = Repeat()
        #     startdt  = obj.get("s", "")
        #     dtstart = startdt.strftime(self.recurrence.dt_format) if startdt else None
        #     if isinstance(obj["r"], list):
        #         for rule in obj["r"]:
        #             print(f"adding rule: {rule}")
        #             self.recurrence.add_rule(rule)
        #     else:
        #         print(f"adding rule: {obj['r']}")
        #         self.recurrence.add_rule(obj["r"])
        #     # self.recurrence.rulestr = self.recurrence.to_string()
        #     print(f"{self.recurrence.rulestr = }")
        #     # self.recurrence.ruleset = rrulestr(self.recurrence.rulestr)

    def parse_input(self, obj: str):
        """
        Parses the input string to extract tokens, then processes and validate the tokens.
        """
        print(f"obj = {obj}")
        self._tokenize(obj)
        print(f"{self.tokens = }")
        self._parse_tokens()
        self._validate()

    def _tokenize(self, entry: str):
        print(f"entry = {entry}")
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
        # print(f"{tokens_with_positions =}")
        self.tokens = tokens_with_positions

    def get_token_at_cursor(self, cursor_pos):
        for token, start_pos, end_pos in self.tokens:
            if start_pos <= cursor_pos < end_pos:
                return token, start_pos, end_pos
        return None, None, None  # No token found at the cursor position

    def _parse_tokens(self):
        # self.tokens = list[tuple(token, start, end)]
        self.itemtype = self.tokens[0][0]
        summary_tokens = []
        recurrence_attributes = {}
        processing_r = False
        job_attributes = {}
        processing_j = False
        for token, start, end in self.tokens[1:]:
            if token.startswith('@'):
                break
            summary_tokens.append(token)
        self.summary = (' '.join(summary_tokens)).strip()
        for token, start, end in self.tokens[len(summary_tokens) + 1:]:
            print(f"{processing_r = }; {token = }")
            if token.startswith('&'):
                attribute, value = self._parse_attribute(token)
                print(f"{attribute = }; {value = }")
                if processing_r:
                    recurrence_attributes[attribute] = value
                    print(f"recurrence_attributes: {recurrence_attributes}")
                elif processing_j:
                    job_attributes[attribute] = value
            elif token.startswith('@'):
                if recurrence_attributes:
                    print(f"{recurrence_attributes = }")
                    self.recurrence.add_rule(recurrence_attributes)
                    recurrence_attributes = {}
                if job_attributes:
                    self.jobs.append(job_attributes)
                    job_attributes = {}
                if token.startswith('@s'):
                    processing_r = processing_j = False
                    self.start = self._parse_datetime(token[3:].strip())
                elif token.startswith('@e'):
                    self.end = self._parse_duration(token[3:].strip())
                elif token.startswith('@r'):
                    processing_r = True
                    recurrence_attributes['r'] = token[3:].strip()
                    print(f"recurrence_attributes: {recurrence_attributes}")
                elif token.startswith('@j'):
                    processing_j = True
                    job_attributes['r'] = token[3:].strip()
                    print(f"job_attributes: {job_attributes}")
        if recurrence_attributes:
            self.recurrence = Repeat(recurrence_attributes)
            print(f"{recurrence_attributes = }")
            self.recurrence.add_rule(recurrence_attributes)
            # self.recurrence.rulestr = self.recurrence.to_string()
        print(f"recurrence: {self.recurrence}")

    def _parse_datetime(self, datetime_str):
        if not datetime_str:
            return None
        try:
            return datetime.strptime(datetime_str, "%Y%m%dT%H%M%S")
        except ValueError:
            try:
                return datetime.strptime(datetime_str, "%Y/%m/%d")
            except ValueError:
                raise ValueError(f"Invalid datetime format: {datetime_str}")

    def _parse_duration(self, duration_str):
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

    def _parse_recurrence(self, recurrence_str):
        return {"r": self.recurrence.parse_input(recurrence_str)}

    def _parse_attribute(self, attribute_str):
        key, value = attribute_str[1:].split()
        if key == "M":
            value = [int(value)]
        elif key == "w":
            value = [f"{value[:1]}TH"]
        return key, value

    def _validate(self):
        if self.itemtype == '*' and not self.start:
            raise ValueError("Events must have a start datetime (@s)")
        if self.recurrence and not self.start:
            raise ValueError("Items with recurrence (@r) must have a start datetime (@s)")

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

# Example usage
json_entry = {
    "created": "{T}:20240712T1052",
    "itemtype": "*",
    "summary": "Thanksgiving",
    "s": "{T}:20101126T0500",
    "r": "RRULE:FREQ=MONTHLY;BYMONTH=11;BYDAY=+4THU",
    "modified": "{T}:20240712T1054"
}

item_from_json = Item(json_entry)
print(f"{item_from_json = }")

item_from_string = Item("* Thanksgiving @s 2010/11/26 @r y &M 11 &w 4TH")
print(f"{item_from_string = }")