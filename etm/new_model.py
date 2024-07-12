import re
from dateutil.rrule import rruleset, rrule, DAILY
from datetime import datetime, timedelta
import pytz

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
        self.summary = ' '.join(summary_tokens)
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
            "w": ["{W}:4TH"]
        }
    ],
    "modified": "{T}:20240712T1054"
}

item_from_json = Item(json_dict=json_entry)
print(item_from_json)

item_from_string = Item(input_string="* Thanksgiving @s 2010/11/26 @r y &M 11 &w 4TH")
print(item_from_string)