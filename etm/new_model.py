import re
from dateutil import rrule 
from dateutil.rrule import rruleset, DAILY, rrulestr
from datetime import datetime, timedelta
from dateutil.tz import gettz
import pytz

from typing import Union, Tuple, Optional
from typing import List, Dict, Any, Callable, Mapping

class Repeat:
    
    wkd_regex = re.compile(r'(?<![\w-])(-?[1-4]?)(MO|TU|WE|TH|FR|SA|SU)(?!\w)')

    frequency = dict(
        y=rrule.YEARLY, m=rrule.MONTHLY, w=rrule.WEEKLY, d=rrule.DAILY, h=rrule.HOURLY, n=rrule.MINUTELY
        )
    
    parameters = dict(
        i='interval', c='count', s='bysetpos', u='until', M='bymonth', m='bymonthday', W='byweekno', w='byweekday', h='byhour', n='byminute', E='byeaster'
        )

    @classmethod
    def get_arg(cls, x: str):
        if x.startswith('-'):
            return f"{x}"
        if x:
            return f"+{x}"
        return x 
    
    @classmethod
    def wkdays_to_rrule(cls, wkd_str: str):
        wkd_str = wkd_str.upper()
        matches = re.findall(cls.wkd_regex, wkd_str)
        good = [f"{x[0]}{x[1]}" for x in matches]
        all = [x.strip() for x in wkd_str.split(',')]
        bad = [x for x in all if x not in good]
        res = []
        print("matches", matches)
        for x in matches:
            # arg = f"+{x[0]}" if x[0] and not x[0].startswith('-') else x[0]
            arg = cls.get_arg(x[0])
            s = f"rrule.{x[1]}({arg})" if arg else f"rrule.{x[1]}"
            print(f"{x = }, {arg = }, {s = }")
            res.append(eval(s))
        return res, good, bad
    
    @classmethod
    def dt_to_naive(cls, dt: datetime)->datetime:
        """Convert an 'aware' datetime to localtime and then remove the timezone information to make it 'naive'.

        Args:
            dt (datetime): an aware datetime.datetime object

        Returns:
            datetime: a naive datetime.datetime object
        """
        return dt if (
            dt.tzinfo is None or 
            dt.tzinfo.utcoffset(dt) is None
            ) else dt.astimezone().replace(tzinfo=None)
        
    def __init__(self, obj: Any = None):
        self.ruleset = rruleset()
        self.startdt = None
        if isinstance(obj, rrule.rruleset):
            self.ruleset = obj
        if isinstance(obj, dict) and 'r' in dict:
            self.ruleset = self._from_dict(obj)
        elif isinstance(obj, str):
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
        raise NotImplementedError
        
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
            
    def add_rule(self, rule: Dict[str, Any]) -> None:
        if 'r' not in rule: 
            raise ValueError("Missing 'r' in rule")
        if rule['r'] not in Repeat.frequency:
            raise ValueError(f"{rule['r']} is not a valid frequency")
        hsh = {}
        hsh['freq'] = Repeat.frequency[rule['r']]
        for k, v in Repeat.parameters.items():
            if k in rule:
                hsh[v] = rule[k]
        print(hsh)
        # dtstart = self.startdt if self.startdt else datetime.now().astimezone().replace(tzinfo=None)
        # lst.append(dtstart = {dtstart})
        # lst.append("cache=True")
        # print(lst, dtstart)
        thisrule = rrule.rrule(**hsh)
        print(thisrule)
        self.ruleset.rrule(thisrule)        
    
    def parse_input(self, input_string):
        self.rruleset = rruleset()
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
    def __init__(self, json_dict=None, input_string=None):
        self.created = self._get_current_timestamp()
        self.itemtype = None
        self.summary = None
        self.start = None
        self.end = None
        self.recurrence = None
        self.rruleset = None
        if json_dict:
            self._init_from_json(json_dict)
        elif input_string:
            self.parse_input(input_string)

    def _get_current_timestamp(self):
        return datetime.now(pytz.utc).strftime("%Y%m%dT%H%M%S")

    def _init_from_json(self, json_dict):
        self.created = json_dict.get("created", self.created)
        self.itemtype = json_dict.get("itemtype")
        self.summary = json_dict.get("summary")
        self.start = self._parse_datetime(json_dict.get("s", "").replace("{T}:", ""))
        self.end = self._parse_datetime(json_dict.get("e", "").replace("{T}:", ""))
        self.recurrence = json_dict.get("r", [{}])[0]

    def parse_input(self, input_string):
        tokens = self._tokenize(input_string)
        self._parse_tokens(tokens)
        self._validate()

    def _tokenize(self, input_string):
        pattern = r'(@\w+ [^@&]+)|(&\w+ \S+)|(^\S+)|(\S[^@&]*)'
        matches = re.findall(pattern, input_string)
        return [match[0] or match[1] or match[2] or match[3] for match in matches if match[0] or match[1] or match[2] or match[3]]

    def _parse_tokens(self, tokens):
        self.itemtype = tokens[0][0]
        summary_tokens = []
        recurrence_attributes = {}
        for token in tokens[1:]:
            if token.startswith('@'):
                break
            summary_tokens.append(token)
        self.summary = (' '.join(summary_tokens)).strip()
        for token in tokens[len(summary_tokens) + 1:]:
            if token.startswith('@s'):
                self.start = self._parse_datetime(token[3:].strip())
            elif token.startswith('@e'):
                self.end = self._parse_duration(token[3:].strip())
            elif token.startswith('@r'):
                self.recurrence = self._parse_recurrence(token[3:].strip())
            elif token.startswith('&'):
                attribute, value = self._parse_attribute(token)
                recurrence_attributes[attribute] = value
        if self.recurrence:
            self.recurrence.update(recurrence_attributes)

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
        return {"r": recurrence_str}

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
            data["r"] = [self.recurrence]
        return data

    def __repr__(self):
        return str(self.to_dict())

# Example usage
json_entry = {
    "created": "{T}:20240712T1052",
    "itemtype": "*",
    "summary": "Thanksgiving",
    "s": "{T}:20101126T0500",
    "r": [
        {
            "r": "y",
            "M": [11],
            "w": ["4TH"]
        }
    ],
    "modified": "{T}:20240712T1054"
}

item_from_json = Item(json_dict=json_entry)
print(item_from_json)

item_from_string = Item(input_string="* Thanksgiving @s 2010/11/26 @r y &M 11 &w 4TH")
print(item_from_string)