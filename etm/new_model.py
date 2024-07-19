import re
from dateutil import rrule
from dateutil.rrule import rruleset, rrulestr
from datetime import datetime, timedelta
from dateutil.tz import gettz
import pytz

from typing import Union, Tuple, Optional
from typing import List, Dict, Any, Callable, Mapping

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

    If the instance is created from the tinydb, then it will have an 'r' attribute that contains the rulestring.

    If the instance is being created from user input, then

    Raises:
        NotImplementedError: _description_
        ValueError: _description_
        ValueError: _description_
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    dt_format = '%Y%m%dT%H%M%S'

    # wkd_regex = re.compile(r'(?<![\w-])(-?[1-4]?)(MO|TU|WE|TH|FR|SA|SU)(?!\w)')
    wkd_regex = re.compile(r'(?<![\w-])([+-][1-4])?(MO|TU|WE|TH|FR|SA|SU)(?!\w)')

    # frequency = dict(
    #     y=rrule.YEARLY, m=rrule.MONTHLY, w=rrule.WEEKLY, d=rrule.DAILY, h=rrule.HOURLY, n=rrule.MINUTELY
    #     )

    frequency = dict(
        y='YEARLY', m='MONTHLY', w='WEEKLY', d='DAILY', h='HOURLY', n='MINUTELY')

    # parameters = dict(
    #     i='interval', c='count', s='bysetpos', u='until', M='bymonth', m='bymonthday', W='byweekno', w='byweekday', h='byhour', n='byminute', E='byeaster'
    #     )

    entry_to_param = dict(
        i='INTERVAL', c='COUNT', s='BYSETPOS', u='UNTIL', M='BYMONTH', m='BYMONTHDAY', W='bYWEEKNO', w='BYDAY', h='BYHOUR', n='BYMINUTE', E='BYEASTER'
        )

    param_to_entry = dict(
        INTERVAL='i', COUNT='c', BYSETPOS='s', UNTIL='u', BYMONTH='M', BYMONTHDAY='m', BYWEEKNO='W', BYDAY='w', BYHOUR='h', BYMINUTE='n', BYEASTER='E'
    )
    @classmethod
    def signed_integer(cls, x: str)->str:
        """
        Returns a string representation of the 'integer' argument `x`.

        Parameters:
            x (str): A string representation of an integer such as '-2' or '3'.

        Returns:
            str: The 'signed' string representation of `x`.
            If `x` cannot be converted to an integer, None is returned.
            Else if `int(x)` is negative, then `x` is returned as is.
            Else `x` is returned prefixed with a '+' sign, e.g., '3' is returned as '+3'.

            The processing of 'byweekday' in dateutil.rrule requires, e.g., `rrule.MO(+3)` for the 3rd Monday in the month.
        """
        try:
            y = int(x)
        except ValueError:
            return None
        else:
            return f"+{y}" if y > 0 else str(y)

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
        good = []
        # print("matches", matches)
        for x in matches:
            # arg = f"+{x[0]}" if x[0] and not x[0].startswith('-') else x[0]
            arg = cls.signed_integer(x[0])
            # s = f"rrule.{x[1]}({arg})" if arg else f"rrule.{x[1]}"
            s = f"{x[0]}{x[1]}" if arg else f"{x[1]}"
            # print(f"{x = }, {arg = }, {s = }")
            # good.append(eval(s))
            good.append(s)
        return ','.join(good), bad

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
        # parts.append("rrules:")
        for rule in self.ruleset._rrule:
            # parts.append(f"{textwrap.fill(str(rule))}")
            parts.append(f"{'\\n'.join(str(rule).split('\n'))}")
        # parts.append("exdates:")
        for exdate in self.ruleset._exdate:
            parts.append(f"EXDATE:{exdate}")
        # parts.append("rdates:")
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

    def add_rule(self, rule: Union[dict, str]) -> None:
        if isinstance(rule, dict):
            if 'r' not in rule:
                raise ValueError("Missing 'r' in rule")
            if rule['r'] not in Repeat.frequency:
                raise ValueError(f"{rule['r']} is not a valid frequency")

            rulelst = []
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
            # dtstart = self.startdt if self.startdt else datetime.now().astimezone().replace(tzinfo=None)
            # lst.append(dtstart = {dtstart})
            # lst.append("cache=True")
            # print(lst, dtstart)
            # thisrule = rrule.rrule(**hsh)
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
        self.created = self._get_current_timestamp()
        self.itemtype = None
        self.summary = None
        self.start = None
        self.end = None
        self.recurrence = Repeat()
        self.rruleset = None
        if isinstance(obj, dict):
            self._init_from_dict(obj)
        elif isinstance(obj, str):
            # handle user input string
            self.parse_input(obj)

    def _get_current_timestamp(self):
        return datetime.now(pytz.utc).strftime("%Y%m%dT%H%MA")

    def _init_from_dict(self, obj):
        self.created = obj.get("created", self.created)
        self.itemtype = obj.get("itemtype")
        self.summary = obj.get("summary")
        self.start = self._parse_datetime(obj.get("s", "").replace("{T}:", ""))
        self.end = self._parse_datetime(obj.get("e", "").replace("{T}:", ""))
        if "r" in obj:
            self.recurrence = Repeat()
            if isinstance(obj["r"], list):
                for rule in obj["r"]:
                    print(f"adding rule: {rule}")
                    self.recurrence.add_rule(rule)
            else:
                print(f"adding rule: {obj['r']}")
                self.recurrence.add_rule(obj["r"])
            # self.recurrence.rulestr = self.recurrence.to_string()
            print(f"{self.recurrence.rulestr = }")
            # self.recurrence.ruleset = rrulestr(self.recurrence.rulestr)

    def parse_input(self, obj: str):
        """
        Parses the input string to extract tokens, then processes and validate the tokens.
        """
        tokens = self._tokenize(obj)
        print(f"{tokens = }")
        self._parse_tokens(tokens)
        self._validate()

    def _tokenize(self, obj):
        pattern = r'(@\w+ [^@&]+)|(&\w+ \S+)|(^\S+)|(\S[^@&]*)'
        matches = re.findall(pattern, obj)
        return [match[0] or match[1] or match[2] or match[3] for match in matches if match[0] or match[1] or match[2] or match[3]]

    def _parse_tokens(self, tokens):
        self.itemtype = tokens[0][0]
        summary_tokens = []
        recurrence_attributes = {}
        processing_r = False
        job_attributes = {}
        processing_j = False
        for token in tokens[1:]:
            if token.startswith('@'):
                break
            summary_tokens.append(token)
        self.summary = (' '.join(summary_tokens)).strip()
        for token in tokens[len(summary_tokens) + 1:]:
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

    def to_dict(self):
        data = {
            "created": self.created,
            "itemtype": self.itemtype,
            "summary": self.summary,
        }
        if self.start:
            data["s"] = "{T}:" + self.start.strftime("%Y%m%dT%H%M%S")
        if self.end:
            data["e"] = "{T}:" + (self.start + self.end).strftime("%Y%m%dT%H%M%S")
        if self.recurrence:
            data["r"] = self.recurrence
        return data

    def __repr__(self):
        return str(self.to_dict())

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