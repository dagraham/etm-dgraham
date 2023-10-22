#!/usr/bin/env python3.12
from dateutil.parser import parse as dateutil_parse
from datetime import datetime, date, timedelta
from pytz import timezone


from pydantic import BaseModel, ConfigDict, ValidationError, field_validator
from typing import Optional
from enum import Enum
from icecream import ic

# from pprint import pprint as print

def parse(s: str, **kwd) -> datetime:
    dt = dateutil_parse(s)
    if 'tzinfo' in kwd:
        tzinfo = kwd['tzinfo']
        if tzinfo == 'float':
            return dt
        elif tzinfo == 'local':
            return dt.astimezone()
        else:
            return timezone(tzinfo).localize(dt)
    else:
        return dt.astimezone()

args = [
        {'tzinfo': 'US/Pacific',},
        {'tzinfo': 'local',},
        {'tzinfo': 'float',},
        {},
        ]
print("\nparse examples:")
for x in args:
    print(f"using parse with {x}")
    ic(parse('2pm fri', **x))
    # dt = parse('2pm fri', **x)
    # ic(dt)

def is_aware(dt: datetime) -> bool:
    return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None

def add_zone_info(dt: datetime, zone: str = None) -> datetime:
    if isinstance(dt, date) and not isinstance(dt, datetime):
        # naive date, return as is
        return dt
    elif isinstance(dt, datetime):
        if is_aware(dt):
            # already aware - convert to UTC
            dt = dt.astimezone(timezone('UTC'))
        elif zone:
            # naive - incorporate zone info if available
            if zone == 'float':
                # leave naive
                pass
            elif zone == 'local':
                # use local timezone
                dt = dt.astimezone().astimezone('UTC')
            else:
                # use the provided timezone
                dt = timezone(zone).localize(dt).astimezone(timezone('UTC'))
        else:
            # default to the local timezone
            dt = dt.astimezone().astimezone('UTC')
        return truncate_datetime(dt)
    else:
        raise ValueError(f"{dt} is not a date or datetime instance")


def truncate_datetime(dt: datetime) -> datetime:
    return dt.replace(microsecond=0)

def truncate_timedelta(td: timedelta) -> timedelta:
    # return timedelta(days=td.days, seconds=td.seconds-td.seconds%60)
    return timedelta(days=td.days, seconds=td.seconds)

# Example usage:
print("\ntruncate examples:")
ic(truncate_datetime(datetime.now()))
# ic('now:', dt)  # will print current time truncated to its minute value, e.g., "2023-10-21 14:57:00"

############
# CLASSES
############

class ReminderType(Enum):
    inbox = '!'
    event = '*'
    task = '-'
    journal = '%'


class Reminder(BaseModel):
    model_config = ConfigDict(extra='forbid', use_enum_values=True)
    reminder_type: ReminderType
    summary: str

    # combine start and zone and store aware datetimes as UTC
    zone: Optional[str] = None
    start: datetime | date
    @field_validator('start')
    @classmethod
    def use_zone(cls, value, values):
        # zone will either be None (null) or have the provided zone information
        return add_zone_info(value, values.data['zone'])
    extent: Optional[timedelta] = None

    def get_end(self):
        if self.extent:
            return (self.start + self.extent).astimezone()
        else:
            return None

    def get_start(self):
        return self.start.astimezone()

print("\nReminder examples:")
try:
    w = Reminder(
        reminder_type = ReminderType.inbox,
        summary = 'now is the time',
        # start = truncate_datetime(datetime.now().astimezone(timezone('UTC'))),
        start = datetime.now(),
        extent = truncate_timedelta(
            timedelta(days=2, hours=1, minutes=30, seconds=10, microseconds=737)
            ),
        zone = 'US/Eastern',
        )
    ic(w.model_dump_json(indent=3))
    ic(w.model_dump())
    ic(w.get_start())
    ic(w.get_end())

except ValidationError as ve:
    print(ve)



def main():
    pass


if __name__ == "__main__":
    main()

